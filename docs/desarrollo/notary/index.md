# Notary

**Servicio de firma digital de documentos PDF** con soporte PAdES y firma visual.

| Propiedad | Valor |
|-----------|-------|
| Puerto | `:8001` (desarrollo) |
| Framework | FastAPI 0.104.1 |
| Firma criptografica | pyHanko 0.27.1 (PAdES-B-T) |
| Firma visual | ReportLab + pypdf |
| Analisis PDF | PyMuPDF (fitz) |
| Runtime | Python 3.11, Gunicorn 21.2.0 |
| Deploy | Docker, Fly.io (internal-only, sin IP publica) |

## Que hace

Notary recibe un PDF y datos del firmante, aplica una firma digital (PAdES criptografica o visual)
y opcionalmente estampa informacion del documento (numero, ciudad, fecha).

```mermaid
flowchart LR
    A[Backend] -->|POST /sign-pdf| B[Notary]
    B --> C{Certificado via multipart?}
    C -->|Si| D[Firma PAdES-B-T + Visual]
    C -->|No + FALLBACK=true| E[Firma Visual]
    C -->|No + FALLBACK=false| F[Error 400]
    D --> G[PDF firmado]
    E --> G
    G -->|Response| A
```

## Modos de firma

### Firma PAdES (recomendado para produccion)

Firma digital criptografica embebida en el PDF, cumpliendo el estandar PAdES-B-T (Basic with Time):

- Firma criptografica con certificado PKCS#12 (.p12)
- Timestamp de servidor TSA (Time Stamping Authority)
- Representacion visual con datos del firmante
- Verificable en Adobe Acrobat Reader (clic en la firma)

### Firma Visual (solo testing)

Firma con elementos visuales (texto y lineas) sin componente criptografico:

- Nombre, cargo, departamento, entidad del firmante
- Timestamp de servidor
- No es verificable criptograficamente

## Comportamiento por ambiente

| Ambiente | `ENVIRONMENT` | `FALLBACK_TO_VISUAL` | Si no hay certificado |
|----------|---------------|----------------------|-----------------------|
| Desarrollo | `test` | `true` (default) | Usa firma visual |
| Produccion | `prd` | `false` (default) | Error 400 |

## Estructura del proyecto

```
GDI-Notary/
├── app/
│   ├── main.py                # Endpoints FastAPI
│   ├── config.py              # Constantes y configuracion
│   ├── auth.py                # Autenticacion API Key
│   ├── layout.py              # Algoritmo posicionamiento 2 columnas
│   ├── signature_inserter.py  # Firma visual (ReportLab + pypdf)
│   ├── document_stamper.py    # Estampado primera/ultima pagina
│   ├── validators.py          # Validaciones de entrada
│   ├── certificate_loader.py  # Carga certificados .p12 por tenant
│   └── pades_signer.py        # Firma PAdES con pyHanko
├── certs/
│   ├── {tenant_id}.p12        # Certificados por tenant
│   └── passwords.json         # Mapeo tenant -> password
├── fonts/
│   └── Roboto-Bold.ttf        # Fuente para firma visual
├── scripts/
│   └── generate_test_cert.py  # Genera certificados de prueba
├── gunicorn_conf.py           # Config produccion
├── Dockerfile
└── requirements.txt
```

## Endpoints

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| `/sign-pdf` | POST | Si | Firma PDF (PAdES o visual) |
| `/sign-pdf/verify` | POST | Si | Verifica firmas PAdES de un PDF |
| `/stamp-number` | POST | Si | Estampa numero/fecha y devuelve coordenadas para FirmadorGDI |
| `/health` | GET | No | Health check (HTTP, sin auth) |
| `/certificate/{tenant_id}` | GET | Si | Info de certificado |
| `/certificates` | GET | Si | Lista certificados |

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `ENVIRONMENT` | `test` | Ambiente de ejecucion (`test` o `prd`) |
| `API_KEY` | (requerida) | API Key de autenticacion. Falla si no esta seteada |
| `CERTS_DIR` | `./certs` | Directorio de certificados |
| `TSA_URL` | `http://timestamp.digicert.com` | Servidor de timestamp |
| `TSA_TIMEOUT` | `3` | Timeout por intento TSA (segundos) |
| `TSA_RETRIES` | `2` | Reintentos ante fallo TSA |
| `FALLBACK_TO_VISUAL` | `false` | Usar firma visual si no llega certificado |
| `GUNICORN_WORKERS` | (ver fly.toml) | Workers de Gunicorn |
| `GUNICORN_TIMEOUT` | `90` | Timeout en segundos |

!!! warning "FALLBACK_TO_VISUAL"
    El default de `FALLBACK_TO_VISUAL` en `config.py` es `false`. Para desarrollo
    sin certificado, setear explicitamente `FALLBACK_TO_VISUAL=true`.

## Flujo completo de firma

```mermaid
sequenceDiagram
    participant B as Backend
    participant N as Notary
    participant TSA as Timestamp Authority

    B->>N: POST /sign-pdf (PDF + datos firmante)
    N->>N: Validar PDF (formato, tamano)
    N->>N: Validar parametros firma
    N->>N: Validar tenant_id (path traversal check)

    alt Certificado llega via multipart (cert_file + cert_password)
        N->>N: load_certificate_from_bytes (tempfile en /dev/shm, chmod 600)
        N->>N: Calcular posicion (layout 2 columnas)
        N->>N: Estampar documento async (si aplica)
        N->>TSA: Solicitar timestamp (RetryingTimestamper + circuit breaker)
        TSA-->>N: Timestamp token
        N->>N: Firma PAdES-B-T + visual (sign_pdf_combined)
    else Sin certificado + FALLBACK=true
        N->>N: Calcular posicion (layout 2 columnas)
        N->>N: Estampar documento async (si aplica)
        N->>N: Firma visual (ReportLab + pypdf)
    else Sin certificado + FALLBACK=false
        N-->>B: Error 400 CERTIFICATE_NOT_PROVIDED
    else TSA caido (circuit breaker abierto)
        N-->>B: Error 503 TSA_UNAVAILABLE
    end

    N-->>B: PDF firmado (X-Signature-Type header)
```
