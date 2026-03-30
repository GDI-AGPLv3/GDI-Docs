# Memos

Comunicacion privada persona a persona. 6 endpoints bajo el prefijo `/memos`.

---

## Endpoints

| # | Metodo | Ruta | Descripcion | Auth |
|---|--------|------|-------------|------|
| 1 | GET | `/memos/received` | Memos recibidos | Bearer |
| 2 | GET | `/memos/sent` | Memos enviados | Bearer |
| 3 | GET | `/memos/archived` | Memos archivados | Bearer |
| 4 | GET | `/memos/{document_id}` | Detalle de un memo | Bearer |
| 5 | PATCH | `/memos/{document_id}/archive` | Archivar/desarchivar | Bearer |
| 6 | GET | `/memos/unread-count` | Contador de no leidos | Bearer |

---

## GET /memos/received

Memos recibidos por el usuario autenticado (no archivados).

**Parametros query:**

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | 1 | Pagina |
| `page_size` | int | 20 | Items por pagina (max 100) |
| `search` | string | - | Busca en numero oficial, asunto, contenido |
| `date_filter` | string | - | Filtro predefinido: `hoy`, `ayer`, `ultimos_7_dias`, `ultimos_30_dias` |
| `date_from` | string | - | Fecha desde (YYYY-MM-DD) |
| `date_to` | string | - | Fecha hasta (YYYY-MM-DD) |

**Response `200 OK`:**

```json
{
  "memos": [
    {
      "document_id": "uuid",
      "official_number": "MEMO-2026-00000001-MUNI-SEC",
      "reference": "Asunto del memo",
      "signed_at": "2026-03-28T14:30:00Z",
      "ai_summary": "Resumen generado por IA...",
      "document_type": "MEMO",
      "recipient_type": "TO",
      "sender": {
        "user_id": "uuid",
        "full_name": "Juan Perez",
        "sector_acronym": "SEC"
      },
      "read_status": {
        "opened": false,
        "opened_at": null
      }
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## GET /memos/sent

Memos enviados por el usuario autenticado.

**Parametros query:** Identicos a `/memos/received`.

**Response `200 OK`:**

```json
{
  "memos": [
    {
      "document_id": "uuid",
      "official_number": "MEMO-2026-00000001-MUNI-SEC",
      "reference": "Asunto del memo",
      "signed_at": "2026-03-28T14:30:00Z",
      "ai_summary": "...",
      "recipients": [
        {
          "user_id": "uuid",
          "full_name": "Maria Garcia",
          "recipient_type": "TO"
        }
      ],
      "openings_count": 3
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## GET /memos/archived

Memos archivados por el usuario autenticado.

**Parametros query:** `page`, `page_size`, `search`.

**Response:** Misma estructura que `/memos/received`.

---

## GET /memos/{document_id}

Detalle completo de un memo. Si el usuario es destinatario y es su primera apertura, registra `opened_at = NOW()`.

**Seguridad:**

- Solo el remitente y los destinatarios pueden acceder
- Los destinatarios BCC solo son visibles para el remitente
- El panel de aperturas solo es visible para el remitente

**Response `200 OK`:**

```json
{
  "document_id": "uuid",
  "official_number": "MEMO-2026-00000001-MUNI-SEC",
  "reference": "Asunto del memo",
  "content": { "html": "<p>Contenido del memo...</p>" },
  "signed_at": "2026-03-28T14:30:00Z",
  "signed_pdf_url": "https://...",
  "ai_summary": "Resumen IA...",
  "signers": [
    { "user_id": "uuid", "full_name": "Juan Perez", "signed_at": "..." }
  ],
  "sender": {
    "user_id": "uuid",
    "full_name": "Juan Perez",
    "sector_name": "Secretaria",
    "sector_acronym": "SEC"
  },
  "recipients": {
    "to": [{ "user_id": "uuid", "full_name": "Maria Garcia", "sector_acronym": "TES" }],
    "cc": [],
    "bcc": null
  },
  "my_access": {
    "is_sender": false,
    "recipient_type": "TO",
    "first_open": true,
    "opened_at": "2026-03-28T15:00:00Z",
    "is_archived": false,
    "archived_at": null
  },
  "openings": null,
  "proposed_cases": null
}
```

!!! info "Campos condicionales"
    - `recipients.bcc`: `null` si el usuario no es el remitente
    - `openings`: `null` si el usuario no es el remitente
    - `my_access.first_open`: `true` solo en la primera apertura

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `403` | No sos remitente ni destinatario |
| `404` | Memo no encontrado |

---

## PATCH /memos/{document_id}/archive

Archiva o desarchiva un memo. Solo disponible para destinatarios (no para el remitente).

**Request body:**

```json
{ "archived": true }
```

**Response `200 OK`:**

```json
{
  "success": true,
  "archived": true,
  "archived_at": "2026-03-28T16:00:00Z"
}
```

**Errores:**

| Codigo | Descripcion |
|--------|-------------|
| `403` | El remitente no puede archivar sus propios memos |
| `404` | Memo no encontrado o no sos destinatario |

---

## GET /memos/unread-count

Cantidad de memos no leidos (para badge en menu lateral).

**Response `200 OK`:**

```json
{ "unread_count": 5 }
```

---

## Servicios

Los servicios de memos estan en `services/memos/`:

| Modulo | Responsabilidad |
|--------|-----------------|
| `validation.py` | Validar tipo MEMO, validar recipients, deduplicar |
| `save_recipients.py` | INSERT/DELETE en `memo_recipients`, snapshot de sectores |
| `recipients.py` | Visibilidad de BCC, acceso, formato para PDF |
| `retrieval.py` | Queries paginadas para received/sent/archived |
| `archiving.py` | Toggle is_archived + archived_at |
| `tracking.py` | Registrar opened_at, obtener detalle |
| `header_builder.py` | Generar HTML de destinatarios para inyectar en PDF |
| `unread.py` | COUNT de memos no leidos |

---

## Tabla de BD

**`memo_recipients`** (por tenant schema):

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `id` | UUID | PK |
| `document_id` | UUID | FK a `document_draft.id` |
| `recipient_user_id` | UUID | FK a `users.id` (destinatario) |
| `sender_user_id` | UUID | FK a `users.id` (remitente) |
| `recipient_type` | VARCHAR(3) | `TO`, `CC` o `BCC` |
| `recipient_sector_id` | UUID | Snapshot del sector del destinatario al momento del envio |
| `sender_sector_id` | UUID | Snapshot del sector del remitente al momento del envio |
| `is_archived` | BOOLEAN | `false` = visible, `true` = archivado |
| `archived_at` | TIMESTAMPTZ | Cuando se archivo |
| `opened_at` | TIMESTAMPTZ | Cuando se abrio por primera vez (`NULL` = no leido) |
| `created_at` | TIMESTAMPTZ | Fecha de creacion |
| `updated_at` | TIMESTAMPTZ | Fecha de actualizacion |

**Indices:**

- `idx_memo_recipients_document` — por document_id
- `idx_memo_recipients_sender` — por sender_user_id
- `idx_memo_recipients_not_archived` (parcial) — recibidos no archivados
- `idx_memo_recipients_archived` (parcial) — recibidos archivados
- `idx_memo_recipients_updated_at` — ordenamiento
