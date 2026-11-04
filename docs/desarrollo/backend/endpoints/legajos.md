# Endpoints de Legajos (RLM)

Endpoints para el módulo RLM (Registro Legajo Multipropósito): CRUD de legajos, campos enriquecidos, historial, relaciones, vinculación con expedientes y documentos, e informes IFRLM.

**Router principal:** `endpoints/rlm/router.py` -- prefijo `/api/v1`, tag `rlm`

## Resumen de Endpoints

| Grupo | Método | Ruta | Descripción |
|-------|--------|------|-------------|
| **Familias** | GET | `/registries` | Listar familias de registros |
| | GET | `/registries/{id}` | Detalle de una familia |
| **Legajos CRUD** | POST | `/records` | Crear legajo |
| | GET | `/records` | Listar legajos (paginado) |
| | GET | `/records/autocomplete` | Autocompletado por número |
| | GET | `/records/{id}` | Detalle de un legajo |
| | PATCH | `/records/{id}` | Actualizar estado/nombre |
| **Campos** | PATCH | `/records/{id}/fields/{field}` | Actualizar campo enriquecido |
| | POST | `/records/{id}/fields/{field}/verify` | Verificar campo |
| **Historial** | GET | `/records/{id}/history` | Historial de cambios |
| **Relaciones** | GET | `/records/{id}/relations` | Listar relaciones |
| | POST | `/records/{id}/relations` | Crear relación |
| | DELETE | `/records/{id}/relations/{rel_id}` | Eliminar relación |
| **Links (expedientes)** | GET | `/records/{id}/cases` | Listar expedientes vinculados |
| | POST | `/records/{id}/cases` | Vincular expediente |
| | DELETE | `/records/{id}/cases/{link_id}` | Desvincular expediente |
| **Links (documentos)** | GET | `/records/{id}/documents` | Listar documentos vinculados |
| | POST | `/records/{id}/documents` | Vincular documento |
| | DELETE | `/records/{id}/documents/{link_id}` | Desvincular documento |
| **Informe** | POST | `/records/{id}/report` | Generar informe IFRLM |

---

## Grupo A: Familias de Registros

### `GET /registries`

Lista todas las familias de registros activas con conteo de legajos y permisos del usuario.

**Permisos:** Autenticado. Los permisos por familia se resuelven en base al sector del usuario.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "registries": [
            {
                "id": "uuid",
                "code": "ARQ",
                "name": "Arquitectura",
                "description": "Legajos de obras de arquitectura",
                "allowed_states": ["Activo", "Inactivo", "Suspendido", "Archivado"],
                "is_active": true,
                "record_count": 42,
                "permissions": {
                    "can_create": true,
                    "can_edit": true,
                    "can_view": true,
                    "can_verify": false
                }
            }
        ],
        "total": 3
    },
    "message": "Se encontraron 3 registros"
}
```

!!! note "Permisos bulk"
    Los permisos se resuelven en 2 queries (no N+1): una para obtener los sectores del usuario y otra para todos los permisos de esos sectores. Lógica OR: si cualquier sector del usuario tiene el permiso, se activa.

**Archivo:** `endpoints/rlm/registries.py`

---

### `GET /registries/{registry_id}`

Obtiene el detalle de una familia de registro incluyendo su `data_schema`.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `registry_id` | UUID | ID de la familia de registro |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "code": "ARQ",
        "name": "Arquitectura",
        "description": "Legajos de obras de arquitectura",
        "data_schema": {
            "nombre_titular": {
                "label": "Nombre del titular",
                "type": "text",
                "required": true
            },
            "habilitacion": {
                "label": "Habilitacion",
                "type": "file",
                "has_expiration": true,
                "has_verification": true,
                "has_document": true
            }
        },
        "allowed_states": ["Activo", "Inactivo", "Suspendido", "Archivado"],
        "record_count": 42,
        "permissions": {
            "can_create": true,
            "can_edit": true,
            "can_view": true,
            "can_verify": false
        }
    },
    "message": "Registro 'ARQ' encontrado"
}
```

**Archivo:** `endpoints/rlm/registries.py`

---

