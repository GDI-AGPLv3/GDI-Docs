# Expedientes

Un ciudadano puede **iniciar expedientes** (tramites) y **seguir los que le compartieron**. El acceso es siempre por share explicito: no hay navegacion libre de expedientes.

---

## Catalogo de tipos de expediente

```
GET /api/v1/tad/case-templates
```

Devuelve los tipos de expediente cuyo canal de creacion es `api` o `both` (configurable por el administrador en BackOffice).

**Respuesta `200 OK`:**

```json
{
  "case_templates": [
    {
      "id": "50c22aa9-41c9-47cd-92eb-b3696f50f33f",
      "type_name": "Habilitacion Comercial",
      "acronym": "HABCOM",
      "description": "Tramite de habilitacion de comercios"
    }
  ]
}
```

---

## Crear expediente

```
POST /api/v1/tad/cases
```

Requiere `X-Citizen-ID` de un ciudadano **validado**. Crea el expediente en la reparticion de radicacion configurada en el tipo, **encola** la caratula (CAEX) firmada por el ciudadano y lo comparte automaticamente con el.

**Body:**

```json
{
  "case_template_id": "50c22aa9-41c9-47cd-92eb-b3696f50f33f",
  "reference": "Habilitacion comercial local Calle Falsa 123"
}
```

**Respuesta `200 OK`:**

```json
{
  "case_id": "584ee1f9-2237-4d69-93dd-0dae54f43ba2",
  "case_number": "EE-2026-000227-MDEV-INNO",
  "official_number": "CAEX-2026-00003045-MDEV-TAD",
  "status": "creating",
  "cover": {
    "status": "queued",
    "session_id": "9d3b50dc-8959-41df-bb71-bc0b8bd457e4",
    "poll_url": "/signing/async-poll/9d3b50dc-8959-41df-bb71-bc0b8bd457e4",
    "message": "Carátula en proceso"
  }
}
```

`400` si el `case_template_id` no existe o su canal no admite creacion por API.

!!! warning "El expediente nace `creating`: su numero ya es definitivo, su caratula todavia no existe"
    El `case_number` y el `official_number` de la caratula se reservan dentro
    del request y **no cambian nunca**. El PDF de la caratula, en cambio, lo
    genera un worker unos segundos despues (GDI-436), y recien cuando sale el
    expediente pasa a `active`.

    Mientras tanto, para ESE expediente:

    - `GET /tad/cases/{id}` lo devuelve **sin documentos** (la caratula todavia
      no esta vinculada).
    - `POST /tad/cases/{id}/propose` responde **`409`**: no se puede proponer
      un documento a un expediente que todavia se esta creando.

    Las dos cosas son transitorias y se resuelven solas.

    **Como saber cuando termino:** pollear `GET /tad/cases/{id}` hasta que
    `status` sea **`active`** — mientras se crea vale `inactive` y `documents`
    viene vacio. Cuando pasa a `active`, en el mismo momento, la caratula ya
    esta vinculada y el `propose` deja de responder `409`.

    !!! danger "El `poll_url` del `cover` NO se puede usar por este canal"
        Viene en la respuesta por consistencia con el canal interno, pero el
        endpoint al que apunta exige `X-User-ID`, y una API Key TAD **no tiene
        usuario asociado**: responde `401`
        (`X-User-ID header requerido para REST API`).

        Desde el portal la señal es `GET /tad/cases/{id}`, no el `poll_url`.

    `official_number` **no sirve para descargar el PDF** hasta ese momento.

    Con el kill-switch `CASE_COVER_ASYNC_ENABLED=false` no hay nada que
    esperar: `status` llega en `"active"` y `session_id`/`poll_url` en `null`.

    Si la caratula falla, el expediente **no se pierde ni cambia de numero**:
    queda esperandola y la cola reintenta.

---

## Listar mis expedientes

```
GET /api/v1/tad/cases
```

Devuelve los expedientes **compartidos con el ciudadano** de `X-Citizen-ID` (incluye los que el mismo inicio). Un ciudadano `pendiente` puede listar; uno `bloqueado` recibe `403`.

**Respuesta `200 OK`:**

```json
{
  "cases": [
    {
      "case_id": "584ee1f9-2237-4d69-93dd-0dae54f43ba2",
      "case_number": "EE-2026-000227-MDEV-INNO",
      "reference": "Habilitacion comercial local Calle Falsa 123",
      "status": "active",
      "template_name": "Habilitacion Comercial",
      "template_acronym": "HABCOM",
      "shared_at": "2026-07-24T18:04:36Z"
    }
  ]
}
```

---

## Detalle de expediente

```
GET /api/v1/tad/cases/{case_id}
```

Solo si el expediente esta compartido con el ciudadano; si no, `404` generico (no distingue "no existe" de "no compartido").

**Respuesta `200 OK`:**

```json
{
  "case_id": "584ee1f9-2237-4d69-93dd-0dae54f43ba2",
  "case_number": "EE-2026-000227-MDEV-INNO",
  "reference": "Habilitacion comercial local Calle Falsa 123",
  "status": "active",
  "template_name": "Habilitacion Comercial",
  "template_acronym": "HABCOM",
  "documents": [
    {
      "document_id": "8bd9b4a2-692d-44dc-826f-22c6533545ac",
      "order": 1,
      "official_number": "CAEX-2026-00003045-MDEV-TAD",
      "reference": "Creacion EE-2026-000227-MDEV-INNO",
      "linked_date": "2026-07-24T18:04:38Z",
      "is_active": true,
      "pdf_source": "official"
    }
  ]
}
```

