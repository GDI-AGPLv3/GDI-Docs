# Endpoints de Dashboard

Endpoints para estadísticas y feed de actividad. Prefijo: `/api/v1/dashboard`.

## Feed de Actividad

### `GET /api/v1/dashboard/feed`

Feed cronológico de actividad reciente relevante al usuario.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | int | Página |
| `page_size` | int | Resultados por página |

**Tipos de eventos en el feed:**

- Documentos creados, editados, enviados a firma
- Documentos firmados y oficializados
- Documentos rechazados
- Expedientes creados
- Expedientes transferidos
- Asignaciones de tarea

**Archivo:** `endpoints/dashboard/feed.py`

---

## Estadísticas

### `GET /api/v1/dashboard/stats`

Obtiene estadísticas del usuario y su sector.

**Response incluye:**

- Total de documentos por estado (draft, sent_to_sign, signed, rejected)
- Documentos pendientes de firma del usuario
- Expedientes activos del sector
- Actividad reciente (últimos 7 y 30 días)

**Archivo:** `endpoints/dashboard/stats.py`

---

## Schemas

Los schemas de dashboard están definidos en `schemas/dashboard_schemas.py`:

```python
class DashboardStatsResponse(BaseModel):
    documents_by_status: dict
    pending_signatures: int
    active_cases: int
    recent_activity: dict
```
