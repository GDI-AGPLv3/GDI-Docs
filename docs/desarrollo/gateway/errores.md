---
title: Errores y Codigos
description: Referencia completa de codigos de error, mensajes y troubleshooting del Gateway GDI.
---

# Errores y Códigos

Referencia completa de los códigos HTTP, mensajes de error y guía de troubleshooting para la API del Gateway.

---

## Códigos HTTP

| Código | Significado | Cuando ocurre |
|--------|------------|---------------|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado (POST create) |
| 400 | Bad Request | Parámetros inválidos, body mal formado |
| 401 | Unauthorized | API Key inválida, falta header, usuario no autorizado |
| 403 | Forbidden | Sin permisos para la operación |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Estado inválido (ej: firmar documento ya firmado) |
| 422 | Unprocessable Entity | Validación fallida |
| 429 | Too Many Requests | Rate limit de la API Key, o cola de firma saturada. Trae `Retry-After` (ver abajo) |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servidor ocupado o una verificación que no se pudo hacer. Trae `Retry-After` |

Cambios recientes en estos códigos: [Cambios de la API](changelog.md).

---

## Formato de error

Todas las respuestas de error siguen el mismo formato JSON:

```json
{
  "error": "Descripcion del error"
}
```

---

## Errores de autenticación (401)

Estos errores ocurren cuando las credenciales son inválidas o están ausentes.

| Mensaje | Causa |
|---------|-------|
| `X-API-Key header requerido` | No se incluyo el header `X-API-Key` en la petición |
| `X-User-ID header requerido para REST API` | No se incluyo el header `X-User-ID` en la petición |
| `API Key inválida` | La API Key no existe. También sale si trae caracteres no ASCII |
| `API Key inactiva` | El municipio desactivó la API Key |
| `API Key expirada` | La API Key pasó su fecha de vencimiento |
| `Municipalidad inactiva` | El municipio de la API Key está inactivo |
| `Usuario no autorizado para esta API Key` | El `X-User-ID` no está asociado a la API Key, o el municipio dio de baja a ese usuario |

**Ejemplo de respuesta:**

```json
{
  "error": "X-API-Key header requerido"
}
```

```bash
# Peticion incorrecta (falta X-API-Key)
curl -X GET "https://gateway.your-domain.com/api/v1/cases/search?search=test" \
  -H "X-User-ID: uuid-del-usuario"
# Respuesta: 401 {"error": "X-API-Key header requerido"}

# Peticion correcta
curl -X GET "https://gateway.your-domain.com/api/v1/cases/search?search=test" \
  -H "X-API-Key: tu-api-key" \
  -H "X-User-ID: uuid-del-usuario"
```

---

## Errores de validación (400)

Estos errores ocurren cuando el body o los parámetros de la petición son inválidos.

| Mensaje | Causa |
|---------|-------|
| `case_id es requerido` | No se proporcionó el `case_id` en el body |
| `document_id es requerido` | No se proporcionó el `document_id` en el body |
| `Body JSON invalido` | El body no es JSON válido o no se envió `Content-Type: application/json` |
| `document_type_acronym es requerido` | Falta el tipo de documento al crear un documento |
| `reference es requerido` | Falta la referencia al crear un recurso |
| `reason es requerido y no puede estar vacio` | Falta el motivo en operaciones que lo requieren (ej: transferencia) |
| `El parametro 'q' es requerido y debe tener al menos 2 caracteres` | La búsqueda requiere al menos 2 caracteres |
| `document_id inválido (se espera UUID)` | Un id del path o del body no es un UUID. El mismo texto sale con `case_id`, `record_id`, `proposed_id`, `document_draft_id`, `relation_id` o `link_id` |

**Ejemplo de respuesta:**

```json
{
  "error": "document_type_acronym es requerido"
}
```

---

## Errores de estado (409)

Estos errores ocurren cuando se intenta realizar una operación incompatible con el estado actual del recurso.

| Mensaje | Causa |
|---------|-------|
| `Documento no puede editarse en su estado actual` | Se intentó editar un documento que ya no está en estado `draft` |
| `Documento no puede firmarse en su estado actual` | Se intentó firmar un documento que no está en estado `sent_to_sign` |
| `Documento no puede rechazarse en su estado actual` | Se intentó rechazar un documento que no está en un estado que permita rechazo |
| `Solo se pueden eliminar documentos en estado draft o rejected` | Se intentó eliminar un documento en un estado no permitido |
| `Solo se puede reemplazar PDF en documentos draft o rejected` | Se intentó reemplazar el PDF de un documento importado que está en firma o ya es oficial |
| `El documento '<id>' ya fue rechazado y no puede ser modificado` | Se intentó rechazar un documento que ya estaba rechazado |
| `No se puede rechazar un documento completado` | Se intentó rechazar un documento oficial (ya numerado) |
| `El documento '<id>' fue firmado y convertido en acto oficial durante el proceso de rechazo...` | El documento se firmó mientras se lo rechazaba. Quedó firmado; el rechazo no se aplicó |

