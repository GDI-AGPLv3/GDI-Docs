# Documentos y Legajos Públicos

La **visibilidad pública** es la tercera pata del modelo de visibilidad del sistema. Junto con **Interno** y **Reservado**, permite abrir informacion a la ciudadania **sin necesidad de login**: cualquier persona en internet puede consultar los documentos oficiales y los legajos que el municipio decida publicar.

!!! abstract "La idea en una frase"
    La publicidad se define **por TIPO** (no item por item), igual que la reserva. Un administrador marca un **Tipo de Documento** como *Público* o una **Familia de Registro** como *Pública*; a partir de ahi, todos los items de ese tipo quedan expuestos por una API publica de solo lectura, con reglas fijas y sin dar permisos a mano.

---

## Las tres visibilidades

Cada Tipo de Documento tiene un campo `visibility` con uno de tres valores:

| Visibilidad | Quien lo ve | Donde se configura |
|-------------|-------------|--------------------|
| **Interno** | Visibilidad estandar del municipio (conducta actual por defecto) | Tipos de Documento / Tipos de Expediente |
| **Reservado** | Solo firmantes, creador y responsables directos (ver [Reservados](reservados.md)) | Tipos de Documento / Tipos de Expediente |
| **Público** | **Cualquiera en internet, sin login** | Solo Tipos de Documento |

!!! warning "Los expedientes NUNCA son publicos"
    La opcion *Público* **solo existe para Tipos de Documento**. Los **Tipos de Expediente** admiten unicamente *Interno* o *Reservado* (decision de diseño D8). El BackOffice rechaza con error cualquier intento de crear o editar un tipo de expediente como publico.

