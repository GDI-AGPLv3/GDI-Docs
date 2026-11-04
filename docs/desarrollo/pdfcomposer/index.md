# PDFComposer

**Servicio que genera los PDF de GDI** a partir de plantillas HTML: documentos, carátulas,
pases, notas, informes de legajo y la hoja informativa de un PDF importado. No guarda nada: recibe
datos y devuelve un PDF.

| Propiedad | Valor |
|-----------|-------|
| Puerto | `:8002` (desarrollo) |
| Framework | FastAPI |
| Motor PDF | WeasyPrint (en el mismo contenedor) |
| Plantillas | Jinja2, una por tipo de documento (`app/templates/`) |
| Firmas y certificación | pyHanko (revisiones incrementales y detección de DocMDP) |
| Autenticación | Header `X-API-Key` (todos los endpoints menos `/` y `/health`) |
| Cliente | Solo el Backend |

La versión vigente sale de `app/version.py`. La lista de endpoints sale de `main.py`.

## Endpoints

Todos reciben `multipart/form-data` y devuelven el PDF en el body (`application/pdf`), con nombre
UUID. Los PDF finales (no las vistas previas) traen además el header `X-PDF-SHA256`.

| Endpoint | Qué genera |
|----------|------------|
| `POST /preview-pdf/` | Vista previa de un documento, con marca de agua "PREVISUALIZACIÓN" |
| `POST /generate-pdf/` | Documento final, sin marca de agua. Acepta un PDF anexo y adjuntos embebidos |
| `POST /create-case/` | Carátula de expediente |
| `POST /move/` | Pase de expediente |
| `POST /import/` | PDF externo + hoja informativa de GDI al final |
| `POST /embed-files/` | Agrega adjuntos embebidos a un PDF importado |
| `POST /note-preview/` | Vista previa de una nota, con marca de agua |
| `POST /note/` | Nota final |
| `POST /ifrlm/` | Informe de legajo |
| `GET /health` | Estado básico, sin API Key |
| `GET /health/details` | Estado con prueba de WeasyPrint |
| `GET /cache/stats` | Estadísticas de la caché de logos (por proceso) |

## Topes de tamaño

| Qué | Tope | Error |
|-----|------|-------|
| Pedido entero (HTML + PDF anexo + adjuntos) | 30 MB (`MAX_REQUEST_BODY_SIZE_MB`) | `413` antes de leer |
| Un campo de texto del formulario (por ejemplo, el HTML) | 25 MB (`MAX_FORM_FIELD_SIZE_MB`) | `413` |
| PDF a importar (`/import/`) | 25 MB | `413` |
| PDF anexo de `/generate-pdf/` | 25 MB | `413` |
| Un adjunto embebido | 20 MB | `413` |
| Suma de adjuntos embebidos | 20 MB | `413` |
| PDF importado + sus adjuntos (`/embed-files/`) | 25 MB | `413` |
| Logo | 2 MB | El PDF sale sin logo |

El tope de 30 MB del pedido es el mismo que usa el Backend al llamar a PDFComposer. Un middleware
lo controla antes de leer el body: si `Content-Length` lo pasa, responde `413` enseguida. Si el
cliente no declara el tamaño, el middleware corta apenas lo leído pasa el tope.

!!! note "Por qué 25 MB para un campo de texto"
    Starlette corta por defecto cada campo del formulario en 1 MB. Un documento con una imagen
    de ~1 MB (que viaja en base64 dentro del HTML) no entraba. PDFComposer lee el formulario
    con `max_part_size` de 25 MB.

## /import/: PDF externo

`/import/` recibe un PDF de afuera, cuenta sus páginas y le agrega al final la hoja informativa
de GDI.

**Parámetros (Form Data):** `pdf_file` (obligatorio), `NameAcronyType`, `document_type`,
`reference` (obligatorios), `urlLogo` y `frase_anual` (opcionales).

### Cómo agrega la hoja

| El PDF trae | Qué hace PDFComposer |
|-------------|----------------------|
| Sin firmas | Reescribe el PDF con la hoja al final (PyMuPDF) |
| Firmas comunes | Agrega la hoja como **revisión incremental** (pyHanko): el original queda igual, byte a byte, y las firmas siguen válidas |
| Firma de certificación (DocMDP) íntegra | **No lo toca**: devuelve los bytes de entrada, sin hoja |
| Firmas y la revisión incremental falla | Rechaza con `422 IMPORT_INCREMENTAL_FAILED`. Nunca devuelve un PDF reescrito con las firmas rotas |

La revisión incremental funciona también con **árboles de páginas anidados** (`/Pages` dentro de
`/Pages`, como los que arman Acrobat o los generadores de oficina). PDFComposer agrega la página
con su propia función (`_append_page` en `app/services/import_merge.py`) y actualiza el `/Count`
de cada nivel. La función de pyHanko fallaba con esos árboles.

