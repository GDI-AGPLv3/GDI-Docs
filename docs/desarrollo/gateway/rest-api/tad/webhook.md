# Webhook de notificaciones

GDI envia un `POST` a la URL de callback configurada en la API Key TAD
(BackOffice → `/api-key`) cuando hay una novedad para el portal. Asi el portal se
entera sin hacer polling.

| Evento | Cuando llega |
|---|---|
| [`documents.signed`](#evento-documentssigned) | Termino de firmarse un documento que el portal dio de alta. **Trae el numero oficial y el PDF.** |
| [`documents.signature_failed`](#evento-documentssignature_failed) | Esa firma fallo definitivamente. |
| [`documents.notified`](#evento-documentsnotified) | Un agente municipal notifico documentos de un expediente al ciudadano. |

!!! tip "Como rutear los eventos en tu handler"
    Todos llegan a la **misma** URL de callback y todos traen el campo **`event`**:
    ruteá por ahí. Y **descartá en silencio** los `event` que no conozcas — es lo que hace
    que un evento nuevo en una version futura de GDI no te tire el handler.

## Evento `documents.signed`

El cierre del alta de documento: `POST /tad/documents` devolvio `202` y **esto es lo
que avisa que la firma termino**, con el numero oficial y el link al PDF.

```json
{
  "event": "documents.signed",
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "official_number": "PROV-2026-00003039-MDEV-TAD",
  "pdf_url": "https://...firma-presignada...&X-Amz-Expires=600&...",
  "status": "signed",
  "sent_at": "2026-07-24T18:12:31.412Z"
}
```

`sent_at` es el momento del envio: en un reintento se refresca junto con el `pdf_url`.

!!! warning "El `pdf_url` expira en 10 minutos"
    Es un link presignado de descarga directa (600 segundos). Si el portal quiere
    guardar el PDF, debe descargarlo al recibir el webhook. Siempre se puede volver a
    obtener un link fresco via
    [`GET /tad/documents/{id}`](documentos.md#consultar-el-estado-de-un-documento) o, si
    el documento ya esta vinculado a un expediente, via `GET /tad/cases/{id}`.

    El campo puede venir en `null` si el link no se pudo generar en ese momento: el
    documento **igual esta firmado y numerado**, y el PDF se obtiene por la via de
    arriba.

## Evento `documents.signature_failed`

La firma de ese documento no salio y no se va a reintentar sola. El documento queda
en el sistema sin numerar.

```json
{
  "event": "documents.signature_failed",
  "document_id": "007a5613-f796-4280-8f3a-ddf60e6c6743",
  "status": "failed",
  "failure_reason": "notary_business_error",
  "sent_at": "2026-07-24T18:12:31.412Z"
}
```

`failure_reason` es un codigo para soporte, no un texto para mostrarle al ciudadano.
Ante este evento, el portal puede volver a dar de alta el documento.

## Evento `documents.notified`

```json
{
  "event": "documents.notified",
  "sent_at": "2026-07-24T18:11:09.097Z",
  "municipality": {"name": "Municipalidad del Futuro", "acronym": "MDF"},
  "citizen": {
    "id": "2c6d5586-9cc7-46ad-809d-e9aa437002cc",
    "country_id": "27333444556",
    "full_name": "Maria Portal"
  },
  "case": {
    "id": "584ee1f9-2237-4d69-93dd-0dae54f43ba2",
    "number": "EE-2026-000227-MDF-INNO",
    "reference": "Habilitacion comercial local Calle Falsa 123"
  },
  "documents": [
    {
      "id": "8bd9b4a2-692d-44dc-826f-22c6533545ac",
      "official_number": "CAEX-2026-00003045-MDF-TAD",
      "name": "Creacion EE-2026-000227-MDF-INNO",
      "url": "https://...presignado-600s..."
    }
  ]
}
```

Los `url` de los documentos son links presignados de **10 minutos**, regenerados en cada intento de envio: descargarlos al recibir el webhook, o pedir links frescos con `GET /tad/cases/{id}`.

## Verificacion de firma HMAC

Cada request lleva el header:

```
X-GDI-Signature: t=<unix_timestamp>,v1=<firma_base64>
```

La firma es `HMAC-SHA256` con el **webhook secret** de la API Key (se muestra una unica vez al configurarlo en BackOffice), sobre el payload:

```
{t}|POST|{path_del_callback}|{sha256_hex(body)}
```

donde `path_del_callback` es el path de la URL configurada (sin query string) y `sha256_hex(body)` es el hash SHA-256 en hexadecimal del cuerpo crudo del request.

**Verificacion en Python:**

```python
import base64, hashlib, hmac, time

def verify_gdi_signature(header: str, secret: str, path: str, body: bytes) -> bool:
    parts = dict(p.split("=", 1) for p in header.split(","))
    ts, received = parts["t"], parts["v1"]
    if abs(time.time() - int(ts)) > 300:   # ventana anti-replay: 5 minutos
        return False
    body_hash = hashlib.sha256(body).hexdigest()
    payload = f"{ts}|POST|{path}|{body_hash}".encode()
    expected = base64.b64encode(
        hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, received)
```

!!! danger "Verificar siempre la firma"
    Sin verificacion, cualquiera que conozca la URL del callback puede inyectar notificaciones falsas. Rechazar requests con firma invalida o timestamp fuera de la ventana de 5 minutos.

## Entrega y reintentos

- El portal debe responder `2xx` rapido (idealmente encolar y procesar despues).
- Si el envio falla, GDI reintenta con **backoff exponencial** durante varias horas.
- La entrega es **al menos una vez**: ante reintentos el portal puede recibir el mismo evento repetido. Para deduplicar: en los eventos de firma, por `document_id` (si ese documento ya tiene numero guardado, descartar); en `documents.notified`, por el par (`case.id`, `documents[].id`). **`sent_at` no sirve para deduplicar**: se refresca en cada reintento.

## Probar el webhook (sandbox)

```
POST /api/v1/tad/webhook/test
```

Dispara un webhook de **prueba** al `webhook_url` configurado en tu API Key TAD, firmado con el **mismo HMAC** que un webhook real. Sirve para verificar que tu receptor recibe el `POST` y valida bien la firma, **sin depender de un tramite real ni tocar produccion**. No lleva `X-Citizen-ID` ni body.

El evento es `webhook.test` (no `documents.notified`) y trae datos ficticios: tu receptor debe reconocerlo y **no** procesarlo como una notificacion real.

```bash
curl -X POST "https://gateway.your-domain.com/api/v1/tad/webhook/test" \
  -H "X-API-Key: tu-api-key-tad"
```

La respuesta te dice **que respondio tu propio servidor** (la llamada es sincrona):

```json
{
  "delivered": true,
  "webhook_url": "https://portal.tu-muni.gob.ar/avisos-gdi",
  "status_code": 200,
  "signature": "t=1784924465,v1=4//7q...",
  "event": "webhook.test",
  "error": null
}
```

- `delivered: true` → tu servidor respondio `2xx`: recibe y (si tu codigo valida la firma) el circuito funciona.
- `delivered: false` con `status_code` → tu servidor respondio pero con error (revisar tu handler); con `status_code: null` y `error` → GDI no pudo ni conectar (URL mal, DNS, TLS, timeout, firewall).
- `422` → tu municipio todavia no tiene una API Key TAD con `webhook_url` y secret configurados en BackOffice.

El cuerpo del `webhook.test` que recibe tu servidor tiene la misma forma que `documents.notified`, mas un campo `note` que aclara que es una prueba:

```json
{
  "event": "webhook.test",
  "sent_at": "2026-07-24T20:00:00.000Z",
  "municipality": {"name": "...", "acronym": "..."},
  "citizen": {"id": "00000000-...", "country_id": "20000000001", "full_name": "Ciudadano de Prueba"},
  "case": {"id": "00000000-...", "number": "EE-2026-000000-TEST-XXXX", "reference": "Expediente de prueba (webhook.test)"},
  "documents": [{"id": "00000000-...", "official_number": "TEST-2026-00000000-XXXX-TAD", "name": "Documento de prueba", "url": "https://ejemplo.invalido/documento-de-prueba.pdf"}],
  "note": "Webhook de PRUEBA disparado desde POST /api/v1/tad/webhook/test. No corresponde a un tramite real."
}
```
