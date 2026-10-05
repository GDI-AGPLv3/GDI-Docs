---
name: gdi-backoffice-admin
description: Administra el BackOffice de GDI (Gestión Documental Inteligente) de un municipio por su API REST — usuarios, reparticiones, sectores, sellos, rangos, tipos de documento y de expediente, familias de legajos, configuración, API Keys, estadísticas y auditoría. Usala cuando el administrador pida dar de alta o de baja empleados, armar o cambiar el organigrama, habilitar tipos de documento, revisar quién hizo qué o consultar métricas del municipio en GDI.
---

# Administrar el BackOffice de GDI por API

Operás el BackOffice del municipio **en nombre de su administrador**, llamando a la API REST
del BackOffice. Todo lo que hacés queda registrado en la auditoría del municipio **a nombre
de ese administrador**. Actuá como lo haría un administrador prolijo: mirá antes de tocar,
mostrá lo que vas a hacer y confirmá antes de borrar.

La lista completa de endpoints (con parámetros y campos) es la **referencia de endpoints**
(ver el paso 0). Consultala cuando necesites un endpoint que no esté en las recetas de abajo.
**No inventes endpoints ni campos**: si no están ahí, no existen.

## 0. Antes de empezar: bajar la referencia de endpoints

GDI publica la referencia **vigente** en su documentación. Antes de la primera llamada a la API:

1. Descargala entera, tal cual, a un archivo:
   ```bash
   curl -sS -o gdi-bo-endpoints.txt https://docs.gdilatam.com/descargas/gdi-backoffice-admin-referencia.txt
   ```
   Usá una descarga directa (`curl`, `Invoke-WebRequest` o la ejecución de código). **No uses una
   herramienta que resuma páginas web**: necesitás los endpoints y campos exactos.
2. Leela completa. Es la fuente de verdad sobre qué endpoints existen y qué campos llevan.
3. Si no la podés descargar, usá la copia local `reference/endpoints.md` si la tenés (viene con
   la skill instalada). Si tampoco está, avisale al administrador y **no sigas** hasta tenerla.

## 1. Conexión

Se necesitan cuatro datos. Buscalos en este orden: variables de entorno, y si no están,
pedíselos al administrador.

| Variable | Qué es | De dónde sale |
|---|---|---|
| `GDI_BO_URL` | URL de la API del BackOffice del municipio (sin `/` al final) | La entrega GDI al habilitar la integración |
| `GDI_BO_SCHEMA` | Identificador del municipio (ej. `101_ejemplo`) | Lo entrega GDI junto con la URL |
| `GDI_BO_USER_ID` | UUID del usuario administrador que opera | Lo entrega GDI, o lo ve otro admin con acceso a la API |
| `GDI_BO_API_KEY` | API Key (`sk-gdi-…`) | El admin la crea en BackOffice → **API Keys** y se autoriza a sí mismo en esa key |

Reglas para la API Key:

- **Nunca la muestres, la repitas ni la escribas en un archivo** que no sea el que el admin
  indicó para guardarla. En los comandos usá siempre la variable (`$GDI_BO_API_KEY`), no el valor.
- Si el admin la pega en el chat, usala pero recomendale moverla a una variable de entorno.
- Si una llamada responde que la key está desactivada o expirada, pedile que genere otra.

Verificá la conexión con una lectura inocua antes de cualquier otra cosa:

```bash
curl -sS "$GDI_BO_URL/admin/settings" \
  -H "X-API-Key: $GDI_BO_API_KEY" \
  -H "X-Tenant-Schema: $GDI_BO_SCHEMA" \
  -H "X-User-ID: $GDI_BO_USER_ID"
```

Si devuelve los datos del municipio, estás conectado. Si no, mirá la tabla de errores (sección 6).

## 2. Cómo llamar

Los **tres headers van en todas las llamadas**: `X-API-Key`, `X-Tenant-Schema`, `X-User-ID`.
Los que llevan cuerpo, además `Content-Type: application/json`.

```bash
curl -sS -X POST "$GDI_BO_URL/admin/departments" \
  -H "X-API-Key: $GDI_BO_API_KEY" \
  -H "X-Tenant-Schema: $GDI_BO_SCHEMA" \
  -H "X-User-ID: $GDI_BO_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "Dirección de Tránsito", "acronym": "TRANS", "parent_id": "<uuid-padre>"}'
```

En Windows PowerShell usá `curl.exe` (no `curl`, que ahí es otro comando) o `Invoke-RestMethod`.

## 3. Reglas de trabajo

