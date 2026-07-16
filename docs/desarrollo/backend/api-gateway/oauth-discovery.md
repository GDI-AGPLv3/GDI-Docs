# OAuth Discovery

Endpoints de descubrimiento OAuth 2.0 que permiten a clientes MCP descubrir automaticamente como autenticarse.

**Ubicacion:** `api_gateway/http_server.py`

## RFCs Implementados

| RFC | Endpoint | Proposito |
|-----|----------|-----------|
| RFC 9728 | `/.well-known/oauth-protected-resource` | Descubrir authorization server |
| RFC 8414 | `/.well-known/oauth-authorization-server` | Metadata OAuth completa |
| MCP Spec | `/.well-known/mcp.json` | Manifest del servidor MCP |
| OpenAPI 3.0 | `/.well-known/openapi.json` | Spec REST API (ChatGPT Actions) |

---

## Flujo de Discovery

```
Cliente MCP (Claude Code, ChatGPT, Gemini)
    |
    1. POST /mcp (sin auth)
    |
    v
Server responde 401 + WWW-Authenticate:
    Bearer resource_metadata="/.well-known/oauth-protected-resource"
    |
    2. GET /.well-known/oauth-protected-resource
    |
    v
Server responde:
    {
        "resource": "https://mcp.tu-dominio.com",
        "authorization_servers": ["https://tu-tenant.us.auth0.com"],
        "scopes_supported": ["openid", "profile", "email", "offline_access"],
        "bearer_methods_supported": ["header"]
    }
    |
    3. GET /.well-known/oauth-authorization-server  (ChatGPT especifico)
    |
    v
Server hace proxy del openid-configuration de Auth0:
    {
        "issuer": "https://tu-tenant.us.auth0.com/",
        "authorization_endpoint": "https://tu-tenant.us.auth0.com/authorize",
        "token_endpoint": "https://tu-tenant.us.auth0.com/oauth/token",
        "registration_endpoint": "https://tu-tenant.us.auth0.com/oidc/register",
        ...
    }
    |
    4. Login en Auth0 (navegador)
    |
    5. POST /mcp con Authorization: Bearer <jwt>
    |
    v
Server valida JWT (audience con/sin barra + issuer), extrae el email
del claim https://gdilatam.com/email, construye MCPContext, procesa tool call
```

---

## Endpoints de Discovery

### `/.well-known/oauth-protected-resource` (RFC 9728)

Indica a clientes MCP **donde autenticarse**.

```json
{
    "resource": "https://mcp.tu-dominio.com",
    "authorization_servers": [
        "https://tu-tenant.us.auth0.com"
    ],
    "scopes_supported": [
        "openid",
        "profile",
        "email",
        "offline_access"
    ],
    "bearer_methods_supported": ["header"]
}
```

### `/.well-known/oauth-authorization-server` (RFC 8414)

Metadata completa del authorization server. **Proxy** del endpoint de Auth0:

```
GET /.well-known/oauth-authorization-server
    -> Proxy a https://tu-tenant.us.auth0.com/.well-known/openid-configuration
    -> Modifica registration_endpoint para DCR
```

!!! info "ChatGPT"
    ChatGPT requiere especificamente `/.well-known/oauth-authorization-server` (no el path de OpenID). Tambien acepta el alias `/.well-known/oauth-authorization-server/mcp`.

### `/.well-known/mcp.json`

Manifest del servidor MCP:

```json
{
    "name": "GDI-Latam MCP Server",
    "version": "1.0.0",
    "description": "Servidor MCP para gestion documental gubernamental",
    "tools": ["search_cases", "get_case", "search_documents", ...],
    "authentication": {
        "type": "oauth2",
        "discovery": "/.well-known/oauth-protected-resource"
    }
}
```

### `/.well-known/openapi.json`

Especificacion OpenAPI 3.0 para la REST API. Usado por ChatGPT Actions:

```json
{
    "openapi": "3.0.0",
    "info": {
        "title": "GDI-Latam REST API",
        "version": "1.0.0"
    },
    "paths": {
        "/api/v1/cases/search": { ... },
        "/api/v1/documents/search": { ... }
    }
}
```

---

## Requisitos Auth0 para MCP

Para que el flujo OAuth de MCP funcione, el tenant Auth0 necesita **cuatro** cosas. Si falta alguna, el cliente termina con un **access token opaco** (no-JWT) y el gateway responde 401 con "Issuer no valido".

### 1. API (resource server) creada

