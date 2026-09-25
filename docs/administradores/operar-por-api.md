# Operar el BackOffice con IA (API)

Todo lo que hacés en el BackOffice (dar de alta usuarios, armar el organigrama, habilitar
tipos de documento, revisar la auditoría) también se puede hacer **pidiéndoselo a tu
asistente de IA** (Claude), que opera el BackOffice por su API en tu nombre.

Por ejemplo:

- *"Dá de alta a estas 12 personas de la planilla en el sector MESA de Obras Públicas."*
- *"Creá la Dirección de Tránsito dentro de la Secretaría de Gobierno, con un sector MESA, y poné de titular a Juan Gómez."*
- *"¿Quién cambió el organigrama la semana pasada?"*
- *"Habilitá el tipo de documento Acta para Legales y que solo lo firmen Directores."*

No hace falta instalar nada. Le pegás a Claude un **prompt de arranque** corto, que le pide
dos cosas antes de empezar: bajar de este sitio la **referencia completa** del BackOffice (las
reglas de cuidado y todos los endpoints) y trabajar según esa referencia. Como la referencia se
baja en cada conversación, Claude siempre trabaja con la versión vigente.

[:material-download: Descargar el prompt (.txt)](../descargas/gdi-backoffice-admin-prompt.txt){ .md-button .md-button--primary }
[:material-file-document-outline: Referencia completa (.txt)](../descargas/gdi-backoffice-admin-referencia.txt){ .md-button }
[:material-book-open-variant: Ver los endpoints](operar-por-api-referencia.md){ .md-button }

!!! warning "Todo lo que haga la IA queda a tu nombre"
    La IA opera con **tu usuario de administrador**. Cada cambio queda en la auditoría del
    municipio como hecho por vos. La skill le indica a Claude que te muestre el plan y te pida
    confirmación antes de borrar o desactivar nada, pero la decisión y la responsabilidad
    son tuyas: leé lo que te propone antes de aceptar.

---

## Qué necesitás

