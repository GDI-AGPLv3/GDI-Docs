# Firma PAdES

El modulo `app/pades_signer.py` implementa la firma digital PAdES-B-T (Basic with Time)
usando la libreria **pyHanko**.

## Que es PAdES

PAdES (PDF Advanced Electronic Signatures) es un estandar de ETSI para firmas
electronicas avanzadas en documentos PDF.

**PAdES-B-T** incluye:

- Firma criptografica embebida en el PDF
- Timestamp de un servidor TSA (Time Stamping Authority)
- Hash SHA-256
- Compatible con Adobe Acrobat Reader (verificacion con clic)

## Flujo de firma PAdES

```mermaid
flowchart TD
    A[PDF + Certificado .p12] --> B[Cargar certificado PKCS#12]
    B --> C[Crear SimpleSigner pyHanko]
    C --> D[Configurar IncrementalPdfFileWriter]
    D --> E[Configurar metadata firma]
    E --> F[Configurar campo visual]
    F --> G{TSA configurado?}
    G -->|Si| H[Solicitar timestamp]
    G -->|No| I[Firma sin timestamp]
    H --> J[Firmar con async_sign_pdf]
    I --> J
    J --> K[PDF firmado PAdES-B-T]
```

## Funcion principal: sign_pdf_combined

Esta es la funcion usada en produccion. Combina firma criptografica PAdES con
representacion visual profesional.

```python
async def sign_pdf_combined(
    pdf_content: bytes,
    cert: LoadedCertificate,
    signature_params: dict,    # name, seal, department, entity
    x: float,                  # Coordenada X (de layout.py)
    y: float,                  # Coordenada Y (de layout.py)
    existing_signature_count: int = 0,
) -> bytes:
```

### Configuracion del firmante

```python
# Crear firmante desde archivo .p12 (metodo nativo de pyHanko)
signer = signers.SimpleSigner.load_pkcs12(
    pfx_file=p12_path,
    passphrase=password.encode('utf-8'),
)
```

### Campo de firma visual

El campo se posiciona en la ultima pagina usando las coordenadas calculadas por `layout.py`:

```python
sig_field_spec = fields.SigFieldSpec(
    sig_field_name=f"GDI_Signature_{pades_count + 1}",
    on_page=last_page,
    box=(sig_x, sig_y, sig_x + SIGNATURE_WIDTH, sig_y + SIGNATURE_HEIGHT),
)
```

### Estilo del stamp visual

```python
stamp_style = TextStampStyle(
    stamp_text=(
        "%(signer_upper)s\n"
        "%(seal)s\n"
        "%(department)s\n"
        "%(entity)s"
    ),
    border_width=0,          # Sin borde
    background_opacity=0.0,  # Sin fondo
)

appearance_text_params = {
    'signer_upper': name.upper(),  # Nombre en MAYUSCULAS
    'seal': seal,
    'department': department,
    'entity': entity,
}
```

### Resultado visual

```
JUAN PEREZ
Director
Hacienda
Municipalidad del Futuro
```

- Nombre en MAYUSCULAS para destacar
- Sin borde, sin fondo
- Sin fecha visible (la fecha esta en los metadatos de la firma)

### Metadata de la firma

```python
signature_meta = signers.PdfSignatureMetadata(
    field_name=sig_field_name,
    name=name,
    reason=f"{seal} - {department}",
    location=entity,
    subfilter=fields.SigSeedSubFilter.PADES,
    md_algorithm='sha256',
)
```

La metadata es visible al hacer clic en la firma en Adobe Reader:

- **Name**: Nombre del firmante
- **Reason**: Cargo - Departamento
- **Location**: Entidad

## Timestamp (TSA) con reintentos y circuit breaker

El cliente TSA usa `RetryingTimestamper` (wrapper sobre `HTTPTimeStamper`) con backoff
exponencial y circuit breaker. La funcion `get_timestamp_client()` **nunca devuelve None**:
si `TSA_URL` no esta configurado, lanza `PAdESTimestampError`.

```python
# Config
TSA_URL     = os.getenv("TSA_URL", "http://timestamp.digicert.com")
TSA_TIMEOUT = int(os.getenv("TSA_TIMEOUT", "3"))   # segundos por intento
TSA_RETRIES = int(os.getenv("TSA_RETRIES", "2"))   # reintentos (total = retries + 1)
```

### Logica de reintentos

Con los valores default: 3 intentos x 3s + backoffs (0.2s + 0.6s) = ~9.8s maximo por firma.

| Intento | Espera antes |
|---------|-------------|
| 1 | - |
| 2 | 0.2s |
| 3 | 0.6s |

### Circuit breaker

Protege contra TSA caido de forma sostenida. Implementado en `TsaCircuitBreaker`:

| Estado | Comportamiento |
|--------|---------------|
| `CLOSED` | Normal, todas las llamadas pasan |
| `OPEN` | Fail-fast: lanza `PAdESTsaUnavailableError` sin llamar al TSA |
| `HALF_OPEN` | Deja pasar 1 request de prueba; exito → `CLOSED`, fallo → `OPEN` |

- **Umbral de apertura**: 5 fallos consecutivos
- **Cooldown**: 60 segundos en `OPEN` antes de pasar a `HALF_OPEN`
- **Alcance**: por proceso Gunicorn (no compartido entre procesos)

Cuando el circuit breaker esta `OPEN`, Notary devuelve `HTTP 503 TSA_UNAVAILABLE`
independientemente de `FALLBACK_TO_VISUAL`, para que el Backend pueda distinguir
"TSA caido" de "sin certificado".

Servidores TSA publicos soportados:

| Servidor | URL |
|----------|-----|
| DigiCert | `http://timestamp.digicert.com` |
| Sectigo | `http://timestamp.sectigo.com` |
| GlobalSign | `http://timestamp.globalsign.com/tsa/r6advanced1` |

## Otras funciones

### count_pades_signatures

Cuenta las firmas PAdES existentes en un PDF:

```python
def count_pades_signatures(pdf_content: bytes) -> int:
    reader = PdfFileReader(io.BytesIO(pdf_content))
    return len(list(reader.embedded_signatures))
```

### verify_pades_signature

Verifica firmas PAdES existentes:

```python
def verify_pades_signature(pdf_content: bytes) -> dict:
    # Retorna: signature_count, signatures[{field_name, valid, intact, trusted}]
```

## Excepciones

| Excepcion | HTTP | Causa |
|-----------|------|-------|
| `PAdESSigningError` | 500 | Error general de firma |
| `PAdESTimestampError` | 500 | Todos los reintentos al TSA fallaron |
| `PAdESTsaUnavailableError` | 503 | Circuit breaker abierto (subclase de `PAdESTimestampError`) |
| `PAdESCertificateError` | 400 | Certificado invalido o expirado |

## Configuracion en config.py

```python
PADES_SIGNATURE_FIELD_NAME = "GDI_Signature"   # Prefijo del campo
PADES_SIGNATURE_REASON = "Documento firmado digitalmente"
PADES_SIGNATURE_LOCATION = "Sistema GDI"
```
