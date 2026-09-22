# Referencia de endpoints — API del BackOffice GDI

> Generado desde el OpenAPI del BackOffice con `scripts/build_backoffice_endpoints.py`.
> No editar a mano: regenerar.

Todos los endpoints llevan los 3 headers de autenticación (`X-API-Key`, `X-Tenant-Schema`,
`X-User-ID`) y exigen que el usuario tenga rol **Administrador**. Las rutas son relativas
a `$GDI_BO_URL`. Los marcados con ⚠️ borran datos o cortan accesos: se confirman con el
administrador antes de ejecutarlos.

105 endpoints.

## Índice

- Usuarios (20)
- Reparticiones (departments) (8)
- Sectores (5)
- Rangos jerárquicos (4)
- Sellos del municipio (4)
- Tipos de documento (12)
- Tipos de expediente (case templates) (8)
- Familias de legajos (12)
- Configuración del municipio (3)
- Ciudadanos (Base TAD) (3)
- API Keys (8)
- Certificados de firma (7)
- Estadísticas (7)
- Auditoría (1)
- Organigrama (1)
- Propuestas al catálogo global (2)

## Usuarios

### `GET /admin/users`

Listar todos los usuarios con roles

Lista todos los usuarios del sistema con informacion completa incluyendo roles asignados.

**Requiere:**
- Token JWT valido
- Rol de Administrador (role_id = 'a0000000-0000-0000-0000-000000000003')

**Respuesta incluye:**
- Datos personales (email, nombre, CUIT)
- Informacion de sector y departamento
- Estado del usuario (activo/inactivo)
- Fechas de creacion y ultimo acceso
- Lista de roles asignados con nombre y descripcion

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `search` | query | string |  | filtra por email/nombre; incluye usuarios archivados |
| `estado` | query | integer |  | filtro exacto por estado (0=Inactivo, 1=Activo, 2=Pendiente, 5=Archivado). Si se pasa, desactiva la exclusion default de archivados. |
| `department_id` | query | string |  | filtro por UUID de departamento (via sector). |
| `role_id` | query | string |  | Solo usuarios que tienen este rol (UUID). Ej: Administrador. |
| `exclude_role_id` | query | string |  | Solo usuarios que NO tienen este rol (UUID). |
| `limit` | query | integer |  | Cantidad maxima de usuarios a devolver (1-500). Default: 100. |
| `offset` | query | integer |  | Desplazamiento para paginacion. Default: 0. |

### `POST /admin/users`

Crear nuevo usuario

Crea un nuevo usuario en el sistema.

**Campos requeridos:**
- email: Email unico del usuario
- full_name: Nombre completo
- sector_id: UUID del sector principal

**Campos opcionales:**
- country_id: CUIT/DNI
- role_ids: Lista de UUIDs de roles a asignar

**Notas:**
- El email se guarda en minusculas
- El usuario se crea con estado=1 (activo)
- auth_id se llenara automaticamente cuando el usuario haga login en Auth0

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `email` | string (email) | sí | Email del usuario (unico) |
| `full_name` | string | sí | Nombre completo |
| `sector_id` | string (uuid) | sí | UUID del sector principal |
| `country_id` | string |  | CUIT/DNI (opcional) |
| `role_ids` | lista de string (uuid) |  | UUIDs de roles a asignar Default: `[]`. |
| `city_seal_id` | integer | sí | ID del sello obligatorio |
| `can_global_search_documents` | boolean |  | Puede buscar documentos de cualquier sector Default: `false`. |
| `can_global_search_cases` | boolean |  | Puede buscar expedientes de cualquier sector Default: `false`. |
| `auth_method` | `social` \| `database` |  | Metodo de autenticacion: 'social' (Google/Microsoft) o 'database' (email+password) Default: `"social"`. |
| `as_backoffice_admin` | boolean |  | si es True, usa el flujo de alta de Administrador del BackOffice (rol Administrador auto-asignado, auth_method forzado a 'database', ticket de activacion y mail con el client_id del BackOffice). Default: `false`. |

### `GET /admin/users/emails`

Emails de usuarios activos (para dedupe en creacion masiva)

**** endpoint liviano que devuelve solo los emails (en minuscula) de
los usuarios NO archivados del tenant. El modal de creacion masiva del BO lo
usa para avisar duplicados sin tener que rehidratar el listado paginado
completo. Excluye archivados (estado=5), el AI worker y el rol Sistema TEST,
igual que el modo default de `GET /admin/users`.

IMPORTANTE: esta ruta va ANTES de `/users/{user_id}` para que FastAPI no
matchee 'emails' como un `user_id`.

### `GET /admin/users/{user_id}`

Obtener detalle de un usuario

Obtiene informacion completa de un usuario especifico incluyendo roles.

**Respuesta incluye:**
- Datos personales completos
- Sector y departamento
- Lista de roles asignados
- Fechas de creacion y ultimo acceso

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `PATCH /admin/users/{user_id}`

Actualizar usuario

Actualiza un usuario existente (actualizacion parcial - PATCH).

**Campos actualizables:**
- full_name: Nombre completo
- sector_id: UUID del sector principal
- country_id: CUIT/DNI

Solo se actualizan los campos enviados en el request.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `full_name` | string |  | Nombre completo |
| `sector_id` | string (uuid) |  | UUID del sector principal |
| `country_id` | string |  | CUIT/DNI |
| `can_global_search_documents` | boolean |  | Puede buscar documentos de cualquier sector |
| `can_global_search_cases` | boolean |  | Puede buscar expedientes de cualquier sector |

### `DELETE /admin/users/{user_id}` ⚠️ requiere confirmación

Borrar usuario definitivamente

Hard delete de un usuario. - Sin actividad -> se borra (BD + Auth0 database si corresponde).
- Con actividad -> 409 con detalle; el admin debe desactivar o archivar.

Auth0: solo se elimina la identidad si `auth_method='database'` Y su email no queda en ningun otro tenant. Cuentas social NO se tocan. Fallo de Auth0 = warning no fatal (el usuario ya salio de la BD).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario a borrar |

### `PATCH /admin/users/{user_id}/email` ⚠️ requiere confirmación

Cambiar email de login

Cambia el email de login de un usuario. Resetea `auth_id` (re-link en el
proximo login). Si el usuario es `database`, primero actualiza el email
en Auth0; si es `social`, solo se cambia en BD (el email lo posee el IdP).

**Bloqueos:**
- Email ya en uso en el mismo municipio (409).
- Email ya en uso en OTRO municipio de la plataforma (409, C1).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `new_email` | string (email) | sí | Nuevo email de login (unico en el schema) |

### `PATCH /admin/users/{user_id}/auth-method` ⚠️ requiere confirmación

Cambiar metodo de acceso (social/database)

Cambia el metodo de autenticacion del usuario. Resetea `auth_id`
(re-link en el proximo login con el nuevo metodo).

- **social -> database**: crea (o reusa) la identidad Auth0 Database
  Connection, genera un link de activacion y encola el mail de
  invitacion.
