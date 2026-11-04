# Documents Signing

Servicios de firma digital: inicio de proceso, firma común, firma numerador y firma unificada.

**Ubicación:** `services/documents/signing/`

## Arquitectura de Firma

```
signing/
├── signing.py          # start_signing + sign_document (comun)
├── numerator.py        # sign_document_as_numerator (numerador)
├── unified_signing.py  # super_sign_document (detecta rol automaticamente)
├── certified_bypass.py # Certificado de origen: conformidad y numeracion sin Notary
└── details_builder.py  # Construye pantalla de firma
```

## Flujo Completo de Firma

```
  Creador                  Firmantes Comunes           Numerador
     |                           |                        |
  start_signing()                |                        |
     |                           |                        |
  [Genera PDF con PDFComposer]   |                        |
  [Sube a R2 bucket tosign]      |                        |
  [Estado: sent_to_sign]         |                        |
     |                           |                        |
     |                    super_sign()                     |
     |                    (firma comun)                    |
     |                           |                        |
     |                    [Descarga de R2]                 |
     |                    [Firma con Notary]               |
     |                    [Sobrescribe en R2]              |
     |                           |                        |
     |                    (repite por firmante)            |
     |                           |                        |
     |                           |               super_sign()
     |                           |               (numerador)
     |                           |                        |
     |                           |               [Genera numero oficial]
     |                           |               [Firma con Notary + numero]
     |                           |               [Sube a R2 bucket oficial]
     |                           |               [Estado: signed]
```

---

## Inicio de Firma (`signing.py`)

### `start_document_signing_process()`

```python
async def start_document_signing_process(
    document_id: str, user_id: str, *, schema_name: str
) -> Dict[str, Any]:
```

**Solo el creador puede iniciar el proceso.**

**Pasos:**

1. Verificar que el documento existe y está en estado editable (`draft` o `rejected`)
2. Verificar que `user_id == created_by`
3. Obtener logo de la organización desde `settings`
4. Si es NOTA: validar que tenga recipients configurados
5. Obtener lista de firmantes
6. Generar PDF con PDFComposer (async)
7. Actualizar estado a `sent_to_sign` y registrar `sent_by`
8. Enviar invitaciones a usuarios inactivos (best-effort)
9. Encolar generación de resumen IA (fire-and-forget)

**Integraciones:**

| Servicio | Función |
|----------|---------|
| PDFComposer | Genera PDF final sin marca de agua |
| R2 tosign | Almacena PDF para proceso de firma |
| Resend (email) | Invita usuarios inactivos (estado=2) |
| Resume trigger | Genera resumen IA del contenido |

---

## Firma Común (`signing.py`)

### `sign_document()`

Firma de un firmante **no numerador**.

```python
async def sign_document(
    document_id: str, user_id: str, *, schema_name: str
) -> Dict[str, Any]:
```

**Pasos:**

1. Verificar que el usuario es firmante y no ha firmado
2. Descargar PDF desde R2 bucket `tosign`
3. Obtener datos del firmante (nombre, sello, departamento, organización)
4. Firmar con Notary API (`official_number=""`, `city=""`)
5. Sobrescribir PDF en R2 `tosign`
6. Actualizar `document_signers.status = 'signed'`

!!! note "Firmante común vs numerador"
    El firmante común firma con `official_number` y `city` **vacíos**. Solo el numerador agrega el número oficial y la ciudad al sello.

---

## Firma Numerador (`numerator.py`)

### `sign_document_as_numerator()`

Proceso completo del numerador: numera, firma y oficializa.

```python
async def sign_document_as_numerator(
    document_id: str, user_id: str, *, schema_name: str
) -> Dict[str, Any]:
```

**Pasos:**

1. **Validaciones previas**: Es numerador, documento en `sent_to_sign`, todos los comunes firmaron
2. **Validar rank y departamento**: El numerador necesita rank suficiente para el tipo de documento
3. **Verificar número existente**: Si ya existe (caso reintento), reutilizar
4. **Generar número oficial**: Con advisory lock ultra corto (10-20ms)
5. **Insertar en `official_documents`**: Con contenido, firmantes, sector_ids, resume
6. **Firmar con Notary**: Con `official_number` y `city` reales
7. **Subir a R2 bucket `oficial`**: Filename = `{official_number}.pdf`
8. **Eliminar de R2 `tosign`**: Soft-fail
9. **Actualizar tablas**: `document_signers`, `document_draft.status = 'signed'`
10. **Commit o rollback automático**

**Validación de Rank:**

```sql
-- Verifica que el rank del usuario sea suficiente
-- para el tipo de documento (ej: Decreto requiere Intendente)
CASE
    WHEN rr.level IS NULL THEN true      -- Sin restriccion
    WHEN ur.level IS NULL THEN false     -- Usuario sin rank
    WHEN ur.level <= rr.level THEN true  -- Rank suficiente
    ELSE false
END as has_rank_permission
```

---

## Firma Unificada (`unified_signing.py`)

### `super_sign_document()`

Punto de entrada único que detecta automáticamente si el usuario es firmante común o numerador.

```python
async def super_sign_document(
    document_id: str, user_id: str, *, schema_name: str
) -> Dict[str, Any]:
```

**Flujo de decisión:**

