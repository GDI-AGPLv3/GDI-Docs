# Documentos

Creacion y **firma electronica**: el documento nace y se firma con el sello del ciudadano, para quedar numerado oficialmente. No hay borradores por API.

!!! info "La firma es asincronica (desde 3.12.0)"
    El alta responde **`202 Accepted` al instante** y la firma se procesa a continuacion.
    El numero oficial y el link al PDF **no vienen en esa respuesta**: llegan por
    **webhook** (`documents.signed`), en segundos.

    Antes el pedido se quedaba esperando a que la firma terminara, lo que bajo carga
    podia superar los 30 segundos y hacer que el portal cortara por timeout un
    documento que en realidad se estaba firmando bien.

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

## Campos de un formulario (FFCC)

```
GET /api/v1/tad/document-types/{id}/fields
```

**Respuesta `200 OK`:**

```json
{
  "document_type_id": 16,
  "field_definitions": [
    {"name": "monto", "type": "number", "label": "Monto", "required": true},
    {"name": "fecha_pago", "type": "date", "label": "Fecha de pago", "required": true},
    {"name": "comprobante", "type": "file", "label": "Comprobante", "required": false}
  ]
}
```

`404` si el tipo no existe, no esta habilitado para TAD o no tiene formulario.

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

    Ver [Webhook de notificaciones](webhook.md).

!!! tip "Reintentos del portal"
    Repetir el mismo `POST` **no genera una segunda firma**: si ya hay una encolada
    para ese documento, se devuelve la misma sesion. Es seguro reintentar ante un
    timeout de red.

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

El HTML se sanitiza y se renderiza en la plantilla oficial del municipio.

### Variante FFCC (formulario controlado)

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/documents" \
  -H "X-API-Key: tu-api-key-tad" \
  -H "X-Citizen-ID: 27333444556" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "PAGO",
    "reference": "Pago de tasa municipal",
    "form_data": {"monto": 15300.50, "fecha_pago": "2026-07-24"}
  }'
```

Validaciones sobre `form_data`:

- Campos `required: true` faltantes → `400` (`"El campo 'Monto' es requerido"`).
- Tipo de dato incorrecto → `400` (`"El campo 'Monto' debe ser un numero"`; las fechas van en formato `YYYY-MM-DD`).
- Campos no definidos en el esquema → `400` (`"Campos no definidos en el formulario: ['x']"`). Enviar exactamente los campos de `field_definitions`.
- Controles de sanidad (aplican aunque el campo no declare limites): los `number` deben ser finitos y de magnitud razonable; los textos tienen un tope de largo; las fechas deben ser reales (`2026-13-45` se rechaza) y de un anio plausible. Si el campo define `min`/`max`/`max_length` propios, mandan esos.
- Campos `type: "file"`: **no se pueden completar por API** — enviar `null` u omitirlos (`400` si traen valor). Para enviar un archivo, usar un tipo de documento `Importado`.
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
