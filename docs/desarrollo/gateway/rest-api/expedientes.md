# Expedientes

**19 endpoints** para gestión de expedientes.

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID` salvo que se indique lo contrario.

---

## Lectura

### Buscar expedientes

```
GET /api/v1/cases/search
```

Busca expedientes con filtros opcionales. Soporta paginación.

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página (max `100`) |
| `search` | string | - | Busca por `case_number` o `reference`. `%` y `_` cuentan como letras, no como comodines |
| `status` | string | - | Filtrar por estado: `active`, `inactive`, `archived` |
| `date_filter` | string | - | Filtrar por fecha: `hoy`, `ayer`, `ultimos_7_dias`, `ultimos_30_dias` |
| `sector_filter` | string | - | Filtrar por UN sector: acrónimo exacto (ej. `HAC`), `DEPT#SECTOR` (ej. `HAC#PRIV`) o UUID. Si no resuelve a un sector activo, o trae comas, responde **400** (desde el 06/10/2026, ver [Cambios de la API](../changelog.md)) |

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

Devuelve la información completa de un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `include_documents` | bool | `false` | Incluir documentos vinculados en la respuesta |

!!! warning "X-User-ID es obligatorio"
    Este endpoint exige `X-User-ID`. Si se omite, la API responde **401** y no
    devuelve datos: no existe ningún modo de consulta que saltee la validación
    de permisos.

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

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para ver el expediente |

---

### Buscar por número exacto

```
GET /api/v1/cases/number/{case_number}
```