Un resource server cuyo `identifier` sea la URL publica del gateway (`MCP_RESOURCE_URI`), firmado con RS256. Ejemplo DEV: `https://gdi-gateway-dev.fly.dev`.

### 2. DCR habilitado

`Settings > Advanced > OIDC Dynamic Application Registration` (tenant flag `enable_dynamic_client_registration = true`). Los clientes MCP (Claude Code, claude.ai, etc.) se auto-registran por Dynamic Client Registration.

### 3. Conexion de BD a Domain Level

La Database Connection (`Username-Password-Authentication`) promovida a Domain Level (`is_domain_connection = true`). Es requisito de DCR.

### 4. Client-grant default para clientes third-party

Los clientes que crea DCR son **third-party** (prefijo `tpc_`). Por defecto NO pueden acceder a la API del gateway: Auth0 corta con `Client is not authorized to access resource server` y el cliente cae a un token opaco. Hay que crear un **client-grant default** para todos los third-party sobre la API:

```bash
POST /api/v2/client-grants
{
  "audience": "<MCP_RESOURCE_URI>",
  "default_for": "third_party_clients",
  "subject_type": "user",
  "allow_all_scopes": true
}
```

### La barra final (RFC 8707)

Los clientes MCP **canonicalizan** el `resource` (RFC 8707 / RFC 9728): a un host sin path le agregan `/`. Por eso piden el token para `https://<gateway>/` (CON barra final), aunque el discovery anuncie la URL sin barra.

Consecuencia: en Auth0 tiene que existir un resource server con **ese identifier exacto (con barra)** mas su client-grant third-party. Como los identifiers de Auth0 son inmutables, se registran las **dos** formas (con y sin `/`), cada una con su grant. El gateway acepta el audience con y sin barra (`_get_mcp_valid_audiences`).

### Audiences JWT soportados

El gateway solo acepta tokens emitidos contra su propia Custom API (`MCP_RESOURCE_URI`), con o sin barra final. **NO** acepta el audience del Management API (`https://<tenant>.auth0.com/api/v2/`).

```python
# _get_mcp_valid_audiences() en api_gateway/auth_mcp.py
VALID_AUDIENCES = [
    MCP_RESOURCE_URI,          # p.ej. https://gdi-gateway-dev.fly.dev
    MCP_RESOURCE_URI + "/",    # variante canonicalizada por el cliente
]
```

### Email del usuario: claim namespaced

El access token de un cliente third-party sale con scope `offline_access` unicamente (**sin `openid`**). Por eso **no trae el claim `email` estandar** y **no sirve para `/userinfo`** (devuelve 401). El email del usuario viaja en un claim **con namespace** que agrega un Action de Auth0:

- `https://gdilatam.com/email`
- `https://gdilatam.com/name`

El gateway lo lee con `_email_from_payload` (con fallback al claim `email` estandar).

---

## Respuesta 401 del MCP

Cuando un cliente envia un request sin token, el server responde:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.tu-dominio.com/.well-known/oauth-protected-resource"
Content-Type: application/json

{
    "error": "Authorization required",
    "hint": "Use OAuth 2.0 to authenticate"
}
```

El header `WWW-Authenticate` con `resource_metadata` es la clave para que clientes MCP descubran automaticamente el flujo OAuth.

---

## Troubleshooting

| Error | Causa | Solucion |
|-------|-------|----------|
| "Authorization required" | No hay token OAuth | Usar cliente MCP con OAuth |
| "Token invalido" | JWT expirado o mal formado | Re-autenticar via OAuth |
| "multi_tenant_selection_required" | Usuario con multiples organizaciones | Especificar `tenant_id` |
| "Audience no valido" | Token con audience incorrecto | Verificar audience en Auth0 |
| Cliente recibe token **opaco** (no-JWT) / "Issuer no valido" | Falta el client-grant `default_for: third_party_clients` en la API | Crear el client-grant third-party (ver Requisitos Auth0 #4) |
| `Client is not authorized to access resource server` | El resource pedido (con barra final) no existe en Auth0 o no tiene grant | Registrar el resource server con barra `https://<gateway>/` + su grant |
| `access_denied: Service not found: https://<gateway>/` | No hay API con el identifier con barra final | Crear el resource server con barra final |
| "Usuario no encontrado" | Email no existe en BD (o no se pudo leer el claim namespaced) | Verificar usuario en la organizacion y el Action que agrega `https://gdilatam.com/email` |
| Discovery no funciona | Endpoint no accesible | Verificar CORS y rutas en http_server.py |
