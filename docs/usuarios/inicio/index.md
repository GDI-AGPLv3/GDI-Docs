# Inicio

**Inicio** (`/inicio`) es la primera pantalla que se abre al entrar al sistema y el tablero de pendientes de cada usuario. Reune en un solo lugar lo que antes estaba repartido entre el Dashboard y la pantalla de Notificaciones, que ya no existen.

La pantalla responde a una sola pregunta: **que tengo que hacer hoy**. Todo lo que aparece ahi es informacion propia del usuario y de su sector; no es un panel de estadisticas del organismo.

---

## Estructura de la pantalla

Inicio se organiza en dos columnas (en pantallas chicas se apilan):

| Zona | Contenido |
|------|-----------|
| **Buscador** (arriba, ancho completo) | Barra de busqueda unica del sistema: documentos y expedientes |
| **Columna izquierda** | Las tres secciones de pendientes: *Requieren tu accion*, *En tus expedientes*, *En tu sector* |
| **Columna derecha** | *Tu dia* (contadores), *Accesos rapidos* y *Tu perfil* |

Debajo del buscador aparece el saludo segun la hora ("Buenos dias / Buenas tardes / Buenas noches") con el nombre del usuario y, si hay pendientes, la frase **"tenes N cosas por resolver"**. Ese numero es el mismo que muestra el **globo rojo** del item **Inicio** en el menu lateral.

!!! info "El contador rojo"
    El contador rojo cuenta **solo** las tres cajas de "Requieren tu accion" (firmas, memos y notas). Las secciones "En tus expedientes" y "En tu sector" son informativas y **no suman** al contador.

---

## Requieren tu accion

Son los pendientes que dependen del usuario y que nadie mas va a resolver por el. Se muestran en tres cajas.

| Caja | Que muestra | Alcance | Cuando desaparece |
|------|-------------|---------|-------------------|
| **Esperando tu firma** | Documentos enviados a la firma del usuario. Muestra tipo, referencia y quien lo envio. No muestra numero: el documento se numera recien al firmarse | Personal | Al firmar o rechazar el documento |
| **Memos sin leer** | Memos dirigidos al usuario. Muestra remitente, numero oficial y referencia | Personal (dirigidos a el) | Cuando el propio usuario lo abre |
| **Notas al Sector sin abrir** | Notas dirigidas al sector del usuario. El remitente es una **etiqueta de sector** (por ejemplo `HAC#MESA`), nunca una persona | Del sector | Cuando **cualquier** integrante del sector la abre |

Cada fila se abre con un click (o con el boton **"Abrir"** / **"Ir a firmar"**). Si hay mas de una firma pendiente, el pie de la caja ofrece **"Firmar todo junto"**, que lleva a la pantalla de firma conjunta.

---

## En tus expedientes

Novedades de los expedientes del usuario. Tiene un selector de alcance en el encabezado:

| Opcion | Muestra |
|--------|---------|
| **Mio** | Expedientes donde el usuario es administrador o actuante |
| **Todo** | Todos los expedientes que el usuario tiene permiso de ver |

Si "Mio" no trae nada en la primera carga, la pantalla pasa sola a "Todo" (una unica vez, para no pisar la eleccion manual del usuario).

La seccion agrupa tres tipos de fila:

| Fila | Significado |
|------|-------------|
| **Te nombraron responsable** | Otro usuario designo al usuario como responsable de un expediente. Indica quien lo asigno y, si la hay, la razon |
| **Te mencionaron** | Alguien menciono al usuario en un comentario del expediente. Se muestra siempre, incluso sin acceso al expediente |
| **N movimientos nuevos** | Resumen agrupado por expediente: cantidad de movimientos no vistos y fecha del ultimo |

!!! warning "Menciones sin acceso"
    Si el usuario fue mencionado en un expediente al que **no** tiene acceso, la fila muestra la etiqueta **"sin acceso"** con un candado y el click **no navega**: avisa que hay que pedir acceso al sector responsable. Esto evita llevar al usuario a una pantalla de permiso denegado.

### El "visto" de los expedientes

La fila **"N movimientos nuevos"** cuenta los movimientos posteriores a la ultima vez que el usuario **vio** ese expediente.

- El contador se resetea **solo** al abrir el expediente: el sistema registra la visita al entrar al detalle.
- Tambien se puede dar por visto **sin abrirlo**, con la **✕** de la fila. Es exactamente el mismo efecto que abrirlo: baja el contador a cero.
- No es un "marcar como leido" por movimiento: es una unica marca de "hasta aca lo vi" por expediente y usuario.

### Descartar avisos

Los avisos de **"Te nombraron responsable"** y **"Te mencionaron"** se cierran con la **✕** de la fila, o al entrar al expediente. Descartar un aviso solo lo saca de Inicio: no cambia nada del expediente ni afecta a otros usuarios.

