# Documentos

**20 endpoints** para gestión de documentos (más 4 de vinculación a expedientes documentados en [Expedientes](expedientes.md)).

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID` salvo que se indique lo contrario.

---

## Lectura

### Buscar documentos

```
GET /api/v1/documents/search
```

Busca documentos con filtros opcionales. Soporta paginación.

**Parámetros query:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | int | `1` | Número de página |
| `page_size` | int | `20` | Resultados por página (max `100`) |
| `search` | string | - | Busca por `document_number`. `%` y `_` cuentan como letras, no como comodines |
| `status` | string | - | Filtrar por estado visual: `"En edición"`, `"Firmar ahora"`, `"En proceso de firma"`, `"Firmado"` |
| `document_type` | string | - | Filtrar por acrónimo del tipo: `INF`, `DICT`, etc. |
| `case_id` | string | - | Filtrar por expediente |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/search?status=signed&document_type=INF&page=1&page_size=10" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "documents": [
    {
      "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "document_number": "IF-2025-00012-SMG-ADGEN",
      "document_type": "INF",
      "reference": "Informe tecnico sobre habilitacion comercial",
      "status": "signed",
      "created_at": "2025-06-16T09:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

### Documentos pendientes de firma

```
GET /api/v1/documents/pending-signatures
```

Devuelve los documentos que el usuario actual tiene pendientes de firma.

!!! warning "X-User-ID requerido"
    Este endpoint requiere `X-User-ID` obligatoriamente para identificar al firmante.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/pending-signatures" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "documents": [
    {
      "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
      "document_number": null,
      "document_type": "DICT",
      "reference": "Dictamen legal sobre habilitacion",
      "status": "sent_to_sign",
      "requested_at": "2025-06-20T14:00:00Z",
      "requested_by": "Maria Garcia"
    }
  ]
}
```

---

### Detalle de documento

```
GET /api/v1/documents/{document_id}
```

Devuelve la información completa de un documento.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

!!! info "X-User-ID opcional"
    Se requiere `X-User-ID` para acceder a documentos que están en proceso de firma. Para documentos en otros estados, es opcional.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/c3d4e5f6-a7b8-9012-cdef-123456789012" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "state_category": "signing",
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "status": "signed",
  "details": { "...": "datos del documento segun su estado" },
  "timestamp": "2026-11-04T10:30:00",
  "linked_case": null,
  "certified_origin": false
}
```

| Campo | Descripción |
|-------|-------------|
| `state_category` | `editing` (borrador o rechazado) o `signing` (en firma o firmado) |
| `details` | Los datos del documento. Cambian según `state_category` |
| `linked_case` | Expediente vinculado, o `null` |
| `certified_origin` | `true` si es un PDF importado **certificado de origen** (ver abajo) |

!!! info "Certificado de origen (`certified_origin`)"
    Un certificado de origen es un PDF importado que ya trae una firma de certificación
    (por ejemplo, de un escribano). GDI lo guarda sin tocarlo: no le agrega la hoja de firma
    ni adjuntos, y **el número oficial no se imprime en el PDF**. El número se lee de la API.
    En la ficha de firma, cada firmante trae `signed_with_provider`: `"conformidad"` quiere
    decir que dio su conformidad sin firmar el PDF.

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | `document_id inválido (se espera UUID)` |
| `404` | Documento no encontrado |
| `403` | Sin permisos para ver el documento |

---

### Contenido HTML

```
GET /api/v1/documents/{document_id}/content
```

Devuelve el contenido HTML de un documento oficial firmado.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

!!! warning "Solo documentos oficiales firmados"
    Este endpoint solo funciona para documentos que ya fueron firmados y tienen número oficial. Los borradores no tienen contenido disponible por esta vía.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/c3d4e5f6-a7b8-9012-cdef-123456789012/content" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "document_number": "IF-2025-00012-SMG-ADGEN",
  "content": "<html><body><h1>Informe Tecnico</h1><p>Se procede a informar...</p></body></html>"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Documento no encontrado |
| `400` | El documento no es oficial o no está firmado |

---

### URL temporal de descarga

```
GET /api/v1/documents/{document_id}/url
```

Genera una URL temporal firmada para descargar el PDF del documento. La URL expira en 10 minutos.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/c3d4e5f6-a7b8-9012-cdef-123456789012/url" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "official_number": "IF-2025-00012-SMG-ADGEN",
  "pdf_url": "https://s3.your-domain.com/municipio/documents/c3d4e5f6.pdf?X-Amz-Signature=abc123&X-Amz-Expires=600",
  "expires_in": 600
}
```

