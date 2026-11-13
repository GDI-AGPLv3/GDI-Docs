# Legajos (RLM)

**20 endpoints** para gestión de legajos del módulo RLM (Registro Legajo Multipropósito).

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID`.

En todas las rutas `/records/{record_id}/...`, los ids del path (`record_id`, `relation_id`, `link_id`) tienen que ser UUID. Si no lo son, la API responde `400` (por ejemplo, `record_id inválido (se espera UUID)`) sin consultar la base.

---

## Lectura

### Buscar legajos

```
GET /api/v1/records/search
```

Busca legajos con filtros opcionales. Soporta paginación.

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página (max `100`) |
| `family_code` | string | - | Código de registro: `ARQ`, `LUM`, `ORD`, etc. |
| `search` | string | - | Busca por número de legajo o datos enriquecidos |
| `state` | string | - | Filtrar por estado del legajo |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/records/search?family_code=ARQ&search=san+martin&page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "records": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "record_number": "RLM-2026-00000001-MUNI-ARQ",
      "display_name": "Edificio San Martin 1234",
      "state": "active",
      "resume": "Legajo de habilitacion arquitectonica para edificio comercial..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### Detalle de legajo

```
GET /api/v1/records/{record_id}
```

Devuelve la información completa de un legajo, incluyendo datos enriquecidos, estado, registro al que pertenece, permisos del usuario y resumen IA.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "record_number": "RLM-2026-00000001-MUNI-ARQ",
  "display_name": "Edificio San Martin 1234",
  "state": "active",
  "registry": {
    "code": "ARQ",
    "name": "Arquitectura"
  },
  "data": {
    "direccion": "San Martin 1234",
    "propietario": "Juan Perez"
  },
  "resume": "Legajo de habilitacion arquitectonica...",
  "permissions": {
    "can_view": true,
    "can_edit": true
  },
  "created_at": "2025-06-15T10:30:00Z"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |
| `403` | Sin permisos para ver el legajo |

---

### Listar familias de registros

```
GET /api/v1/registries
```

Devuelve las familias de registros disponibles en la organización (ej: Arquitectura, Luminarias, Ordenamiento).

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/registries" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "registries": [
    {
      "code": "ARQ",
      "name": "Arquitectura"
    },
    {
      "code": "LUM",
      "name": "Luminarias"
    },
    {
      "code": "ORD",
      "name": "Ordenamiento"
    }
  ],
  "total": 3
}
```

---

### Historial de legajo

```
GET /api/v1/records/{record_id}/history
```

Devuelve el historial de cambios del legajo con paginación.

Vincular y desvincular quedan en el historial. El campo `action` vale `document_linked`, `document_unlinked`, `case_linked` o `case_unlinked`.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/history?page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |

---

### Relaciones del legajo

```
GET /api/v1/records/{record_id}/relations
```

Devuelve los legajos relacionados (padre, hijo, reemplaza, etc.) con paginación.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |

---

### Expedientes vinculados

```
GET /api/v1/records/{record_id}/cases
```

Devuelve los expedientes vinculados al legajo con paginación.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |

---

### Documentos vinculados

```
GET /api/v1/records/{record_id}/documents
```

Devuelve los documentos vinculados al legajo con paginación.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página |
| `search` | string | - | Filtra por número oficial o referencia. Busca por "contiene" y no distingue mayúsculas |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |

---

## Operaciones

### Crear legajo

```
POST /api/v1/records
```

Crea un nuevo legajo en un registro específico.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `registry_code` | string | Sí | Código del registro (`ARQ`, `LUM`, `ORD`) |
| `display_name` | string | Sí | Nombre descriptivo del legajo |
| `data` | object | No | Campos enriquecidos del legajo |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/records" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "registry_code": "ARQ",
    "display_name": "Edificio San Martin 1234",
    "data": {
      "direccion": "San Martin 1234",
      "propietario": "Juan Perez"
    }
  }'
```

**Respuesta `200 OK`:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "record_number": "RLM-2026-00000001-MUNI-ARQ",
  "display_name": "Edificio San Martin 1234",
  "state": "active"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `registry_code` o `display_name` faltantes, o datos inválidos |
| `404` | Registro no encontrado |
| `403` | Sin permisos para crear legajos |

---

### Actualizar legajo

```
PATCH /api/v1/records/{record_id}
```

Actualiza el estado o nombre de un legajo.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `state` | string | Parcial | Nuevo estado del legajo |
| `display_name` | string | Parcial | Nuevo nombre descriptivo |
| `reason` | string | No | Motivo del cambio |

!!! warning "Al menos uno requerido"
    Debe enviarse al menos `state` o `display_name`. Si no se envía ninguno, devuelve `400`.

**Ejemplo:**

```bash
curl -X PATCH "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "inactive",
    "reason": "Legajo cerrado por finalizacion de obra"
  }'
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Ningún campo proporcionado |
| `404` | Legajo no encontrado |
| `403` | Sin permisos para actualizar |

---

### Actualizar campo del legajo

```
PATCH /api/v1/records/{record_id}/fields/{field_name}
```

Actualiza un campo individual de los datos enriquecidos del legajo.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |
| `field_name` | string | Nombre del campo a actualizar |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `value` | any | No | Nuevo valor del campo |
| `expiration_date` | string | No | Fecha de vencimiento (ISO 8601) |
| `document_id` | string | No | UUID del documento de respaldo |
| `document_reference` | string | No | Referencia del documento |
| `document_resume` | string | No | Resumen del documento |
| `notes` | string | No | Notas adicionales |

**Ejemplo:**

