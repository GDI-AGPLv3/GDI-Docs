# Variables de Entorno

Tabla consolidada de todas las variables de entorno del ecosistema GDI, agrupadas por servicio.

## GDI-Backend (:8000)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Si | `postgresql://user:pass@host:port/db` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Si | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Si | `https://api.tu-dominio.com` |
| `PDFCOMPOSER_URL` | URL de GDI-PDFComposer | Si | `http://pdfcomposer:8002` |
| `PDFCOMPOSER_API_KEY` | API Key para PDFComposer | Si | `(secreto)` |
| `NOTARY_URL` | URL de GDI-Notary | Si | `http://notary:8001` |
| `NOTARY_API_KEY` | API Key para Notary | Si | `(secreto)` |
| `R2_ACCOUNT_ID` | Cloudflare Account ID | Si | `(secreto)` |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 Access Key | Si | `(secreto)` |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 Secret Key | Si | `(secreto)` |
| `R2_ENDPOINT` | Endpoint R2 S3-compatible | Si | `https://ACCOUNT_ID.r2.cloudflarestorage.com` |
| `FRONTEND_URL` | URL del frontend (CORS) | No | `https://tu-frontend.tu-dominio.com` |
| `TESTING_MODE` | Modo testing (sin Auth0) | No | `true` / `false` |
| `PORT` | Puerto del servicio | No | `8000` (Docker lo inyecta) |

## GDI-MCP Server (:8005)

Integrado en GDI-Backend (`api_gateway/`). Comparte las variables del Backend mas las siguientes:

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `MCP_RESOURCE_URI` | URI del recurso MCP | No | `https://mcp.tu-dominio.com` |

**Audiences JWT soportados automaticamente:**

- `AUTH0_AUDIENCE` (del Backend)
- `MCP_RESOURCE_URI` (si definida)
- `https://mcp.tu-dominio.com` (hardcodeado)

## GDI-BackOffice-Back (:8010)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DB_HOST` | Host PostgreSQL | Si | `postgres` (Docker) / `localhost` (local) |
| `DB_PORT` | Puerto PostgreSQL | Si | `5432` |
| `DB_USER` | Usuario PostgreSQL | Si | `postgres` |
| `DB_PASSWORD` | Password PostgreSQL | Si | `(secreto)` |
| `DB_NAME` | Nombre de la base de datos | Si | `railway` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Si | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Si | `https://tu-tenant.us.auth0.com/api/v2/` |
| `FRONTEND_URL` | URL del BackOffice Front (CORS) | No | `http://localhost:3013` |
| `BACKOFFICE_URL` | URL propia (referencia) | No | `http://localhost:8010` |
| `RESEND_API_KEY` | API Key de Resend (emails transaccionales) | Si | `re_...` |
| `AUTH0_M2M_CLIENT_ID` | Client ID de app M2M (Management API) | Si | `(secreto)` |
| `AUTH0_M2M_CLIENT_SECRET` | Client Secret de app M2M | Si | `(secreto)` |
| `AUTH0_FRONTEND_CLIENT_ID` | Client ID de app frontend (redirect en password tickets) | No | `(secreto)` |
| `AUTH0_DB_CONNECTION` | Nombre de la Database Connection en Auth0 | No | `Username-Password-Authentication` |
| `TESTING_MODE` | Modo testing | No | `true` / `false` |
| `PORT` | Puerto del servicio | No | `8010` |

