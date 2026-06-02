---
hide:
  - navigation
  - toc
---

# GDI Docs

**Documentacion unificada** del Sistema de Gestion Documental Inteligente para gobiernos LATAM.

Selecciona la seccion que corresponde a tu perfil:

---

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } **Gateway API**

    ---

    Integracion con GDI: MCP Server para agentes IA y REST API para sistemas externos. 45 endpoints documentados.

    [:octicons-arrow-right-24: Ir a Gateway API](desarrollo/gateway/index.md)

-   :material-account:{ .lg .middle } **Usuarios**

    ---

    Manual de usuario: como crear documentos, gestionar expedientes, enviar notas, firmar y usar el asistente AI.

    [:octicons-arrow-right-24: Ir al manual de usuario](usuarios/index.md)

-   :material-shield-account:{ .lg .middle } **Administradores**

    ---

    Panel de administracion (BackOffice): gestion de organizaciones, usuarios, permisos, sectores y configuracion del sistema.

    [:octicons-arrow-right-24: Ir a administracion](administradores/index.md)

-   :material-code-braces:{ .lg .middle } **Desarrollo**

    ---

    Documentacion tecnica por servicio: arquitectura, endpoints, services, database, deploy y guias de desarrollo.

    [:octicons-arrow-right-24: Ir a desarrollo](desarrollo/index.md)

</div>

---

## Stack Tecnologico

| Capa | Tecnologias |
|------|-------------|
| **Frontend** | Next.js 15, React 18, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.12, Auth0, PostgreSQL 17 |
| **Gateway API** | MCP Server (42 tools) + REST API (45 endpoints) |
| **Microservicios** | Notary (pyHanko), AgenteLANG (LangGraph) |
| **Infraestructura** | Docker, Cloudflare R2, GitHub Actions |

## Servicios y Puertos

| Servicio | Puerto | Stack |
|----------|--------|-------|
| GDI-FRONTEND | `:3003` | Next.js 15, React 18, TypeScript |
| GDI-BackOffice-Front | `:3013` | Next.js 15, React 18, TypeScript |
| GDI-Backend | `:8000` | FastAPI, Python 3.12 |
| GDI-BackOffice-Back | `:8010` | FastAPI, Python 3.12 |
| GDI-Gateway | `:8005` | MCP Server + REST API |
| GDI-Notary | `:8001` | FastAPI, pyHanko, PyMuPDF |
| GDI-AgenteLANG | `:8004` | FastAPI, LangGraph, OpenRouter |

---

!!! info "Sobre esta documentacion"
    Esta documentacion esta organizada por audiencia. Cada tab corresponde a un perfil de usuario diferente. Usa el buscador para encontrar cualquier termino en las tres secciones.
