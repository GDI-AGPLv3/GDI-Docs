# MCP Server

!!! info "Documentacion completa en la seccion Gateway"
    La documentacion autoritativa del MCP Server vive en [desarrollo/gateway/mcp-server.md](../../gateway/mcp-server.md).
    Esta pagina es un resumen de arquitectura interna; para la lista de tools, flujos y configuracion de clientes, ver esa seccion.

El MCP Server expone **42 tools** (lectura y escritura) a agentes IA. Se implementa como Streamable HTTP (JSON-RPC) sobre el endpoint `POST /mcp`.

**Ubicacion del codigo:** `api_gateway/http_server.py` (handler `handle_list_tools`) y `api_gateway/tools/` (implementacion de cada tool).

## Implementacion Interna

### Definicion de Tools (`http_server.py`)

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

El contexto se inyecta automaticamente desde el JWT:

```python
async def validate_mcp_auth(token: str) -> MCPContext:
    # 1. Validar JWT con Auth0 JWKS
    # 2. Extraer email (del token o de /userinfo)
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

Los tools son funciones async que reciben `MCPContext` y parametros tipados:

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

## Autenticacion MCP (`auth_mcp.py`)

Ver [OAuth Discovery](oauth-discovery.md) para el flujo completo.

JWT multi-audience soportado:

```python
VALID_AUDIENCES = [
    os.getenv('AUTH0_AUDIENCE'),
    os.getenv('MCP_RESOURCE_URI'),
]
```

### Multi-Tenant Selection

Si un usuario tiene acceso a multiples organizaciones, el server devuelve error `multi_tenant_selection_required`. El agente debe usar la tool `list_my_tenants` para listar las opciones y luego incluir `tenant_id` en las llamadas.
