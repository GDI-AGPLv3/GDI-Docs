# Autenticacion

El backend usa **Auth0** con tokens **JWT RS256** para autenticacion. Definido en `auth.py`.

## Configuracion Auth0

| Variable | Valor Default |
|----------|--------------|
| `AUTH0_DOMAIN` | `tu-tenant.us.auth0.com` |
| `AUTH0_AUDIENCE` | Configurado en `.env` |
| `AUTH0_ALGORITHMS` | `["RS256"]` |

## Flujo de Autenticacion

### Modo Produccion

```
1. Frontend obtiene JWT de Auth0 (login)
2. Frontend envia request con header:
   Authorization: Bearer <jwt_token>
   X-Tenant-Schema: 200_muni
3. TenantMiddleware valida email del JWT contra el schema
4. auth.py valida JWT y obtiene AuthenticatedUser
5. Endpoint recibe current_user con permisos
```

### Modo Testing

Si `TESTING_MODE=true` en `.env`, el backend acepta autenticacion simplificada:

| Metodo | Header | Descripcion |
|--------|--------|-------------|
| API Key fija | `X-API-Key: <TESTING_API_KEY>` | Usa primer usuario activo |
| UUID directo | `X-User-ID: <uuid>` | UUID del usuario |
| Bearer UUID | `Authorization: Bearer <uuid>` | UUID en lugar de JWT |
| JWT normal | `Authorization: Bearer <jwt>` | Funciona igual que produccion |

!!! warning "Seguridad"
    `TESTING_MODE` se desactiva automaticamente si se detecta entorno de produccion.

## Funciones Principales

### get_current_user

Dependency principal de FastAPI. Se usa en todos los endpoints protegidos.

```python
# auth.py
def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> AuthenticatedUser:
```

**Retorna** un `AuthenticatedUser` con:

- `user_id`: UUID del usuario en la BD
- `auth_id`: ID de Auth0 (`sub` del JWT)
- `full_name`: Nombre completo
- `email`: Email
- `permissions`: Lista de `SectorPermission`

**Uso en endpoints:**

```python
@router.get("/documents")
async def list_documents(
    current_user: AuthenticatedUser = Depends(get_current_user),
    schema_name: str = Depends(get_tenant_schema)
):
    # current_user.user_id, current_user.permissions, etc.
    ...
```

### verify_token

Verifica y decodifica un JWT de Auth0.

```python
def verify_token(token: str) -> Dict[str, Any]:
```

Proceso:

1. Obtiene la clave RSA publica de Auth0 (JWKS) con cache de 30 minutos
2. Busca la clave correspondiente al `kid` del token
3. Decodifica y verifica el JWT con audience e issuer

**Errores:**

| HTTP | Detalle |
|------|---------|
| 401 | Token expirado |
| 401 | Claims incorrectos (audience/issuer) |
| 401 | Token invalido |
| 503 | No se pudo obtener claves de Auth0 |

### verify_auth0_token

Valida JWT sin requerir que el usuario exista en BD. Util para onboarding.

```python
def verify_auth0_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
```

### load_user_permissions

Carga permisos de sectores del usuario desde la BD.

```python
def load_user_permissions(user_id: str, *, schema_name: str) -> list:
```

Retorna lista de `SectorPermission` con informacion de cada sector donde el usuario tiene acceso.

### decode_jwt_from_request

Extrae y valida JWT del header Authorization. Usado internamente por el TenantMiddleware.

```python
def decode_jwt_from_request(request) -> Dict[str, Any]:
```

## Cache de JWKS

Las claves publicas de Auth0 se cachean por **30 minutos** para evitar consultas frecuentes:

```python
_jwks_cache = None
_jwks_cache_expiry = None  # datetime.now() + timedelta(minutes=30)
```

## Permisos de Sectores

El sistema de permisos se basa en sectores. Cada usuario puede tener acceso a multiples sectores con diferentes niveles:

| Permiso | Descripcion |
|---------|-------------|
| `can_view` | Ver documentos y expedientes del sector |
| `can_edit` | Crear y editar documentos en el sector |
| `is_primary` | Sector principal del usuario |

Los permisos se cargan desde la tabla `user_sector_permissions` al autenticar al usuario y se incluyen en el `AuthenticatedUser`.

## Dependencies de FastAPI

Definidas en `shared/dependencies.py`:

```python
def get_tenant_schema(request: Request) -> str:
    """Extrae schema_name del request.state (seteado por TenantMiddleware)."""
    return request.state.schema_name

def get_auth_source(request: Request) -> str:
    """Extrae auth_source del request.state."""
    return getattr(request.state, 'auth_source', 'unknown')
```

---