Busca un expediente por su número exacto.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_number` | string | Número del expediente (ej: `EE-2025-00001-SMG-ADGEN`) |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/number/EE-2025-00001-SMG-ADGEN" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:** el expediente viene envuelto en `case`, junto con
`found` y `total`.

```json
{
  "case": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "case_number": "EE-2025-00001-SMG-ADGEN",
    "reference": "Habilitacion comercial",
    "last_modified_at": "2025-06-15T10:30:00Z",
    "case_type": { "name": "Habilitacion Comercial", "acronym": "HABI" },
    "access_reason": "PUBLIC_SEARCH",
    "admin_sector": {
      "acronym": "ADGEN#PRIV",
      "department": "Administracion General",
      "sector_color": "#6C3483"
    },
    "assigned_sectors": [],
    "is_reserved": false,
    "status": "active",
    "is_creating": false
  },
  "found": true,
  "total": 1
}
```

| Campo | Que significa |
|-------|---------------|
| `access_reason` | **Por que** este usuario puede ver el expediente: `ADMINSECTOR` (es de su sector), `ASSIGNEDSECTOR` (se lo asignaron), `PUBLIC_SEARCH` (lo alcanzó por el permiso de búsqueda global, ver abajo), `RESERVED_NUMBER_MATCH` (reservado: solo se confirma que existe) |
| `is_reserved` | El expediente es de un tipo **reservado**: no se expone su contenido aunque se conozca el número |
| `is_creating` | Todavía espera su carátula (ver [Crear expediente](#crear-expediente)) |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | No existe **o** el usuario no tiene permiso para verlo (misma respuesta a propósito: no revela si existe) |

---

### Visibilidad y búsqueda global

Un usuario **no ve todos los expedientes del municipio**. El listado
(`GET /cases/search`) devuelve solo los de sus sectores: los que administra y los
que le asignaron.

La **búsqueda por número exacto** es la única excepción, y está gobernada por dos
permisos de la ficha del usuario, que se administran **por usuario desde el
BackOffice** y vienen **desactivados** por defecto:

| Permiso | Habilita |
|---------|----------|
| `can_global_search_cases` | Recuperar por número exacto un **expediente** de cualquier sector |
| `can_global_search_documents` | Lo mismo para **documentos** |

Con el permiso activo, `GET /cases/number/{n}` devuelve el expediente con
`access_reason: "PUBLIC_SEARCH"` aunque no pertenezca a los sectores del usuario.
Sin el permiso, responde `404`.

!!! warning "Es un permiso de BUSQUEDA, no de listado"
    Aunque el usuario lo tenga activo, el listado sigue mostrando **solo sus
    sectores**: el permiso amplia el alcance únicamente cuando se busca un
    número exacto. Por eso es normal que un expediente que `GET /cases/number/`
    devuelve no aparezca en `GET /cases/search`.

!!! danger "Si exponés la consulta por número al público, filtra vos"
    El caso de uso típico de un portal municipal —*"consulta tu expediente
    ingresando el número"*— se vuelve riesgoso si la API Key está asociada a un
    usuario con `can_global_search_cases` activo: **cualquier vecino que pruebe
    números correlativos vería expedientes ajenos**, incluidos sus PDFs.

    Para ese caso, una de dos:

    - usar una API Key asociada a un usuario **sin** el permiso global, **o**
    - filtrar en el portal por `access_reason` y mostrar solo lo que corresponda.

    Los expedientes **reservados** nunca se exponen por esta vía: con el número
    exacto solo se confirma que existen (`access_reason:
    "RESERVED_NUMBER_MATCH"`, sin `reference` ni sectores), para poder
    proponerles un documento.

---

### Historial de movimientos

```
GET /api/v1/cases/{case_id}/history
```

Devuelve el historial completo de movimientos (transferencias, asignaciones, etc.) de un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
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

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |

---

### Documentos del expediente

```
GET /api/v1/cases/{case_id}/documents
```

Devuelve todos los documentos vinculados a un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

!!! warning "X-User-ID es obligatorio"
    Este endpoint exige `X-User-ID`. Si se omite, la API responde **401** y no
    devuelve datos: los documentos siempre se filtran por los permisos de
    visibilidad del usuario.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "official": [
    {
      "id": "e1f2a3b4-c5d6-7890-abcd-ef1234567890",
      "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "order": 2,
      "official_number": "IF-2026-00000012-MUNDEV-ADGEN",
      "reference": "Informe tecnico sobre habilitacion",
      "linked_date": "2026-11-02T09:00:00",
      "is_active": true,
      "pdf_source": "official",
      "short_resume": "Informe favorable a la habilitacion comercial.",
      "linked_by": "Juan Perez",
      "linked_sector": "SECGEN#ADGEN",
      "is_reserved": false,
      "is_public": false,
      "embedded_files_count": 0,
      "certified_origin": false
    }
  ],
  "proposed": [
    {
      "id": "b8c9d0e1-f2a3-4567-abcd-678901234567",
      "document_draft_id": "f6a7b8c9-d0e1-2345-abcd-456789012345",
      "reference": "Dictamen legal",
      "status": "draft",
      "document_number": null,
      "document_type_name": "Dictamen",
      "document_type_acronym": "DICT",
      "is_reserved": false,
      "is_public": false,
      "can_link": false,
      "proposed_date": "2026-11-03T11:30:00",
      "proposed_by": "Maria Garcia",
      "short_resume": null
    }
  ],
  "total_official": 1,
  "total_proposed": 1
}
```

| Campo (en `official`) | Descripción |
|-------|-------------|
| `pdf_source` | De que endpoint pedir el PDF. La lista no trae URLs: se piden al abrir el documento |
| `embedded_files_count` | Cantidad de archivos adjuntos dentro del PDF oficial |
| `certified_origin` | `true` si es un PDF importado certificado de origen: GDI no lo modificó y el número oficial no está impreso en el PDF |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |

---

### Permisos del usuario

```
GET /api/v1/cases/{case_id}/permissions
```

