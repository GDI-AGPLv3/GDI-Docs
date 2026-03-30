# Servicios RLM

Modulos de logica de negocio para el sistema de legajos (RLM). Organizados por dominio funcional.

**Ubicacion:** `services/rlm/`

## Arquitectura

```
services/rlm/
├── queries.py       # SQL centralizado (~530 lineas, ~25 queries)
├── records.py       # CRUD de legajos (crear, leer, listar, actualizar)
├── registries.py    # Operaciones sobre familias de registros
├── fields.py        # Campos enriquecidos (actualizar, verificar)
├── history.py       # Historial de cambios
├── relations.py     # Relaciones entre legajos
├── links.py         # Vinculacion con documentos y expedientes
├── report.py        # Generacion de informes IFRLM
├── validation.py    # Validacion de datos contra data_schema
└── permissions.py   # Verificacion de permisos por sector
```

---

## Records (`records.py`)

CRUD principal de legajos. Todas las funciones usan `schema_name` keyword-only.

### Funciones

| Funcion | Descripcion | Permisos |
|---------|-------------|----------|
| `create_record()` | Crea legajo con numero atomico | `can_create` |
| `get_record()` | Detalle completo + permisos | `can_view` |
| `list_records()` | Listado paginado con filtros | `can_view` (filtrado) |
| `update_record()` | Actualiza estado y/o nombre | `can_edit` |
| `autocomplete_records()` | Autocompletado por numero | `can_view` |

### create_record()

```python
def create_record(
    registry_code: str,
    data: dict,
    display_name: str,
    user_id: str,
    *,
    schema_name: str
) -> dict:
```

**Flujo:**

1. Buscar la familia por codigo (`get_registry_by_code`)
2. Verificar permiso `can_create`
3. Obtener info del sector del usuario
4. Validar datos contra `data_schema` (con `skip_required=True`)
5. Calcular `next_expiration` (fecha de vencimiento mas proxima)
6. Transaccion atomica:
    - Obtener acronimo del municipio
    - Advisory lock `777777`
    - Obtener siguiente secuencia (`MAX(record_number) + 1`)
    - Generar numero: `RLM-{ANIO}-{SEQ:08d}-{MUNI}-{CODE}`
    - INSERT del legajo
7. Registrar en historial (fuera de la transaccion)

!!! warning "Advisory lock"
    El lock `pg_advisory_xact_lock(777777)` se usa para evitar race conditions en la generacion de numeros. Es diferente del `888888` usado para documentos. El lock se libera automaticamente al commit/rollback de la transaccion.

### list_records()

```python
def list_records(
    user_id: str,
    *,
    schema_name: str,
    registry_code: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
```

**Flujo:**

1. Obtener permisos bulk (todas las familias)
2. Filtrar familias donde el usuario tiene `can_view`
3. Construir WHERE dinamico con filtros opcionales
4. Ejecutar count + list queries
5. Retornar resultado paginado

La busqueda (`search`) usa ILIKE sobre `record_number`, `display_name` y `data::text`, con escape de caracteres especiales.

### update_record()

```python
def update_record(
    record_id: str,
    user_id: str,
    *,
    schema_name: str,
    new_state: Optional[str] = None,
    new_display_name: Optional[str] = None,
    reason: Optional[str] = None,
) -> dict:
```

Actualiza estado y/o nombre en una transaccion atomica junto con el registro de historial. Valida que el estado nuevo este en la lista de `states` de la familia.

---

## Registries (`registries.py`)

Operaciones sobre familias de registros (`registry_families`).

### Funciones

| Funcion | Descripcion |
|---------|-------------|
| `list_registries()` | Lista familias con conteo y permisos bulk |
| `get_registry_detail()` | Detalle con `data_schema` completo |
| `get_registry_by_code()` | Busca por codigo (ARQ, LUM, ORD) |

### list_registries()

```python
def list_registries(user_id: str, *, schema_name: str) -> dict:
```

Usa `get_bulk_permissions()` para resolver permisos de todas las familias en 2 queries (evita N+1). Retorna lista de familias con `permissions` y `record_count`.

---

## Fields (`fields.py`)

Manejo de campos enriquecidos individuales. Usa `jsonb_set` atomico + `SELECT FOR UPDATE` para evitar race conditions.

### Funciones

| Funcion | Descripcion | Permisos |
|---------|-------------|----------|
| `update_field()` | Actualiza un campo individual | `can_edit` |
| `verify_field()` | Marca campo como verificado | `can_verify` |

### update_field()

