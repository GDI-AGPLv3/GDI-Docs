# Endpoints de Expedientes

Endpoints para gestion de expedientes (cases). Prefijo: `/api/v1/cases`.

## Listar Expedientes

### `GET /api/v1/cases/`

Lista expedientes del usuario autenticado con filtros avanzados y paginacion.

**Query Parameters:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | 1 | Numero de pagina |
| `page_size` | int | 20 | Elementos por pagina (max 100) |
| `status` | string | null | `active`, `inactive`, `archived` |
| `search` | string | null | Buscar en referencia y numero |
| `date_filter` | string | null | `hoy`, `ayer`, `ultimos_7_dias`, `ultimos_30_dias` |
| `date_from` | string | null | Fecha inicio (YYYY-MM-DD) |
| `date_to` | string | null | Fecha fin (YYYY-MM-DD) |
| `sector_filter` | string | null | UUID del sector asignado |
| `trata_filter` | string | null | UUID del sector administrativo |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "cases": [
            {
                "id": "uuid",
                "case_number": "EE-2025-00001-SMG-ADGEN",
                "reference": "Expediente de habilitacion comercial",
                "last_modified_at": "2025-01-15T10:30:00",
                "case_type": {
                    "name": "Expediente Administrativo",
                    "acronym": "EXP-ADM"
                },
                "access_reason": "ADMINSECTOR",
                "admin_sector": {
                    "acronym": "ADGEN",
                    "department": "Administracion General"
                },
                "assigned_sectors": []
            }
        ],
        "total": 25,
        "page": 1,
        "page_size": 20,
        "total_pages": 2
    },
    "message": "Se encontraron 25 expedientes"
}
```

**Archivo:** `endpoints/cases/list_cases.py`

---

## Crear Expediente

### `POST /api/v1/cases/`

Crea un expediente nuevo con caratula CAEX automatica.

**Request:**

```json
{
    "case_template_id": "uuid-template",
    "reference": "Habilitacion comercial - Panaderia El Sol",
    "owner_sector_id": "uuid-sector"
}
```

**Proceso:**

1. Valida template y usuario
2. Genera numero de expediente (`EE-2025-00001-SMG-ADGEN`)
3. Crea expediente en BD
4. Genera documento CAEX (caratula) automaticamente
5. Firma la caratula automaticamente
6. Vincula CAEX al expediente

**Response (200):**

```json
{
    "success": true,
    "data": {
        "case": {
            "case_id": "uuid",
            "case_number": "EE-2025-00001-SMG-ADGEN"
        },
        "cover": {
            "document_id": "uuid",
            "official_number": "CAEX-2025-00001-SMG-ADGEN"
        }
    },
    "message": "Expediente creado exitosamente: EE-2025-00001-SMG-ADGEN"
}
```

**Archivo:** `endpoints/cases/create_case.py`

---

## Plantillas de Expedientes

### `GET /api/v1/cases/templates`

Obtiene plantillas de expedientes disponibles para el usuario.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "templates": [
            {
                "id": "uuid",
                "name": "Expediente Administrativo",
                "acronym": "EXP-ADM",
                "description": "Expediente de habilitacion comercial",
                "filing_department_name": "Legal y Tecnica"
            }
        ],
        "total": 5
    }
}
```

---

## Transferir Expediente

### `POST /api/v1/cases/{case_id}/transfer`

Transfiere un expediente a otro sector.

**Request:**

```json
{
    "target_sector_id": "uuid-sector-destino",
    "reason": "Transferencia por competencia",
    "transfer_ownership": true,
    "assigned_user_id": null,
    "create_official_doc": false
}
```

| Campo | Descripcion |
|-------|-------------|
| `target_sector_id` | Sector destino |
| `reason` | Motivo (5-500 caracteres) |
| `transfer_ownership` | `true`=transfiere propiedad, `false`=solo asigna tarea |
| `assigned_user_id` | Usuario especifico (opcional) |
| `create_official_doc` | Si `true`, genera PV (Pase de Vista) automatico |

**Archivo:** `endpoints/cases/transfer_case.py`

---

## Asignar Tarea

