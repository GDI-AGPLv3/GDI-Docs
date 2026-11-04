# MCP Server

!!! info "Documentación completa en la sección Gateway"
    La documentación autoritativa del MCP Server vive en [desarrollo/gateway/mcp-server.md](../../gateway/mcp-server.md).
    Esta página es un resumen de arquitectura interna; para la lista de tools, flujos y configuración de clientes, ver esa sección.

El MCP Server expone **42 tools** (lectura y escritura) a agentes IA. Se implementa como Streamable HTTP (JSON-RPC) sobre el endpoint `POST /mcp`.

**Ubicación del código:** `api_gateway/http_server.py` (handler `handle_list_tools`) y `api_gateway/tools/` (implementación de cada tool).

## Implementación Interna

### Definición de Tools (`http_server.py`)

Las tools se definen en `handle_list_tools` y se despachan en `handle_call_tool`. Cada tool recibe un `MCPContext` con el usuario y schema del tenant:

```python
# Definicion (handle_list_tools)
Tool(
    name="search_cases",
    description="Busca expedientes por texto...",
    inputSchema={
        "type": "object",
        "properties": {
            "search": {"type": "string"},
            "page": {"type": "integer", "default": 1},
            "page_size": {"type": "integer", "default": 20},
        }
    }
)

# Ejecucion (handle_call_tool)
if name == "search_cases":
    result = await cases.search_cases(ctx, **arguments)
    return [TextContent(type="text", text=json.dumps(result))]
```

### Contexto Multi-Tenant (`auth_mcp.py`)

El contexto se inyecta automáticamente desde el JWT:

```python
async def validate_mcp_auth(token: str) -> MCPContext:
    # 1. Validar JWT con Auth0 JWKS (audience con/sin barra final)
    # 2. Extraer email del claim namespaced https://gdilatam.com/email
    #    (clientes third-party no traen claim "email" ni sirven para /userinfo)
    # 3. Buscar usuario en BD por email
    # 4. Construir MCPContext con user_id, schema_name, etc.
    return MCPContext(
        user_id=...,
        schema_name=...,
        user_full_name=...,
        user_email=...,
    )
```

### Tools Layer (`tools/`)

Los tools son funciones async que reciben `MCPContext` y parámetros tipados:

```python
# tools/cases.py
async def search_cases(
    ctx: MCPContext,
    search: str = "",
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    date_filter: str = None,
    sector_filter: str = None
) -> Dict[str, Any]:
    """Busca expedientes accesibles por el usuario."""
    # Usa ctx.schema_name para multi-tenant
    # Filtra por sectores del usuario automaticamente
```

## Autenticación MCP (`auth_mcp.py`)

Ver [OAuth Discovery](oauth-discovery.md) para el flujo completo.

Audience soportado: solo la Custom API del gateway (`MCP_RESOURCE_URI`), con y sin barra final. NO el Management API. Ver [OAuth Discovery > Requisitos Auth0 para MCP](oauth-discovery.md#requisitos-auth0-para-mcp).

```python
VALID_AUDIENCES = [
    MCP_RESOURCE_URI,          # p.ej. https://<your-gateway-app>.fly.dev
    MCP_RESOURCE_URI + "/",    # variante canonicalizada por el cliente (RFC 8707)
]
```

### Multi-Tenant Selection

Si un usuario tiene acceso a múltiples organizaciones, el server devuelve error `multi_tenant_selection_required`. El agente debe usar la tool `list_my_tenants` para listar las opciones y luego incluir `tenant_id` en las llamadas.
