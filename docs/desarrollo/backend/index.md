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
| `BACKEND_ROLE` | `all` (default), `web` o `worker`: que parte del Backend corre este proceso. Ver [Procesos](#procesos-backend_role) |
| `ALERT_AMBIENTE` | Nombre del ambiente en `GET /api/v1/system/health` y en los mails de alerta (ej. `prd`). Si falta, se usa `SENTRY_ENV` |
| `BOOT_DB_WAIT_SECONDS` | Segundos que el arranque espera a la base si no responde (default `90`) |
| `DB_WATCHDOG_ESCALATE_AFTER_SECONDS` | Segundos sin conexion a Postgres antes de que el proceso salga para que lo reinicien (default `180`) |
| `DB_WATCHDOG_ESCALATE_MIN_GAP_SECONDS` | Tiempo minimo entre dos salidas de ese tipo (default `300`) |

## Comandos

```bash
# Desarrollo local
uvicorn main:app --reload --port 8000

# Produccion (Docker): la imagen arranca con
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind "[::]:8080" --workers 2

# Health check
curl http://localhost:8000/health
```

## Procesos (`BACKEND_ROLE`)

El Backend tiene dos partes: la API HTTP y los trabajos de fondo (cola de firma, avisos de TAD
por webhook y tareas programadas). `BACKEND_ROLE` elige cuales corre cada proceso:

| Valor | Que corre | Como se arranca |
|-------|-----------|-----------------|
| `all` (default) | API + trabajos de fondo, en un solo proceso | `gunicorn main:app -k uvicorn.workers.UvicornWorker` (lo que hace la imagen Docker) |
| `web` | Solo la API. Los trabajos de fondo tienen que correr en otro proceso | Igual que `all` |
| `worker` | Solo los trabajos de fondo. No monta rutas de negocio, solo `/health` | `python -m workers.run_all` |

- Sin la variable (o vacia), el rol es `all`.
- Un valor distinto de `all`, `web` o `worker` **frena el arranque** con un error que lo explica.
- Con `web`, levantar **un solo** proceso `worker`: se arranca con uvicorn de un proceso, no con varios workers de gunicorn.
- El proceso `worker` devuelve a la cola las firmas en curso cuando recibe `SIGTERM`. El tiempo de apagado del contenedor tiene que ser mayor que `ESCRI_SHUTDOWN_GRACE_SECONDS`.

## Chequeos de salud

| Ruta | Que dice | Codigos |
|------|----------|---------|
| `GET /livez` | El proceso esta vivo. No mira la base | `200` |
| `GET /health` | Version, `backend_role` y estado del worker de firma | `200`. Con `BACKEND_ROLE=worker`: `503` si la cola, los avisos de TAD o el programador de tareas no andan |
| `GET /health/db` | El proceso llega a Postgres (`SELECT 1` con tope de 2 s) | `200` `{"status": "ok"}` o `{"status": "busy"}` (pool lleno: la base esta, atendiendo); `503` `{"status": "fail"}` |

!!! warning "`/health/db` no se puede usar desde Internet"
    Si el pedido trae alguna cabecera que agrega un proxy (`X-Forwarded-For`, `Forwarded`,
    `X-Real-IP` y similares), `/health/db` responde `404`. Asi nadie de afuera lo usa para
    ocupar conexiones de la base. El chequeo de salud del contenedor tiene que llamar directo
    al puerto del servicio, sin pasar por el proxy. La respuesta nunca trae el detalle del
    error: ese detalle va al log.

**Si la base se cae:**

1. Al arrancar, el Backend reintenta la conexion hasta `BOOT_DB_WAIT_SECONDS` (90 s). Una contrasena mal o una base inexistente fallan en el acto, sin esperar.
2. Con el servicio andando, un vigilante revisa la conexion. Si no llega a Postgres durante `DB_WATCHDOG_ESCALATE_AFTER_SECONDS` (3 min), el proceso sale con codigo `3` y deja un aviso en el log y por mail.
3. El orquestador (Docker, systemd o la plataforma) tiene que **reiniciar el contenedor** cuando sale. Con la base de vuelta, el Backend arranca solo.

El Gateway hace lo mismo: tiene su propio `/health/db` y su vigilante.

## Ultimo acceso de los usuarios

`users.last_access` se actualiza **como mucho una vez cada 5 minutos** por usuario, no en cada
pedido. Un valor de hace menos de 5 minutos quiere decir "usa el sistema ahora".

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
