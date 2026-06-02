# Desarrollo Local

Guia para levantar el ecosistema GDI Latam en tu maquina local.

## Requisitos

| Software | Version | Notas |
|----------|---------|-------|
| Python | 3.12+ | Backend principal y microservicios |
| Node.js | 20+ | Frontends (Next.js 15) |
| PostgreSQL | 17+ | Con extensiones pgvector, unaccent, pg_trgm |
| Docker | Latest | Para servicios containerizados |
| Git | Latest | Cada subcarpeta es un repo independiente |

!!! tip "Versiones exactas"
    El Backend usa Python 3.12. Los microservicios (PDFComposer, Notary) funcionan con Python 3.11+. Los frontends usan Next.js 15 con React 18.

## Clonar Repositorios

Cada servicio es un repositorio Git independiente. La carpeta raiz **no es un repo**.

```bash
# Crear directorio raiz
mkdir mi-proyecto && cd mi-proyecto

# Backends
git clone <url>/GDI-Backend.git        # API principal (:8000)
git clone <url>/GDI-BackOffice-Back.git # API admin (:8010)

# Frontends
git clone <url>/GDI-FRONTEND.git        # App usuarios (:3003)
git clone <url>/GDI-BackOffice-Front.git # Panel admin (:3013)

# Microservicios
git clone <url>/GDI-PDFComposer.git  # Generador PDFs (:8002)
git clone <url>/GDI-Notary.git       # Firma digital (:8001)
git clone <url>/GDI-AgenteLANG.git   # Agente IA (:8004)

# Base de datos
git clone <url>/GDI-BD.git           # Scripts SQL
```

!!! warning "Git desde raiz"
    Nunca ejecutar comandos `git` desde la carpeta raiz. Siempre operar dentro de cada repo individual o usar `git -C <repo>`.

## Variables de Entorno

Cada servicio necesita su propio archivo `.env`. A continuacion las variables minimas para desarrollo local.

### GDI-Backend (.env)

```bash
# Base de datos
DATABASE_URL=postgresql://postgres:password@localhost:5432/railway

# Auth0 (desactivar para desarrollo)
TESTING_MODE=true

# Microservicios (URLs locales)
PDFCOMPOSER_URL=http://localhost:8002
PDFCOMPOSER_API_KEY=dev-key-pdf
NOTARY_URL=http://localhost:8001
NOTARY_API_KEY=dev-key-notary

# Cloudflare R2
CF_R2_ENDPOINT=https://ACCOUNT_ID.r2.cloudflarestorage.com
CF_R2_ACCESS_KEY_ID=your-access-key
CF_R2_SECRET_ACCESS_KEY=your-secret-key
CF_R2_SIGN_EXPIRATION=600

# CORS
FRONTEND_URL=http://localhost:3003
```

### GDI-BackOffice-Back (.env)

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=railway
TESTING_MODE=true
FRONTEND_URL=http://localhost:3013
```

### GDI-FRONTEND (.env.local)

```bash
AUTH0_SECRET=your-long-secret-string
AUTH0_BASE_URL=http://localhost:3003
AUTH0_ISSUER_BASE_URL=https://tu-tenant.us.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### GDI-BackOffice-Front (.env.local)

```bash
AUTH0_SECRET=your-long-secret-string
AUTH0_BASE_URL=http://localhost:3013
AUTH0_ISSUER_BASE_URL=https://tu-tenant.us.auth0.com
AUTH0_CLIENT_ID=your-bo-client-id
AUTH0_CLIENT_SECRET=your-bo-client-secret
NEXT_PUBLIC_API_URL=http://localhost:8010
```

### GDI-PDFComposer (.env)

```bash
API_KEY=dev-key-pdf
```

### GDI-Notary (.env)

```bash
API_KEY=dev-key-notary
ENVIRONMENT=test
CERTS_DIR=./certs
FALLBACK_TO_VISUAL=true
```