Los **legajos** (RLM) tienen su propio mecanismo de publicacion, a nivel de **Familia de Registro** (ver [Familias públicas](#familias-de-registro-publicas) mas abajo).

---

## Publicar un Tipo de Documento

Al **crear un tipo de documento propio** (boton *Nuevo tipo propio* en [Tipos de Documentos](tipos-de-documentos.md)), el modal incluye un selector obligatorio de **Visibilidad** con las tres opciones:

| Opcion | Descripcion que muestra el selector |
|--------|-------------------------------------|
| **Interno** | *Visibilidad estandar del municipio (conducta actual).* |
| **Reservado** | *Confidencial e irreversible. Solo firmantes/responsables directos podran verlo.* |
| **Público** | *Sin login, accesible por cualquiera en internet. Irreversible.* |

Al elegir **Público** y presionar *Crear tipo*, el sistema pide una **confirmacion explicita** antes de dar de alta el tipo:

!!! quote "Dialogo de confirmacion — Crear tipo como Público"
    Este tipo de documento va a nacer como PUBLICO.

    Esto es IRREVERSIBLE: no se va a poder volver a "Interno" despues de creado. Los PDFs firmados de este tipo van a quedar accesibles por cualquier persona en internet, SIN necesidad de login. Una vez publicado un PDF, aunque se borre despues puede seguir cacheado o indexado por buscadores. Asegurate de que este tipo de documento nunca vaya a contener datos sensibles (DNI, CBU, domicilios, etc.).

    **Botones:** *Cancelar* / *Si, crear como Público*

### Que se publica exactamente

Cuando un documento de un tipo publico se **firma**, su **PDF oficial** se copia automaticamente a un bucket publico y queda accesible por una URL estable. Solo se publican **documentos oficiales firmados** (`signed_at` presente): un borrador nunca sale a internet.

!!! danger "Irreversibilidad y prudencia"
    - La visibilidad de un tipo de documento se define **una sola vez, al crearlo**, y es **irreversible**: un tipo publico no se puede volver a interno.
    - En el detalle del tipo la visibilidad aparece como una etiqueta de **solo lectura** (*"La visibilidad se define al crear el tipo y no se puede cambiar."*).
    - Una vez que un PDF se publico, aunque despues se despublique o borre, **puede seguir cacheado o indexado** por buscadores. Nunca marques como publico un tipo que pueda contener datos personales o sensibles.

!!! info "Solo tipos virgenes"
    Por debajo, el unico cambio de visibilidad que el sistema acepta por edicion es `interno → publico` (o `interno → reservado`) y **solo si el tipo no tiene ningun documento creado todavia**. En la practica esto se resuelve eligiendo la visibilidad en el momento del alta.

---

## Familias de Registro públicas

Los legajos se publican a nivel de **Familia de Registro**. En el detalle de una familia ([Familias de Registro](familias-registro.md)) hay una tarjeta **"Publicación Pública"**.

!!! quote "Publicación Pública"
    *Expone los legajos de esta familia sin login, en internet. Reversible en cualquier momento.*

A diferencia de los tipos de documento, **publicar una familia es reversible** (decision D4): se puede prender y apagar cuando se quiera. Al apagarlo, la API publica deja de servir esos legajos de inmediato.

### Configuracion de una familia publica

Al activar el toggle **"Familia pública"** el sistema pide confirmacion:

!!! quote "Dialogo — Publicar familia de legajos"
    Los legajos de esta familia van a ser visibles publicamente en internet, sin necesidad de login, mostrando solo los campos y estados que marques a continuacion.

    Podes desactivarlo en cualquier momento (es reversible): al apagarlo, la API publica deja de servir estos legajos.

    **Botones:** *Cancelar* / *Sí, activar*

Con la familia publica, se configura **exactamente que se expone** (`public_config`):

| Opcion | Que controla |
|--------|--------------|
| **Campos públicos** | Subconjunto de los campos del esquema de datos de la familia que se muestran. Solo se publican los campos tildados; el resto nunca sale |
| **Estados visibles** | Solo los legajos que estan en alguno de estos estados salen por la API publica |
| **Mostrar documentos vinculados** | Expone los documentos publicos vinculados al legajo |
| **Mostrar expedientes vinculados** | Expone **solo numero y caratula** de los expedientes vinculados, sin acceso al contenido |
| **Mostrar legajos relacionados** | Expone los legajos relacionados que tambien pertenezcan a familias publicas |

!!! tip "Los estados filtran en vivo"
    Solo los legajos en los **estados marcados** salen por la API publica. Un legajo que cambia a un estado **no** marcado **desaparece de lo publico automaticamente**, sin ninguna accion manual. Es la forma natural de despublicar un legajo puntual: cambiarlo de estado.

!!! warning "Validaciones"
    - Los **campos públicos** deben ser un subconjunto de los campos definidos en el esquema de la familia.
    - Los **estados visibles** deben ser un subconjunto de los estados de la familia.
    - Si se borra un campo del esquema que estaba marcado como publico, el sistema lo saca de la configuracion publica automaticamente.

---

## El acronimo queda congelado

Las URLs publicas dependen del **acronimo del municipio** (viaja en la ruta, ver [API pública](#api-publica)). Por eso, mientras el tenant tenga **algun tipo de documento publico** o **alguna familia publica** activa, **no se puede cambiar el acronimo** del municipio.

!!! danger "Error 409 al cambiar el acronimo"
    Si se intenta cambiar el acronimo de un municipio con publicaciones activas, el sistema responde:

    > *No se puede cambiar el acronimo: el tenant tiene tipos de documento o familias de legajos publicos activos (GDI-098). Las URLs publicas dependen del acronimo.*

    Para cambiar el acronimo, primero hay que despublicar (apagar) las familias publicas. Los tipos de documento publicos, al ser irreversibles, hacen que esta decision sea de fondo: elegir bien el acronimo antes de publicar.

---

## Requisito operativo: bucket publico

La publicacion de PDFs requiere que el tenant tenga configurado un **bucket R2 publico** (`settings.bucket_publico`) y el ruteo de dominio en Cloudflare. Esto **no se configura desde el BackOffice**: es parte del alta / aprovisionamiento del cliente (DevOps).

- Si `bucket_publico` **no** esta configurado (`NULL`), la feature esta **apagada** para ese tenant: la copia del PDF publico es un *no-op* silencioso y las URLs de PDF no se generan (el resto de la informacion publica sigue disponible, solo sin link al PDF).
- Marcar tipos o familias como publicos **no rompe nada** si el bucket no esta: simplemente no habra PDFs publicados hasta que DevOps active el bucket.

!!! note "Auditoria"
    Todo cambio de visibilidad (crear un tipo publico, prender/apagar una familia, editar su `public_config`) queda registrado en la auditoria del sistema, en la misma transaccion que el cambio (D18).

---

## API pública

La informacion publicada se consume por un **bloque de API de solo lectura** pensado para portales de transparencia, integraciones y consultas de la ciudadania. Vive bajo el prefijo `/api/v1/public/{muni}/...`, donde `{muni}` es el **acronimo del municipio**.

!!! warning "Requiere API Key del municipio (no es anonima)"
    Aunque la informacion sea publica, la API **no es anonima**: cada pedido debe incluir el header **`X-API-Key`** con una **clave de municipio** (GDI-112). No lleva `X-User-ID` (la clave es del municipio, no de un usuario). La clave debe corresponder al `{muni}` de la URL; si no coincide, la respuesta es **403**. Estas claves son server-to-server: **no deben viajar a un navegador** (por eso las respuestas se sirven como `Cache-Control: private`).

### Endpoints

| Metodo y ruta | Que devuelve |
|---------------|--------------|
| `GET /api/v1/public/{muni}/search?q=...` | Busqueda combinada de documentos publicos + legajos publicos en un unico listado |
| `GET /api/v1/public/{muni}/registries` | Familias de registro publicas del municipio, con sus campos publicos |
| `GET /api/v1/public/{muni}/registries/{code}/records` | Legajos publicos de la familia `code` (paginado) |
| `GET /api/v1/public/{muni}/records/{record_number}` | Detalle de un legajo publico |

**Parametros y notas:**

- **`search`**: `q` obligatorio (minimo 2 caracteres). Cada resultado es de tipo `document` (con `official_number`, `document_type`, `resume`, `snippet`, `pdf_url`, ...) o `record` (legajo, con `record_number`, `display_name`, `registry_code`, `fields`).
- **`registries/{code}/records`**: acepta `page` (default 1), `page_size` (default 20, tope 25) y `search` (opcional, min 2 caracteres). Una familia inexistente o no publica devuelve **404** (no distingue "no existe" de "privada").
- **`records/{record_number}`**: devuelve `record_number`, `display_name`, `state`, `registry` y los `fields` publicos; ademas `documents`, `cases` y `related_records` **solo** si la familia los habilito. Un legajo que no existe, cuya familia no es publica, o cuyo estado no esta en `visible_states`, devuelve **404**.

### URLs de los PDFs

Los PDFs publicos se sirven con una URL plana y estable:

```
https://public.gdilatam.com/{numero_oficial}.pdf
```

El mapeo dominio → bucket por municipio lo resuelve Cloudflare. La URL solo se incluye en la respuesta si el tipo del documento es publico **y** el tenant tiene `bucket_publico` configurado; si no, el campo `pdf_url` viene `null`.

---

## Seguridad del bloque publico

El bloque publico esta blindado por varias capas (todas activas en la implementacion GDI-098 / GDI-112):

| Capa | Comportamiento |
|------|----------------|
| **Autenticacion** | `X-API-Key` de municipio, validada contra el acronimo de la URL. Aislamiento cross-tenant (403 si la clave es de otro municipio) |
| **Rate limit por IP** | Por minuto y por IP real (`fly-client-ip`), **fail-closed** (si el limitador no responde, bloquea): 30/min en busqueda, 60/min en listados → **429** |
| **Cupo de IA** | La busqueda semantica tiene un cupo diario por municipio; si se agota o el servicio no responde, **degrada** a busqueda lexica (nunca falla con error) |
| **Whitelist de campos** | Solo se sirven los campos marcados en `public_config`; los nombres se validan con `^[a-z0-9_]{1,64}$` antes de tocar la base (previene inyeccion) |
| **Nunca expone reservados** | Documentos y expedientes reservados jamas aparecen: se filtran en la propia consulta, no despues |
| **No expone el schema** | El `schema_name` del tenant se resuelve del lado del servidor y nunca se devuelve |

!!! info "Busqueda inteligente"
    La busqueda publica es **hibrida**: combina busqueda semantica (embeddings + RAG) con busqueda lexica, fusionadas con Reciprocal Rank Fusion (RRF). Si no hay cupo de IA disponible, degrada de forma transparente a busqueda lexica.

---

!!! example "Estado de la funcionalidad"
    El comportamiento descripto en esta pagina corresponde al **modelo diseñado** de documentos y legajos publicos (GDI-098, con el endurecimiento de autenticacion GDI-112). La implementacion se esta verificando en el ambiente de desarrollo (DEV) durante julio de 2026. Requiere ademas el aprovisionamiento del bucket publico R2 y el ruteo de dominio en Cloudflare por parte de DevOps. Si detectas una diferencia entre lo documentado aca y lo que ves en la aplicacion, prevalece este modelo como comportamiento esperado.