**Ejemplo de respuesta:**

```json
{
  "error": "Documento no puede firmarse en su estado actual"
}
```

!!! warning "Diagrama de estados de documento"
    Los documentos siguen un ciclo de vida estricto: `draft` -> `sent_to_sign` -> `signed`. Una vez que un documento sale de `draft`, no puede volver a editarse. Consulta la documentación de la REST API para ver el diagrama completo de estados.

---

## Errores de permisos (403)

Estos errores ocurren cuando el usuario autenticado no tiene los permisos necesarios para la operación.

| Mensaje | Causa |
|---------|-------|
| `Sin permisos para asignar` | El usuario no tiene permiso para asignar el expediente |
| `Sin permisos para transferir` | El usuario no tiene permiso para transferir el expediente |
| `Usuario no autorizado para firmar este documento` | El usuario no está en la lista de firmantes del documento |
| `Sin permiso de rango para numerar '<tipo>'...` | El numerador no tiene el rango que pide el tipo de documento |
| `Sin permisos para vincular documento` | El usuario no tiene permiso para vincular documentos al expediente |

**Ejemplo de respuesta:**

```json
{
  "error": "Usuario no autorizado para firmar este documento"
}
```

---

## Esperas: 429 y 503

Estas respuestas traen la cabecera `Retry-After` con los segundos que hay que esperar.

| Código | Mensaje (ejemplo) | Qué hacer |
|--------|-------------------|-----------|
| `429` | Rate limit de la API Key | Esperar `Retry-After` y bajar el ritmo de pedidos |
| `429` | `El sistema de firma está temporalmente saturado. Reintentá en ~30 segundos.` | Esperar `Retry-After` y reintentar una vez |
| `429` sin `Retry-After` | `El sistema de firma no puede procesar esta cola en este momento y necesita intervención manual. Contactá a soporte.` | No reintentar: avisar al municipio |
| `503` | `Servidor ocupado, reintente en unos segundos` | Esperar `Retry-After` y reintentar |
| `503` | `No pudimos verificar el PDF certificado de origen. Reintentá en unos segundos.` (con `"code": "CERTIFIED_CHECK_RETRY"`) | Esperar `Retry-After` y reintentar la firma |

---

## Troubleshooting común

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| Siempre recibo 401 | API Key incorrecta o expirada | Verificar la API Key con el administrador del municipio. Asegurarse de enviar ambos headers (`X-API-Key` y `X-User-ID`) |
| 404 al buscar expediente | UUID incorrecto o el usuario no tiene permisos sobre ese expediente | Usar el endpoint de búsqueda (`/cases/search`) primero para obtener el UUID correcto |
| 409 al firmar | El documento no está en estado `sent_to_sign` | Verificar el estado actual del documento con `GET /documents/{id}`. Si está en `draft`, primero ejecutar `start-signing` |
| 500 intermitente | El servidor está en cold start (primer request después de inactividad) | Reintentar la petición después de 10 segundos. Los cold starts solo ocurren tras periodos de inactividad |
| Body JSON inválido con 400 | Falta el header `Content-Type` o el JSON está mal formado | Verificar que se envía `Content-Type: application/json` y que el body es JSON válido |
| 403 al transferir expediente | El usuario no es el responsable actual del expediente | Solo el usuario asignado al expediente puede transferirlo. Verificar la asignación |
| Timeout en requests | El servidor está procesando una operación pesada (ej: firma con PDF grande) | Aumentar el timeout del cliente. Las firmas pueden tomar hasta 30 segundos para PDFs grandes |

---

## Buenas prácticas para manejo de errores

1. **Siempre verificar el código HTTP** antes de procesar la respuesta.
2. **Parsear el campo `error`** del JSON de respuesta para mostrar mensajes claros al usuario.
3. **Implementar reintentos** para errores 500 con backoff exponencial (máximo 3 reintentos).
4. **No reintentar** errores 400, 401, 403, 404 o 409 sin modificar la petición.
5. **Respetar `Retry-After`** en los `429` y `503`: esperar esos segundos antes del reintento.
6. **Loguear el request y response** completos para facilitar el debugging.

```python
import requests
import time

def call_gateway(method, path, **kwargs):
    """Ejemplo de cliente con reintentos para errores 500."""
    url = f"https://gateway.your-domain.com{path}"
    headers = {
        "X-API-Key": "tu-api-key",
        "X-User-ID": "uuid-del-usuario",
    }
    headers.update(kwargs.pop("headers", {}))

    for attempt in range(3):
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code < 500:
            return response

        # Backoff exponencial para errores 500
        wait = 2 ** attempt
        time.sleep(wait)

    return response  # Retornar ultimo intento
```
