# Webhook de notificaciones

Cuando un agente municipal **notifica documentos** de un expediente a un ciudadano desde la app GDI, GDI envia un `POST` a la URL de callback configurada en la API Key TAD (BackOffice → `/api-key`). Asi el portal se entera de novedades sin hacer polling.

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
- La entrega es **al menos una vez**: ante reintentos el portal puede recibir el mismo evento repetido. Usar el par (`case.id`, `sent_at`) o el contenido de `documents` para deduplicar.
