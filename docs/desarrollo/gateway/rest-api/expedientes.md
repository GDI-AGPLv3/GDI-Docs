# Expedientes

**19 endpoints** para gestion de expedientes.

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID` salvo que se indique lo contrario.

---

## Lectura

### Buscar expedientes

```
GET /api/v1/cases/search
```

Busca expedientes con filtros opcionales. Soporta paginacion.

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Resultados por pagina (max `100`) |
| `search` | string | - | Busca por `case_number` o `reference` |
| `status` | string | - | Filtrar por estado: `active`, `inactive`, `archived` |
| `date_filter` | string | - | Filtrar por fecha: `hoy`, `ayer`, `ultimos_7_dias`, `ultimos_30_dias` |
| `sector_filter` | string | - | Filtrar por acronimo del sector |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/search?search=habilitacion&status=active&page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "cases": [
    {
      "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "case_number": "EE-2025-00001-SMG-ADGEN",
      "reference": "Habilitacion comercial",
      "status": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

### Detalle de expediente

```
GET /api/v1/cases/{case_id}
```

Devuelve la informacion completa de un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `include_documents` | bool | `false` | Incluir documentos vinculados en la respuesta |

!!! info "X-User-ID opcional"
    Si se omite `X-User-ID`, se salta la validacion de permisos y se devuelve el expediente sin restricciones de visibilidad.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890?include_documents=true" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_number": "EE-2025-00001-SMG-ADGEN",
  "reference": "Habilitacion comercial",
  "status": "active",
  "created_at": "2025-06-15T10:30:00Z",
  "current_sector": {
    "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Administracion General",
    "acronym": "ADGEN"
  },
  "documents": [
    {
      "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "document_number": "IF-2025-00012-SMG-ADGEN",
      "reference": "Informe tecnico",
      "status": "signed"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para ver el expediente |

---

### Buscar por numero exacto

```
GET /api/v1/cases/number/{case_number}
```

Busca un expediente por su numero exacto.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_number` | string | Numero del expediente (ej: `EE-2025-00001-SMG-ADGEN`) |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/number/EE-2025-00001-SMG-ADGEN" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_number": "EE-2025-00001-SMG-ADGEN",
  "reference": "Habilitacion comercial",
  "status": "active",
  "created_at": "2025-06-15T10:30:00Z",
  "current_sector": {
    "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Administracion General",
    "acronym": "ADGEN"
  }
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | No se encontro expediente con ese numero |

---

### Historial de movimientos

```
GET /api/v1/cases/{case_id}/history
```

