# Troubleshooting

Problemas comunes y soluciones al desarrollar con el ecosistema GDI Latam.

## TypeError: takes N positional arguments but M were given

**Causa**: El parametro `schema_name` se paso como argumento posicional en lugar de keyword argument.

**Contexto**: Todas las funciones de base de datos usan `schema_name` como parametro **keyword-only** (despues de `*` en la firma). Este es el error mas comun en el proyecto.

**Ejemplo del error**:

```python
# INCORRECTO - causa TypeError
result = execute_query("SELECT * FROM users", (user_id,), schema_name)

# CORRECTO - siempre usar schema_name=
result = execute_query("SELECT * FROM users", (user_id,), schema_name=schema_name)
```

**Solucion**: Buscar todas las llamadas a funciones de BD y asegurar que `schema_name` se pasa con `=`:

```python
# Funciones principales que requieren keyword-only
execute_query(query, params, *, schema_name=schema_name)
execute_update(query, params, *, schema_name=schema_name)
execute_transaction(*, schema_name=schema_name)
execute_single_update(query, params, *, schema_name=schema_name)
check_user_exists(user_id, *, schema_name=schema_name)
get_authenticated_user(user_id, *, schema_name=schema_name)
```

Ver [Regla keyword-only](../arquitectura/multi-tenant.md#regla-keyword-only-schema_name) para mas detalles.

---

## Error de CORS

**Sintomas**: El navegador muestra `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:3003' has been blocked by CORS policy`.

**Causa**: El origen del frontend no esta en la lista de origenes permitidos del Backend.

**Solucion**:

### Desarrollo local

El Backend ya permite puertos 3000-3050 y 8000-8050 en localhost por defecto. Si usas un puerto fuera de ese rango, el CORS fallara.

```python
# main.py - origenes permitidos automaticamente
allowed_origins = (
    [f"http://localhost:{port}" for port in range(3000, 3051)] +
    [f"http://127.0.0.1:{port}" for port in range(3000, 3051)] +
    [f"http://localhost:{port}" for port in range(8000, 8051)] +
    [f"http://127.0.0.1:{port}" for port in range(8000, 8051)]
)
```

### Produccion (Docker)

Configurar la variable de entorno `FRONTEND_URL` con la URL del frontend:

```bash
# En el archivo .env del Backend o en docker-compose.yml
FRONTEND_URL=https://tu-frontend.tu-dominio.com

# Reiniciar el servicio
docker compose restart backend
```

Ver [Middleware](../backend/middleware.md) para la configuracion completa de CORS.

---

## JWT Expired / Invalid Token

**Sintomas**: Error 401 `{"detail": "Token expired"}` o `{"detail": "Invalid token"}`.

**Causas posibles**:

1. **Token expirado**: Los tokens JWT de Auth0 tienen un tiempo de vida limitado
2. **Audience incorrecto**: El token fue emitido para un audience diferente
3. **Domain incorrecto**: `AUTH0_DOMAIN` no coincide con el emisor del token

**Solucion**:

### En desarrollo (evitar Auth0)

Activar `TESTING_MODE` para no requerir JWT:

```bash
# .env del Backend
TESTING_MODE=true
```

Y usar el header `X-User-ID` en lugar de JWT:

```bash
curl -H "X-User-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
     http://localhost:8000/users
```

### En produccion

```bash
# Verificar variables Auth0 en Docker
docker compose exec backend env | grep AUTH0

# Deben coincidir:
# AUTH0_DOMAIN=tu-tenant.us.auth0.com
# AUTH0_AUDIENCE=https://api.tu-dominio.com
```

Si el token expira rapidamente, verificar la configuracion de token lifetime en Auth0 Dashboard > APIs > Settings.

Ver [Autenticacion](../backend/auth.md) para el flujo completo de Auth0.

---

## Cloudflare R2 Access Denied

**Sintomas**: Error 403 `Access Denied` o 404 `NoSuchBucket` al subir o descargar PDFs.

**Causas posibles**:

1. Credenciales R2 incorrectas
2. Bucket no existe
3. El nombre del bucket no coincide con `settings` de la organizacion

**Diagnostico**:

```sql
-- Verificar buckets configurados para el municipio
SELECT bucket_oficial, bucket_tosign FROM "200_muni".settings;
```

**Solucion**:

```bash
# Verificar variables R2 en el Backend
# Desarrollo local:
cat .env | grep CF_R2

# Docker:
docker compose exec backend env | grep CF_R2

# Variables necesarias:
# CF_R2_ENDPOINT=https://ACCOUNT_ID.r2.cloudflarestorage.com
# CF_R2_ACCESS_KEY_ID=...
# CF_R2_SECRET_ACCESS_KEY=...
```

Si el bucket no existe, crearlo en Cloudflare Dashboard. Los nombres de bucket estan en la tabla `settings` del schema.

Ver [Cloudflare R2](../deploy/cloudflare-r2.md) y [Storage Service](../backend/services/storage-service.md).

---

## Advisory Lock Timeout

**Sintomas**: El proceso de firma se cuelga o tarda mucho. Posible deadlock en la numeracion de documentos.

**Causa**: El advisory lock `888888` esta bloqueado por otra transaccion que no libero el lock.

**Diagnostico**:

```sql
-- Ver locks activos
SELECT pid, mode, granted
FROM pg_locks
WHERE locktype = 'advisory' AND classid = 888888;

-- Ver queries activas que podrian tener el lock
SELECT pid, state, query, age(clock_timestamp(), query_start)
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

**Solucion**:

```sql
-- Opcion 1: Esperar a que la transaccion termine (recomendado)
-- Verificar la query que tiene el lock y esperar

-- Opcion 2: Cancelar la query bloqueante (si esta colgada)
SELECT pg_cancel_backend(PID_DE_LA_QUERY);

-- Opcion 3: Terminar el backend bloqueante (ultimo recurso)
SELECT pg_terminate_backend(PID_DE_LA_QUERY);
```

!!! danger "No eliminar el advisory lock"
    El advisory lock `888888` previene numeros oficiales duplicados. Nunca deshabilitar la logica de locking en `shared/numbering.py`.

Ver [Numeracion](../database/numeracion.md) para entender el sistema de numeracion secuencial.

---

## Schema Not Found

**Sintomas**: Error `Schema "nombre_schema" does not exist` o `relation "tabla" does not exist`.

**Causas posibles**:

1. El schema no fue creado en la BD
2. El `search_path` no se configuro correctamente
3. El nombre del schema tiene caracteres especiales sin comillas

**Diagnostico**:

```sql
-- Listar schemas existentes
SELECT schema_name FROM information_schema.schemata
WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema';

-- Verificar que el municipio esta registrado
SELECT * FROM public.municipalities;

-- Verificar tabla especifica
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = '200_muni';
-- Debe retornar 33
```

**Solucion**:

Si el schema no existe, ejecutar el script de creacion:

```bash
cd GDI-BD
python tools/create_municipio.py
# O ejecutar 03-create-municipio.sql manualmente
```

Si el schema existe pero las queries fallan, verificar que el `search_path` se esta configurando:

```python
# El Backend hace esto automaticamente en cada request
# shared/database.py
cursor.execute(f'SET LOCAL search_path TO "{schema_name}", public')
```

!!! info "Comillas dobles"
    Los schemas que empiezan con numero (ej: `200_muni`) requieren comillas dobles en SQL: `"200_muni".users`. El Backend maneja esto automaticamente.

Ver [Multi-Tenant](../arquitectura/multi-tenant.md) y [Database](../backend/database.md).

---

## Docker Deploy Failed

**Sintomas**: El deploy falla durante build o startup del contenedor.

### Build failed

**Diagnostico**:

```bash
docker compose build --no-cache <servicio>
```

**Causas comunes**:

| Error | Causa | Solucion |
|-------|-------|----------|
| `ModuleNotFoundError` | Dependencia no esta en requirements.txt | `pip freeze > requirements.txt` |
| `Python version` | Version incompatible | Verificar Dockerfile |
| `Node version` | Version incompatible | Verificar `package.json` engines |
| `Dockerfile error` | Dockerfile invalido | Verificar sintaxis |

### Startup crash

**Diagnostico**:

```bash
docker compose logs --tail 100 <servicio>
```

**Causas comunes**:

| Error | Causa | Solucion |
|-------|-------|----------|
| `PORT already in use` | Puerto hardcodeado | Usar `os.getenv("PORT")` |
| `DATABASE_URL invalid` | Variable mal configurada | `docker compose exec <servicio> env` para verificar |
| `Out of Memory` | Servicio consume mucha RAM | Aumentar limite en docker-compose.yml |
| `Import error` | Dependencia faltante | Verificar requirements.txt |

**Solucion general**:

```bash
# Ver variables de entorno
docker compose exec <servicio> env

# Forzar rebuild y redeploy
docker compose up -d --build <servicio>

# Rollback: reconstruir con version anterior
git checkout <commit-anterior>
docker compose up -d --build <servicio>
```

---

## Frontend: Error "Failed to fetch" al llamar al Backend

**Sintomas**: El frontend muestra error de red al intentar comunicarse con el Backend.

**Causas posibles**:

1. Backend no esta corriendo
2. `NEXT_PUBLIC_API_URL` apunta a URL incorrecta
3. Error de CORS (ver seccion dedicada)
4. Certificado SSL invalido (produccion)

**Solucion**:

```bash
# Verificar que el Backend responde
curl http://localhost:8000/health

# Verificar variable en frontend
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# En produccion, verificar que la URL sea la publica
NEXT_PUBLIC_API_URL=https://tu-backend.tu-dominio.com
```

!!! tip "Prefijo NEXT_PUBLIC_"
    Las variables de entorno en Next.js que empiezan con `NEXT_PUBLIC_` son accesibles desde el navegador. Las demas solo desde el servidor. `NEXT_PUBLIC_API_URL` debe ser la URL **publica** del Backend, no la interna de Docker.

---

## Errores de Firma Digital

### Error FULLPAGE

**Sintomas**: Error 400 de Notary con mensaje "FULLPAGE" al firmar un documento.

**Causa**: No hay espacio suficiente en la ultima pagina del PDF para la firma visual.

**Solucion**: El Backend maneja esto automaticamente: detecta el error, agrega una pagina en blanco y reintenta la firma. Si persiste:

```bash
# Verificar logs del Backend
docker compose logs backend | grep FULLPAGE

# Verificar que Notary responde
curl http://localhost:8001/health
```

### Posicion de firma incorrecta

**Causa**: El layout de firmas calcula posiciones automaticamente en 2 columnas. Si hay muchos firmantes, puede haber solapamiento.

**Referencia**: Ver [Layout de Firmas](../notary/layout-firmas.md) y [Firma Visual](../notary/firma-visual.md).

---

## Resumen Rapido

| Problema | Primera accion |
|----------|---------------|
| TypeError schema_name | Agregar `=` en la llamada: `schema_name=schema_name` |
| CORS | Verificar puerto o `FRONTEND_URL` |
| JWT invalid | Activar `TESTING_MODE=true` en desarrollo |
| R2 denied | Verificar variables `CF_R2_*` y buckets en settings |
| Lock timeout | `SELECT pid FROM pg_locks WHERE classid = 888888` |
| Schema not found | Verificar `information_schema.schemata` |
| Deploy failed | `docker compose build --no-cache` o `docker compose logs` |
| Frontend fetch error | Verificar `NEXT_PUBLIC_API_URL` y health del Backend |
| Firma FULLPAGE | Se resuelve automaticamente (agrega pagina en blanco) |