1. **Mirá antes de tocar.** Los IDs se buscan con un `GET` (por nombre o sigla). Nunca inventes
   un UUID ni supongas uno. Si hay dos candidatos parecidos, preguntá cuál.
2. **Mostrá el plan y esperá el OK** antes de cualquier cambio: qué endpoint, sobre qué
   registro (nombre, no solo UUID) y con qué valores.
3. **Confirmación explícita para lo marcado ⚠️** en la referencia: borrar, desactivar,
   archivar, quitar el rol de Administrador, cambiar el email o el método de acceso, borrar
   API Keys o certificados. Repetí qué se pierde y pedí un "sí" claro. Un "dale" dicho antes
   para otra cosa no cuenta.
4. **Un cambio, un resultado.** Después de cada escritura mostrá lo que devolvió la API. Si
   falló, pará y explicá el error; no sigas con los pasos siguientes como si nada.
5. **Cargas masivas** (ej. 80 usuarios desde una planilla): primero mostrá la tabla completa
   de lo que vas a crear, detectá duplicados contra `GET /admin/users/emails`, pedí el OK, y
   después andá de a una llamada por segundo como máximo. El límite es **60 pedidos por minuto**.
6. **Nunca le quites el rol de Administrador a quien está operando**, ni dejes al municipio
   sin ningún administrador activo.
7. **Links de activación**: `POST /admin/users/{id}/activation-link` devuelve un link que
   funciona como una contraseña (sirve una vez, vence a los 5 días). Dáselo solo al
   administrador, nunca lo guardes en archivos.

## 4. Cómo está organizado un municipio en GDI

- **Repartición** (`department`): unidad del organigrama (Secretaría, Dirección…). Forman un
  árbol: toda repartición tiene una repartición padre (`parent_id`), salvo la raíz. Puede
  tener un **titular** (`head_user`) y un **rango**.
- **Sector**: subdivisión de una repartición donde trabajan los usuarios (ej. `MESA`, `LEGAL`).
  Al crear una repartición se crea sola su sector `PRIV` (privada del titular), que no se
  puede borrar.
- **Usuario**: pertenece a **un sector principal** (`sector_id`) y puede tener permisos
  sobre otros sectores (`sector-permissions`). Para crearlo hace falta un **sello**.
- **Sello** (`city_seal`): cómo aparece la firma del usuario (ej. "Director"). Se asigna a
  cada usuario y puede estar asociado a un rango.
- **Rango** (`rank`): nivel jerárquico (Intendente, Secretario, Director…). Define qué
  tipos de documento puede firmar alguien.
- **Tipo de documento**: los habilitados en el municipio son copias locales del **catálogo
  global** de GDI. Se habilitan con `from-global` y después se configuran (sectores que lo
  usan, rangos que lo firman, tipo de firma).
- **Tipo de expediente** (`case_template`): igual que los tipos de documento, con reparticiones
  habilitadas y una repartición de radicación.
- **Estado del usuario**: activo → **desactivado** (no entra, sus documentos pendientes de
  firma se rechazan solos) → **archivado** (ex empleado: sale del listado). **Borrar** solo
  funciona si el usuario nunca tuvo actividad; si tuvo, la API responde 409 y hay que
  desactivar o archivar.

## 5. Recetas

Todas fueron probadas de punta a punta. Los `{…}` se reemplazan por IDs obtenidos con `GET`.

### Dar de alta un empleado

1. Ubicar el sector: `GET /admin/departments` devuelve el árbol de reparticiones (sin
   sectores); con el ID de la repartición, `GET /admin/departments/{id}` trae sus `sectors`
   con los usuarios de cada uno. Para ver todos los sectores del municipio de una vez:
   `GET /admin/document-types/options/sectors`.
2. Ver sellos disponibles: `GET /admin/city-seals` (respuesta en `city_seals`).
3. Chequear que el email no exista: `GET /admin/users/emails`.
4. Crear: `POST /admin/users`
   ```json
   {"email": "ana.perez@municipio.gob.ar", "full_name": "Ana Pérez",
    "sector_id": "{sector}", "city_seal_id": 4, "auth_method": "social"}
   ```
   `auth_method`: `social` si entra con su cuenta de Google o Microsoft; `database` si entra
   con email y contraseña (recibe un mail para crearla).
5. Si no le llega el mail: `POST /admin/users/{id}/reinvite`, o
   `POST /admin/users/{id}/activation-link` para darle el link por otro canal (solo `database`).

### Crear una repartición con su sector y su titular

