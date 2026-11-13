# Inicio

**Inicio** (`/inicio`) es la primera pantalla que se abre al entrar al sistema y el tablero de pendientes de cada usuario. Reune en un solo lugar lo que antes estaba repartido entre el Dashboard y la pantalla de Notificaciones, que ya no existen.

La pantalla responde a una sola pregunta: **que tengo que hacer hoy**. Todo lo que aparece ahí es información propia del usuario y de su sector; no es un panel de estadísticas del organismo.

---

## Estructura de la pantalla

Inicio se organiza en dos columnas (en pantallas chicas se apilan):

| Zona | Contenido |
|------|-----------|
| **Buscador** (arriba, ancho completo) | Barra de búsqueda única del sistema: documentos y expedientes |
| **Columna izquierda** | Las tres secciones de pendientes: *Requieren tu acción*, *En tus expedientes*, *En tu sector* |
| **Columna derecha** | *Tu día* (contadores), *Accesos rápidos* y *Tu perfil* |

Debajo del buscador aparece el saludo según la hora ("Buenos días / Buenas tardes / Buenas noches") con el nombre del usuario y, si hay pendientes, la frase **"tenés N cosas por resolver"**. Ese número es el mismo que muestra el **globo rojo** del ítem **Inicio** en el menú lateral.

!!! info "El contador rojo"
    El contador rojo cuenta **solo** las tres cajas de "Requieren tu acción" (firmas, memos y notas). Las secciones "En tus expedientes" y "En tu sector" son informativas y **no suman** al contador.

---

## Requieren tu acción

Son los pendientes que dependen del usuario y que nadie más va a resolver por él. Se muestran en tres cajas.

| Caja | Que muestra | Alcance | Cuando desaparece |
|------|-------------|---------|-------------------|
| **Esperando tu firma** | Documentos enviados a la firma del usuario. Muestra tipo, referencia y quien lo envió. No muestra número: el documento se numera recién al firmarse | Personal | Al firmar o rechazar el documento |
| **Memos sin leer** | Memos dirigidos al usuario. Muestra remitente, número oficial y referencia | Personal (dirigidos a él) | Cuando el propio usuario lo abre |
| **Notas al Sector sin abrir** | Notas dirigidas al sector del usuario. El remitente es una **etiqueta de sector** (por ejemplo `HAC#MESA`), nunca una persona | Del sector | Cuando **cualquier** integrante del sector la abre |

Cada fila se abre con un click (o con el botón **"Abrir"** / **"Ir a firmar"**). Si hay más de una firma pendiente, el pie de la caja ofrece **"Firmar todo junto"**, que lleva a la pantalla de firma conjunta.

---

## En tus expedientes

Novedades de los expedientes del usuario. Tiene un selector de alcance en el encabezado:

| Opción | Muestra |
|--------|---------|
| **Mio** | Expedientes donde el usuario es administrador o actuante |
| **Todo** | Todos los expedientes que el usuario tiene permiso de ver |

Si "Mio" no trae nada en la primera carga, la pantalla pasa sola a "Todo" (una única vez, para no pisar la elección manual del usuario).

La sección agrupa tres tipos de fila:

| Fila | Significado |
|------|-------------|
| **Te nombraron responsable** | Otro usuario designo al usuario como responsable de un expediente. Indica quién lo asignó y, si la hay, la razón |
| **Te mencionaron** | Alguien mencionó al usuario en un comentario del expediente. Se muestra siempre, incluso sin acceso al expediente |
| **N movimientos nuevos** | Resumen agrupado por expediente: cantidad de movimientos no vistos y fecha del último |

!!! warning "Menciones sin acceso"
    Si el usuario fue mencionado en un expediente al que **no** tiene acceso, la fila muestra la etiqueta **"sin acceso"** con un candado y el click **no navega**: avisa que hay que pedir acceso al sector responsable. Esto evita llevar al usuario a una pantalla de permiso denegado.

### El "visto" de los expedientes

La fila **"N movimientos nuevos"** cuenta los movimientos posteriores a la última vez que el usuario **vio** ese expediente.

- El contador se resetea **solo** al abrir el expediente: el sistema registra la visita al entrar al detalle.
- También se puede dar por visto **sin abrirlo**, con la **✕** de la fila. Es exactamente el mismo efecto que abrirlo: baja el contador a cero.
- No es un "marcar como leído" por movimiento: es una única marca de "hasta acá lo vi" por expediente y usuario.

### Descartar avisos

Los avisos de **"Te nombraron responsable"** y **"Te mencionaron"** se cierran con la **✕** de la fila, o al entrar al expediente. Descartar un aviso solo lo saca de Inicio: no cambia nada del expediente ni afecta a otros usuarios.

---

## En tu sector