Devuelve los permisos que el usuario actual tiene sobre el expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
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
  "can_assign": true,
  "can_archive": true,
  "can_link_documents": true,
  "can_create_movements": true,
  "can_subsanar": true,
  "ownership_level": "owner",
  "is_creating": false
}
```

| Campo | Que habilita |
|-------|--------------|
| `can_view` | Ver el expediente. **Es el único que sigue en `true` mientras el expediente se está creando** |
| `can_transfer` | `POST /cases/{id}/transfer` |
| `can_assign` | Asignar el expediente a un sector o usuario |
| `can_archive` | Archivar el expediente |
| `can_link_documents` | `POST /cases/{id}/documents/link` y `.../propose` |
| `can_create_movements` | Generar movimientos (pases) |
| `can_subsanar` | Subsanar un documento del expediente |
| `ownership_level` | `owner`, `participant` o `creator`: de donde sale el acceso |
| `is_creating` | `true` mientras el expediente espera su carátula (ver más abajo) |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |

!!! warning "Los seis permisos de escritura se apagan mientras el expediente se crea"
    Si `is_creating` es `true`, los seis `can_*` de escritura vienen en `false`
    y **`can_view` sigue en `true`**: el expediente se puede mostrar, lo que no
    se puede todavía es operarlo.

    Eso **no es falta de permisos del usuario** — es transitorio y dura lo que
    tarde la carátula (GDI-436/GDI-470). Para saber cuándo terminó, reconsultar
    este mismo endpoint hasta que `is_creating` sea `false`: la señal está en la
    misma respuesta, no hace falta pollear otra cosa.

---

### Preparar asignación

```
GET /api/v1/cases/{case_id}/prepare-assignment
```

Devuelve la lista de sectores y usuarios disponibles para asignar el expediente. Usar antes de llamar al endpoint de asignación.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
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

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para asignar este expediente |

---

### Preparar transferencia

```
GET /api/v1/cases/{case_id}/prepare-transfer
```

Devuelve los sectores disponibles para transferir el expediente. Usar antes de llamar al endpoint de transferencia.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
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

| Código | Descripción |
|--------|-------------|
| `404` | Expediente no encontrado |
| `403` | Sin permisos para transferir este expediente |

---

### Usuarios de un sector

```
GET /api/v1/cases/sectors/{sector_id}/users
```

Devuelve la lista de usuarios que pertenecen a un sector determinado.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
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

| Código | Descripción |
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

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `case_template_id` | UUID | Sí | ID de la plantilla de expediente |
| `reference` | string | Sí | Descripción o referencia del expediente |
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
  "success": true,
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_number": "EE-2025-00042-SMG-ADGEN",
  "status": "creating",
  "cover": {
    "status": "queued",
    "session_id": "9d3b50dc-8959-41df-bb71-bc0b8bd457e4",
    "poll_url": "/signing/async-poll/9d3b50dc-8959-41df-bb71-bc0b8bd457e4"
  },
  "message": "Expediente creado exitosamente"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Datos inválidos o campos requeridos faltantes |
| `400` | La plantilla no existe: `Plantilla de expediente no encontrada. Verificá que el ID sea correcto.` |

!!! warning "El expediente nace `creating`: su número ya es definitivo, su carátula todavía no"
    El `case_number` se reserva dentro del request y **no cambia nunca**. El
    PDF de la carátula (CAEX) lo genera un worker unos segundos después
    (GDI-436), y recién cuando sale, el expediente pasa a `active`.

    Mientras `status` sea `"creating"`, sobre ESE expediente:

    - `POST /cases/{id}/documents/link` y `POST /cases/{id}/documents/propose`
      responden **`409`** ("El expediente todavía se está creando...").
    - `GET /cases/{id}/permissions` devuelve los seis `can_*` de **escritura**
      en `false` con `is_creating: true`, pero **`can_view` sigue en `true`**:
      el expediente se puede mostrar, lo que no se puede es operarlo. No es
      falta de permisos del usuario -- es transitorio (GDI-470).

    **Cómo saber cuándo terminó** (cualquiera de las dos, la primera es la más
    simple):

    1. Reconsultar `GET /cases/{id}` o `GET /cases/{id}/permissions` hasta que
       `is_creating` sea `false`. No hace falta pollear nada aparte.
    2. Pollear el `poll_url` del `cover` hasta `signed` -- mismos estados que
       la firma asincrónica
       (`queued | processing | signed | failed | expired`).

    !!! danger "`poll_url` viene sin el prefijo del Gateway"
        El valor que devuelve es `/signing/async-poll/{session_id}`, **sin
        `/api/v1`**. Concatenado tal cual al host del Gateway da `404`: hay que
        pedirlo como `{host}/api/v1/signing/async-poll/{session_id}`.

    Con el kill-switch
    `CASE_COVER_ASYNC_ENABLED=false`, `status` llega en `"active"` y
    `session_id`/`poll_url` en `null`: no hay nada que esperar.

    Si la carátula falla, el expediente **no se pierde ni cambia de número**:
    queda esperándola y la cola reintenta.

!!! tip "Obtener plantillas"
    Para listar las plantillas disponibles, usar `GET /api/v1/system/case-templates` antes de crear un expediente.

---

### Transferir expediente

```
POST /api/v1/cases/{case_id}/transfer
```

Transfiere un expediente a otro sector.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `target_sector_id` | UUID | Sí | Sector destino |
| `reason` | string | Sí | Motivo de la transferencia |
| `assigned_user_id` | UUID | No | Usuario específico en el sector destino. Tiene que estar activo y ser del sector destino, o tener permiso adicional de edición sobre ese sector |
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

| Código | Descripción |
|--------|-------------|
| `403` | Sin permisos para transferir |
| `404` | Expediente o sector destino no encontrado |
| `400` | Sector destino inválido o expediente no transferible |
| `409` | El expediente todavía se está **creando** (falta su carátula): transitorio, reintentar en unos segundos (GDI-436) |
| `422` | El expediente no está activo por otro motivo (p. ej. **archivado**): esto NO se resuelve esperando |

!!! tip "Preparar antes de transferir"
    Usar `GET /api/v1/cases/{case_id}/prepare-transfer` para obtener la lista de sectores disponibles antes de ejecutar la transferencia.

---

### Asignar expediente

```
POST /api/v1/cases/{case_id}/assign
```

Asigna un expediente a un usuario en un sector específico.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `target_sector_id` | UUID | Sí | Sector destino |
| `reason` | string | Sí | Motivo de la asignación (5-500 caracteres) |
| `assigned_user_id` | UUID | No | Usuario específico al que se asigna |
| `create_official_doc` | bool | No | Crear documento oficial de asignación |

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

| Código | Descripción |
|--------|-------------|
| `400` | Motivo demasiado corto (mínimo 5 caracteres) o demasiado largo (máximo 500) |
| `403` | Sin permisos para asignar |
| `404` | Expediente, sector o usuario no encontrado |

---

### Cerrar asignación

```
POST /api/v1/cases/{case_id}/close-assign
```

Cierra una asignación activa sobre un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `movement_id` | UUID | Sí | ID del movimiento de asignación a cerrar |
| `reason` | string | Sí | Motivo del cierre (5-500 caracteres) |

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

| Código | Descripción |
|--------|-------------|
| `400` | Motivo inválido o movimiento no es una asignación activa |
| `403` | Sin permisos para cerrar la asignación |
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

| Código | Descripción |
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

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `user_id` | UUID | Sí | Usuario a agregar |
| `type` | string | Sí | `ADMIN` o `ADDITIONAL` |
| `sector_id` | UUID | Sí | Sector del usuario |
| `reason` | string | No | Motivo (default: "Asignación de responsable") |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Datos inválidos |
| `403` | Sin permisos para modificar este expediente |
| `404` | Expediente no encontrado |

---

### Quitar responsable

```
DELETE /api/v1/cases/{case_id}/responsibles/{responsible_id}
```

Quita un responsable del expediente (soft delete).

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |
| `responsible_id` | UUID | ID del registro en `case_responsibles` |

**Parámetros query (opcional):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `reason` | string | Motivo de remoción |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `403` | Sin permisos para modificar este expediente |
| `404` | Responsable o expediente no encontrado |

---

## Subsanación

### Subsanar documento oficial

```
POST /api/v1/cases/{case_id}/subsanar
```

Subsana un documento oficial erróneo en el expediente. Desactiva el documento erróneo y vincula el documento que justifica la subsanación. Solo usuarios ADMIN del expediente pueden ejecutarlo.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `official_document_id_erroneo` | UUID | Sí | Documento a desactivar |
| `official_document_id_justifica` | UUID | Sí | Documento correcto que justifica |

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Los dos IDs son idénticos, o campos faltantes |
| `403` | El usuario no tiene rol ADMIN sobre el expediente |
| `404` | Expediente o documento no encontrado |

---

## Movimientos

### Movimientos del expediente

```
GET /api/v1/cases/{case_id}/movements
```

Lista plana de movimientos de un expediente. A diferencia de `/history`, no incluye análisis IA ni resumen narrativo.

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

| Código | Descripción |
|--------|-------------|
| `401` | Usuario inválido o inactivo en el schema |
| `404` | Expediente no encontrado o sin permisos |
