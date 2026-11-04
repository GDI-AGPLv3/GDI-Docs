# Validaciones

El módulo `app/validators.py` centraliza todas las validaciones de entrada del servicio Notary.
Cada validación lanza `HTTPException` con código de error específico.

## Validación de PDF

### validate_pdf_format

Valida formato, tamaño y signatura del PDF recibido por multipart.

```python
def validate_pdf_format(pdf_file: UploadFile) -> bytes:
```

| Validación | Condición | Error |
|------------|-----------|-------|
| Tamaño declarado | `pdf_file.size > 64 MB` | `400 FILE_TOO_LARGE` |
| Lectura | No se puede leer el archivo | `400 INVALID_PDF_FILE` |
| Tamaño real | Los bytes leídos pasan de 64 MB | `400 FILE_TOO_LARGE` |
| Signatura PDF | No comienza con `%PDF` | `400 INVALID_PDF_FORMAT` |

El tope sale de `MAX_SIGNABLE_PDF_SIZE_MB = 64` en `config.py`. Es el mismo número que usa el
Backend: los adjuntos embebidos viajan dentro del PDF a firmar y suman peso.

El tamaño se controla dos veces. El campo `.size` lo declara el cliente y no alcanza. Después de
leer, Notary vuelve a medir los bytes reales.

```python
# El .size lo declara el cliente: el tope real es sobre lo leido.
if len(pdf_content) > MAX_SIGNABLE_PDF_SIZE_MB * 1024 * 1024:
    raise HTTPException(status_code=400,
                        detail=f"PDF file too large. Maximum size: {MAX_SIGNABLE_PDF_SIZE_MB}MB",
                        headers={"error_code": "FILE_TOO_LARGE"})

# Signatura valida
if not pdf_content.startswith(b'%PDF'):
    raise HTTPException(status_code=400, detail="Invalid PDF format")
```

### Tope del pedido entero

Antes de llegar al endpoint, un middleware mide el **pedido completo**: PDF, certificado `.p12`
y campos del formulario. El tope es `MAX_REQUEST_BODY_SIZE_MB`. Por defecto vale 64 MB del PDF
más 4 MB de margen (68 MB).

- Si el header `Content-Length` declara más que el tope, Notary responde `413` sin leer nada.
- Si el cliente no declara el tamaño (o declara menos), el middleware cuenta lo que lee y
  corta con `413` apenas se pasa.

```json
{ "detail": "Request body too large. Maximum: 71303168 bytes", "error_code": "REQUEST_BODY_TOO_LARGE" }
```

!!! note "Modo URL"
    Cuando el PDF llega por URL pre-firmada (body JSON con `pdf_url`), el tope de la descarga es
    `URL_FETCH_MAX_SIZE_MB` (50 MB por defecto). Notary lo controla mientras descarga.

---

## Control de certificación (DocMDP)

Un PDF puede traer una **firma de certificación** (DocMDP). La pone el autor del documento y
dice qué cambios se permiten después:

- `P=1`: ningún cambio;
- `P=2`: completar formularios y firmar;
- `P=3`: lo de `P=2` y, además, anotaciones.

Si GDI estampa o firma encima, esa certificación queda rota. Por eso Notary revisa el PDF
**antes** de estamparlo o firmarlo. El módulo es `app/certification.py` y la función,
`detect_certification(pdf_bytes)`.

### Dónde corre

| Endpoint | Cuándo |
|----------|--------|
| `/sign-pdf` | Al entrar, antes del fallback visual |
| `/stamp-number` | Al entrar |
| `/sign-pdf/prepare` | Al entrar |
| `/sign-pdf/finish` | Después de armar la firma y antes de subir el resultado |
| `/timestamp-pdf` | **No corre**: un sello de tiempo no rompe la certificación |
| `/sign-pdf/verify` | **No corre**: solo lee |

El control va antes del fallback visual (`FALLBACK_TO_VISUAL=true`). Así un ambiente de
desarrollo rechaza el mismo PDF que producción.

En `/sign-pdf/finish` el control mira el PDF ya firmado. El PDF preparado trae la firma vacía
(`/Contents` en ceros) y pyHanko no lo puede leer. Si el control rechaza, Notary no sube nada.

### La regla

`detect_certification` devuelve uno de 7 estados. Sigue estos pasos:

1. Abre el PDF con `PdfFileReader` de pyHanko en modo estricto. Si no abre: `unreadable`.
2. Si está encriptado, prueba `decrypt("")`. Si falla: `encrypted_password`.
3. Lista las firmas con `/ByteRange`. Si eso tira una excepción, el resultado es `unreadable`
   (nunca "0 firmas").
4. Marca como certificación cada firma que declara nivel DocMDP o a la que apunta
   `/Perms/DocMDP` del catálogo. Si el nivel no se puede leer, la firma cuenta como
   certificación. Si hay alguna: `certified`.
5. Si el catálogo trae `/Perms/DocMDP` sin firma de certificación detrás: con 0 firmas,
   `orphan_perms`; con firmas, `inconsistent`.
6. Si no: con firmas, `signed`; sin firmas, `none`.

!!! info "Misma regla en PDFComposer"
    PDFComposer tiene una copia de esta regla para `/import/` y `/embed-files/`. Las dos copias
    tienen que dar el mismo resultado para el mismo PDF: si se cambia una, se cambia la otra.
    Ver [PDFComposer](../pdfcomposer/index.md).

### Qué responde

Los estados `none` y `signed` siguen el camino normal. También sigue `orphan_perms`, salvo con
`P=1`. El resto se rechaza con **422**:

| Estado | `code` | Cuándo |
|--------|--------|--------|
| `certified` | `PDF_CERTIFIED` | Alguna firma es de certificación (DocMDP P=1/2/3, `/Lock /P`, o `/Perms/DocMDP` apunta a ella) |
| `inconsistent` | `PDF_CERTIFICATION_INCONSISTENT` | `/Perms/DocMDP` sin firma real que lo respalde, con otras firmas |
| `orphan_perms` con `P=1` | `PDF_CERTIFICATION_INCONSISTENT` | `/Perms/DocMDP` con P=1 y ninguna firma: pyHanko se niega a firmarlo |
| `unreadable` | `PDF_SIGNATURES_UNREADABLE` | No se pueden leer las firmas (campo firmado sin `/ByteRange`, PDF dañado) |
| `encrypted_password` | `PDF_ENCRYPTED_PASSWORD` | El PDF pide contraseña para abrirse |

```json
{
  "detail": {
    "error_code": "PDF_CERTIFIED",
    "code": "PDF_CERTIFIED",
    "detail": "El PDF trae una firma de certificación: GDI no lo firma ni lo estampa para no romperla.",
    "certification_status": "certified"
  }
}
```

El código viene también en el header `error_code`.

!!! warning "422 es un error de contenido"
    Reintentar no sirve: el mismo PDF da el mismo 422. El Backend no suma un 4xx distinto de
    400 a su freno de Notary. Un error de firma cualquiera sigue siendo `500 PADES_ERROR`.

---

## PDF encriptado con contraseña de dueño

Muchos PDF reales (bancos, organismos de recaudación) vienen encriptados con **contraseña de
dueño** y sin contraseña de apertura. Cualquiera los abre, pero los objetos van cifrados.

Notary los firma y los estampa si no traen certificación. El módulo es `app/pdf_encryption.py`:

| Función | Qué hace |
|---------|----------|
| `open_reader(pdf_content)` | Abre el PDF y, si está encriptado, lo desencripta con `decrypt("")` |
| `open_incremental_writer(pdf_content)` | Abre un escritor incremental. Si el original está encriptado, la revisión nueva sale encriptada igual (`encrypt("")`) |

La norma PDF no deja sacar la encriptación en una revisión incremental. Por eso la revisión de
GDI sale con la misma encriptación que el original. Resultado: la firma del proveedor queda
intacta y la firma de GDI es válida.

Un PDF que pide contraseña para abrirse no llega a estas funciones. Lo frena antes el control
de certificación con `422 PDF_ENCRYPTED_PASSWORD`.

---

## Validación de parámetros de firma

### validate_signature_params

Valida los 4 parámetros obligatorios de la firma.

```python
def validate_signature_params(
    name: str,        # 1-100 chars
    seal: str,        # 1-50 chars
    department: str,  # 1-100 chars
    entity: str       # 1-100 chars
) -> dict:
```

| Parámetro | Límite | Validaciones |
|-----------|--------|-------------|
| `name` | 1-100 chars | No vacío, no excede 100 |
| `seal` | 1-50 chars | No vacío, no excede 50 |
| `department` | 1-100 chars | No vacío, no excede 100 |
| `entity` | 1-100 chars | No vacío, no excede 100 |

