# Conectar el portal de tramites

Guia de punta a punta para el equipo que desarrolla el **portal de tramites del municipio**: que hay que tener antes de escribir la primera linea, cual es el flujo completo de un tramite y **como se entera el portal del numero oficial** de un documento firmado.

Si buscas el contrato campo por campo de cada endpoint, esta en [Ciudadanos](ciudadanos.md), [Documentos](documentos.md), [Expedientes](expedientes.md) y [Webhook](webhook.md). Esta pagina es el hilo que los une.

!!! info "Disponibilidad por ambiente"
    El `202`, el `GET /tad/documents/{id}` y la `Idempotency-Key` estan disponibles hoy en
    **DEV**; llegan a **ARIES** y a **produccion** con el proximo pase. Detalle en
    [API TAD Ciudadano](index.md). Confirma con el equipo GDI contra que ambiente integras.

---

## 1. Antes de empezar---

## 1. Antes de empezar

Cinco cosas que se piden **una sola vez** al administrador del municipio (BackOffice) y sin las cuales el portal no arranca:

| # | Que | Donde se obtiene | Sin esto |
|---|-----|------------------|----------|
| 1 | **URL del Gateway** de tu municipio | Administrador / equipo GDI | No hay a donde pegarle |
| 2 | **API Key de tipo TAD** (`key_type='tad'`) | BackOffice → `/api-key` | `401` en todo |
| 3 | **URL de callback + secret del webhook**, cargados en esa misma key | BackOffice → `/api-key` | El portal nunca se entera del numero oficial |
| 4 | **Tipos de documento con "Firmable por TAD"** activo | BackOffice → Tipos de Documento | `400 Tipo de documento 'X' no habilitado para firma ciudadana (TAD)` |
| 5 | **Tipos de expediente con canal `api` o `both`** | BackOffice → Tipos de Expediente | El catalogo de expedientes vuelve vacio |

!!! danger "La API Key es del municipio entero"
    Identifica al municipio completo y no tiene usuario asociado: quien la tiene puede operar a nombre de **cualquier** ciudadano de la base. Vive en el **backend** del portal, nunca en el navegador ni en una app movil.