```bash
curl -X PATCH "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/fields/habilitacion_comercial" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "value": true,
    "expiration_date": "2026-12-31",
    "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "notes": "Habilitacion otorgada por resolucion 123/2025"
  }'
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo o campo no encontrado |
| `403` | Sin permisos para editar el campo |

---

### Verificar campo del legajo

```
POST /api/v1/records/{record_id}/fields/{field_name}/verify
```

Marca un campo como verificado, vinculándolo a un documento oficial de respaldo.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |
| `field_name` | string | Nombre del campo a verificar |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_id` | string | Sí | UUID del documento oficial de respaldo |
| `notes` | string | No | Notas de verificación |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/fields/habilitacion_comercial/verify" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "notes": "Verificado contra resolucion original"
  }'
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `document_id` faltante |
| `404` | Legajo, campo o documento no encontrado |
| `403` | Sin permisos para verificar |

---

### Generar informe IFRLM

```
POST /api/v1/records/{record_id}/report
```

Genera un informe IFRLM (snapshot del estado actual del legajo). Crea un documento tipo IFRLM, lo vincula al legajo y registra la acción en el historial.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/report" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo no encontrado |
| `403` | Sin permisos para generar informe |

---

### Crear relación entre legajos

```
POST /api/v1/records/{record_id}/relations
```

Crea una relación entre dos legajos.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo origen |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `target_record_id` | string | Sí | UUID del legajo destino |
| `relation_type` | string | Sí | Tipo: `parent`, `child`, `related`, `replaces`, `sibling`, `cousin` |
| `notes` | string | No | Notas sobre la relación |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/relations" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "target_record_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "relation_type": "parent",
    "notes": "Legajo original antes de subdivision"
  }'
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `target_record_id` o `relation_type` faltantes |
| `404` | Legajo origen o destino no encontrado |
| `403` | Sin permisos |

---

### Eliminar relación entre legajos

```
DELETE /api/v1/records/{record_id}/relations/{relation_id}
```

Elimina una relación existente entre dos legajos.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |
| `relation_id` | UUID | Identificador de la relación |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo o relación no encontrada |
| `403` | Sin permisos |

---

### Vincular expediente al legajo

```
POST /api/v1/records/{record_id}/cases
```

Vincula un expediente existente al legajo.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `case_id` | string | Sí | UUID del expediente a vincular |
| `notes` | string | No | Notas sobre la vinculación |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `case_id` faltante |
| `404` | Legajo o expediente no encontrado |
| `409` | El expediente ya está vinculado al legajo |

---

### Desvincular expediente del legajo

```
DELETE /api/v1/records/{record_id}/cases/{link_id}
```

Elimina la vinculación entre un legajo y un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |
| `link_id` | UUID | Identificador del vínculo |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo o vínculo no encontrado |
| `403` | Sin permisos |

---

### Vincular documento al legajo

```
POST /api/v1/records/{record_id}/documents
```

Vincula un documento existente al legajo, opcionalmente asociándolo a un campo específico.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_id` | string | Sí | UUID del documento a vincular |
| `field_name` | string | No | Campo del legajo al que asociar el documento |
| `notes` | string | No | Notas sobre la vinculación |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `document_id` faltante |
| `404` | Legajo o documento no encontrado |
| `409` | El documento ya está vinculado al legajo |

---

### Desvincular documento del legajo

```
DELETE /api/v1/records/{record_id}/documents/{link_id}
```

Elimina la vinculación entre un legajo y un documento.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | Identificador del legajo |
| `link_id` | UUID | Identificador del vínculo |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Legajo o vínculo no encontrado |
| `403` | Sin permisos |

---

## MCP Tools (Legajos)

El Gateway expone 3 tools MCP para legajos, accesibles vía el protocolo MCP (JSON-RPC over SSE).

### `search_records`

Busca legajos con filtros. Equivalente al endpoint REST `GET /api/v1/records/search`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `family_code` | string | null | Código de registro (`ARQ`, `LUM`, `ORD`) |
| `search` | string | null | Texto de búsqueda |
| `state` | string | null | Filtro por estado |
| `page` | int | 1 | Número de página |
| `page_size` | int | 20 | Ítems por página (max 100) |

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

### `get_record`

Obtiene el detalle completo de un legajo. Equivalente al endpoint REST `GET /api/v1/records/{record_id}`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `record_id` | string | *requerido* | UUID del legajo |

**Respuesta:** Legajo completo con `record_number`, `display_name`, `state`, `registry`, `data`, `resume` (resumen IA) y `permissions`.

### `get_registry_families`

Lista las familias de registros disponibles. Equivalente al endpoint REST `GET /api/v1/registries`.

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| *(ninguno)* | - | - | - |

**Respuesta:**

```json
{
  "registries": [
    { "code": "ARQ", "name": "Arquitectura" },
    { "code": "LUM", "name": "Luminarias" }
  ],
  "total": 2
}
```

---

## Errores Comunes

| Código | Situación | Solución |
|--------|-----------|----------|
| `400` | Campos requeridos faltantes | Verificar que `registry_code`, `display_name`, etc. estén presentes |
| `400` | Un id del path no es UUID | Verificar `record_id`, `relation_id` o `link_id` |
| `401` | API Key inválida o `X-User-ID` faltante | Verificar headers de autenticación |
| `403` | Sin permisos sobre el legajo | El usuario no tiene acceso al sector del legajo |
| `404` | Legajo, registro o recurso no encontrado | Verificar UUID |
| `409` | Vínculo duplicado | El expediente o documento ya está vinculado |
| `500` | Error interno | Revisar logs del Gateway |
