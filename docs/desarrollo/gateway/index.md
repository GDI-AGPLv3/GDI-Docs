---
hide:
  - toc
---

# Gateway API

**Interfaz publica para integrar sistemas externos con el Sistema de Gestion Documental Inteligente (GDI).**

| Propiedad | Valor |
|-----------|-------|
| Puerto | `:8005` (desarrollo), `:8080` (Docker interno) |
| Framework | FastAPI (ASGI), Python 3.12 |
| Auth MCP | OAuth 2.0 via Auth0 (JWT) |
| Auth REST | API Key + X-User-ID |
| Deploy | Docker |

---

## Que es el Gateway

El Gateway es el punto de entrada para que **sistemas externos** interactuen con GDI sin acceder directamente al Backend. Cualquier municipio que necesite conectar su sistema de tramites, tableros de control, scripts de automatizacion o agentes de inteligencia artificial puede hacerlo a traves de esta API.

El Gateway expone **dos interfaces** segun el tipo de cliente:

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } **MCP Server**

    ---

    Protocolo estandar para **agentes de inteligencia artificial** (Claude, ChatGPT, Gemini). Autenticacion automatica via OAuth 2.0. El agente se conecta, se autentica con su cuenta de usuario y opera con los mismos permisos que tendria en la interfaz web.

    **42 tools** (lectura y escritura).

    [:octicons-arrow-right-24: Ver MCP Server](mcp-server.md)

-   :material-code-json:{ .lg .middle } **REST API**

    ---

    Endpoints HTTP clasicos para **scripts, bots, sistemas de tramites y aplicaciones externas**. Autenticacion por API Key + User ID. Ideal para integraciones programaticas donde no se necesita un agente IA.

    **80+ endpoints** organizados por dominio.

    [:octicons-arrow-right-24: Ver REST API](rest-api/index.md)

</div>

---

## Arquitectura

```mermaid
flowchart LR
    subgraph ext["Sistemas Externos"]
        MCP["Agentes IA<br/>(Claude, ChatGPT, Gemini)"]
        REST["Scripts, Bots,<br/>Sistemas de Tramites"]
    end

    subgraph gw["Gateway API (:8005)"]
        MCPS["MCP Server<br/>POST /mcp"]
        RESTAPI["REST API<br/>/api/v1/*"]
    end

    subgraph back["GDI Backend Services"]
        TOOLS["Tools Layer<br/>cases | documents | system | notes"]
        DB[("PostgreSQL<br/>Multi-tenant")]
        R2[("Cloudflare R2<br/>Storage")]
    end

    MCP -->|"OAuth 2.0<br/>(Auth0 JWT)"| MCPS
    REST -->|"API Key +<br/>X-User-ID"| RESTAPI
    MCPS --> TOOLS
    RESTAPI --> TOOLS
    TOOLS --> DB
    TOOLS --> R2
```

!!! info "Misma logica, distinta interfaz"
    Ambas interfaces (MCP y REST) comparten la misma capa de tools internamente. Un `search_cases` por MCP ejecuta exactamente el mismo codigo que `GET /api/v1/cases/search` por REST. La unica diferencia es el metodo de autenticacion y el formato de entrada/salida.

---

## Resumen de Operaciones

El Gateway organiza sus operaciones en **4 dominios funcionales**:

### Expedientes

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Buscar expedientes | `search_cases` | `GET /api/v1/cases/search` |
| Detalle de expediente | `get_case` | `GET /api/v1/cases/{id}` |
| Historial de movimientos | `get_case_history` | `GET /api/v1/cases/{id}/history` |
| Documentos del expediente | `get_case_documents` | `GET /api/v1/cases/{id}/documents` |
| Permisos del usuario | `get_case_permissions` | `GET /api/v1/cases/{id}/permissions` |
| Buscar por numero | `get_case_by_number` | `GET /api/v1/cases/number/{number}` |
| Preparar pase | `prepare_assignment` | `GET /api/v1/cases/{id}/prepare-assignment` |
| Ejecutar pase | `assign_case` | `POST /api/v1/cases/{id}/assign` |
| Cerrar pase | - | `POST /api/v1/cases/{id}/close-assign` |
| Preparar transferencia | - | `GET /api/v1/cases/{id}/prepare-transfer` |
| Transferir | - | `POST /api/v1/cases/{id}/transfer` |
| Crear expediente | - | `POST /api/v1/cases/` |
| Responsables: listar | `get_case_responsibles` | `GET /api/v1/cases/{id}/responsibles` |
| Responsables: agregar | `add_case_responsible` | `POST /api/v1/cases/{id}/responsibles` |
| Responsables: quitar | `remove_case_responsible` | `DELETE /api/v1/cases/{id}/responsibles/{rid}` |
| Subsanar documento | - | `POST /api/v1/cases/{id}/subsanar` |
| Movimientos planos | - | `GET /api/v1/cases/{id}/movements` |
| Usuarios de sector | - | `GET /api/v1/cases/sectors/{sector_id}/users` |
| Templates disponibles | `get_case_templates` | `GET /api/v1/system/case-templates` |

