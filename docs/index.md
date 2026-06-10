---
hide:
  - navigation
  - toc
---

<div class="gdi-hero" markdown>
<span class="gdi-wordmark"><span class="dot"></span> GDI LATAM</span>

# Documentación de GDI Latam

<p class="gdi-lede">Todo lo que necesitás para usar, administrar e integrar la plataforma de <strong>Gestión Documental Inteligente</strong> para gobiernos de América Latina.</p>

<div class="gdi-hero-actions">
<a class="md-button" href="usuarios/">Manual de usuario</a>
<a class="md-button gdi-ghost" href="desarrollo/gateway/">Integrar con la API</a>
</div>
</div>

<span class="gdi-section-eyebrow">Elegí tu sección</span>
## Por dónde empezar

<div class="grid cards" markdown>

-   :material-account:{ .lg .middle } **Usuarios**

    ---

    Cómo crear documentos, gestionar expedientes, enviar notas y memos, firmar con token y usar el asistente AI.

    [:octicons-arrow-right-24: Ir al manual de usuario](usuarios/index.md)

-   :material-shield-account:{ .lg .middle } **Administradores**

    ---

    Panel de administración (BackOffice): organizaciones, usuarios, permisos, sectores, tipos de documento y configuración.

    [:octicons-arrow-right-24: Ir a administración](administradores/index.md)

-   :material-api:{ .lg .middle } **Gateway API**

    ---

    Integración con GDI: MCP Server para agentes IA y REST API para sistemas externos. 45 endpoints documentados.

    [:octicons-arrow-right-24: Ir a Gateway API](desarrollo/gateway/index.md)

-   :material-code-braces:{ .lg .middle } **Desarrollo**

    ---

    Documentación técnica por servicio: arquitectura, endpoints, services, base de datos, deploy y guías.

    [:octicons-arrow-right-24: Ir a desarrollo](desarrollo/index.md)

</div>

!!! info "Sobre esta documentación"
    Está organizada por audiencia: cada perfil tiene su propia sección. Usá el buscador (arriba a la derecha) para encontrar cualquier término en toda la documentación.

---

<span class="gdi-section-eyebrow">Referencia técnica</span>
## Stack y servicios

??? abstract "Stack tecnológico"

    | Capa | Tecnologías |
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
