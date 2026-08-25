# Documentos

Creacion y **firma electronica**: el documento nace y se firma con el sello del ciudadano, para quedar numerado oficialmente. No hay borradores por API.

!!! info "La firma es asincronica (desde 3.12.0, en DEV y ARIES)"
    El alta responde **`202 Accepted`** y la firma se procesa a continuacion. El numero
    oficial y el link al PDF **no vienen en esa respuesta**: llegan por **webhook**
    (`documents.signed`).

    Antes el pedido se quedaba esperando a que la firma terminara, lo que bajo carga
    podia superar los 30 segundos y hacer que el portal cortara por timeout un
    documento que en realidad se estaba firmando bien.

    En **produccion** este cambio todavia no esta: alli el alta responde `200` con el
    `official_number` ya en el cuerpo. Ver la [tabla por ambiente](index.md).

!!! warning "Configura el timeout del cliente en mas de 60 segundos"
    El `202` es rapido **con el servicio caliente** (unos pocos segundos), pero la
    **primera llamada del dia puede tardar mas de 40 segundos**: el armado del PDF todavia
    ocurre dentro del pedido, y el servicio que lo genera arranca en frio.

    Dos consecuencias practicas, y las dos importan:

    1. **Un timeout de 30 segundos te va a cortar un alta que salio bien.** El documento
       queda creado y encolado igual: cortar el pedido no lo cancela.
    2. Por eso la **[`Idempotency-Key`](#reintentos-seguros-idempotency-key) no es opcional
       en la practica**. Sin ella, ese reintento crea un segundo documento y el vecino
       termina con dos tramites numerados.

    Recomendacion: timeout de cliente **&ge; 60 s** y `Idempotency-Key` en todas las altas.

Numeracion: `{ACRONIMO}-{ANIO}-{NUMERO}-{MUNI}-TAD` (el sufijo `TAD` identifica los documentos firmados por ciudadanos).

---

## Catalogo de tipos habilitados

```
GET /api/v1/tad/document-types
```

Devuelve los tipos que el administrador habilito para firma ciudadana ("Firmable por TAD" en BackOffice). Solo pueden habilitarse tipos `HTML` (incluye formularios controlados FFCC) e `Importado`.

**Respuesta `200 OK`:**

```json
{
  "document_types": [
    {"id": 16, "name": "Constancia de Pago", "acronym": "PAGO", "description": "Constancia de pago", "has_fields": true},
    {"id": 6, "name": "Informe Grafico Importado", "acronym": "IFGRA", "description": "...", "has_fields": false},
    {"id": 3, "name": "Providencia", "acronym": "PROV", "description": "...", "has_fields": false}
  ]
}
```

`has_fields: true` indica que el tipo es un **formulario controlado (FFCC)**: antes de crear el documento hay que consultar sus campos.

!!! tip "Esquema descargable"
    Desde BackOffice, en el detalle de cada tipo de documento, el boton **"Descargar esquema para API"** genera el JSON con el contrato exacto de ese tipo, listo para compartir con el equipo del portal.

---

## Formularios controlados (FFCC)

**FFCC = Formulario Controlado.** Es un tipo de documento en el que el municipio, en vez de dejar escribir texto libre, define de antemano **que campos tiene el documento** (nombre, tipo de dato, si es obligatorio, que valores acepta). El portal no manda HTML: manda **los valores**, y GDI arma el PDF con la plantilla oficial, renderizando los campos como una tabla de dos columnas (etiqueta | valor).

Por que importa:

- **El municipio controla la forma del documento**, no el portal. Si mañana cambia el formulario, el PDF cambia solo.
- **GDI valida los datos** antes de firmar: un campo obligatorio vacio o un monto que no es numero se rechazan con `400`, no llegan a firmarse.
- El documento guarda un **snapshot** `{schema, data}`: queda registrado con que definicion de formulario se firmo, aunque despues el municipio la modifique.

Un tipo es FFCC cuando `GET /tad/document-types` lo devuelve con `has_fields: true`. En ese caso, antes de crear el documento hay que pedir su definicion:

```
GET /api/v1/tad/document-types/{id}/fields
```

!!! note "Aca va el `id`, no el acronimo"
    Este es el unico endpoint del bloque que se pide por `id` numerico (el que devuelve el catalogo). El `POST /tad/documents` en cambio usa `document_type_acronym`.

**Respuesta `200 OK`:**

```json
{
  "document_type_id": 16,
  "field_definitions": [
    {"name": "monto", "type": "number", "label": "Monto", "required": true, "min": 0},
    {"name": "fecha_pago", "type": "date", "label": "Fecha de pago", "required": true},
    {"name": "medio", "type": "select", "label": "Medio de pago", "required": true,
     "options": ["Efectivo", "Transferencia", "Debito"]},
    {"name": "observaciones", "type": "textarea", "label": "Observaciones",
     "required": false, "max_length": 500},
    {"name": "comprobante", "type": "file", "label": "Comprobante", "required": false}
  ]
}
```

`404` si el tipo no existe, no esta habilitado para TAD o no tiene formulario.

### Tipos de campo

Los campos los define el municipio; el portal tiene que saber leerlos todos. `label` es el texto que se muestra (y el que aparece en los mensajes de error); `name` es la clave que va en `form_data`.

| `type` | Que mandar en `form_data` | Restricciones opcionales del campo |
|---|---|---|
| `text` | string | `max_length` |
| `textarea` | string (varias lineas) | `max_length` |
| `email` | string con formato de email valido | `max_length` |
| `number` | numero JSON (`15300.50`). Tambien se tolera el string `"15300.50"`. **`true`/`false` no cuentan como numero** | `min`, `max` |
| `date` | string `"YYYY-MM-DD"` | — |
| `select` | uno de los valores de `options`, exacto | `options` (obligatorio en la definicion) |
| `boolean` | `true` o `false` (JSON, no `"true"`) | — |
| `file` | **no disponible por API**: enviar `null` u omitir | — |

Si el campo no declara sus propios limites, igual rigen topes de cordura: los `number` deben ser finitos y de magnitud razonable (hasta ±1 000 000 000 000), los textos tienen tope de 20 000 caracteres y las fechas deben ser reales y con año entre 1900 y 2200. Si el campo si declara `min`/`max`/`max_length`, mandan esos.

Un campo opcional se omite del `form_data` o se manda en `null`: no se valida su tipo.

---

## Crear y firmar documento

```
POST /api/v1/tad/documents
```

Requiere `X-Citizen-ID` de un ciudadano **validado**.

**Body comun:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `document_type_acronym` | string | Si | Acronimo del tipo (ej. `PROV`) |
| `reference` | string | Si | Referencia / motivo del documento |

Segun el tipo, el contenido va en **uno solo** de estos tres campos (son mutuamente excluyentes):

| Tipo | Campo de contenido | Regla |
|------|--------------------|-------|
| HTML comun (`has_fields: false`) | `content_html` | Opcional: si se omite, el PDF muestra la `reference` |
| FFCC (`has_fields: true`) | `form_data` | **Requerido**: dict plano `{campo: valor}` |
| Importado | `pdf_base64` | **Requerido**: PDF en base64, maximo 20 MB |

**Respuesta `202 Accepted`** (igual para las tres variantes):

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

El `session_id` identifica esta firma: sirve para trazar el caso con soporte si algo
no llega.

!!! warning "El numero oficial NO viene aca"
    Llega por webhook, en el evento **`documents.signed`**, junto con el `pdf_url`.
    Si la firma falla definitivamente, llega **`documents.signature_failed`** — el
    portal nunca se queda esperando un aviso que no va a existir.

    **Guardar el `document_id`** es lo que permite reconocer despues ese webhook: es el
    unico dato que ata la solicitud con su desenlace.

    Si el portal prefiere (o necesita) preguntar en vez de esperar, esta
    [`GET /tad/documents/{id}`](#consultar-el-estado-de-un-documento).

    Ver [Webhook de notificaciones](webhook.md) y
    [como saber el numero oficial](conectar-portal.md#paso-5-saber-el-numero-oficial).

### Reintentos seguros: `Idempotency-Key`

Cada `POST /tad/documents` crea un documento **nuevo**. Sin ninguna precaucion, un portal que reintenta por un timeout de red — cuando la primera llamada en realidad si habia llegado — termina con **dos documentos firmados y numerados** para el mismo tramite. Un timeout **no significa que el documento no se creo**.

Para eso esta el header opcional `Idempotency-Key`: un identificador que el portal elige (un UUID, o el id del tramite en su propia base) y **repite en cada reintento del mismo envio**.

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Idempotency-Key: tramite-4711" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

| Situacion | Respuesta |
|---|---|
| Primera vez con esa clave | `202` normal: se crea el documento |
| Reintento, el alta anterior ya termino | `202` con **el mismo cuerpo** que la primera vez + header `Idempotent-Replay: true`. No se crea nada |
| Reintento mientras el primero todavia se procesa | `409` — reintentar en unos segundos |
| Misma clave con **otro contenido** | `409` — es una clave reciclada por error; cada solicitud distinta necesita la suya |
| El alta falla (`400`/`403`) | La clave **queda libre**: se puede corregir el cuerpo y reintentar con la misma |

!!! danger "Rehacer un documento despues de `documents.signature_failed` necesita una clave NUEVA"
    La clave protege **el pedido de alta**, no el desenlace de la firma. Si el alta se
    acepto (`202`) y la firma fallo despues, para GDI esa clave **ya cumplio** y quedo
    consumida por 24 horas.

    Entonces, cuando llega `documents.signature_failed` y volves a dar de alta el documento:

    - con la **misma** clave → recibis el `202` viejo con `Idempotent-Replay: true` y el
      `document_id` de siempre. **No se crea nada**, y te quedas esperando un webhook que
      ya ocurrio y fracaso.
    - con una clave **nueva** → se crea el documento nuevo, que es lo que querias.

    Es la unica excepcion a la regla de "una clave por tramite": un re-alta despues de un
    fracaso de firma es, a estos efectos, un pedido distinto.

- **Una clave por trámite, no por reintento**: si el portal genera una clave nueva en cada intento, no protege de nada.
- La clave vale **24 horas** y su alcance es la API Key (el municipio). Maximo 255 caracteres.
- **No se deduplica por contenido**: dos solicitudes identicas del mismo vecino pueden ser dos tramites reales. El unico que sabe si son "el mismo" es el portal, por eso lo declara con la clave.
- El header es **opcional**: sin el, el comportamiento es el de siempre y la proteccion contra duplicados queda enteramente del lado del portal. Ver [Reintentos](conectar-portal.md#4-reintentos-manda-siempre-una-idempotency-key).

---

!!! info "Disponibilidad por ambiente"
    El `202`, el `GET /tad/documents/{id}` y la `Idempotency-Key` estan disponibles en
    **DEV** y en **ARIES**; llegan a **produccion** con el proximo pase. Detalle en
    [API TAD Ciudadano](index.md). Confirma con el equipo GDI contra que ambiente integras.

## Consultar el estado de un documento

```
GET /api/v1/tad/documents/{document_id}
```

Requiere `X-Citizen-ID`: el documento tiene que ser de ese ciudadano (si no, `404` generico, igual que si no existiera).

Contesta si la firma sigue en cola, si ya termino — con el numero oficial y un link fresco al PDF — o si fallo:

```json
{
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "status": "signed",
  "official_number": "PROV-2026-00003039-MDEV-TAD",
  "pdf_url": "https://...presignado...",
  "signed_at": "2026-07-24T18:12:29Z",
  "reference": "Solicitud de poda de arbol",
  "document_type_acronym": "PROV",
  "created_at": "2026-07-24T18:11:09Z",
  "failure_reason": null
}
```

| `status` | Que significa | Que hace el portal |
|---|---|---|
| `queued` | La firma esta en cola o procesandose | Esperar. Trae ademas `session_id` y `expires_at` |
| `signed` | Firmado y numerado | Guardar `official_number`, descargar el `pdf_url` |
| `failed` | No se va a firmar solo | Mirar `failure_reason` y volver a dar de alta el documento |

Tres detalles del cuerpo, para que el portal no se rompa con ellos:

- Con `status: "signed"` el `pdf_url` puede venir en `null` si el link presignado no se pudo
  armar en ese momento. **El `official_number` sigue siendo valido**: se vuelve a pedir el
  estado y listo.
- `failure_reason: "signing_never_enqueued"` significa que el documento se creo pero su firma
  nunca llego a encolarse: hay que volver a darlo de alta.
- **Podes ver `queued` durante unos instantes despues de recibir `documents.signed`.** La
  firma y la escritura del documento oficial no son el mismo instante; mientras tanto el
  endpoint contesta `queued` a proposito, porque todavia no hay numero para mostrar. No es
  un error ni una vuelta atras: el numero que ya te llego por webhook es valido.

### Que hacer con cada `failure_reason`

`failure_reason` es un **codigo para soporte**, no un texto para mostrarle al vecino. No es
una lista cerrada —pueden aparecer codigos nuevos— asi que trata cualquier valor desconocido
como el caso general: **rehacer el alta con una `Idempotency-Key` nueva**, y si se repite,
escalarlo con el `session_id`.

| `failure_reason` | Que paso | Que hacer |
|---|---|---|
| `signing_never_enqueued` | El documento se creo pero la firma nunca llego a la cola | Rehacer el alta |
| `notary_business_error` | El servicio de firma rechazo el documento | Rehacer el alta; si se repite con el mismo contenido, escalar |
| `unknown` | El carril de firma no dejo causa registrada. Se vio en arranques en frio, y el reintento salio bien sin cambiar nada | Rehacer el alta una vez. Si vuelve a pasar, **escalar con el `session_id`**: no es un error del portal |
| cualquier otro | — | Rehacer el alta; escalar si se repite |

!!! warning "Un `failed` no siempre es culpa del contenido"
    Antes de mostrarle un error al vecino o de marcar el tramite como rechazado, reintenta
    al menos una vez. Varios de estos motivos son transitorios y el mismo documento, tal
    cual, se firma bien en el segundo intento.

!!! warning "Esto no reemplaza al webhook"
    El webhook avisa **cuando pasa algo**; esto contesta **cuando preguntan**. Un portal
    que sondee en loop cerrado se va a comer el rate limit de la key (30 req/min) y va a
    tardar mas en enterarse que si escuchara. Usalo para desarrollo (mientras tu endpoint
    no sea alcanzable desde GDI), para reconciliar trámites que quedaron sin aviso, y como
    respaldo — no como mecanismo principal.

    El `pdf_url` es un link presignado de **10 minutos**, como el del webhook: se puede
    volver a pedir cuantas veces haga falta.

---

### Variante HTML

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "PROV",
    "reference": "Solicitud de poda de arbol",
    "content_html": "<h1>Solicitud</h1><p>Solicito la poda del arbol frente a mi domicilio.</p>"
  }'
```

El HTML se **sanitiza** (es contenido que viene de afuera) y se renderiza dentro de la plantilla oficial del municipio: encabezado, pie, numeracion y hoja de firma los pone GDI. El portal manda solo el cuerpo.

#### Que HTML sobrevive a la sanitizacion

Todo lo que no este en esta lista se descarta en silencio: no da error, simplemente no aparece en el PDF. Conviene probar el tipo de documento antes de salir a produccion.

| | Permitido |
|---|---|
| **Etiquetas** | `p` `br` `hr` `div` `span` `blockquote` `pre` · `h1`–`h6` · `strong` `b` `em` `i` `u` `s` `sub` `sup` `mark` · `ul` `ol` `li` · `table` `thead` `tbody` `tfoot` `tr` `th` `td` `caption` `colgroup` `col` · `img` `a` · `figure` `figcaption` `details` `summary` |
| **Atributos** | `class` (en cualquier etiqueta) · `a`: `href` `title` `target` · `img`: `src` `alt` `title` `width` `height` · `td`/`th`: `colspan` `rowspan` · `col`/`colgroup`: `span` · `table`: `border` `cellpadding` `cellspacing` |
| **URLs** | solo `http`, `https` y `mailto` |

Lo que **no** pasa, y suele sorprender:

- **`style` inline y `<style>`**: no estan permitidos. El formato lo da la plantilla del municipio; para variantes visuales, usar `class`.
- **`src="data:image/png;base64,..."`**: el esquema `data:` no esta en la lista, asi que **las imagenes embebidas en base64 se pierden**. Un `<img>` tiene que apuntar a una URL `https` accesible desde el servidor que genera el PDF. Para adjuntar archivos, usar [`embedded_files`](#adjuntos-embebidos-embedded_files).
- **`id`**: se elimina a proposito (evita colisiones con el visor del sistema).
- `script`, `iframe`, `form`, `input`, `object` y los manejadores `on*`: se descartan enteros.
- A los `<a>` se les agrega `rel="noopener noreferrer"` automaticamente.

### Variante FFCC (formulario controlado)

Ver [Formularios controlados (FFCC)](#formularios-controlados-ffcc) para que es y como leer su definicion. El `form_data` es un **dict plano** `{name: valor}` con los `name` de `field_definitions` — ni anidado, ni con los `label`.

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "PAGO",
    "reference": "Pago de tasa municipal",
    "form_data": {
      "monto": 15300.50,
      "fecha_pago": "2026-07-24",
      "medio": "Transferencia",
      "observaciones": "Cuota 3 de 12"
    }
  }'
```

`form_data` es **excluyente** con `content_html` y `pdf_base64`: mandar dos da `400`. Y es al reves tambien — mandar `form_data` a un tipo que no es FFCC tambien da `400`.

Validaciones sobre `form_data`:

- Campos `required: true` faltantes → `400` (`"El campo 'Monto' es requerido"`).
- Tipo de dato incorrecto → `400` (`"El campo 'Monto' debe ser un numero"`; las fechas van en formato `YYYY-MM-DD`).
- Campos no definidos en el esquema → `400` (`"Campos no definidos en el formulario: ['x']"`). Enviar exactamente los campos de `field_definitions`.
- Controles de sanidad (aplican aunque el campo no declare limites): los `number` deben ser finitos y de magnitud razonable; los textos tienen un tope de largo; las fechas deben ser reales (`2026-13-45` se rechaza) y de un anio plausible. Si el campo define `min`/`max`/`max_length` propios, mandan esos.
- `select` con un valor fuera de `options` → `400` (`"El campo 'Medio de pago' debe ser uno de: Efectivo, Transferencia, Debito"`).
- Campos `type: "file"`: **no se pueden completar por API** — enviar `null` u omitirlos (`400` si traen valor: `"El campo 'Comprobante' es de tipo archivo: no disponible via TAD"`). Un formulario con un campo `file` **obligatorio** no se puede firmar por API: hay que pedirle al municipio que lo haga opcional. Para hacer llegar el archivo: un documento aparte de tipo `Importado`, o [`embedded_files`](#adjuntos-embebidos-embedded_files) si el tipo lo admite.
- El documento guarda un snapshot `{schema, data}` con la definicion vigente del formulario al momento de la firma.

### Variante Importado (PDF del portal)

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "IFGRA",
    "reference": "Escritura digitalizada",
    "pdf_base64": "JVBERi0xLjQK..."
  }'
```

- Maximo **20 MB**; el contenido debe ser un PDF real (se validan los magic bytes, no solo el nombre).
- GDI agrega la hoja de firma al final del PDF importado.
- `embedded_files` **no esta soportado** en Importado (el PDF no se regenera).

### Adjuntos embebidos (`embedded_files`)

Para tipos con "Admite archivos embebidos" habilitado (y que no sean Importado), se pueden adjuntar archivos que viajan **dentro** del PDF final:

```json
{
  "document_type_acronym": "IFPU",
  "reference": "Informe con plano adjunto",
  "content_html": "<p>Se adjunta plano del local.</p>",
  "embedded_files": [
    {"file_name": "plano.pdf", "content_base64": "JVBERi0xLjQK..."}
  ]
}
```

Limites: maximo **10 archivos** de **50 MB** cada uno. Extensiones permitidas: `csv, doc, docx, dxf, jpeg, jpg, ods, odt, pdf, png, txt, xls, xlsx`. Los PDF se validan por contenido (magic bytes).

### Errores frecuentes

| Codigo | Mensaje (ejemplo) | Causa |
|--------|-------------------|-------|
| `400` | `Tipo de documento 'X' no habilitado para firma ciudadana (TAD)` | Acronimo inexistente o tipo sin "Firmable por TAD" (mensaje identico en ambos casos, anti-enumeracion) |
| `400` | `El tipo de documento 'PROV' no es Importado: 'pdf_base64' no esta permitido` | Campo de contenido que no corresponde al tipo |
| `400` | `'pdf_base64' no decodifica a un PDF valido` | Base64 corrupto o contenido que no es PDF |
| `403` | `El ciudadano debe estar 'validado' para esta operacion (estado actual: pendiente)` | Ciudadano sin validar |
| `403` | Ciudadano bloqueado | Estado `bloqueado` |
