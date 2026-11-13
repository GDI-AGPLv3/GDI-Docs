# API TAD Ciudadano

La API TAD (Trámites A Distancia) permite que el **portal ciudadano del municipio** (u otro software externo) opere sobre GDI **a nombre de un ciudadano**: crear y firmar documentos, iniciar expedientes y seguir su avance. El ciudadano NO es un usuario de GDI: vive en una base propia (`citizens`) y firma con **firma electrónica** en el mismo acto de creación del documento.

**13 endpoints** bajo el prefijo `/api/v1/tad/*`, pensados para consumo **server-to-server** desde el backend del portal municipal (la API Key nunca debe viajar a un navegador).

```
Portal municipal (backend)  --X-API-Key-->  Gateway GDI  -->  GDI
                            <──── webhooks ────
```

!!! info "Disponibilidad por ambiente"
    El flujo asincrónico (`202`), `GET /tad/documents/{id}`, la `Idempotency-Key` y el campo
    `event` en los webhooks están disponibles en **todos** los ambientes.

    **Webhooks sin links**: los avisos no traen `pdf_url` ni `documents[].url`.
    La URL se pide con el ID del documento.

!!! tip "¿Es tu primera integración?"
    Empeza por **[Conectar el portal de trámites](conectar-portal.md)**: que pedirle al
    administrador antes de escribir código, el flujo completo de un trámite, como se
    entera el portal del número oficial y el checklist de puesta en producción. Las demás
    páginas son el contrato campo por campo.

## Autenticación

Todos los endpoints requieren el header `X-API-Key` con una **API Key de tipo TAD** (`key_type='tad'`), creada desde BackOffice (`/api-key`). Es una key a nivel municipio: no tiene usuarios autorizados asociados.

Los endpoints que operan **a nombre de un ciudadano** requieren además el header `X-Citizen-ID`, que acepta el **UUID** del ciudadano o su **ID nacional (CUIL)**:

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

| Endpoint | `X-Citizen-ID` |
|----------|----------------|
| `POST /tad/citizens`, `GET /tad/citizens/{id}`, `PATCH /tad/citizens/{id}` | No (gestión de la base de ciudadanos) |
| `GET /tad/document-types`, `GET /tad/document-types/{id}/fields`, `GET /tad/case-templates` | No (catálogos) |
| `POST /tad/documents`, `GET /tad/documents/{id}`, `POST /tad/cases`, `GET /tad/cases`, `GET /tad/cases/{id}`, `GET /tad/cases/{id}/documents/{document_id}/url`, `POST /tad/cases/{id}/propose` | **Sí** |

!!! warning "Server-to-server"
    La API Key identifica al municipio completo. Nunca exponerla en frontend ni en apps moviles: todas las llamadas deben salir del backend del portal.

## Estados del ciudadano

| Estado | Puede leer sus expedientes | Puede crear/firmar |
|--------|---------------------------|--------------------|
| `pendiente` | Sí | No (403) |
| `validado` | Sí | Sí |
| `bloqueado` | No (403 en todo) | No (403) |

La validación de identidad del ciudadano es **responsabilidad del portal** (el municipio decide cómo valida: presencial, con el registro civil, etc.). GDI solo registra el estado.

## Códigos de error

La API usa un criterio **anti-enumeracion**: los 404 son genéricos y no distinguen "no existe" de "existe pero no es tuyo". Un portal no puede usar la API para descubrir CUILs, expedientes o documentos ajenos.

| Código | Cuando |
|--------|--------|
| `400` | Validación de negocio: campo faltante o inválido, tipo no habilitado, contenido mal formado. El mensaje en `{"error": "..."}` siempre explica el motivo. |
| `401` | API Key faltante, inválida, expirada o de otro tipo (una key REST común no sirve para `/tad/*`). |
| `403` | Ciudadano `bloqueado` (cualquier operación) o no `validado` (operaciones de escritura). |
| `404` | Recurso inexistente **o no accesible para ese ciudadano** (mismo mensaje en ambos casos). |
| `409` | Conflicto de estado (ej. proponer un documento que no está firmado). |
| `429` | Rate limit excedido. |
| `503` | **Dos causas distintas, y se manejan al revés una de la otra** — ver abajo. |

### El `503` tiene dos causas

| Mensaje | Que es | Que hace el portal |
|---|---|---|
| `Servidor ocupado, reintente en unos segundos` | Pico de carga momentáneo del lado de GDI | **Reintentar solo**, con backoff. Se resuelve sin que intervenga nadie |
| Infraestructura del tenant incompleta (ej. migraciones pendientes) | Al municipio le falta una migración en su base | **No reintentar en loop**: avisar al equipo GDI |