## Grupo B: Legajos CRUD

### `POST /records`

Crea un nuevo legajo. Genera número automático con advisory lock `777777`.

**Permisos:** `can_create` sobre la familia de registro.

**Request:**

```json
{
    "registry_code": "ARQ",
    "display_name": "Edificio San Martin 1234",
    "data": {
        "nombre_titular": "Juan Perez",
        "direccion": "San Martin 1234"
    }
}
```

!!! info "Validación de datos"
    Los campos se validan contra el `data_schema` de la familia. En creación se usa `skip_required=True` (los campos requeridos se pueden completar después). Los campos con `has_verification` se inicializan automáticamente con `verified: false`.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "record_number": "RLM-2026-00000001-SMG-ARQ",
        "display_name": "Edificio San Martin 1234",
        "state": "Activo",
        "registry_code": "ARQ",
        "registry_name": "Arquitectura",
        "created_at": "2026-03-30 10:30:00"
    },
    "message": "Legajo RLM-2026-00000001-SMG-ARQ creado exitosamente"
}
```

**Formato del número:** `RLM-{ANIO}-{SECUENCIA:08d}-{MUNICIPIO}-{CODIGO_FAMILIA}`

!!! warning "Numeración atómica"
    La generación del número usa `pg_advisory_xact_lock(777777)` dentro de la misma transacción que el INSERT, garantizando unicidad sin race conditions. Es un lock distinto al `888888` usado por documentos.

**Post-creacion:** Se encola la generación de resumen IA (`enqueue_record_resume_fire_and_forget`) de forma asincrona y no bloqueante.

**Archivo:** `endpoints/rlm/records.py`

---

### `GET /records`

Lista legajos con filtros, búsqueda y paginación. Solo muestra legajos de familias donde el usuario tiene `can_view`.

**Permisos:** `can_view` (se filtra automáticamente por familias visibles).

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `registry` | string | null | Filtrar por código de familia (ARQ, LUM, ORD) |
| `state` | string | null | Filtrar por estado |
| `search` | string | null | Buscar por número, nombre o datos (min 2 chars) |
| `page` | int | 1 | Página (>= 1) |
| `page_size` | int | 10 | Ítems por página (1-100) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "records": [
            {
                "id": "uuid",
                "record_number": "RLM-2026-00000001-SMG-ARQ",
                "display_name": "Edificio San Martin 1234",
                "state": "Activo",
                "resume": "Legajo de obra en San Martin 1234...",
                "next_expiration": "2026-06-15",
                "created_at": "2026-03-30 10:30:00",
                "updated_at": "2026-03-30 10:30:00",
                "registry": {
                    "code": "ARQ",
                    "name": "Arquitectura"
                },
                "created_by": {
                    "name": "Juan Perez",
                    "sector": "PRIV",
                    "department": "OOPU"
                }
            }
        ],
        "total": 42,
        "page": 1,
        "page_size": 10,
        "total_pages": 5
    },
    "message": "Se encontraron 42 legajos"
}
```

