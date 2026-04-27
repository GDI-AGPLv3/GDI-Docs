# Sistema y Catalogos

**7 endpoints** de datos maestros y catalogos del sistema.

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID`.

!!! info "Datos de referencia"
    Estos endpoints devuelven datos maestros que cambian con poca frecuencia. Se recomienda cachear las respuestas localmente y refrescar periodicamente en lugar de consultar en cada operacion.

---

### Tipos de documentos

```
GET /api/v1/system/document-types
```

Devuelve la lista de tipos de documentos activos en el tenant.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/document-types" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_types": [
    {
      "acronym": "INF",
      "name": "Informe",
      "description": "Documento informativo emitido por un area",
      "is_active": true
    },
    {
      "acronym": "DICT",
      "name": "Dictamen",
      "description": "Opinion tecnica o legal vinculante",
      "is_active": true
    },
    {
      "acronym": "RESO",
      "name": "Resolucion",
      "description": "Acto administrativo de caracter resolutorio",
      "is_active": true
    },
    {
      "acronym": "NOTA",
      "name": "Nota",
      "description": "Comunicacion formal entre areas",
      "is_active": true
    }
  ]
}
```

---

### Estados de documentos

```
GET /api/v1/system/document-states
```

Devuelve el catalogo de estados posibles para documentos.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/document-states" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_states": [
    {
      "code": "draft",
      "name": "Borrador",
      "description": "Documento en edicion, aun no enviado a firma"
    },
    {
      "code": "sent_to_sign",
      "name": "Enviado a firma",
      "description": "Documento esperando firma de los firmantes asignados"
    },
    {
      "code": "signed",
      "name": "Firmado",
      "description": "Documento firmado por todos los firmantes, con numero oficial"
    },
    {
      "code": "rejected",
      "name": "Rechazado",
      "description": "Documento rechazado por un firmante"
    }
  ]
}
```

---

### Sectores

```
GET /api/v1/system/sectors
```

Devuelve la estructura de sectores y departamentos del municipio.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/sectors" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "sectors": [
    {
      "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "Administracion General",
      "acronym": "ADGEN",
      "department": "Secretaria de Gobierno",
      "is_active": true
    },
    {
      "sector_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "name": "Obras Publicas",
      "acronym": "OBPUB",
      "department": "Secretaria de Infraestructura",
      "is_active": true
    },
    {
      "sector_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "name": "Hacienda",
      "acronym": "HAC",
      "department": "Secretaria de Economia",
      "is_active": true
    }
  ]
}
```

---

### Plantillas de expedientes

```
GET /api/v1/system/case-templates
```

Devuelve las plantillas disponibles para crear expedientes.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/case-templates" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "case_templates": [
    {
      "case_template_id": "f1e2d3c4-b5a6-7890-fedc-ba0987654321",
      "name": "Expediente General",
      "description": "Expediente de tramitacion general sin tipo especifico",
      "is_active": true
    },
    {
      "case_template_id": "e2d3c4b5-a6f7-8901-edcb-a09876543210",
      "name": "Habilitacion Comercial",
      "description": "Tramite de habilitacion para actividad comercial",
      "is_active": true
    }
  ]
}
```

!!! tip "Uso al crear expedientes"
    El campo `case_template_id` es requerido al crear un expediente con `POST /api/v1/cases/`. Consultar este endpoint para obtener los IDs validos.

---

### Listar usuarios

```
GET /api/v1/system/users/list
```

Devuelve la lista completa de usuarios del tenant.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/users/list" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "users": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Juan Perez",
      "email": "juan.perez@municipio.gob.ar",
      "sector": "Administracion General",
      "role": "director",
      "is_active": true
    },
    {
      "user_id": "660f9511-f3ac-52e5-b827-557766551111",
      "full_name": "Ana Lopez",
      "email": "ana.lopez@municipio.gob.ar",
      "sector": "Obras Publicas",
      "role": "empleado",
      "is_active": true
    }
  ]
}
```

---

### Buscar usuarios

```
GET /api/v1/system/users/search
```

Busca usuarios por nombre o email. Pensado para funciones de autocompletado en interfaces.

**Parametros query:**

| Parametro | Tipo | Requerido | Default | Descripcion |
|-----------|------|-----------|---------|-------------|
| `q` | string | Si | - | Texto de busqueda (minimo 2 caracteres) |
| `limit` | int | No | `10` | Cantidad maxima de resultados |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/users/search?q=pere&limit=5" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "users": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Juan Perez",
      "email": "juan.perez@municipio.gob.ar",
      "sector": "Administracion General"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | El parametro `q` es requerido y debe tener al menos 2 caracteres |

!!! warning "Minimo 2 caracteres"
    La busqueda requiere al menos 2 caracteres en el parametro `q`. Consultas con un solo caracter devolverian demasiados resultados y seran rechazadas.

---

### Informacion de usuario

```
GET /api/v1/system/users/{user_id}
```

Devuelve la informacion detallada de un usuario especifico.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `user_id` | UUID | Identificador del usuario |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/system/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Juan Perez",
  "email": "juan.perez@municipio.gob.ar",
  "sector": {
    "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Administracion General",
    "acronym": "ADGEN"
  },
  "role": "director",
  "is_active": true,
  "created_at": "2025-01-15T08:00:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Usuario no encontrado |