- **database -> social**: actualiza primero la BD (camino seguro); el
  usuario entra con Google/Microsoft usando su email actual. La identidad
  Auth0 Database vieja se borra despues (best-effort, no fatal) SOLO si
  el email no queda en uso como `database` en ningun otro tenant de la
  plataforma (mismo guard que el hard delete de .

Si el usuario ya tiene el metodo pedido, es un no-op (200).

****: si el email de este usuario es `shared_identity=true` (ver
`GET /admin/users/{id}`), este endpoint devuelve 409 `code=SHARED_IDENTITY`
en las DOS direcciones (social->database Y database->social) -- el
metodo de acceso es una propiedad de la identidad Auth0 compartida, no de
la ficha de este municipio, y no se puede tocar desde aca.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `auth_method` | `social` \| `database` | sí | Nuevo metodo de autenticacion: 'social' o 'database' |

### `GET /admin/users/{user_id}/sector-permissions`

Obtener permisos de sectores adicionales de un usuario

Retorna los sectores adicionales asignados a un usuario con sus permisos
de lectura y escritura.

**Respuesta incluye:**
- Lista de sectores con acronimo, departamento y permisos (can_view, can_edit)

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `PUT /admin/users/{user_id}/sector-permissions`

Reemplazar permisos de sectores adicionales de un usuario

Reemplaza todos los permisos de sectores adicionales del usuario.
Los permisos existentes se eliminan y se insertan los nuevos.

**Request body:**
- permissions: Lista de objetos con sector_id, can_view, can_edit

**Notas:**
- Enviar lista vacia para remover todos los permisos adicionales
- El sector principal del usuario (users.sector_id) NO se modifica

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `permissions` | lista de SectorPermissionItem |  | Lista de permisos a asignar (reemplaza los existentes) Default: `[]`. |

### `GET /admin/users/{user_id}/seal`

Obtener sello de firma de un usuario

Retorna el sello de firma asignado al usuario.
Cada usuario puede tener maximo un sello asignado.

**Respuesta:**
- seal: Objeto con datos del sello o null si no tiene

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `PUT /admin/users/{user_id}/seal`

Asignar o remover sello de firma de un usuario

Asigna un sello de firma al usuario o lo remueve.

**Request body:**
- city_seal_id: ID del sello a asignar, o null para remover

**Notas:**
- Cada usuario puede tener maximo un sello
- Si ya tiene uno asignado, se reemplaza
- Enviar city_seal_id: null para remover el sello

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `city_seal_id` | integer |  | ID del sello a asignar (null para remover) |

### `POST /admin/users/{user_id}/admin-role` ⚠️ requiere confirmación

Asignar rol Administrador a un usuario

Asigna el rol de Administrador a un usuario activo.

**No se puede:**
- Asignar a un usuario inactivo

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `DELETE /admin/users/{user_id}/admin-role` ⚠️ requiere confirmación

Quitar rol Administrador a un usuario

Quita el rol de Administrador a un usuario.

**No se puede:**
- Quitarse el rol a si mismo
- Quitar el rol a un usuario que no lo tiene

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `POST /admin/users/{user_id}/deactivate` ⚠️ requiere confirmación

Desactivar usuario

Desactiva un usuario y rechaza automaticamente todos sus documentos
pendientes de firma con motivo "Sistema BackOffice".

**No se puede:**
- Desactivar al admin que ejecuta la accion
- Desactivar un usuario ya inactivo

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario a desactivar |

### `POST /admin/users/{user_id}/reactivate`

Reactivar usuario

Reactiva un usuario previamente desactivado.

**No se puede:**
- Reactivar al admin que ejecuta la accion
- Reactivar un usuario ya activo

**Nota importante**: Reactivar un usuario NO restaura los documentos que fueron
rechazados automaticamente al desactivarlo. Si el usuario tenia documentos
pendientes de firma cuando se lo desactivo, esos documentos quedaron en estado
'rechazado' con motivo "Sistema BackOffice" y permanecen asi. El admin debe
crear nuevos documentos si es necesario.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario a reactivar |

### `POST /admin/users/{user_id}/archive` ⚠️ requiere confirmación

Archivar usuario

Archiva un usuario (estado=5). El archivado desaparece del listado default; se ve solo en busqueda por texto con badge 'Archivado' y no puede loguear. Uso tipico: ex-empleados con actividad que no se pueden borrar.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario a archivar |

### `POST /admin/users/{user_id}/unarchive`

Desarchivar usuario

Desarchiva un usuario (estado=5 -> estado=1). Vuelve a listado y login.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario a desarchivar |

### `POST /admin/users/{user_id}/reinvite`

Reenviar invitacion o email de bienvenida

Reenvia la comunicacion al usuario segun su auth_method:

- **Database**: Genera un nuevo link de activacion y reenvia email de invitacion.
- **Social**: Reenvia el email de bienvenida con el link de acceso a la app.

Util cuando el usuario no recibio el email o necesita las instrucciones de acceso.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

### `POST /admin/users/{user_id}/activation-link`

Generar link de activacion para entrega manual

Genera un link de activacion (password change ticket de Auth0) y lo devuelve
SIN enviar ningun email, para que el admin lo entregue por otro canal
(WhatsApp, telefono, en persona) cuando el mail no llega o no existe.

Funciona siempre, tenga o no correo configurado el ambiente (SaaS u on-premise).

Solo aplica a usuarios con `auth_method = database`: los usuarios con login
social (Google/Microsoft) no tienen contraseña en GDI, entran directo con su
cuenta desde la URL de la app.

El link sirve una sola vez y vence a los 5 dias. Tratarlo como una contraseña.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `user_id` | path | string | sí | UUID del usuario |

## Reparticiones (departments)

### `GET /admin/departments`

Arbol de departamentos

Lista todos los departamentos como arbol jerarquico.

**Respuesta incluye:**
- Arbol con departamentos raiz y sus hijos
- Rank asociado a cada departamento
- Titular (head_user) de cada departamento
- Estadisticas: empleados, sectores, sub-departamentos

### `POST /admin/departments`

Crear reparticion

Crea una nueva reparticion (departamento) como hija de otra existente.

**Requiere:**
- Nombre (2-100 caracteres)
- Acronimo unico (2-20 caracteres, se convierte a mayusculas)
- ID de la reparticion padre

**Auto-crea** un sector PRIV para la nueva reparticion.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string | sí | Nombre de la reparticion |
| `acronym` | string | sí | Acronimo unico. 2-20 caracteres, letras y numeros (se guarda en mayusculas) |
| `parent_id` | string | sí | UUID de la reparticion padre |
| `rank_id` | string |  | UUID del rank (Intendente/Secretario/Director) |

### `GET /admin/departments/{department_id}/available-users`

Usuarios disponibles para asignar como titular

Lista usuarios activos que pueden ser asignados como titular de un departamento.

**Respuesta incluye:**
- Usuarios activos con nombre, email, sector y departamento actual

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |
| `limit` | query | integer |  | Cantidad maxima de usuarios a devolver (1-500). Default: 100. |
| `offset` | query | integer |  | Desplazamiento para paginacion. Default: 0. |

### `PATCH /admin/departments/{department_id}/head`

Asignar o remover titular de departamento

Asigna o remueve el titular (head_user) de un departamento.

**Para asignar:** enviar `head_user_id` con el UUID del usuario.
**Para remover:** enviar `head_user_id` como `null`.

**Al asignar:**
- El usuario se mueve al sector PRIV del departamento
- Se le asigna el sello correspondiente al rank del departamento
- Si el departamento ya tenia otro titular, se remueve primero

**Al remover:**
- Se quita el sello del usuario anterior
- Se limpia el head_user_id del departamento

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `head_user_id` | string |  | UUID del responsable (null para remover) |

### `PATCH /admin/departments/{department_id}/color`

Actualizar colores de departamento y sectores

Actualiza el color primario de un departamento y los colores de sus sectores atomicamente.

**Recibe:**
- `primary_color`: Color hex del departamento (#RRGGBB)
- `sector_colors`: Diccionario sector_id -> color hex (opcional, para override manual)

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `primary_color` | string | sí | Color hex (#RRGGBB) |
| `sector_colors` | object |  | Map sector_id -> color hex |

### `PATCH /admin/departments/{department_id}`

Actualizar nombre/acronimo/rank de reparticion

Actualiza el nombre, acronimo y/o rank de una reparticion existente.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  | Nuevo nombre |
| `acronym` | string |  | Nuevo acronimo. 2-20 caracteres, letras y numeros (se guarda en mayusculas) |
| `rank_id` | string |  | UUID del rango (null para quitar) |
| `parent_id` | string |  | UUID del departamento padre (string vacio para mover a raiz) |

### `DELETE /admin/departments/{department_id}` ⚠️ requiere confirmación

Eliminar reparticion

Elimina una reparticion si cumple todas las condiciones.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |

### `GET /admin/departments/{department_id}`

Detalle de departamento

Obtiene detalle de un departamento con sus sectores, usuarios y sub-departamentos.

**Respuesta incluye:**
- Datos del departamento (nombre, acronimo, rank, titular)
- Sectores con sus usuarios
- Usuarios con rank, sello, estado e indicador de titular
- Sub-departamentos con estadisticas

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | path | string | sí | UUID del departamento |

## Sectores

### `POST /admin/sectors`

Crear sector

Crea un nuevo sector dentro de un departamento.

**Request body:**
- `department_id`: UUID del departamento (requerido)
- `acronym`: Acronimo unico del sector (1-10 caracteres, se convierte a mayusculas)

**Validaciones:**
- El acronimo 'PRIV' esta reservado y no puede usarse
- El departamento debe existir
- El acronimo debe ser unico dentro del municipio

**Ejemplo:**
```json
{"department_id": "uuid-del-depto", "acronym": "MESA"}
```

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `department_id` | string | sí | ID del departamento al que pertenece |
| `acronym` | string | sí | Acronimo del sector (ej: MESA, ADMIN). 2-10 caracteres, letras y numeros (se guarda en mayusculas) |

### `PATCH /admin/sectors/{sector_id}`

Actualizar sector

Actualiza un sector (actualizacion parcial - PATCH).

**Campos editables:**
- `acronym`: Nuevo acronimo (1-10 caracteres)
- `is_active`: Estado activo/inactivo

**Restricciones:**
- El sector PRIV no puede ser modificado
- El nuevo acronimo no puede ser 'PRIV'
- El acronimo debe ser unico

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `sector_id` | path | string | sí | UUID del sector |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `acronym` | string |  | Nuevo acronimo. 2-10 caracteres, letras y numeros (se guarda en mayusculas) |
| `is_active` | boolean |  | Estado activo/inactivo |
| `primary_color` | string |  | Color primario hex |

### `DELETE /admin/sectors/{sector_id}` ⚠️ requiere confirmación

Desactivar sector (soft-delete)

Desactiva un sector (soft-delete). No elimina fisicamente, sino que marca
`is_active = false` y `end_date = NOW()`.

**Validaciones:**
- El sector PRIV no puede ser desactivado
- El sector no debe estar ya inactivo
- El sector no debe tener usuarios activos asignados (reasignarlos primero)

**Nota:** Los datos historicos (expedientes, movimientos, notas) se mantienen intactos.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `sector_id` | path | string | sí | UUID del sector |

### `GET /admin/sectors/{sector_id}/deactivation-status`

Estado de desactivacion de un sector

Evalua (solo lectura) si un sector se puede desactivar y, si no, por que.
Corre las mismas validaciones que el DELETE pero sin ejecutar nada.

**Devuelve:**
- `can_deactivate`: si el sector se puede desactivar
- `blockers`: lista de motivos que lo impiden (codigo + cantidad + mensaje)
- `counts`: conteos de usuarios, expedientes, movimientos y permisos

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `sector_id` | path | string | sí | UUID del sector |

### `POST /admin/sectors/{sector_id}/assign-user`

Asignar usuario a sector

Asigna un usuario existente a un sector.

**Request body:**
- `user_id`: UUID del usuario a asignar (requerido)

**Validaciones:**
- El sector debe existir y estar activo
- El usuario debe existir y estar activo (estado = 1)
- El usuario no debe estar ya asignado a ese sector

**Ejemplo:**
```json
{"user_id": "uuid-del-usuario"}
```

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `sector_id` | path | string | sí | UUID del sector |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `user_id` | string | sí | ID del usuario a asignar |

## Rangos jerárquicos

### `GET /admin/ranks`

Listar ranks jerarquicos

Lista todos los ranks (rangos jerarquicos) configurados en el municipio.

**Respuesta incluye:**
- ID del rank
- Nombre del rank (ej: Intendente, Secretario, Director)
- Nivel jerarquico (1 = mas alto, ej: Intendente = 1, Secretario = 2)
- Nombre del sello vinculado para titulares (head_signature)
- ID del city_seal vinculado (si tiene)

**Jerarquia y uso:**
- Los ranks definen niveles jerarquicos en la organizacion
- Cada departamento tiene un rank asociado
- El titular de un departamento hereda el rank y sello del departamento
- Los ranks pueden restringir quien puede firmar ciertos tipos de documento

**Sello automatico:**
- Cuando un rank tiene `city_seal_id` asignado
- Al designar titular de departamento con ese rank
- El usuario recibe automaticamente ese sello

### `POST /admin/ranks`

Crear rank jerarquico

Crea un nuevo rank (rango jerarquico) y vincula un sello obligatorio para titulares.

**Request body:**
- `name`: Nombre del rango (requerido, 2-50 caracteres, ej: "Director General")
- `level`: Nivel jerarquico (requerido, >= 1). Nivel 1 = mas alto (ej: Intendente)
- `city_seal_id`: ID del sello a vincular (obligatorio). Titulares con este rank reciben el sello automaticamente

**Validaciones:**
- El nombre debe ser unico dentro del municipio (case-insensitive)
- El sello debe existir y no estar vinculado a otro rank
- El nivel debe ser >= 1

**Uso posterior:**
- Asignar a departamentos al crearlos o editarlos
- Configurar como rank permitido para firmar tipos de documento especificos
- Cuando se asigne titular a departamento con este rank, recibira el sello vinculado

**Ejemplo:**
```json
{
  "name": "Subsecretario",
  "level": 3,
  "city_seal_id": 2
}
```

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string | sí | Nombre del rango |
| `level` | integer | sí | Nivel jerarquico (1=mas alto) |
| `city_seal_id` | integer | sí | ID del sello a vincular (obligatorio) |

### `DELETE /admin/ranks/{rank_id}` ⚠️ requiere confirmación

Eliminar rank jerarquico

Elimina un rank (rango jerarquico) del municipio de forma permanente.

**Parametros:**
- `rank_id`: UUID del rank a eliminar

**Validaciones:**
- El rank NO debe tener departamentos asociados
- Si tiene departamentos, reasignarlos o eliminarlos primero

**Advertencia:**
- La eliminacion es permanente
- El sello vinculado al rank se desvincula automaticamente (no se elimina)

**Flujo seguro:**
1. Verificar via GET `/admin/ranks` que el rank no tenga departamentos dependientes
2. Reasignar departamentos si es necesario
3. Eliminar rank

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `rank_id` | path | string | sí | UUID del rango |

### `PATCH /admin/ranks/{rank_id}`

Actualizar rank jerarquico

Actualiza un rank (rango jerarquico) del municipio (actualizacion parcial - PATCH).

**Parametros:**
- `rank_id`: UUID del rank a actualizar

**Campos editables:**
- `name`: Nombre del rango (2-50 caracteres)
- `level`: Nivel jerarquico (>= 1)
- `city_seal_id`: ID del sello a vincular (no se permite null, un rango siempre debe tener sello)

**Validaciones:**
- El nuevo nombre debe ser unico dentro del municipio (case-insensitive)
- El sello (si se envia) debe existir y no estar vinculado a otro rank
- No se permite enviar `city_seal_id: null` (sello obligatorio)
- Debe enviarse al menos un campo para actualizar

**Impacto:**
- Cambiar nombre: Se actualiza en toda la UI
- Cambiar level: Puede afectar jerarquia de permisos
- Cambiar sello: Futuros titulares recibiran el nuevo sello

**Ejemplo - Cambiar sello:**
```json
{
  "city_seal_id": 5
}
```

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `rank_id` | path | string | sí | UUID del rango |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  | Nombre del rango |
| `level` | integer |  | Nivel jerarquico (1=mas alto) |
| `city_seal_id` | integer |  | ID del sello a vincular |

## Sellos del municipio

### `GET /admin/city-seals`

Listar sellos del municipio

Lista todos los sellos configurados en el municipio.

**Respuesta incluye:**
- ID del sello
- Nombre del sello
- Descripcion opcional
- ID del rank vinculado (si tiene)
- Fecha de creacion

**Uso de sellos:**
- **Vinculacion a ranks:** Cuando un rank tiene sello vinculado, el titular del departamento
  con ese rank recibe automaticamente ese sello
- **Asignacion manual:** Los sellos tambien pueden asignarse manualmente a usuarios especificos
  via `/admin/users/{user_id}/seal`

**Nota:** Un sello vinculado a un rank no puede eliminarse hasta desvincular el rank.

### `POST /admin/city-seals`

Crear sello del municipio

Crea un nuevo sello municipal que puede vincularse a rangos o asignarse a usuarios.

**Request body:**
- `name`: Nombre del sello (requerido, 2-100 caracteres)
- `description`: Descripcion opcional del sello (max 500 caracteres)

**Validaciones:**
- El nombre debe ser unico dentro del municipio (case-insensitive)

**Usos posteriores:**
1. **Vincular a rank:** PATCH `/admin/ranks/{rank_id}` con `city_seal_id`
   - Cuando se asigna titular a departamento, recibe este sello automaticamente
2. **Asignar a usuario:** PUT `/admin/users/{user_id}/seal` con `city_seal_id`
   - Asignacion manual directa a un usuario especifico

**Ejemplo de uso:**
- Crear sello "Intendente Municipal" → vincular al rank "Intendente"
- Cuando se asigne titular a Intendencia, recibira el sello automaticamente

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string | sí | Nombre del sello |
| `description` | string |  | Descripcion opcional |

### `DELETE /admin/city-seals/{seal_id}` ⚠️ requiere confirmación

Eliminar sello del municipio

Elimina un sello del municipio de forma permanente.

**Parametros:**
- `seal_id`: ID del sello a eliminar

**Validaciones:**
- El sello NO debe estar vinculado a un rank
- Si esta vinculado, desvincular primero via PATCH `/admin/ranks/{rank_id}` con `city_seal_id: null`

**Advertencia:**
- La eliminacion es permanente
- Si usuarios tienen este sello asignado, se desvincularan automaticamente
- Verificar que no este en uso antes de eliminar

**Flujo seguro:**
1. Verificar via GET `/admin/city-seals` si el sello tiene `rank_id` asignado
2. Si tiene rank, desvincular primero via PATCH rank
3. Eliminar sello

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `seal_id` | path | integer | sí |  |

### `PATCH /admin/city-seals/{seal_id}`

Actualizar sello del municipio

Actualiza un sello del municipio (actualizacion parcial - PATCH).

**Parametros:**
- `seal_id`: ID del sello a actualizar

**Campos editables:**
- `name`: Nombre del sello (2-100 caracteres)
- `description`: Descripcion del sello (max 500 caracteres)

**Validaciones:**
- El nuevo nombre debe ser unico dentro del municipio (case-insensitive)
- Debe enviarse al menos un campo para actualizar

**Nota:**
- La vinculacion a ranks se gestiona via `/admin/ranks/{rank_id}`, no aqui
- Si el sello esta asignado a usuarios, mantendran la asignacion con el nuevo nombre

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `seal_id` | path | integer | sí |  |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  | Nombre del sello |
| `description` | string |  | Descripcion |

## Tipos de documento

### `GET /admin/document-types`

Listar tipos de documento

Lista todos los tipos de documento configurados localmente en el municipio.

**Respuesta incluye:**
- ID local y ID del tipo global de origen
- Nombre y acronimo del tipo
- Tipo de documento (`HTML`, `Importado`, `NOTA`)
- Tipo de firma requerida (`electronic`, `digital_all`, `digital_num`)
- Estado activo/inactivo
- Confiabilidad (gobierno/externo)
- Fecha de creacion local

**Uso:**
- Ver catalogo local de tipos disponibles para crear documentos
- Identificar tipos activos e inactivos
- Obtener IDs para operaciones de actualizacion

### `POST /admin/document-types`

Crear tipo de documento propio del tenant

Crea un Tipo de Documento PROPIO del municipio, sin origen en el Catalogo Global.

**Validaciones:**
- `acronym`: 2-6 letras A-Z (mayusculas). Se normaliza automaticamente (strip + upper).
- El acronimo NO puede coincidir con ninguno del Catalogo Global (activos ni inactivos).
- El acronimo NO puede repetirse en el municipio.
- `type`: HTML | Importado | NOTA | MEMO.
- `signature_policy`: electronic | digital_all | digital_num.
- Si se provee `field_definitions`: el tipo nace **inactivo** (`is_active=false`)
  hasta que se validen los campos.

**El acronimo es inmutable post-creacion** (decision de diseno: la numeracion depende de el).

**`visibility` ** clasificacion elegida al crear. `interno` (default) | `reservado`
| `publico`. Inmutable despues de la creacion. El BackOffice-Front lo pide como seleccion
obligatoria y explicita en el modal de alta, no como checkbox opcional.

**Errores posibles:**
- 400: Formato de acronimo invalido, o dato de Pydantic invalido.
- 409: Acronimo ya existe en el Catalogo Global o en el municipio.
- 403: Sin permisos de Administrador.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string | sí | Nombre del tipo de documento |
| `acronym` | string | sí | Acronimo unico (2-6 letras A-Z, mayusculas). Inmutable post-creacion. |
| `description` | string |  | Descripcion opcional |
| `type` | `HTML` \| `Importado` \| `NOTA` \| `MEMO` | sí | Tipo base del documento. SIN FFCC: 'Formulario Controlado' es una capacidad que se activa via field_definitions, no un valor de este campo. |
| `signature_policy` | `electronic` \| `digital_all` \| `digital_num` | sí | Politica de firma del tenant: electronic=FirmadorGDI (.p12), digital_all=firma digital todos, digital_num=firma digital solo numerador |
| `trust` | boolean |  | True = documento de gobierno (confiable). False = externo (requiere validacion). Default: `true`. |
| `special_numbering` | boolean |  | Si usa numeracion especial independiente (no la numeracion general). Default: `false`. |
| `external_signable` | boolean |  | (TAD Ciudadano): si true, habilita a un ciudadano a crear y firmar documentos de este tipo desde /api/v1/tad/*. Solo valido si signature_policy='electronic' (422 si no). Default: `false`. |
| `visibility` | `interno` \| `reservado` \| `publico` |  | Clasificacion de visibilidad , obligatoria y mutuamente excluyente: 'interno' (default) \| 'reservado' \| 'publico'. Se elige UNA vez al crear el tipo (selector obligatorio en el BackOffice) e inmutable despues (no se puede cambiar por PATCH una vez creado en 'reservado' o 'publico'). Default: `"interno"`. |
| `field_definitions` | lista de FieldDefinition |  | Definicion de campos de formulario controlado (capacidad FFCC). Si se provee, el tipo nace inactivo (is_active=false) hasta validar los campos. |

### `GET /admin/document-types/options/sectors`

Listar sectores disponibles

Lista sectores activos disponibles para configurar como habilitados en tipos de documento.

**Respuesta incluye:**
- ID del sector
- Acronimo del sector
- Nombre del departamento al que pertenece
- Acronimo del departamento

**Uso:**
- Obtener opciones para campo `enabled_sector_ids` al actualizar tipos de documento
- Si un tipo tiene sectores habilitados, solo usuarios de esos sectores pueden usarlo
- Si la lista esta vacia, todos los sectores pueden usar el tipo

### `GET /admin/document-types/options/ranks`

Listar rangos disponibles

Lista rangos jerarquicos disponibles para configurar como permitidos para firmar tipos de documento.

**Respuesta incluye:**
- ID del rank
- Nombre del rank (ej: Intendente, Secretario, Director)
- Nivel jerarquico (1 = mas alto)

**Uso:**
- Obtener opciones para campo `allowed_rank_ids` al actualizar tipos de documento
- Si un tipo tiene ranks permitidos, solo usuarios con esos ranks pueden firmarlo
- Si la lista esta vacia, no hay restriccion de rank para firmar

### `GET /admin/document-types/global`

Listar tipos de documento globales

Lista los tipos de documento del catalogo global maestro disponibles para importar al municipio.

**Parametros de query:**
- `include_copied`: Si es `true`, incluye tipos ya copiados al municipio. Por defecto `false` (solo muestra no copiados).

**Respuesta incluye:**
- ID del tipo global
- Nombre, acronimo y descripcion
- Tipo de firma sugerido
- Tipo de documento (HTML, Importado, NOTA)
- `is_copied`: Indica si ya fue copiado al municipio
- `local_id`: ID local si ya fue copiado (null si no)

**Flujo de uso:**
1. Listar tipos globales disponibles (`include_copied=false`)
2. Identificar tipo deseado por su `id`
3. Crear copia local via POST `/from-global`

**Catalogo maestro:**
- Los tipos globales son gestionados por el equipo GDI
- Incluyen tipos comunes a todos los municipios (Informe, Dictamen, Resolucion, etc.)
- Se agregan nuevos tipos periodicamente

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `include_copied` | query | boolean |  |  |

### `POST /admin/document-types/from-global`

Crear tipo de documento desde catalogo global

Crea una copia local de un tipo de documento desde el catalogo global maestro.

**Request body:**
- `global_document_type_id`: ID del tipo en el catalogo global a copiar
- `type` (opcional): tipo base con el que se crea la copia local
  (`HTML` | `Importado` | `NOTA` | `MEMO`). Si se omite se hereda el del catalogo.
  El catalogo trae un `type` fijo por item (`DECRE` viene como `HTML`) y no todos los
  municipios lo usan igual: el que importa los decretos escaneados necesita `Importado`.

**Validaciones:**
- El tipo global debe existir y estar activo
- No debe existir una copia local previa (evita duplicados)
- `type`, si viene, debe ser uno de los 4 tipos base

**Operacion:**
- Copia nombre, acronimo, descripcion y tipo de firma del catalogo
- El tipo de documento es el elegido en `type`, o el del catalogo si no se eligio
- El nuevo tipo se crea activo por defecto (`is_active=true`)
- Mantiene referencia al tipo global (`global_document_type_id`)

**Posterior configuracion:**
- Usar PATCH `/admin/document-types/{id}` para:
  - Habilitar sectores especificos (`enabled_sector_ids`)
  - Configurar rangos permitidos para firmar (`allowed_rank_ids`)
  - Ajustar nombre o descripcion local
  - Corregir el `type` base, mientras el tipo siga sin documentos
  - Desactivar si es necesario

**Importante:**
- No se puede copiar dos veces el mismo tipo global
- El acronimo queda fijo (heredado del tipo global)

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `global_document_type_id` | string | sí | ID del tipo global a copiar |
| `type` | `HTML` \| `Importado` \| `NOTA` \| `MEMO` |  | Tipo base a usar en la copia local. Si se omite se hereda el `type` del catalogo global (comportamiento historico). El catalogo trae un `type` fijo por item (ej. DECRE es 'HTML') y no todos los municipios lo usan asi: el que importa los decretos escaneados necesita 'Importado'. Como el acronimo es inmutable y ademas colisiona con el global, adoptar con el type errado dejaba la sigla inutilizable. |

### `GET /admin/document-types/{document_type_id}`

Detalle de tipo de documento

Obtiene el detalle completo de un tipo de documento local, incluyendo configuracion
de sectores habilitados y rangos permitidos para firmar.

**Parametros:**
- `document_type_id`: ID local del tipo de documento

**Respuesta incluye:**
- **Datos basicos:** nombre, acronimo, tipo de documento, tipo de firma, estado
- **Info del tipo global:** datos del tipo global de origen desde catalogo maestro
- **Sectores habilitados:** lista de sectores que pueden usar este tipo (vacio = todos)
- **Rangos permitidos:** lista de rangos que pueden firmar documentos de este tipo (vacio = sin restriccion)

**Uso:**
- Ver configuracion completa antes de actualizar
- Validar sectores y rangos configurados

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

### `PATCH /admin/document-types/{document_type_id}`

Actualizar tipo de documento

Actualiza un tipo de documento local del municipio (actualizacion parcial - PATCH).

**Parametros:**
- `document_type_id`: ID local del tipo de documento a actualizar

**Campos editables:**
- `name`: Nombre del tipo de documento (2-100 caracteres)
- `description`: Descripcion del tipo (max 250 caracteres)
- `type`: Tipo de documento (`HTML`, `Importado`, `NOTA`)
- `signature_policy`: Tipo de firma (`electronic`, `digital_all`, `digital_num`)
- `is_active`: Estado activo/inactivo (boolean)
- `trust`: Confiabilidad - `true` = gobierno, `false` = externo
- `enabled_sector_ids`: Lista de IDs de sectores habilitados (vacia = todos los sectores pueden usar)
- `allowed_rank_ids`: Lista de IDs de ranks permitidos para firmar (vacia = sin restriccion de rank)
- `visibility`: Cambia la clasificacion interno/reservado/publico **Restricciones:**
- El acronimo NO se puede cambiar (definido desde tipo global)
- Debe enviarse al menos un campo para actualizar
- `type` solo se puede cambiar mientras el tipo este VIRGEN (sin documentos draft ni
  oficiales); con documentos existentes se rechaza con 400. Ademas no se puede pasar
  a `Importado` con formulario controlado (FFCC) vigente: hay que desactivarlo antes.
- `visibility` es inmutable salvo `interno -> reservado` o `interno -> publico`, y solo si
  el tipo NO tiene documentos creados (400 si tiene). Desde `reservado` o `publico` nunca
  se sale (400 con mensaje explicito).

**Validaciones:**
- `type` debe ser uno de: `HTML`, `Importado`, `NOTA`
- `signature_policy` debe ser uno de: `electronic`, `digital_all`, `digital_num`
- Los IDs de sectores y ranks deben existir
- Si enabled_sector_ids esta vacia, se permite uso desde cualquier sector
- Si allowed_rank_ids esta vacia, cualquier usuario puede firmar (segun permisos)

**Ejemplo de request:**
```json
{
  "type": "Importado",
  "signature_policy": "electronic",
  "description": "Informe grafico importado desde archivo"
}
```

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  | Nombre del tipo |
| `description` | string |  | Descripcion |
| `type` | `HTML` \| `Importado` \| `NOTA` \| `MEMO` |  | Tipo base del documento (HTML, NOTA, MEMO, Importado). La capacidad de formulario controlado se configura via field_definitions, no via este campo. |
| `required_signature` | `electronic` \| `digital_all` \| `digital_num` |  | Tipo de firma: electronic (Notary .p12), digital_all (AutoFirma todos), digital_num (AutoFirma solo numerador) |
| `is_active` | boolean |  | Si esta activo |
| `trust` | boolean |  | true = gobierno (confiable), false = externo (requiere validacion) |
| `special_numbering` | boolean |  | Si usa numeracion especial independiente |
| `accepts_embedded_files` | boolean |  | Si permite adjuntar archivos embebidos al PDF |
| `external_signable` | boolean |  | (TAD Ciudadano): habilita/deshabilita la firma ciudadana externa para este tipo. Solo se puede activar (true) si signature_policy (actual o enviado en el mismo PATCH) es 'electronic'; si no, 422. |
| `visibility` | `interno` \| `reservado` \| `publico` |  | Cambia la clasificacion de visibilidad . INMUTABLE en general: se rechaza con 400 si el tipo actual ya es 'reservado' o 'publico' (una vez fijado, no se sale). Unica transicion permitida via PATCH: interno -> reservado o interno -> publico, y solo si el tipo no tiene documentos creados (guard FOR UPDATE + EXISTS, molde . |
| `enabled_sector_ids` | lista de string |  | IDs de sectores habilitados (lista vacia = todos) |
| `allowed_rank_ids` | lista de string |  | IDs de ranks permitidos (lista vacia = sin restriccion) |
| `field_definitions` | lista de FieldDefinition |  | Agrega capacidad de formulario controlado al tipo. NO aplica a type='Importado'. |

### `GET /admin/document-types/{document_type_id}/fields`

Obtener campos de formulario FFCC

Retorna la definicion de campos del tipo de documento FFCC.

- El tipo de documento debe ser FFCC (de lo contrario retorna 404)

**Tipos de campo soportados (ADR-7, alineados con RLM):**
`text`, `textarea`, `number`, `date`, `select`, `boolean`, `file`

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

### `PUT /admin/document-types/{document_type_id}/fields`

Reemplazar campos de formulario FFCC

Reemplaza completamente la definicion de campos de un tipo FFCC (ADR-4: sin versionado, UNIQUE por document_type_id).

- El tipo de documento debe ser FFCC (de lo contrario retorna 404)

**Comportamiento:**
- Si el tipo no tiene campos aun: INSERT.
- Si ya tiene campos: reemplaza completamente (no merge).
- Los documentos ya firmados NO se ven afectados (tienen su propio snapshot, ADR-3).

**Validaciones de estructura:**
- `name` debe ser unico dentro del formulario.
- `options` es requerido cuando `type='select'`.
- Los 7 tipos de campo son los mismos que RLM (ADR-7).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `field_definitions` | lista de FieldDefinition | sí | Nueva definicion completa de campos |

### `DELETE /admin/document-types/{document_type_id}/fields` ⚠️ requiere confirmación

Desactivar formulario FFCC (eliminar campos)

Elimina la definicion de campos de un tipo FFCC, devolviendolo a tipo
normal (NOTA/MEMO/HTML sin formulario controlado).

**Comportamiento:**
- Guard de inmutabilidad: NO se puede desactivar si existen documentos
  del tipo (retorna 409).
- Idempotente: si el tipo no tenia campos, responde 200 con deleted=false.
- Los documentos ya firmados NO se ven afectados (snapshot propio, ADR-3).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

### `GET /admin/document-types/{document_type_id}/api-schema`

Descargar esquema de integracion API TAD Ciudadano

Arma el JSON con todo lo que el software del municipio necesita para
crear y firmar documentos de este tipo via API TAD Ciudadano endpoint, headers requeridos y un ejemplo de body (varia segun el tipo:
`Importado` manda `pdf_base64`, FFCC manda `form_data`, HTML "libre"
manda `content_html`; se agrega `embedded_files` si el tipo acepta
adjuntos embebidos).

- El tipo de documento debe tener `external_signable=true` (de lo
  contrario 422: hay que habilitarlo primero)

**La URL del gateway del ambiente NO la conoce el BackOffice**: el body
trae un placeholder `{GATEWAY_URL}` que el municipio reemplaza por la
URL publica de su gateway.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `document_type_id` | path | integer | sí |  |

## Tipos de expediente (case templates)

### `GET /admin/case-templates`

Listar templates de expediente

Lista todos los templates de expediente configurados en el municipio.

**Respuesta incluye:**
- ID local y global
- Nombre y acronimo
- Canal de creacion (web, api, both)
- Departamento de radicacion
- Estado (activo/inactivo)

### `POST /admin/case-templates`

Crear tipo de expediente propio del tenant

Crea un Tipo de Expediente PROPIO del municipio, sin origen en el Catalogo Global.

**Validaciones:**
- `acronym`: 2-6 letras A-Z (mayusculas). Se normaliza automaticamente (strip + upper).
- El acronimo NO puede coincidir con ninguno del Catalogo Global (activos ni inactivos).
- El acronimo NO puede repetirse en el municipio.
- `creation_channel`: web | api | both.
- `filing_department_id`: debe existir y estar activo en el municipio.

**El acronimo es inmutable post-creacion** (decision de diseno: la numeracion depende de el).

**`visibility` ** clasificacion elegida al crear. `interno` (default) | `reservado`.
NUNCA `publico` (400: los expedientes no pueden ser publicos, D8). Inmutable post-creacion.
El BackOffice-Front lo pide como seleccion obligatoria y explicita en el modal de alta.

**Errores posibles:**
- 400: Formato de acronimo invalido, o dato de Pydantic invalido.
- 403: Sin permisos de Administrador.
- 404: Departamento de radicacion no encontrado o inactivo.
- 409: Acronimo ya existe en el Catalogo Global o en el municipio.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `type_name` | string | sí | Nombre del tipo de expediente |
| `acronym` | string | sí | Acronimo unico (2-6 letras A-Z, mayusculas). Inmutable post-creacion. |
| `description` | string |  | Descripcion opcional |
| `creation_channel` | `web` \| `api` \| `both` |  | Canal de creacion: web (formulario), api (integracion), both (ambos) Default: `"web"`. |
| `filing_department_id` | string | sí | UUID del departamento de radicacion. Debe existir, estar activo, y NO ser de sistema TAD). |
| `filing_sector_id` | string | sí | (TAD): UUID del sector de radicacion. La radicacion es DPTO#SECTOR: debe existir, estar activo y pertenecer a filing_department_id. |
| `visibility` | `interno` \| `reservado` \| `publico` |  | Clasificacion de visibilidad 'interno' (default) \| 'reservado' \| 'publico'. 'publico' se declara aca (Literal completo) para que el service lo rechace con un 400 explicito ('expedientes no pueden ser publicos', D8) en vez de un 422 generico de Pydantic. Se elige UNA vez al crear el tipo (selector obligatorio en el BackOffice) e inmutable despues. Default: `"interno"`. |

### `GET /admin/case-templates/global`

Listar templates de expediente globales

Lista los templates de expediente globales disponibles para agregar al municipio.

**Respuesta incluye:**
- Templates globales activos
- Indicador de si ya fueron copiados al municipio

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `include_copied` | query | boolean |  |  |

### `POST /admin/case-templates/from-global`

Crear template de expediente desde global

Crea una copia local de un template de expediente global.

**Requisitos:**
- El template global debe existir y estar activo
- No debe existir una copia local previa
- Se debe especificar el departamento de radicacion

**Se copia:**
- Nombre, acronimo, descripcion
- El nuevo template se crea activo por defecto

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `global_case_template_id` | string | sí | UUID del template global a copiar |
| `filing_department_id` | string | sí | UUID del departamento de radicacion |
| `filing_sector_id` | string | sí | (TAD): UUID del sector de radicacion. Debe pertenecer a filing_department_id. |
| `creation_channel` | string |  | Canal: web, api, both Default: `"web"`. |

### `GET /admin/case-templates/options/departments`

Listar departamentos disponibles

Lista departamentos activos para seleccionar como permitidos en un template.

### `GET /admin/case-templates/options/sectors`

Listar sectores disponibles (picker de radicacion,

Lista sectores activos con su departamento, para el picker DEPENDIENTE de
"Depto. radicacion" la radicacion de un Tipo de Expediente es
DPTO#SECTOR).

**Contrato para el Front:**
- `GET /admin/case-templates/options/sectors` (sin query param): TODOS los
  sectores activos del municipio (excluye sectores de departamentos de
  sistema, ej. TAD) — igual forma que `/admin/document-types/options/sectors`.
- `GET /admin/case-templates/options/sectors?department_id={id}`: SOLO los
  sectores de ese departamento. Uso tipico: el Front primero elige el
  departamento (picker `/options/departments`) y con ese `id` pide acá el
  picker de sector dependiente.
- Respuesta: `{"sectors": [{"id", "acronym", "primary_color", "department_name",
  "department_acronym"}, ...]}` (mismo shape que el picker de document-types).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `department_id` | query | string |  | Si viene, filtra solo los sectores de ese departamento (picker dependiente) |

### `GET /admin/case-templates/{case_template_id}`

Detalle de template de expediente

Obtiene detalle completo de un template de expediente.

**Respuesta incluye:**
- Datos basicos del template
- Info del template global de origen
- Departamentos permitidos para crear expedientes de este tipo

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `case_template_id` | path | string | sí | UUID del template de expediente |

### `PATCH /admin/case-templates/{case_template_id}`

Actualizar template de expediente

Actualiza un template de expediente local del municipio.

**Campos editables:**
- type_name: Nombre del tipo de expediente
- description: Descripcion
- creation_channel: Canal de creacion (web, api, both)
- filing_department_id: UUID del departamento de radicacion (puede ser null)
- is_active: Estado activo/inactivo
- visibility: Cambia la clasificacion interno/reservado . 'publico' SIEMPRE 400.
- allowed_department_ids: Lista de UUIDs de departamentos permitidos

**NOTA:** El acronimo NO se puede cambiar.

**visibility ** inmutable salvo `interno -> reservado`, y solo activable en tipos
virgenes.
- `interno -> reservado`: solo si el tipo NO tiene expedientes creados. Si tiene, 400.
- Desde `reservado`: siempre rechazado con 400 (inmutable).
- `publico`: siempre rechazado con 400 (expedientes no pueden ser publicos, D8).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `case_template_id` | path | string | sí | UUID del template de expediente |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `type_name` | string |  | Nombre del tipo |
| `description` | string |  | Descripcion |
| `creation_channel` | string |  | Canal: web, api, both |
| `filing_department_id` | string |  | UUID del departamento de radicacion |
| `filing_sector_id` | string |  | (TAD): UUID del sector de radicacion. Si se cambia filing_department_id sin enviar filing_sector_id (o viceversa), se valida el par EFECTIVO resultante (el sector debe pertenecer al departamento vigente tras el PATCH). |
| `is_active` | boolean |  | Si esta activo |
| `visibility` | `interno` \| `reservado` \| `publico` |  | Cambia la clasificacion de visibilidad . 'publico' SIEMPRE rechazado con 400 (expedientes no pueden ser publicos, D8). INMUTABLE en general: se rechaza con 400 si el tipo actual ya es 'reservado'. Unica transicion permitida: interno -> reservado, y solo si el tipo no tiene expedientes creados (guard FOR UPDATE + EXISTS, molde . |
| `allowed_department_ids` | lista de string |  | UUIDs de departamentos permitidos |

## Familias de legajos

### `GET /admin/global-registry-families`

Listar plantillas globales de familias de legajos

Lista todas las plantillas globales de familias de legajos disponibles.

**Respuesta incluye:**
- Datos de cada plantilla (code, name, description, default_data_schema, default_states)
- Indicador de si ya fue copiada al tenant (is_copied)
- UUID local si ya fue copiada (local_id)

### `GET /admin/registry-families`

Listar familias de legajos del tenant

Lista todas las familias de legajos configuradas en el municipio.

**Respuesta incluye:**
- ID, code, name, is_active
- Cantidad de campos en data_schema (field_count)
- Cantidad de estados (state_count)

### `POST /admin/registry-families`

Crear familia de legajos

Crea una familia de legajos. Dos modalidades:

**Desde plantilla global:**
```json
{ "from_global_id": "uuid-de-plantilla-global" }
```

**Custom:**
```json
{
  "code": "VEHICULOS",
  "name": "Legajo de Vehiculos",
  "data_schema": { ... },
  "states": ["activo", "baja"]
}
```

**Validaciones:**
- El codigo debe ser unico por tenant
- Si es desde global, la plantilla debe existir y no haber sido copiada

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `from_global_id` | string |  | UUID de la plantilla global (si se crea desde global) |
| `code` | string |  | Codigo unico (solo para custom, max 10 chars) |
| `name` | string |  | Nombre (solo para custom) |
| `description` | string |  | Descripcion (solo para custom) |
| `data_schema` | object |  | Schema de campos (solo para custom) |
| `states` | lista de string |  | Estados posibles (solo para custom) |

### `GET /admin/registry-families/{family_id}`

Obtener detalle de familia de legajos

Obtiene el detalle completo de una familia de legajos por su ID.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

### `PATCH /admin/registry-families/{family_id}`

Actualizar familia de legajos

Actualiza una familia de legajos.

**Campos editables:**
- name: Nombre descriptivo
- states: Lista de estados posibles
- is_active: Activar/desactivar
- is_public: Publica o despublica la familia . Reversible, sin restricciones (D4).
- public_config: fields / visible_states / show_documents / show_cases / show_related_records.
  `fields` debe ser subconjunto de data_schema, `visible_states` subconjunto de states (400 si no).

**NOTA:** El code NO se puede cambiar (inmutable).

**Validacion:** No se puede desactivar si hay legajos activos.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  | Nombre descriptivo |
| `description` | string |  | Descripcion de la familia |
| `states` | lista de string |  | Estados posibles |
| `is_active` | boolean |  | Activar/desactivar |
| `is_public` | boolean |  | Publica o despublica la familia . Reversible sin restricciones (D4): a diferencia de document_types, no hay guard de 'virgen' ni irreversibilidad. |
| `public_config` | PublicConfig |  | Configuracion de exposicion publica . 'fields' debe ser subconjunto de data_schema; 'visible_states' debe ser subconjunto de states (400 si no cumple). |

### `DELETE /admin/registry-families/{family_id}` ⚠️ requiere confirmación

Desactivar familia de legajos (soft delete)

Desactiva una familia de legajos (soft delete, is_active = false).

**Validacion:** No se puede desactivar si hay legajos activos en esta familia.
Si hay legajos activos, responde con error incluyendo la cantidad.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

### `PATCH /admin/registry-families/{family_id}/schema`

Agregar/editar campo en data_schema

Agrega o actualiza un campo en el data_schema de la familia.

**Si el campo (field_key) ya existe:** lo actualiza.
**Si no existe:** lo agrega.

**Tipos soportados:** text, number, date, select, boolean, file, textarea.
Para campos tipo `select`, incluir lista de `options`.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `field_key` | string | sí | Clave del campo (minusculas, numeros, underscore) |
| `type` | `text` \| `number` \| `date` \| `select` \| `boolean` \| `file` \| `textarea` | sí | Tipo de dato |
| `label` | string | sí | Etiqueta visible |
| `required` | boolean |  | Si es obligatorio Default: `false`. |
| `has_expiration` | boolean |  | Si tiene fecha de vencimiento Default: `false`. |
| `has_verification` | boolean |  | Si requiere verificacion Default: `false`. |
| `options` | lista de string |  | Opciones para campos tipo select |

### `DELETE /admin/registry-families/{family_id}/schema/{field_key}` ⚠️ requiere confirmación

Eliminar campo del data_schema

Elimina un campo del data_schema de la familia.

**Validacion:** No se puede eliminar si hay legajos con datos en ese campo.
Si hay datos, responde con error incluyendo la cantidad de legajos afectados.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |
| `field_key` | path | string | sí |  |

### `GET /admin/registry-families/{family_id}/permissions`

Listar permisos por sector

Lista todos los sectores con sus permisos para la familia de legajos.

**Respuesta incluye:**
- Sector ID y nombre
- Flags: can_create, can_edit, can_view, can_verify

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

### `POST /admin/registry-families/{family_id}/permissions`

Agregar sector con permisos

Agrega un sector con permisos a la familia de legajos.

**Permisos disponibles:**
- can_create: Puede crear legajos
- can_edit: Puede editar legajos
- can_view: Puede ver legajos
- can_verify: Puede verificar legajos

**Validacion:** UNIQUE(family_id, sector_id). No se puede duplicar.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `sector_id` | string | sí | UUID del sector |
| `can_create` | boolean |  | Puede crear legajos Default: `false`. |
| `can_edit` | boolean |  | Puede editar legajos Default: `false`. |
| `can_view` | boolean |  | Puede ver legajos Default: `true`. |
| `can_verify` | boolean |  | Puede verificar legajos Default: `false`. |

### `PATCH /admin/registry-families/{family_id}/permissions/{sector_id}`

Editar permisos de sector

Actualiza los permisos de un sector para la familia de legajos.

**Campos editables:**
- can_create, can_edit, can_view, can_verify (todos opcionales)

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |
| `sector_id` | path | string | sí | UUID del sector |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `can_create` | boolean |  | Puede crear legajos |
| `can_edit` | boolean |  | Puede editar legajos |
| `can_view` | boolean |  | Puede ver legajos |
| `can_verify` | boolean |  | Puede verificar legajos |

### `DELETE /admin/registry-families/{family_id}/permissions/{sector_id}` ⚠️ requiere confirmación

Quitar sector de permisos

Elimina el permiso del sector para la familia de legajos.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `family_id` | path | string | sí | UUID de la familia de legajos |
| `sector_id` | path | string | sí | UUID del sector |

## Configuración del municipio

### `GET /admin/settings`

Obtener configuracion del municipio

Retorna la configuracion completa del municipio desde la tabla `{schema}.settings`.

**Respuesta incluye:**
- `city`: Ciudad para usar en documentos oficiales
- `address`: Domicilio fiscal del municipio
- `annual_slogan`: Lema o frase institucional del año
- `logo_url`: URL del logo institucional completo
- `isologo_url`: URL del isologo (version simplificada del logo)
- `cover_url`: URL de la imagen de portada para onboarding
- `timezone`: Zona horaria del municipio (ej: America/Argentina/Buenos_Aires)
- `updated_at`: Fecha de ultima actualizacion de configuracion

**Nota:** Las URLs de imagenes se gestionan por separado via endpoints de upload.

### `PUT /admin/settings`

Actualizar configuracion del municipio

Actualiza la configuracion textual del municipio. Los campos de imagenes se gestionan
por separado via endpoints de upload de archivos.

**Campos editables:**
- `city`: Ciudad para documentos oficiales (max 100 caracteres)
- `address`: Domicilio fiscal del municipio (max 150 caracteres)
- `annual_slogan`: Lema o frase institucional (max 255 caracteres)

**Validaciones:**
- Debe enviarse al menos un campo para actualizar
- Los campos enviados reemplazan los valores actuales

**Nota:** Las URLs de imagenes (logo_url, isologo_url, cover_url) NO se actualizan
mediante este endpoint. Usar endpoints especificos de upload de archivos.

**Auditoria:** La actualizacion registra el `user_id` del administrador que realizo el cambio.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `city` | string |  |  |
| `address` | string |  |  |
| `annual_slogan` | string |  |  |
| `primary_color` | string |  |  |

### `POST /admin/settings/upload-image`

Subir logo o isologo

Sube imagen a R2 y guarda URL en settings.

Body `multipart/form-data` (subida de archivo):

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `file` | string | sí |  |
| `field` | string | sí |  |

## Ciudadanos (Base TAD)

### `GET /admin/citizens`

Listar/buscar ciudadanos (Base TAD)

Lista la Base de Ciudadanos del municipio , TAD Ciudadano), con busqueda
opcional por nombre o CUIL/DNI.

**Requiere:** Rol de Administrador.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `search` | query | string |  | Filtra por nombre o CUIL/DNI (case-insensitive) |
| `page` | query | integer |  | Numero de pagina (1-based) |
| `page_size` | query | integer |  | Tamano de pagina (1-500) |

### `POST /admin/citizens`

Alta manual de ciudadano (mostrador)

Da de alta un ciudadano manualmente (ej. validacion presencial en el mostrador).
`country_id` (CUIL/DNI) debe ser unico dentro del municipio.

Si `estado='validado'`, el admin que crea queda registrado como validador.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `full_name` | string | sí | Nombre y apellido |
| `country_id` | string | sí | CUIL/DNI |
| `estado` | `pendiente` \| `validado` \| `bloqueado` |  | Estado inicial. Default 'pendiente'. Si se envia 'validado', el admin que crea queda registrado como validador (validated_by/validated_at). Default: `"pendiente"`. |

### `PATCH /admin/citizens/{citizen_id}/estado`

Cambiar estado de ciudadano

Cambia el estado de un ciudadano: `pendiente` | `validado` | `bloqueado`.
Nombre e ID (CUIL/DNI) NO se editan por este endpoint (inmutables por ahora).

Uso tipico: validar identidad presencial (`-> validado`) o bloquear un ciudadano
por un problema puntual (`-> bloqueado`).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `citizen_id` | path | string | sí | UUID del ciudadano |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `estado` | `pendiente` \| `validado` \| `bloqueado` | sí | Nuevo estado: pendiente \| validado \| bloqueado |

## API Keys

### `GET /admin/api-keys`

Listar API Keys del municipio

Lista todas las API Keys creadas por el municipio con conteo de usuarios autorizados.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `limit` | query | integer |  | Cantidad maxima de API Keys a devolver (1-500). Default: 100. |
| `offset` | query | integer |  | Desplazamiento para paginacion. Default: 0. |

### `POST /admin/api-keys`

Crear API Key

Crea una nueva API Key. La key completa se muestra SOLO en esta respuesta.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string | sí | Nombre descriptivo de la API Key |
| `description` | string |  | Descripcion opcional |
| `expires_at` | string |  | Fecha de expiracion ISO 8601 (null = no expira) |
| `rate_limit_per_minute` | integer |  | Limite de requests por minuto Default: `60`. |
| `key_type` | `api` \| `tad` |  | 'api' (default, Gateway REST comun) \| 'tad' habilita SOLO la superficie /api/v1/tad/* para el software del municipio). Inmutable post-creacion. Default: `"api"`. |
| `webhook_url` | string |  | URL de callback , evento documents.notified) |
| `webhook_secret` | string |  | Secreto para firmar el webhook (HMAC X-GDI-Signature). Se guarda CIFRADO y nunca se devuelve en claro por la API. |
| `allowed_origins` | lista de string |  | Origenes permitidos (CORS). Opcional (tambien para key_type='tad'). |

### `GET /admin/api-keys/{key_id}/users`

Listar usuarios autorizados de una API Key

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |
| `limit` | query | integer |  | Cantidad maxima de usuarios a devolver (1-500). Default: 100. |
| `offset` | query | integer |  | Desplazamiento para paginacion. Default: 0. |

### `POST /admin/api-keys/{key_id}/users`

Agregar usuario autorizado a una API Key

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `user_id` | string | sí | UUID del usuario a autorizar |

### `DELETE /admin/api-keys/{key_id}/users/{user_id}` ⚠️ requiere confirmación

Remover usuario autorizado de una API Key

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |
| `user_id` | path | string | sí | UUID del usuario autorizado |

### `GET /admin/api-keys/{key_id}`

Detalle de una API Key

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |

### `PATCH /admin/api-keys/{key_id}`

Actualizar API Key

Actualiza campos parciales de una API Key (nombre, descripcion, estado, expiracion, rate limit).

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `name` | string |  |  |
| `description` | string |  |  |
| `is_active` | boolean |  |  |
| `expires_at` | string |  |  |
| `rate_limit_per_minute` | integer |  |  |
| `webhook_url` | string |  | URL de callback |
| `webhook_secret` | string |  | Nuevo secreto del webhook (se re-cifra). Enviar null no lo borra: usar '' para eso. |
| `allowed_origins` | lista de string |  | Origenes permitidos (CORS) |

### `DELETE /admin/api-keys/{key_id}` ⚠️ requiere confirmación

Eliminar API Key

Elimina una API Key y todos sus usuarios autorizados.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `key_id` | path | string | sí | UUID de la API Key |

## Certificados de firma

### `GET /admin/certificates`

Listar certificados

Lista todos los certificados de tenants registrados.

### `POST /admin/certificates`

Subir certificado digital

Sube un archivo .p12 y su password para un tenant. El archivo se almacena en R2 y el password se encripta con Fernet.

Body `multipart/form-data` (subida de archivo):

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `cert_file` | string | sí | Archivo .p12 (max 5MB) |
| `cert_password` | string | sí | Password del archivo .p12 |
| `tenant_id` | string |  | Tenant ID (default: tenant del admin) |

### `POST /admin/certificates/generate-csr`

Generar KEY + CSR para solicitud ONTI

Genera una clave privada RSA 2048 y un CSR con los campos requeridos por AC ONTI.

**El municipio debe:**
1. Guardar la `key_pem` en un lugar seguro (nunca compartirla)
2. Enviar el `csr_pem` a ONTI via JIRA
3. Cuando reciba el `.cer` de ONTI, llamar a `/finalize`

**GDI no almacena la clave privada.**

### `POST /admin/certificates/finalize`

Finalizar certificado con .cer de ONTI

Combina el `.cer` emitido por ONTI con la clave privada del municipio,
genera el `.p12` y lo activa en GDI automaticamente.

**El municipio debe aportar:**
- El archivo `.cer` recibido de ONTI
- El archivo `.key` que guardo en el paso de generacion del CSR
- Una contrasena para proteger el certificado (min 8 caracteres)

**La clave privada NO se almacena. Solo se usa para armar el .p12.**

Body `multipart/form-data` (subida de archivo):

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `cer_file` | string | sí | Archivo .cer/.crt/.pem/.p7b emitido por ONTI |
| `key_file` | string | sí | Archivo .key generado en el paso anterior |
| `cert_password` | string | sí | Contrasena para proteger el certificado (min 8 chars) |
| `tenant_id` | string |  | Tenant ID (default: tenant del admin) |

### `GET /admin/certificates/{tenant_id}`

Info de certificado

Obtiene informacion de un certificado por tenant_id.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `tenant_id` | path | string | sí |  |

### `DELETE /admin/certificates/{tenant_id}` ⚠️ requiere confirmación

Eliminar certificado

Elimina un certificado de R2 y BD.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `tenant_id` | path | string | sí |  |

### `POST /admin/certificates/send-instructions`

Enviar instrucciones de certificado por email

Envía al admin logueado las instrucciones del proceso ONTI con la nota modelo.

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `cn` | string | sí |  |
| `org` | string | sí |  |
| `sha256` | string | sí |  |
| `nota_texto` | string | sí |  |
| `fd_code` | string |  | Default: `""`. |

## Estadísticas

### `GET /admin/stats/summary`

Metricas generales del tenant

Retorna metricas generales del tenant:
expedientes (total/activos/cerrados/last_14_days),
documentos firmados, usuarios, notas enviadas,
departamentos activos y sectores activos.

### `GET /admin/stats/documents-by-type`

Documentos por tipo en el periodo

Documentos oficiales agrupados por tipo de documento en el periodo indicado.
Default: ultimos 14 dias.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `date_from` | query | string |  | Fecha inicio YYYY-MM-DD |
| `date_to` | query | string |  | Fecha fin YYYY-MM-DD |

### `GET /admin/stats/cases-activity`

Expedientes creados por dia

Expedientes creados por dia en el periodo indicado.
Default: ultimos 14 dias.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `date_from` | query | string |  | Fecha inicio YYYY-MM-DD |
| `date_to` | query | string |  | Fecha fin YYYY-MM-DD |

### `GET /admin/stats/signatures`

Estadisticas de firmas digitales

Firmas de public.firma_audit_log filtrado por schema del tenant y periodo.
Default: ultimos 14 dias.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `date_from` | query | string |  | Fecha inicio YYYY-MM-DD |
| `date_to` | query | string |  | Fecha fin YYYY-MM-DD |

### `GET /admin/stats/last-access`

Ultimos accesos de usuarios

Retorna los N usuarios que accedieron mas recientemente al sistema.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `limit` | query | integer |  | Numero de usuarios a retornar |

### `GET /admin/stats/recent-signed-documents`

Ultimos documentos firmados

Retorna los N documentos firmados mas recientes. Default: ultimos 14 dias.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `limit` | query | integer |  | Numero de documentos a retornar |
| `date_from` | query | string |  | Fecha inicio YYYY-MM-DD |
| `date_to` | query | string |  | Fecha fin YYYY-MM-DD |

### `GET /admin/stats/cases-list`

Lista paginada de todos los expedientes

Lista paginada de TODOS los expedientes del tenant con filtros opcionales
de status, busqueda de texto y rango de fechas.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `page` | query | integer |  | Pagina actual |
| `page_size` | query | integer |  | Expedientes por pagina |
| `status` | query | string |  | Filtrar por status |
| `search` | query | string |  | Buscar en numero o asunto |
| `date_from` | query | string |  | Fecha inicio YYYY-MM-DD |
| `date_to` | query | string |  | Fecha fin YYYY-MM-DD |

## Auditoría

### `GET /admin/audit`

Historial de auditoria del organigrama

Devuelve el historial de cambios registrado automaticamente via triggers SQL
sobre las tablas del organigrama.

**Tablas disponibles:** `departments, ranks, sectors, user_roles, user_seals, user_sector_permissions, users`

**Por defecto** devuelve `departments` + `sectors` (el organigrama completo).

Cada entrada incluye:
- Quien hizo el cambio (nombre + email del usuario, o 'Sistema')
- Cuando (timestamp con timezone)
- Que tabla y que operacion (INSERT / UPDATE / DELETE)
- La entidad afectada (id + nombre/acronimo)
- Para UPDATE: los campos modificados con valor viejo y nuevo
- Para INSERT/DELETE: snapshot de los campos relevantes

**Paginacion:** `limit` (max 500) + `offset`.
Ordenado por `event_time DESC`.

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `tables` | query | lista de string |  | Tablas a incluir. Permitidas: departments, ranks, sectors, user_roles, user_seals, user_sector_permissions, users. Se puede enviar multiples veces (?tables=departments&tables=sectors). Si se omite, devuelve departments + sectors. |
| `from` | query | string (date) |  | Fecha de inicio del filtro (ISO date, ej: 2026-01-01). Inclusivo. |
| `to` | query | string (date) |  | Fecha de fin del filtro (ISO date, ej: 2026-05-31). Inclusivo (hasta 23:59:59). |
| `limit` | query | integer |  | Cantidad maxima de resultados (1-500). Default: 100. |
| `offset` | query | integer |  | Desplazamiento para paginacion. Default: 0. |

## Organigrama

### `GET /admin/organigrama/export`

Exportar organigrama a XLSX

Genera y descarga el organigrama completo del municipio en formato Excel (.xlsx).

**Incluye tres hojas:**
- **Reparticiones**: árbol plano de departamentos activos con titular, rango y estadísticas
- **Sectores**: listado de sectores con conteo de empleados
- **Usuarios**: padrón completo (activos e inactivos) con roles, permisos y sellos

**No tiene LIMIT**: exporta todos los registros del tenant.

## Propuestas al catálogo global

### `POST /admin/catalog/propose`

Proponer nuevo item al catalogo global

Un admin municipal propone un nuevo item para el catalogo global.

**Flujo:**
1. Valida acronimo/codigo contra conflictos existentes
2. Llama a AgenteLANG para analisis IA (fuera de transaccion)
3. Si IA aprueba automaticamente: UPSERT en tabla global + guarda propuesta como 'approved'
4. Si IA deriva a revision: guarda propuesta como 'pending' + envia email a el equipo de GDI

**Rate limit:** 60 req/min (global por IP, aplicado por middleware)

Body JSON:

| Campo | Tipo | Oblig. | Descripción |
|---|---|---|---|
| `catalog_table` | `global_document_types` \| `global_case_templates` \| `global_registry_families` | sí |  |
| `data` | DocumentTypeProposalData \| CaseTemplateProposalData \| RegistryFamilyProposalData | sí |  |

### `GET /admin/catalog/proposals`

Listar propuestas de catalogo

Lista las propuestas de catalogo, filtrable por status.

**Status posibles:** pending | approved | rejected

| Parámetro | Dónde | Tipo | Oblig. | Descripción |
|---|---|---|---|---|
| `status` | query | string |  |  |
| `catalog_table` | query | string |  |  |
