# Ciudadanos

Gestion de la **base de ciudadanos** del municipio. Estos endpoints usan solo `X-API-Key` (no llevan `X-Citizen-ID`).

---

## Alta / upsert de ciudadano

```
POST /api/v1/tad/citizens
```

Crea un ciudadano o actualiza su estado si ya existe (upsert por `country_id`).

**Body:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `full_name` | string | Si | Nombre completo |
| `country_id` | string | Si | ID nacional (CUIL en Argentina). Es la clave de upsert. |
| `estado` | string | No | `pendiente` (default), `validado` o `bloqueado` |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/citizens" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Maria Portal", "country_id": "27333444556"}'
```

**Respuesta `200 OK`:**

```json
{
  "id": "2c6d5586-9cc7-46ad-809d-e9aa437002cc",
  "full_name": "Maria Portal",
  "country_id": "27333444556",
  "estado": "pendiente",
  "created_via": "api",
  "validated_at": null,
  "validated_by": null,
  "created_at": "2026-07-24T18:02:33Z",
  "updated_at": "2026-07-24T18:02:33Z"
}
```

!!! note "El formato de `country_id` no se valida"
    GDI acepta cualquier string como `country_id` (la API es multi-pais). El portal es responsable de validar el formato del documento antes de dar de alta.

---

## Consultar ciudadano

```
GET /api/v1/tad/citizens/{id_o_country_id}
```

Acepta el **UUID** del ciudadano o su **`country_id`** (CUIL). Devuelve el mismo objeto del alta. `404` generico si no existe.

```bash
curl "https://gateway.your-domain.com/api/v1/tad/citizens/27333444556" \
  -H "X-API-Key: tu-api-key-tad"
```

!!! warning "Rate limit estricto"
    Este endpoint tiene un limite adicional de **10 requests/min** por ser el mas expuesto a enumeracion de CUILs.

---

## Cambiar estado

```
PATCH /api/v1/tad/citizens/{id_o_country_id}
```

Acepta el **UUID** del ciudadano o su **`country_id`** (CUIL), igual que el GET. **Solo permite cambiar `estado`**: cualquier otro campo en el body devuelve `400` (nombre e ID nacional son inmutables por API).

**Body:**

```json
{"estado": "validado"}
```

**Errores:**

| Codigo | Motivo |
|--------|--------|
| `400` | Body con campos distintos de `estado`, o estado invalido |
| `404` | Ciudadano inexistente |

**Ciclo tipico del portal:**

1. `POST /tad/citizens` al registrarse el vecino → queda `pendiente` (ya puede **ver** expedientes que le compartan).
2. El municipio valida la identidad → `PATCH {"estado": "validado"}` → ya puede **crear y firmar**.
3. Ante un problema → `PATCH {"estado": "bloqueado"}` → toda la API responde `403` para ese ciudadano.