Devuelve el historial completo de movimientos (transferencias, asignaciones, etc.) de un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/history" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "movements": [
    {
      "movement_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "movement_type": "transfer",
      "from_sector": "Administracion General",
      "to_sector": "Obras Publicas",
      "reason": "Requiere evaluacion tecnica",
      "created_by": "Juan Perez",
      "created_at": "2025-06-20T14:15:00Z"
    },
    {
      "movement_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "movement_type": "creation",
      "from_sector": null,
      "to_sector": "Administracion General",
      "reason": "Creacion del expediente",
      "created_by": "Maria Garcia",
      "created_at": "2025-06-15T10:30:00Z"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |

---

### Documentos del expediente

```
GET /api/v1/cases/{case_id}/documents
```

Devuelve todos los documentos vinculados a un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

!!! info "X-User-ID opcional"
    Si se omite `X-User-ID`, se devuelven todos los documentos sin filtrar por permisos de visibilidad.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "documents": [
    {
      "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "document_number": "IF-2025-00012-SMG-ADGEN",
      "document_type": "INF",
      "reference": "Informe tecnico sobre habilitacion",
      "status": "signed",
      "created_at": "2025-06-16T09:00:00Z"
    },
    {
      "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
      "document_number": null,
      "document_type": "DICT",
      "reference": "Dictamen legal",
      "status": "draft",
      "created_at": "2025-06-18T11:30:00Z"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |

---

### Permisos del usuario

```
GET /api/v1/cases/{case_id}/permissions
```

Devuelve los permisos que el usuario actual tiene sobre el expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/permissions" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "can_view": true,
  "can_transfer": true,
  "can_assign": false,
  "can_add_documents": true,
  "can_close": false
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |

---

### Preparar asignacion

```
GET /api/v1/cases/{case_id}/prepare-assignment
```

Devuelve la lista de sectores y usuarios disponibles para asignar el expediente. Usar antes de llamar al endpoint de asignacion.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/prepare-assignment" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "available_sectors": [
    {
      "sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "Administracion General",
      "acronym": "ADGEN",
      "users": [
        {
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "full_name": "Juan Perez",
          "email": "juan.perez@municipio.gob.ar"
        }
      ]
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para asignar este expediente |

---

### Preparar transferencia

```
GET /api/v1/cases/{case_id}/prepare-transfer
```

Devuelve los sectores disponibles para transferir el expediente. Usar antes de llamar al endpoint de transferencia.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/prepare-transfer" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "available_sectors": [
    {
      "sector_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "name": "Obras Publicas",
      "acronym": "OBPUB"
    },
    {
      "sector_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "name": "Hacienda",
      "acronym": "HAC"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para transferir este expediente |

---

### Usuarios de un sector

```
GET /api/v1/cases/sectors/{sector_id}/users
```

Devuelve la lista de usuarios que pertenecen a un sector determinado.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `sector_id` | UUID | Identificador del sector |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/sectors/b2c3d4e5-f6a7-8901-bcde-f12345678901/users" \
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
      "role": "director"
    },
    {
      "user_id": "660f9511-f3ac-52e5-b827-557766551111",
      "full_name": "Ana Lopez",
      "email": "ana.lopez@municipio.gob.ar",
      "role": "empleado"
    }
  ]
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Sector no encontrado |

---

## Operaciones

### Crear expediente

```
POST /api/v1/cases/
```

Crea un nuevo expediente a partir de una plantilla.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `case_template_id` | UUID | Si | ID de la plantilla de expediente |
| `reference` | string | Si | Descripcion o referencia del expediente |
| `owner_sector_id` | UUID | No | Sector propietario (por defecto, el sector del usuario) |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "case_template_id": "f1e2d3c4-b5a6-7890-fedc-ba0987654321",
    "reference": "Habilitacion comercial - Panaderia San Martin"
  }'
```

**Respuesta `201 Created`:**

```json
{
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_number": "EE-2025-00042-SMG-ADGEN",
  "reference": "Habilitacion comercial - Panaderia San Martin",
  "status": "active",
  "created_at": "2025-07-01T09:00:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Datos invalidos o campos requeridos faltantes |
| `404` | Plantilla no encontrada |

!!! tip "Obtener plantillas"
    Para listar las plantillas disponibles, usar `GET /api/v1/system/case-templates` antes de crear un expediente.

---

### Transferir expediente

```
POST /api/v1/cases/{case_id}/transfer
```

Transfiere un expediente a otro sector.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `target_sector_id` | UUID | Si | Sector destino |
| `reason` | string | Si | Motivo de la transferencia |
| `assigned_user_id` | UUID | No | Usuario especifico en el sector destino |
| `create_official_doc` | bool | No | Crear documento oficial de transferencia (default `false`) |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/transfer" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "target_sector_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "reason": "Requiere evaluacion tecnica del area de Obras Publicas"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Case transferred successfully",
  "movement_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "from_sector": "Administracion General",
  "to_sector": "Obras Publicas"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `403` | Sin permisos para transferir |
| `404` | Expediente o sector destino no encontrado |
| `400` | Sector destino invalido o expediente no transferible |

!!! tip "Preparar antes de transferir"
    Usar `GET /api/v1/cases/{case_id}/prepare-transfer` para obtener la lista de sectores disponibles antes de ejecutar la transferencia.

---

### Asignar expediente

```
POST /api/v1/cases/{case_id}/assign
```

Asigna un expediente a un usuario en un sector especifico.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `target_sector_id` | UUID | Si | Sector destino |
| `reason` | string | Si | Motivo de la asignacion (5-500 caracteres) |
| `assigned_user_id` | UUID | No | Usuario especifico al que se asigna |
| `create_official_doc` | bool | No | Crear documento oficial de asignacion |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/assign" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "target_sector_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "reason": "Asignado para revision de documentacion adjunta",
    "assigned_user_id": "660f9511-f3ac-52e5-b827-557766551111"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Case assigned successfully",
  "movement_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
  "assigned_to": "Ana Lopez",
  "sector": "Administracion General"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Motivo demasiado corto (minimo 5 caracteres) o demasiado largo (maximo 500) |
| `403` | Sin permisos para asignar |
| `404` | Expediente, sector o usuario no encontrado |

---

### Cerrar asignacion

```
POST /api/v1/cases/{case_id}/close-assign
```

Cierra una asignacion activa sobre un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `movement_id` | UUID | Si | ID del movimiento de asignacion a cerrar |
| `reason` | string | Si | Motivo del cierre (5-500 caracteres) |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/close-assign" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "movement_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "reason": "Revision completada, documentacion conforme"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Assignment closed successfully",
  "movement_id": "e5f6a7b8-c9d0-1234-efab-345678901234"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Motivo invalido o movimiento no es una asignacion activa |
| `403` | Sin permisos para cerrar la asignacion |
| `404` | Expediente o movimiento no encontrado |

---

## Responsables

### Listar responsables

```
GET /api/v1/cases/{case_id}/responsibles
```

Lista los responsables activos de un expediente.

**Respuesta `200 OK`:** Lista de responsables con `user_id`, `type` (ADMIN o ADDITIONAL), `sector_id`, `added_at`.

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `403` | Sin permisos para ver este expediente |
| `404` | Expediente no encontrado |

---

### Agregar responsable

```
POST /api/v1/cases/{case_id}/responsibles
```

Agrega un responsable al expediente.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `user_id` | UUID | Si | Usuario a agregar |
| `type` | string | Si | `ADMIN` o `ADDITIONAL` |
| `sector_id` | UUID | Si | Sector del usuario |
| `reason` | string | No | Motivo (default: "Asignacion de responsable") |

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Datos invalidos |
| `403` | Sin permisos para modificar este expediente |
| `404` | Expediente no encontrado |

---

### Quitar responsable

```
DELETE /api/v1/cases/{case_id}/responsibles/{responsible_id}
```

Quita un responsable del expediente (soft delete).

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |
| `responsible_id` | UUID | ID del registro en `case_responsibles` |

**Parametros query (opcional):**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `reason` | string | Motivo de remocion |

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `403` | Sin permisos para modificar este expediente |
| `404` | Responsable o expediente no encontrado |

---

## Subsanacion

### Subsanar documento oficial

```
POST /api/v1/cases/{case_id}/subsanar
```

Subsana un documento oficial erroneo en el expediente. Desactiva el documento erroneo y vincula el documento que justifica la subsanacion. Solo usuarios ADMIN del expediente pueden ejecutarlo.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `official_document_id_erroneo` | UUID | Si | Documento a desactivar |
| `official_document_id_justifica` | UUID | Si | Documento correcto que justifica |

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | Los dos IDs son identicos, o campos faltantes |
| `403` | El usuario no tiene rol ADMIN sobre el expediente |
| `404` | Expediente o documento no encontrado |

---

## Movimientos

### Movimientos del expediente

```
GET /api/v1/cases/{case_id}/movements
```

Lista plana de movimientos de un expediente. A diferencia de `/history`, no incluye analisis IA ni resumen narrativo.

**Respuesta `200 OK`:**

```json
{
  "success": true,
  "data": {
    "movements": [...],
    "total": 5
  },
  "message": "Movimientos obtenidos exitosamente"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `401` | Usuario invalido o inactivo en el schema |
| `404` | Expediente no encontrado o sin permisos |