!!! tip "Tiempo de expiración"
    La URL es válida por `600` segundos (10 minutos). Después de ese tiempo, se debe solicitar una nueva URL.

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Documento no encontrado o sin PDF disponible |

---

### Detalles de firma

```
GET /api/v1/documents/{document_id}/signature-details
```

Devuelve los detalles de firma de un documento (firmantes, fechas, estado de cada firma).

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/c3d4e5f6-a7b8-9012-cdef-123456789012/signature-details" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "document_number": "IF-2025-00012-SMG-ADGEN",
  "signature_status": "fully_signed",
  "signers": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Juan Perez",
      "role": "director",
      "status": "signed",
      "signed_at": "2025-06-17T10:30:00Z"
    }
  ]
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | Documento no encontrado |

---

### Buscar documento oficial por número

```
GET /api/v1/documents/search-official/{doc_number}
```

Busca un documento oficial por su número exacto.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `doc_number` | string | Número oficial del documento (ej: `IF-2025-00012-SMG-ADGEN`) |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/search-official/IF-2025-00012-SMG-ADGEN" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "document_number": "IF-2025-00012-SMG-ADGEN",
  "document_type": "INF",
  "reference": "Informe tecnico sobre habilitacion comercial",
  "status": "signed",
  "created_at": "2025-06-16T09:00:00Z"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `404` | No existe **o** el usuario no tiene permiso para verlo (misma respuesta a propósito: no revela si existe) |

!!! warning "Alcanzar un documento de otro sector depende de un permiso del usuario"
    Igual que con los expedientes, un usuario solo ve los documentos de sus
    sectores. La búsqueda por número exacto amplia ese alcance **únicamente si
    su ficha tiene activado `can_global_search_documents`**, permiso que se
    administra por usuario desde el BackOffice y viene **desactivado** por
    defecto.

    Sin ese permiso, un documento de otro sector responde `404` aunque el número
    sea correcto.

    Vale la misma advertencia que para expedientes: si el portal expone
    "consulta por número" al público, conviene usar una API Key asociada a un
    usuario **sin** el permiso global, o filtrar antes de mostrar. Ver
    [Visibilidad y búsqueda global](expedientes.md#visibilidad-y-busqueda-global).

---

### Verificar permisos de firma

```
GET /api/v1/documents/check-signer-permissions
```

Verifica si un usuario tiene permisos para firmar documentos de un tipo determinado.

**Parámetros query:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `user_id` | UUID | Sí | ID del usuario a verificar |
| `document_type_acronym` | string | Sí | Acrónimo del tipo de documento (ej: `INF`, `DICT`) |

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/check-signer-permissions?user_id=550e8400-e29b-41d4-a716-446655440000&document_type_acronym=INF" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type_acronym": "INF",
  "can_sign": true,
  "reason": "User has signer role for INF documents"
}
```

---

## Operaciones

### Crear documento borrador

```
POST /api/v1/documents/
```

Crea un nuevo documento en estado borrador.

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_type_acronym` | string | Sí | Acrónimo del tipo de documento (`INF`, `DICT`, etc.) |
| `reference` | string | Sí | Descripción o asunto del documento |
| `case_id` | UUID | No | Vincular directamente a un expediente |
| `recipients` | list | No | Lista de UUIDs de usuarios destinatarios |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/documents/" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_acronym": "INF",
    "reference": "Informe de inspeccion ocular - Local comercial Av. San Martin 1234",
    "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

**Respuesta `201 Created`:**

