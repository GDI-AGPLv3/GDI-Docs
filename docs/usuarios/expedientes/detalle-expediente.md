# Detalle del Expediente

Esta pantalla muestra la informacion completa de un expediente electronico: su panel de gestion (sectores, responsables y resumen IA), los documentos que lo componen, el historial de actividad y el asistente de inteligencia artificial. Se accede haciendo click en cualquier expediente desde el listado de expedientes.

![Detalle del expediente - Pestana Panel](../capturas/expediente-panel.png)

---

## Header del expediente

En la parte superior de la pantalla se muestra la informacion general del expediente en dos lineas compactas. El header es comun a todas las pestanas.

### Primera linea: titulo y numero

| Elemento | Descripcion |
|----------|-------------|
| **Flecha de retorno** | Vuelve al listado de expedientes, preservando la solapa activa |
| **Titulo** | Nombre descriptivo del expediente (motivo de creacion) |
| **Numero oficial** | Identificador unico mostrado junto al titulo, con boton para copiar al portapapeles |
| **Estrella** (favorito) | Marca o desmarca el expediente como favorito. Amarilla cuando esta activa. Se sincroniza inmediatamente con el servidor |
| **Boton "Acciones"** | Desplegable con las operaciones disponibles sobre el expediente |

### Segunda linea: resumen inline

Debajo del titulo se muestra un resumen de los datos del expediente en una sola linea separada por barras:

| Dato | Descripcion | Ejemplo |
|------|-------------|---------|
| **Tipo** | Sigla y nombre del tipo de tramite | `HABI - Habilitacion comercial de local gastronomico` |
| **Admin** | Sector administrador actual (badge de color) con el avatar del responsable administrador inline | `CONT#PRIV` |
| **Act** | Sector actuante con las iniciales de la persona asignada. Si no hay actuante, aparece el badge **"Sin asignar"** | `LEGAL#PRIV` o badge "Sin asignar" |

### Opciones del menu "Acciones"