!!! note "Búsqueda"
    El parámetro `search` busca con ILIKE en `record_number`, `display_name` y `data::text` (casting del JSONB a texto). Los caracteres especiales (`%`, `_`, `\`) se escapan automáticamente.

**Archivo:** `endpoints/rlm/records.py`

---

### `GET /records/autocomplete`

Autocompletado de legajos por número o nombre. Respeta permisos `can_view` vía `registry_family_permissions`.

**Query parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `q` | string | Texto de búsqueda (2-50 chars, requerido) |
| `limit` | int | Máximo de resultados (1-50, default 10) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "records": [
            {
                "record_id": "uuid",
                "record_number": "RLM-2026-00000001-SMG-ARQ",
                "display_name": "Edificio San Martin 1234",
                "family_code": "ARQ",
                "state": "Activo"
            }
        ],
        "total": 1,
        "query": "RLM-2026"
    },
    "message": "Se encontraron 1 legajos"
}
```

**Archivo:** `endpoints/rlm/records.py`

---

### `GET /records/{record_id}`

Obtiene el detalle completo de un legajo incluyendo datos JSONB, info de la familia, creador y permisos del usuario.

**Permisos:** `can_view` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "record_number": "RLM-2026-00000001-SMG-ARQ",
        "display_name": "Edificio San Martin 1234",
        "state": "Activo",
        "data": {
            "nombre_titular": {
                "value": "Juan Perez",
                "verified": false,
                "verified_at": null,
                "verified_by": null
            },
            "habilitacion": {
                "value": "Habilitacion comercial",
                "expiration_date": "2026-06-15",
                "document_id": "uuid-doc",
                "verified": true,
                "verified_at": "2026-03-15T10:00:00",
                "verified_by": "uuid-verificador",
                "verified_by_name": "Maria Garcia"
            }
        },
        "resume": "Legajo de obra en San Martin 1234...",
        "next_expiration": "2026-06-15",
        "created_at": "2026-03-30 10:30:00",
        "updated_at": "2026-03-30 10:30:00",
        "registry": {
            "id": "uuid-registry",
            "code": "ARQ",
            "name": "Arquitectura",
            "data_schema": { "..." : "..." },
            "allowed_states": ["Activo", "Inactivo", "Suspendido", "Archivado"]
        },
        "created_by": {
            "user_id": "uuid",
            "name": "Juan Perez",
            "sector": "PRIV",
            "department": "OOPU"
        },
        "permissions": {
            "can_create": true,
            "can_edit": true,
            "can_view": true,
            "can_verify": false
        }
    },
    "message": "Legajo RLM-2026-00000001-SMG-ARQ encontrado"
}
```

**Archivo:** `endpoints/rlm/records.py`

---

### `PATCH /records/{record_id}`

Actualiza el estado y/o nombre de un legajo. Registra historial atómicamente en la misma transacción.

**Permisos:** `can_edit` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |

**Request:**

```json
{
    "state": "Suspendido",
    "display_name": "Edificio San Martin 1234 - SUSPENDIDO",
    "reason": "Obra sin avance en 6 meses"
}
```

!!! info "Validación"
    Debe enviarse al menos `state` o `display_name`. El estado se valida contra la lista de `states` definida en la familia del registro. El `reason` se registra en historial pero es opcional.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "state": "Suspendido",
        "display_name": "Edificio San Martin 1234 - SUSPENDIDO",
        "updated_at": "2026-03-30 11:00:00"
    },
    "message": "Legajo actualizado - Estado: 'Suspendido', Nombre: 'Edificio San Martin 1234 - SUSPENDIDO'"
}
```

**Acciones registradas en historial:**

| Campo actualizado | Acción |
|-------------------|--------|
| Solo estado | `state_changed` |
| Solo nombre | `display_name_changed` |
| Ambos | `record_updated` |

**Archivo:** `endpoints/rlm/records.py`

---

## Grupo C: Campos Enriquecidos

### `PATCH /records/{record_id}/fields/{field_name}`

Actualiza un campo enriquecido específico de un legajo. Usa `SELECT FOR UPDATE` + `jsonb_set` para atomicidad: dos usuarios pueden editar campos distintos del mismo legajo sin pisarse.

**Permisos:** `can_edit` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |
| `field_name` | string | Nombre del campo (debe existir en `data_schema`) |

**Request:**

```json
{
    "value": "Juan Carlos Perez",
    "expiration_date": "2026-12-31",
    "document_id": "uuid-documento",
    "notes": "Actualizado segun documento oficial",
    "document_reference": "IF-2026-0001234-SMG",
    "document_resume": "Informe de actualizacion de titular"
}
```

