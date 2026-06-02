# REST API

API REST publica del Gateway con **80+ endpoints** para integraciones programaticas con el sistema de gestion documental.

---

## Base URL

```
https://gateway.your-domain.com/api/v1
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

### Expedientes (19 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/cases/search` | Buscar expedientes con filtros |
| `GET` | `/cases/{case_id}` | Detalle de un expediente |
| `GET` | `/cases/number/{case_number}` | Buscar expediente por numero exacto |
| `GET` | `/cases/{case_id}/history` | Historial de movimientos con resumen IA |
| `GET` | `/cases/{case_id}/documents` | Documentos del expediente |
| `GET` | `/cases/{case_id}/permissions` | Permisos del usuario sobre el expediente |
| `GET` | `/cases/{case_id}/prepare-assignment` | Preparar datos para asignacion |
| `GET` | `/cases/{case_id}/prepare-transfer` | Preparar datos para transferencia |
| `GET` | `/cases/{case_id}/movements` | Movimientos del expediente (plano, sin IA) |
| `GET` | `/cases/{case_id}/responsibles` | Responsables activos del expediente |
| `GET` | `/cases/sectors/{sector_id}/users` | Usuarios de un sector |
| `POST` | `/cases/` | Crear expediente |
| `POST` | `/cases/{case_id}/transfer` | Transferir expediente a otro sector |
| `POST` | `/cases/{case_id}/assign` | Asignar expediente a sector |
| `POST` | `/cases/{case_id}/close-assign` | Cerrar asignacion activa |
| `POST` | `/cases/{case_id}/responsibles` | Agregar responsable al expediente |
| `POST` | `/cases/{case_id}/subsanar` | Subsanar documento oficial erroneo |
| `DELETE` | `/cases/{case_id}/responsibles/{responsible_id}` | Quitar responsable del expediente |

Documentacion completa: [Expedientes](expedientes.md)

---

### Documentos (20 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/documents/search` | Buscar documentos con filtros |
| `GET` | `/documents/pending-signatures` | Documentos pendientes de firma |
| `GET` | `/documents/{document_id}` | Detalle de un documento |
| `GET` | `/documents/{document_id}/content` | Contenido HTML del documento (solo oficiales) |
| `GET` | `/documents/{document_id}/url` | URL temporal para descargar PDF |
| `GET` | `/documents/{document_id}/signature-details` | Detalles de firma |
| `GET` | `/documents/search-official/{doc_number}` | Buscar documento oficial por numero |
| `GET` | `/documents/check-signer-permissions` | Verificar permisos de firma de un usuario |
| `POST` | `/documents/` | Crear documento borrador |
| `POST` | `/documents/import` | Importar PDF externo (multipart/form-data) |
| `PATCH` | `/documents/{document_id}` | Guardar cambios en borrador |
| `PUT` | `/documents/{document_id}/imported-pdf` | Reemplazar PDF importado |
| `DELETE` | `/documents/{document_id}` | Eliminar borrador o rechazado |
| `POST` | `/documents/{document_id}/start-signing` | Iniciar proceso de firma |
| `POST` | `/documents/{document_id}/sign` | Firmar documento (solo firma electronica) |
| `POST` | `/documents/{document_id}/reject` | Rechazar documento |
| `POST` | `/cases/{case_id}/documents/link` | Vincular documento oficial a expediente |
| `POST` | `/cases/{case_id}/documents/propose` | Proponer borrador a expediente |
| `POST` | `/cases/{case_id}/documents/accept-proposal` | Aceptar propuesta de documento |
| `POST` | `/cases/{case_id}/documents/reject-proposal` | Rechazar propuesta de documento |

!!! warning "Firma digital con token fisico"
    `POST /documents/{id}/sign` solo acepta firma electronica. Documentos con `signature_policy=digital_all` o numeradores con `digital_num` devuelven `422` e instruyen al usuario a firmar desde el portal web con FirmadorGDI.

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
| `GET` | `/system/users/search` | Buscar usuarios por nombre (autocompletado) |
| `GET` | `/system/users/{user_id}` | Informacion de un usuario (solo propia) |

!!! note "Restriccion en GET /system/users/{user_id}"
    Por seguridad (SEC-12), el usuario solo puede consultar su propia informacion. Intentar consultar otro `user_id` devuelve `403`.

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

### Memos (4 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/memos/received` | Memos recibidos del usuario |
| `GET` | `/memos/sent` | Memos enviados por el usuario |
| `GET` | `/memos/archived` | Memos archivados del usuario |
| `GET` | `/memos/{memo_id}` | Detalle de un memo |

---

### Busqueda Semantica (1 endpoint)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/search/semantic` | Busqueda semantica vectorial sobre documentos |

**Parametros query:** `query` (requerido, min 3 chars), `limit` (default 20, max 50).

---

### Legajos - RLM (18 endpoints)

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/records/search` | Buscar legajos con filtros |
| `GET` | `/records/{record_id}` | Detalle de un legajo |
| `GET` | `/records/families` | Familias de registro disponibles |
| `GET` | `/records/{record_id}/history` | Historial del legajo |
| `GET` | `/records/{record_id}/relations` | Relaciones con otros legajos |
| `GET` | `/records/{record_id}/cases` | Expedientes vinculados |
| `GET` | `/records/{record_id}/documents` | Documentos vinculados |
| `POST` | `/records` | Crear legajo |
| `PATCH` | `/records/{record_id}` | Actualizar estado o nombre |
| `PATCH` | `/records/{record_id}/fields/{field_name}` | Actualizar campo del legajo |
| `POST` | `/records/{record_id}/fields/{field_name}/verify` | Verificar campo con documento oficial |
| `POST` | `/records/{record_id}/report` | Generar informe IFRLM |
| `POST` | `/records/{record_id}/relations` | Crear relacion entre legajos |
| `DELETE` | `/records/{record_id}/relations/{relation_id}` | Eliminar relacion |
| `POST` | `/records/{record_id}/cases` | Vincular expediente al legajo |
| `DELETE` | `/records/{record_id}/cases/{link_id}` | Desvincular expediente |
| `POST` | `/records/{record_id}/documents` | Vincular documento al legajo |
| `DELETE` | `/records/{record_id}/documents/{link_id}` | Desvincular documento |

Ademas, `/registries` es un alias de `/records/families`.

Documentacion completa: [Legajos (RLM)](legajos.md)

---

### Backup / Sync (3 endpoints)

!!! warning "Autenticacion especial"
    Estos endpoints usan **Backup API Keys** (`key_type='backup'`). No requieren `X-User-ID`. Validan IP de origen y aplican rate limiting por accion.

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/sync/schema` | Catalogo de tablas sincronizables |
| `GET` | `/sync/data` | Datos incrementales de una tabla |
| `GET` | `/sync/documents` | PDFs firmados con presigned URLs |

**Parametros `/sync/data`:** `table` (requerido), `since` (ISO 8601, requerido), `page`, `page_size` (max 100).

**Parametros `/sync/documents`:** `since` (ISO 8601, requerido), `page`, `page_size` (max 100).