### Header X-GDI-Certified

Toda respuesta `200` de `/import/` trae el header `X-GDI-Certified`:

| Valor | Qué significa |
|-------|---------------|
| `false` | PDFComposer agregó la hoja informativa |
| `true` | El PDF trae una firma de certificación íntegra y volvió **sin tocar** |

Con `true`, el Backend guarda el PDF tal cual y lo numera sin pasar por Notary (Notary lo
rechazaría con `422 PDF_CERTIFIED`). La marca queda en la base, en
`document_draft.certified_pdf_sha256` (ver [Schema Municipio](../database/schema-municipio.md)).

### Validación estricta de la certificación

Un PDF que **parece** certificado no alcanza. Una firma copiada de otro PDF, o un contenido
cambiado con una revisión posterior, tendría la misma estructura. Por eso, antes de devolverlo
sin tocar, PDFComposer valida cada firma de certificación con pyHanko
(`validate_certification_integrity` en `app/services/certification.py`). Tienen que cumplirse
las 4 condiciones:

1. `intact`: el hash del `/ByteRange` coincide con lo firmado.
2. `valid`: la firma criptográfica es válida.
3. La firma cubre el archivo entero o la revisión entera (`ENTIRE_FILE` o `ENTIRE_REVISION`).
4. `docmdp_ok`: las revisiones posteriores respetan el nivel `P`.

La validación no revisa **quién** firmó (no usa raíces de confianza ni red). Revisa que la
firma esté sana.

Detalles de la validación:

- **Igual que Acrobat.** La política de cambios es la estándar de pyHanko con un solo cambio:
  acepta una firma de aprobación visible nueva después de certificar (P=2 o P=3). Es el caso
  normal de un convenio certificado que otro firma después. Por la misma razón pasa la
  "Sneaky Signature", como en Acrobat. Siguen rechazados: firma copiada, contenido cambiado,
  PDF reescrito o comprimido y "Evil Annotation".
- **SHA-1 permitido.** pyHanko rechaza SHA-1 por defecto, pero Acrobat lo sigue validando.
  PDFComposer acepta certificaciones firmadas con SHA-1. MD2 y MD5 siguen rechazados.
- **Lectura estricta.** La validación lee siempre en modo estricto, como Notary.

Si falla cualquier condición, o la validación tira una excepción, la respuesta es
`422 IMPORT_CERTIFICATION_BROKEN`.

### Errores de /import/

| Código | `error_code` | Cuándo |
|--------|--------------|--------|
| 400 | - | El archivo no empieza con `%PDF-` |
| 413 | - | El PDF pasa de 25 MB |
| 422 | `IMPORT_INCREMENTAL_FAILED` | El PDF tiene firmas y no se pudo agregar la hoja sin invalidarlas |
| 422 | `IMPORT_CERTIFICATION_BROKEN` | Parece certificado, pero la firma de certificación no está íntegra |
| 422 | `IMPORT_CERTIFICATION_INCONSISTENT` | `/Perms/DocMDP` que ninguna firma respalda, con otras firmas |
| 422 | `IMPORT_PDF_ENCRYPTED_PASSWORD` | El PDF pide contraseña para abrirse |
| 422 | `IMPORT_SIGNATURES_UNREADABLE` | Hay firmas que no se pueden leer |

```json
{
  "detail": {
    "error_code": "IMPORT_CERTIFICATION_BROKEN",
    "firmas": 1,
    "message": "..."
  }
}
```

Dos casos más:

- **Firmas ilegibles en modo estricto.** `/import/` reintenta en modo permisivo, solo para
  detectar. Si encuentra certificación, sigue como certificado (y la validación estricta
  decide). Si encuentra alguna firma, rechaza con `IMPORT_SIGNATURES_UNREADABLE`. Si no
  encuentra nada, reescribe como un PDF sin firmas.
- **`/Perms/DocMDP` sin ninguna firma.** Reescribe el PDF y borra `/Perms`. Si no lo borrará,
  Notary no podría firmarlo nunca.

## /embed-files/: adjuntos en un importado

`/embed-files/` agrega adjuntos embebidos (`/EmbeddedFiles`) a un PDF importado, que ya trae su
hoja informativa. No toca el contenido de las páginas.

**Parámetros (Form Data):**

| Parámetro | Obligatorio | Descripción |
|-----------|-------------|-------------|
| `pdf_file` | Sí | El PDF importado |
| `embedded_files` | Sí (al menos 1) | Archivos a embeber. Campo repetido, igual que en `/generate-pdf/` |

Reglas:

- Extensiones permitidas: `pdf`, `xls`, `xlsx`, `doc`, `docx`, `odt`, `ods`, `csv`, `txt`,
  `png`, `jpg`, `jpeg`, `dxf`. El contenido tiene que coincidir con la extensión (magic bytes).
