# Schema Audit

Cada organización tiene un schema de auditoría dedicado con nomenclatura `{schema_name}_audit` (ejemplo: `100_test_audit`). Registra automáticamente cambios en 9 tablas críticas mediante triggers.

## Arquitectura

```
{schema_name}_audit/
+-- audit_log             # Tabla unica de auditoria
+-- fn_log_change()       # Funcion que registra los cambios
+-- 9 triggers            # Uno por tabla auditada (trg_audit_*)
```

## Tabla: audit_log

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | BIGSERIAL | NO | auto | Identificador secuencial |
| `event_time` | TIMESTAMPTZ | NO | `NOW()` | Momento del evento |
| `schema_name` | TEXT | NO | - | Schema donde ocurrio el cambio |
| `table_name` | TEXT | NO | - | Tabla modificada |
| `operation` | TEXT | NO | - | Tipo: INSERT, UPDATE, DELETE |
| `user_name` | TEXT | SI | - | Usuario de PostgreSQL (`current_user`) |
| `user_id` | UUID | SI | - | ID del usuario de la app (vía GUC `app.user_id`) |
| `auth_source` | VARCHAR(20) | SI | - | Origen de autenticación |
| `old_row` | JSONB | SI | - | Fila antes del cambio (UPDATE/DELETE) |
| `new_row` | JSONB | SI | - | Fila después del cambio (INSERT/UPDATE) |
| `changed_fields` | TEXT[] | SI | - | Lista de campos modificados (solo UPDATE) |

**Índices:**

| Índice | Columnas | Propósito |
|--------|----------|-----------|
| `idx_{schema}_audit_audit_log_event_time` | `event_time` | Búsqueda por fecha |
| `idx_{schema}_audit_audit_log_table` | `table_name` | Filtrar por tabla |
| `idx_{schema}_audit_audit_log_user` | `user_id` | Buscar por usuario |
| `idx_{schema}_audit_audit_log_table_event` | `(table_name, event_time DESC)` | Pantalla de auditoría: una tabla, lo más nuevo primero (migración 137) |

## Valores de auth_source

| Valor | Origen | Descripción |
|-------|--------|-------------|
| `jwt` | GDI-Frontend | Usuario autenticado vía Auth0 JWT |
| `api_key` | REST API | Acceso vía API Key (GDI-MCP) |
| `mcp_oauth` | MCP Server | Acceso vía OAuth del MCP Server |
| `testing` | Testing mode | Modo de pruebas (sin Auth0) |
| `system` | Backend | Operaciones automáticas del sistema |

## Función: fn_log_change

La función `fn_log_change()` se ejecuta como trigger AFTER en cada operación. Desde la
migración 137 recibe 2 argumentos por trigger (`TG_ARGV`):

| Argumento | Valores | Qué hace |
|-----------|---------|----------|
| `TG_ARGV[0]` modo | `full` o `diff` (sin argumento: `full`) | Cuánto de la fila se guarda |
| `TG_ARGV[1]` columnas ruido | Lista separada por comas (puede ir vacía) | Columnas que solas no generan registro |

Qué registra en cada operación:

- **INSERT**: `new_row` con la fila insertada.
- **UPDATE**: `old_row`, `new_row` y `changed_fields`. Antes calcula qué columnas cambiaron.
- **DELETE**: `old_row` con la fila eliminada.

### Cuándo no escribe nada

En un UPDATE, la función descarta `updated_at` y las columnas ruido. Si no queda ningún cambio,
**no escribe** la fila de auditoría. Ejemplos:

- un usuario entra al sistema y solo cambia `users.last_access`;
- el agente IA indexa un documento y solo cambia `official_documents.indexed_at`;
- un UPDATE que no cambia ningún valor.

### Modo full y modo diff

| Modo | INSERT y DELETE | UPDATE |
|------|-----------------|--------|
| `full` | La fila entera | `old_row` y `new_row` con la fila entera |
| `diff` | La fila sin las columnas pesadas | `old_row` y `new_row` con `id` y solo las columnas que cambiaron |