| Requisito | Detalle |
|---|---|
| **Rol Administrador** en el BackOffice | Solo un administrador puede operar la API |
| **Claude con acceso a internet** | Claude Code, Claude Desktop o claude.ai: tiene que poder bajar la referencia de este sitio y llamar a la API (ver [paso 3](#paso-3-pasarle-el-prompt-a-claude)) |
| **Una API Key** | La creás vos mismo en el BackOffice ([paso 1](#paso-1-crear-la-api-key)) |
| **Los datos de conexión** | URL, identificador del municipio y tu ID de usuario ([paso 2](#paso-2-pedir-los-datos-de-conexion)) |

---

## Paso 1: crear la API Key

1. En el BackOffice, entrá a **API Keys** → **Nueva API Key**.
2. Tipo **API**. Nombre que identifique el uso, por ejemplo *"Asistente IA — Ana Pérez"*.
3. Poné **fecha de vencimiento** (recomendado: 90 días). Si la key se filtra, vence sola.
4. Copiá la key (`sk-gdi-…`): **se muestra una sola vez**. Guardala en un gestor de
   contraseñas.
5. Abrí la key recién creada y, en **Usuarios autorizados**, agregate **a vos mismo**.
   Sin este paso la API responde *"Usuario no autorizado para esta API Key"*.

!!! danger "Una API Key abre más que el BackOffice"
    La misma key sirve también para la [API del Gateway](../desarrollo/gateway/autenticacion.md)
    (documentos y expedientes) con los usuarios que autorices en ella. Por eso:

    - Creá una key **exclusiva** para el asistente, autorizá **solo a tu usuario** y no la
      reutilices para otras integraciones.
    - **Desactivala** cuando no la uses y borrala si dejás el cargo.
    - Nunca la pegues en documentos compartidos, mails ni capturas de pantalla.

## Paso 2: pedir los datos de conexión

Además de la key, Claude necesita tres datos que hoy entrega GDI. Pedilos a
**soporte@gdilatam.com** indicando tu municipio y tu email de administrador:

| Variable | Qué es | Ejemplo |
|---|---|---|
| `GDI_BO_URL` | URL de la API del BackOffice de tu municipio | `https://backoffice-api.your-domain.com` |
| `GDI_BO_SCHEMA` | Identificador de tu municipio en GDI | `101_ejemplo` |
| `GDI_BO_USER_ID` | Tu ID de usuario (UUID) | `550e8400-e29b-41d4-a716-446655440000` |
| `GDI_BO_API_KEY` | La key del paso 1 | `sk-gdi-…` |

## Paso 3: pasarle el prompt a Claude

1. Copiá el prompt de abajo (botón de copiar, arriba a la derecha) o
   [descargalo como .txt](../descargas/gdi-backoffice-admin-prompt.txt).
2. Completá los tres `<completar>` con tus datos de conexión (paso 2).
3. Pegalo al **empezar cada conversación** con Claude. Lo primero que va a hacer es bajar la
   referencia completa de `docs.gdilatam.com` y leerla; después prueba la conexión y espera tu
   pedido.

```text
--8<-- "docs/descargas/gdi-backoffice-admin-prompt.txt"
```

!!! info "Acceso a internet"
    Claude tiene que poder salir a internet a **dos** lugares: `docs.gdilatam.com`, para bajar
    la referencia, y el dominio de tu `GDI_BO_URL`, para llamar a la API.

    - **Claude Code:** ya tiene acceso. Conviene cargar la API Key como variable de entorno en
      `~/.claude/settings.json`, que solo lee tu usuario, así no la pegás en el chat:

        ```json
        {
          "env": {
            "GDI_BO_API_KEY": "<tu-api-key>"
          }
        }
        ```

    - **claude.ai / Claude Desktop:** en **Configuración → Capacidades**, habilitá la ejecución
      de código con acceso a red. Si te pide una lista de dominios, agregá los dos. La key que
      pegues queda en el historial de ese chat: usá una key con vencimiento y borrá la
      conversación si la compartís.

!!! tip "Si Claude no puede bajar la referencia"
    El prompt le pide que te avise y no siga. En ese caso, descargá vos la
    [referencia completa (.txt)](../descargas/gdi-backoffice-admin-referencia.txt) y adjuntásela
    en la conversación junto con el prompt.

## Paso 4: probar

Pedile a Claude:

> *"Conectate al BackOffice de GDI y decime cuántos usuarios activos tenemos."*

Tiene que responder con los datos de tu municipio. Si aparece un error, la skill trae la
tabla de errores y le explica a Claude qué revisar; los más comunes:

| Mensaje | Causa |
|---|---|
| `Usuario no autorizado para esta API Key` | Falta el punto 5 del paso 1 |
| `NOT_ADMIN` | El `GDI_BO_USER_ID` no es de un administrador |
| `API Key no autorizada para este tenant` | `GDI_BO_SCHEMA` no corresponde a tu municipio |
| `API Key desactivada` / `expirada` | Generá una nueva (paso 1) |

---

## Qué puede y qué no puede hacer

| Puede | No puede |
|---|---|
| Usuarios: alta, edición, sellos, permisos, rol Administrador, desactivar, archivar, reenviar invitación | Crear el municipio, el onboarding y la licencia |
| Organigrama: reparticiones, sectores, titulares, rangos, sellos | Borrar una repartición que alguna vez tuvo un sector de trabajo (hoy la API lo rechaza) |
| Tipos de documento y de expediente: habilitar desde el catálogo, configurar | Crear, firmar o asignar documentos y expedientes (eso es la API del Gateway) |
| Familias de legajos, ciudadanos de la Base TAD, configuración del municipio | Aprobar propuestas al catálogo global (lo hace GDI) |
| API Keys, estadísticas, auditoría, organigrama en Excel | |

Los certificados de firma y el logo del municipio se pueden subir por API, pero conviene
hacerlo desde la pantalla: llevan archivos y contraseñas.

## Opcional: instalarla como skill

Si usás Claude todos los días y no querés pegar el prompt en cada conversación, podés
instalar el mismo contenido como **skill**. Claude la carga sola cuando le pedís algo del
BackOffice. La contra es que queda fija la versión que bajaste: cuando GDI actualice la
referencia, hay que volver a descargarla.

[:material-download: Descargar la skill (ZIP)](../descargas/gdi-backoffice-admin.zip){ .md-button }

=== "Claude Code"

    1. Descomprimí el ZIP en tu carpeta de skills, de modo que quede
       `~/.claude/skills/gdi-backoffice-admin/SKILL.md`.
    2. Cargá las cuatro variables en `~/.claude/settings.json`:

        ```json
        {
          "env": {
            "GDI_BO_URL": "https://backoffice-api.your-domain.com",
            "GDI_BO_SCHEMA": "101_ejemplo",
            "GDI_BO_USER_ID": "<tu-user-id>",
            "GDI_BO_API_KEY": "<tu-api-key>"
          }
        }
        ```

    3. Abrí Claude Code de nuevo para que tome la skill y las variables.

=== "claude.ai / Claude Desktop"

    1. En **Configuración → Capacidades → Skills**, subí el ZIP sin descomprimirlo.
    2. Habilitá la ejecución de código con acceso a red (ver paso 3).
    3. Al empezar cada conversación, pasale los datos de conexión.

## Límites

- **60 pedidos por minuto.** En cargas masivas la skill le indica a Claude ir de a uno por
  segundo; una carga de 100 usuarios lleva un par de minutos.
- **Confirmación para cambios delicados.** Antes de borrar, desactivar, archivar, quitar el
  rol de Administrador o cambiar un email, Claude te muestra qué se pierde y espera tu "sí".
- **La licencia manda.** Si la licencia del municipio no está operativa, la API se bloquea
  igual que la pantalla.
