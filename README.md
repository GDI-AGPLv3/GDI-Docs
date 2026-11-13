# GDI Docs

Documentación técnica del sistema de Gestión Documental Inteligente (GDI).

Sitio publicado: **[https://gdi-agplv3.github.io/GDI-Docs/](https://gdi-agplv3.github.io/GDI-Docs/)**

## Build local

```bash
pip install -r requirements.txt
mkdocs serve
```

Luego abrir `http://localhost:8000`.

## Estructura

- `docs/` — Markdown sources organizados por área (backend, frontend, gateway, BD, deploy).
- `mkdocs.yml` — Configuración del sitio.
- `.github/workflows/deploy.yml` — Build automático a GitHub Pages.

## Repos relacionados

- [GDI-Backend](https://github.com/GDI-AGPLv3/GDI-Backend) — API REST + Gateway MCP
- [GDI-Frontend](https://github.com/GDI-AGPLv3/GDI-Frontend) — Next.js
- [GDI-BD](https://github.com/GDI-AGPLv3/GDI-BD) — Schema PostgreSQL multi-tenant

## Licencia

Este proyecto está licenciado bajo la **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Ver el archivo [LICENSE](LICENSE) para los términos completos.