`documents` lista los documentos **vinculados** (oficiales) del expediente. Los documentos solo *propuestos* no aparecen hasta que el municipio los acepte.

!!! warning "Cambio de contrato (GDI-229): aca ya no viene `pdf_url`"
    Hasta la version 3.17.0 cada documento traia un `pdf_url` presignado listo para abrir.
    **Ya no.** Ahora viene `pdf_source` (`"official"`), que dice de que carril sale el PDF, y
    **la URL se pide aparte** al endpoint de abajo, cuando el ciudadano realmente va a ver el
    documento.

    El motivo: antes se firmaba una URL por CADA documento de CADA listado, aunque nadie
    abriera ninguno, y el TTL empezaba a correr ahi mismo. Un expediente de 30 documentos
    gastaba 30 firmas para mostrar una lista.

## Obtener la URL de un documento

```
GET /api/v1/tad/cases/{case_id}/documents/{document_id}/url
```

Devuelve un link presignado **fresco** del PDF oficial. Mismo gate que el detalle del
expediente: el share tiene que estar activo y el documento tiene que ser uno de los visibles
en **ese** expediente.

**Respuesta 200:**

```json
{
  "document_id": "8bd9b4a2-692d-44dc-826f-22c6533545ac",
  "official_number": "CAEX-2026-00003045-MDEV-TAD",
  "pdf_url": "https://...presignado...",
  "expires_in": 180
}
```

`expires_in` es **un entero de segundos** (180), no un texto: se puede hacer aritmetica con el.

| Codigo | Que significa | Que hacer |
|--------|---------------|-----------|
| `200` | URL generada | Descargar el PDF **ya** |
| `404` | No existe, no es tuyo, esta reservado, desvinculado o todavia sin firmar | No reintentar |
| `502` | Fallo transitorio de storage | **Reintentar** en unos segundos |
| `500` | Error interno | Reportar |

!!! danger "El `404` no distingue"
    Por diseno, un documento ajeno y uno inexistente dan el **mismo** 404:
    el portal no puede usar el codigo de error para averiguar si un UUID existe.

---

## Proponer documento al expediente

```
POST /api/v1/tad/cases/{case_id}/propose
```

Propone vincular un documento **ya firmado por el mismo ciudadano** a un expediente compartido con el. Del lado municipal la propuesta se acepta o rechaza desde la app GDI (igual que cualquier propuesta interna).

**Body:**

```json
{"document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743"}
```

**Respuesta `200 OK`:**

```json
{
  "case_id": "584ee1f9-2237-4d69-93dd-0dae54f43ba2",
  "document_draft_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "message": "Documento propuesto para vincular al expediente"
}
```

**Errores:**

| Codigo | Motivo |
|--------|--------|
| `404` | Expediente no compartido / inexistente, o documento inexistente **o de otro ciudadano** (mensaje generico) |
| `409` | El documento no esta firmado, o **ya tiene una propuesta pendiente** en ese expediente, o el **expediente todavia se esta creando** (ver abajo) |

!!! note "Propuestas repetidas"
    Proponer dos veces el mismo documento devuelve `409` mientras la primera propuesta siga pendiente. Si el municipio la rechaza, el documento puede proponerse de nuevo.

!!! tip "Un `409` recien creado el expediente se resuelve esperando"
    Los tres `409` de la tabla NO son equivalentes: los dos primeros piden que
    cambies algo (firmar el documento, esperar que resuelvan la propuesta
    anterior), pero el de **expediente en creacion** se arregla solo en unos
    segundos, cuando sale la caratula.

    Si acabas de crear el expediente con `POST /tad/cases`, espera a que
    `GET /tad/cases/{id}` devuelva `status: "active"` antes de proponer. El
    mensaje del error lo distingue del resto:

    > El expediente todavía se está creando (falta su carátula). Aguardá unos
    > instantes y volvé a proponer el documento.

    El cuerpo del `409` trae **solo** la clave `error` con ese texto: no hay
    `Retry-After` ni un codigo de error estable, asi que los tres casos se
    distinguen por el mensaje. (La respuesta si trae un header
    `x-correlation-id`, util para reportar un problema a soporte.)

---

## Flujo completo tipico

```mermaid
sequenceDiagram
    participant P as Portal municipal
    participant G as GDI (API TAD)
    participant M as Municipio (app GDI)

    P->>G: POST /tad/citizens (alta vecino)
    P->>G: PATCH /tad/citizens/{id} {"estado":"validado"}
    P->>G: POST /tad/cases (inicia tramite)
    G-->>P: case_id + numeros definitivos (status "creating": falta el PDF de la CAEX)
    Note over G: la caratula se genera aparte; el expediente pasa a active al salir
    P->>G: POST /tad/documents (declaracion a firmar)
    G-->>P: 202 Accepted + document_id (SIN numero)
    Note over G: la firma se procesa aparte
    G-->>P: Webhook documents.signed (official_number + pdf_url)
    P->>G: POST /tad/cases/{id}/propose (recien ahora: el doc ya esta firmado)
    M->>M: Acepta la propuesta y trabaja el expediente
    M->>G: Notificar documentos al ciudadano
    G-->>P: Webhook documents.notified (HMAC)
    P->>G: GET /tad/cases/{id} (estado y PDFs frescos)
```
