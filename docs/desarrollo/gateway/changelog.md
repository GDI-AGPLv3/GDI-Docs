---
title: Cambios de la API
description: Cambios del Gateway (REST y MCP) que pueden afectar a integraciones existentes.
---

# Cambios de la API

Cambios del Gateway (REST `/api/v1` y MCP) que pueden afectar a una integración que ya
funciona. Lo más nuevo arriba. La fecha es el día en que el cambio llegó a producción.

---

## Próxima versión (Backend/Gateway 5.11.0) — Alta de legajo sin duplicar, usuarios por tandas y rango de fechas

**Afecta a:** `POST /api/v1/records`, `POST /api/v1/records/{record_id}/documents`, `POST /api/v1/documents/import`, `GET /api/v1/system/users/list`, `GET /api/v1/cases/search`, `GET /api/v1/documents/search`, `POST /api/v1/documents/{document_id}/reject`, `GET /api/v1/cases/{case_id}`, `GET /api/v1/cases/{case_id}/permissions`, `POST /api/v1/cases/{case_id}/documents/propose` y las tools MCP `search_cases`, `search_documents`, `reject_document` y `propose_document`.
**Versión del Backend/Gateway:** 5.11.0. La fecha se completa el día que llega a producción.

| Situación | Antes | Ahora |
|---|---|---|
| Se reintenta el alta de un legajo después de un corte | Quedaba un legajo duplicado | Con el header `Idempotency-Key`, el reintento devuelve la respuesta original (`Idempotent-Replay: true`) y no crea otro. Ver [Legajos](rest-api/legajos.md#reintentos-seguros-idempotency-key) |
| Alta de legajo con `document_id` | Había que crear y vincular en dos pedidos | Un solo pedido: si la vinculación falla, no queda el legajo vacío |
| Se vincula un documento que ya estaba vinculado al mismo legajo | `409` | `200` con `"already_linked": true` |
| Se importa un PDF dos veces por un reintento | Quedaban dos documentos | Con `Idempotency-Key`, uno solo |
| `page` y `page_size` en la lista de usuarios | Se ignoraban: venían todos | Se respetan. Sin esos parámetros, la lista entera como siempre. Ver [Sistema](rest-api/sistema.md) |
| `date_from` y `date_to` en la búsqueda de expedientes y documentos (REST y MCP) | Se ignoraban sin aviso: venía todo | Filtran de verdad. Formato `YYYY-MM-DD` |
| Motivo de rechazo de menos de 5 caracteres | Se aceptaba (solo se frenaba el vacío) | `422`: `El motivo debe tener al menos 5 caracteres`. Igual que la pantalla |
| Se pide un expediente que no existe | `403` «Sin permisos» | `404` «Expediente no encontrado». Uno que existe pero es de otra área sigue en `403` |
| Se piden los permisos de un expediente de otra área | `500` | `403` |
| Se propone un documento ya propuesto o ya vinculado, o a un expediente archivado | Se aceptaba (propuesta duplicada) | `409` con el motivo. Los permisos traen `can_propose_documents` |

### Qué tenés que revisar

- Si tu integración manda `page` o `page_size` a `GET /system/users/list` y espera la lista entera, sacalos o recorré las páginas hasta `has_more: false`.
- Si tu integración trataba el `409` de «documento ya vinculado al legajo» como éxito, ahora llega `200`.
- Si mandás `date_from`/`date_to`, los resultados ahora vienen filtrados.

---

## Próxima versión (Backend/Gateway 5.10.0) — Firma con 409 y 422, topes de tamaño y de búsquedas

**Afecta a:** `POST /api/v1/documents/{document_id}/sign`, los pedidos que suben archivos (importar, reemplazar el PDF, adjuntos y Trámites a Distancia) y las búsquedas (REST y MCP).
**Versión del Backend/Gateway:** 5.10.0. La fecha se completa el día que llega a producción.

| Situación | Antes | Ahora |
|---|---|---|
| Se pide firmar un documento que ya se está firmando | `500` | `409` con el motivo |
| La firma no entra en la página | `500` | `422` `{"error": "<motivo>", "code": "FULLPAGE"}` |
| Pedido de importar, reemplazar o adjuntar de más de 30 MB | Rechazo por encima de 25 MB | `413` |
| Pedido de Trámites a Distancia de más de 36 MB | Sin tope propio | `413` |
| PDF de más de 250 páginas al importar o al firmar | Se aceptaba | `422` `PDF_DEMASIADAS_PAGINAS` |
| Muchas búsquedas seguidas de la misma persona | Sin tope | `429` `"code": "tope_busquedas"` con `Retry-After`. Parámetro opcional `query_id` (UUID) para contar una búsqueda una sola vez |

---

## 04/11/2026 — Rechazar un documento Importado ya no le borra el PDF

**Afecta a:** `POST /api/v1/documents/{document_id}/reject`, `PUT /api/v1/documents/{document_id}/imported-pdf` y la tool MCP `reject_document`.
**Versión del Backend/Gateway:** 5.9.2.

### Qué cambió

Un documento Importado no tiene texto: su contenido es el PDF.

| Situación | Antes | Ahora |
|---|---|---|
| Se rechaza un Importado | El PDF se borraba. El documento volvía a edición sin contenido | El documento vuelve a edición **con su PDF**, sin las firmas ni los adjuntos que GDI le había agregado |
| Se reemplaza el PDF de un Importado rechazado | `409` | `200`. El documento sigue en `rejected` hasta que se lo vuelve a enviar a firma |

La respuesta del rechazo de un Importado trae `pdf_cleanup` con lo que pasó con el PDF:

```json
{
  "success": true,
  "message": "Documento rechazado exitosamente",
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "new_status": "rejected",
  "pdf_cleanup": {
    "imported_pdf": "deleted",
    "reupload_required": true,
    "note": "El documento quedó sin PDF: hay que volver a subirlo con \"Reemplazar PDF\" antes de mandarlo a firmar."
  }
}
```

| `pdf_cleanup.imported_pdf` | Qué significa |
|---|---|
| `restored` | GDI volvió a dejar el PDF que se importó |
| `kept` | Nadie había firmado: el PDF quedó como estaba |
| `deleted` | El documento se envió a firma antes de este cambio y alguien ya había firmado. No hay copia limpia: hay que volver a subir el PDF |
| `missing` | No quedó ninguna copia del PDF: hay que volver a subirlo |
| `error` | No se pudo comprobar el PDF. El rechazo quedó guardado igual |

`reupload_required` y `note` vienen solo con `deleted` y `missing`.

### Por qué

Rechazar un Importado lo dejaba vacío. Para corregirlo había que borrarlo e importarlo de nuevo.

### Qué tiene que hacer una integración

- Si `pdf_cleanup.reupload_required` es `true`, subir el PDF con
  `PUT /api/v1/documents/{document_id}/imported-pdf` antes de volver a enviarlo a firma.
- Para corregir un Importado rechazado, reemplazar el PDF directamente: ya no hace falta
  borrar el documento.

---

## 02/11/2026 — Cabeceras de seguridad y búsquedas sin comodines

**Afecta a:** todas las respuestas del Gateway; el parámetro `search` de `GET /api/v1/cases/search` y `GET /api/v1/documents/search`, y las tools MCP `search_cases` y `search_documents`.
**Versión del Backend/Gateway:** 5.9.1.

### Qué cambió

1. **Cabeceras de seguridad.** Todas las respuestas del Gateway traen estas cabeceras:

    | Cabecera | Valor |
    |---|---|
    | `X-Content-Type-Options` | `nosniff` |
    | `Referrer-Policy` | `strict-origin-when-cross-origin` |
    | `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
    | `X-Frame-Options` | `DENY` |

2. **`%` y `_` en `search` son letras.** Antes eran comodines de la base de datos:
   `?search=%%%` devolvía todos los expedientes o documentos. Ahora `?search=50%` busca el
   texto `50%` tal cual.

### Por qué

Las cabeceras ya estaban en el Backend; faltaban en el Gateway. Los comodines dejaban que una
búsqueda trajera mucho más de lo que se pedía.

### Qué tiene que hacer una integración

- Si usaba `%` o `_` en `search` como comodín, mandar solo el texto que busca: la búsqueda ya
  es por "contiene".
- No mostrar respuestas del Gateway dentro de un `<iframe>`: el navegador lo bloquea por
  `X-Frame-Options: DENY`.

---

## 02/11/2026 — Errores que daban 500 ahora dan el código correcto

**Afecta a:** rechazo y firma de documentos, rutas `/api/v1/records/...` y autenticación por API Key.
**Versión del Backend/Gateway:** 5.9.1.

### Qué cambió

| Situación | Antes | Ahora |
|---|---|---|
| `POST /documents/{id}/reject` de un documento ya rechazado | `500` | **`409`** `El documento '<id>' ya fue rechazado y no puede ser modificado` |
| `POST /documents/{id}/reject` de un documento oficial (ya numerado) | `500` | **`409`** `No se puede rechazar un documento completado` |
| `POST /documents/{id}/reject` y el documento se firma en ese mismo momento | `500` | **`409`**: el documento quedó firmado y el rechazo no se aplicó |
| `POST /documents/{id}/sign` de un numerador sin el rango que pide el tipo | `403` `Usuario no autorizado para firmar este documento` | `403` con el motivo real, por ejemplo `Sin permiso de rango para numerar '<tipo>'...` |
| `record_id`, `relation_id` o `link_id` que no es un UUID, en cualquier ruta `/records/{record_id}/...` | `500` | **`400`** `record_id inválido (se espera UUID)` |
| `X-API-Key` con caracteres no ASCII (por ejemplo, una `ñ` pegada por error) | `500` en algunas instalaciones | **`401`**, como cualquier API Key inválida |

### Por qué

Con un `500`, la integración no sabe si el pedido falló o si conviene reintentar. Un rechazo
repetido o un id mal copiado terminaban en reintentos que nunca iban a andar.

### Qué tiene que hacer una integración

- Tratar el `409` del rechazo como "ya no hay nada que rechazar": consultar el documento con
  `GET /api/v1/documents/{document_id}` para ver su estado.
- Con el `403` de firma, mostrar el texto de `error`: dice qué rango hace falta.
- No reintentar un `400` ni un `401` sin cambiar el pedido.

---

## 02/11/2026 — Documentos certificados de origen (`certified_origin`)

**Afecta a:** `GET /api/v1/documents/{document_id}`, `GET /api/v1/cases/{case_id}/documents`, `POST /api/v1/documents/{document_id}/sign`, `POST /api/v1/documents/import` y las tools MCP `get_document` y `get_case_documents`.
**Versión del Backend/Gateway:** 5.9.1.

### Qué cambió

Un **certificado de origen** es un PDF que llega con una firma de certificación (por ejemplo,
de un escribano). Si GDI le agrega algo, esa certificación se rompe. Por eso GDI lo guarda
sin tocarlo:

- no le agrega la hoja de firma de GDI;
- no le agrega adjuntos;
- el número oficial queda en la base de datos, pero **no se imprime en el PDF**;
- los firmantes comunes dan **conformidad** en vez de firmar el PDF;
- el numerador numera sin firmar el PDF.

Campos nuevos (booleano, `false` por defecto):

| Dónde | Campo |
|---|---|
| `GET /documents/{id}` y tool `get_document` | `certified_origin` en la raíz de la respuesta |
| `GET /cases/{id}/documents` y tool `get_case_documents` | `certified_origin` en cada elemento de `official` |

Firma por REST: un certificado de origen se firma con `POST /documents/{id}/sign` **aunque el
tipo de documento exija firma digital**. Ahí nadie firma el PDF, así que no hace falta token.

| Situación al firmar un certificado de origen | Respuesta |
|---|---|
| GDI no pudo comprobar el PDF en ese momento | `503` con `Retry-After: 5` y `"code": "CERTIFIED_CHECK_RETRY"` |
| El PDF cambió desde que se importó | `409` `El PDF cambió desde que se verificó como certificado de origen...` |

Al importar (`POST /documents/import`), GDI rechaza con `400` un PDF cuya certificación no se
puede conservar. Ejemplos del texto de `error`:

- `La firma de este PDF está rota o el documento fue modificado después de firmarse...`
- `El PDF dice venir certificado, pero ninguna de sus firmas respalda esa certificación...`
- `El PDF está protegido con contraseña para abrirse...`
- `El PDF trae firmas digitales que no se pudieron leer...`

### Por qué

Antes GDI firmaba encima del PDF certificado y la certificación de origen dejaba de ser válida.

### Qué tiene que hacer una integración

- No esperar el número oficial impreso en un PDF con `certified_origin: true`: leerlo de la
  respuesta de la API.
- Para sumar archivos a un certificado de origen, cargarlos como documento aparte en el mismo
  expediente.
- Con el `503` de `CERTIFIED_CHECK_RETRY`, reintentar después de los segundos de `Retry-After`.

---

## 26/10/2026 — Buscar dentro de los documentos de un legajo

**Afecta a:** `GET /api/v1/records/{record_id}/documents`.
**Versión del Backend/Gateway:** 5.7.0.

### Qué cambió

Parámetro nuevo `search`: filtra los documentos vinculados por número oficial o por
referencia. Busca por "contiene" y no distingue mayúsculas.

```http
GET /api/v1/records/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents?search=IF-2026
```

Sin `search`, la respuesta es la misma de antes.

### Qué tiene que hacer una integración

Nada. Es un parámetro opcional.

---

## 26/10/2026 — MCP: la identidad se ata al `sub`, no solo al email

**Afecta a:** todas las tools MCP y `list_my_tenants`.
**Versión del Backend/Gateway:** 5.8.0.

### Qué cambió

Cada usuario de GDI queda atado al `sub` de su cuenta en el proveedor de autenticación la primera vez que entra. Si
el email del token coincide con un usuario atado a **otro** `sub`, el Gateway no lo toma: ese
municipio no aparece para esa cuenta.

### Por qué

Con el email solo, otra cuenta en el proveedor de autenticación con el mismo email podía entrar como esa persona.

### Qué tiene que hacer una integración

Nada, si cada persona usa siempre la misma cuenta. Si alguien deja de ver su municipio después
de crear una cuenta nueva con el mismo email, el municipio tiene que revisar su usuario.

---

## 21/10/2026 — Más errores con su código correcto y API Keys de usuarios dados de baja

**Afecta a:** firma, alta de expedientes, propuestas de documentos y autenticación por API Key.
**Versión del Backend/Gateway:** 5.6.0.

### Qué cambió

| Situación | Antes | Ahora |
|---|---|---|
| `POST /documents/{id}/sign` con la cola de firma saturada | `500` | **`429`** con `Retry-After` |
| `POST /cases` con una plantilla (`case_template_id`) que no existe | `500` | **`400`** con el motivo |
| `POST /cases/{id}/documents/reject-proposal` de una propuesta ya procesada | `500` | **`400`** |
| `case_id`, `proposed_id` o `document_draft_id` que no es un UUID, en `propose`, `accept-proposal` o `reject-proposal` | `500` | **`400`** `<campo> inválido (se espera UUID)` |
| API Key autorizada para un usuario que el municipio **dio de baja** | La integración seguía operando como ese usuario | **`401`** `Usuario no autorizado para esta API Key` |

Sobre el `429` de la firma:

- Con `Retry-After`, la saturación es pasajera: el texto dice `Reintentá en ~30 segundos`.
- Sin `Retry-After`, la cola necesita que intervenga soporte: el texto dice `Contactá a soporte`.
  Reintentar no sirve.

### Por qué

Dar de baja a una persona tiene que cortar también lo que una integración hace en su nombre.
Los `500` de firma y de propuestas eran errores del pedido o esperas pasajeras, no fallas del
servidor.

### Qué tiene que hacer una integración

- Con `429`, esperar los segundos de `Retry-After` y reintentar una sola vez.
- Con `401` de un usuario que antes andaba, pedirle al municipio que confirme que la persona
  sigue activa. Si se fue, autorizar a otro usuario para la API Key.
- Pedir las plantillas con `GET /api/v1/system/case-templates` en vez de guardar ids fijos.

---

## 06/10/2026 — `sector_filter` inválido ahora responde 400

**Afecta a:** `GET /api/v1/cases/search` (REST) y la tool MCP `search_cases`.
**Versión del Backend/Gateway:** 5.3.0.

### Qué cambió

`sector_filter` filtra la búsqueda de expedientes por **un** sector. Acepta:

- el acrónimo exacto de un sector activo (ej. `HAC`, `LEGAL`);
- el formato `DEPT#SECTOR` (ej. `HAC#PRIV`);
- el UUID del sector.

| Situación | Antes | Ahora |
|---|---|---|
| El valor resuelve a un sector | 200, lista filtrada | 200, lista filtrada (sin cambios) |
| El acrónimo o `DEPT#SECTOR` no existe (o el sector está inactivo) | 200 con la lista **sin filtrar** | **400** |
| El valor trae comas (varios sectores) | 200 con la lista **sin filtrar** | **400** |
| No se manda el parámetro | 200, lista completa | 200, lista completa (sin cambios) |

### Por qué

Con un valor que no resolvía, la API devolvía **todos** los expedientes con 200 y la integración
creía que había filtrado. Un error de tipeo, o un asistente de IA que inventaba un acrónimo,
terminaba mostrando datos que no correspondían al filtro pedido, sin ningún aviso.

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

Con comas el mensaje indica que `sector_filter` espera un sector único.

### Qué tiene que hacer una integración

- Mandar solo acrónimos que existan en el municipio: se pueden consultar con
  `GET /api/v1/system/sectors`.
- Si el sector no se conoce con certeza, **omitir** el parámetro en vez de adivinarlo.
- Tratar el 400 como "filtro inválido", no reintentar con el mismo valor.
