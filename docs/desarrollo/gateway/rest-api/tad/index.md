# API TAD Ciudadano

La API TAD (Tramites A Distancia) permite que el **portal ciudadano del municipio** (u otro software externo) opere sobre GDI **a nombre de un ciudadano**: crear y firmar documentos, iniciar expedientes y seguir su avance. El ciudadano NO es un usuario de GDI: vive en una base propia (`citizens`) y firma con **firma electronica** en el mismo acto de creacion del documento.

**11 endpoints** bajo el prefijo `/api/v1/tad/*`, pensados para consumo **server-to-server** desde el backend del portal municipal (la API Key nunca debe viajar a un navegador).

```
Portal municipal (backend)  --X-API-Key-->  Gateway GDI  -->  GDI
                            <--webhook documents.notified--
```

## Autenticacion

Todos los endpoints requieren el header `X-API-Key` con una **API Key de tipo TAD** (`key_type='tad'`), creada desde BackOffice (`/api-key`). Es una key a nivel municipio: no tiene usuarios autorizados asociados.

Los endpoints que operan **a nombre de un ciudadano** requieren ademas el header `X-Citizen-ID`, que acepta el **UUID** del ciudadano o su **ID nacional (CUIL)**:

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

| Endpoint | `X-Citizen-ID` |
|----------|----------------|
| `POST /tad/citizens`, `GET /tad/citizens/{id}`, `PATCH /tad/citizens/{id}` | No (gestion de la base de ciudadanos) |
| `GET /tad/document-types`, `GET /tad/document-types/{id}/fields`, `GET /tad/case-templates` | No (catalogos) |
| `POST /tad/documents`, `POST /tad/cases`, `GET /tad/cases`, `GET /tad/cases/{id}`, `POST /tad/cases/{id}/propose` | **Si** |

!!! warning "Server-to-server"
    La API Key identifica al municipio completo. Nunca exponerla en frontend ni en apps moviles: todas las llamadas deben salir del backend del portal.

## Estados del ciudadano

| Estado | Puede leer sus expedientes | Puede crear/firmar |
|--------|---------------------------|--------------------|
| `pendiente` | Si | No (403) |
| `validado` | Si | Si |
| `bloqueado` | No (403 en todo) | No (403) |

La validacion de identidad del ciudadano es **responsabilidad del portal** (el municipio decide como valida: presencial, con el registro civil, etc.). GDI solo registra el estado.

## Codigos de error

La API usa un criterio **anti-enumeracion**: los 404 son genericos y no distinguen "no existe" de "existe pero no es tuyo". Un portal no puede usar la API para descubrir CUILs, expedientes o documentos ajenos.

| Codigo | Cuando |
|--------|--------|
| `400` | Validacion de negocio: campo faltante o invalido, tipo no habilitado, contenido mal formado. El mensaje en `{"error": "..."}` siempre explica el motivo. |
| `401` | API Key faltante, invalida, expirada o de otro tipo (una key REST comun no sirve para `/tad/*`). |
| `403` | Ciudadano `bloqueado` (cualquier operacion) o no `validado` (operaciones de escritura). |
| `404` | Recurso inexistente **o no accesible para ese ciudadano** (mismo mensaje en ambos casos). |
| `409` | Conflicto de estado (ej. proponer un documento que no esta firmado). |
| `429` | Rate limit excedido. |
| `503` | Infraestructura del tenant incompleta (ej. migraciones pendientes). Reintentar mas tarde y avisar al municipio. |

## Rate limits

| Alcance | Limite |
|---------|--------|
| Toda la API TAD (por key) | 30 requests/min |
| `GET /tad/citizens/*` (adicional, anti-scraping) | 10 requests/min |

Superado el limite se responde `429`. El portal debe encolar y reintentar pasado el minuto.

## Errores por endpoint

Codigos que puede devolver cada endpoint, mas alla de los transversales (`401` sin/mala key, `429` rate limit, `500` inesperado). Todos los cuerpos de error tienen la forma `{"error": "mensaje"}`.

| Endpoint | Codigos especificos |
|----------|---------------------|
| `POST /tad/citizens` | `400` (`full_name`/`country_id` faltante, estado invalido) |
| `GET /tad/citizens/{ref}` | `404` (no existe) |
| `PATCH /tad/citizens/{ref}` | `400` (campo distinto de `estado`, estado invalido) · `404` (no existe) |
| `GET /tad/document-types` · `GET /tad/case-templates` | — (solo transversales) |
| `GET /tad/document-types/{id}/fields` | `404` (tipo inexistente, no habilitado, o sin formulario) |
| `POST /tad/documents` | `400` (tipo no habilitado, campo de contenido incorrecto, PDF/base64 invalido, `form_data` invalido) · `403` (ciudadano no validado o bloqueado) · `503` (migraciones pendientes) |
| `POST /tad/cases` | `400` (`case_template_id` inexistente o canal no-API) · `403` (ciudadano no validado o bloqueado) |
| `GET /tad/cases` | `403` (ciudadano bloqueado) |
| `GET /tad/cases/{id}` | `404` (inexistente o no compartido) |
| `POST /tad/cases/{id}/propose` | `404` (expediente/documento inexistente, no compartido o ajeno) · `409` (documento no firmado, o propuesta ya pendiente) |
| `POST /tad/webhook/test` | `422` (sin webhook configurado en la key TAD) |

## Contenido de la seccion

- [Ciudadanos](ciudadanos.md) — alta, consulta y cambio de estado de la base de ciudadanos.
- [Documentos](documentos.md) — catalogo de tipos y creacion + firma en un paso (HTML, formulario controlado FFCC e Importado PDF), con adjuntos embebidos.
- [Expedientes](expedientes.md) — creacion de expedientes, consulta de los compartidos y propuesta de vinculacion de documentos.
- [Webhook de notificaciones](webhook.md) — evento `documents.notified` con firma HMAC.