Las columnas pesadas son `content`, `resume`, `short_resume`, `ai_summary` y `short_ai_summary`.
En modo `diff` no se copia su valor. En un UPDATE queda la clave con el texto `"(cambió)"`.

`changed_fields` queda **completo** en los dos modos: incluye `updated_at` y las columnas ruido.
El BackOffice lo lee igual que antes.

Ejemplo: un UPDATE de `cases` que cambia `status` guarda en modo `diff`:

```json
{ "old_row": { "id": "…", "status": "active" },
  "new_row": { "id": "…", "status": "archived" },
  "changed_fields": ["status", "updated_at"] }
```

### Contexto de Auditoría (GUC)

La función lee variables de sesión inyectadas por el Backend:

```sql
-- El Backend inyecta estos valores antes de cada operacion
SET LOCAL app.user_id = 'uuid-del-usuario';
SET LOCAL app.auth_source = 'jwt';
```

```python
# En Python (GDI-Backend), el contexto se inyecta automaticamente:
with get_db_cursor(
    commit=True,
    schema_name=schema_name,
    user_id=creator_id,      # Se inyecta como app.user_id
    auth_source="jwt"        # Se inyecta como app.auth_source
) as cursor:
    cursor.execute("INSERT INTO ...")
```

La función usa `current_setting('app.user_id', true)` con el segundo parámetro `true` para retornar NULL en lugar de error si la variable no existe.

### Código SQL

Fragmento de la versión de la migración 137 (la completa está en `sql/03-create-municipio.sql`):

```sql
CREATE OR REPLACE FUNCTION "{SCHEMA_NAME}_audit"."fn_log_change"()
RETURNS TRIGGER AS $$
DECLARE
    v_old_row JSONB := NULL;
    v_new_row JSONB := NULL;
    v_changed_fields TEXT[] := '{}';
    v_useful TEXT[];
    v_user_id UUID := NULL;
    v_auth_source VARCHAR(20) := NULL;
    -- TG_ARGV[0] = 'full' | 'diff' (sin argumento = 'full')
    -- TG_ARGV[1] = columnas ruido separadas por coma
    v_mode TEXT := COALESCE(NULLIF(btrim(TG_ARGV[0]), ''), 'full');
    v_noise TEXT[] := ARRAY(
        SELECT btrim(x) FROM unnest(string_to_array(COALESCE(TG_ARGV[1], ''), ',')) AS x
        WHERE btrim(x) <> ''
    );
    -- Columnas pesadas: en modo 'diff' no se copia su valor
    v_heavy TEXT[] := ARRAY['content', 'resume', 'short_resume', 'ai_summary', 'short_ai_summary'];
BEGIN
    -- (lectura de app.user_id y app.auth_source, igual que antes)

    IF TG_OP = 'UPDATE' THEN
        v_old_row := to_jsonb(OLD);
        v_new_row := to_jsonb(NEW);

        SELECT COALESCE(array_agg(n.key), '{}') INTO v_changed_fields
        FROM jsonb_each(v_new_row) AS n
        WHERE v_old_row -> n.key IS DISTINCT FROM n.value;

        -- Cambios que cuentan: sin updated_at ni columnas ruido
        SELECT COALESCE(array_agg(k), '{}') INTO v_useful
        FROM unnest(v_changed_fields) AS k
        WHERE k <> 'updated_at' AND NOT (k = ANY (v_noise));

        IF cardinality(v_useful) = 0 THEN
            RETURN NEW;  -- no escribe nada
        END IF;

        IF v_mode = 'diff' THEN
            -- id + solo las claves utiles; las pesadas llevan '"(cambió)"'
            ...
        END IF;

        INSERT INTO "{SCHEMA_NAME}_audit".audit_log(
            schema_name, table_name, operation, user_name, user_id, auth_source,
            old_row, new_row, changed_fields
        ) VALUES (
            TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, current_user, v_user_id, v_auth_source,
            v_old_row, v_new_row, v_changed_fields
        );
        RETURN NEW;
    END IF;
    -- INSERT y DELETE: en modo 'diff' se guarda la fila sin las columnas pesadas
    ...
END;
$$ LANGUAGE plpgsql;
```