Todos los campos del body son opcionales. Solo se actualizan los campos enviados.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "field_name": "nombre_titular",
        "field_data": {
            "value": "Juan Carlos Perez",
            "expiration_date": "2026-12-31",
            "document_id": "uuid-documento",
            "notes": "Actualizado segun documento oficial",
            "document_reference": "IF-2026-0001234-SMG",
            "document_resume": "Informe de actualizacion de titular"
        },
        "next_expiration": "2026-06-15",
        "updated_at": "2026-03-30 11:30:00"
    },
    "message": "Campo 'nombre_titular' actualizado"
}
```

!!! warning "Concurrencia"
    El endpoint usa `SELECT ... FOR UPDATE OF r` para lockear la fila del record antes de leer los datos frescos. Esto evita race conditions cuando dos usuarios editan campos distintos del mismo legajo. El lock se libera al terminar la transacción.

**Archivo:** `endpoints/rlm/fields.py`

---

### `POST /records/{record_id}/fields/{field_name}/verify`

Marca un campo como verificado. El campo debe tener `has_verification: true` en el `data_schema`.

**Permisos:** `can_verify` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |
| `field_name` | string | Nombre del campo a verificar |

**Request:**

```json
{
    "document_id": "uuid-documento-oficial",
    "notes": "Verificado contra documento oficial"
}
```

El `document_id` es requerido y debe existir en `official_documents`.

**Response (200):**

```json
{
    "success": true,
    "data": {
        "field_name": "habilitacion",
        "field_data": {
            "value": "Habilitacion comercial",
            "expiration_date": "2026-12-31",
            "verified": true,
            "verified_at": "2026-03-30T11:45:00",
            "verified_by": "uuid-verificador",
            "verified_by_name": "Maria Garcia",
            "verified_document_id": "uuid-documento-oficial",
            "verified_document_number": "IF-2026-0001234-SMG",
            "verified_document_resume": "Informe de habilitacion",
            "verification_notes": "Verificado contra documento oficial"
        },
        "updated_at": "2026-03-30 11:45:00"
    },
    "message": "Campo 'habilitacion' verificado"
}
```

**Archivo:** `endpoints/rlm/fields.py`

---

## Grupo D: Historial

### `GET /records/{record_id}/history`

Obtiene el historial de cambios de un legajo, paginado y ordenado por fecha descendente.

**Permisos:** `can_view` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página (>= 1) |
| `page_size` | int | 20 | Ítems por página (1-100) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "entries": [
            {
                "id": "uuid",
                "action": "field_updated",
                "field_name": "nombre_titular",
                "before_value": {"value": "Juan Perez"},
                "after_value": {"value": "Juan Carlos Perez"},
                "user_id": "uuid",
                "user_name": "Admin User",
                "sector_name": "PRIV",
                "created_at": "2026-03-30 11:30:00"
            }
        ],
        "total": 15,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "message": "Se encontraron 15 entradas en el historial"
}
```

**Tipos de acciones registradas:**

| Acción | Descripción |
|--------|-------------|
| `created` | Legajo creado |
| `state_changed` | Cambio de estado |
| `display_name_changed` | Cambio de nombre |
| `record_updated` | Cambio de estado y nombre |
| `field_updated` | Campo enriquecido actualizado |
| `field_verified` | Campo verificado |
| `relation_created` | Relación creada |
| `relation_deleted` | Relación eliminada |
| `document_linked` | Documento vinculado |
| `document_unlinked` | Documento desvinculado |
| `case_linked` | Expediente vinculado |
| `case_unlinked` | Expediente desvinculado |
| `ifrlm_generated` | Informe IFRLM generado |

**Archivo:** `endpoints/rlm/fields.py`

---

## Grupo E: Relaciones entre Legajos

### `GET /records/{record_id}/relations`

Lista relaciones de un legajo con otros legajos. La consulta es bidireccional: muestra relaciones donde el legajo es source O target.