```python
# Query inicial obtiene todo lo necesario
result = cursor.execute(get_signer_role_and_document_status_query(), ...)
# Retorna: is_numerator, signer_status, doc_status, pending_common_signers

# Validaciones comunes
if doc_status != 'sent_to_sign':
    raise DocumentStateError(...)
if signer_status not in ['pending', None]:
    raise ValidationError("Ya firmo")

# Bifurcacion
if not is_numerator:
    result = await sign_document(...)        # Rama A: Comun
else:
    if pending_common_signers > 0:
        raise ValidationError("Faltan firmantes")
    result = await sign_document_as_numerator(...)  # Rama B: Numerador
```

**Respuesta unificada (SuperSignResponse):**

```python
{
    "success": True,
    "message": "Documento firmado exitosamente",
    "document_id": "uuid",
    "signature_id": "uuid",
    "document_status": "signed",  # o "sent_to_sign" si es comun
    "signed_at": "2025-01-15T10:30:00",
    "is_numerator": True,
    "official_number": "IF-2025-0000157-SMG-ADGEN",  # null si comun
}
```

---

## Interacción con Notary

Todas las firmas pasan por `services/shared/notary_api.py`:

```python
signed_pdf_bytes = await call_notary_sign_pdf(
    pdf_bytes=pdf_bytes,
    signer_name="Juan Perez",
    signer_seal="Subsecretario de Gestion",
    signer_department="Administracion General",
    signer_municipality="Municipalidad del Futuro",
    official_number="IF-2025-0000157-SMG-ADGEN",  # Vacio para comun
    city="Ciudad del Futuro",                       # Vacio para comun
    stamp_position="last",  # Solo para importados
    tenant_id=schema_name   # Para firma PAdES
)
```

!!! warning "FULLPAGE"
    Si Notary responde con error FULLPAGE (sin espacio para firma), se agrega automáticamente una página con marcador `end-text` y se reintenta.

    La página se agrega como **revisión incremental** (`PdfWriter(..., incremental=True)`):
    los bytes anteriores del PDF quedan intactos. Así se conservan las firmas de los
    firmantes anteriores y los adjuntos embebidos. Si la cantidad de adjuntos cambia al
    agregar la página, la firma se corta antes de llamar a Notary.

---

## Certificado de origen (`certified_bypass.py`)

Un **certificado de origen** es un PDF importado que ya trae una firma de certificación
(`/DocMDP`), por ejemplo de un escribano. Una firma nueva rompe esa certificación. Por eso
GDI no lo firma: lo numera sin pasar por Notary.

**Cómo se marca:**

1. Al importar, PDFComposer `/import/` devuelve el PDF byte a byte con el header `X-GDI-Certified: true`.
2. El Backend guarda el SHA-256 de esos bytes en `document_draft.certified_pdf_sha256`. `NULL` = no certificado.
3. La marca se pone en `NULL` **antes** de tocar R2, y el hash **después** de que la subida salio bien. Una marca en `NULL` con un PDF certificado es segura: Notary lo frena con `422`.

**Cuándo se saltea Notary:** solo si `debe_saltear_notary` da `True`. Exige dos cosas:

- la columna `certified_pdf_sha256` tiene un hash;
- ese hash es igual al SHA-256 de los bytes que el llamador acaba de bajar de R2.

La columna sola no alcanza. Con hash distinto, el documento va por el camino normal (Notary).

**Qué hace cada rol:**

| Rol | Con certificado de origen |
|-----|---------------------------|
| Firmante común | Deja **conformidad**: fila en `document_signers` con `signed_with_provider = 'conformidad'`. No toca el PDF |
| Numerador | Asigna el número en la base y copia el PDF tal cual al bucket `oficial` (nunca a `preoficial`: el sellado diferido reescribiría el PDF). El número **no** se imprime en el PDF |

No se valida el marcador `end-text`: el PDF no lleva la hoja de GDI.

**Modo `solo_sin_notary`:** las puertas que ya decidieron "es certificado" y mandan un tipo
que exige firma digital por la vía electrónica (super-sign, Gateway REST, tanda con token)
prenden este modo. Si la segunda verificación da distinto, no caen a Notary con firma
electrónica:

| Situación | Error | HTTP |
|-----------|-------|------|
| El hash ya no coincide | `CertifiedHashMismatchError` (`CERTIFIED_HASH_MISMATCH`) | `409` en el Gateway |
| No se pudo bajar el PDF para comparar | `CertifiedCheckRetryError` (`CERTIFIED_CHECK_RETRY`) | `503` + `Retry-After: 5` |

**Adjuntos:** un certificado de origen no admite adjuntos de GDI.

- El alta de un adjunto responde `400` con `error_code` `CERTIFIED_NO_ATTACHMENTS`.
- Reemplazar el PDF por uno certificado, con adjuntos ya cargados, responde `400` con `CERTIFIED_PDF_WITH_ATTACHMENTS`.
- Por TAD, el alta termina en `failed` con `failure_reason: certified_pdf_with_attachments`.

**Dónde se ve:** `certified_origin` en `GET /documents/{id}/details`, en la lista de documentos
oficiales del expediente y en el Gateway. Ver [Endpoints de documentos](../endpoints/documentos.md#detalles-unificados).
