# Documentos y Legajos Públicos

La **visibilidad pública** es la tercera pata del modelo de visibilidad del sistema. Junto con **Interno** y **Reservado**, permite abrir información a la ciudadanía **sin necesidad de login**: cualquier persona en internet puede consultar los documentos oficiales y los legajos que el municipio decida publicar.

!!! abstract "La idea en una frase"
    La publicidad se define **por TIPO** (no ítem por ítem), igual que la reserva. Un administrador marca un **Tipo de Documento** como *Público* o una **Familia de Registro** como *Pública*; a partir de ahí, todos los ítems de ese tipo quedan expuestos por una API pública de solo lectura, con reglas fijas y sin dar permisos a mano.

!!! tip "Caso de uso completo: el Digesto Normativo"
    La aplicación más común de este modelo es publicar la normativa del municipio. La guía paso a paso está en [Digesto Normativo Público](digesto-normativo.md).

---

## Las tres visibilidades

Cada Tipo de Documento tiene un campo `visibility` con uno de tres valores:

| Visibilidad | Quien lo ve | Donde se configura |
|-------------|-------------|--------------------|
| **Interno** | Visibilidad estándar del municipio (conducta actual por defecto) | Tipos de Documento / Tipos de Expediente |
| **Reservado** | Solo firmantes, creador y responsables directos (ver [Reservados](reservados.md)) | Tipos de Documento / Tipos de Expediente |
| **Público** | **Cualquiera en internet, sin login** | Solo Tipos de Documento |

!!! warning "Los expedientes NUNCA son públicos"
    La opción *Público* **solo existe para Tipos de Documento**. Los **Tipos de Expediente** admiten únicamente *Interno* o *Reservado*. El BackOffice rechaza con error cualquier intento de crear o editar un tipo de expediente como público.

