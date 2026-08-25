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

Requiere `X-Citizen-ID` de un ciudadano **validado**. Crea el expediente en la reparticion de radicacion configurada en el tipo, genera la **caratula (CAEX) firmada por el ciudadano** y lo comparte automaticamente con el.

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
  "official_number": "CAEX-2026-00003045-MDEV-TAD"
}
```

`400` si el `case_template_id` no existe o su canal no admite creacion por API.

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
      "pdf_url": "https://...presignado-600s..."
    }
  ]
}
```

`documents` lista los documentos **vinculados** (oficiales) del expediente, cada uno con un `pdf_url` presignado fresco (10 minutos). Los documentos solo *propuestos* no aparecen hasta que el municipio los acepte.

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
| `409` | El documento no esta firmado, o **ya tiene una propuesta pendiente** en ese expediente |

!!! note "Propuestas repetidas"
    Proponer dos veces el mismo documento devuelve `409` mientras la primera propuesta siga pendiente. Si el municipio la rechaza, el documento puede proponerse de nuevo.

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
    G-->>P: case_id + CAEX (sincronico: el numero viene ya)
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