| Opcion | Descripcion |
|--------|-------------|
| **Descargar** | Descarga un archivo ZIP con todos los documentos oficiales del expediente. Ver seccion [Descargar expediente como ZIP](#descargar-expediente-como-zip) |
| **Nuevo Movimiento** | Abre el modal para crear una nueva asignacion o transferencia. Ver [Nueva Tarea / Asignacion](#nueva-tarea-asignacion) |
| **Vincular Documentos** | Navega a la pestana Documentos y abre el modal de vinculacion. Ver [Vincular Documentos](vincular-documentos.md) |
| **Subsanar** | Abre el proceso guiado de subsanacion. Ver [Subsanar en Expediente](subsanar-expediente.md) |

---

## Pestanas disponibles

La pantalla se organiza en cuatro pestanas:

| Pestana | Descripcion |
|---------|-------------|
| **Panel** | Vista de gestion del expediente: sector administrador, responsables, resumen IA y sectores actuantes (pestana por defecto) |
| **Documentos** | Lista de documentos oficiales y propuestos del expediente |
| **Historial** | Historial de actividad y acciones realizadas sobre el expediente. Ver [Historial](movimientos.md) |
| **Tu Asistente** | Asistente de inteligencia artificial para consultas sobre el expediente. Ver [Tu Asistente](../asistente-ai/index.md) |

!!! info "Panel es la pestana por defecto"
    Al abrir un expediente, la pestana **Panel** se muestra activa. La antigua pestana "Movimientos" ahora se llama **Historial**.

---

## Pestana Panel

Es la pestana central del expediente. Concentra la gestion de quien controla el expediente, quienes son sus responsables y que sectores estan actuando sobre el. Se organiza en dos columnas.

![Pestana Panel del expediente](../capturas/expediente-panel.png)

### Columna izquierda: administracion y responsables

#### Sector Administrador

La tarjeta **"SECTOR ADMINISTRADOR"** muestra el badge del sector que controla el expediente (por ejemplo `CONT#PRIV`). Es el area organizacional responsable del expediente.

#### Responsables

Debajo, la seccion **"RESPONSABLES"** lista cada responsable asignado:

| Elemento | Descripcion |
|----------|-------------|
| **Avatar y nombre** | Foto o iniciales del responsable, su nombre y su sector |
| **Boton "Quitar responsable" (X)** | Quita al responsable de la lista |
| **"Sin responsables asignados."** | Mensaje que aparece cuando no hay ningun responsable |
| **Boton "+ responsable"** | Abre el modal para agregar un responsable administrador |
| **Boton "Transferir"** | Cede el control administrativo del expediente a otro sector |

!!! note "Responsable administrador y responsables adicionales"
    El expediente puede tener un **responsable administrador** principal y **responsables adicionales**. El responsable administrador solo puede elegirse entre los usuarios del **sector administrador** del expediente.

##### Modal "Agregar responsable administrador"

El boton **"+ responsable"** abre el modal titulado **"Agregar responsable administrador - Busca y elegi la persona"**. El buscador solo muestra usuarios pertenecientes al sector administrador. Al elegir una persona y confirmar, queda registrada como responsable.

#### Resumen del expediente (IA)

La tarjeta **"RESUMEN DEL EXPEDIENTE"**, identificada con el badge **"IA"**, muestra un resumen generado automaticamente por inteligencia artificial a partir de los documentos y movimientos del expediente. Si todavia no se genero, muestra el mensaje **"Todavia no hay resumen."**.

!!! info "Resumen no oficial"
    El resumen generado por IA es un apoyo informativo. No constituye un documento oficial ni reemplaza la lectura de los documentos del expediente.

### Columna derecha: Sectores Actuantes

La columna **"Sectores Actuantes"** lista los sectores que tienen acceso para actuar sobre el expediente sin controlarlo. Un contador en el encabezado indica cuantos hay (por ejemplo **"1 abiertos"**).

Cada sector actuante se muestra como una tarjeta con:

| Elemento | Descripcion |
|----------|-------------|
| **Badge del sector** | Sigla del sector actuante (por ejemplo `LEGAL#PRIV`) |
| **Persona asignada** | Avatar, nombre y fecha de la persona a cargo de la tarea |
| **Motivo** | Texto de la solicitud (`Motivo: ...`) |
| **Boton "Reasignar responsable"** | Cambia la persona asignada dentro del sector actuante |
| **Boton "Cerrar tarea"** | Cierra la tarea de ese sector actuante |
| **Boton "Cerrar"** | Cierra el sector actuante |

Debajo de las tarjetas hay una caja punteada **"Nueva Tarea / Asignacion — Asignar un sector o una persona"** con un boton **+** que abre el modal de nuevo movimiento.

---

## Nueva Tarea / Asignacion

El boton **"Nueva Tarea / Asignacion"** (la caja punteada de la columna Sectores Actuantes, o la opcion **"Nuevo Movimiento"** del menu Acciones) abre el modal **"Nuevo Movimiento — &lt;numero&gt;"**, con dos pestanas: **Asignacion** y **Transferencia**.

![Modal Nuevo Movimiento - pestana Asignacion](../capturas/expediente-asignacion-modal.png)

### Asignacion

Solicita una **Actuacion Interna**: otorgas acceso a otros sectores **sin perder el control** del Expediente. El sector asignado puede consultar los documentos y realizar las tareas solicitadas, pero el sector administrador mantiene la responsabilidad.

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| **Sector a Asignar (persona opcional)** | Combobox con busqueda | Al escribir 2 o mas caracteres busca y agrupa los resultados en **"Solo sector"** y **"Personas"**. Si se elige una persona, se muestran sus sectores para seleccionar uno |
| **Motivo (min. 5 caracteres)** | Textarea | Descripcion de lo que se solicita. Muestra un contador `/500` |
| **Sector Solicitante** | Texto fijo | El sector del usuario que realiza la solicitud. No es editable |
| **Asentar en el expediente** | Si / No | Si es **Si**, genera una providencia de pase (PV) que queda registrada en la pestana Documentos |

| Boton | Accion |
|-------|--------|
| **Cancelar** | Cierra el modal sin crear la asignacion |
| **Confirmar Asignacion** | Crea la actuacion interna y otorga el acceso al sector o persona elegida |

!!! info "Asignar otorga acceso, no cede el control"
    Una asignacion suma al sector o persona como **actuante**: obtiene acceso para consultar y actuar sobre el expediente, pero el control administrativo sigue en el sector administrador.

### Transferencia

La pestana **Transferencia** **cede el control administrativo** del expediente a otro sector, igual que la transferencia clasica. A diferencia de la asignacion, el sector que transfiere pierde el rol de administrador y el sector destino pasa a ser el nuevo administrador.

!!! warning "La transferencia cambia el administrador"
    Al transferir, el sector de origen pierde el control administrativo. Solo el nuevo sector administrador podra volver a transferir el expediente o gestionarlo.

---

## Pestana Documentos

Lista los documentos que componen el expediente y permite previsualizar cada PDF.

![Pestana Documentos](../capturas/expediente-documentos.png)

### Documentos oficiales

La seccion colapsable **"DOCUMENTOS OFICIALES (N)"** muestra un contador con la cantidad total de documentos incorporados. Cada documento de la lista muestra:

| Elemento | Descripcion | Ejemplo |
|----------|-------------|---------|
| **Numero de orden** | Posicion dentro del expediente (001, 002, 003...) | `001` |
| **Numero oficial** | Identificador unico del documento, con boton para copiar | `CAEX-2026-00000133-...` |
| **Fecha** | Fecha de incorporacion al expediente | `18/02/26` |
| **Referencia** | Titulo descriptivo del documento | *Creacion del expediente* |
| **Linea de vinculacion** | `Vinculado el FECHA por USUARIO / Sector: SECTOR` | — |
| **Resumen IA** | A veces, un resumen de una linea generado por inteligencia artificial | — |

Al hacer click en un documento de la lista, se muestra una **vista previa del PDF** en el panel derecho.

!!! info "Primer documento: Caratula (CAEX)"
    El documento numero 001 de todo expediente es siempre la **caratula** (tipo CAEX), generada automaticamente por el sistema al crear el expediente. Contiene los datos basicos: tipo, numero, motivo y reparticion iniciadora.

El boton **"Vincular Documento"** abre el flujo de vinculacion. Ver [Vincular Documentos](vincular-documentos.md).

### Documentos propuestos

Cuando hay vinculaciones pendientes, aparece la seccion **"DOCUMENTOS PROPUESTOS"**, que muestra los documentos cuya vinculacion fue solicitada pero aun no fue aceptada por el sector administrador.

Cada documento propuesto muestra:

| Elemento | Descripcion |
|----------|-------------|
| **Badge "VINCULACION PROPUESTA"** | Etiqueta que indica que el documento esta pendiente de aceptacion |
| **Estado de firma** | Badge "En firma" o "Firmado", segun el estado actual del documento |
| **Menu "Acciones"** | Desplegable con las opciones disponibles segun el estado del documento |

#### Acciones sobre documentos propuestos

| Accion | Disponible cuando | Descripcion |
|--------|-------------------|-------------|
| **Aceptar Vinculacion** | El documento esta **Firmado** | Incorpora el documento al expediente como documento oficial. Se le asigna un numero de orden |
| **Rechazar Vinculacion** | Siempre (Firmado o En firma) | Rechaza la propuesta. El documento no se incorpora al expediente |

!!! warning "Documentos en firma"
    Un documento que esta **"En firma"** (aun no fue firmado por todos los firmantes) solo puede ser **rechazado**. La opcion "Aceptar Vinculacion" no esta disponible hasta que el documento este completamente firmado.

---

## Pestana Historial

La pestana **Historial** (antes "Movimientos") muestra la linea de tiempo de actividad del expediente: que documentos se vincularon, que acciones se realizaron, quien las ejecuto y cuando. Tiene su propia pagina: ver [Historial](movimientos.md).

---

## Pestana Tu Asistente

La pestana **Tu Asistente** abre el asistente de inteligencia artificial, que responde consultas sobre el contenido del expediente. Ver [Tu Asistente](../asistente-ai/index.md).

---

## Descargar expediente como ZIP

La opcion **"Descargar"** del menu Acciones genera y descarga un archivo `.zip` con todos los documentos oficiales activos del expediente.

### Que incluye el ZIP

- Solo los **documentos oficiales** del expediente (no borradores ni propuestas pendientes).
- El ZIP se nombra con el numero oficial del expediente: por ejemplo `EE-2026-000019-TXST-CONT.zip`.
- Cada PDF dentro del ZIP se nombra con su numero de orden y numero oficial: `001 - CAEX-2026-00000133-TXST-CONT.pdf`, `002 - IF-2026-00000136-TXST-CONT.pdf`, etc.

### Como descargar

1. Abrir el expediente.
2. Hacer click en el boton **"Acciones"** (esquina superior derecha).
3. Seleccionar **"Descargar"**.
4. El sistema prepara el archivo. El boton muestra el texto *"Descargando..."* mientras procesa.
5. El archivo `.zip` se descarga automaticamente al completarse.

!!! info "Expedientes grandes"
    Expedientes con muchos documentos pueden tardar unos segundos en prepararse antes de que comience la descarga. El boton queda deshabilitado durante ese tiempo para evitar descargas duplicadas.

!!! note "Solo documentos oficiales"
    Los documentos en estado de propuesta (pendientes de aceptacion) y los documentos subsanados no se incluyen en el ZIP.

---

## Preguntas frecuentes

??? question "Cual es la diferencia entre asignacion y transferencia?"
    La **asignacion** (actuacion interna) otorga acceso a otro sector o persona sin perder el control: el sector administrador sigue siendo el mismo. La **transferencia** cede el control administrativo al sector destino, que pasa a ser el nuevo administrador.

??? question "Quien puede ser responsable administrador?"
    El responsable administrador solo puede elegirse entre los usuarios del **sector administrador** del expediente. Se asigna desde el modal "Agregar responsable administrador" en la pestana Panel.

??? question "Que es el badge IA en la tarjeta de resumen?"
    Indica que el resumen del expediente fue generado automaticamente por inteligencia artificial a partir de sus documentos y movimientos. Si aun no se genero, muestra "Todavia no hay resumen.".

??? question "Que significa el contador 'N abiertos' en Sectores Actuantes?"
    Es la cantidad de sectores actuantes activos sobre el expediente, es decir, los sectores a los que se les otorgo acceso mediante una asignacion y que todavia no fueron cerrados.

??? question "Una asignacion genera algun documento en el expediente?"
    Si el campo **"Asentar en el expediente"** queda en **Si**, la asignacion genera una providencia de pase (PV) que queda registrada en la pestana Documentos.

??? question "Puedo ver el contenido de un documento sin descargarlo?"
    Si. En la pestana Documentos, al hacer click en cualquier documento de la lista se muestra una vista previa del PDF en el panel derecho.

??? question "Que significa el numero de orden de cada documento?"
    Es la posicion cronologica del documento dentro del expediente. El 001 es siempre la caratula, y los siguientes se numeran en el orden en que fueron incorporados.

??? question "Quien puede aceptar o rechazar documentos propuestos?"
    Solo el **sector administrador** del expediente puede aceptar o rechazar propuestas de vinculacion de documentos.

??? question "Puedo copiar el numero del expediente o de un documento?"
    Si. Junto al numero oficial del expediente (en la primera linea del header) y junto a cada numero de documento hay un boton de copia que permite copiar al portapapeles con un solo click.

??? question "Que es la estrella junto al boton Acciones?"
    Es el boton de **favorito**. Al hacer click, marca el expediente como favorito (estrella amarilla) o lo desmarca. Los expedientes marcados como favoritos aparecen en la solapa "Favoritos" del listado de expedientes.

??? question "El ZIP incluye todos los documentos del expediente?"
    Incluye todos los documentos **oficiales** activos. No incluye documentos en estado de propuesta de vinculacion ni documentos que hayan sido subsanados (reemplazados por otro documento).
