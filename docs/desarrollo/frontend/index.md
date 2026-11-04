# Frontend - GDI-FRONTEND

GDI-FRONTEND es la aplicación web para usuarios finales del Sistema de Gestión Documental Inteligente. Permite crear, editar, firmar y gestionar documentos oficiales, expedientes administrativos y notas internas.

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | Next.js (Pages Router) | 15.5.9 |
| UI Library | React | 18.3.1 |
| Lenguaje | TypeScript (strict) | 5.x |
| Estilos | Tailwind CSS + tailwindcss-animate | 3.4.3 |
| Componentes UI | shadcn/ui (New York style) | - |
| Primitivas | Radix UI (Dialog, Select, Tabs, Popover, Tooltip, Dropdown) | - |
| Iconos | Lucide React | 0.563.0 |
| Editor Rich Text | React Quill | 2.0.0 |
| Command Palette | cmdk | 1.1.1 |
| Autenticación | Auth0 vía @auth0/nextjs-auth0 | 4.14.0 |
| Deploy | Docker | - |
| Puerto local | 3003 | - |

## Funcionalidades Principales

- **Documentos**: Crear, editar con editor rich text (Quill), previsualizar PDF, enviar a firma
- **Firma Digital**: Proceso de firma multi-firmante con orden secuencial, firma conjunta por lotes
- **Expedientes**: Crear, asignar a sectores, transferir, vincular documentos, timeline de movimientos
- **Notas Internas**: Enviar/recibir notas entre sectores con destinatarios TO/CC/BCC y archivado
- **Dashboard**: Feed de actividad con movimientos de expedientes, estadísticas por sector
- **Búsqueda Unificada**: Buscar documentos y expedientes por número oficial o texto libre
- **Asistente IA**: Chat con agente inteligente por expediente o general (RAG)
- **Multi-Tenant**: Soporte para múltiples organizaciones con colores dinámicos por tenant

## Comunicación con Backend

El frontend se comunica con GDI-Backend (:8000) exclusivamente a través de API Routes de Next.js (`/api/*`), que actuan como proxy server-side. El cliente nunca contacta al backend directamente.

```
Browser  -->  Next.js API Route (/api/*)  -->  GDI-Backend (:8000)
                  (server-side proxy)
```

## Subsecciones

| Sección | Descripción |
|---------|-------------|
| [Estructura del Proyecto](estructura-proyecto.md) | Árbol de carpetas y organización del código |
| [Páginas](paginas.md) | Todas las rutas y páginas de la aplicación |
| [Componentes](componentes.md) | Inventario de componentes por módulo |
| [Hooks](hooks.md) | Custom hooks con parámetros y tipos de retorno |
| [Types](types.md) | Interfaces TypeScript agrupadas por dominio |
| [Lib y Utilidades](lib-utils.md) | fetchWithAuth, tenant utils, theme, validación |
| [Middleware y Auth](middleware-auth.md) | Flujo Auth0 completo y protección de rutas |
| [Design System](design-system.md) | Colores, badges, iconografía y patrones de layout |
| [API Routes](api-routes.md) | Proxy routes y endpoints del backend |

## Comandos

```bash
# Desarrollo local (puerto 3003)
npm run dev

# Build de produccion
npm run build

# Iniciar en produccion
npm run start

# Linting
npm run lint
```

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `AUTH0_SECRET` | Secret para cifrado de sesiones |
| `AUTH0_BASE_URL` | URL base de la aplicación (ej: `http://localhost:3003`) |
| `AUTH0_ISSUER_BASE_URL` | URL del tenant Auth0 |
| `AUTH0_CLIENT_ID` | Client ID de la aplicación en Auth0 |
| `AUTH0_CLIENT_SECRET` | Client Secret de Auth0 |
| `AUTH0_AUDIENCE` | API Audience de Auth0 |
| `NEXT_PUBLIC_API_URL` | URL del backend API (ej: `http://localhost:8000`) |
| `NEXT_PUBLIC_ENV` | Entorno: `production` o vacío para desarrollo |
