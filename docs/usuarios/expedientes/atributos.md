# Atributos del expediente

La pestaña **Atributos e Historial** junta dos cosas en una sola pantalla:

- a la izquierda, el [Historial](movimientos.md) de siempre, con la línea de tiempo y el chat de comentarios;
- a la derecha, el **panel de atributos**, con datos del expediente que no son documentos.

El panel se puede ocultar con el botón **Ocultar atributos** y volver a mostrar con **Mostrar atributos**. Ocultarlo no cambia nada del expediente: solo deja más lugar para el Historial.

---

## Objetivo

La tarjeta **Objetivo** muestra el instructivo del **tipo de expediente**: para qué sirve el trámite, qué documentos lleva y cuándo termina. Lo escribe el administrador del municipio en el BackOffice (ver [Tipos de Expedientes](../../administradores/tipos-de-expedientes.md#objetivo)).

| Qué ves | Qué significa |
|---------|---------------|
| La tarjeta plegada, con el nombre del tipo | Hay un objetivo cargado. Abrila para leerlo |
| **"Sin objetivo"** | El tipo de expediente todavía no tiene objetivo. No es un error |
| **"Ver todo"** | El objetivo es largo y se muestra recortado. Tocalo para leerlo entero |

Por ejemplo, en la **Municipalidad del Futuro**, el tipo *Habilitación Comercial* puede tener este objetivo:

> Habilitar un local comercial en el municipio. Lleva: solicitud del titular, plano aprobado, informe de Bromatología y pago de la tasa. Termina con el certificado de habilitación.

!!! info "Es igual para todos los expedientes del mismo tipo"
    El objetivo es del **tipo** de expediente, no de cada expediente. Si el administrador lo cambia, el cambio se ve enseguida en todos los expedientes de ese tipo, también en los que están en trámite.

!!! tip "Lo usa Tu Asistente"
    El asistente de IA y el resumen del expediente leen el objetivo para saber de qué trata el trámite. Por ejemplo, podés preguntarle a **Tu Asistente** *"¿qué documentos le faltan a este expediente?"* y va a comparar lo que pide el objetivo con lo que ya está vinculado. El objetivo es información del trámite: no le da permisos al asistente ni cambia sus reglas.

---

## Estado

La tarjeta **Estado** muestra en qué momento está el expediente. La misma etiqueta se ve en el encabezado, al lado del número.

### Los 5 estados

| Estado | Qué significa | Qué se puede hacer |
|--------|---------------|--------------------|
| **En creación** | El expediente todavía no tiene carátula | Nada. Espera a que se vincule la carátula. Lo pone el sistema solo |
| **En trámite** | Se está trabajando | Todo: pases, asignaciones, tareas, comentarios y documentos |
| **Paralizado** | Se espera algo del vecino (por ejemplo, que traiga un papel) | Todo, igual que En trámite |
| **Suspendido** | Se espera a otro organismo o a otro expediente | Todo, igual que En trámite |
| **Cerrado** | El trámite terminó | Nada, salvo vincular un legajo. Va al [Archivo](archivo.md) |

Paralizado y Suspendido no frenan nada. Sirven para que se vea por qué el expediente está quieto. Sigue en los listados, en Inicio y en los contadores, y se puede pasar, asignar y comentar como siempre.

### Quién cambia el estado

Lo cambia **solo el sector administrador** del expediente, desde la tarjeta Estado. Siempre hay que escribir el **motivo** (entre 5 y 500 caracteres). El cambio queda en el [Historial](movimientos.md) con quién lo hizo, cuándo y el motivo.

Por ejemplo, en la **Municipalidad del Futuro**, Lucía, de Mesa de Entradas de Habilitaciones, administra el expediente `EE-2026-000414-MUNDEV-HABI` ("Habilitación de panadería La Espiga del Futuro"). El vecino tiene que traer el plano firmado. Lucía pasa el expediente a **Paralizado** con el motivo *"Se espera el plano firmado por el titular"*. En el Historial queda: *"Cambió el estado: de En trámite a Paralizado"*.

!!! info "Si otra persona cambió el estado mientras mirabas"
    Si el estado cambió desde que abriste la pantalla, el sistema no pisa el cambio: te avisa. Recargá el expediente y volvé a intentar.

### Cerrar el expediente

Para cerrar, el sector administrador elige **Cerrado** y completa 2 cosas. Las dos son obligatorias:

1. **Cómo terminó:**
    - **Resuelto**: el trámite llegó a su fin.
    - **Desistido por el interesado**: el vecino retiró el pedido.
    - **Caducado**: venció el plazo sin que el trámite avanzara.
    - **Denegado por silencio**: la administración no contestó en plazo y eso cuenta como rechazo.
    - **Fusionado con otro expediente**: el trámite sigue en otro expediente.
2. **Motivo**: por qué se cierra, en palabras.

**No se puede cerrar si queda algo abierto.** Antes hay que terminar o cancelar:

- las asignaciones abiertas;
- las tareas abiertas, también las tareas de comentario;
- los documentos en camino (por ejemplo, el documento de un pase que todavía se está generando).

Si queda algo de esto, el sistema no cierra y muestra cuáles son.

Al cerrar, el sistema genera el documento **"Cierre de Expediente"** (sigla `CIEX`). Lleva el número del expediente, la referencia, cómo terminó, el motivo, quién cerró y la fecha. Primero aparece en el Historial como "en proceso" y, cuando está listo, con su número. Queda en **Docs Oficiales**, como cualquier documento del expediente.

Siguiendo el ejemplo: sale el certificado de habilitación. Lucía cierra `EE-2026-000414-MUNDEV-HABI` como **Resuelto**, con el motivo *"Se emitió el certificado de habilitación"*. En el Historial queda *"Cerró el expediente (Resuelto)"* y se genera el `CIEX`.

### Qué pasa con un expediente cerrado

- **No admite nada:** ni pases, ni asignaciones, ni tareas, ni comentarios, ni documentos nuevos. La única excepción es **vincular un legajo**.
- **Sale de los listados** de todos los sectores y de Inicio. Ni el sector que lo administraba ni quienes trabajaron en él lo encuentran, tampoco por número.
- **Va al [Archivo](archivo.md).** Lo ven solo las personas que tienen el permiso **Archivo**. Desde ahí se puede leer y, si hace falta, reabrir.

Por ejemplo, Tomás, de Bromatología, hizo la inspección de la panadería. Con el expediente cerrado, Tomás ya no lo ve en sus listados. Si necesita consultarlo, se lo pide a alguien con permiso de Archivo.

---

## Quién ve el panel

Lo ve todo el que puede ver el expediente. El objetivo no se edita desde el expediente: solo se cambia en el BackOffice. El estado lo cambia solo el sector administrador; en un expediente cerrado, quien tiene el permiso Archivo.

---

## Preguntas frecuentes

??? question "¿Dónde quedó la pestaña Historial?"
    Es la misma, ahora se llama **Atributos e Historial**. La línea de tiempo y el chat de comentarios funcionan igual que antes.

??? question "La tarjeta dice "Sin objetivo". ¿Hice algo mal?"
    No. Ese tipo de expediente no tiene objetivo cargado. Si te sirve tenerlo, pedíselo al administrador de tu municipio.

??? question "Quiero cerrar y no me deja. ¿Por qué?"
    Puede faltar elegir cómo terminó o escribir el motivo. Si no, queda algo abierto: una asignación, una tarea o un documento que todavía se está generando. El sistema te muestra cuáles. Terminá o cancelá cada uno y volvé a intentar.

??? question "Cerré un expediente por error. ¿Cómo lo vuelvo atrás?"
    Pedile a alguien con permiso de Archivo que lo reabra. Ver [Reabrir un expediente](archivo.md#reabrir-un-expediente).

??? question "¿Paralizado y Suspendido frenan el expediente?"
    No. Indican por qué está quieto. Se sigue trabajando igual que En trámite.

??? question "¿El objetivo tiene valor legal?"
    No. Es una guía de trabajo. Lo oficial del expediente son sus documentos, en la pestaña **Documentos**.