!!! warning "El webhook se configura del lado de GDI, no del tuyo"
    La URL de callback la carga el administrador en la API Key. Es el paso que mas se olvida: sin el, `POST /tad/documents` sigue devolviendo `202` con normalidad, la firma se hace bien... y el aviso con el numero **no le llega a nadie**. Verificalo con [`POST /tad/webhook/test`](webhook.md#probar-el-webhook-sandbox) **antes** de escribir el resto del portal.

### Prueba de humo (5 minutos)

Antes de integrar nada, confirma que la key funciona y que tu receptor de webhooks esta vivo:

```bash
export GW="https://gateway.tu-muni.gob.ar"
export KEY="tu-api-key-tad"

# 1. La key es valida y hay tipos habilitados
curl -s "$GW/api/v1/tad/document-types" -H "X-API-Key: $KEY"

# 2. Tu receptor de webhooks recibe y valida la firma
curl -s -X POST "$GW/api/v1/tad/webhook/test" -H "X-API-Key: $KEY"
```

El segundo comando te devuelve **que contesto tu propio servidor** (`delivered`, `status_code`, `error`). Si ahi no da verde, no sigas: el resto del flujo depende de eso.

---

## 2. El flujo completo

```
                       PORTAL MUNICIPAL                    GDI
  El vecino se registra
        │
        ├─ 1. POST /tad/citizens ──────────────────────►  ciudadano 'pendiente'
        │
  El municipio valida identidad
        │
        ├─ 2. PATCH /tad/citizens/{id} {"estado":"validado"} ──►  puede firmar
        │
  El vecino inicia un tramite
        │
        ├─ 3. GET /tad/document-types ─────────────────►  que puede firmar
        │
        ├─ 4. POST /tad/documents ─────────────────────►  202 Accepted
        │                                                    │ (firma en cola)
        │  ◄──── webhook documents.signed ───────────────────┘
        │        (numero oficial + pdf_url)
        │
        ├─ 5. POST /tad/cases ─────────────────────────►  expediente + caratula
        │                                                 (numero al instante)
        │
        └─ 6. POST /tad/cases/{id}/propose ────────────►  el municipio acepta
                                                          la vinculacion
```

Los pasos 1 y 2 se hacen una vez por vecino; del 3 al 6, una vez por tramite.

---

## 3. Paso a paso

### Paso 1 y 2 — El ciudadano tiene que existir y estar validado

`POST /tad/documents` exige un ciudadano en estado `validado`. Un ciudadano recien creado nace `pendiente` y **no puede firmar** (`403`).

```bash
# Alta (upsert por country_id: si ya existe, actualiza en vez de duplicar)
curl -X POST "$GW/api/v1/tad/citizens" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"full_name": "Maria Portal", "country_id": "27333444556"}'

# Validacion (el unico campo que acepta el PATCH es `estado`)
curl -X PATCH "$GW/api/v1/tad/citizens/27333444556" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"estado": "validado"}'
```

**Quien valida es el municipio, no GDI.** GDI solo guarda el estado: el criterio (login con AFIP/ANSES, validacion presencial, mesa de entradas) lo define el portal. Decidilo antes de salir a produccion, porque es el paso que puede dejar tramites frenados esperando a una persona.

Detalle completo en [Ciudadanos](ciudadanos.md).

### Paso 3 — Preguntar que se puede firmar

Nunca hardcodees acronimos: el administrador puede habilitar o deshabilitar tipos en cualquier momento.

```bash
curl -s "$GW/api/v1/tad/document-types" -H "X-API-Key: $KEY"
```

De cada tipo te importan dos cosas: el `acronym` (es lo que manda el `POST`, no el `id`) y el `has_fields`:

- `has_fields: false` → mandas HTML libre en `content_html` (o nada, y sale la `reference`).
- `has_fields: true` → es un **formulario controlado (FFCC)**: primero pedis los campos con `GET /tad/document-types/{id}/fields` (aca si, por `id`) y despues mandas `form_data`. Ver [FFCC](documentos.md#variante-ffcc-formulario-controlado).
- Si el tipo es **Importado**, mandas el PDF ya armado en `pdf_base64`.

### Paso 4 — Crear y firmar: la respuesta es `202`, no el numero

```bash
curl -X POST "$GW/api/v1/tad/documents" \
  -H "X-API-Key: $KEY" -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "PROV",
    "reference": "Solicitud de poda de arbol",
    "content_html": "<p>Solicito la poda del arbol frente a mi domicilio.</p>"
  }'
```

```json
{
  "success": true,
  "message": "Documento recibido — la firma se está procesando",
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "session_id": "9f2b1c40-5d3e-4a71-9c88-2b0a5e6d1f34",
  "status": "queued",
  "expires_at": "2026-07-24T18:41:09Z"
}
```

Que hacer con cada campo:

| Campo | Que es | Que hace el portal con esto |
|---|---|---|
| `document_id` | El documento, ya creado | **Guardalo.** Es la clave con la que vas a reconocer el webhook y con la que se propone la vinculacion al expediente |
| `session_id` | Esta corrida de firma | Guardalo para trazar el caso con soporte si algo no llega |
| `status` | `queued` | La firma esta en cola |
| `expires_at` | Vencimiento de la sesion de firma (30 min por defecto) | Si pasado ese plazo no llego ningun webhook, es un caso a revisar |

!!! danger "Guardar el `document_id` no es opcional"
    Es el **unico** identificador que vincula tu solicitud con el webhook que va a llegar despues. Persistilo junto al tramite **en la misma transaccion** en la que registras el pedido del vecino, antes de contestarle nada al navegador. Si lo perdes, el documento se firma igual pero tu portal no tiene como saber de quien era.

### Paso 5 — Saber el numero oficial

Esta es la parte que mas confunde al llegar de un modelo sincronico. **El numero no viene en el `202`.** La firma real (armado del PDF, sellado, subida) tarda unos segundos y bajo carga puede tardar mas, asi que GDI corta el request enseguida y avisa despues.

#### Camino oficial: el webhook `documents.signed`

```json
{
  "event": "documents.signed",
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "official_number": "PROV-2026-00003039-MDEV-TAD",
  "pdf_url": "https://...presignado-600s...",
  "status": "signed",
  "sent_at": "2026-07-24T18:12:31.412Z"
}
```

Tu handler tiene que, en este orden:

1. **Validar la firma HMAC** del header `X-GDI-Signature` ([como](webhook.md#verificacion-de-firma-hmac)). Sin esto cualquiera que descubra tu URL te inyecta numeros falsos.
2. **Responder `2xx` rapido** — encolar y procesar despues. GDI reintenta con backoff exponencial durante horas si no contestas.
3. Buscar el tramite por `document_id` y guardar el `official_number`.
4. **Descargar el PDF ya**: el `pdf_url` es un link presignado que **vence a los 10 minutos**. Si lo guardas en tu base para usarlo mañana, mañana da error.
5. **Deduplicar**: la entrega es *al menos una vez*. El mismo `documents.signed` puede llegar dos veces; si ya tenes numero para ese `document_id`, ignoralo.

Y el par negativo, que hay que manejar si o si:

```json
{
  "event": "documents.signature_failed",
  "document_id": "007a5613-...",
  "status": "failed",
  "failure_reason": "notary_business_error",
  "sent_at": "2026-07-24T18:12:31.412Z"
}
```

El documento **queda sin numerar**. El portal puede volver a dar de alta el documento (un `POST` nuevo). `failure_reason` es un codigo para soporte, no un texto para mostrarle al vecino.

!!! tip "Un solo endpoint receptor para todos los eventos"
    Los tres eventos llegan a la **misma** URL de callback y todos traen el campo
    `event`: ruteá por ahí. **Ignora silenciosamente** los que no reconozcas — es la forma
    de que un evento nuevo en una version futura de GDI no te tire el handler.

#### El otro camino: preguntar

```
GET /api/v1/tad/documents/{document_id}
```

Con el `document_id` del `202`, el portal puede preguntar en cualquier momento como viene esa firma:

```bash
curl -s "$GW/api/v1/tad/documents/$DOC_ID"   -H "X-API-Key: $KEY" -H "X-Citizen-ID: 27333444556"
```

```json
{
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "status": "signed",
  "official_number": "PROV-2026-00003039-MDEV-TAD",
  "pdf_url": "https://...presignado...",
  "signed_at": "2026-07-24T18:12:29Z",
  "reference": "Solicitud de poda de arbol",
  "document_type_acronym": "PROV",
  "failure_reason": null
}
```

`status` es `queued` (esperar), `signed` (listo, con numero y PDF) o `failed` (con `failure_reason`: hay que volver a dar de alta el documento). Detalle en [Documentos](documentos.md#consultar-el-estado-de-un-documento).

Para que sirve, en concreto:

- **Desarrollo**: `localhost` no es alcanzable desde GDI, asi que sin esto habria que montar un tunel solo para ver si la firma salio.
- **Reconciliar**: un trámite que quedo en `queued` pasado el `expires_at`, o uno cuyo webhook se perdio porque tu servidor estuvo caido mas tiempo que los reintentos.
- **Respaldo del webhook**, mientras el municipio termina de publicar el endpoint de callback.

!!! warning "Preguntar no reemplaza escuchar"
    El webhook avisa **cuando pasa algo**; esto contesta **cuando preguntan**. Un portal
    que sondee en loop cerrado se come el rate limit de la key (30 req/min) y se entera
    **mas tarde** que uno que escucha. Si vas a sondear igual, hacelo con backoff
    (2 s, 5 s, 15 s, 30 s) y solo sobre los documentos que todavia esperas.

    **Configura el webhook igual.** Este endpoint es una red, no el piso.

### Paso 6 — Expediente y vinculacion

A diferencia del documento, el expediente **si devuelve el numero al instante** (es sincronico):

```bash
curl -X POST "$GW/api/v1/tad/cases" \
  -H "X-API-Key: $KEY" -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{"case_template_id": 4, "reference": "Poda de arbol - Calle Falsa 123"}'
```

```json
{
  "case_id": "584ee1f9-...",
  "case_number": "EE-2026-000227-MDF-INNO",
  "official_number": "CAEX-2026-00003045-MDF-TAD"
}
```

El expediente nace con su caratula y **compartido con el ciudadano** que lo inicio. Despues, con el documento ya firmado (paso 5), se **propone** la vinculacion: el municipio la acepta o la rechaza desde la aplicacion. Es asi a proposito — el portal propone, el municipio dispone.

Detalle en [Expedientes](expedientes.md).

---

## 4. Reintentos: mandá siempre una `Idempotency-Key`

Cada `POST /tad/documents` crea un documento **nuevo**. Si el portal reintenta por un timeout de red y la primera llamada en realidad si habia llegado, quedan **dos documentos firmados y numerados** para el mismo tramite. Un timeout **no significa que el documento no se creo**.

La solucion es un header:

```bash
curl -X POST "$GW/api/v1/tad/documents"   -H "X-API-Key: $KEY" -H "X-Citizen-ID: 27333444556"   -H "Idempotency-Key: tramite-4711"   -H "Content-Type: application/json"   -d '{ ... }'
```

Con la misma clave, un reintento devuelve **la misma respuesta** (`202` + header `Idempotent-Replay: true`) en vez de crear un segundo documento.

!!! danger "Una clave por trámite, no por intento"
    Es el error que anula toda la proteccion: si generas un UUID nuevo en cada reintento,
    para GDI son solicitudes distintas y vas a tener duplicados igual. La clave se genera
    **cuando el vecino aprieta el boton** y se guarda junto al tramite; todos los
    reintentos de ese envio la reusan.

Reglas del resto:

- La clave vive **24 horas** y su alcance es tu API Key. Maximo 255 caracteres.
- **Misma clave con otro contenido → `409`**: es una clave reciclada por error. Cada solicitud distinta necesita la suya.
- **Reintento mientras el primero se procesa → `409`**: esperar unos segundos.
- **Si el alta falla (`400`/`403`), la clave queda libre**: se corrige el cuerpo y se reintenta con la misma.
- **No se deduplica por contenido**: dos solicitudes identicas del mismo vecino pueden ser dos tramites reales. Sos vos el que sabe si son el mismo.

Y aunque uses la clave, sigue valiendo lo de siempre: no reintentes automaticamente un timeout sin mirar. Con `Idempotency-Key` el reintento es seguro; sin ella, un timeout es "no se que paso" y conviene marcarlo para revision — o preguntar con [`GET /tad/documents/{id}`](documentos.md#consultar-el-estado-de-un-documento).

Contrato completo en [Documentos](documentos.md#reintentos-seguros-idempotency-key).

## 5. Checklist antes de produccion

- [ ] La API Key vive solo en el backend; no aparece en el bundle del front ni en un repo.
- [ ] El webhook esta configurado en la key y `POST /tad/webhook/test` da `delivered: true`.
- [ ] El handler **valida la firma HMAC** y rechaza timestamps fuera de la ventana de 5 minutos.
- [ ] El handler responde `2xx` en menos de un par de segundos (encola y procesa aparte).
- [ ] El handler **deduplica** por `document_id`.
- [ ] El handler rutea por `event` e **ignora los desconocidos**.
- [ ] Se maneja `documents.signature_failed`, no solo el camino feliz.
- [ ] El PDF se **descarga al recibir el webhook** (el link vence a los 10 minutos).
- [ ] El `document_id` se persiste junto al tramite antes de contestarle al vecino.
- [ ] El `POST /tad/documents` manda `Idempotency-Key`, **una por tramite** (no por intento).
- [ ] Se respeta el rate limit de 30 req/min por key y se maneja el `429`.
- [ ] Esta definido **quien y como** pasa un ciudadano de `pendiente` a `validado`.
- [ ] Hay un tablero o alerta para tramites que quedaron en `queued` pasado el `expires_at`.

---

## 6. Sintomas y causas

| Sintoma | Causa mas probable |
|---|---|
| `401` en todo | La key no es de tipo TAD (una key REST comun **no** sirve para `/tad/*`), o esta vencida/inactiva |
| `403` al crear un documento | El ciudadano esta `pendiente` (falta el PATCH a `validado`) o `bloqueado` |
| `400 Tipo de documento 'X' no habilitado...` | Falta tildar "Firmable por TAD" en BackOffice, o el acronimo no existe (el mensaje es el mismo en ambos casos, a proposito) |
| El `202` llega pero **nunca** el webhook | La API Key no tiene `webhook_url` configurada. Confirmalo con `POST /tad/webhook/test`: si da `422`, es eso. Mientras tanto, el estado se consulta con `GET /tad/documents/{id}` |
| El webhook llega y el PDF da error al descargarlo | El `pdf_url` vencio (10 min). Hay que descargarlo al recibirlo |
| Documentos duplicados | Reintento sin `Idempotency-Key`, o una clave nueva por intento. Ver [Reintentos](#4-reintentos-manda-siempre-una-idempotency-key) |
| `409` al crear un documento | Reintento en curso con la misma `Idempotency-Key`, o clave reusada con otro contenido |
| `429` | Rate limit: 30 req/min por key (10/min adicional en los `GET /tad/citizens/*`) |
| `503` | Infraestructura del tenant incompleta (migraciones pendientes). No es un error del portal: avisar al equipo GDI |
| El catalogo de expedientes vuelve vacio | Ningun tipo de expediente tiene canal `api` o `both` |