---

## En tu sector

Seccion **informativa**: muestra trabajo que le corresponde al sector del usuario pero que todavia nadie tomo. **No suma al contador rojo.**

| Caja | Que muestra | Quien es dueno del expediente |
|------|-------------|-------------------------------|
| **Transferidos a tu sector, sin responsable** | Expedientes transferidos al sector del usuario que nadie tomo como responsable | El sector del usuario |
| **Tareas para tu sector, sin tomar** | Tareas asignadas al sector del usuario que nadie tomo | Otro sector |

Las filas de estas cajas **solo abren el expediente**: no hay botones para hacerse responsable ni para tomar la tarea desde Inicio. Esas acciones se hacen **dentro del expediente**, despues de ver de que se trata.

Cuando hay mas items de los que entran en la caja, el pie ofrece un acceso al listado de Expedientes con el filtro correspondiente ya aplicado.

---

## Panel derecho

### Tu dia

Contadores de la jornada. Cada fila con un valor mayor a cero es clickeable: lleva a la caja correspondiente de la columna izquierda y la resalta un instante.

| Fila | Corresponde a |
|------|---------------|
| **Para firmar** | Esperando tu firma |
| **Memos sin leer** | Memos sin leer |
| **Notas al Sector** | Notas al Sector sin abrir |
| **Sin responsable** *(informativo)* | Transferidos a tu sector, sin responsable |
| **Tareas sin tomar** *(informativo)* | Tareas para tu sector, sin tomar |

Las tres primeras suman al contador rojo; las dos ultimas, marcadas como **Informativo**, no.

### Accesos rapidos

| Acceso | Que hace |
|--------|----------|
| **Crear documento** | Abre el dialogo de creacion de documento, sin salir de Inicio |
| **Documentos** | Va al listado de documentos |
| **Expedientes** | Va al listado de expedientes |
| **Legajos** | Va al listado de legajos |

### Tu perfil

Resumen de contexto del usuario: **organizacion** (municipio activo), **sello** por defecto asignado y **sector** al que pertenece.

---

## Como se comporta la pantalla

| Comportamiento | Detalle |
|----------------|---------|
| **Apertura en pestana nueva** | Todos los items de Inicio (documentos, memos, notas y expedientes) se abren en una **pestana nueva**: el usuario resuelve el item y vuelve a Inicio sin perder el resto de la lista |
| **Resumen con inteligencia artificial** | Al pasar el mouse por una fila, el contenido se reemplaza por el resumen automatico del documento o expediente. Si no hay resumen, indica "Sin resumen disponible" |
| **Tope de items por caja** | Cada caja lista hasta **5** items. El numero del encabezado siempre muestra el **total real**, y el pie avisa "Tenes N mas" |
| **Actualizacion automatica** | El contador se actualiza solo cada 30 segundos, y todas las cajas se refrescan al volver a la pestana de Inicio |
| **Teclado** | Las filas se pueden recorrer con el tabulador y activar con <kbd>Enter</kbd> o <kbd>Espacio</kbd> |

---

## Cuando no hay nada pendiente

Si no hay firmas, ni memos, ni notas, ni movimientos ni expedientes sin asignar, la pantalla muestra el estado **"Estas al dia"** con el detalle de lo que se verifico:

- Firmas pendientes — ninguna
- Memos y notas — todo leido
- Transferidos sin responsable — ninguno
- Tareas para tu sector sin tomar — ninguna
- Movimientos nuevos en tus expedientes — nada nuevo

---

## Preguntas frecuentes

??? question "Por que un aviso que descarte no aparece mas?"
    Descartar con la **✕** oculta el aviso solo para el usuario que lo descarto y solo en Inicio. El hecho sigue registrado en el historial del expediente, donde se puede consultar cuando se quiera.

??? question "Por que una nota desaparecio si yo no la abri?"
    Las notas son del **sector**, no de una persona. Alcanza con que cualquier integrante del sector la abra para que salga de la caja de todos.

??? question "Por que el numero del encabezado de una caja no coincide con la cantidad de filas?"
    Cada caja lista hasta 5 items, pero el encabezado muestra el total real. La diferencia se indica en el pie de la caja ("Tenes N mas").

??? question "Que diferencia hay entre las cajas rojas y las informativas?"
    Las de **"Requieren tu accion"** son pendientes personales que solo el usuario puede resolver y suman al contador rojo del menu. Las de **"En tu sector"** son trabajo disponible para el sector: se muestran para dar visibilidad, pero no son una obligacion personal.

??? question "Donde quedaron el Dashboard y la pantalla de Notificaciones?"
    Ya no existen. Todo lo que mostraban esta ahora en Inicio: los pendientes en las cajas de accion, y el feed de notificaciones convertido en avisos y movimientos agrupados por expediente.