## Tablas Auditadas (9)

| Tabla | Grupo | Modo | Columnas ruido | Que se registra |
|-------|-------|------|----------------|-----------------|
| `users` | Usuarios | `full` | `last_access` | Alta, cambios y baja de usuarios |
| `departments` | Estructura | `full` | - | Creación, renombramiento, cambio de jerarquía |
| `sectors` | Estructura | `full` | - | Creación, activacion/desactivacion |
| `citizens` | Ciudadanos | `full` | - | Alta y cambios de ciudadanos |
| `official_documents` | Documentos | `diff` | `indexed_at` | Numeración de documentos oficiales |
| `cases` | Expedientes | `diff` | `last_modified_at` | Creación, cambio de estado, archivado |
| `case_movements` | Expedientes | `diff` | - | Transferencias, asignaciones, subsanaciones |
| `case_assignment_tasks` | Expedientes | `diff` | - | Tareas de asignación |
| `case_official_documents` | Expedientes | `diff` | - | Vinculacion/desvinculacion de docs a expedientes |

Conteo por schema de municipio: 9 triggers `trg_audit_*` más 1 de sincronización
(`trg_sync_user_registry`, en `users`), 10 en total. Aparte están los triggers de `updated_at`.

### Triggers

Cada trigger es de tipo `AFTER INSERT OR UPDATE OR DELETE ... FOR EACH ROW` y pasa el modo y las
columnas ruido:

```sql
-- Ejemplo: trigger en cases
CREATE TRIGGER "trg_audit_cases"
    AFTER INSERT OR UPDATE OR DELETE ON "{SCHEMA_NAME}"."cases"
    FOR EACH ROW EXECUTE FUNCTION "{SCHEMA_NAME}_audit"."fn_log_change"('diff', 'last_modified_at');
```

### updated_at que ignora el ruido

La migración 137 también creó `public.fn_set_updated_at_skip_noise()`. Es como
`public.fn_set_updated_at()`, pero no mueve `updated_at` cuando lo único que cambió son las
columnas ruido. Se usa solo en 2 tablas:

| Tabla | Trigger | Columna ruido |
|-------|---------|---------------|
| `users` | `trg_users_updated_at` | `last_access` |
| `official_documents` | `trg_official_documents_updated_at` | `indexed_at` |

Un UPDATE que cambia otra columna, que pone `updated_at` a mano o que no cambia nada sigue
moviendo `updated_at` como siempre. Las demás tablas siguen con `public.fn_set_updated_at()`.

!!! note "Tablas NO auditadas"
    Tablas de alta frecuencia como `document_draft`, `document_signers`, `user_roles` y `notes_recipients` no tienen triggers de auditoría para evitar impacto en rendimiento. Solo se auditan las tablas donde los cambios tienen impacto legal o administrativo.

!!! info "Lo ya escrito no cambia"
    La migración 137 no borra ni achica los registros que ya estaban en `audit_log`. Rige para
    los cambios nuevos.

## Consultas Utiles

### Ver últimos cambios

```sql
SELECT event_time, table_name, operation, user_id, changed_fields
FROM "100_test_audit".audit_log
ORDER BY event_time DESC
LIMIT 20;
```

### Filtrar por tabla y operación

```sql
SELECT event_time, operation, user_id, auth_source,
       new_row->>'case_number' as case_number,
       new_row->>'status' as status
FROM "100_test_audit".audit_log
WHERE table_name = 'cases'
  AND operation = 'UPDATE'
ORDER BY event_time DESC;
```

### Ver cambios de un usuario específico

```sql
SELECT event_time, table_name, operation, changed_fields
FROM "100_test_audit".audit_log
WHERE user_id = 'uuid-del-usuario'
ORDER BY event_time DESC;
```

### Ver transferencias de expedientes

```sql
SELECT event_time,
       new_row->>'case_id' as case_id,
       new_row->>'type' as movement_type,
       new_row->>'reason' as reason,
       auth_source
FROM "100_test_audit".audit_log
WHERE table_name = 'case_movements'
  AND operation = 'INSERT'
ORDER BY event_time DESC;
```