Retorna los parámetros con `strip()` aplicado. Si falla, lanza `400 INVALID_PARAMETERS`
con la lista de errores.

---

## Validación de estampado

### validate_stamp_params

Valida los parámetros opcionales de estampado.

```python
def validate_stamp_params(
    document_number: Optional[str],  # max 40 chars
    city: Optional[str]              # max 50 chars, requerido si document_number
) -> Optional[dict]:
```

| Regla | Descripción |
|-------|-------------|
| `city` es obligatorio | Si se envía `document_number`, `city` es requerido |
| `document_number` max | 40 caracteres |
| `city` max | 50 caracteres |

Error: `400 INVALID_STAMP_PARAMETERS`

### validate_stamp_position

Valida que `stamp_position` sea un valor válido.

```python
def validate_stamp_position(stamp_position: Optional[str]) -> None:
    valid_positions = ["first", "last"]
    if stamp_position not in valid_positions:
        raise HTTPException(
            status_code=400,
            detail=f"stamp_position must be 'first' or 'last'"
        )
```

Error: `400 INVALID_STAMP_POSITION`

---

## Validación de tenant_id

### validate_tenant_id

Previene path traversal validando el formato del `tenant_id`.

```python
TENANT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

def validate_tenant_id(tenant_id: str) -> str:
    if not tenant_id or not TENANT_ID_PATTERN.match(tenant_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid tenant_id format"
        )
    return tenant_id
```

**Caracteres permitidos:** `a-z`, `A-Z`, `0-9`, `-`, `_`

!!! danger "Prevención de path traversal"
    Sin esta validación, un `tenant_id` como `../../etc/passwd` podría
    hacer que el sistema intente cargar un archivo fuera del directorio
    de certificados. Esta validación trabaja en conjunto con la verificación
    de contención en `certificate_loader.get_certificate_path()`.

Error: `400 INVALID_TENANT_ID`

---

## Sanitización de nombres de archivo

### sanitize_filename

Reemplaza caracteres especiales en nombres de archivo.

```python
SPECIAL_CHARS = r'/\:*?"<>|'

def sanitize_filename(filename: str) -> str:
    sanitized = filename
    for char in SPECIAL_CHARS:
        sanitized = sanitized.replace(char, '-')
    return sanitized
```

**Ejemplo:** `IF/2025\doc.pdf` se convierte en `IF-2025-doc.pdf`

---

## Autenticación (auth.py)

El módulo `app/auth.py` implementa la validación de API Key:

```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
```

Se usa como dependencia de FastAPI en los endpoints protegidos:

```python
@app.post("/sign-pdf")
async def sign_pdf(
    ...,
    api_key: str = Depends(validate_api_key)
):
```

Error: `401 INVALID_API_KEY`

---

## Resumen de códigos de error

| Código | Error Code | Módulo | Descripción |
|--------|------------|--------|-------------|
| 400 | `FILE_TOO_LARGE` | validators | PDF > 64 MB (declarado o leído) |
| 400 | `INVALID_PDF_FILE` | validators | No se puede leer |
| 400 | `INVALID_PDF_FORMAT` | validators | No es PDF válido |
| 400 | `INVALID_PARAMETERS` | validators | Parámetros de firma inválidos |
| 400 | `INVALID_STAMP_PARAMETERS` | validators | Estampado inválido |
| 400 | `INVALID_STAMP_POSITION` | validators | Position no es first/last |
| 400 | `INVALID_TENANT_ID` | validators | Caracteres no permitidos |
| 400 | `CERTIFICATE_NOT_FOUND` | main | Sin cert + FALLBACK=false |
| 400 | `CERTIFICATE_LOAD_ERROR` | main | Error al cargar cert |
| 401 | `INVALID_API_KEY` | auth | API Key inválida |
| 413 | `REQUEST_BODY_TOO_LARGE` | main (middleware) | Pedido entero > `MAX_REQUEST_BODY_SIZE_MB` (68 MB por defecto) |
| 422 | `PDF_CERTIFIED` | certification | El PDF trae firma de certificación |
| 422 | `PDF_CERTIFICATION_INCONSISTENT` | certification | `/Perms/DocMDP` sin firma que lo respalde |
| 422 | `PDF_SIGNATURES_UNREADABLE` | certification | Firmas ilegibles o PDF dañado |
| 422 | `PDF_ENCRYPTED_PASSWORD` | certification | El PDF pide contraseña para abrirse |
| 500 | `PADES_ERROR` | main | Error en firma PAdES |