### `POST /api/v1/cases/{case_id}/assign`

Asigna tarea a otro sector sin transferir propiedad.

**Request:**

```json
{
    "target_sector_id": "uuid-sector",
    "reason": "Solicitud de informe tecnico",
    "assigned_user_id": null,
    "create_official_doc": true
}
```

---

## Cerrar Asignacion

### `POST /api/v1/cases/{case_id}/close-assign`

Cierra una asignacion activa.

**Request:**

```json
{
    "movement_id": "uuid-movimiento",
    "reason": "Tarea completada satisfactoriamente"
}
```

---

## Sectores Disponibles

### `GET /api/v1/cases/{case_id}/available-sectors`

Obtiene sectores disponibles para transferencia o asignacion. Excluye el sector propietario actual.

---

## Usuarios de un Sector

### `GET /api/v1/cases/sectors/{sector_id}/users`

Lista usuarios activos de un sector para asignacion especifica.

---

## Vincular Documento

### `POST /api/v1/cases/{case_id}/link-document`

Vincula un documento oficial firmado a un expediente.

---

## Detalle de Expediente

### `GET /api/v1/cases/{case_id}`

Obtiene detalle completo de un expediente con movimientos, documentos y permisos.

---

## Buscar por Numero

### `GET /api/v1/cases/by-number/{case_number}`

Busca un expediente por su numero exacto (ej: `EE-2025-00001-SMG-ADGEN`).

---

## Descargar Expediente como ZIP

### `GET /api/v1/cases/{case_id}/download-zip`

Descarga todos los documentos oficiales activos del expediente en un unico archivo ZIP.

**Autenticacion:** JWT Auth0 (igual que todos los endpoints del backend directo).

!!! warning "Solo disponible en el Backend directo"
    Este endpoint **no esta expuesto en el Gateway REST** (`/api/v1/` del MCP Server). Es exclusivo de `GDI-Backend` en `/api/v1/cases/{case_id}/download-zip`. Los clientes que usen el Gateway no pueden invocarlo.

**Path Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | ID del expediente |

**Proceso:**

1. Valida usuario autenticado (JWT).
2. Verifica permiso de visualizacion (`can_user_view_case`). Si falla retorna 404 para no revelar existencia del expediente.
3. Obtiene el `case_number` desde BD.
4. Consulta documentos oficiales activos con `official_number` y `pdf_url` presignada.
5. Filtra los que tienen `is_active=true`, `official_number` y `pdf_url` (URLs presignadas de R2).
6. Ordena por `order` ASC.
7. Descarga todos los PDFs en paralelo via `asyncio.gather` con cliente `httpx.AsyncClient`.
8. Verifica que el total no supere 500 MB (`BusinessLogicError` si lo supera).
9. Construye el ZIP en un `SpooledTemporaryFile` con compresion `ZIP_STORED`.
10. Retorna `StreamingResponse` en chunks de 64 KB.

**Nombres de archivos dentro del ZIP:**

```
{order:03d} - {official_number}.pdf
# Ejemplo: 001 - IF-2025-00001-SMG-ADGEN.pdf
#          002 - DICT-2025-00002-SMG-ADGEN.pdf
```

**Nombre del archivo ZIP:**

```
{case_number}.zip
# Ejemplo: EE-2025-00001-SMG-ADGEN.zip
# Las barras / se reemplazan por guiones para evitar problemas en Windows/Mac.
```

**Response (200):**