**Permisos:** `can_view` sobre la familia del legajo.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página (>= 1) |
| `page_size` | int | 20 | Ítems por página (1-100) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "relations": [
            {
                "relation_id": "uuid",
                "relation_type": "related",
                "notes": "Misma direccion",
                "created_at": "2026-03-30 12:00:00",
                "related_record": {
                    "id": "uuid",
                    "record_number": "RLM-2026-00000002-SMG-LUM",
                    "display_name": "Luminaria San Martin 1234",
                    "state": "Activo",
                    "registry_code": "LUM",
                    "registry_name": "Luminarias",
                    "resume": "..."
                }
            }
        ],
        "total": 2,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "message": "Se encontraron 2 relaciones"
}
```

**Archivo:** `endpoints/rlm/relations.py`

---

### `POST /records/{record_id}/relations`

Crea una relación entre dos legajos. No se permite crear una relación de un legajo consigo mismo.

**Permisos:** `can_edit` sobre la familia del legajo origen.

**Request:**

```json
{
    "target_record_id": "uuid-legajo-destino",
    "relation_type": "related",
    "notes": "Misma direccion"
}
```

**Tipos de relación válidos (enum `relation_type`):**

| Tipo | Descripción |
|------|-------------|
| `parent` | El legajo origen es padre del destino |
| `child` | El legajo origen es hijo del destino |
| `related` | Relación genérica |
| `replaces` | El legajo origen reemplaza al destino |
| `sibling` | Legajos hermanos |
| `cousin` | Legajos primos |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "source_record_id": "uuid-origen",
        "target_record_id": "uuid-destino",
        "relation_type": "related"
    },
    "message": "Relacion creada exitosamente"
}
```

**Archivo:** `endpoints/rlm/relations.py`

---

### `DELETE /records/{record_id}/relations/{relation_id}`

Elimina una relación entre legajos. El `relation_id` debe pertenecer al legajo (como source o target).

**Permisos:** `can_edit` sobre la familia del legajo.

**Response (200):**

```json
{
    "success": true,
    "data": {"removed": true},
    "message": "Relacion eliminada exitosamente"
}
```

**Archivo:** `endpoints/rlm/relations.py`

---

## Grupo F: Links con Expedientes

### `GET /records/{record_id}/cases`

Lista expedientes vinculados a un legajo con paginación.

