# Scripts de Deploy

El repositorio **GDI-BD** contiene los scripts SQL que crean la base, las migraciones posteriores
y herramientas Python para administrarla.

## Estructura del Repositorio

```
GDI-BD/
+-- Dockerfile.prd                # PostgreSQL 17 + pgvector + pgBackRest (imagen de produccion)
+-- sql/
|   +-- 00-tuning.sql             # Configuracion del cluster (ALTER SYSTEM)
|   +-- 01-install.sql            # Extensiones + ENUMs + tablas public + baseline de migraciones
|   +-- 02-seed-global.sql        # Datos globales: roles, doc types, case templates
|   +-- 02b-seed-agente.sql       # Tablas de GDI-AgenteLANG en public
|   +-- 03-create-municipio.sql   # Template para crear municipio (con placeholders)
|   +-- 04-seed-demo.sql          # Crear 100_test + datos demo (autonomo)
|   +-- migrations/               # Migraciones posteriores al corte 122 (123 en adelante)
|       +-- archive/              # 000-122: ya plegadas al template, no se aplican mas
|
+-- tools/                        # Scripts Python
|   +-- create_municipio.py       # Crear municipio nuevo (interactivo)
|   +-- install.py                # Instalacion limpia de 100_test
|   +-- run_migrations.py         # Aplica todas las migraciones pendientes, en orden
|   +-- check_migrations.py       # Compara archivos contra public.schema_migrations
|   +-- migrate.py                # Aplica una migracion
|   +-- run_single_script.py      # Ejecutar script SQL individual
|   +-- verify_db.py              # Verificar integridad de BD
|
+-- .env.example                  # Template de credenciales
+-- README.md
```

## Flujos de Deploy

=== "Produccion (organizacion nueva)"

    Se ejecutan 3 scripts en orden. Los dos primeros solo se ejecutan una vez al crear la BD.

    ```
    01-install.sql           -- Extensiones + ENUMs + 9 tablas public
         |
         v
    02-seed-global.sql       -- 3 roles + 61 doc types + 30 case templates + 6 display states + 3 registry families
         |
         v
    03-create-municipio.sql  -- Schema del municipio + audit + datos iniciales
    ```

    El script `03` requiere reemplazo de 9 placeholders antes de ejecutar.

=== "Dev/Test (100_test)"

    Se ejecutan 3 scripts. El tercero (`04-seed-demo.sql`) es autonomo y contiene toda la estructura y datos hardcoded.

    ```
    01-install.sql           -- Extensiones + ENUMs + 9 tablas public
         |
         v
    02-seed-global.sql       -- Datos globales
         |
         v
    04-seed-demo.sql         -- 100_test completo (schemas + datos demo)
    ```

---

## Scripts SQL

### 01-install.sql

Crea la infraestructura base en el schema `public`. Solo se ejecuta una vez por BD.

**Contenido:**

