# Base de Datos

## Overview

GDI Latam utiliza **PostgreSQL 17** como motor de base de datos, con arquitectura **multi-tenant** basada en schemas. Cada organización opera en su propio schema aislado, compartiendo tablas globales del schema `public`.

| Componente | Tecnología |
|------------|------------|
| Motor | PostgreSQL 17.0+ |
| Extensiones | pgvector, pg_trgm, unaccent |
| Hosting | Docker (pgvector/pgvector:pg17) |
| Multi-tenant | Un schema por organización |
| Connection Pool | Sin PgBouncer (psycopg2 directo con asyncpg en async) |
| ORM | Ninguno (psycopg2 directo con RealDictCursor) |

## Arquitectura Multi-Schema

```
PostgreSQL
|
+-- public/                         # Compartido por todos los tenants
|   +-- roles                       # 3 roles del sistema
|   +-- global_document_types       # Tipos de documento globales
|   +-- global_case_templates       # Plantillas de expediente globales
|   +-- municipalities              # Registro de tenants
|   +-- document_display_states     # 6 estados de visualizacion
|   +-- user_registry               # Mapeo email -> schema
|   +-- api_keys                    # API Keys (REST API)
|   +-- api_key_users               # Usuarios autorizados por API Key
|   +-- global_registry_families    # Familias de registros
|   +-- tenant_certificates         # Certificados digitales por tenant
|   +-- backup_access_log           # Log de accesos del sistema de backup
|   +-- (tablas LangGraph)          # Creadas automaticamente por GDI-AgenteLANG
|
+-- {schema_municipio}/             # Ej: 100_test, 101_ejemplo
|   +-- 35 tablas (Grupos A-J)
|   +-- ~52 indices
|   +-- 34 triggers updated_at + 1 trigger sync user_registry
|   +-- 1 funcion (fn_sync_user_registry)
|
+-- {schema_municipio}_audit/       # Ej: 100_test_audit
    +-- audit_log                   # Registro de auditoria
    +-- fn_log_change               # Funcion de auditoria
    +-- 9 triggers de auditoria (modo full/diff)
```

## Ambientes

| Ambiente | Host | Puerto | Uso |
|----------|------|--------|-----|
| Producción | `postgres:5432` (Docker interno) | 5432 | Producción |
| Desarrollo | `localhost:5432` | 5432 | Desarrollo y pruebas |

!!! warning "Ambiente de desarrollo"
    La base de datos de producción no debe modificarse sin autorización. Para desarrollo usar una instancia local de PostgreSQL.

### Conexión

```bash
# Formato generico (NO incluye credenciales reales)
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

El schema de pruebas es `100_test`. Cada backend se conecta y setea `search_path` al schema del tenant en cada request.

## Extensiones

| Extensión | Versión | Propósito |
|-----------|---------|-----------|
| `vector` (pgvector) | 0.7.0+ | Embeddings y búsqueda semántica (RAG) para GDI-AgenteLANG |
| `unaccent` | built-in | Búsquedas sin acentos ("trámite" encuentra "trámite") |
| `pg_trgm` | built-in | Búsqueda por similitud (trigram matching) |

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Estructura de Schemas

### Schema `public` (11 tablas)

Contiene datos globales compartidos por todas las organizaciones: roles del sistema, tipos de documento maestros, plantillas de expediente, registro de organizaciones activas, autenticación API, certificados digitales y log de backup.

Ver: [Schema Public](schema-public.md)

### Schema por organización (35 tablas)

Cada organización tiene su propio schema con la estructura completa: estructura organizacional, usuarios, documentos, expedientes, configuración, agente IA, notas, registros, responsables y favoritos de expediente.

Ver: [Schema Municipio](schema-municipio.md)

### Schema de auditoría (1 tabla)

Cada organización tiene un schema `{nombre}_audit` con una tabla `audit_log` y triggers automáticos sobre 9 tablas críticas. Desde la migración 137, cada trigger elige
cuánto guarda (modo `full` o `diff`) y no escribe nada cuando solo cambia una columna ruido
(por ejemplo, `users.last_access`).

Ver: [Schema Audit](schema-audit.md)

## Convenciones

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Tablas | `snake_case` | `document_draft`, `case_movements` |
| Primary keys | `UUID DEFAULT gen_random_uuid()` | `id UUID NOT NULL DEFAULT gen_random_uuid()` |
| Serial PKs | `SERIAL` o `BIGSERIAL` | `id SERIAL NOT NULL` (para tablas lookup) |
| Foreign keys | `{tabla}_id` o `{relacion}_id` | `document_type_id`, `created_by` |
| Timestamps | `TIMESTAMPTZ DEFAULT NOW()` | `created_at`, `updated_at` |
| Soft delete | `is_deleted BOOLEAN` o `is_active BOOLEAN` | `is_deleted NOT NULL DEFAULT false` |
| Búsqueda | Índices B-tree, GIN, HNSW | Según tipo de dato |

## Flujo de Deploy

=== "Producción (organización nueva)"

    ```
    01-install.sql       -- Extensiones + ENUMs + 11 tablas public (una vez)
         |
         v
    02-seed-global.sql   -- Roles + doc types + case templates (una vez)
         |
         v
    03-create-municipio.sql  -- Schema + audit + datos iniciales (por municipio)
    ```

=== "Dev/Test (100_test)"

    ```
    01-install.sql       -- Extensiones + ENUMs + 11 tablas public
         |
         v
    02-seed-global.sql   -- Datos globales
         |
         v
    04-seed-demo.sql     -- 100_test completo con datos demo (autonomo)
    ```

Ver: [Scripts de Deploy](scripts-deploy.md)

## Multi-Tenant en el Backend

El Backend usa `schema_name` como parámetro **keyword-only** en todas las funciones de base de datos:

```python
# CORRECTO - keyword-only
result = execute_query("SELECT * FROM users", schema_name=schema_name)

# INCORRECTO - causa TypeError en runtime
result = execute_query("SELECT * FROM users", schema_name)
```

El `search_path` se configura por transacción usando `SET LOCAL`:

```python
@contextmanager
def get_db_connection(schema_name: str):
    # Valida schema_name contra SQL injection
    validated_schema = validate_schema_name(schema_name)
    # SET LOCAL se resetea al final de la transaccion
    cursor.execute(f'SET LOCAL search_path TO "{validated_schema}", public')
    yield connection
```

!!! danger "Regla keyword-only"
    `schema_name` es siempre keyword-only (después de `*` en la firma). Pasar `schema_name` como argumento posicional causa `TypeError` en runtime. Este patrón previene SQL injection de tenant y hace explícito el schema en cada llamada.

## Índice de Secciones

| Sección | Contenido |
|---------|-----------|
| [Schema Public](schema-public.md) | 11 tablas globales: roles, document types, municipalities, API keys, tenant_certificates, backup_access_log |
| [Schema Municipio](schema-municipio.md) | 35 tablas por tenant (Grupos A-J) con índices |
| [Schema Audit](schema-audit.md) | Auditoría automática con triggers |
| [Scripts de Deploy](scripts-deploy.md) | Archivos SQL, flujo de ejecución, migraciones, herramientas Python |
| [Numeración](numeracion.md) | Sistema de numeración secuencial con advisory lock |
| [ENUMs y Tipos](enums-y-tipos.md) | 7 ENUMs y tipos custom |
| [Herramientas](herramientas.md) | psql, pgAdmin, scripts utiles |
| [Schema RLM](schema-rlm.md) | Tablas del Registro de Legajos Municipales (familias, registros, campos) |
