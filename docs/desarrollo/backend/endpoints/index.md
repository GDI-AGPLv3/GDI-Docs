# Endpoints

!!! tip "Endpoints públicos del Gateway"
    Los endpoints públicos del Gateway API (MCP + REST) están documentados en la sección [Gateway API](../../gateway/index.md). Esta página documenta los endpoints internos del Backend que consume el Frontend directamente.

Tabla resumen de todos los endpoints REST del backend. Organizados por dominio.

## Documentos

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/document-types` | Listar tipos de documentos | Sí |
| GET | `/document-states` | Listar estados visuales | Sí |
| POST | `/documents` | Crear documento (draft) | Sí |
| POST | `/documents/import` | Crear documento importado (PDF externo) | Sí |
| GET | `/documents/autocomplete` | Autocompletado de documentos oficiales | Sí |
| GET | `/api/v1/documents/search-official/{doc_number}` | Buscar documento oficial por número | Sí |
| GET | `/documents/{id}/details` | Detalles unificados del documento | Sí |
| GET | `/documents/{id}/editor` | Detalles para editor | Sí |
| GET | `/documents/{id}/signature-details` | Detalles de firma | Sí |
| PATCH | `/documents/{id}/save` | Guardar cambios (contenido, firmantes, etc.) | Sí |
| PUT | `/documents/{id}/replace-pdf` | Reemplazar PDF importado | Sí |
| POST | `/documents/{id}/preview-info` | Información para preview | Sí |
| POST | `/documents/{id}/preview-download` | Descargar PDF de preview | Sí |
| POST | `/documents/{id}/start-signing-process` | Iniciar proceso de firma | Sí |
| POST | `/documents/{id}/super-sign` | Firma unificada (común o numerador) | Sí |
| POST | `/documents/{id}/reject` | Rechazar documento | Sí |
| DELETE | `/documents/{id}` | Eliminar documento (soft delete) | Sí |
| GET | `/documents/{id}/official-url` | URL del PDF oficial | Sí |
| GET | `/documents/{id}/content` | Contenido HTML del documento | Sí |
| GET | `/documents/{id}/check-signer-permissions` | Verificar permisos de firma | Sí |

## Expedientes

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/cases/` | Listar expedientes con filtros y paginación | Sí |
| POST | `/api/v1/cases/` | Crear expediente (genera CAEX automática) | Sí |
| GET | `/api/v1/cases/templates` | Plantillas de expedientes disponibles | Sí |
| GET | `/api/v1/cases/{id}` | Detalle de expediente | Sí |
| GET | `/api/v1/cases/by-number/{num}` | Buscar expediente por número | Sí |
| POST | `/api/v1/cases/{id}/transfer` | Transferir expediente a otro sector | Sí |
| POST | `/api/v1/cases/{id}/assign` | Asignar tarea sin transferir propiedad | Sí |
| POST | `/api/v1/cases/{id}/close-assign` | Cerrar asignación | Sí |
| GET | `/api/v1/cases/{id}/available-sectors` | Sectores disponibles para transferencia | Sí |
| GET | `/api/v1/cases/sectors/{sector_id}/users` | Usuarios de un sector | Sí |
| POST | `/api/v1/cases/{id}/link-document` | Vincular documento oficial a expediente | Sí |
| GET | `/api/v1/cases/{id}/actions` | Acciones disponibles para el usuario | Sí |
| POST | `/api/v1/cases/{id}/subsanar` | Subsanar documento en expediente | Sí |
| GET | `/api/v1/cases/{id}/proposed-documents` | Documentos propuestos | Sí |

## Usuarios

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/users` | Listar usuarios activos | Sí |
| GET | `/users/{id}/profile` | Perfil de usuario | Sí |
| GET | `/users/search` | Buscar usuarios | Sí |
| GET | `/users/{id}/documents` | Documentos del usuario con filtros | Sí |

## Sectores

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/sectors/` | Listar sectores con departamentos | Sí |

## Notas

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/notes/received` | Notas recibidas | Sí |
| GET | `/notes/sent` | Notas enviadas | Sí |
| GET | `/notes/archived` | Notas archivadas | Sí |
| GET | `/notes/{id}` | Detalle de nota | Sí |
| POST | `/notes/{id}/archive` | Archivar nota | Sí |

## Memos

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/memos/received` | Memos recibidos | Sí |
| GET | `/memos/sent` | Memos enviados | Sí |
| GET | `/memos/archived` | Memos archivados | Sí |
| GET | `/memos/{id}` | Detalle de memo (registra apertura) | Sí |
| PATCH | `/memos/{id}/archive` | Archivar/desarchivar memo | Sí |
| GET | `/memos/unread-count` | Contador de no leídos | Sí |

Documentación completa: [Memos](memos.md)

## Dashboard

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/dashboard/feed` | Feed de actividad reciente | Sí |
| GET | `/api/v1/dashboard/stats` | Estadísticas del usuario | Sí |

## Legajos (RLM)

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/records/` | Listar legajos con filtros y paginación | Sí |
| POST | `/api/v1/records/` | Crear legajo | Sí |
| GET | `/api/v1/records/{id}` | Detalle de legajo | Sí |
| PATCH | `/api/v1/records/{id}` | Actualizar legajo | Sí |
| GET | `/api/v1/records/families` | Familias de registro disponibles | Sí |

Documentación completa: [Legajos (RLM)](legajos.md)

## Sistema

| Método | Path | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/auth/test` | Test de autenticación | Sí |

## Patrón de Endpoint

Todos los endpoints siguen el mismo patrón:

```python
@router.post("/documents/{document_id}/action")
async def action_endpoint(
    request: Request,
    document_id: str = Path(..., description="UUID del documento"),
    body: ActionRequest = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    schema_name: str = Depends(get_tenant_schema)
) -> ActionResponse:
    try:
        result = action_service(
            document_id,
            current_user.user_id,
            schema_name=schema_name
        )
        return ActionResponse(**result)
    except (ValidationError, DocumentNotFoundError) as e:
        raise exception_to_http_exception(e)
```
