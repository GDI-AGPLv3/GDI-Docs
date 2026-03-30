# MCP Server

Server MCP (Model Context Protocol) con 17 tools para agentes IA. Compatible con Claude Code, ChatGPT y Gemini.

**Endpoint:** `POST /mcp` (JSON-RPC over SSE)

---

## Configuracion por Cliente

### Claude Code

Archivo `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "gdi-gateway": {
      "type": "url",
      "url": "https://gateway.tu-municipio.gdilatam.com/mcp"
    }
  }
}
```

### ChatGPT

Utiliza la especificacion OpenAPI disponible en `/.well-known/openapi.json` junto con el descubrimiento OAuth automatico.

### Claude Desktop

Configuracion similar a Claude Code. Agregar el servidor MCP desde la interfaz de configuracion apuntando a la misma URL:

```
https://gateway.tu-municipio.gdilatam.com/mcp
```

---

## Tools Detallados (17 total)

### Expedientes (5 tools)

#### 1. `search_cases`

Busca expedientes por texto en contenido completo.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `search` | string | - | Texto de busqueda |
| `page` | int | 1 | Numero de pagina |
| `page_size` | int | 20 | Items por pagina (max 100) |
| `status` | string | null | `active`, `inactive`, `archived` |
| `date_filter` | string | null | `today`, `week`, `month`, `year` |
| `sector_filter` | string | null | Acronimo del sector |

**Respuesta:**

```json
{
  "cases": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

#### 2. `get_case`

Obtiene el detalle completo de un expediente.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `include_documents` | bool | false | Incluir documentos vinculados |

**Respuesta:** Expediente completo con `reference`, `case_number`, `status`, `sector`, fechas de creacion y modificacion.

#### 3. `get_case_history`

Historial de movimientos del expediente con resumen generado por IA.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

**Respuesta:**

```json
{
  "history": [...],
  "ai_summary": "Resumen narrativo de los movimientos del expediente"
}
```

!!! note "Recomendacion"
    Esta es la primera tool a usar cuando se investiga un expediente. El `ai_summary` proporciona un resumen narrativo que facilita la comprension rapida del estado y recorrido del expediente.

#### 4. `get_case_documents`

Lista los documentos vinculados a un expediente, separados entre oficiales y propuestos.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

**Respuesta:**

```json
{
  "official_documents": [...],
  "proposed_documents": [...]
}
```

#### 5. `get_case_permissions`

Consulta los permisos del usuario autenticado sobre un expediente especifico.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

**Respuesta:**

```json
{
  "can_view": true,
  "can_edit": true,
  "can_transfer": false,
  "can_assign": false
}
```

---

### Documentos (4 tools)

#### 6. `search_documents`

Busca en el contenido completo de documentos.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `search` | string | - | Texto de busqueda |
| `page` | int | 1 | Numero de pagina |
| `page_size` | int | 20 | Items por pagina |
| `status` | string | null | `pending`, `sent_to_sign`, `signed`, `rejected` |
| `document_type` | string | null | Acronimo del tipo: `INF`, `DICT`, `RES`, etc. |
| `case_id` | string | null | Filtrar por expediente especifico |

**Respuesta:**

```json
{
  "documents": [...],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

#### 7. `get_document`

Obtiene el detalle de un documento con resumen generado por IA.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |

**Respuesta:** Documento completo con estado, firmantes, `linked_case` y `ai_summary`.

#### 8. `get_document_content`

Obtiene el contenido HTML completo de un documento. Solo disponible para documentos oficiales firmados.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |

**Respuesta:**

```json
{
  "content": "<html>..."
}
```

#### 9. `get_pending_signatures`

Lista los documentos que esperan la firma del usuario autenticado.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | Usa el contexto OAuth del usuario |

**Respuesta:**

```json
{
  "documents": [...]
}
```

---

### Sistema (4 tools)

#### 10. `get_document_types`

Catalogo de tipos de documentos activos en la organizacion.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:**

```json
{
  "types": [
    { "acronym": "INF", "name": "Informe" },
    { "acronym": "DICT", "name": "Dictamen" }
  ]
}
```

#### 11. `get_sectors`

Sectores y departamentos de la organizacion.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:**

```json
{
  "sectors": [...]
}
```

#### 12. `get_user_info`

Informacion del usuario autenticado. No recibe parametros, utiliza el contexto OAuth.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | Usa contexto OAuth |

**Respuesta:**

```json
{
  "user_id": "uuid",
  "full_name": "Juan Perez",
  "email": "jperez@municipio.gob.ar",
  "sector": "Administracion General",
  "roles": ["operador", "firmante"]
}
```

#### 13. `get_case_templates`

Plantillas de expedientes disponibles para crear nuevos expedientes.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:**

```json
{
  "templates": [
    { "id": "uuid", "name": "Habilitacion Comercial", "description": "..." }
  ]
}
```

---

### Legajos - RLM (3 tools)

#### 15. `search_records`

Busca legajos con filtros por familia de registro, texto y estado.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `family_code` | string | null | Codigo de registro (`ARQ`, `LUM`, `ORD`) |
| `search` | string | null | Texto de busqueda |
| `state` | string | null | Filtro por estado |
| `page` | int | 1 | Numero de pagina |
| `page_size` | int | 20 | Items por pagina (max 100) |

**Respuesta:**

```json
{
  "records": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

#### 16. `get_record`

Obtiene el detalle completo de un legajo con datos enriquecidos, permisos y resumen IA.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `record_id` | string | *requerido* | UUID del legajo |

**Respuesta:** Legajo completo con `record_number`, `display_name`, `state`, `registry`, `data`, `resume` y `permissions`.

#### 17. `get_registry_families`

Lista las familias de registros disponibles en la organizacion.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:**

```json
{
  "registries": [
    { "code": "ARQ", "name": "Arquitectura" }
  ],
  "total": 1
}
```

---

### Utilidades (1 tool)

#### 18. `get_agent_guide`

Guia completa del sistema GDI. Retorna un texto con guia de uso, flujos recomendados y tips para el agente.

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:** Texto plano con la guia completa del sistema.

!!! note "Recomendacion"
    Llamar esta tool al conectarse por primera vez para que el agente entienda el contexto del sistema GDI antes de responder consultas del usuario.

---

## Flujos Recomendados para Agentes

### "Que tengo para firmar?"

```
1. get_pending_signatures
2. Responder con la lista de documentos pendientes de firma
```

### "Contame sobre el expediente de la panaderia"

```
1. search_cases(search="panaderia")
2. get_case_history(case_id=...)
3. Responder con RESUMEN NARRATIVO (no lista de pasos)
```

### "Busca documentos de Juan Perez"

```
1. search_documents(search="Juan Perez")
2. Responder con lista resumida
```

### Al conectarse por primera vez

```
1. get_agent_guide
2. Entender el sistema antes de responder consultas
```

---

## Autenticacion

OAuth 2.0 automatico via Auth0. Los clientes MCP compatibles manejan el flujo de autenticacion de forma transparente.

Para mas detalle sobre el flujo OAuth, descubrimiento de endpoints y configuracion de Auth0, ver [Autenticacion](autenticacion.md).