1. Padre: `GET /admin/departments` → ID de la repartición de la que depende.
2. Rango (opcional): `GET /admin/ranks`.
3. `POST /admin/departments` → `{"name": "…", "acronym": "…", "parent_id": "{padre}", "rank_id": "{rango}"}`.
   La sigla: 2 a 20 letras y números, única en el municipio.
4. Sector de trabajo: `POST /admin/sectors` → `{"department_id": "{rep}", "acronym": "MESA"}`
   (2 a 10 letras y números).
5. Titular: `GET /admin/departments/{rep}/available-users` y después
   `PATCH /admin/departments/{rep}/head` → `{"head_user_id": "{usuario}"}` (`null` lo quita).

### Dar de baja a un empleado ⚠️

1. `GET /admin/users/{id}`: confirmá con el admin que es la persona correcta.
2. Explicá la diferencia y preguntá qué quiere:
   - **Desactivar** (`POST …/deactivate`): no entra más; sus documentos pendientes de firma
     se rechazan automáticamente. Se puede revertir con `…/reactivate`.
   - **Archivar** (`POST …/archive`): para ex empleados; además desaparece del listado.
     Se revierte con `…/unarchive`.
   - **Borrar** (`DELETE /admin/users/{id}`): definitivo, y solo si nunca tuvo actividad.
3. Si era titular de una repartición, quitalo antes (`PATCH …/head` con `null`) o proponé
   reemplazo.

### Habilitar un tipo de documento del catálogo global

1. `GET /admin/document-types/global` → los que tienen `is_copied: false` están disponibles.
2. `POST /admin/document-types/from-global` → `{"global_document_type_id": "{id}"}`.
   Opcional `"type"` (`HTML`, `Importado`, `NOTA`, `MEMO`) si el municipio lo usa distinto
   del catálogo (ej. decretos escaneados = `Importado`).
3. Configurar con `PATCH /admin/document-types/{id}`: `enabled_sector_ids` (vacío = todos),
   `allowed_rank_ids` (vacío = sin restricción), `required_signature`. Opciones en
   `GET /admin/document-types/options/sectors` y `…/options/ranks`.
4. No se borran: se desactivan con `{"is_active": false}`.

### Consultas frecuentes

- Resumen del municipio: `GET /admin/stats/summary`.
- Quién cambió qué en el organigrama: `GET /admin/audit`.
- Últimos accesos: `GET /admin/stats/last-access`.
- Organigrama completo en Excel: `GET /admin/organigrama/export` (guardá la respuesta en un
  archivo `.xlsx`, no la imprimas).

## 6. Errores

| Código | Qué significa | Qué hacer |
|---|---|---|
| 400 | Falta un header o un dato mal formado (ej. UUID inválido) | Revisá los tres headers y el cuerpo |
| 401 | API Key inválida o sin enviar | Revisá `GDI_BO_API_KEY` |
| 403 `API Key desactivada` / `expirada` | La key ya no sirve | El admin genera otra en BackOffice → API Keys |
| 403 `Usuario no autorizado para esta API Key` | El usuario no está autorizado en esa key | En BackOffice → API Keys → la key → agregar al usuario |
| 403 `API Key no autorizada para este tenant` | La key es de otro municipio | Revisá `GDI_BO_SCHEMA` |
| 403 `NOT_ADMIN` | El usuario no tiene rol Administrador | Tiene que operar un administrador |
| 403 `USER_INACTIVE` | El usuario que opera está desactivado | Usar otro administrador |
| 403 por licencia | La licencia del municipio no está operativa | Contactar a GDI |
| 404 | No existe (o el usuario de `X-User-ID` no está en el municipio) | Volvé a buscar el ID con un `GET` |
| 409 | Conflicto de negocio (ej. sigla repetida, usuario con actividad, sector con usuarios) | Leé `detail`: dice qué resolver primero |
| 422 | Falta un campo obligatorio o tiene un tipo inválido | `detail` indica el campo |
| 429 | Más de 60 pedidos por minuto | Esperá lo que indique `Retry-After` y seguí más despacio |

## 7. Qué no se puede hacer por acá

- **Crear el municipio, el onboarding y la licencia**: se hacen desde la pantalla, con login.
- **Aprobar propuestas al catálogo global**: es tarea de GDI, no del municipio.
- **Documentos y expedientes** (crear, firmar, asignar): no son del BackOffice; van por la API
  del Gateway, que es otra integración.
- **Subir certificados de firma y el logo**: existen en la API pero conviene hacerlo desde la
  pantalla (llevan archivos y contraseñas).
- **Borrar una repartición que alguna vez tuvo un sector de trabajo**: hoy la API lo rechaza
  aunque el sector esté desactivado. Si el admin lo necesita, que contacte a GDI.
