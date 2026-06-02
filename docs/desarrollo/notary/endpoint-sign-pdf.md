# Endpoint /sign-pdf

El endpoint principal de Notary. Firma documentos PDF con firma PAdES digital o visual,
usando layout automatico de 2 columnas.

## Request

```
POST /sign-pdf
Content-Type: multipart/form-data
X-API-Key: {api_key}
```

### Parametros (Form Data)

| Parametro | Tipo | Requerido | Descripcion |
|-----------|------|-----------|-------------|
| `pdf_file` | File | Si | PDF formato A4, max 10 MB |
| `name` | string | Si | Nombre del firmante (1-100 chars) |
| `seal` | string | Si | Cargo del firmante (1-50 chars) |
| `department` | string | Si | Departamento (1-100 chars) |
| `entity` | string | Si | Entidad (1-100 chars) |
| `document_number` | string | No | Numero de documento para estampado (max 40 chars) |
| `city` | string | Condicional | Ciudad para estampado. Requerido si `document_number` presente |
| `stamp_position` | string | No | `'first'` (default) o `'last'` |
| `tenant_id` | string | No | ID del tenant (para logging; el certificado llega via `cert_file`) |
| `use_pades` | string | No | `'true'` (default) o `'false'` |
| `cert_file` | File | No | Archivo `.p12` del certificado (enviado por el Backend desde R2) |
| `cert_password` | string | No | Password del `.p12` (enviado por el Backend) |
| `expected_sha256` | string | No | Hash SHA-256 hex del PDF esperado. Si se envia, se verifica integridad antes de firmar |

!!! warning "Campos condicionales"
    - `city` es **obligatorio** cuando se envia `document_number`
    - Para firma PAdES, el Backend debe enviar `cert_file` + `cert_password` (el certificado viene desde R2, no se busca localmente)
    - Si `expected_sha256` no coincide con el hash real del PDF recibido, se rechaza con `400 PDF_INTEGRITY_FAILED`

## Response

**Exito (200):**

```
Content-Type: application/pdf
Content-Disposition: attachment; filename={document_number}.pdf
X-Signature-Type: pades | visual
```

El body es el PDF firmado en bytes.

**Header `X-Signature-Type`:**

- `pades`: Se aplico firma PAdES criptografica
- `visual`: Se aplico firma visual (sin componente criptografico)

### Nomenclatura del archivo

- Si se envio `document_number`: el archivo se llama `{document_number}.pdf`
- Si no se envio: se mantiene el nombre original del archivo subido

## Ejemplo con cURL

### Firma PAdES

```bash
curl -X POST "http://localhost:8001/sign-pdf" \
     -H "X-API-Key: your-api-key-here" \
     -F "pdf_file=@documento.pdf" \
     -F "name=Juan Perez" \
     -F "seal=Director" \
     -F "department=Hacienda" \
     -F "entity=Municipalidad del Futuro" \
     -F "tenant_id=200_muni" \
     -F "document_number=IF-2025-00001234-MUNI" \
     -F "city=Ciudad Autonoma" \
     --output firmado.pdf
```

### Firma visual (sin certificado)

```bash
curl -X POST "http://localhost:8001/sign-pdf" \
     -H "X-API-Key: your-api-key-here" \
     -F "pdf_file=@documento.pdf" \
     -F "name=Maria Lopez" \
     -F "seal=Secretaria" \
     -F "department=Administracion" \
     -F "entity=Municipalidad Demo" \
     -F "use_pades=false" \
     --output firmado_visual.pdf
```

## Proceso interno paso a paso

```mermaid
flowchart TD
    A[Recibir request] --> B[Validar tenant_id si presente]
    B --> C[Validar PDF: formato + tamano]
    C --> SHA{expected_sha256 presente?}
    SHA -->|Si| SHAV[Calcular SHA-256 del PDF recibido]
    SHAV --> SHAC{Hash coincide?}
    SHAC -->|No| SHAERR[Error 400 PDF_INTEGRITY_FAILED]
    SHAC -->|Si| D
    SHA -->|No| D[Validar parametros firma]
    D --> E{document_number?}
    E -->|Si| F[Validar stamp params]
    E -->|No| G[Determinar modo firma]
    F --> G

    G --> H{cert_file + cert_password + use_pades?}
    H -->|Si| J[load_certificate_from_bytes /dev/shm]
    H -->|No + FALLBACK=true| K[Modo visual]
    H -->|No + FALLBACK=false| L[Error 400 CERTIFICATE_NOT_PROVIDED]

    J --> M[Contar firmas existentes]
    K --> M
    M --> N[Calcular posicion X,Y]
    N --> O{document_number + city?}
    O -->|Si| P[stamp_document async - asyncio.to_thread]
    O -->|No| Q{PAdES?}
    P --> Q
    Q -->|Si| R[sign_pdf_combined - TSA con reintentos + circuit breaker]
    Q -->|No| S[sign_pdf_document async - asyncio.to_thread]
    R -->|TSA caido| TSA503[Error 503 TSA_UNAVAILABLE]
    R --> T[Response PDF - header X-Signature-Type]
    S --> T
```

