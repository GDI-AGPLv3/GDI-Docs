# Endpoints de Documentos

Endpoints para el ciclo de vida completo de documentos: creación, edición, preview, firma, rechazo y eliminación.

## Flujo de Vida de un Documento

```
POST /documents (crear)
    |
    v
PATCH /documents/{id}/save (guardar contenido + firmantes)
    |
    v
POST /documents/{id}/preview-download (preview PDF)
    |
    v
POST /documents/{id}/start-signing-process (enviar a firma)
    |
    v
POST /documents/{id}/super-sign (firma de cada firmante)
    |
    +-- Firmante comun -> firma y sigue en sent_to_sign
    +-- Numerador (ultimo) -> firma, numera, oficializa -> signed
```

## Crear Documento

### `POST /documents`

Crea un documento en estado `draft`.

**Request:**

```json
{
    "document_type_acronym": "INF",
    "reference": "Informe sobre presupuesto anual",
    "recipients": {
        "to": ["uuid-sector-1"],
        "cc": ["uuid-sector-2"],
        "bcc": []
    }
}
```

!!! note "Recipients"
    El campo `recipients` solo es requerido para documentos tipo **NOTA**. Para otros tipos se omite.

**Response (200):**

```json
{
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "draft",
    "message": "Documento creado exitosamente"
}
```

**Archivo:** `endpoints/documents/create_document.py`

---

## Guardar Cambios

### `PATCH /documents/{document_id}/save`

Guarda cambios parciales o completos en un documento editable. Solo funciona en estado `draft` o `rejected`.

**Request:**

```json
{
    "reference": "Nuevo asunto",
    "content": "<p>Contenido HTML del documento</p>",
    "signers": [
        {
            "user_id": "uuid-firmante",
            "is_numerator": true
        }
    ],
    "proposed_case_ids": ["uuid-expediente-1", "uuid-expediente-2"]
}
```

Todos los campos son opcionales. Solo se actualizan los campos enviados.

**Response (200):**

```json
{
    "success": true,
    "message": "Cambios guardados exitosamente",
    "document_id": "uuid",
    "last_modified_at": "2025-01-15T10:30:00"
}
```

**Archivo:** `endpoints/documents/save_document.py`

---

## Preview

### `POST /documents/{document_id}/preview-info`

Obtiene información completa del documento para previsualización sin generar PDF.

### `POST /documents/{document_id}/preview-download`

Genera y descarga PDF del documento:

- **Documentos HTML**: PDF con marca de agua "BORRADOR"
- **Documentos importados**: URL firmada del PDF en R2

**Response (documentos HTML):** Binario PDF con `Content-Type: application/pdf`

**Response (documentos importados):**

```json
{
    "success": true,
    "pdf_url": "https://r2.cloudflare.com/...",
    "is_imported": true
}
```

**Archivo:** `endpoints/documents/preview_document.py`

---

## Iniciar Firma

### `POST /documents/{document_id}/start-signing-process`

Cambia el estado del documento de `draft` a `sent_to_sign`.

**Requisitos:**

- Solo el **creador** puede iniciar el proceso
- Debe tener al menos un **firmante** asignado
- Debe tener un **numerador** asignado

**Proceso:**

1. Valida que el usuario sea el creador
2. Verifica firmantes y numerador
3. Genera el PDF final
4. Cambia estado a `sent_to_sign`

**Response (200):**

```json
{
    "success": true,
    "message": "Proceso de firma iniciado exitosamente"
}
```

**Archivo:** `endpoints/documents/start_signing.py`

---

## Firma Unificada

### `POST /documents/{document_id}/super-sign`

Endpoint unificado que detecta automáticamente si el usuario es firmante común o numerador.

**Firmante común:**

1. Estampa firma digital vía GDI-Notary
2. Actualiza estado del firmante a `signed`
3. Documento sigue en `sent_to_sign`

**Numerador (último firmante):**

1. Valida que todos los firmantes comunes hayan firmado
2. Genera número oficial (ej: `INF-2025-0001234-SMG-ADGEN`)
3. Estampa firma y numera vía GDI-Notary
4. Mueve PDF a bucket oficial en R2
5. Cambia estado a `signed`

