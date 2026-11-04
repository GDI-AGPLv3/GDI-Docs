# Variables de Entorno

Tabla consolidada de todas las variables de entorno del ecosistema GDI, agrupadas por servicio.

## GDI-Backend (:8000)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Sí | `postgresql://user:pass@host:port/db` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Sí | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Sí | `https://api.tu-dominio.com` |
| `PDFCOMPOSER_URL` | URL de GDI-PDFComposer | Sí | `http://pdfcomposer:8002` |
| `PDFCOMPOSER_API_KEY` | API Key para PDFComposer | Sí | `(secreto)` |
| `NOTARY_URL` | URL de GDI-Notary | Sí | `http://notary:8001` |
| `NOTARY_API_KEY` | API Key para Notary | Sí | `(secreto)` |
| `R2_ACCOUNT_ID` | Cloudflare Account ID | Sí | `(secreto)` |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 Access Key | Sí | `(secreto)` |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 Secret Key | Sí | `(secreto)` |
| `R2_ENDPOINT` | Endpoint R2 S3-compatible | Sí | `https://ACCOUNT_ID.r2.cloudflarestorage.com` |
| `FRONTEND_URL` | URL del frontend (CORS) | No | `https://tu-frontend.tu-dominio.com` |
| `TESTING_MODE` | Modo testing (sin Auth0) | No | `true` / `false` |
| `PORT` | Puerto del servicio | No | `8000` (Docker lo inyecta) |
| `BACKEND_ROLE` | Qué corre el proceso: `all` = API + trabajos de fondo; `web` = solo API; `worker` = solo trabajos de fondo (`python -m workers.run_all`). Un valor inválido frena el arranque | No | `all` (default) |
| `ALERT_AMBIENTE` | Nombre del ambiente en `/api/v1/system/health` y en los mails de alerta. Si falta, se usa `SENTRY_ENV` | No | `prd` |
| `SENTRY_ENV` | Marca de ambiente cuando falta `ALERT_AMBIENTE`. Sin ninguna de las dos, en una instalación propia la marca es `local` | No | `prd` |
| `BOOT_DB_WAIT_SECONDS` | Segundos que el arranque espera a que la base responda | No | `90` (default) |
| `DB_WATCHDOG_ESCALATE_AFTER_SECONDS` | Segundos sin llegar a Postgres antes de que el proceso salga (código `3`) para que el orquestador lo reinicie | No | `180` (default) |
| `DB_WATCHDOG_ESCALATE_MIN_GAP_SECONDS` | Tiempo mínimo entre dos salidas de ese tipo | No | `300` (default) |