```
Content-Type: application/zip
Content-Disposition: attachment; filename="EE-2025-00001-SMG-ADGEN.zip"
[stream binario]
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| 401 | Usuario no autenticado |
| 404 | Expediente no encontrado o sin permisos de visualizacion |
| 404 | El expediente no tiene documentos oficiales activos vinculados |
| 422 | Limite de 500 MB superado (`BusinessLogicError`) |
| 502 | No se pudo descargar ningun PDF de R2 |

**Archivo:** `endpoints/cases/download_case_zip.py`

**Notas de implementacion:**

- Los PDFs que fallan en la descarga de R2 se omiten con `logger.warning` (no abortan el ZIP si al menos uno tuvo exito).
- Si TODOS los PDFs fallan → 502.
- `SpooledTemporaryFile(max_size=50MB)`: hasta 50 MB se guarda en RAM; si es mayor, vuelca a disco temporario.
- Compresion `ZIP_STORED` (sin compresion): los PDFs ya son binarios comprimidos; comprimirlos de nuevo no reduce el tamano y agrega CPU innecesaria.

---

## Responsables de Expediente

### `GET /api/v1/cases/{case_id}/responsibles`

Lista los responsables activos de un expediente.

**Descripcion:** Retorna el responsable administrador (`type=ADMIN`, unico activo a la vez) y la lista de responsables adicionales (`type=ADDITIONAL`). Requiere que el usuario pueda ver el expediente.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "admin": {
            "id": "uuid",
            "user_id": "uuid",
            "sector_id": "uuid",
            "type": "ADMIN",
            "full_name": "Juan Perez",
            "email": "juan.perez@municipio.gob.ar",
            "sector_acronym": "ADGEN",
            "department_name": "Administracion General",
            "department_acronym": "ADGEN",
            "added_at": "2025-06-15T10:30:00Z"
        },
        "additional": [
            {
                "id": "uuid",
                "user_id": "uuid",
                "sector_id": "uuid",
                "type": "ADDITIONAL",
                "full_name": "Ana Lopez",
                "email": "ana.lopez@municipio.gob.ar",
                "sector_acronym": "LEGAL",
                "department_name": "Legal y Tecnica",
                "department_acronym": "LEGAL",
                "added_at": "2025-06-16T09:00:00Z"
            }
        ]
    },
    "message": "Responsables obtenidos correctamente"
}
```

**Errores:** 404 si el expediente no existe o el usuario no puede verlo.

---

### `GET /api/v1/cases/{case_id}/available-responsibles?type=ADMIN|ADDITIONAL`

Lista usuarios disponibles para ser asignados como responsables del expediente.

**Query Parameters:**

| Parametro | Tipo | Requerido | Descripcion |
|-----------|------|-----------|-------------|
| `type` | string | SI | `ADMIN` o `ADDITIONAL` |
| `sector_id` | UUID | NO | Filtrar por sector especifico (util en transferencia/asignacion) |

**Logica por tipo:**

- `type=ADMIN`: usuarios del sector administrador actual del expediente.
- `type=ADDITIONAL`: usuarios de sectores admin o actuantes activos del expediente (sector principal o con `can_edit=true` en `user_sector_permissions`).
- `sector_id` (opcional): filtra directamente por ese sector (Transferencia/Asignacion).

---

### `POST /api/v1/cases/{case_id}/responsibles`

Agrega un responsable al expediente.

**Permisos:** Requiere `can_user_edit_case`. 403 si puede ver pero no editar.

**Request:**

```json
{
    "user_id": "uuid-usuario",
    "type": "ADMIN",
    "sector_id": "uuid-sector",
    "reason": "Asignacion de responsable"
}
```

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `user_id` | UUID | SI | Usuario a agregar como responsable |
| `type` | string | SI | `ADMIN` o `ADDITIONAL` |
| `sector_id` | UUID | SI | Sector del usuario responsable |
| `reason` | string | NO | Motivo (min 1, max 500 chars; default: "Asignacion de responsable") |

**Comportamiento por tipo:**

- `type=ADMIN`: reemplaza al responsable admin actual (desactiva el anterior con soft delete).
- `type=ADDITIONAL`: agrega sin modificar el admin existente.

---

### `DELETE /api/v1/cases/{case_id}/responsibles/{responsible_id}?reason=texto`

Quita un responsable del expediente (soft delete: `is_active = false`).

**Permisos:** Requiere `can_user_edit_case`.

**Path Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | ID del expediente |
| `responsible_id` | UUID | ID del registro en `case_responsibles` |

**Query Parameters (opcional):**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `reason` | string | Motivo de remocion (default: "Remocion de responsable") |

Crea un movimiento de tipo `responsible_remove` en el historial.

**Archivo:** `endpoints/cases/responsibles.py`

**Tabla BD:** `{schema}.case_responsibles` (migracion 042b)