## Auth0 Database Connection

El BackOffice soporta **dual auth**: usuarios pueden autenticarse via proveedores sociales (Google, Microsoft) o via Database Connection (email + password). La gestion de Database Connection se implementa en `services/auth0_service.py` del BackOffice-Back.

### Tipos de Autenticacion

| Tipo | Connection | Uso tipico |
|------|-----------|------------|
| **Social** | `google-oauth2`, `windowslive` | Usuarios con cuenta Google/Microsoft institucional |
| **Database** | `Username-Password-Authentication` | Usuarios sin cuenta social (email + password manual) |

### Variables de Entorno

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `AUTH0_M2M_CLIENT_ID` | Client ID de la aplicacion M2M (Management API) | *requerida* |
| `AUTH0_M2M_CLIENT_SECRET` | Client Secret de la aplicacion M2M | *requerida* |
| `AUTH0_M2M_AUDIENCE` | Audience de la Management API | `https://{AUTH0_DOMAIN}/api/v2/` |
| `AUTH0_DB_CONNECTION` | Nombre de la Database Connection | `Username-Password-Authentication` |
| `AUTH0_FRONTEND_CLIENT_ID` | Client ID de la app frontend (para redirect en password tickets) | `AUTH0_CLIENT_ID` (fallback) |

### Token M2M (Management API)

Para interactuar con la Management API de Auth0, el servicio obtiene un token via **Client Credentials** grant. El token se cachea por **23 horas** (el token dura 24h, se renueva 1 hora antes de expirar).

```python
# Cache del token M2M
_token_cache = {"token": None, "expires_at": 0}

def _get_management_token() -> str:
    """Obtiene token via Client Credentials. Cachea 23h."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]
    # POST https://{AUTH0_DOMAIN}/oauth/token
    # grant_type: client_credentials
    # ...
```

### Funciones del Servicio

#### `check_user_exists_in_auth0(email)`

Busca si un email ya existe en Auth0 (cualquier connection).

```python
# GET https://{AUTH0_DOMAIN}/api/v2/users-by-email?email={email}
users = check_user_exists_in_auth0("juan@municipio.gob.ar")
# Retorna: lista de usuarios (puede ser vacia)
```

#### `check_email_has_social_account(email)`

Verifica si el email ya tiene una cuenta Social (Google/Microsoft). Retorna `True`/`False`.

Util para decidir si hay que crear una Database Connection o si el usuario ya puede hacer login social.

#### `create_database_user(email, full_name)`

Crea un usuario en Auth0 Database Connection con password aleatorio.

```python
result = create_database_user("juan@municipio.gob.ar", "Juan Perez")
# Retorna: {"user_id": "auth0|abc123", ...}
```

Detalles de implementacion:

- Password aleatorio: `secrets.token_urlsafe(32) + "!A1"` (cumple Good policy)
- `email_verified: True` (evita mail de verificacion)
- `verify_email: False`
- `app_metadata: {"gdi_invitation": True}` (marca como invitado)

#### `create_password_change_ticket(auth0_user_id, client_id)`

Genera un link de activacion (password change ticket) para que el usuario establezca su password.

```python
ticket_url = create_password_change_ticket("auth0|abc123", FRONTEND_CLIENT_ID)
# Retorna: "https://gdilatam.us.auth0.com/lo/reset?..."
```

Detalles:

- TTL: **5 dias** (432000 segundos)
- Usa `client_id` (no `result_url`) porque New Universal Login ignora `result_url`
- Auth0 usa el Application Login URI configurado en la app del `client_id` para el boton de redirect post-cambio

### Flujo Completo: Crear Usuario con Database Connection

```
1. Admin crea usuario en BackOffice
2. BackOffice-Back verifica si email tiene cuenta social:
   - SI tiene social → no crea Database user, el usuario ya puede loguearse
   - NO tiene social → sigue al paso 3
3. create_database_user(email, full_name)
   → Auth0 crea usuario con password aleatorio
4. create_password_change_ticket(auth0_user_id, FRONTEND_CLIENT_ID)
   → Auth0 genera link de activacion (5 dias TTL)
5. Se envia email al usuario con el link de activacion (via Resend)
6. Usuario abre el link → establece su password en Auth0
7. Usuario hace login con email + password → obtiene JWT
8. En primer login, el Backend completa auth_id en la tabla users (onboarding)
```

!!! info "Onboarding: auth_id"
    La columna `auth_id` en la tabla `users` se completa en el primer login del usuario. Hasta entonces, el usuario existe en la BD pero sin `auth_id`. La funcion `verify_auth0_token` permite validar el JWT sin requerir que el usuario exista previamente en la BD, facilitando este flujo de onboarding.
