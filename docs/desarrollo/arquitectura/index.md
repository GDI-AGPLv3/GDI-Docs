# Visión General de la Arquitectura

GDI Latam es un **Sistema de Gestión Documental Inteligente** para gobiernos y organizaciones de América Latina. La plataforma permite crear, firmar, numerar y gestionar documentos oficiales y expedientes administrativos de forma digital.

## Tabla de Servicios

| Servicio | Stack | Puerto | Repositorio | Descripción |
|----------|-------|--------|-------------|-------------|
| GDI-FRONTEND | Next.js 15, React 18, TypeScript, Tailwind, shadcn/ui | 3003 | GDI-FRONTEND | Aplicación de usuarios finales |
| GDI-BackOffice-Front | Next.js 15, React 18, TypeScript, Tailwind | 3013 | GDI-BackOffice-Front | Panel de administración |
| GDI-Backend | Python 3.12, FastAPI, Pydantic, PostgreSQL 17 | 8000 | GDI-Backend | API principal de gestión documental |
| GDI-BackOffice-Back | Python 3.12, FastAPI, psycopg2 | 8010 | GDI-BackOffice-Back | API de administración (49 endpoints + MCP) |
| GDI-MCP Server | FastAPI, MCP Protocol, OAuth 2.0 | 8005 | GDI-Backend (api_gateway/) | Server MCP para IA externa |
| GDI-AgenteLANG | FastAPI, LangGraph, OpenRouter, pgvector | 8004 | GDI-AgenteLANG | Agente IA con RAG y chat |
| GDI-PDFComposer | FastAPI, Jinja2, WeasyPrint, PyMuPDF | 8002 | GDI-PDFComposer | Motor de generación de PDFs |
| GDI-Notary | FastAPI, pyHanko, PyMuPDF, ReportLab | 8001 | GDI-Notary | Firma digital PAdES y visual |

## Principios Arquitectónicos

### Separación de responsabilidades

Cada capa del sistema tiene una responsabilidad clara e inviolable:

- **Frontends**: Solo interfaz de usuario. Sin lógica de negocio.
- **Backends**: Toda la lógica de negocio, validaciones y orquestación.
- **Microservicios**: Funciones atómicas y stateless (generar PDF, firmar).
- **Base de datos**: PostgreSQL como fuente de verdad, con pgvector para búsqueda semántica.

### Multi-tenant por schema

Cada organización opera en su propio schema de PostgreSQL. Esto garantiza aislamiento total de datos entre organizaciones sin necesidad de bases de datos separadas.

```
PostgreSQL
├── public             # Tablas globales (roles, tipos globales, api_keys)
├── 200_muni           # Schema del municipio "Test" (33 tablas)
├── 200_muni_audit     # Auditoria del municipio "Test"
├── 200_ejemplo          # Schema de otro municipio
└── 200_ejemplo_audit    # Su auditoria
```

!!! warning "Regla crítica: schema_name keyword-only"
    Todas las funciones que acceden a BD usan `schema_name` como parámetro keyword-only.
    Siempre escribir `schema_name=schema_name`, nunca posicional.

### Microservicios stateless

Los microservicios (PDFComposer, Notary) no mantienen estado propio. Reciben un request, procesan y responden. Esto permite escalar horizontalmente sin complejidad.

La única excepción parcial es **GDI-AgenteLANG**, que mantiene un AIWorker background para procesamiento asincrono de resúmenes, embeddings y transcripciones.

### Comunicación sincrona vía REST

Todos los servicios se comunican vía HTTP REST. No se usan colas de mensajes, gRPC ni WebSockets. La simplicidad de REST sincrono es suficiente para el volumen actual y reduce la complejidad operativa.

| Patrón | Solución adoptada | Alternativa evitada |
|--------|-------------------|---------------------|
| Comunicación entre servicios | REST sincrono | gRPC, GraphQL |
| Cola de tareas | PostgreSQL polling (AIWorker) | Redis, RabbitMQ |
| Cache | No se usa (aún) | Redis prematuro |
| Real-time | Polling / SSE | WebSockets |
| Autenticación | Auth0 JWT (OAuth 2.0) | Autenticación custom |

### Storage distribuido

- **PDFs**: Cloudflare R2 (S3-compatible) con dos buckets por tenant: `tosign` (pendientes) y `oficial` (firmados).
- **Embeddings**: pgvector en PostgreSQL para búsqueda semántica RAG.
- **Imágenes de config**: Cloudflare R2 (logos, isologos) gestionados por BackOffice.

### Deploy en Fly.io y Vercel

Cada servicio backend se empaqueta como imagen Docker y se despliega en **Fly.io** vía GitHub Actions. Los frontends Next.js se despliegan en **Vercel** automáticamente al hacer push. La comunicación interna entre microservicios usa la red privada de Fly.io (`*.internal`) para menor latencia y mayor seguridad, sin exponer puertos públicos para PDFComposer y Notary en PRD.

## Repositorios

El proyecto está organizado como **multi-repo**: cada carpeta en el directorio raíz es un repositorio Git independiente. No es un monorepo.

```
APP-GDILatam/         # Directorio raiz (NO es repo git)
├── GDI-FRONTEND/      # App usuarios (Next.js :3003 local, Vercel PRD)
├── GDI-Backend/       # API principal + MCP Gateway (FastAPI :8000/:8005 local, :8080 Fly.io)
├── GDI-BackOffice-Front/  # Admin UI (Next.js :3013 local, Vercel PRD)
├── GDI-BackOffice-Back/   # Admin API (FastAPI :8010 local, :8080 Fly.io)
├── GDI-AgenteLANG/    # Agente IA (FastAPI :8004 local, :8080 Fly.io)
├── GDI-PDFComposer/   # Genera PDFs (FastAPI :8002 local, :8080 Fly.io internal-only PRD)
├── GDI-Notary/        # Firma digital (FastAPI :8001 local, :8080 Fly.io internal-only PRD)
├── GDI-BD/            # Scripts SQL de BD
└── GDI-Docs/          # Esta documentacion
```

!!! info "Git multi-repo"
    Nunca ejecutar `git` desde el directorio raíz. Siempre usar `git -C <repo>` para operar sobre un repositorio específico.