### GDI-AgenteLANG (.env)

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/railway
OPENROUTER_API_KEY=sk-or-your-key
OPENROUTER_MODEL=openai/gpt-4.1-nano
OPENROUTER_FAST_MODEL=openai/gpt-4.1-nano
EMBEDDINGS_MODEL=openai/text-embedding-3-small
GDI_BACKEND_URL=http://localhost:8000
INTERNAL_API_KEY=gdi-internal-dev
AUTH0_DOMAIN=tu-tenant.us.auth0.com
AUTH0_AUDIENCE=https://api.tu-dominio.com
```

Ver referencia completa en [Variables de Entorno](../arquitectura/variables-entorno.md).

## Base de Datos Local

### Opcion A: PostgreSQL local

```bash
# Instalar extensiones (una vez)
psql -U postgres -c "CREATE DATABASE railway;"

# Ejecutar scripts de GDI-BD en orden
cd GDI-BD

# Paso 1: Estructura base (extensiones + tablas public)
psql -U postgres -d railway -f sql/01-install.sql

# Paso 2: Datos globales (roles, document types, case templates)
psql -U postgres -d railway -f sql/02-seed-global.sql

# Paso 3: Schema de prueba 200_muni con datos demo
psql -U postgres -d railway -f sql/04-seed-demo.sql
```

Ver mas detalles en [Base de Datos](../database/index.md) y [Scripts de Deploy](../database/scripts-deploy.md).

## Puertos del Ecosistema

| Servicio | Puerto | URL Local |
|----------|--------|-----------|
| GDI-Backend | 8000 | `http://localhost:8000` |
| GDI-BackOffice-Back | 8010 | `http://localhost:8010` |
| GDI-FRONTEND | 3003 | `http://localhost:3003` |
| GDI-BackOffice-Front | 3013 | `http://localhost:3013` |
| GDI-PDFComposer | 8002 | `http://localhost:8002` |
| GDI-Notary | 8001 | `http://localhost:8001` |
| GDI-AgenteLANG | 8004 | `http://localhost:8004` |
| PostgreSQL | 5432 | `localhost:5432` |

## Orden de Inicio Recomendado

Seguir este orden para evitar errores de dependencia:

### 1. Infraestructura

```bash
# PostgreSQL (si es local, asegurar que este corriendo)
pg_isready -U postgres
```

### 2. Microservicios

```bash
# PDFComposer
cd GDI-PDFComposer
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Notary
cd GDI-Notary
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 3. Backends

```bash
# Backend principal
cd GDI-Backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# BackOffice Backend
cd GDI-BackOffice-Back
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
```

### 4. Frontends

```bash
# Frontend principal
cd GDI-FRONTEND
npm install
npm run dev  # Puerto 3003

# BackOffice Frontend
cd GDI-BackOffice-Front
npm install
npm run dev  # Puerto 3013
```

!!! tip "Inicio minimo"
    Para desarrollo basico de documentos, solo necesitas: PostgreSQL + PDFComposer + Backend + Frontend. Los demas servicios son opcionales segun el feature que trabajes.

## Verificar Instalacion

```bash
# Health checks
curl http://localhost:8000/health   # Backend
curl http://localhost:8010/health   # BackOffice Backend
curl http://localhost:8002/health   # PDFComposer
curl http://localhost:8001/health   # Notary
```

Respuesta esperada del Backend:

```json
{"status": "healthy", "database": "connected"}
```

## Tips de Debug

### TESTING_MODE

Con `TESTING_MODE=true`, el Backend acepta un header `X-User-ID` con el UUID del usuario en lugar de requerir un JWT de Auth0. Esto simplifica el desarrollo local.

```bash
# Request autenticado en modo testing
curl -H "X-User-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
     http://localhost:8000/users
```

### Swagger UI

FastAPI genera documentacion interactiva automaticamente:

- Backend: `http://localhost:8000/docs`
- BackOffice: `http://localhost:8010/docs`
- PDFComposer: `http://localhost:8002/docs`
- Notary: `http://localhost:8001/docs`

### Logs de Backend

El Backend usa un sistema de logging con `correlation_id` para rastrear requests:

```bash
# Los logs incluyen el schema del tenant
[2026-02-16 10:00:00] [req-abc-123] [200_muni] INFO: GET /documents 200
```

### Virtualenvs Python

Se recomienda usar un virtualenv por servicio para evitar conflictos de dependencias:

```bash
cd GDI-Backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Hot Reload

- **Python** (FastAPI): `uvicorn main:app --reload` recarga automaticamente al editar codigo
- **Next.js**: `npm run dev` tiene hot reload incluido

Ver tambien [Troubleshooting](troubleshooting.md) para problemas comunes.
