---
title: Cambios de la API
description: Cambios del Gateway (REST y MCP) que pueden afectar a integraciones existentes.
---

# Cambios de la API

Cambios del Gateway (REST `/api/v1` y MCP) que pueden afectar a una integracion que ya
funciona. Lo mas nuevo arriba.

---

## 06/10/2026 — `sector_filter` invalido ahora responde 400

**Afecta a:** `GET /api/v1/cases/search` (REST) y la tool MCP `search_cases`.
**Version del Backend/Gateway:** 5.3.0.

### Que cambio

`sector_filter` filtra la busqueda de expedientes por **un** sector. Acepta:

- el acronimo exacto de un sector activo (ej. `HAC`, `LEGAL`);
- el formato `DEPT#SECTOR` (ej. `HAC#PRIV`);
- el UUID del sector.

| Situacion | Antes | Ahora |
|---|---|---|
| El valor resuelve a un sector | 200, lista filtrada | 200, lista filtrada (sin cambios) |
| El acronimo o `DEPT#SECTOR` no existe (o el sector esta inactivo) | 200 con la lista **sin filtrar** | **400** |
| El valor trae comas (varios sectores) | 200 con la lista **sin filtrar** | **400** |
| No se manda el parametro | 200, lista completa | 200, lista completa (sin cambios) |

### Por que

Con un valor que no resolvia, la API devolvia **todos** los expedientes con 200 y la integracion
creia que habia filtrado. Un error de tipeo, o un asistente de IA que inventaba un acronimo,
terminaba mostrando datos que no correspondian al filtro pedido, sin ningun aviso.

### Ejemplo de respuesta

```http
GET /api/v1/cases/search?sector_filter=XYZ
```

```json
{
  "detail": {
    "message": "sector_filter: 'XYZ' no se pudo resolver a un sector (ni como UUID, ni como DEPT#SECTOR, ni como acrónimo de sector activo).",
    "type": "ValidationError"
  }
}
```

Con comas el mensaje indica que `sector_filter` espera un sector unico.

### Que tiene que hacer una integracion

- Mandar solo acronimos que existan en el municipio: se pueden consultar con
  `GET /api/v1/system/sectors`.
- Si el sector no se conoce con certeza, **omitir** el parametro en vez de adivinarlo.
- Tratar el 400 como "filtro invalido", no reintentar con el mismo valor.
