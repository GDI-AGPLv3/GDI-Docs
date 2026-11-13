# MCP Server

Server MCP (Model Context Protocol) con **42 tools** (lectura y escritura) para agentes IA. Compatible con Claude Code, ChatGPT y Gemini.

**Endpoint:** `POST /mcp` (Streamable HTTP / JSON-RPC)

---

## Configuración por Cliente

### Claude Code

Archivo `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "gdi-gateway": {
      "type": "url",
      "url": "https://gateway.your-domain.com/mcp"
    }
  }
}
```

### ChatGPT

Utiliza la especificación OpenAPI disponible en `/.well-known/openapi.json` junto con el descubrimiento OAuth automático.

### Claude Desktop

Configuración similar a Claude Code. Agregar el servidor MCP desde la interfaz de configuración apuntando a la misma URL:

```
https://gateway.your-domain.com/mcp
```

---

## Tools Detallados (42 total)

### Expedientes — Lectura (5 tools)

#### 1. `search_cases`

Busca expedientes por texto en contenido completo.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `search` | string | - | Texto de búsqueda |
| `page` | int | 1 | Número de página |
| `page_size` | int | 20 | Ítems por página (max 100) |
| `status` | string | null | `active`, `inactive`, `archived` |
| `date_filter` | string | null | `hoy`, `ayer`, `ultimos_7_dias`, `ultimos_30_dias` |
| `sector_filter` | string | null | UN sector: acrónimo exacto, `DEPT#SECTOR` o UUID. Si no resuelve, la tool devuelve error (no la lista completa). Ver [Cambios de la API](changelog.md) |

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

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `include_documents` | bool | false | Incluir documentos vinculados |

**Respuesta:** Expediente completo con `reference`, `case_number`, `status`, `sector`, fechas de creación y modificación.

#### 3. `get_case_history`

Historial de movimientos del expediente con resumen generado por IA.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

**Respuesta:**

```json
{
  "case_number": "EE-2026-00001234",
  "ai_summary": "Resumen narrativo de los movimientos del expediente",
  "short_ai_summary": "Resumen corto",
  "movements": [...]
}
```

!!! note "Recomendación"
    Esta es la primera tool a usar cuando se investiga un expediente. El `ai_summary` proporciona un resumen narrativo que facilita la comprensión rápida del estado y recorrido del expediente.

#### 4. `get_case_documents`

Lista los documentos vinculados a un expediente, separados entre oficiales y propuestos.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

**Respuesta:**

```json
{
  "official": [...],
  "proposed": [...],
  "total_official": 3,
  "total_proposed": 1
}
```