Un portal que trate los dos igual falla de alguna de las dos formas: o le abre un ticket a
soporte por un pico de tráfico, o reintenta para siempre algo que ninguna cantidad de
reintentos va a arreglar. **Ruteá por el mensaje del cuerpo**, no solo por el código.

## Rate limits

Se aplican **varios baldes independientes a la vez**: una request tiene que pasar todos los
que le correspondan. Superado cualquiera se responde `429`, y el portal debe encolar y
reintentar pasado el minuto.

| Alcance | Límite |
|---------|--------|
| Toda la API TAD (por key) | **el valor configurado en tu API Key** (por defecto **60**/min; el administrador lo puede cambiar desde BackOffice) |
| `POST /tad/citizens` (adicional) | 5 requests/min |
| `GET /tad/citizens/*` (adicional, anti-scraping) | 10 requests/min |
| `POST` y `GET` de `/tad/citizens/*`, **por IP de origen** | 30 requests/min |

!!! warning "El alta de ciudadanos es el límite más apretado: 5/min"
    Es a propósito (evita que la API sirva para recorrer CUILs), pero sorprende a cualquiera
    que planee una **carga inicial del padrón**. Si tenés que dar de alta muchos vecinos de
    una, hablalo con el equipo GDI antes: a ese ritmo son 300 por hora.

!!! note "El límite general no es un número fijo"
    Es un valor por API Key guardado en la base. Preguntale al administrador cual tiene la
    tuya en vez de asumirlo — y no lo deduzcas midiendo, porque el balde por IP puede
    cortarte antes por un motivo distinto.

## Errores por endpoint

Códigos que puede devolver cada endpoint, más allá de los transversales (`401` sin/mala key, `429` rate limit, `500` inesperado). Todos los cuerpos de error tienen la forma `{"error": "mensaje"}`.

| Endpoint | Códigos específicos |
|----------|---------------------|
| `POST /tad/citizens` | `400` (`full_name`/`country_id` faltante, estado inválido) · `429` (límite propio de 5/min) |
| `GET /tad/citizens/{ref}` | `404` (no existe) |
| `PATCH /tad/citizens/{ref}` | `400` (campo distinto de `estado`, estado inválido) · `404` (no existe) |
| `GET /tad/document-types` · `GET /tad/case-templates` | — (solo transversales) |
| `GET /tad/document-types/{id}/fields` | `404` (tipo inexistente, no habilitado, o sin formulario) |
| `POST /tad/documents` | `400` (tipo no habilitado, campo de contenido incorrecto, PDF/base64 inválido, `form_data` inválido, `Idempotency-Key` vacía o >255) · `403` (ciudadano no validado o bloqueado) · `409` (reintento en curso o `Idempotency-Key` reusada con otro contenido) · `503` (migraciones pendientes, **o** servidor ocupado: reintentar) |
| `GET /tad/documents/{id}` | `404` (inexistente o de otro ciudadano) |
| `POST /tad/cases` | `400` (`case_template_id` inexistente o canal no-API) · `403` (ciudadano no validado o bloqueado) |
| `GET /tad/cases` | `403` (ciudadano bloqueado) |
| `GET /tad/cases/{id}` | `404` (inexistente o no compartido) |
| `GET /tad/cases/{id}/documents/{document_id}/url` | `404` (expediente/documento inexistente, no compartido, reservado, desvinculado o sin firmar) · `502` (fallo transitorio de storage: **reintentar**) |
| `POST /tad/cases/{id}/propose` | `404` (expediente/documento inexistente, no compartido o ajeno) · `409` (documento no firmado, o propuesta ya pendiente) |
| `POST /tad/webhook/test` | `422` (sin webhook configurado en la key TAD) |

## Contenido de la sección

- **[Conectar el portal de trámites](conectar-portal.md)** — guía de punta a punta: requisitos previos, flujo completo, como saber el número oficial, reintentos y checklist de producción. **Empeza acá.**
- [Ciudadanos](ciudadanos.md) — alta, consulta y cambio de estado de la base de ciudadanos.
- [Documentos](documentos.md) — catálogo de tipos, creación + firma en un paso (HTML, formulario controlado FFCC e Importado PDF), consulta de estado y reintentos con `Idempotency-Key`.
- [Expedientes](expedientes.md) — creación de expedientes, consulta de los compartidos y propuesta de vinculación de documentos.
- [Webhook de notificaciones](webhook.md) — eventos `documents.signed`, `documents.signature_failed` y `documents.notified`, con firma HMAC.