```python
def update_field(
    record_id: str,
    field_name: str,
    user_id: str,
    value: Any = None,
    expiration_date: Optional[str] = None,
    document_id: Optional[str] = None,
    notes: Optional[str] = None,
    document_reference: Optional[str] = None,
    document_resume: Optional[str] = None,
    *,
    schema_name: str
) -> dict:
```

**Flujo:**

1. Lectura sin lock para validaciones rapidas (permisos, schema)
2. Verificar `can_edit`
3. Validar campo contra `data_schema`
4. Obtener info del usuario
5. Transaccion atomica:
    - `SELECT ... FOR UPDATE OF r` (lockea la fila)
    - Leer campo actual desde datos frescos
    - Construir nuevo campo (merge con valores existentes)
    - Calcular `next_expiration` con datos frescos + nuevo campo
    - `UPDATE records SET data = jsonb_set(data, path, value)` (atomico)
    - INSERT en `record_history`

!!! info "jsonb_set atomico"
    Se usa `jsonb_set(COALESCE(data, '{}'::jsonb), %s, %s::jsonb)` para actualizar solo el campo modificado. El path es `'{nombre_campo}'`. Esto permite que dos usuarios editen campos distintos del mismo legajo sin pisarse.

### verify_field()

```python
def verify_field(
    record_id: str,
    field_name: str,
    user_id: str,
    document_id: str,
    notes: Optional[str] = None,
    *,
    schema_name: str
) -> dict:
```

Similar a `update_field()` pero:

- Requiere permiso `can_verify` (no `can_edit`)
- El campo debe tener `has_verification: true` en el schema
- El `document_id` debe existir en `official_documents`
- Agrega metadata de verificacion: `verified`, `verified_at`, `verified_by`, `verified_by_name`, `verified_document_id`, `verified_document_number`, `verified_document_resume`

---

## History (`history.py`)

Servicio de historial de cambios.

### Funciones

| Funcion | Descripcion |
|---------|-------------|
| `record_action()` | Registra una accion (fire-and-forget, no propaga errores) |
| `get_history()` | Obtiene historial paginado |

### record_action()

```python
def record_action(
    record_id: str,
    action: str,
    user_id: str,
    sector_id: Optional[str] = None,
    field_name: Optional[str] = None,
    before_value: Any = None,
    after_value: Any = None,
    *,
    schema_name: str
) -> None:
```

!!! note "Tolerancia a fallos"
    `record_action()` captura excepciones y solo las loguea, sin propagarlas. Esto evita que un error de historial bloquee la operacion principal. Sin embargo, cuando se registra historial dentro de una transaccion (como en `update_record()` o `update_field()`), el INSERT va en la misma transaccion que la operacion principal.

### get_history()

```python
def get_history(
    record_id: str,
    user_id: str,
    *,
    schema_name: str,
    page: int = 1,
    page_size: int = 20,
) -> dict:
```

Verifica `can_view` antes de retornar el historial via `verify_record_view_permission()`.

---

## Relations (`relations.py`)

Relaciones entre legajos. Las relaciones son bidireccionales en la consulta (source O target) pero se almacenan direccionalmente.

### Funciones

| Funcion | Descripcion | Permisos |
|---------|-------------|----------|
| `get_relations()` | Listar relaciones (bidireccional) | `can_view` |
| `create_relation()` | Crear relacion | `can_edit` |
| `delete_relation()` | Eliminar relacion | `can_edit` |

### create_relation()

Validaciones:

- No se puede crear relacion de un legajo consigo mismo
- Ambos legajos deben existir
- Usuario necesita `can_edit` sobre el legajo origen
- Constraint UNIQUE `(source_record_id, target_record_id)` en BD

### get_relations()

La query usa `UNION ALL` para buscar relaciones donde el legajo es source O target, combinando ambos resultados en una lista unificada.

---

## Links (`links.py`)

Vinculacion de documentos oficiales y expedientes con legajos. Dos secciones independientes en el mismo archivo.

### Funciones - Documentos

| Funcion | Descripcion | Permisos |
|---------|-------------|----------|
| `get_linked_documents()` | Listar documentos vinculados | `can_view` |
| `link_document()` | Vincular documento | `can_edit` |
| `unlink_document()` | Desvincular documento | `can_edit` |

### Funciones - Expedientes

| Funcion | Descripcion | Permisos |
|---------|-------------|----------|
| `get_linked_cases()` | Listar expedientes vinculados | `can_view` |
| `link_case()` | Vincular expediente | `can_edit` |
| `unlink_case()` | Desvincular expediente | `can_edit` |

### Duplicados

