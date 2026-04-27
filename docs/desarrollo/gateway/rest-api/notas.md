# Notas

**5 endpoints** para gestion de notas internas.

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID`.

Las notas son comunicaciones internas entre usuarios del sistema. Funcionan como un sistema de mensajeria interna vinculado al contexto de gestion documental.

---

## Lectura

### Notas recibidas

```
GET /api/v1/notes/received
```

Devuelve las notas recibidas por el usuario actual. Soporta paginacion.

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Resultados por pagina (max `100`) |
| `unread_only` | bool | `false` | Mostrar solo notas no leidas |
| `search` | string | - | Buscar en el contenido o asunto de las notas |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/notes/received?unread_only=true&page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "notes": [
    {
      "note_id": "a1b2c3d4-0000-1111-2222-333344445555",
      "subject": "Revision de expediente EE-2025-00001",
      "sender": {
        "user_id": "660f9511-f3ac-52e5-b827-557766551111",
        "full_name": "Ana Lopez"
      },
      "is_read": false,
      "created_at": "2025-07-01T09:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### Notas enviadas

```
GET /api/v1/notes/sent
```

Devuelve las notas enviadas por el usuario actual. Soporta paginacion.

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Resultados por pagina (max `100`) |
| `search` | string | - | Buscar en el contenido o asunto de las notas |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/notes/sent?page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "notes": [
    {
      "note_id": "b2c3d4e5-1111-2222-3333-444455556666",
      "subject": "Solicitud de dictamen legal",
      "recipients": [
        {
          "user_id": "660f9511-f3ac-52e5-b827-557766551111",
          "full_name": "Ana Lopez",
          "is_read": true
        }
      ],
      "created_at": "2025-06-30T16:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### Notas archivadas

```
GET /api/v1/notes/archived
```

Devuelve las notas que el usuario ha archivado. Soporta paginacion.

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Resultados por pagina (max `100`) |
| `search` | string | - | Buscar en el contenido o asunto de las notas |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/notes/archived?page=1&page_size=5" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "notes": [
    {
      "note_id": "c3d4e5f6-2222-3333-4444-555566667777",
      "subject": "Recordatorio: Vencimiento plazo expediente",
      "sender": {
        "user_id": "770a0622-a4bd-63f6-c938-668877662222",
        "full_name": "Carlos Martinez"
      },
      "is_read": true,
      "archived_at": "2025-06-28T10:00:00Z",
      "created_at": "2025-06-25T08:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 5,
  "total_pages": 1
}
```

---

### Detalle de nota

```
GET /api/v1/notes/{note_id}
```

Devuelve el contenido completo de una nota. Si la nota estaba sin leer, se marca como leida automaticamente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `note_id` | UUID | Identificador de la nota |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/notes/a1b2c3d4-0000-1111-2222-333344445555" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "note_id": "a1b2c3d4-0000-1111-2222-333344445555",
  "subject": "Revision de expediente EE-2025-00001",
  "body": "Solicito revision de la documentacion adjunta al expediente EE-2025-00001-SMG-ADGEN antes del viernes. Se requiere dictamen del area legal.",
  "sender": {
    "user_id": "660f9511-f3ac-52e5-b827-557766551111",
    "full_name": "Ana Lopez",
    "sector": "Obras Publicas"
  },
  "recipients": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Juan Perez",
      "is_read": true,
      "read_at": "2025-07-01T10:00:00Z"
    }
  ],
  "is_archived": false,
  "created_at": "2025-07-01T09:30:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Nota no encontrada |
| `403` | El usuario no es remitente ni destinatario de la nota |

!!! info "Marcado automatico de lectura"
    Al consultar el detalle de una nota recibida, esta se marca como leida automaticamente. No es necesario realizar una accion adicional.

---

## Operaciones

### Archivar o desarchivar nota

```
PATCH /api/v1/notes/{note_id}/archive
```

Archiva o desarchiva una nota. Las notas archivadas dejan de aparecer en la bandeja de recibidos y se muestran en la seccion de archivados.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `note_id` | UUID | Identificador de la nota |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `archived` | bool | Si | `true` para archivar, `false` para desarchivar |
| `sector_id` | UUID | Si | ID del sector desde el que se realiza la accion |

**Ejemplo (archivar):**

```bash
curl -X PATCH "https://gateway.your-domain.com/api/v1/notes/a1b2c3d4-0000-1111-2222-333344445555/archive" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "archived": true,
    "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "note_id": "a1b2c3d4-0000-1111-2222-333344445555",
  "archived": true,
  "message": "Note archived successfully"
}
```

**Ejemplo (desarchivar):**

```bash
curl -X PATCH "https://gateway.your-domain.com/api/v1/notes/a1b2c3d4-0000-1111-2222-333344445555/archive" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "archived": false,
    "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "note_id": "a1b2c3d4-0000-1111-2222-333344445555",
  "archived": false,
  "message": "Note unarchived successfully"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Campos requeridos faltantes o invalidos |
| `403` | El usuario no tiene permisos sobre esta nota desde el sector indicado |
| `404` | Nota no encontrada |