```json
{
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "document_type": "INF",
  "reference": "Informe de inspeccion ocular - Local comercial Av. San Martin 1234",
  "status": "draft",
  "created_at": "2025-07-01T11:00:00Z"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Tipo de documento inválido o campos requeridos faltantes |
| `404` | Expediente no encontrado (si se pasó `case_id`) |

!!! tip "Tipos de documentos"
    Para ver los tipos de documentos disponibles, usar `GET /api/v1/system/document-types`.

---

### Importar PDF externo

```
POST /api/v1/documents/import
```

Importa un archivo PDF externo como documento en el sistema.

**Content-Type:** `multipart/form-data`

**Campos del formulario:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_type_acronym` | string | Sí | Acrónimo del tipo de documento |
| `reference` | string | Sí | Descripción del documento |
| `pdf_file` | file | Sí | Archivo PDF a importar |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/documents/import" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -F "document_type_acronym=INF" \
  -F "reference=Informe pericial externo - Perito Martinez" \
  -F "pdf_file=@/ruta/al/archivo/informe-pericial.pdf"
```

**Respuesta `201 Created`:**

```json
{
  "document_id": "a7b8c9d0-e1f2-3456-ghab-567890123456",
  "document_type": "INF",
  "reference": "Informe pericial externo - Perito Martinez",
  "status": "draft",
  "is_imported": true,
  "created_at": "2025-07-01T12:00:00Z"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Archivo no es PDF válido o campos requeridos faltantes |
| `400` | El PDF trae una firma de certificación que GDI no puede conservar (ver abajo) |
| `422` | Archivo excede el tamaño máximo permitido |

!!! info "PDF que ya viene certificado"
    Si el PDF trae una firma de certificación válida, GDI lo guarda **byte a byte** como
    certificado de origen: `GET /documents/{id}` lo marca con `certified_origin: true`.
    Si la certificación no se puede conservar, GDI responde `400` y no crea el documento.
    Textos de `error` y qué hacer:

    - `La firma de este PDF está rota o el documento fue modificado después de firmarse...`: subir el archivo original, sin comprimirlo ni editarlo.
    - `El PDF dice venir certificado, pero ninguna de sus firmas respalda esa certificación...`: volver a exportar el PDF desde su origen.
    - `El PDF está protegido con contraseña para abrirse...`: subir una copia sin contraseña de apertura.
    - `El PDF trae firmas digitales que no se pudieron leer...`: volver a exportar el PDF desde su origen.

---

### Guardar cambios en borrador

```
PATCH /api/v1/documents/{document_id}
```

Actualiza el contenido y/o metadatos de un documento en estado borrador.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `content` | string | No | Contenido HTML del documento |
| `reference` | string | No | Nueva referencia o asunto |
| `signers` | list | No | Lista de UUIDs de firmantes |
| `recipients` | list | No | Lista de UUIDs de destinatarios |
| `proposed_case_ids` | list | No | Lista de UUIDs de expedientes propuestos |

**Ejemplo:**

```bash
curl -X PATCH "https://gateway.your-domain.com/api/v1/documents/f6a7b8c9-d0e1-2345-fgab-456789012345" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<p>Se informa que el local ubicado en Av. San Martin 1234 cumple con los requisitos de habilitacion vigentes.</p>",
    "signers": ["550e8400-e29b-41d4-a716-446655440000"],
    "recipients": ["660f9511-f3ac-52e5-b827-557766551111"]
  }'
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "status": "draft",
  "updated_at": "2025-07-01T13:00:00Z"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no está en estado borrador |
| `403` | Sin permisos para editar este documento |
| `404` | Documento no encontrado |

---

### Reemplazar PDF importado

```
PUT /api/v1/documents/{document_id}/imported-pdf
```

Reemplaza el archivo PDF de un documento importado en estado `draft` o `rejected`. Un
documento `rejected` sigue en ese estado hasta que se lo vuelve a enviar a firma.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento importado |

**Content-Type:** `multipart/form-data`

**Campos del formulario:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `pdf_file` | file | Sí | Nuevo archivo PDF |

**Ejemplo:**

```bash
curl -X PUT "https://gateway.your-domain.com/api/v1/documents/a7b8c9d0-e1f2-3456-ghab-567890123456/imported-pdf" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -F "pdf_file=@/ruta/al/archivo/informe-pericial-v2.pdf"
```

**Respuesta `200 OK`:**

```json
{
  "success": true,
  "pdf_url": "https://...",
  "message": "PDF reemplazado exitosamente"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no es importado |
| `400` | El PDF nuevo es un certificado de origen y el documento ya tiene adjuntos: `El PDF nuevo viene certificado de origen y no admite adjuntos agregados desde GDI...` |
| `404` | Documento no encontrado |
| `409` | `Solo se puede reemplazar PDF en documentos draft o rejected`: el documento está en firma o ya es oficial |
| `422` | Archivo no es PDF válido |

---

### Eliminar borrador

```
DELETE /api/v1/documents/{document_id}
```

Elimina un documento que se encuentra en estado `draft` o `rejected`.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

!!! warning "Solo borradores y rechazados"
    Solo se pueden eliminar documentos en estado `draft` o `rejected`. Los documentos firmados o en proceso de firma no pueden eliminarse.

**Ejemplo:**

```bash
curl -X DELETE "https://gateway.your-domain.com/api/v1/documents/f6a7b8c9-d0e1-2345-fgab-456789012345" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "message": "Document deleted successfully"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no está en estado `draft` o `rejected` |
| `403` | Sin permisos para eliminar este documento |
| `404` | Documento no encontrado |

---

## Firma

### Iniciar proceso de firma

```
POST /api/v1/documents/{document_id}/start-signing
```

Envía un documento borrador al circuito de firma. Cambia el estado del documento a `sent_to_sign`.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/documents/f6a7b8c9-d0e1-2345-fgab-456789012345/start-signing" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "status": "sent_to_sign",
  "message": "Document sent for signing"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no está en estado borrador o no tiene firmantes asignados |
| `403` | Sin permisos para enviar a firma |
| `404` | Documento no encontrado |

!!! tip "Requisitos previos"
    Antes de iniciar la firma, asegurar que el documento tenga contenido y firmantes asignados. Usar `PATCH /api/v1/documents/{document_id}` para configurar los firmantes.

---

### Firmar documento

```
POST /api/v1/documents/{document_id}/sign
```

Aplica la firma del usuario actual al documento. Si todos los firmantes requeridos firman, el documento pasa a estado `signed` y se genera el número oficial.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/documents/f6a7b8c9-d0e1-2345-fgab-456789012345/sign" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "status": "signed",
  "document_number": "IF-2025-00042-SMG-ADGEN",
  "signed_at": "2025-07-01T15:00:00Z"
}
```

!!! warning "Firma digital con token físico"
    Este endpoint solo acepta **firma electrónica**. Si el documento requiere firma con token físico (`signature_policy=digital_all`, o el usuario es numerador con `digital_num`), la API devuelve `422` con el mensaje _"Este documento requiere firma con token físico. Firma desde el portal web."_. La firma con token se realiza desde el portal web con FirmadorGDI.

    **Excepción:** un certificado de origen (`certified_origin: true`) se firma por este endpoint
    aunque el tipo exija firma digital. Nadie firma ese PDF: los firmantes comunes dan
    conformidad y el numerador lo numera.

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no está en estado `sent_to_sign`, o `document_id inválido (se espera UUID)` |
| `403` | El usuario no es firmante de este documento |
| `403` | El numerador no tiene el rango que pide el tipo. El texto dice cuál falta: `Sin permiso de rango para numerar '<tipo>'...` |
| `404` | Documento no encontrado |
| `409` | Certificado de origen cuyo PDF cambió desde que se importó: `El PDF cambió desde que se verificó como certificado de origen...` |
| `422` | El documento requiere firma con token físico |
| `429` | La cola de firma está saturada. Con `Retry-After`, reintentar después de esos segundos. Sin `Retry-After`, avisar al municipio: reintentar no sirve |
| `503` | Espera pasajera (por ejemplo, `"code": "CERTIFIED_CHECK_RETRY"` en un certificado de origen). Reintentar después de `Retry-After` |

---

### Rechazar documento

```
POST /api/v1/documents/{document_id}/reject
```

Rechaza un documento que se encuentra en proceso de firma. El documento vuelve al estado `rejected`.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `reason` | string | Sí | Motivo del rechazo |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/documents/f6a7b8c9-d0e1-2345-fgab-456789012345/reject" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "El informe no incluye los datos del relevamiento de campo"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "success": true,
  "message": "Documento rechazado exitosamente",
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "rejected_by": "550e8400-e29b-41d4-a716-446655440000",
  "rejected_by_name": "Juan Perez",
  "rejection_id": "d1e2f3a4-b5c6-7890-abcd-ef1234567890",
  "rejected_at": "2026-11-04T15:00:00Z",
  "reason": "El informe no incluye los datos del relevamiento de campo",
  "new_status": "rejected",
  "display_status": "En edición",
  "reset_info": {
    "sent_to_sign_at_cleared": true,
    "sent_by_cleared": true,
    "document_generate_id_cleared": true,
    "all_signers_reset_to_pending": true
  },
  "pdf_cleanup": {
    "attempted": true,
    "success": true,
    "error": null,
    "note": "PDF cleanup is best-effort (soft-fail)"
  }
}
```

!!! info "Rechazar un documento Importado"
    Un Importado vuelve a edición **con su PDF**. `pdf_cleanup.imported_pdf` dice qué pasó
    con el archivo (`restored`, `kept`, `deleted`, `missing` o `error`). Si trae
    `reupload_required: true`, el documento quedó sin PDF: subirlo con
    [Reemplazar PDF importado](#reemplazar-pdf-importado) antes de volver a enviarlo a firma.
    Detalle en [Cambios de la API](../changelog.md).

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | Motivo vacío, o `document_id inválido (se espera UUID)` |
| `403` | El usuario no es firmante de este documento |
| `404` | Documento no encontrado |
| `409` | El documento ya estaba rechazado, ya es oficial, o se firmó mientras se lo rechazaba. Consultar su estado con `GET /documents/{id}` |

---

## Vincular a expediente

### Vincular documento oficial

```
POST /api/v1/cases/{case_id}/documents/link
```

Vincula un documento oficial (firmado) a un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `official_document_id` | UUID | Sí | ID del documento oficial a vincular |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents/link" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "official_document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Document linked to case successfully",
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no es oficial o ya está vinculado |
| `403` | Sin permisos sobre el expediente |
| `409` | El expediente todavía se está **creando** (falta su carátula): es transitorio, reintentar en unos segundos (GDI-436) |
| `404` | Expediente o documento no encontrado |

---

### Proponer borrador

```
POST /api/v1/cases/{case_id}/documents/propose
```

Propone vincular un documento en estado borrador a un expediente. Requiere aceptación por parte del responsable del expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `document_draft_id` | UUID | Sí | ID del documento borrador a proponer |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents/propose" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "document_draft_id": "f6a7b8c9-d0e1-2345-fgab-456789012345"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Document proposed to case",
  "proposed_id": "b8c9d0e1-f2a3-4567-hgab-678901234567",
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "status": "pending_approval"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | El documento no está en estado borrador, o `case_id` / `document_draft_id` no es un UUID |
| `403` | Sin permisos para proponer documentos a este expediente |
| `409` | El expediente todavía se está **creando** (falta su carátula): es transitorio, reintentar en unos segundos (GDI-436) |
| `404` | Expediente o documento no encontrado |

---

### Aceptar propuesta

```
POST /api/v1/cases/{case_id}/documents/accept-proposal
```

Acepta una propuesta de vinculación de documento a un expediente.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `proposed_id` | UUID | Sí | ID de la propuesta a aceptar |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents/accept-proposal" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "proposed_id": "b8c9d0e1-f2a3-4567-hgab-678901234567"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Proposal accepted",
  "proposed_id": "b8c9d0e1-f2a3-4567-hgab-678901234567",
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | La propuesta ya fue procesada, o `case_id` / `proposed_id` no es un UUID |
| `403` | Sin permisos para aceptar propuestas en este expediente |
| `404` | Expediente o propuesta no encontrada |

---

### Rechazar propuesta

```
POST /api/v1/cases/{case_id}/documents/reject-proposal
```

Rechaza una propuesta de vinculación de documento.

**Parámetros path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `proposed_id` | UUID | Sí | ID de la propuesta a rechazar |

**Ejemplo:**

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/cases/a1b2c3d4-e5f6-7890-abcd-ef1234567890/documents/reject-proposal" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "proposed_id": "b8c9d0e1-f2a3-4567-hgab-678901234567"
  }'
```

**Respuesta `200 OK`:**

```json
{
  "message": "Proposal rejected",
  "proposed_id": "b8c9d0e1-f2a3-4567-hgab-678901234567",
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| `400` | La propuesta ya fue procesada, o `case_id` / `proposed_id` no es un UUID |
| `403` | Sin permisos para rechazar propuestas en este expediente |
| `404` | `Propuesta no encontrada` |