Sección **informativa**: muestra trabajo que le corresponde al sector del usuario pero que todavía nadie tomó. **No suma al contador rojo.**

| Caja | Que muestra | Quién es dueño del expediente |
|------|-------------|-------------------------------|
| **Transferidos a tu sector, sin responsable** | Expedientes transferidos al sector del usuario que nadie tomó como responsable | El sector del usuario |
| **Tareas para tu sector, sin tomar** | Tareas asignadas al sector del usuario que nadie tomó | Otro sector |

Las filas de estas cajas **solo abren el expediente**: no hay botones para hacerse responsable ni para tomar la tarea desde Inicio. Esas acciones se hacen **dentro del expediente**, después de ver de que se trata.

Cuando hay más ítems de los que entran en la caja, el pie ofrece un acceso al listado de Expedientes con el filtro correspondiente ya aplicado.

---

## Panel derecho

### Tu día

Contadores de la jornada. Cada fila con un valor mayor a cero es clickeable: lleva a la caja correspondiente de la columna izquierda y la resalta un instante.

| Fila | Corresponde a |
|------|---------------|
| **Para firmar** | Esperando tu firma |
| **Memos sin leer** | Memos sin leer |
| **Notas al Sector** | Notas al Sector sin abrir |
| **Sin responsable** *(informativo)* | Transferidos a tu sector, sin responsable |
| **Tareas sin tomar** *(informativo)* | Tareas para tu sector, sin tomar |

Las tres primeras suman al contador rojo; las dos últimas, marcadas como **Informativo**, no.

### Accesos rápidos

| Acceso | Que hace |
|--------|----------|
| **Crear documento** | Abre el diálogo de creación de documento, sin salir de Inicio |
| **Documentos** | Va al listado de documentos |
| **Expedientes** | Va al listado de expedientes |
| **Legajos** | Va al listado de legajos |

### Tu perfil

Resumen de contexto del usuario: **organización** (municipio activo), **sello** por defecto asignado y **sector** al que pertenece.

---

## Cómo se comporta la pantalla

| Comportamiento | Detalle |
|----------------|---------|
| **Apertura en pestaña nueva** | Todos los ítems de Inicio (documentos, memos, notas y expedientes) se abren en una **pestaña nueva**: el usuario resuelve el ítem y vuelve a Inicio sin perder el resto de la lista |
| **Resumen con inteligencia artificial** | Al pasar el mouse por una fila, el contenido se reemplaza por el resumen automático del documento o expediente. Si no hay resumen, indica "Sin resumen disponible" |
| **Tope de ítems por caja** | Cada caja lista hasta **5** ítems. El número del encabezado siempre muestra el **total real**, y el pie avisa "Tenés N más" |
| **Actualización automática** | El contador se actualiza solo cada 30 segundos, y todas las cajas se refrescan al volver a la pestaña de Inicio |
| **Teclado** | Las filas se pueden recorrer con el tabulador y activar con <kbd>Enter</kbd> o <kbd>Espacio</kbd> |

---

## Cuando no hay nada pendiente

Si no hay firmas, ni memos, ni notas, ni movimientos ni expedientes sin asignar, la pantalla muestra el estado **"Estas al día"** con el detalle de lo que se verificó:

- Firmas pendientes — ninguna
- Memos y notas — todo leído
- Transferidos sin responsable — ninguno
- Tareas para tu sector sin tomar — ninguna
- Movimientos nuevos en tus expedientes — nada nuevo

---

## Preguntas frecuentes

??? question "Por qué un aviso que descarte no aparece más?"
    Descartar con la **✕** oculta el aviso solo para el usuario que lo descartó y solo en Inicio. El hecho sigue registrado en el historial del expediente, donde se puede consultar cuando se quiera.

??? question "Por qué una nota desaparecio si yo no la abrí?"
    Las notas son del **sector**, no de una persona. Alcanza con que cualquier integrante del sector la abra para que salga de la caja de todos.

??? question "Por qué el número del encabezado de una caja no coincide con la cantidad de filas?"
    Cada caja lista hasta 5 ítems, pero el encabezado muestra el total real. La diferencia se indica en el pie de la caja ("Tenés N más").

??? question "Qué diferencia hay entre las cajas rojas y las informativas?"
    Las de **"Requieren tu acción"** son pendientes personales que solo el usuario puede resolver y suman al contador rojo del menú. Las de **"En tu sector"** son trabajo disponible para el sector: se muestran para dar visibilidad, pero no son una obligación personal.

??? question "Dónde quedaron el Dashboard y la pantalla de Notificaciones?"
    Ya no existen. Todo lo que mostraban está ahora en Inicio: los pendientes en las cajas de acción, y el feed de notificaciones convertido en avisos y movimientos agrupados por expediente.