### Documentos

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Buscar documentos | `search_documents` | `GET /api/v1/documents/search` |
| Detalle de documento | `get_document` | `GET /api/v1/documents/{id}` |
| Contenido HTML | `get_document_content` | `GET /api/v1/documents/{id}/content` |
| URL temporal PDF | - | `GET /api/v1/documents/{id}/url` |
| Firmas pendientes | `get_pending_signatures` | `GET /api/v1/documents/pending-signatures` |
| Buscar por numero oficial | `search_document_by_number` | `GET /api/v1/documents/search-official/{num}` |
| Detalles de firma | `get_signature_details` | `GET /api/v1/documents/{id}/signature-details` |
| Verificar permisos firma | - | `GET /api/v1/documents/check-signer-permissions` |
| Crear documento | `create_document` | `POST /api/v1/documents/` |
| Guardar borrador | `save_document` | `PATCH /api/v1/documents/{id}` |
| Eliminar borrador | - | `DELETE /api/v1/documents/{id}` |
| Importar PDF externo | - | `POST /api/v1/documents/import` |
| Reemplazar PDF importado | - | `PUT /api/v1/documents/{id}/imported-pdf` |
| Iniciar firma | `start_signing` | `POST /api/v1/documents/{id}/start-signing` |
| Firmar documento | - | `POST /api/v1/documents/{id}/sign` |
| Rechazar documento | `reject_document` | `POST /api/v1/documents/{id}/reject` |
| Proponer borrador a exp. | `propose_document` | `POST /api/v1/cases/{id}/documents/propose` |
| Vincular doc oficial | - | `POST /api/v1/cases/{id}/documents/link` |
| Aceptar propuesta | - | `POST /api/v1/cases/{id}/documents/accept-proposal` |
| Rechazar propuesta | `reject_proposal` | `POST /api/v1/cases/{id}/documents/reject-proposal` |

### Sistema y Catalogos

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Tipos de documentos | `get_document_types` | `GET /api/v1/system/document-types` |
| Estados de documentos | `get_document_states` | `GET /api/v1/system/document-states` |
| Sectores y departamentos | - | `GET /api/v1/system/sectors` |
| Templates de expedientes | `get_case_templates` | `GET /api/v1/system/case-templates` |
| Listar usuarios | - | `GET /api/v1/system/users/list` |
| Buscar usuarios | `search_users` | `GET /api/v1/system/users/search` |
| Info de usuario | `get_user_info` | `GET /api/v1/system/users/{id}` |

### Notas

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Notas recibidas | `get_notes` | `GET /api/v1/notes/received` |
| Notas enviadas | `get_sent_notes` | `GET /api/v1/notes/sent` |
| Notas archivadas | `get_archived_notes` | `GET /api/v1/notes/archived` |
| Detalle de nota | `get_note_detail` | `GET /api/v1/notes/{id}` |
| Archivar nota | - | `PATCH /api/v1/notes/{id}/archive` |

### Memos

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Memos recibidos | `get_memos` | `GET /api/v1/memos/received` |
| Memos enviados | `get_sent_memos` | `GET /api/v1/memos/sent` |
| Memos archivados | `get_archived_memos` | `GET /api/v1/memos/archived` |
| Detalle de memo | `get_memo_detail` | `GET /api/v1/memos/{id}` |

