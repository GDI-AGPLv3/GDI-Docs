# Base de Datos

Capa de acceso a datos definida en `database.py`. Usa **asyncpg** con pool nativo async. Migrado de psycopg2 en VersionCimientos.

## Pool de Conexiones

```python
# database.py
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=ASYNCPG_MIN_SIZE,   # default 2, configurable via ASYNCPG_MIN_SIZE
    max_size=ASYNCPG_MAX_SIZE,   # default 8, configurable via ASYNCPG_MAX_SIZE
    command_timeout=ASYNCPG_COMMAND_TIMEOUT,  # default 60s
    init=_init_conn,   # registra codecs JSON/JSONB/UUID
)
```

El pool se inicializa al arrancar la aplicacion en el `lifespan` de FastAPI (no en `startup`).

## Multi-Tenant: schema_name

!!! danger "Regla Critica"
    **Todas** las funciones de BD reciben `schema_name` como parametro **keyword-only** (despues de `*`). Esto es obligatorio para evitar SQL injection y tenant leakage.

```python
# CORRECTO
result = execute_query("SELECT ...", schema_name=schema_name)

# INCORRECTO - causa TypeError en runtime
result = execute_query("SELECT ...", schema_name)
```

### Como funciona

1. El `TenantMiddleware` extrae `schema_name` del header `X-Tenant-Schema`
2. El endpoint lo obtiene via `request.state.schema_name` o `Depends(get_tenant_schema)`
3. Se pasa a funciones de BD como `schema_name=schema_name`
4. `get_conn()` ejecuta `SET LOCAL search_path TO "{schema}", public` dentro de una transaccion

## Funciones Principales

### get_conn

Context manager async que adquiere una conexion del pool con tenant context seguro.

```python
@asynccontextmanager
async def get_conn(
    *,
    schema_name: str,
    user_id: Optional[str] = None,
    auth_source: Optional[str] = None,
):
    """
    Adquiere conexion del pool con SET LOCAL search_path + GUC de auditoria.
    Siempre abre transaccion: el search_path se revierte automaticamente al salir.
    """
```

!!! danger "Seguridad multi-tenant"
    Toda adquisicion abre SIEMPRE una transaccion y usa `SET LOCAL search_path`. Al COMMIT/ROLLBACK el search_path vuelve al default del pool. La conexion NUNCA regresa al pool contaminada con el tenant anterior.

### with_tenant

Establece tenant context en una conexion que ya tiene una transaccion abierta. Usar cuando el caller pasa `conn` explicitamente.

```python
async def with_tenant(
    conn: asyncpg.Connection,
    *,
    schema_name: str,
    user_id: Optional[str] = None,
    auth_source: Optional[str] = None,
) -> None:
```

### fetch_all

SELECT que devuelve multiples filas.

```python
async def fetch_all(sql: str, *params, schema_name: str) -> list[asyncpg.Record]:
```

### fetch_one

SELECT que devuelve una fila o None.

```python
async def fetch_one(sql: str, *params, schema_name: str) -> Optional[asyncpg.Record]:
```

### fetch_val

Escalar de la primera columna. Util para `INSERT ... RETURNING id`.

```python
async def fetch_val(sql: str, *params, schema_name: str, column: int = 0) -> Any:
```

### execute

INSERT/UPDATE/DELETE sin RETURNING. Devuelve el status (ej: `'UPDATE 1'`).

```python
async def execute(
    sql: str,
    *params,
    schema_name: str,
    user_id: Optional[str] = None,
    auth_source: Optional[str] = None,
) -> str:
```

### transaction

Context manager async para transacciones atomicas multi-statement.

```python
@asynccontextmanager
async def transaction(
    *,
    schema_name: str,
    user_id: Optional[str] = None,
    auth_source: Optional[str] = None,
):
```

**Uso:**

```python
async with transaction(schema_name="200_muni", user_id=uid) as conn:
    await conn.execute("INSERT INTO ...", a, b)
    doc_id = await conn.fetchval("INSERT ... RETURNING id", c)
# COMMIT automatico al salir sin excepcion; ROLLBACK si excepcion
```

## Validacion de Schema

```python
def validate_schema_name(schema_name: str) -> str:
```

Valida que el schema sea seguro para SQL:

- No vacio ni None
- **Normaliza a minusculas** y elimina espacios
- Solo letras minusculas, numeros y guion bajo (`^[a-z0-9_]+$`)
- Maximo 63 caracteres (limite PostgreSQL)
- Bloquea schemas reservados (`information_schema`, `pg_catalog`, `pg_toast`)
- Ejemplos validos: `"200_muni"`, `"public"`, `"municipio_abc"`

!!! info "Normalizacion"
    `validate_schema_name` llama a `.strip().lower()` antes de validar. El schema ingresado siempre se normaliza a minusculas en la capa de BD.

## Codecs asyncpg

Al inicializar cada conexion del pool (`_init_conn`), se registran codecs automaticos:

- `json` / `jsonb` — encode/decode con `json.dumps` / `json.loads`
- `uuid` — devuelve como `str` (compatible con Pydantic `str` fields, igual que psycopg2)

## Conexion directa a PostgreSQL

El backend conecta directo a PostgreSQL (no PgBouncer). El pool asyncpg maneja sus propias conexiones. La deteccion de PgBouncer es por `DB_PORT == 6432` pero **no esta activada** en produccion actual.

## Funciones de Validacion

```python
async def check_user_exists(user_id: str, *, schema_name: str) -> bool:
async def check_document_exists(document_id: str, *, schema_name: str) -> bool:
async def get_document_basic_info(document_id: str, *, schema_name: str) -> Optional[asyncpg.Record]:
```

!!! note "Sin get_user_basic_info"
    `get_user_basic_info()` no existe en `database.py`. Los datos de usuario se obtienen via `services/users/` o `user_service.py`.

## Numeracion

La numeracion con advisory lock esta en `shared/numbering.py`, no en `database.py`.

- **Documentos**: advisory lock `888888`
- **Legajos (RLM)**: advisory lock `777777`

Formato de numero de expediente: `EE-{año}-{secuencia:06d}-{organizacion}-{departamento}`

## Contexto de Auditoria

Cuando se pasan `user_id` y `auth_source` a `get_conn()`, `execute()` o `transaction()`, se inyectan como GUC de PostgreSQL usando `set_config(..., true)` (scope transaccional):

```sql
SELECT set_config('app.user_id', 'uuid-del-usuario', true);
SELECT set_config('app.auth_source', 'jwt', true);
```

Esto permite que los triggers de auditoria en la BD registren quien hizo cada operacion. El GUC se revierte automaticamente al final de la transaccion (scope `true` = local a la transaccion).
