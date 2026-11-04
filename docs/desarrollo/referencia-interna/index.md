---
title: Referencia Interna
description: Documentacion interna para el equipo de desarrollo de GDI Latam.
---

# Referencia Interna

!!! note "Sección interna"
    Esta sección es referencia interna para el equipo de desarrollo de GDI. Si buscás integrar tu sistema con GDI, ve a [Gateway API](../gateway/index.md).

Esta sección contiene la documentación técnica detallada de cada componente del sistema GDI. Aquí encontrarás guías de arquitectura, convenciones de código, configuración de entornos y procedimientos operativos que utiliza el equipo de desarrollo.

---

<div class="grid cards" markdown>

-   **Frontend**

    ---

    Aplicaciones web construidas con Next.js 15, React 18 y TypeScript. Incluye el portal ciudadano y el backoffice administrativo.

    [:octicons-arrow-right-24: Ver documentación](../frontend/index.md)

-   **Backend Services**

    ---

    APIs REST construidas con FastAPI y Python 3.12. Gestionan toda la lógica de negocio, autenticación y comunicación con microservicios.

    [:octicons-arrow-right-24: Ver documentación](../backend/index.md)

-   **Database**

    ---

    PostgreSQL 17 con arquitectura multi-tenant. Cada municipio opera en un schema aislado con pgvector para búsqueda semántica.

    [:octicons-arrow-right-24: Ver documentación](../database/index.md)

-   **Notary**

    ---

    Microservicio de firma digital PAdES. Genera firmas electrónicas válidas sobre documentos PDF con sellado de tiempo.

    [:octicons-arrow-right-24: Ver documentación](../notary/index.md)

-   **Deploy**

    ---

    Infraestructura con Docker, almacenamiento en Cloudflare R2 y CI/CD con GitHub Actions. Incluye guías de despliegue y troubleshooting.

    [:octicons-arrow-right-24: Ver documentación](../deploy/index.md)

</div>
