# Documentos

**20 endpoints** para gestion de documentos (mas 4 de vinculacion a expedientes documentados en [Expedientes](expedientes.md)).

Todos los endpoints usan la base URL `https://gateway.your-domain.com/api/v1` y requieren los headers `X-API-Key` y `X-User-ID` salvo que se indique lo contrario.

---

## Lectura

### Buscar documentos

```
GET /api/v1/documents/search
```

Busca documentos con filtros opcionales. Soporta paginacion.

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Resultados por pagina (max `100`) |
| `search` | string | - | Busca por `document_number` |
| `status` | string | - | Filtrar por estado visual: `"En edición"`, `"Firmar ahora"`, `"En proceso de firma"`, `"Firmado"` |
| `document_type` | string | - | Filtrar por acronimo del tipo: `INF`, `DICT`, etc. |
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

Devuelve la informacion completa de un documento.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

!!! info "X-User-ID opcional"
    Se requiere `X-User-ID` para acceder a documentos que estan en proceso de firma. Para documentos en otros estados, es opcional.

**Ejemplo:**

```bash
curl -X GET "https://gateway.your-domain.com/api/v1/documents/c3d4e5f6-a7b8-9012-cdef-123456789012" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: 550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta `200 OK`:**

```json
{
  "document_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "document_number": "IF-2025-00012-SMG-ADGEN",
  "document_type": {
    "acronym": "INF",
    "name": "Informe"
  },
  "reference": "Informe tecnico sobre habilitacion comercial",
  "status": "signed",
  "content": "<p>Contenido HTML del documento...</p>",
  "created_by": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "Juan Perez"
  },
  "signers": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Juan Perez",
      "signed_at": "2025-06-17T10:30:00Z"
    }
  ],
  "created_at": "2025-06-16T09:00:00Z",
  "signed_at": "2025-06-17T10:30:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Documento no encontrado |
| `403` | Sin permisos para ver el documento |

---

### Contenido HTML

```
GET /api/v1/documents/{document_id}/content
```

Devuelve el contenido HTML de un documento oficial firmado.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

!!! warning "Solo documentos oficiales firmados"
    Este endpoint solo funciona para documentos que ya fueron firmados y tienen numero oficial. Los borradores no tienen contenido disponible por esta via.

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

| Codigo | Descripcion |
|--------|-------------|
| `404` | Documento no encontrado |
| `400` | El documento no es oficial o no esta firmado |

---

### URL temporal de descarga

```
GET /api/v1/documents/{document_id}/url
```

Genera una URL temporal firmada para descargar el PDF del documento. La URL expira en 10 minutos.

**Parametros path:**