### Legajos (RLM)

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Buscar legajos | `search_records` | `GET /api/v1/records/search` |
| Detalle de legajo | `get_record` | `GET /api/v1/records/{id}` |
| Familias de registros | `get_registry_families` | `GET /api/v1/records/families` |
| Crear legajo | - | `POST /api/v1/records` |
| Actualizar legajo | - | `PATCH /api/v1/records/{id}` |
| Actualizar campo | - | `PATCH /api/v1/records/{id}/fields/{field}` |
| Verificar campo | - | `POST /api/v1/records/{id}/fields/{field}/verify` |
| Historial | - | `GET /api/v1/records/{id}/history` |
| Informe IFRLM | - | `POST /api/v1/records/{id}/report` |
| Relaciones: listar | - | `GET /api/v1/records/{id}/relations` |
| Relaciones: crear | - | `POST /api/v1/records/{id}/relations` |
| Relaciones: eliminar | - | `DELETE /api/v1/records/{id}/relations/{rid}` |
| Expedientes vinculados | - | `GET /api/v1/records/{id}/cases` |
| Vincular expediente | - | `POST /api/v1/records/{id}/cases` |
| Desvincular expediente | - | `DELETE /api/v1/records/{id}/cases/{link_id}` |
| Documentos vinculados | - | `GET /api/v1/records/{id}/documents` |
| Vincular documento | - | `POST /api/v1/records/{id}/documents` |
| Desvincular documento | - | `DELETE /api/v1/records/{id}/documents/{link_id}` |

### Busqueda Semantica

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Busqueda semantica IA | `semantic_search` | `GET /api/v1/search/semantic` |

### Backup / Sync

| Operacion | MCP Tool | REST Endpoint |
|-----------|----------|---------------|
| Catalogo de tablas | - | `GET /api/v1/sync/schema` |
| Datos incrementales | - | `GET /api/v1/sync/data` |
| PDFs firmados | - | `GET /api/v1/sync/documents` |

!!! note "Autenticacion especial para Backup/Sync"
    Los endpoints `/api/v1/sync/*` usan **Backup API Keys** (`key_type='backup'`) en lugar de las API Keys normales. No requieren `X-User-ID` pero validan IP de origen y aplican rate limiting estricto.

---

## Tu primera llamada en 5 minutos

!!! tip "Prerequisito"
    Necesitas una **API Key** y un **User ID** que te proporcionara el administrador de tu municipio. Si no los tienes, contacta al area de sistemas de tu organizacion.

### 1. Obtener credenciales

Solicita al administrador de GDI de tu municipio:

- **API Key**: cadena con formato `sk-gdi-xxx` (se genera desde el BackOffice)
- **User ID**: UUID del usuario con el que operaras (ej: `550e8400-e29b-41d4-a716-446655440000`)

### 2. Hacer tu primera consulta

Buscar expedientes activos:

```bash
curl -H "X-API-Key: tu-api-key" \
     -H "X-User-ID: tu-user-id" \
     "https://gateway.your-domain.com/api/v1/cases/search?page=1&status=active"
```

### 3. Verificar la respuesta

Si todo esta correcto, recibiras un JSON con los expedientes accesibles para ese usuario:

```json
{
  "cases": [
    {
      "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "case_number": "EE-2026-00042-SMG-ADGEN",
      "reference": "Habilitacion comercial - Farmacia San Martin",
      "status": "active",
      "admin_sector": "ADGEN",
      "current_sector": "Direccion de Habilitaciones",
      "created_at": "2026-02-10T14:30:00",
      "last_modified_at": "2026-03-01T09:15:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

!!! warning "Permisos"
    El usuario asociado a la API Key solo vera los expedientes y documentos a los que tiene acceso segun su sector y rol dentro de GDI. Los mismos permisos que aplican en la interfaz web aplican en la API.

---

## Secciones de esta guia

<div class="grid cards" markdown>

-   :material-key:{ .lg .middle } **Autenticacion**

    ---

    Como autenticarse por REST (API Key) y por MCP (OAuth 2.0). Tablas de BD, errores comunes y flujo completo.

    [:octicons-arrow-right-24: Autenticacion](autenticacion.md)

-   :material-robot:{ .lg .middle } **MCP Server**

    ---

    Referencia completa de los 42 tools MCP, parametros, respuestas y flujos recomendados para agentes IA.

    [:octicons-arrow-right-24: MCP Server](mcp-server.md)

-   :material-code-json:{ .lg .middle } **REST API**

    ---

    Referencia completa de los 45 endpoints REST organizados por dominio, con ejemplos curl y respuestas.

    [:octicons-arrow-right-24: REST API](rest-api/index.md)

-   :material-swap-horizontal:{ .lg .middle } **Flujos Completos**

    ---

    Ejemplos paso a paso de operaciones comunes: buscar expediente, crear documento, firmar, consultar historial.

    [:octicons-arrow-right-24: Flujos completos](flujos.md)

-   :material-alert-circle:{ .lg .middle } **Errores**

    ---

    Catalogo completo de errores HTTP, codigos, mensajes y como resolverlos.

    [:octicons-arrow-right-24: Errores](errores.md)

</div>