**Response (firmante común):**

```json
{
    "success": true,
    "message": "Documento firmado exitosamente",
    "document_id": "uuid",
    "document_status": "sent_to_sign",
    "is_numerator": false,
    "official_number": null
}
```

**Response (numerador):**

```json
{
    "success": true,
    "message": "Documento firmado y numerado exitosamente",
    "document_id": "uuid",
    "document_status": "signed",
    "is_numerator": true,
    "official_number": "INF-2025-0001234-SMG-ADGEN"
}
```

**Archivo:** `endpoints/documents/super_sign.py`

---

## Rechazar Documento

### `POST /documents/{document_id}/reject`

Permite a cualquier firmante rechazar un documento con un motivo.

**Request:**

```json
{
    "reason": "El documento tiene errores en el presupuesto"
}
```

**Response (200):** `RejectDocumentResponse`

```json
{
    "success": true,
    "message": "Documento rechazado exitosamente",
    "document_id": "uuid",
    "rejected_by": "uuid",
    "rejected_by_name": "Juan Perez",
    "rejection_id": "uuid",
    "rejected_at": "2026-11-04T15:00:00Z",
    "reason": "El documento tiene errores en el presupuesto",
    "new_status": "rejected",
    "display_status": "En edición",
    "reset_info": {"...": "..."}
}
```

**Errores:**

| Código | Cuándo |
|--------|--------|
| `409` | El documento ya estaba rechazado, o se firmó mientras se lo rechazaba |
| `422` | El documento ya es oficial: `No se puede rechazar un documento completado` |

!!! info "Importados"
    Un documento Importado vuelve a edición **con su PDF**: el Backend lo restaura desde la
    copia que guardó al enviarlo a firma (`{id}_base.pdf`). Desde ahí se puede reemplazar el PDF
    con el documento en `rejected`. Si no hay copia limpia (documentos enviados a firma antes
    del 04/11/2026 que alguien ya firmó), el PDF se borra y hay que volver a subirlo.

**Archivo:** `endpoints/documents/reject_document.py`

---

## Eliminar Documento

### `DELETE /documents/{document_id}`

Soft delete. Solo el creador puede eliminar documentos en estado `draft` o `rejected`.

**Response (200):**

```json
{
    "success": true,
    "message": "Documento eliminado exitosamente",
    "unlinked_cases": 2
}
```

**Archivo:** `endpoints/documents/delete_document.py`

---

## Detalles Unificados

### `GET /documents/{document_id}/details`

Obtiene detalles de un documento en cualquier estado, delegando al servicio apropiado.

**Response:** `UnifiedDocumentDetailsResponse` con `state_category` ("editing" o "signing") y detalles específicos.

Campos de certificado de origen:

| Campo | Dónde | Qué es |
|-------|-------|--------|
| `certified_origin` | `details` (editing); `details.document` y raíz de `details` (signing) | `true` si es un PDF importado con firma de certificación de origen. GDI no lo modifica y el número oficial no va impreso en el PDF |
| `signed_with_provider` | Cada firmante de `signature_progress.signatures` (signing) | Con qué firmó. `"conformidad"` = dio su conformidad sin firmar el PDF (certificado de origen). `null` si todavía no firmó |

`certified_origin` sale de `document_draft.certified_pdf_sha256 IS NOT NULL`. Un documento
oficial comparte el id con su borrador, así que el campo vale también para documentos firmados.

**Archivo:** `endpoints/documents/unified_details.py`

---

## Buscar Documento Oficial

### `GET /api/v1/documents/search-official/{doc_number}`

Busca documento oficial por número exacto. Sin restricciones de usuario.

**Formato del número:** `TIPO-AÑO-NUMERO-CIUDAD-SECTOR` (ej: `INF-2025-0001234-SMG-ADGEN`)

**Response:**

```json
{
    "found": true,
    "document": { ... },
    "search_term": "INF-2025-0001234-SMG-ADGEN"
}
```

**Archivo:** `endpoints/documents/search_official.py`
