# Operar el BackOffice con IA (API)

Todo lo que hacés en el BackOffice (dar de alta usuarios, armar el organigrama, habilitar
tipos de documento, revisar la auditoría) también se puede hacer **pidiéndoselo a tu
asistente de IA** (Claude), que opera el BackOffice por su API en tu nombre.

Por ejemplo:

- *"Dá de alta a estas 12 personas de la planilla en el sector MESA de Obras Públicas."*
- *"Creá la Dirección de Tránsito dentro de la Secretaría de Gobierno, con un sector MESA, y poné de titular a Juan Gómez."*
- *"¿Quién cambió el organigrama la semana pasada?"*
- *"Habilitá el tipo de documento Acta para Legales y que solo lo firmen Directores."*

Para eso GDI publica una **skill**: un paquete de instrucciones que le enseña a Claude cómo
funciona el BackOffice, qué endpoints tiene y qué reglas de cuidado seguir.

[:material-download: Descargar la skill (ZIP)](../descargas/gdi-backoffice-admin.zip){ .md-button .md-button--primary }
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
| **Claude** | Claude Code, Claude Desktop o claude.ai (ver [paso 3](#paso-3-instalar-la-skill)) |
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

## Paso 3: instalar la skill

=== "Claude Code"

    1. Descargá el [ZIP](../descargas/gdi-backoffice-admin.zip) y descomprimilo en tu
       carpeta de skills, de modo que quede `~/.claude/skills/gdi-backoffice-admin/SKILL.md`.
    2. Cargá las cuatro variables en tu entorno. La forma más simple es agregarlas al
       archivo `~/.claude/settings.json`, que solo lee tu usuario:

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

    1. Descargá el [ZIP](../descargas/gdi-backoffice-admin.zip) (no lo descomprimas).
    2. En Claude, entrá a **Configuración → Capacidades → Skills** y subí el ZIP.
    3. Claude necesita salir a internet para llamar a la API: en **Configuración →
       Capacidades** habilitá la ejecución de código con acceso a red y, si te pide una
       lista de dominios, agregá el de tu `GDI_BO_URL`. Si tu plan no lo permite, usá
       Claude Code.
    4. Al empezar cada conversación, pasale los datos de conexión. Tené en cuenta que la
       key queda en el historial de ese chat: usá una key con vencimiento y borrá la
       conversación si la compartís.

=== "Copiar el SKILL.md"

    Si preferís crear la skill a mano, este es el `SKILL.md` completo. La lista de endpoints
    va en `reference/endpoints.md`, al lado: la encontrás [acá](operar-por-api-referencia.md)
    y dentro del ZIP.

    ````markdown
    --8<-- "skills/gdi-backoffice-admin/SKILL.md"
    ````

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

## Límites

- **60 pedidos por minuto.** En cargas masivas la skill le indica a Claude ir de a uno por
  segundo; una carga de 100 usuarios lleva un par de minutos.
- **Confirmación para cambios delicados.** Antes de borrar, desactivar, archivar, quitar el
  rol de Administrador o cambiar un email, Claude te muestra qué se pierde y espera tu "sí".
- **La licencia manda.** Si la licencia del municipio no está operativa, la API se bloquea
  igual que la pantalla.