Ambas funciones `link_*` capturan `psycopg2.IntegrityError` y lo convierten en `ConflictError` (HTTP 409) cuando se intenta vincular algo que ya esta vinculado. Los constraints UNIQUE en BD son `(record_id, document_id)` y `(record_id, case_id)`.

### Historial enriquecido

Al vincular un documento o expediente, se obtiene la info del documento/case (`official_number`, `reference`, `short_ai_summary`) para registrarla en el historial. Esto permite que el historial muestre informacion legible sin necesidad de JOINs adicionales.

---

## Report (`report.py`)

Generacion de informes IFRLM (snapshot de legajo como documento oficial firmado).

### generate_ifrlm()

```python
async def generate_ifrlm(
    record_id: str,
    user_id: str,
    *,
    schema_name: str,
    notes: str = None,
    is_initial: bool = False,
) -> Dict[str, Any]:
```

**Pipeline completo:**

```
1. Leer datos del legajo (campos JSONB)
2. Leer documentos vinculados (hasta 100)
3. Leer expedientes vinculados (hasta 100)
4. Obtener info del usuario generador
5. Construir snapshot (_build_snapshot_data)
6. Obtener datos del firmante (signer_data)
7. Obtener settings del tenant (city, logo_url)
8. Ejecutar pipeline: create_and_sign_case_document()
   -> PDFComposer /create-ifrlm/
   -> Notary (firma digital)
   -> R2 (almacenamiento)
9. Vincular IFRLM al legajo (record_document_links)
10. Registrar en historial (ifrlm_generated)
```

Los pasos 9 y 10 son atomicos (misma transaccion).

!!! info "Funcion async"
    `generate_ifrlm()` es `async` porque llama a `create_and_sign_case_document()` que es async (hace HTTP a PDFComposer y Notary). Es la unica funcion async en todo el modulo RLM.

### Funciones auxiliares

| Funcion | Descripcion |
|---------|-------------|
| `_build_snapshot_data()` | Estructura datos del legajo para el informe |
| `_build_ifrlm_html()` | Genera HTML del informe con tablas de campos, docs y cases |
| `_format_field_value()` | Formatea un campo enriquecido para HTML (maneja dicts, listas, verificaciones) |

---

## Validation (`validation.py`)

Validacion de datos contra el `data_schema` de la familia de registro.

### Funciones

| Funcion | Descripcion |
|---------|-------------|
| `validate_record_data()` | Valida datos completos contra schema |
| `validate_field_update()` | Valida que un campo exista en el schema |
| `calculate_next_expiration()` | Calcula proxima fecha de vencimiento |

### validate_record_data()

```python
def validate_record_data(
    data: dict,
    data_schema: dict,
    *,
    skip_required: bool = False
) -> dict:
```

Recorre el `data_schema` y para cada campo:

1. Verifica si es requerido (a menos que `skip_required=True`)
2. Si tiene valor, construye un campo enriquecido via `_build_enriched_field()`

### Campos enriquecidos

La funcion `_build_enriched_field()` construye un dict con:

| Propiedad del schema | Efecto en el campo |
|---------------------|--------------------|
| (siempre) | `{"value": valor}` |
| `has_expiration` | Agrega `expiration_date` desde `{campo}_expiration` |
| `has_document` o `type: "file"` | Agrega `document_id`, `document_reference`, `document_resume` |
| `has_verification` | Inicializa `verified: false`, `verified_at: null`, `verified_by: null` |

### Tipos de campo validos

```python
VALID_FIELD_TYPES = {"text", "number", "date", "select", "boolean", "file", "textarea"}
```

### calculate_next_expiration()

```python
def calculate_next_expiration(data: dict, data_schema: dict) -> Optional[str]:
```

Recorre todos los campos con `has_expiration` en el schema, extrae las `expiration_date` de los datos, y retorna la mas proxima (la primera en vencer). Retorna `None` si no hay campos con vencimiento.

---

## Permissions (`permissions.py`)

Verificacion de permisos basada en la tabla `registry_family_permissions`.

### Funciones

| Funcion | Descripcion |
|---------|-------------|
| `check_permission()` | Verifica un permiso especifico (bool) |
| `get_user_permissions()` | Obtiene todos los permisos sobre una familia |
| `get_bulk_permissions()` | Obtiene permisos sobre TODAS las familias (2 queries) |
| `verify_record_view_permission()` | Verifica can_view o lanza error |

### Logica de permisos

1. Se obtienen todos los sectores del usuario (principal + adicionales via `user_sector_permissions`)
2. Se buscan permisos de cada sector en `registry_family_permissions`
3. **Logica OR**: si CUALQUIER sector del usuario tiene el permiso, se autoriza

