# REST API

API REST publica del Gateway con **45 endpoints** para integraciones programaticas con el sistema de gestion documental.

---

## Base URL

```
https://gateway.tu-municipio.gdilatam.com/api/v1
```

Reemplazar `tu-municipio` por el identificador de tu municipio asignado por GDI Latam.

---

## Autenticacion

Todas las peticiones requieren dos headers obligatorios:

| Header | Tipo | Descripcion |
|--------|------|-------------|
| `X-API-Key` | string | Clave de API asignada al municipio |
| `X-User-ID` | UUID | Identificador del usuario que realiza la accion |

Para mas detalles sobre como obtener y gestionar las credenciales, consultar la [guia de autenticacion](../autenticacion.md).

!!! warning "Headers obligatorios"
    Las peticiones sin `X-API-Key` recibiran un error `401 Unauthorized`. Algunos endpoints permiten omitir `X-User-ID` (se indica en cada caso), pero la mayoria lo requieren para validar permisos.

---

## Formato de respuesta

### Respuesta exitosa

Las respuestas exitosas devuelven JSON con los datos solicitados y el codigo HTTP correspondiente (`200`, `201`, etc.).

```json
{
  "cases": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### Respuesta de error

Los errores devuelven un objeto JSON con el campo `error` y el codigo HTTP apropiado:

```json
{
  "error": "Case not found"
}
```

| Codigo HTTP | Significado |
|-------------|-------------|
| `400` | Solicitud invalida (parametros faltantes o incorrectos) |
| `401` | No autenticado (API key invalida o ausente) |
| `403` | Sin permisos para la operacion |
| `404` | Recurso no encontrado |
| `422` | Error de validacion en los datos enviados |
| `500` | Error interno del servidor |

---

## Paginacion

Los endpoints que devuelven listas soportan paginacion con los siguientes parametros query:

| Parametro | Tipo | Default | Descripcion |
|-----------|------|---------|-------------|
| `page` | int | `1` | Numero de pagina |
| `page_size` | int | `20` | Cantidad de resultados por pagina (maximo `100`) |

La respuesta incluye metadatos de paginacion:

```json
{
  "data": [...],
  "total": 150,
  "page": 2,
  "page_size": 20,
  "total_pages": 8
}
```

---

## Endpoints por dominio

### Expedientes (13 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/cases/search` | Buscar expedientes con filtros |
| `GET` | `/cases/{case_id}` | Detalle de un expediente |
| `GET` | `/cases/number/{case_number}` | Buscar expediente por numero exacto |
| `GET` | `/cases/{case_id}/history` | Historial de movimientos |
| `GET` | `/cases/{case_id}/documents` | Documentos del expediente |
| `GET` | `/cases/{case_id}/permissions` | Permisos del usuario sobre el expediente |
| `GET` | `/cases/{case_id}/prepare-assignment` | Preparar datos para asignacion |
| `GET` | `/cases/{case_id}/prepare-transfer` | Preparar datos para transferencia |
| `GET` | `/cases/sectors/{sector_id}/users` | Usuarios de un sector |
| `POST` | `/cases/` | Crear expediente |
| `POST` | `/cases/{case_id}/transfer` | Transferir expediente a otro sector |
| `POST` | `/cases/{case_id}/assign` | Asignar expediente a usuario |
| `POST` | `/cases/{case_id}/close-assign` | Cerrar asignacion activa |

Documentacion completa: [Expedientes](expedientes.md)

---

### Documentos (20 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/documents/search` | Buscar documentos con filtros |
| `GET` | `/documents/pending-signatures` | Documentos pendientes de firma |
| `GET` | `/documents/{document_id}` | Detalle de un documento |
| `GET` | `/documents/{document_id}/content` | Contenido HTML del documento |
| `GET` | `/documents/{document_id}/url` | URL temporal para descargar PDF |
| `GET` | `/documents/{document_id}/signature-details` | Detalles de firma |
| `GET` | `/documents/search-official/{doc_number}` | Buscar documento oficial por numero |
| `GET` | `/documents/check-signer-permissions` | Verificar permisos de firma |
| `POST` | `/documents/` | Crear documento borrador |
| `POST` | `/documents/import` | Importar PDF externo |
| `PATCH` | `/documents/{document_id}` | Guardar cambios en borrador |
| `PUT` | `/documents/{document_id}/imported-pdf` | Reemplazar PDF importado |
| `DELETE` | `/documents/{document_id}` | Eliminar borrador |
| `POST` | `/documents/{document_id}/start-signing` | Iniciar proceso de firma |
| `POST` | `/documents/{document_id}/sign` | Firmar documento |
| `POST` | `/documents/{document_id}/reject` | Rechazar documento |
| `POST` | `/cases/{case_id}/documents/link` | Vincular documento oficial a expediente |
| `POST` | `/cases/{case_id}/documents/propose` | Proponer borrador a expediente |
| `POST` | `/cases/{case_id}/documents/accept-proposal` | Aceptar propuesta de documento |
| `POST` | `/cases/{case_id}/documents/reject-proposal` | Rechazar propuesta de documento |

Documentacion completa: [Documentos](documentos.md)

---

### Sistema y Catalogos (7 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/system/document-types` | Tipos de documentos activos |
| `GET` | `/system/document-states` | Estados posibles de documentos |
| `GET` | `/system/sectors` | Sectores con departamentos |
| `GET` | `/system/case-templates` | Plantillas de expedientes |
| `GET` | `/system/users/list` | Listar todos los usuarios del tenant |
| `GET` | `/system/users/search` | Buscar usuarios (autocompletado) |
| `GET` | `/system/users/{user_id}` | Informacion de un usuario |

Documentacion completa: [Sistema y Catalogos](sistema.md)

---

### Notas (5 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/notes/received` | Notas recibidas |
| `GET` | `/notes/sent` | Notas enviadas |
| `GET` | `/notes/archived` | Notas archivadas |
| `GET` | `/notes/{note_id}` | Detalle de una nota |
| `PATCH` | `/notes/{note_id}/archive` | Archivar o desarchivar nota |

Documentacion completa: [Notas](notas.md)

---

### Legajos - RLM (endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/records/search` | Buscar legajos con filtros |
| `GET` | `/records/{record_id}` | Detalle de un legajo |
| `GET` | `/records/families` | Familias de registro disponibles |
| `POST` | `/records/` | Crear legajo |
| `PATCH` | `/records/{record_id}` | Actualizar legajo |

Documentacion completa: [Legajos (RLM)](legajos.md)