!!! info "Email via Resend"
    El envio de emails transaccionales (invitaciones, notificaciones) esta integrado directamente en GDI-BackOffice-Back usando la API de [Resend](https://resend.com). No existe un microservicio de email separado. La variable `RESEND_API_KEY` es necesaria para el envio de correos en produccion.

## GDI-FRONTEND (:3003)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `AUTH0_SECRET` | Secret para sesiones NextAuth | Si | `(secreto largo)` |
| `AUTH0_BASE_URL` | URL base del frontend | Si | `http://localhost:3003` |
| `AUTH0_ISSUER_BASE_URL` | URL de Auth0 | Si | `https://tu-tenant.us.auth0.com` |
| `AUTH0_CLIENT_ID` | Client ID Auth0 | Si | `(secreto)` |
| `AUTH0_CLIENT_SECRET` | Client Secret Auth0 | Si | `(secreto)` |
| `NEXT_PUBLIC_API_URL` | URL del Backend API | Si | `http://localhost:8000` |

## GDI-BackOffice-Front (:3013)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `AUTH0_SECRET` | Secret para sesiones NextAuth | Si | `(secreto largo)` |
| `AUTH0_BASE_URL` | URL base del frontend | Si | `http://localhost:3013` |
| `AUTH0_ISSUER_BASE_URL` | URL de Auth0 | Si | `https://tu-tenant.us.auth0.com` |
| `AUTH0_CLIENT_ID` | Client ID Auth0 | Si | `(secreto)` |
| `AUTH0_CLIENT_SECRET` | Client Secret Auth0 | Si | `(secreto)` |
| `NEXT_PUBLIC_API_URL` | URL del BackOffice Backend | Si | `http://localhost:8010` |

## GDI-AgenteLANG (:8004)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Si | `postgresql://user:pass@host:port/db` |
| `OPENROUTER_API_KEY` | API Key de OpenRouter | Si | `sk-or-...` |
| `OPENROUTER_MODEL` | Modelo LLM principal | Si | `google/gemini-2.0-flash-001` |
| `OPENROUTER_FAST_MODEL` | Modelo para Router (gratis) | Si | `meta-llama/llama-3.3-70b-instruct:free` |
| `EMBEDDINGS_MODEL` | Modelo de embeddings | Si | `openai/text-embedding-3-small` |
| `GDI_BACKEND_URL` | URL del Backend | Si | `http://backend:8000` |
| `INTERNAL_API_KEY` | API Key interna para Backend | Si | `your-internal-api-key` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Si | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Si | `https://api.tu-dominio.com` |
| `AI_WORKER_INTERVAL` | Intervalo del worker (segundos) | No | `60` (default) |
| `AI_WORKER_BATCH_SIZE` | Documentos por batch | No | `10` (default) |
| `ENABLED_SCHEMAS` | Schemas a procesar | No | `["200_muni"]` |
| `TRANSCRIPTION_ENABLED` | Habilitar transcripcion de PDFs | No | `true` (default) |
| `TRANSCRIPTION_VISION_MODEL` | Modelo de vision para OCR | No | `google/gemini-flash-1.5` |
| `TRANSCRIPTION_MAX_FILE_SIZE_MB` | Tamano maximo PDF (MB) | No | `10` |
| `TRANSCRIPTION_MAX_PAGES` | Paginas maximas a transcribir | No | `50` |
| `TRANSCRIPTION_DPI` | Resolucion de renderizado | No | `150` |

## GDI-PDFComposer (:8002)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `API_KEY` | API Key de autenticacion | Si | `(secreto)` |
| `GUNICORN_WORKERS` | Numero de workers | No | `4` (default) |
| `BETTERSTACK_SOURCE_TOKEN` | Token para logging centralizado | No | `(secreto)` |
| `PORT` | Puerto del servicio | No | `8002` |

## GDI-Notary (:8001)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `API_KEY` | API Key de autenticacion | Si | `(secreto)` |
| `ENVIRONMENT` | Ambiente de ejecucion | Si | `test` / `prd` |
| `CERTS_DIR` | Directorio de certificados | No | `./certs` (default) |
| `TSA_URL` | Servidor de timestamp | No | `http://timestamp.digicert.com` |
| `FALLBACK_TO_VISUAL` | Firma visual si no hay cert | No | `true` (test) / `false` (prd) |
| `GUNICORN_WORKERS` | Numero de workers | No | `3` (default) |
| `GUNICORN_TIMEOUT` | Timeout de Gunicorn (seg) | No | `90` (default) |

## GDI-BD (Scripts SQL)

| Variable | Descripcion | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Si | `postgresql://user:pass@host:port/db` |

## Resumen de Variables Compartidas

Algunas variables se repiten en multiples servicios:

| Variable | Servicios que la usan |
|----------|-----------------------|
| `DATABASE_URL` | Backend, AgenteLANG, GDI-BD |
| `AUTH0_DOMAIN` | Backend, BackOffice-Back, AgenteLANG, Frontends |
| `AUTH0_AUDIENCE` | Backend, BackOffice-Back, AgenteLANG |
| `API_KEY` | PDFComposer, Notary |
| `PORT` | Todos (inyectado por Docker) |

!!! warning "Seguridad"
    Nunca commitear archivos `.env` ni credenciales en Git. Todas las variables sensibles deben configurarse en los archivos `.env` del servidor o en Docker Compose.