**Permisos:** `can_view` sobre la familia del legajo.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página (>= 1) |
| `page_size` | int | 20 | Ítems por página (1-100) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "cases": [
            {
                "link_id": "uuid",
                "case_id": "uuid",
                "notes": "Expediente de habilitacion",
                "linked_at": "2026-03-30 12:30:00",
                "case_number": "HABI-2026-0000001-SMG",
                "reference": "Habilitacion comercial San Martin 1234",
                "short_ai_summary": "Expediente de habilitacion comercial..."
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "message": "Se encontraron 1 expedientes vinculados"
}
```

**Archivo:** `endpoints/rlm/cases.py`

---

### `POST /records/{record_id}/cases`

Vincula un expediente a un legajo.

**Permisos:** `can_edit` sobre la familia del legajo.

**Request:**

```json
{
    "case_id": "uuid-expediente",
    "notes": "Expediente de habilitacion"
}
```

**Response (200):**

```json
{
    "success": true,
    "data": {
        "record_id": "uuid-legajo",
        "case_id": "uuid-expediente"
    },
    "message": "Expediente vinculado exitosamente"
}
```

**Errores:**

| Código | Causa |
|--------|-------|
| 404 | Legajo o expediente no encontrado |
| 403 | Sin permiso `can_edit` |
| 409 | El expediente ya está vinculado (constraint UNIQUE) |

**Archivo:** `endpoints/rlm/cases.py`

---

### `DELETE /records/{record_id}/cases/{link_id}`

Desvincula un expediente de un legajo.

**Permisos:** `can_edit` sobre la familia del legajo.

**Response (200):**

```json
{
    "success": true,
    "data": {"removed": true},
    "message": "Expediente desvinculado exitosamente"
}
```

**Archivo:** `endpoints/rlm/cases.py`

---

## Grupo G: Links con Documentos

### `GET /records/{record_id}/documents`

Lista documentos oficiales vinculados a un legajo con paginación.

**Permisos:** `can_view` sobre la familia del legajo.

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | 1 | Página (>= 1) |
| `page_size` | int | 20 | Ítems por página (1-100) |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "documents": [
            {
                "link_id": "uuid",
                "document_id": "uuid",
                "field_name": "habilitacion",
                "notes": "Documento de habilitacion",
                "linked_at": "2026-03-30 13:00:00",
                "official_number": "IF-2026-0001234-SMG",
                "reference": "Informe de habilitacion",
                "document_type": "IF",
                "is_auto": false,
                "resume": "Informe sobre habilitacion comercial..."
            }
        ],
        "total": 3,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    },
    "message": "Se encontraron 3 documentos vinculados"
}
```

!!! note "Documentos automáticos"
    Los documentos con `document_type = "IFRLM"` tienen `is_auto: true`. Son informes generados automáticamente por el sistema.

**Archivo:** `endpoints/rlm/documents.py`

---

### `POST /records/{record_id}/documents`

Vincula un documento oficial a un legajo. Opcionalmente se puede asociar a un campo específico del legajo.

**Permisos:** `can_edit` sobre la familia del legajo.

**Request:**

```json
{
    "document_id": "uuid-documento-oficial",
    "field_name": "habilitacion",
    "notes": "Documento de habilitacion"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_id` | string | Sí | ID del documento oficial |
| `field_name` | string | No | Campo del legajo al que se asocia |
| `notes` | string | No | Notas sobre la vinculación |

**Response (200):**

```json
{
    "success": true,
    "data": {
        "record_id": "uuid-legajo",
        "document_id": "uuid-documento"
    },
    "message": "Documento vinculado exitosamente"
}
```

**Errores:**

| Código | Causa |
|--------|-------|
| 404 | Legajo o documento no encontrado |
| 403 | Sin permiso `can_edit` |
| 409 | El documento ya está vinculado (constraint UNIQUE) |

**Archivo:** `endpoints/rlm/documents.py`

---

### `DELETE /records/{record_id}/documents/{link_id}`

Desvincula un documento de un legajo.

**Permisos:** `can_edit` sobre la familia del legajo.

**Response (200):**

```json
{
    "success": true,
    "data": {"removed": true},
    "message": "Documento desvinculado exitosamente"
}
```

**Archivo:** `endpoints/rlm/documents.py`

---

## Grupo H: Informe IFRLM

### `POST /records/{record_id}/report`

Genera un informe IFRLM (snapshot) del legajo. Crea un documento oficial tipo IFRLM con los datos actuales, lo firma automáticamente, lo vincula al legajo y registra en historial.

**Permisos:** `can_edit` sobre la familia del legajo.

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `record_id` | UUID | ID del legajo |

**Pipeline de generación:**

```
1. Leer datos actuales del legajo (campos, docs, cases)
2. Construir snapshot HTML
3. Pipeline: create_and_sign_case_document()
   -> PDFComposer /create-ifrlm/
   -> Notary (firma digital)
   -> R2 (almacenamiento)
4. Vincular IFRLM al legajo (record_document_links)
5. Registrar en historial: action=ifrlm_generated
```

**Response (200):**

```json
{
    "success": true,
    "data": {
        "document_id": "uuid",
        "official_number": "IFRLM-2026-0000001-SMG",
        "record_id": "uuid",
        "record_number": "RLM-2026-00000001-SMG-ARQ",
        "report_type": "IFRLM",
        "is_initial": false,
        "notes": "Informe de legajo",
        "generated_at": "2026-03-30T14:00:00",
        "generated_by": "Juan Perez"
    },
    "message": "Informe IFRLM generado exitosamente para legajo RLM-2026-00000001-SMG-ARQ"
}
```

!!! info "Informe inicial"
    Cuando se crea un legajo, se genera automáticamente un IFRLM inicial (con `is_initial: true`) desde el endpoint `POST /records` de forma asincrona.

**Archivo:** `endpoints/rlm/records.py`

---

## Errores Comunes

| Código | Error | Causa |
|--------|-------|-------|
| 401 | No autenticado | Token JWT inválido o expirado |
| 403 | Sin permisos | El usuario no tiene el permiso requerido sobre la familia |
| 404 | No encontrado | Legajo, registro, documento o expediente inexistente |
| 409 | Conflicto | Vinculación duplicada (constraint UNIQUE) |
| 422 | Validación | Datos inválidos, campo inexistente en schema, estado no permitido |
| 500 | Error interno | Error en servicios externos (PDFComposer, Notary) |

## Autenticación

Todos los endpoints requieren token JWT vía `Authorization: Bearer <token>`. El schema del tenant se resuelve automáticamente desde el token vía `get_tenant_schema`.