Cada documento de `official` trae `certified_origin`: `true` si es un PDF importado certificado de origen (el número oficial no está impreso en el PDF). Detalle de los campos en [REST: Documentos del expediente](rest-api/expedientes.md#documentos-del-expediente).

#### 5. `get_case_permissions`

Consulta los permisos del usuario autenticado sobre un expediente específico.

| Parámetro | Tipo | Default | Descripción |
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

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `search` | string | - | Texto de búsqueda |
| `page` | int | 1 | Número de página |
| `page_size` | int | 20 | Ítems por página |
| `status` | string | null | `"En edición"`, `"Firmar ahora"`, `"En proceso de firma"`, `"Firmado"` |
| `document_type` | string | null | Acrónimo del tipo: `INF`, `DICT`, `RES`, etc. |
| `case_id` | string | null | Filtrar por expediente específico |

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

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |

**Respuesta:** Documento completo con estado, firmantes, `linked_case` y `ai_summary`. Trae `certified_origin` en la raíz: `true` si es un PDF importado certificado de origen. Ver [REST: Detalle de documento](rest-api/documentos.md#detalle-de-documento).

#### 8. `get_document_content`

Obtiene el contenido HTML completo de un documento. Solo disponible para documentos oficiales firmados.

| Parámetro | Tipo | Default | Descripción |
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

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | Usa el contexto OAuth del usuario |

**Respuesta:**

```json
{
  "documents": [...]
}
```

---

### Sistema (6 tools)

#### 10. `get_document_types`

Catálogo de tipos de documentos activos en la organización.

| Parámetro | Tipo | Default | Descripción |
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

#### 11. `get_document_states`

Estados visuales de documentos disponibles en la organización.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

#### 12. `get_user_info`

Información del usuario autenticado. No recibe parámetros, utiliza el contexto OAuth.

| Parámetro | Tipo | Default | Descripción |
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

| Parámetro | Tipo | Default | Descripción |
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

#### 14. `search_users`

Busca usuarios activos del tenant por nombre o email.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `query` | string | *requerido* | Texto de búsqueda |

#### 15. `get_case_by_number`

Obtiene un expediente por su número oficial (ej: `EE-2026-00001234-SMG-ADGEN`).

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_number` | string | *requerido* | Número oficial del expediente |

---

### Legajos - RLM (3 tools)

#### 15. `search_records`

Busca legajos con filtros por familia de registro, texto y estado.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `family_code` | string | null | Código de registro (`ARQ`, `LUM`, `ORD`) |
| `search` | string | null | Texto de búsqueda |
| `state` | string | null | Filtro por estado |
| `page` | int | 1 | Número de página |
| `page_size` | int | 20 | Ítems por página (max 100) |

#### 16. `get_record`

Obtiene el detalle completo de un legajo con datos enriquecidos, permisos y resumen IA.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `record_id` | string | *requerido* | UUID del legajo |

**Respuesta:** Legajo completo con `record_number`, `display_name`, `state`, `registry`, `data`, `resume` y `permissions`.

#### 17. `get_registry_families`

Lista las familias de registros disponibles en la organización.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

---

### Búsqueda Semántica (1 tool)

#### 18. `semantic_search`

Búsqueda semántica vectorial sobre documentos del tenant.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `query` | string | *requerido* | Texto de búsqueda (min 3 caracteres) |
| `limit` | int | 20 | Máximo de resultados (max 50) |

---

### Multi-tenant (1 tool)

#### 19. `list_my_tenants`

Lista las municipalidades a las que tiene acceso el usuario autenticado. Usar cuando se recibe error `multi_tenant_selection_required`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

---

### Notas (4 tools)

#### 20. `get_notes`

Notas recibidas en los sectores del usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página |
| `unread_only` | bool | false | Solo no leídas |
| `search` | string | null | Buscar en contenido |

#### 21. `get_sent_notes`

Notas enviadas por el usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página |
| `search` | string | null | Buscar en contenido |

#### 22. `get_archived_notes`

Notas archivadas del usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página |
| `search` | string | null | Buscar en contenido |

#### 23. `get_note_detail`

Detalle completo de una nota.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `note_id` | string | *requerido* | UUID de la nota |

---

### Memos (4 tools)

#### 24. `get_memos`

Memos recibidos del usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página (max 100) |
| `search` | string | null | Buscar en contenido |

#### 25. `get_sent_memos`

Memos enviados por el usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página (max 100) |
| `search` | string | null | Buscar en contenido |

#### 26. `get_archived_memos`

Memos archivados del usuario.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Resultados por página (max 100) |
| `search` | string | null | Buscar en contenido |

#### 27. `get_memo_detail`

Detalle completo de un memo.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `memo_id` | string | *requerido* | UUID del memo |

---

### Documentos — Escritura (5 tools)

#### 28. `create_document`

Crea un documento nuevo en estado `draft`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_type_acronym` | string | *requerido* | Acrónimo del tipo (ej: `INF`, `DICT`) |
| `reference` | string | *requerido* | Asunto del documento |
| `recipients` | object | null | Solo para tipo NOTA: `{to, cc, bcc}` con UUIDs de sectores |

#### 29. `save_document`

Guarda cambios en un documento editable (draft o rejected).

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |
| `reference` | string | null | Nuevo asunto |
| `content` | string | null | HTML del contenido |
| `signers` | array | null | Lista de firmantes `[{user_id, is_numerator}]` |

#### 30. `start_signing`

Inicia el proceso de firma de un documento (draft → sent_to_sign). Solo el creador puede ejecutar esta acción.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |

#### 31. `reject_document`

Rechaza un documento en proceso de firma. Disponible para cualquier firmante asignado.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |
| `reason` | string | *requerido* | Motivo del rechazo |

#### 33. `search_document_by_number`

Busca un documento oficial por su número exacto (ej: `INF-2026-00001234-MUNI-LEGAL`).

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `doc_number` | string | *requerido* | Número oficial del documento |

#### 34. `get_signature_details`

Detalles de firma de un documento (firmantes, estado, fechas de firma).

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `document_id` | string | *requerido* | UUID del documento |

---

### Expedientes — Escritura (4 tools)

#### 35. `prepare_assignment`

Prepara la asignación de un expediente: obtiene sectores disponibles y usuarios del sector destino.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

#### 36. `assign_case`

Asigna o transfiere un expediente a otro sector.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `target_sector_id` | string | *requerido* | UUID del sector destino |
| `reason` | string | *requerido* | Motivo |
| `transfer_ownership` | bool | false | `true` = transferir propiedad, `false` = asignar tarea |
| `assigned_user_id` | string | null | UUID del usuario específico (opcional) |
| `create_official_doc` | bool | false | Generar PV automático |

#### 37. `propose_document`

Propone un documento oficial para vincularlo a un expediente.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `document_id` | string | *requerido* | UUID del documento oficial |

#### 38. `reject_proposal`

Rechaza la propuesta de vinculación de un documento a un expediente.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `document_id` | string | *requerido* | UUID del documento propuesto |

---

### Expedientes — Responsables (3 tools)

#### 39. `get_case_responsibles`

Lista responsables activos de un expediente.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |

#### 40. `add_case_responsible`

Agrega un responsable a un expediente.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `user_id` | string | *requerido* | UUID del usuario a agregar |
| `type` | string | *requerido* | `ADMIN` o `ADDITIONAL` |
| `sector_id` | string | *requerido* | UUID del sector del usuario |
| `reason` | string | opcional | Motivo (default: "Asignación de responsable") |

#### 41. `remove_case_responsible`

Quita un responsable de un expediente (soft delete).

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `case_id` | string | *requerido* | UUID del expediente |
| `responsible_id` | string | *requerido* | UUID del registro en case_responsibles |
| `reason` | string | opcional | Motivo de remoción |

---

### Utilidades (1 tool)

#### 42. `get_agent_guide`

Guía completa del sistema GDI. Retorna un texto con guía de uso, flujos recomendados y tips para el agente. No requiere autenticación.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

!!! note "Recomendación"
    Llamar esta tool al conectarse por primera vez para que el agente entienda el contexto del sistema GDI antes de responder consultas del usuario.

---

### Resumen de los 42 tools

| # | Tool | Categoría |
|---|------|-----------|
| 1 | `add_case_responsible` | Expedientes escritura |
| 2 | `assign_case` | Expedientes escritura |
| 3 | `create_document` | Documentos escritura |
| 4 | `get_agent_guide` | Utilidades |
| 5 | `get_archived_memos` | Memos |
| 6 | `get_archived_notes` | Notas |
| 7 | `get_case` | Expedientes lectura |
| 8 | `get_case_by_number` | Expedientes lectura |
| 9 | `get_case_documents` | Expedientes lectura |
| 10 | `get_case_history` | Expedientes lectura |
| 11 | `get_case_permissions` | Expedientes lectura |
| 12 | `get_case_responsibles` | Expedientes lectura |
| 13 | `get_case_templates` | Sistema |
| 14 | `get_document` | Documentos lectura |
| 15 | `get_document_content` | Documentos lectura |
| 16 | `get_document_states` | Sistema |
| 17 | `get_document_types` | Sistema |
| 18 | `get_memo_detail` | Memos |
| 19 | `get_memos` | Memos |
| 20 | `get_note_detail` | Notas |
| 21 | `get_notes` | Notas |
| 22 | `get_pending_signatures` | Documentos lectura |
| 23 | `get_record` | Legajos (RLM) |
| 24 | `get_registry_families` | Legajos (RLM) |
| 25 | `get_sent_memos` | Memos |
| 26 | `get_sent_notes` | Notas |
| 27 | `get_signature_details` | Documentos lectura |
| 28 | `get_user_info` | Sistema |
| 29 | `list_my_tenants` | Multi-tenant |
| 30 | `prepare_assignment` | Expedientes escritura |
| 31 | `propose_document` | Expedientes escritura |
| 32 | `reject_document` | Documentos escritura |
| 33 | `reject_proposal` | Expedientes escritura |
| 34 | `remove_case_responsible` | Expedientes escritura |
| 35 | `save_document` | Documentos escritura |
| 36 | `search_cases` | Expedientes lectura |
| 37 | `search_document_by_number` | Documentos lectura |
| 38 | `search_documents` | Documentos lectura |
| 39 | `search_records` | Legajos (RLM) |
| 40 | `search_users` | Sistema |
| 41 | `semantic_search` | Búsqueda semántica |
| 42 | `start_signing` | Documentos escritura |

---

## Flujos Recomendados para Agentes

### "Qué tengo para firmar?"

```
1. get_pending_signatures
2. Responder con la lista de documentos pendientes de firma
```

### "Contame sobre el expediente de la panadería"

```
1. search_cases(search="panaderia")
2. get_case_history(case_id=...)
3. Responder con RESUMEN NARRATIVO (no lista de pasos)
```

### "Busca documentos de Juan Pérez"

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

## Autenticación

OAuth 2.0 automático vía el proveedor de autenticación. Los clientes MCP compatibles manejan el flujo de autenticación de forma transparente.

!!! warning "Requisitos del proveedor de autenticación (si el MCP no conecta)"
    El tenant necesita 4 cosas o el cliente termina con un token opaco: **DCR habilitado**, **conexión de BD a Domain Level**, un **client-grant `default_for: third_party_clients`** sobre la API, y el **resource server con la barra final** (`https://<gateway>/`). Lo configura quien administra la instalación de GDI. Ver [Autenticación > Validación del JWT](autenticacion.md#validacion-del-jwt).

Para más detalle sobre el flujo OAuth, descubrimiento de endpoints y configuración del proveedor de autenticación, ver [Autenticación](autenticacion.md).
