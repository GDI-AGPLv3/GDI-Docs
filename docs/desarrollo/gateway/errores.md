---
title: Errores y Codigos
description: Referencia completa de codigos de error, mensajes y troubleshooting del Gateway GDI.
---

# Errores y Codigos

Referencia completa de los codigos HTTP, mensajes de error y guia de troubleshooting para la API del Gateway.

---

## Codigos HTTP

| Codigo | Significado | Cuando ocurre |
|--------|------------|---------------|
| 200 | OK | Operacion exitosa |
| 201 | Created | Recurso creado (POST create) |
| 400 | Bad Request | Parametros invalidos, body mal formado |
| 401 | Unauthorized | API Key invalida, falta header, usuario no autorizado |
| 403 | Forbidden | Sin permisos para la operacion |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Estado invalido (ej: firmar documento ya firmado) |
| 422 | Unprocessable Entity | Validacion fallida |
| 500 | Internal Server Error | Error del servidor |

---

## Formato de error

Todas las respuestas de error siguen el mismo formato JSON:

```json
{
  "error": "Descripcion del error"
}
```

---

## Errores de autenticacion (401)

Estos errores ocurren cuando las credenciales son invalidas o estan ausentes.

| Mensaje | Causa |
|---------|-------|
| `X-API-Key header requerido` | No se incluyo el header `X-API-Key` en la peticion |
| `X-User-ID header requerido para REST API` | No se incluyo el header `X-User-ID` en la peticion |
| `API Key invalida o expirada` | La API Key proporcionada no existe o ha expirado |
| `Usuario no autorizado para esta API Key` | El `X-User-ID` no esta asociado a la API Key utilizada |

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

## Errores de validacion (400)

Estos errores ocurren cuando el body o los parametros de la peticion son invalidos.

| Mensaje | Causa |
|---------|-------|
| `case_id es requerido` | No se proporciono el `case_id` en el body |
| `document_id es requerido` | No se proporciono el `document_id` en el body |
| `Body JSON invalido` | El body no es JSON valido o no se envio `Content-Type: application/json` |
| `document_type_acronym es requerido` | Falta el tipo de documento al crear un documento |
| `reference es requerido` | Falta la referencia al crear un recurso |
| `reason es requerido y no puede estar vacio` | Falta el motivo en operaciones que lo requieren (ej: transferencia) |
| `El parametro 'q' es requerido y debe tener al menos 2 caracteres` | La busqueda requiere al menos 2 caracteres |

**Ejemplo de respuesta:**

```json
{
  "error": "document_type_acronym es requerido"
}
```

---

## Errores de estado (409)

Estos errores ocurren cuando se intenta realizar una operacion incompatible con el estado actual del recurso.

| Mensaje | Causa |
|---------|-------|
| `Documento no puede editarse en su estado actual` | Se intento editar un documento que ya no esta en estado `draft` |
| `Documento no puede firmarse en su estado actual` | Se intento firmar un documento que no esta en estado `sent_to_sign` |
| `Documento no puede rechazarse en su estado actual` | Se intento rechazar un documento que no esta en un estado que permita rechazo |
| `Solo se pueden eliminar documentos en estado draft o rejected` | Se intento eliminar un documento en un estado no permitido |
| `Solo se puede reemplazar PDF en documentos draft` | Se intento reemplazar el PDF de un documento importado que ya no esta en `draft` |

**Ejemplo de respuesta:**

```json
{
  "error": "Documento no puede firmarse en su estado actual"
}
```

!!! warning "Diagrama de estados de documento"
    Los documentos siguen un ciclo de vida estricto: `draft` -> `sent_to_sign` -> `signed`. Una vez que un documento sale de `draft`, no puede volver a editarse. Consulta la documentacion de la REST API para ver el diagrama completo de estados.

---

## Errores de permisos (403)

Estos errores ocurren cuando el usuario autenticado no tiene los permisos necesarios para la operacion.

| Mensaje | Causa |
|---------|-------|
| `Sin permisos para asignar` | El usuario no tiene permiso para asignar el expediente |
| `Sin permisos para transferir` | El usuario no tiene permiso para transferir el expediente |
| `Usuario no autorizado para firmar este documento` | El usuario no esta en la lista de firmantes del documento |
| `Sin permisos para vincular documento` | El usuario no tiene permiso para vincular documentos al expediente |

**Ejemplo de respuesta:**

```json
{
  "error": "Usuario no autorizado para firmar este documento"
}
```

---

## Troubleshooting comun

| Problema | Causa probable | Solucion |
|----------|---------------|----------|
| Siempre recibo 401 | API Key incorrecta o expirada | Verificar la API Key con el administrador del municipio. Asegurarse de enviar ambos headers (`X-API-Key` y `X-User-ID`) |
| 404 al buscar expediente | UUID incorrecto o el usuario no tiene permisos sobre ese expediente | Usar el endpoint de busqueda (`/cases/search`) primero para obtener el UUID correcto |
| 409 al firmar | El documento no esta en estado `sent_to_sign` | Verificar el estado actual del documento con `GET /documents/{id}`. Si esta en `draft`, primero ejecutar `start-signing` |
| 500 intermitente | El servidor esta en cold start (primer request despues de inactividad) | Reintentar la peticion despues de 10 segundos. Los cold starts solo ocurren tras periodos de inactividad |
| Body JSON invalido con 400 | Falta el header `Content-Type` o el JSON esta mal formado | Verificar que se envia `Content-Type: application/json` y que el body es JSON valido |
| 403 al transferir expediente | El usuario no es el responsable actual del expediente | Solo el usuario asignado al expediente puede transferirlo. Verificar la asignacion |
| Timeout en requests | El servidor esta procesando una operacion pesada (ej: firma con PDF grande) | Aumentar el timeout del cliente. Las firmas pueden tomar hasta 30 segundos para PDFs grandes |

---

## Buenas practicas para manejo de errores

1. **Siempre verificar el codigo HTTP** antes de procesar la respuesta.
2. **Parsear el campo `error`** del JSON de respuesta para mostrar mensajes claros al usuario.
3. **Implementar reintentos** para errores 500 con backoff exponencial (maximo 3 reintentos).
4. **No reintentar** errores 400, 401, 403, 404 o 409 sin modificar la peticion.
5. **Loguear el request y response** completos para facilitar el debugging.

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