## Codigos de error

| Codigo | Error Code | Causa |
|--------|------------|-------|
| 400 | `FILE_TOO_LARGE` | PDF excede 10 MB |
| 400 | `INVALID_PDF_FILE` | No se puede leer el archivo |
| 400 | `INVALID_PDF_FORMAT` | No comienza con `%PDF` |
| 400 | `PDF_INTEGRITY_FAILED` | Hash SHA-256 del PDF no coincide con `expected_sha256` |
| 400 | `INVALID_PARAMETERS` | Parametros de firma invalidos |
| 400 | `INVALID_STAMP_PARAMETERS` | `document_number` sin `city` |
| 400 | `INVALID_STAMP_POSITION` | `stamp_position` no es `first` ni `last` |
| 400 | `INVALID_TENANT_ID` | `tenant_id` con caracteres no permitidos |
| 400 | `CERTIFICATE_NOT_PROVIDED` | No llego `cert_file` y `FALLBACK_TO_VISUAL=false` |
| 400 | `CERTIFICATE_LOAD_ERROR` | Error al cargar certificado desde `cert_file` |
| 400 | `LayoutError` | No se encontro `end-text` o pagina llena (`FULLPAGE`) |
| 401 | `INVALID_API_KEY` | API Key invalida o faltante |
| 500 | `PADES_ERROR` | Error en firma PAdES |
| 503 | `TSA_UNAVAILABLE` | Circuit breaker abierto: TSA no disponible |
| 500 | - | Error interno del servidor |

## Otros endpoints

### GET /health

Health check sin autenticacion. Unico endpoint con IP publica en Fly.io.

```json
{
  "status": "healthy",
  "service": "Notary",
  "version": "2.1.0",
  "signature_system": { "type": "digital_signature", "version": "2.0" },
  "pades_system": { "type": "PAdES-B-T", "library": "pyHanko" },
  "available_certificates": ["200_muni"],
  "fallback_to_visual": false
}
```

### POST /sign-pdf/verify

Verifica las firmas PAdES de un PDF. Requiere API Key. Limite 50 MB.

```json
{
  "ok": true,
  "failure_reason": null,
  "signature_count": 2,
  "signature_visible": true,
  "modification_level": "LTA_UPDATES",
  "signatures": [
    { "intact": true, "valid": true, "modification_level": "LTA_UPDATES", "signature_visible": true }
  ]
}
```

Si no hay firmas:

```json
{ "ok": false, "failure_reason": "no_signatures_found", "signature_count": 0 }
```

### POST /stamp-number

Estampa numero/fecha en el PDF y devuelve el PDF estampado en base64 mas las
coordenadas donde el cliente de firma (FirmadorGDI) debe insertar la firma criptografica.
Requiere API Key.

**Parametros (Form Data):**

| Parametro | Requerido | Descripcion |
|-----------|-----------|-------------|
| `pdf_file` | Si | PDF a estampar |
| `document_number` | No | Numero de documento. Si se omite, solo calcula posicion |
| `city` | Condicional | Requerido si `document_number` presente |
| `stamp_position` | No | `'first'` (default) o `'last'` |
| `existing_count` | No | Override manual de firmas existentes (omitir para auto-deteccion) |

**Respuesta:**

```json
{
  "stamped_pdf_b64": "JVBERi0x...",
  "sig_llx": 50.0,
  "sig_lly": 192.0,
  "sig_urx": 250.0,
  "sig_ury": 272.0
}
```

### GET /certificate/{tenant_id}

Informacion de un certificado especifico. Requiere API Key.

```json
{
  "exists": true,
  "tenant_id": "200_muni",
  "subject": "<Name(CN=GESTION DOCUMENTAL INTELIGENTE,O=Municipalidad del Futuro)>",
  "issuer": "...",
  "not_valid_before": "2025-01-01T00:00:00+00:00",
  "not_valid_after": "2026-01-01T00:00:00+00:00",
  "is_valid": true,
  "validation_message": "Certificado valido",
  "serial_number": "..."
}
```

### GET /certificates

Lista todos los certificados disponibles. Requiere API Key.

```json
{
  "count": 1,
  "certificates": ["200_muni"]
}
```