Los **legajos** (RLM) tienen su propio mecanismo de publicación, a nivel de **Familia de Registro** (ver [Familias públicas](#familias-de-registro-publicas) más abajo).

---

## Publicar un Tipo de Documento

Al **crear un tipo de documento propio** (botón *Nuevo tipo propio* en [Tipos de Documentos](tipos-de-documentos.md)), el modal incluye un selector obligatorio de **Visibilidad** con las tres opciones:

| Opción | Descripción que muestra el selector |
|--------|-------------------------------------|
| **Interno** | *Visibilidad estándar del municipio (conducta actual).* |
| **Reservado** | *Confidencial e irreversible. Solo firmantes/responsables directos podrán verlo.* |
| **Público** | *Sin login, accesible por cualquiera en internet. Irreversible.* |

Al elegir **Público** y presionar *Crear tipo*, el sistema pide una **confirmación explícita** antes de dar de alta el tipo:

!!! quote "Diálogo de confirmación — Crear tipo como Público"
    Este tipo de documento va a nacer como PUBLICO.

    Esto es IRREVERSIBLE: no se va a poder volver a "Interno" después de creado. Los PDFs firmados de este tipo van a quedar accesibles por cualquier persona en internet, SIN necesidad de login. Una vez publicado un PDF, aunque se borre después puede seguir cacheado o indexado por buscadores. Asegurate de que este tipo de documento nunca vaya a contener datos sensibles (DNI, CBU, domicilios, etc.).

    **Botones:** *Cancelar* / *Si, crear como Público*

### Qué se publica exactamente

Cuando un documento de un tipo público se **firma**, su **PDF oficial** se copia automáticamente a un bucket público y queda accesible por una URL estable. Solo se publican **documentos oficiales firmados** (`signed_at` presente): un borrador nunca sale a internet.

!!! danger "Irreversibilidad y prudencia"
    - La visibilidad de un tipo de documento se define **una sola vez, al crearlo**, y es **irreversible**: un tipo público no se puede volver a interno.
    - En el detalle del tipo la visibilidad aparece como una etiqueta de **solo lectura** (*"La visibilidad se define al crear el tipo y no se puede cambiar."*).
    - Una vez que un PDF se publicó, aunque después se despublique o borre, **puede seguir cacheado o indexado** por buscadores. Nunca marques como publico un tipo que pueda contener datos personales o sensibles.

!!! info "Solo tipos virgenes"
    Por debajo, el único cambio de visibilidad que el sistema acepta por edición es `interno → publico` (o `interno → reservado`) y **solo si el tipo no tiene ningún documento creado todavía**. En la práctica esto se resuelve eligiendo la visibilidad en el momento del alta.

---

## Familias de Registro públicas

Los legajos se publican a nivel de **Familia de Registro**. En el detalle de una familia ([Familias de Registro](familias-registro.md)) hay una tarjeta **"Publicación Pública"**.

!!! quote "Publicación Pública"
    *Expone los legajos de esta familia sin login, en internet. Reversible en cualquier momento.*

A diferencia de los tipos de documento, **publicar una familia es reversible**: se puede prender y apagar cuando se quiera. Al apagarlo, la API pública deja de servir esos legajos de inmediato.

### Configuración de una familia pública

Al activar el toggle **"Familia pública"** el sistema pide confirmación:

!!! quote "Diálogo — Publicar familia de legajos"
    Los legajos de esta familia van a ser visibles públicamente en internet, sin necesidad de login, mostrando solo los campos y estados que marques a continuación.

    Podés desactivarlo en cualquier momento (es reversible): al apagarlo, la API pública deja de servir estos legajos.

    **Botones:** *Cancelar* / *Sí, activar*

Con la familia pública, se configura **exactamente que se expone** (`public_config`):

| Opción | Que controla |
|--------|--------------|
| **Campos públicos** | Subconjunto de los campos del esquema de datos de la familia que se muestran. Solo se publican los campos tildados; el resto nunca sale |
| **Estados visibles** | Solo los legajos que están en alguno de estos estados salen por la API pública |
| **Mostrar documentos vinculados** | Expone los documentos públicos vinculados al legajo |
| **Mostrar expedientes vinculados** | Expone **solo número y carátula** de los expedientes vinculados, sin acceso al contenido |
| **Mostrar legajos relacionados** | Expone los legajos relacionados que también pertenezcan a familias públicas |

!!! tip "Los estados filtran en vivo"
    Solo los legajos en los **estados marcados** salen por la API publica. Un legajo que cambia a un estado **no** marcado **desaparece de lo público automáticamente**, sin ninguna acción manual. Es la forma natural de despublicar un legajo puntual: cambiarlo de estado.

!!! warning "Validaciones"
    - Los **campos públicos** deben ser un subconjunto de los campos definidos en el esquema de la familia.
    - Los **estados visibles** deben ser un subconjunto de los estados de la familia.
    - Si se borra un campo del esquema que estaba marcado como publico, el sistema lo saca de la configuración pública automáticamente.

---

## El acrónimo queda congelado

Las URLs públicas dependen del **acrónimo del municipio** (viaja en la ruta, ver [API pública](#api-publica)). Por eso, mientras el tenant tenga **algún tipo de documento público** o **alguna familia pública** activa, **no se puede cambiar el acrónimo** del municipio.

!!! danger "Error 409 al cambiar el acrónimo"
    Si se intenta cambiar el acrónimo de un municipio con publicaciones activas, el sistema responde:

    > *No se puede cambiar el acrónimo: el tenant tiene tipos de documento o familias de legajos públicos activos. Las URLs públicas dependen del acrónimo.*

    Para cambiar el acrónimo, primero hay que despublicar (apagar) las familias publicas. Los tipos de documento públicos, al ser irreversibles, hacen que esta decisión sea de fondo: elegir bien el acrónimo antes de publicar.

---

## Publicación de PDFs: viene lista de fábrica

El almacenamiento público donde se sirven los PDFs **viene habilitado de fábrica**: toda instancia nace con su espacio de publicación propio, creado automáticamente en el alta del municipio. El administrador **no tiene que configurar ni pedir nada** — alcanza con marcar un tipo de documento como público para que sus PDFs firmados empiecen a publicarse.

- Cuando se firma un documento de un tipo publico, el PDF oficial se copia automáticamente al espacio público y su `pdf_url` aparece en la API.
- Si un documento vinculado **no** es de tipo público, su `pdf_url` viene `null`: es el comportamiento esperado, no una falla.

!!! note "Auditoría"
    Todo cambio de visibilidad (crear un tipo público, prender/apagar una familia, editar su `public_config`) queda registrado en la auditoría del sistema, en la misma transacción que el cambio.

---

## API pública

La información publicada se consume por un **bloque de API de solo lectura** pensado para portales de transparencia, integraciones y consultas de la ciudadanía. Vive bajo el prefijo `/api/v1/public/{muni}/...`, donde `{muni}` es el **acrónimo del municipio** (en minúsculas).

!!! abstract "Qué necesita el equipo técnico del municipio para integrar"
    1. La **URL base** del ambiente (la entrega GDI en la puesta en marcha).
    2. La **API Key del municipio** (la entrega GDI por un canal seguro; nunca por mail junto con la URL).
    3. El **acrónimo** del municipio, que va en la ruta.
    4. Un cliente **server-to-server** (backend propio, no un navegador).

!!! warning "Requiere API Key del municipio (no es anónima)"
    Aunque la información sea publica, la API **no es anónima**: cada pedido debe incluir el header **`X-API-Key`** con una **clave de municipio**. No lleva `X-User-ID` (la clave es del municipio, no de un usuario). La clave debe corresponder al `{muni}` de la URL; si no coincide, la respuesta es **403**. Estas claves son server-to-server: **no deben viajar a un navegador** (por eso las respuestas se sirven como `Cache-Control: private`).

### Endpoints

| Método y ruta | Que devuelve |
|---------------|--------------|
| `GET /api/v1/public/{muni}/search?q=...` | Búsqueda combinada de documentos públicos + legajos públicos en un único listado |
| `GET /api/v1/public/{muni}/registries` | Familias de registro públicas del municipio, con sus campos públicos |
| `GET /api/v1/public/{muni}/registries/{code}/records` | Legajos públicos de la familia `code` (paginado) |
| `GET /api/v1/public/{muni}/records/{record_number}` | Detalle de un legajo público |
| `GET /api/v1/public/{muni}/documents/{document_id}/content` | Contenido (texto completo, en HTML) de un documento público, identificado por su `document_id` (UUID) |

**Parámetros y notas:**

- **`search`**: `q` obligatorio (mínimo 2 caracteres). Cada resultado es de tipo `document` (con `official_number`, `document_type`, `resume`, `snippet`, `pdf_url`, ...) o `record` (legajo, con `record_number`, `display_name`, `registry_code`, `fields`).
- **`registries/{code}/records`**: acepta `page` (default 1), `page_size` (default 20, tope 25: valores mayores se ajustan a 25 sin error) y `search` (opcional, min 2 caracteres: con menos, el filtro se ignora y se devuelve el listado completo). Una familia inexistente o no pública devuelve **404** (no distingue "no existe" de "privada").
- **`records/{record_number}`**: devuelve `record_number`, `display_name`, `state`, `registry` y los `fields` públicos; además `documents`, `cases` y `related_records` **solo** si la familia los habilitó. Un legajo que no existe, cuya familia no es pública, o cuyo estado no está en `visible_states`, devuelve **404**.
    - **Resumen de los vinculados:** cada `documents` incluye `resume` **solo si el documento es público** (mismo criterio que `pdf_url`); si no es público, `resume` viene `null`. Cada `related_records` incluye `resume` **solo si el legajo destino es público y navegable** (mismo criterio que `linked`); si no, `resume` viene `null`. Los `cases` (expedientes) **nunca** incluyen resumen: siguen devolviendo solo `case_number` y `reference`.
    - **`document_id` de los vinculados:** cada `documents` incluye además un `document_id` (UUID) **solo si el documento es público**; si no lo es, viene `null`. Ese identificador es el que se usa en el endpoint de contenido (abajo). Es la única forma de obtenerlo: la API nunca expone el UUID de un documento no público.
- **`documents/{document_id}/content`**: devuelve el **texto completo del documento en HTML**, además de `official_number`, `reference`, `document_type` y `signed_at`. El `document_id` es el UUID que trae el detalle de legajo (`documents[].document_id`). Solo responde para documentos **públicos y firmados**; para cualquier otro caso —no existe, no es público, no está firmado, o el `document_id` no es un UUID válido— devuelve **404** con el mismo cuerpo (`{"error": "Documento no encontrado"}`), sin distinguir el motivo. El PDF de ese mismo documento se sigue descargando por `pdf_url`; el endpoint de contenido es el complemento en texto (para indexar, mostrar en HTML, etc.).

### Ejemplos de uso

Listar las familias públicas del municipio:

```bash
curl -H "X-API-Key: $API_KEY" \
  "https://URL-BASE/api/v1/public/muni/registries"
```

```json
{
  "registries": [
    {
      "code": "NORMA",
      "name": "Normativa HCD",
      "description": "Registro de normativa emitida por el Honorable Concejo Deliberante",
      "fields": ["materia", "tipo_norma", "numero_norma", "fecha_sancion"]
    }
  ],
  "total": 1
}
```

Listar los legajos de una familia, paginados:

```bash
curl -H "X-API-Key: $API_KEY" \
  "https://URL-BASE/api/v1/public/muni/registries/NORMA/records?page=1&page_size=5"
```

```json
{
  "records": [
    {
      "record_number": "RLM-2026-00000036-MUNI-NORMA",
      "display_name": "Ordenanza 5383 - Regula contrataciones municipales",
      "state": "Vigente",
      "registry_code": "NORMA",
      "fields": {
        "materia": {"value": "Presupuesto"},
        "tipo_norma": {"value": "Ordenanza"},
        "numero_norma": {"value": "5383"}
      }
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 5,
  "total_pages": 2
}
```

Detalle de un legajo, con sus documentos públicos:

```bash
curl -H "X-API-Key: $API_KEY" \
  "https://URL-BASE/api/v1/public/muni/records/RLM-2026-00000036-MUNI-NORMA"
```

```json
{
  "record_number": "RLM-2026-00000036-MUNI-NORMA",
  "display_name": "Ordenanza 5383 - Regula contrataciones municipales",
  "state": "Vigente",
  "registry": {"code": "NORMA", "name": "Normativa HCD"},
  "fields": {
    "materia": {"value": "Presupuesto"},
    "tipo_norma": {"value": "Ordenanza"},
    "numero_norma": {"value": "5383"}
  },
  "documents": [
    {
      "official_number": "NORPU-2026-00001234-MUNI-HCD",
      "reference": "5383/26",
      "document_id": "07669375-29d9-4446-b18c-239e8038d60c",
      "pdf_url": "https://URL-PDF/NORPU-2026-00001234-MUNI-HCD.pdf",
      "resume": "Resumen del contenido generado automaticamente..."
    },
    {
      "official_number": "ANEXO-2026-00001235-MUNI-HCD",
      "reference": "Anexo interno",
      "document_id": null,
      "pdf_url": null,
      "resume": null
    }
  ]
}
```

!!! tip "pdf_url: null NO es un error"
    Un documento vinculado al legajo que **no** sea de tipo público aparece en la lista con `pdf_url: null` y `resume: null`. Es el comportamiento esperado: el legajo muestra que el documento existe, pero su contenido no es publico. El PDF de los documentos públicos se descarga directo de `pdf_url`, **sin API Key** (es un link público).

Contenido (texto completo en HTML) de un documento publico. El `document_id` sale del detalle de legajo de arriba (`documents[].document_id`):

```bash
curl -H "X-API-Key: $API_KEY" \
  "https://URL-BASE/api/v1/public/muni/documents/07669375-29d9-4446-b18c-239e8038d60c/content"
```

```json
{
  "document_id": "07669375-29d9-4446-b18c-239e8038d60c",
  "official_number": "NORPU-2026-00001234-MUNI-HCD",
  "reference": "5383/26",
  "document_type": {"name": "Norma Publicada", "acronym": "NORPU"},
  "content": {"html": "<div class=\"transcription\">...texto completo del documento...</div>", "format": "html"},
  "signed_at": "2026-07-21T18:57:14+00:00"
}
```

!!! tip "PDF y contenido son complementarios"
    El detalle de legajo entrega, para cada documento público, tanto el `pdf_url` (para descargar el PDF firmado) como el `document_id` (para pedir el texto en HTML por este endpoint). Sirven a fines distintos: el PDF es el documento oficial descargable; el contenido HTML es útil para indexar, buscar o mostrar el texto embebido en un portal sin abrir el PDF.

!!! warning "Sanitizar el HTML antes de mostrarlo en un navegador"
    El `content.html` es el texto del documento tal como quedo en el sistema; la API lo devuelve **sin sanitizar** (es una API server-to-server, no pensada para render directo en un browser). Si el portal del municipio lo va a inyectar en una página, **debe pasarlo antes por un sanitizador** (por ejemplo DOMPurify) — nunca hacer `dangerouslySetInnerHTML` / `innerHTML` con el HTML crudo. Es la misma precaución que con cualquier contenido de origen externo.

!!! info "Flujo típico de integración"
    1. `GET /registries` -> familias públicas del municipio.
    2. `GET /registries/{code}/records` -> legajos de una familia.
    3. `GET /records/{record_number}` -> detalle del legajo; de acá sale, por cada documento público, su `pdf_url` y su `document_id`.
    4. `GET /documents/{document_id}/content` -> texto completo en HTML de ese documento.

Búsqueda combinada:

```bash
curl -H "X-API-Key: $API_KEY" \
  "https://URL-BASE/api/v1/public/muni/search?q=ordenanza%205383"
```

Cada resultado trae `type` (`record` o `document`). Los resultados `document` incluyen además `linked_records`, con los legajos públicos a los que está vinculado el documento.

### Respuestas de error

| Caso | Código | Cuerpo |
|------|--------|--------|
| Sin header `X-API-Key` | 401 | `{"error": "X-API-Key requerido"}` |
| Clave inválida, inactiva, vencida o revocada | 401 | `{"error": "API Key invalida"}` (mensaje genérico a propósito) |
| Clave válida pero de **otro** municipio | 403 | `{"error": "API Key no valida para este municipio"}` |
| Familia inexistente o no pública | 404 | `{"error": "Familia no encontrada"}` |
| Legajo inexistente, no público o en estado no visible | 404 | `{"error": "Legajo no encontrado"}` |
| Documento inexistente, no público, sin firmar, o `document_id` mal formado | 404 | `{"error": "Documento no encontrado"}` |
| `q` de búsqueda con menos de 2 caracteres | 400 | `{"error": "q requerido (min 2 caracteres)"}` |
| Exceso de consultas | 429 | `{"error": "Rate limit exceeded. Retry after 60s"}` |

!!! tip "Buenas prácticas de integración"
    - **Cachear en el servidor** las respuestas hasta 60 segundos (las respuestas ya lo indican con `Cache-Control: private, max-age=60`). Un portal de transparencia no necesita pegarle a la API en cada visita.
    - Ante un **429**, esperar 60 segundos y reintentar: es la protección contra abuso funcionando, no una falla.
    - La API Key vive **solo en el backend** del municipio. Si aparece en el código del frontend, en un repositorio o en un navegador, hay que pedir a GDI que la **rote** (revocar y emitir una nueva).
    - Al reportar un problema a GDI, enviar URL completa, fecha/hora, código HTTP y cuerpo de la respuesta. **Nunca incluir la API Key** en el reporte.

### URLs de los PDFs

Los PDFs públicos se sirven con una URL plana y estable, cuyo nombre de archivo es el **número oficial** del documento:

```
{url-base-de-publicacion}/{numero_oficial}.pdf
```

La URL base de publicación depende del ambiente; el integrador **no necesita construirla**: siempre llega completa en el campo `pdf_url` de las respuestas. La URL se incluye solo para documentos de **tipo público**; para el resto el campo `pdf_url` viene `null`. La descarga del PDF **no requiere API Key**.

---

## Seguridad del bloque público

El bloque público se diseñó con la seguridad como prioridad. Sin entrar en detalles de implementación, estas son las garantías que ofrece:

| Garantía | Que significa |
|----------|---------------|
| **Acceso autenticado y aislado** | Cada pedido se valida contra una clave de municipio y queda acotado a ese municipio: no hay forma de acceder a la información de otro (403 si la clave no corresponde) |
| **Solo lectura y protegida contra abuso** | La API no permite modificar nada y limita la cantidad de consultas por origen; los excesos se rechazan automáticamente |
| **Solo se expone lo que marcás** | Únicamente salen los campos que el administrador tilda explícitamente en la configuración publica; el resto nunca se publica |
| **Nunca expone reservados** | Documentos y expedientes reservados jamás aparecen: se filtran en origen, antes de armar la respuesta |
| **No revela la estructura interna** | La respuesta nunca incluye datos internos del sistema ni de la base de datos |

!!! info "Búsqueda inteligente"
    La búsqueda pública combina coincidencia por palabras con una búsqueda que entiende el **significado** de la consulta, para devolver resultados relevantes aunque no coincidan exactamente los términos. Si el servicio inteligente no está disponible en un momento dado, la búsqueda sigue funcionando de forma transparente por coincidencia de texto.

