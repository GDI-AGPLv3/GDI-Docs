# Base de Datos

## Overview

GDI Latam utiliza **PostgreSQL 17** como motor de base de datos, con arquitectura **multi-tenant** basada en schemas. Cada organizacion opera en su propio schema aislado, compartiendo tablas globales del schema `public`.

| Componente | Tecnologia |
|------------|------------|
| Motor | PostgreSQL 17.0+ |
| Extensiones | pgvector, pg_trgm, unaccent |
| Hosting | Docker (pgvector/pgvector:pg17) |
| Multi-tenant | Un schema por organizacion |
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
+-- {schema_municipio}/             # Ej: 100_test, 101_esco
|   +-- 35 tablas (Grupos A-J)
|   +-- ~52 indices
|   +-- 34 triggers updated_at + 1 trigger sync user_registry
|   +-- 1 funcion (fn_sync_user_registry)
|
+-- {schema_municipio}_audit/       # Ej: 100_test_audit
    +-- audit_log                   # Registro de auditoria
    +-- fn_log_change               # Funcion de auditoria
    +-- 7 triggers de auditoria
```

## Ambientes

| Ambiente | Host | Puerto | Uso |
|----------|------|--------|-----|
| Produccion | `postgres:5432` (Docker interno) | 5432 | Produccion |
| Desarrollo | `localhost:5432` | 5432 | Desarrollo y pruebas |

!!! warning "Ambiente de desarrollo"
    La base de datos de produccion no debe modificarse sin autorizacion. Para desarrollo usar una instancia local de PostgreSQL.

### Conexion

```bash
# Formato generico (NO incluye credenciales reales)
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

El schema de pruebas es `100_test`. Cada backend se conecta y setea `search_path` al schema del tenant en cada request.

## Extensiones

| Extension | Version | Proposito |
|-----------|---------|-----------|
| `vector` (pgvector) | 0.7.0+ | Embeddings y busqueda semantica (RAG) para GDI-AgenteLANG |
| `unaccent` | built-in | Busquedas sin acentos ("tramite" encuentra "tramite") |
| `pg_trgm` | built-in | Busqueda por similitud (trigram matching) |

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Estructura de Schemas

### Schema `public` (11 tablas)

Contiene datos globales compartidos por todas las organizaciones: roles del sistema, tipos de documento maestros, plantillas de expediente, registro de organizaciones activas, autenticacion API, certificados digitales y log de backup.

Ver: [Schema Public](schema-public.md)

### Schema por organizacion (35 tablas)

Cada organizacion tiene su propio schema con la estructura completa: estructura organizacional, usuarios, documentos, expedientes, configuracion, agente IA, notas, registros, responsables y favoritos de expediente.

Ver: [Schema Municipio](schema-municipio.md)

### Schema de auditoria (1 tabla)

Cada organizacion tiene un schema `{nombre}_audit` con una tabla `audit_log` y triggers automaticos sobre 7 tablas criticas.

Ver: [Schema Audit](schema-audit.md)

## Convenciones

| Elemento | Convencion | Ejemplo |
|----------|------------|---------|
| Tablas | `snake_case` | `document_draft`, `case_movements` |
| Primary keys | `UUID DEFAULT gen_random_uuid()` | `id UUID NOT NULL DEFAULT gen_random_uuid()` |
| Serial PKs | `SERIAL` o `BIGSERIAL` | `id SERIAL NOT NULL` (para tablas lookup) |
| Foreign keys | `{tabla}_id` o `{relacion}_id` | `document_type_id`, `created_by` |
| Timestamps | `TIMESTAMPTZ DEFAULT NOW()` | `created_at`, `updated_at` |
| Soft delete | `is_deleted BOOLEAN` o `is_active BOOLEAN` | `is_deleted NOT NULL DEFAULT false` |
| Busqueda | Indices B-tree, GIN, HNSW | Segun tipo de dato |

## Flujo de Deploy

=== "Produccion (organizacion nueva)"

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

El Backend usa `schema_name` como parametro **keyword-only** en todas las funciones de base de datos:

```python
# CORRECTO - keyword-only
result = execute_query("SELECT * FROM users", schema_name=schema_name)

# INCORRECTO - causa TypeError en runtime
result = execute_query("SELECT * FROM users", schema_name)
```

El `search_path` se configura por transaccion usando `SET LOCAL`:

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
    `schema_name` es siempre keyword-only (despues de `*` en la firma). Pasar `schema_name` como argumento posicional causa `TypeError` en runtime. Este patron previene SQL injection de tenant y hace explicito el schema en cada llamada.

## Indice de Secciones

| Seccion | Contenido |
|---------|-----------|
| [Schema Public](schema-public.md) | 11 tablas globales: roles, document types, municipalities, API keys, tenant_certificates, backup_access_log |
| [Schema Municipio](schema-municipio.md) | 35 tablas por tenant (Grupos A-J) con indices |
| [Schema Audit](schema-audit.md) | Auditoria automatica con triggers |
| [Scripts de Deploy](scripts-deploy.md) | 4 archivos SQL, flujo de ejecucion, herramientas Python |
| [Numeracion](numeracion.md) | Sistema de numeracion secuencial con advisory lock |
| [ENUMs y Tipos](enums-y-tipos.md) | 7 ENUMs y tipos custom |
| [Herramientas](herramientas.md) | psql, pgAdmin, scripts utiles |
| [Schema RLM](schema-rlm.md) | Tablas del Registro de Legajos Municipales (familias, registros, campos) |
