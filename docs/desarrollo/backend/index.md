# Backend (GDI-Backend)

API REST principal del sistema GDI Latam. Gestiona documentos, expedientes, firmas digitales, usuarios y sectores para gobiernos municipales de Latinoamerica.

## Stack Tecnologico

| Componente | Tecnologia | Version |
|------------|-----------|---------|
| Lenguaje | Python | 3.12 |
| Framework | FastAPI | latest |
| Base de datos | PostgreSQL + pgvector | 17 |
| Driver BD | asyncpg (raw SQL async, sin ORM) | - |
| Validacion | Pydantic | v2 |
| Auth | Auth0 JWT (RS256) | - |
| Storage | Cloudflare R2 (S3-compatible) | - |
| Deploy | Docker (Fly.io) | - |
| Server | Gunicorn + Uvicorn | 2 workers |

## Puerto

| Entorno | Puerto |
|---------|--------|
| Local | `8000` |
| Docker | Variable `PORT` (default 8080) |

## Arquitectura General

```
Cliente (Frontend/MCP)
        |
        v
   FastAPI App (:8000)
        |
        +-- TenantMiddleware (valida schema)
        +-- Auth (JWT Auth0)
        |
        v
   Endpoints (thin controllers)
        |
        v
   Services (logica de negocio)
        |
        +-- GDI-PDFComposer (generar PDFs)
        +-- GDI-Notary (firmar PDFs)
        +-- Cloudflare R2 (almacenar PDFs)
        +-- PostgreSQL (datos)
```

## Principios de Diseno

- **Endpoints thin**: Solo validacion y delegacion a services
- **Services con logica**: Toda la logica de negocio en la capa de servicios
- **Multi-tenant**: Cada organizacion tiene su propio schema en PostgreSQL
- **keyword-only `schema_name`**: Patron obligatorio en todas las funciones de BD
- **Auth0 JWT**: Autenticacion via tokens RS256
- **Async-first**: Endpoints async con `async def`

## Integraciones Externas

| Servicio | URL | Proposito |
|----------|-----|-----------|
| GDI-PDFComposer | `PDFCOMPOSER_URL` (env, Fly.io *.internal:8080) | Generar PDFs (preview, final, CAEX, PV, IFRLM) |
| GDI-Notary | `NOTARY_URL` (env, Fly.io *.internal:8080) | Firma digital multi-firmante |
| Cloudflare R2 | S3-compatible | Almacenamiento de PDFs |
| Auth0 | `<your-tenant>.auth0.com` | Autenticacion OAuth 2.0 |

## Variables de Entorno

| Variable | Descripcion |
|----------|-------------|
| `DATABASE_URL` | Connection string PostgreSQL |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexion individual a BD |
| `AUTH0_DOMAIN` | Dominio Auth0 (`tu-tenant.us.auth0.com`) |
| `AUTH0_AUDIENCE` | Audience Auth0 |
| `AUTH0_CLIENT_ID` | Client ID Auth0 |
| `PDFCOMPOSER_URL` | URL interna GDI-PDFComposer |
| `PDFCOMPOSER_API_KEY` | API Key PDFComposer |
| `NOTARY_URL` | URL interna GDI-Notary |
| `NOTARY_API_KEY` | API Key Notary |
| `R2_ACCOUNT_ID` | Cloudflare account |
| `R2_ACCESS_KEY_ID` | R2 access key |
| `R2_SECRET_ACCESS_KEY` | R2 secret |
| `R2_ENDPOINT` | Endpoint R2 S3-compatible |
| `TESTING_MODE` | `true`/`false` - bypass Auth0 en desarrollo. Requiere `ALLOW_TESTING_MODE_LOCAL=true` en entornos locales sin FLY_APP_NAME |
| `ALLOW_TESTING_MODE_LOCAL` | `true`/`false` - opt-in para activar TESTING_MODE localmente (fail-closed por defecto) |
| `ASYNCPG_MIN_SIZE` | Minimo de conexiones en el pool (default `2`) |
| `ASYNCPG_MAX_SIZE` | Maximo de conexiones en el pool (default `8`) |
| `ASYNCPG_COMMAND_TIMEOUT` | Timeout de comandos SQL en segundos (default `60`) |
| `FRONTEND_URL` | URL/s del frontend (CORS, soporta multiples separadas por coma) |

## Comandos

```bash
# Desarrollo local
uvicorn main:app --reload --port 8000

# Produccion (Docker)
python server.py

# Health check
curl http://localhost:8000/health
```

## Contenido de esta Seccion

| Pagina | Descripcion |
|--------|-------------|
| [Estructura del Proyecto](estructura-proyecto.md) | Arbol de carpetas y organizacion |
| [Models y Schemas](models-schemas.md) | Modelos Pydantic de validacion |
| [Middleware](middleware.md) | TenantMiddleware, CORS |
| [Autenticacion](auth.md) | Auth0, JWT, permisos |
| [Base de Datos](database.md) | Pool, queries, multi-tenant |
| [Endpoints](endpoints/index.md) | Todos los endpoints REST |
| [Services](services/index.md) | Logica de negocio |
| [API Gateway](api-gateway/index.md) | MCP Server + REST API |