!!! info "Procesos y chequeos de salud"
    Cómo separar la API de los trabajos de fondo, qué devuelve cada chequeo de salud y por qué
    `/health/db` responde `404` detrás de un proxy: ver [Backend › Procesos](../backend/index.md#procesos-backend_role).

## GDI-MCP Server (:8005)

Integrado en GDI-Backend (`api_gateway/`). Comparte las variables del Backend más las siguientes:

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `MCP_RESOURCE_URI` | URI del recurso MCP | No | `https://mcp.tu-dominio.com` |

**Audiences JWT soportados automáticamente:**

- `AUTH0_AUDIENCE` (del Backend)
- `MCP_RESOURCE_URI` (si definida)
- `https://mcp.tu-dominio.com` (hardcodeado)

## GDI-BackOffice-Back (:8010)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DB_HOST` | Host PostgreSQL | Sí | `postgres` (Docker) / `localhost` (local) |
| `DB_PORT` | Puerto PostgreSQL | Sí | `5432` |
| `DB_USER` | Usuario PostgreSQL | Sí | `postgres` |
| `DB_PASSWORD` | Password PostgreSQL | Sí | `(secreto)` |
| `DB_NAME` | Nombre de la base de datos | Sí | `railway` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Sí | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Sí | `https://tu-tenant.us.auth0.com/api/v2/` |
| `FRONTEND_URL` | URL del BackOffice Front (CORS) | No | `http://localhost:3013` |
| `BACKOFFICE_URL` | URL propia (referencia) | No | `http://localhost:8010` |
| `RESEND_API_KEY` | API Key de Resend (emails transaccionales) | Sí | `re_...` |
| `AUTH0_M2M_CLIENT_ID` | Client ID de app M2M (Management API) | Sí | `(secreto)` |
| `AUTH0_M2M_CLIENT_SECRET` | Client Secret de app M2M | Sí | `(secreto)` |
| `AUTH0_FRONTEND_CLIENT_ID` | Client ID de app frontend (redirect en password tickets) | No | `(secreto)` |
| `AUTH0_DB_CONNECTION` | Nombre de la Database Connection en Auth0 | No | `Username-Password-Authentication` |
| `TESTING_MODE` | Modo testing | No | `true` / `false` |
| `PORT` | Puerto del servicio | No | `8010` |

!!! info "Email vía Resend"
    El envío de emails transaccionales (invitaciones, notificaciones) está integrado directamente en GDI-BackOffice-Back usando la API de [Resend](https://resend.com). No existe un microservicio de email separado. La variable `RESEND_API_KEY` es necesaria para el envío de correos en producción.

## GDI-FRONTEND (:3003)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `AUTH0_SECRET` | Secret para sesiones NextAuth | Sí | `(secreto largo)` |
| `AUTH0_BASE_URL` | URL base del frontend | Sí | `http://localhost:3003` |
| `AUTH0_ISSUER_BASE_URL` | URL de Auth0 | Sí | `https://tu-tenant.us.auth0.com` |
| `AUTH0_CLIENT_ID` | Client ID Auth0 | Sí | `(secreto)` |
| `AUTH0_CLIENT_SECRET` | Client Secret Auth0 | Sí | `(secreto)` |
| `NEXT_PUBLIC_API_URL` | URL del Backend API | Sí | `http://localhost:8000` |

## GDI-BackOffice-Front (:3013)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `AUTH0_SECRET` | Secret para sesiones NextAuth | Sí | `(secreto largo)` |
| `AUTH0_BASE_URL` | URL base del frontend | Sí | `http://localhost:3013` |
| `AUTH0_ISSUER_BASE_URL` | URL de Auth0 | Sí | `https://tu-tenant.us.auth0.com` |
| `AUTH0_CLIENT_ID` | Client ID Auth0 | Sí | `(secreto)` |
| `AUTH0_CLIENT_SECRET` | Client Secret Auth0 | Sí | `(secreto)` |
| `NEXT_PUBLIC_API_URL` | URL del BackOffice Backend | Sí | `http://localhost:8010` |

## GDI-AgenteLANG (:8004)

!!! info "Stack LLM"
    GDI-AgenteLANG usa **exclusivamente GPT-4.1-nano** vía OpenRouter para todos los nodos (router, respond, resume, transcripción). Los embeddings usan `openai/text-embedding-3-small` (1536 dims) también vía OpenRouter con la misma API key.

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Sí | `postgresql://user:pass@host:port/db` |
| `OPENROUTER_API_KEY` | API Key de OpenRouter | Sí | `sk-or-...` |
| `OPENROUTER_MODEL` | Modelo LLM principal | Sí | `openai/gpt-4.1-nano` |
| `OPENROUTER_FAST_MODEL` | Modelo para Router | Sí | `openai/gpt-4.1-nano` |
| `EMBEDDINGS_MODEL` | Modelo de embeddings (vía OpenRouter) | Sí | `openai/text-embedding-3-small` |
| `GDI_BACKEND_URL` | URL del Backend | Sí | `http://localhost:8000` (dev) / `http://{cliente}-backend-prd.internal:8080` (prd) |
| `GDI_GATEWAY_URL` | URL del Gateway MCP | Sí | `http://localhost:8005` (dev) / `http://{cliente}-gateway-prd.internal:8080` (prd) |
| `INTERNAL_API_KEY` | API Key interna compartida con Backend (1 por ambiente) | Sí | `(secreto)` |
| `AUTH0_DOMAIN` | Dominio Auth0 | Sí | `<your-tenant>.auth0.com` |
| `AUTH0_AUDIENCE` | Audience Auth0 | Sí | `https://<your-tenant>.auth0.com/api/v2/` |
| `ALLOW_TEST_MODE` | Permite modo test sin auth (solo dev) | No | `false` (default en prd) |
| `AI_WORKER_INTERVAL` | Intervalo del worker (segundos) | No | `60` (default) |
| `AI_WORKER_BATCH_SIZE` | Documentos por batch | No | `10` (default) |
| `TRANSCRIPTION_ENABLED` | Habilitar transcripción de PDFs | No | `true` (default) |
| `TRANSCRIPTION_VISION_MODEL` | Modelo de visión para OCR | No | `openai/gpt-4.1-nano` |
| `TRANSCRIPTION_MAX_FILE_SIZE_MB` | Tamaño máximo PDF (MB) | No | `10` |
| `TRANSCRIPTION_MAX_PAGES` | Páginas máximas a transcribir | No | `50` |
| `TRANSCRIPTION_DPI` | Resolución de renderizado | No | `150` |

!!! warning "ENABLED_SCHEMAS removida"
    La variable `ENABLED_SCHEMAS` fue eliminada. El AIWorker descubre automáticamente los schemas a procesar desde `public.ai_usage_limits` en la BD.

## GDI-PDFComposer (:8002)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `API_KEY` | API Key de autenticación | Sí | `(secreto)` |
| `GUNICORN_WORKERS` | Número de workers | No | `4` (default) |
| `BETTERSTACK_SOURCE_TOKEN` | Token para logging centralizado | No | `(secreto)` |
| `PORT` | Puerto del servicio | No | `8002` |

## GDI-Notary (:8001)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `API_KEY` | API Key de autenticación | Sí | `(secreto)` |
| `ENVIRONMENT` | Ambiente de ejecución | Sí | `test` / `prd` |
| `CERTS_DIR` | Directorio de certificados | No | `./certs` (default) |
| `TSA_URL` | Servidor de timestamp | No | `http://timestamp.digicert.com` |
| `FALLBACK_TO_VISUAL` | Firma visual si no hay cert | No | `true` (test) / `false` (prd) |
| `GUNICORN_WORKERS` | Número de workers | No | `3` (default) |
| `GUNICORN_TIMEOUT` | Timeout de Gunicorn (seg) | No | `90` (default) |

## GDI-BD (Scripts SQL)

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | Sí | `postgresql://user:pass@host:port/db` |

## Resumen de Variables Compartidas

Algunas variables se repiten en múltiples servicios:

| Variable | Servicios que la usan |
|----------|-----------------------|
| `DATABASE_URL` | Backend, AgenteLANG, GDI-BD |
| `AUTH0_DOMAIN` | Backend, BackOffice-Back, AgenteLANG, Frontends |
| `AUTH0_AUDIENCE` | Backend, BackOffice-Back, AgenteLANG |
| `API_KEY` | PDFComposer, Notary |
| `PORT` | Todos (inyectado por Docker) |

!!! warning "Seguridad"
    Nunca commitear archivos `.env` ni credenciales en Git. Todas las variables sensibles deben configurarse en los archivos `.env` del servidor o en Docker Compose.