- 3 extensiones: `vector`, `unaccent`, `pg_trgm`
- 7 tipos enumerados (ver [ENUMs y Tipos](enums-y-tipos.md))
- 9 tablas globales (ver [Schema Public](schema-public.md))
- la zona horaria de la base (`America/Argentina/Buenos_Aires`)
- `jit = off` a nivel base
- el baseline de `public.schema_migrations` (migraciones `000`-`122`, ver [Migraciones](#migraciones))

**Nombre de la base.** Los ajustes de base (`ALTER DATABASE`) usan `current_database()`. Así el
script anda con cualquier nombre de base (el `DB_NAME` de la instalación). Antes el nombre iba
fijo y una base con otro nombre quedaba a medio crear.

```sql
DO $$
BEGIN
    EXECUTE format('ALTER DATABASE %I SET timezone = %L',
                   current_database(), 'America/Argentina/Buenos_Aires');
END
$$;
```

**JIT apagado.** El `01` corre el mismo bloque que la migración `113` (`jit_off_a_nivel_base`).
La `113` figura en el baseline como aplicada, pero es un ajuste de la base, no del esquema: sin
este bloque, una instalación de cero quedaba con JIT prendido. El Backend apaga JIT en cada
conexión, pero detrás de PgBouncer en modo `transaction` ese `SET` se pierde.

```sql
DO $$
BEGIN
    EXECUTE format('ALTER DATABASE %I SET jit = off', current_database());
END $$;
```

Los dos ajustes rigen para las conexiones **nuevas**.

```sql
-- Extensiones
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ENUMs
CREATE TYPE "public"."country_enum" AS ENUM ('AR', 'BR', 'UY', ...);
CREATE TYPE "public"."document_status" AS ENUM ('draft', 'sent_to_sign', ...);
-- ... (7 ENUMs en total)

-- Tablas
CREATE TABLE "public"."roles" (...);
CREATE TABLE "public"."global_document_types" (...);
-- ... (9 tablas en total)
```

### 02-seed-global.sql

Inserta datos iniciales en las tablas globales.

| Tabla | Cantidad | Descripcion |
|-------|----------|-------------|
| `roles` | 3 | Usuario General, Funcionario, Administrador |
| `global_document_types` | 61 | 58 publicos + PV + CAEX (internos) |
| `global_case_templates` | 30 | EEVAR, LICPUB, HABI, COMP, DEM, RRHH, etc. |
| `document_display_states` | 6 | DRAFT, PENDING_SIGN, SIGNED, REJECTED, CANCELLED, NUMBERED |
| `global_registry_families` | 3 | ARQ, LUM, ORD |

### 03-create-municipio.sql

Template para crear una organizacion nueva. Contiene **9 placeholders** que deben reemplazarse antes de ejecutar.

**Placeholders:**

| Placeholder | Ejemplo | Descripcion |
|-------------|---------|-------------|
| `{SCHEMA_NAME}` | `201_otra` | Nombre del schema |
| `{MUNICIPALITY_NAME}` | `Municipalidad del Futuro` | Nombre completo de la organizacion |
| `{ACRONYM}` | `BSAS` | Acronimo (2-4 letras) |
| `{COUNTRY}` | `AR` | Codigo de pais |
| `{SCHEMA_NUMBER}` | `101` | Numero auto-incremental |
| `{BUCKET_OFICIAL}` | `gdi-bsas-oficial` | Bucket R2 para docs oficiales |
| `{BUCKET_TOSIGN}` | `gdi-bsas-tosign` | Bucket R2 para docs a firmar |
| `{CITY}` | `Buenos Aires` | Ciudad (aparece en sellos) |
| `{PRIMARY_COLOR}` | `16158C` | Color hex sin # |

**Secciones del script:**

1. **Schema municipio** - 33 tablas (Grupos A-I) + ~47 indices + trigger sync
2. **Schema audit** - `audit_log` + `fn_log_change` + 6 triggers
3. **Datos iniciales** - settings + estado_users
4. **Registro del tenant** - INSERT en `public.municipalities` + departamento ROOT + 2 case_templates base (EEVAR, ECAPA)

!!! tip "Usar el script Python"
    En lugar de reemplazar placeholders manualmente, usar `python tools/create_municipio.py` que lo hace de forma interactiva.

### 04-seed-demo.sql

Script autonomo que crea el tenant `100_test` completo. No necesita `03-create-municipio.sql` porque contiene toda la estructura embebida.

**Secciones:**

| Seccion | Contenido |
|---------|-----------|
| 1 | Schema `100_test`: 33 tablas + indices + trigger sync |
| 2 | Schema `100_test_audit`: audit_log + fn_log_change + 6 triggers |
| 3 | Datos iniciales: settings + estado_users + organizacion en public |
| 4 | Datos demo: departamentos, sectores, ranks, usuarios, doc types, case templates, registry families |
| 5 | Drafts de bienvenida: 5 documentos borrador tipo IF |

**Datos demo incluidos:**

| Dato | Cantidad | Descripcion |
|------|----------|-------------|
| Departamentos | 10 | INTE, LEGAL, INNO, SAL, HAC, TESO, CONT, SEG, OOPU, OOPA |
| Sectores | 14 | 10 PRIV + 4 MESA/ADMIN |
| Ranks | 3 | Intendente (1), Secretario (2), Director (3) |
| City Seals | 4 | Innovador (generico), Intendente, Secretario, Director |
| Usuarios | 15 | Ficticios @munitest.com |
| User Seals | 15 | Uno por usuario |
| Document Types | 20 | IF, NOTA, PROV, ACT, RESOL, DICTA, PERMI, etc. |
| Case Templates | 6 | TEST, HABI, HIND, COMP, DEM, RRHH |
| Registry Families | 3 | ARQ, LUM, ORD (con permisos) |
| Drafts | 5 | Bienvenida a GDI (IF) |

---

## Herramientas Python

Todos los scripts Python usan la variable de entorno `DATABASE_URL` para conectarse:

```bash
# Configurar conexion
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:PORT/DATABASE'
```

O copiar `.env.example` a `.env` y editar:

```bash
# .env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

### install.py

Instalacion limpia del tenant `100_test`. Elimina y recrea todo.

```bash
cd GDI-BD/tools
python install.py
```

**Flujo:**

1. Pide confirmacion (elimina datos existentes)
2. DROP schemas `100_test` y `100_test_audit`
3. Ejecuta `01-install.sql`
4. Ejecuta `02-seed-global.sql`
5. Ejecuta `04-seed-demo.sql`
6. Ejecuta `verify_db.py` para verificar

### create_municipio.py

Crea una organizacion nueva de forma interactiva.

```bash
cd GDI-BD/tools
python create_municipio.py
```

**Flujo:**

1. Pide datos: nombre, acronimo, pais, ciudad, color, buckets
2. Auto-calcula `schema_number` (MAX + 1 de municipalities)
3. Auto-genera `schema_name` como `{number}_{acronym_lower}`
4. Muestra resumen y pide confirmacion
5. Reemplaza los 9 placeholders en `03-create-municipio.sql`
6. Ejecuta el SQL
7. Verifica la creacion (tablas, settings, departamento ROOT)
8. Muestra pasos manuales pendientes (buckets R2, Auth0, etc.)

### run_single_script.py

Ejecuta un archivo SQL individual. Util para migraciones o scripts ad-hoc.

```bash
cd GDI-BD/tools
python run_single_script.py 02-seed-global.sql
```

### verify_db.py

Verifica la integridad de la BD. Lista schemas, tablas y conteos.

```bash
cd GDI-BD/tools
python verify_db.py
```

**Verifica:**

- Schema `public`: tablas y datos (roles, document types, case templates, municipalities, display states)
- Schema `100_test`: tablas y datos (settings, estado_users, city_seals, document_types, case_templates)
- Schema `100_test_audit`: tabla audit_log y conteo

---

## Migraciones

Las migraciones se aplican **después** del baseline de `01-install.sql`. Viven en
`sql/migrations/`.

### Cómo se aplican

`tools/run_migrations.py` toma `sql/migrations/*.sql` (sin entrar a `archive/`), las ordena por
nombre y corre las que no figuran en `public.schema_migrations`. Si una falla, corta ahí y no
sigue con las siguientes.

```bash
DATABASE_URL='postgresql://USER:PASSWORD@HOST:PORT/DATABASE' python tools/run_migrations.py
```

`tools/check_migrations.py` compara los archivos contra esa tabla. Muestra las pendientes y las
que cambiaron después de aplicarse (compara el `checksum`).

### Corte 122

Las migraciones `000`-`122` se archivaron en `sql/migrations/archive/`: es el "corte 122". El
template ya crea el esquema completo hasta la `122` y `01-install.sql` registra esas versiones
como aplicadas. Una base nueva nace en la `122` y solo corre de la `123` en adelante.

!!! warning "Regla del template"
    Una migración que crea o cambia estructura se pliega a `01-install.sql` /
    `03-create-municipio.sql` **en el mismo commit**. Si no, al archivarla, una instalación
    nueva nace sin ese cambio.

### Huecos en la numeración

Los números faltantes no son un error ni un archivo perdido. El runner no exige números
consecutivos: aplica lo que hay, en orden de nombre.

| Número | Por qué falta |
|--------|---------------|
| `130` | Se escribió un índice y se revirtió (el planner no lo usaba). El número queda sin usar |
| `136` | Reservado por una rama en curso que todavía no llegó a la rama principal |

### Migraciones recientes

| Archivo | Qué hace |
|---------|----------|
| `137_audit_log_adelgazar.sql` | `fn_log_change` nueva con modo `full`/`diff` y columnas ruido, 9 triggers de auditoría con argumentos, `public.fn_set_updated_at_skip_noise()` en `users` y `official_documents`, índice `(table_name, event_time DESC)` en cada `audit_log`. Ver [Schema Audit](schema-audit.md) |
| `138_drop_idx_dss_session_duplicado.sql` | Borra `public.idx_dss_session`: duplicaba el índice único de `digital_signature_sessions.session_id`. Solo lo borra si la constraint única existe |
| `139_document_draft_certified_pdf_sha256.sql` | Agrega `document_draft.certified_pdf_sha256` con su `CHECK` en cada municipio. Ver [Schema Municipio](schema-municipio.md) |

Notas de operación de la `137`:

- Pide `lock_timeout = 2s`: recrear triggers bloquea tablas con mucho uso. Es mejor que falle y
  se reintente a que trabe la aplicación.
- Recorre todos los municipios. Si uno falla, deshace ese municipio, deja un `WARNING` con su
  nombre y sigue. Al final, si hubo alguno, aborta todo y la migración no se registra. Es
  idempotente: se arregla y se vuelve a correr.
- El `CREATE INDEX` (sin `CONCURRENTLY`) bloquea las escrituras al `audit_log` de ese municipio
  mientras se construye. Conviene aplicarla en horario tranquilo.

La `139` va **antes** que el Backend que la usa, en cada ambiente. Sola no cambia nada visible
(una columna en `NULL`). Un Backend nuevo sobre una base sin la `139` falla con
`column does not exist`.

### Reglas para una migración nueva

1. Usá el siguiente número libre. Revisá que ninguna rama abierta lo haya tomado.
2. Hacela idempotente **statement por statement** (`IF EXISTS`, `IF NOT EXISTS`, `ON CONFLICT`).
   El runner no envuelve cada archivo en una transacción.
3. Registrala en `public.schema_migrations`, como las existentes.
4. Si crea o cambia estructura, plegá el cambio a `01-install.sql` / `03-create-municipio.sql`
   en el mismo commit.
5. Si una aplicación la necesita (Backend, BackOffice-Back o AgenteLANG), subí su archivo
   `MIGRACION_MINIMA` a este número en el cambio de esa aplicación. Así el despliegue no instala
   la aplicación sobre una base que todavía no tiene la migración.

---

## pgBackRest en la imagen de produccion

`Dockerfile.prd` instala **pgBackRest** sobre `pgvector/pgvector:pg17`. Sirve para la copia
continua de la base (WAL minuto a minuto más una copia completa diaria).

Instalarlo no prende nada:

- pgBackRest corre recién cuando la base tiene `archive_mode=on`;
- eso lo prende el instalador OnPremise con `BACKUP_PITR=on`;
- las claves llegan como variables `PGBACKREST_*` del contenedor, nunca en un archivo.

Cómo se prende y se usa en una instalación: [Copia minuto a minuto](../../administradores/onpremise/copia-minuto-a-minuto.md).

La imagen no trae archivo de configuración (`/etc/pgbackrest.conf`). Las carpetas de log, lock y
cola (`/var/log/pgbackrest`, `/var/lib/pgbackrest`, `/var/spool/pgbackrest`) son del usuario
`postgres`.