| Parametro | Tipo | Descripcion |
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
  "pdf_url": "https://r2.gdilatam.com/municipio/documents/c3d4e5f6.pdf?X-Amz-Signature=abc123&X-Amz-Expires=600",
  "expires_in": 600
}
```

!!! tip "Tiempo de expiracion"
    La URL es valida por `600` segundos (10 minutos). Despues de ese tiempo, se debe solicitar una nueva URL.

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `404` | Documento no encontrado o sin PDF disponible |

---

### Detalles de firma

```
GET /api/v1/documents/{document_id}/signature-details
```

Devuelve los detalles de firma de un documento (firmantes, fechas, estado de cada firma).

**Parametros path:**

| Parametro | Tipo | Descripcion |
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

| Codigo | Descripcion |
|--------|-------------|
| `404` | Documento no encontrado |

---

### Buscar documento oficial por numero

```
GET /api/v1/documents/search-official/{doc_number}
```

Busca un documento oficial por su numero exacto.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `doc_number` | string | Numero oficial del documento (ej: `IF-2025-00012-SMG-ADGEN`) |

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

| Codigo | Descripcion |
|--------|-------------|
| `404` | No se encontro documento con ese numero |

---

### Verificar permisos de firma

```
GET /api/v1/documents/check-signer-permissions
```

Verifica si un usuario tiene permisos para firmar documentos de un tipo determinado.

**Parametros query:**

| Parametro | Tipo | Requerido | Descripcion |
|-----------|------|-----------|-------------|
| `user_id` | UUID | Si | ID del usuario a verificar |
| `document_type_acronym` | string | Si | Acronimo del tipo de documento (ej: `INF`, `DICT`) |

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

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `document_type_acronym` | string | Si | Acronimo del tipo de documento (`INF`, `DICT`, etc.) |
| `reference` | string | Si | Descripcion o asunto del documento |
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

| Codigo | Descripcion |
|--------|-------------|
| `400` | Tipo de documento invalido o campos requeridos faltantes |
| `404` | Expediente no encontrado (si se paso `case_id`) |

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

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `document_type_acronym` | string | Si | Acronimo del tipo de documento |
| `reference` | string | Si | Descripcion del documento |
| `pdf_file` | file | Si | Archivo PDF a importar |

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

| Codigo | Descripcion |
|--------|-------------|
| `400` | Archivo no es PDF valido o campos requeridos faltantes |
| `422` | Archivo excede el tamano maximo permitido |

---

### Guardar cambios en borrador

```
PATCH /api/v1/documents/{document_id}
```

Actualiza el contenido y/o metadatos de un documento en estado borrador.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
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

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado borrador |
| `403` | Sin permisos para editar este documento |
| `404` | Documento no encontrado |

---

### Reemplazar PDF importado

```
PUT /api/v1/documents/{document_id}/imported-pdf
```

Reemplaza el archivo PDF de un documento importado.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento importado |

**Content-Type:** `multipart/form-data`

**Campos del formulario:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `pdf_file` | file | Si | Nuevo archivo PDF |

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
  "document_id": "a7b8c9d0-e1f2-3456-ghab-567890123456",
  "message": "PDF replaced successfully",
  "updated_at": "2025-07-01T14:00:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no es importado o no esta en estado borrador |
| `404` | Documento no encontrado |
| `422` | Archivo no es PDF valido |

---

### Eliminar borrador

```
DELETE /api/v1/documents/{document_id}
```

Elimina un documento que se encuentra en estado `draft` o `rejected`.

**Parametros path:**

| Parametro | Tipo | Descripcion |
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

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado `draft` o `rejected` |
| `403` | Sin permisos para eliminar este documento |
| `404` | Documento no encontrado |

---

## Firma

### Iniciar proceso de firma

```
POST /api/v1/documents/{document_id}/start-signing
```

Envia un documento borrador al circuito de firma. Cambia el estado del documento a `sent_to_sign`.

**Parametros path:**

| Parametro | Tipo | Descripcion |
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

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado borrador o no tiene firmantes asignados |
| `403` | Sin permisos para enviar a firma |
| `404` | Documento no encontrado |

!!! tip "Requisitos previos"
    Antes de iniciar la firma, asegurar que el documento tenga contenido y firmantes asignados. Usar `PATCH /api/v1/documents/{document_id}` para configurar los firmantes.

---

### Firmar documento

```
POST /api/v1/documents/{document_id}/sign
```

Aplica la firma del usuario actual al documento. Si todos los firmantes requeridos firman, el documento pasa a estado `signed` y se genera el numero oficial.

**Parametros path:**

| Parametro | Tipo | Descripcion |
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

!!! warning "Firma digital con token fisico"
    Este endpoint solo acepta **firma electronica**. Si el documento requiere firma con token fisico (`signature_policy=digital_all`, o el usuario es numerador con `digital_num`), la API devuelve `422` con el mensaje _"Este documento requiere firma con token fisico. Firma desde el portal web."_. La firma con token se realiza desde el portal web con FirmadorGDI.

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado `sent_to_sign` |
| `403` | El usuario no es firmante de este documento |
| `404` | Documento no encontrado |
| `422` | El documento requiere firma con token fisico |

---

### Rechazar documento

```
POST /api/v1/documents/{document_id}/reject
```

Rechaza un documento que se encuentra en proceso de firma. El documento vuelve al estado `rejected`.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `document_id` | UUID | Identificador del documento |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `reason` | string | Si | Motivo del rechazo |

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
  "document_id": "f6a7b8c9-d0e1-2345-fgab-456789012345",
  "status": "rejected",
  "rejected_by": "Juan Perez",
  "reason": "El informe no incluye los datos del relevamiento de campo"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado `sent_to_sign` o motivo vacio |
| `403` | El usuario no es firmante de este documento |
| `404` | Documento no encontrado |

---

## Vincular a expediente

### Vincular documento oficial

```
POST /api/v1/cases/{case_id}/documents/link
```

Vincula un documento oficial (firmado) a un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `official_document_id` | UUID | Si | ID del documento oficial a vincular |

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

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no es oficial o ya esta vinculado |
| `403` | Sin permisos sobre el expediente |
| `404` | Expediente o documento no encontrado |

---

### Proponer borrador

```
POST /api/v1/cases/{case_id}/documents/propose
```

Propone vincular un documento en estado borrador a un expediente. Requiere aceptacion por parte del responsable del expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `document_draft_id` | UUID | Si | ID del documento borrador a proponer |

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

| Codigo | Descripcion |
|--------|-------------|
| `400` | El documento no esta en estado borrador |
| `403` | Sin permisos para proponer documentos a este expediente |
| `404` | Expediente o documento no encontrado |

---

### Aceptar propuesta

```
POST /api/v1/cases/{case_id}/documents/accept-proposal
```

Acepta una propuesta de vinculacion de documento a un expediente.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `proposed_id` | UUID | Si | ID de la propuesta a aceptar |

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

| Codigo | Descripcion |
|--------|-------------|
| `400` | La propuesta ya fue procesada |
| `403` | Sin permisos para aceptar propuestas en este expediente |
| `404` | Expediente o propuesta no encontrada |

---

### Rechazar propuesta

```
POST /api/v1/cases/{case_id}/documents/reject-proposal
```

Rechaza una propuesta de vinculacion de documento.

**Parametros path:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `case_id` | UUID | Identificador del expediente |

**Body (JSON):**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `proposed_id` | UUID | Si | ID de la propuesta a rechazar |

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

| Codigo | Descripcion |
|--------|-------------|
| `400` | La propuesta ya fue procesada |
| `403` | Sin permisos para rechazar propuestas en este expediente |
| `404` | Expediente o propuesta no encontrada |