```python
# Ejemplo: usuario con sector principal PRIV-INTE y adicional MESA-INTE
# Si MESA-INTE tiene can_view pero PRIV-INTE no, el usuario SI tiene can_view
```

### Permisos disponibles

| Permiso | Descripcion | Endpoints que lo usan |
|---------|-------------|----------------------|
| `can_create` | Crear legajos | `POST /records` |
| `can_edit` | Editar legajos, campos, relaciones, links | PATCH, POST, DELETE en records/fields/relations/cases/documents |
| `can_view` | Ver legajos, historial, relaciones, links | Todos los GET |
| `can_verify` | Verificar campos enriquecidos | `POST /records/{id}/fields/{field}/verify` |

### get_bulk_permissions()

```python
def get_bulk_permissions(user_id: str, *, schema_name: str) -> dict:
```

Optimizacion para evitar N+1 al listar familias:

1. Query 1: obtener sector_ids del usuario
2. Query 2: obtener TODOS los permisos de esos sectores con un solo `SELECT ... WHERE sector_id IN (...)`
3. Agrupar por `registry_family_id` con logica OR

Retorna `{registry_family_id: {can_create, can_edit, can_view, can_verify}}`.

---

## Queries (`queries.py`)

Centraliza todas las consultas SQL del modulo RLM. Cada query es una funcion que retorna un string SQL.

### Queries por categoria

| Categoria | Funciones | Proposito |
|-----------|-----------|-----------|
| **Registros** | `get_registries_query`, `get_registry_detail_query`, `get_registry_by_code_query` | SELECT de registry_families |
| **Legajos** | `get_records_list_query`, `get_records_count_query`, `get_record_detail_query`, `get_record_family_query`, `insert_record_query`, `update_record_query` | CRUD de records |
| **Campos** | `get_record_detail_for_update_query`, `update_record_field_atomic_query`, `update_record_data_query` | SELECT FOR UPDATE + jsonb_set |
| **Permisos** | `get_sector_permissions_query`, `get_all_permissions_for_sectors_query` | SELECT de registry_family_permissions |
| **Historial** | `insert_history_query`, `get_record_history_query`, `get_record_history_count_query` | CRUD de record_history |
| **Links docs** | `get_record_documents_query`, `get_record_documents_count_query`, `insert_document_link_query`, `delete_document_link_query` | record_document_links |
| **Links cases** | `get_record_cases_query`, `get_record_cases_count_query`, `insert_case_link_query`, `delete_case_link_query` | record_case_links |
| **Relaciones** | `get_record_relations_query`, `get_record_relations_count_query`, `insert_relation_query`, `delete_relation_query` | record_relations |
| **Numeracion** | `get_next_record_sequence_query` | Secuencia para numeros RLM |
| **Usuarios** | `get_user_sector_info_query` | Info sector del usuario |
| **Autocomplete** | `autocomplete_records_query` | Autocompletado con permisos |

### Queries dinamicas

Algunas queries aceptan parametros para construir SQL dinamico:

```python
# WHERE dinamico con filtros opcionales
def get_records_list_query(where_clauses: list[str]) -> str:

# SET dinamico segun campos a actualizar
def update_record_query(update_state: bool = False, update_display_name: bool = False) -> str:

# IN clause dinamico segun cantidad de sectores
def get_all_permissions_for_sectors_query(sector_ids: list[str]) -> tuple[str, tuple]:

# IN clause dinamico segun cantidad de sectores
def autocomplete_records_query(sector_ids: list[str]) -> str:
```

### Query destacada: FOR UPDATE

```python
def get_record_detail_for_update_query() -> str:
    """
    SELECT ... FROM records r
    JOIN registry_families rf ON ...
    WHERE r.id = %s
    FOR UPDATE OF r
    """
```

El `FOR UPDATE OF r` lockea solo la fila del record (no las tablas joineadas). Esto es clave para la atomicidad de `update_field()` y `verify_field()`.

### Query destacada: jsonb_set

```python
def update_record_field_atomic_query() -> str:
    """
    UPDATE records
    SET data = jsonb_set(COALESCE(data, '{}'::jsonb), %s, %s::jsonb),
        next_expiration = %s,
        updated_at = now()
    WHERE id = %s
    RETURNING id, data, next_expiration, updated_at
    """
```

Actualiza solo un campo del JSONB `data` sin tocar los demas. El `COALESCE(data, '{}'::jsonb)` maneja el caso donde `data` es NULL.