- Conserva los adjuntos que el PDF ya traía (por ejemplo, el XML de una factura PDF/A-3).
  Un nombre nuevo que choca con uno existente se renombra con `_2`, `_3`…
- Si el PDF trae firmas comunes, los adjuntos van como revisión incremental y las firmas siguen
  válidas.

| Código | `error_code` | Cuándo |
|--------|--------------|--------|
| 400 | - | PDF inválido, sin adjuntos o con un adjunto que no pasa la validación de contenido |
| 413 | - | Un adjunto > 20 MB, adjuntos > 20 MB o PDF + adjuntos > 25 MB |
| 422 | `EMBED_CERTIFIED_PDF` | El PDF trae firma de certificación: agregar archivos la rompe en cualquier nivel `P` |
| 422 | `EMBED_CERTIFICATION_INCONSISTENT` | `/Perms/DocMDP` que ninguna firma respalda |
| 422 | `EMBED_PDF_ENCRYPTED_PASSWORD` | El PDF pide contraseña para abrirse |
| 422 | `EMBED_SIGNATURES_UNREADABLE` | Hay firmas que no se pueden leer |
| 422 | `EMBED_INCREMENTAL_FAILED` | El PDF tiene firmas y no se pudieron agregar los adjuntos sin invalidarlas |

Acá no hay reintento permisivo: el PDF que llega ya pasó por `/import/`.

## La regla de certificación

PDFComposer y [Notary](../notary/validaciones.md#control-de-certificacion-docmdp) usan la
**misma regla** para decidir si un PDF está certificado. Está escrita dos veces, una en cada
servicio (`app/services/certification.py` y `app/certification.py`). Si se cambia una copia, se
cambia la otra.

Resumen: la función `detect_certification` devuelve uno de 7 estados (`none`, `signed`,
`certified`, `orphan_perms`, `inconsistent`, `unreadable`, `encrypted_password`).

## PDF encriptado

Un PDF encriptado con **contraseña de dueño** (sin contraseña de apertura) se abre con
`decrypt("")`. Si trae una firma común, la revisión incremental vuelve a encriptar con
`encrypt("")`. Así el documento sale como llegó. Un PDF que pide contraseña para abrirse recibe
`422 IMPORT_PDF_ENCRYPTED_PASSWORD` o `422 EMBED_PDF_ENCRYPTED_PASSWORD`.

## Logo

El parámetro `urlLogo` acepta dos formas:

| Forma | Qué hace |
|-------|----------|
| `https://...` o `http://...` | Descarga el logo, con control SSRF y caché por proceso |
| `data:image/png;base64,...` | Usa el logo tal cual, sin red |

El `data:` URI sirve para el logo por defecto de un municipio sin logo propio: anda sin bucket
ni internet. Las dos formas siguen las mismas reglas:

- tipos permitidos: `image/png`, `image/jpeg`, `image/jpg`, `image/svg+xml`, `image/webp`,
  `image/gif`;
- hasta 2 MB;
- en un `data:` URI, el base64 tiene que ser válido.

Si el logo no cumple, el PDF sale sin logo (queda un warning en el log).

## Protección SSRF

Antes de descargar un logo o una imagen, `validate_url_safety` (en
`app/services/pdf_service.py`) revisa la URL:

1. Solo acepta `http` y `https`.
2. Rechaza hostnames bloqueados y los que terminan en `.internal`.
3. Resuelve el hostname y revisa cada IP. Rechaza loopback, link-local y `0.0.0.0` siempre.
   Rechaza IP privadas o reservadas, salvo que el host esté en `SSRF_ALLOWED_PRIVATE_HOSTS`.
4. Salvo para los hosts de confianza, fija la IP resuelta para la descarga. Así un cambio de DNS
   entre el control y la descarga no lleva a otra IP.

Una IPv6 **IPv4-mapped** (`::ffff:a.b.c.d`) se revisa dos veces: como IPv6 y como la IPv4 que
lleva adentro. Ejemplo: `::ffff:127.0.0.1` es loopback, aunque `is_loopback` de la IPv6 dé
`False`. Sin este doble control, esa dirección pasaba.

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `API_KEY` | (requerida) | API Key de autenticación |
| `MAX_REQUEST_BODY_SIZE_MB` | `30` | Tope del pedido entero |
| `MAX_FORM_FIELD_SIZE_MB` | `25` | Tope de un campo de texto del formulario |
| `PDF_MAX_CONCURRENCY` | `2` | PDF que se generan a la vez por proceso |
| `PDF_MAX_QUEUE` | `30` | Pedidos en curso o en espera por proceso. Al llegar al tope, responde `503` |
| `SSRF_ALLOWED_PRIVATE_HOSTS` | (vacío) | Nombres de host que pueden resolver a IP privada (solo nombres, no IP) |
