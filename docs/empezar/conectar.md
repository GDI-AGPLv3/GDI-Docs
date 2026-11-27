---
title: Empezá acá · Conectar otro sistema o una IA
description: Conectá GDI con otro sistema del municipio o con una IA como Claude o ChatGPT.
hide:
  - toc
---

# Conectar otro sistema o una IA

GDI se conecta con los demás sistemas del municipio y con asistentes de IA. ¿Qué querés conectar?

<div class="grid cards gdi-formas" markdown>

-   :material-robot-outline:{ .gdi-forma-icono } **Una IA (Claude, ChatGPT)**

    La IA lee expedientes y documentos, y hasta prepara borradores, con los mismos permisos que la persona que la usa.

    [Conectar una IA (MCP)](../desarrollo/gateway/mcp-server.md)

-   :material-swap-horizontal-bold:{ .gdi-forma-icono } **Otro sistema del municipio**

    Rentas, Personal, Compras: tu sistema crea expedientes, sube documentos y consulta en qué están.

    [Conectar por API](../desarrollo/gateway/rest-api/index.md)

-   :material-account-group-outline:{ .gdi-forma-icono } **El portal de trámites del vecino**

    El vecino inicia el trámite en la web del municipio y llega a GDI como expediente.

    [Conectar el portal](../desarrollo/gateway/rest-api/tad/conectar-portal.md)

-   :material-cog-transfer-outline:{ .gdi-forma-icono } **Configurar el BackOffice con IA**

    Cargar usuarios, sectores o tipos de documento pidiéndoselo a una IA, en vez de hacerlo a mano.

    [Operar el BackOffice por API](../administradores/operar-por-api.md)

</div>

## Antes de empezar

1. **Pedile una clave al administrador de tu municipio.** La crea en el BackOffice, en *API Keys*. Cómo funciona: [Autenticación](../desarrollo/gateway/autenticacion.md).
2. **Probá en un municipio de prueba**, nunca con datos reales.
3. **¿Dudas?** [Preguntale a la IA](https://notebooklm.google.com/notebook/56b820d3-ef1d-403f-bbd2-aa2710e5bdd4){ target="_blank" rel="noopener" } o leé los [flujos completos](../desarrollo/gateway/flujos.md).

??? abstract "Stack tecnológico de GDI"

    | Capa | Tecnologías |
    |------|-------------|
    | **Frontend** | Next.js 15, React 18, TypeScript, Tailwind CSS, shadcn/ui |
    | **Backend** | FastAPI, Python 3.12, OIDC/OAuth 2.0, PostgreSQL 17 |
    | **Gateway API** | MCP Server (42 tools) + REST API (45 endpoints) |
    | **Microservicios** | Notary (pyHanko), AgenteLANG (LangGraph) |
    | **Infraestructura** | Docker, almacenamiento S3 compatible |
