---
hide:
  - navigation
  - toc
---

<div class="gdi-hero" markdown>
<span class="gdi-wordmark"><span class="dot"></span> GDI LATAM</span>

# Documentacion de GDI Latam

<p class="gdi-lede">Todo lo que necesitas para usar, administrar e integrar la plataforma de <strong>Gestion Documental Inteligente</strong> para gobiernos de America Latina.</p>

<div class="gdi-hero-actions">
<a class="md-button" href="usuarios/">Manual de usuario</a>
<a class="md-button gdi-ghost" href="desarrollo/gateway/">Integrar con la API</a>
</div>
</div>

<span class="gdi-section-eyebrow">Elegi tu seccion</span>
## Por donde empezar

<div class="grid cards" markdown>

-   :material-account:{ .lg .middle } **Usuarios**

    ---

    Como crear documentos, gestionar expedientes, enviar notas y memos, firmar con token y usar el asistente AI.

    [:octicons-arrow-right-24: Ir al manual de usuario](usuarios/index.md)

-   :material-shield-account:{ .lg .middle } **Administradores**

    ---

    Panel de administracion (BackOffice): organizaciones, usuarios, permisos, sectores, tipos de documento y configuracion.

    [:octicons-arrow-right-24: Ir a administracion](administradores/index.md)

-   :material-api:{ .lg .middle } **Gateway API**

    ---

    Integracion con GDI: MCP Server para agentes IA y REST API para sistemas externos. 45 endpoints documentados.

    [:octicons-arrow-right-24: Ir a Gateway API](desarrollo/gateway/index.md)

-   :material-code-braces:{ .lg .middle } **Desarrollo**

    ---

    Documentacion tecnica por servicio: arquitectura, endpoints, services, base de datos, deploy y guias.

    [:octicons-arrow-right-24: Ir a desarrollo](desarrollo/index.md)

</div>

!!! info "Sobre esta documentacion"
    Esta organizada por audiencia: cada perfil tiene su propia seccion. Usa el buscador (arriba a la derecha) para encontrar cualquier termino en toda la documentacion.

---

<span class="gdi-section-eyebrow">Referencia tecnica</span>
## Stack y servicios

??? abstract "Stack tecnologico"

    | Capa | Tecnologias |
    |------|-------------|
    | **Frontend** | Next.js 15, React 18, TypeScript, Tailwind CSS, shadcn/ui |
    | **Backend** | FastAPI, Python 3.12, Auth0, PostgreSQL 17 |
    | **Gateway API** | MCP Server (42 tools) + REST API (45 endpoints) |
    | **Microservicios** | Notary (pyHanko), AgenteLANG (LangGraph) |
    | **Infraestructura** | Docker, Cloudflare R2, GitHub Actions |

??? abstract "Servicios y puertos (desarrollo local)"

    | Servicio | Puerto | Stack |
    |----------|--------|-------|
    | GDI-FRONTEND | `:3003` | Next.js 15, React 18, TypeScript |
    | GDI-BackOffice-Front | `:3013` | Next.js 15, React 18, TypeScript |
    | GDI-Backend | `:8000` | FastAPI, Python 3.12 |
    | GDI-BackOffice-Back | `:8010` | FastAPI, Python 3.12 |
    | GDI-Gateway | `:8005` | MCP Server + REST API |
    | GDI-Notary | `:8001` | FastAPI, pyHanko, PyMuPDF |
    | GDI-AgenteLANG | `:8004` | FastAPI, LangGraph, OpenRouter |
