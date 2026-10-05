# Expedientes y Documentos Reservados

Los **expedientes y documentos reservados** son items confidenciales cuya existencia y contenido solo son visibles para un conjunto acotado de personas. Sirven para tramites sensibles (sumarios, RRHH, legales, seguridad) que no deben aparecer en busquedas, listados ni en el asistente de IA para quien no tiene acceso.

!!! abstract "La idea en una frase"
    La reserva se marca **por TIPO** (no item por item), eligiendo la visibilidad **Reservado** en el tipo. Con eso, todas las puertas del sistema (interfaz, API REST, Gateway y MCP) aplican solas las mismas reglas de acceso, sin necesidad de dar permisos a mano.

---

## Que es un item reservado

La confidencialidad se define a nivel de **tipo**, no de cada expediente o documento individual:

| Donde se marca | Campo | Valores | Efecto |
|----------------|-------|---------|--------|
| Tipo de Documento (`document_types`) | `visibility` | Interno / Reservado / Publico | Con *Reservado*, todo documento de ese tipo nace reservado |
| Tipo de Expediente (`case_templates`) | `visibility` | Interno / Reservado | Con *Reservado*, todo expediente de ese tipo nace reservado |

Por debajo, el sistema deriva de `visibility` la marca de solo lectura `is_reserved` (`visibility = 'reservado'`), que es la que consultan todas las reglas de acceso.

La ventaja de hacerlo por tipo: cero tablas nuevas de permisos y cero pantallas para dar acceso manual. Las reglas son fijas y viven en la visibilidad del tipo.

!!! warning "La reserva es irreversible y solo se activa en tipos virgenes"
    - Marcar un tipo como reservado **solo se permite si el tipo no tiene ningun item creado** (0 expedientes o 0 documentos). Un tipo con items ya usados no se puede pasar a reservado.
    - Una vez marcado como reservado, **no se puede volver a Interno** (es irreversible).

    Esto garantiza que nunca exista un item que haya sido publico antes y luego se oculte (o al reves), y elimina cualquier ambiguedad historica.

Quien puede marcarlo: el mismo administrador del BackOffice que edita hoy los tipos de documento y expediente. La opcion **Reservado** aparece en el selector de visibilidad del ABM de **Tipos de Documentos** y **Tipos de Expedientes**, con la descripcion *"Confidencial e irreversible"*. En la practica se elige al dar de alta el tipo.

---

## Quien puede ver un expediente reservado

Para un expediente reservado, el modelo de acceso habitual por sector **no aplica**: pertenecer al sector administrador o a un sector asignado ya **no alcanza** para verlo. En terminos de negocio lo ven solo **el titular de la reparticion y los responsables del expediente**. Tecnicamente son cuatro condiciones (modelo R1 / R2 / R3 / R4), porque hay dos formas de ser responsable y dos de ser titular:

| Rama | Quien | Detalle |
|------|-------|---------|
| **R1** | Responsables del expediente | Usuarios cargados en la lista de responsables del expediente (titular o adicionales) que esten activos |
| **R2** | Titular de la reparticion administradora | El titular **directo** de la reparticion del **sector administrador actual** del expediente |
| **R3** | Titular de cada reparticion asignada | El titular **directo** de la reparticion de **cada sector asignado activo** del expediente |
| **R4** | Responsables de una actuacion | Usuarios designados responsables de una actuacion o tarea del expediente (actuantes). Es la otra forma de ser responsable del expediente: vale mientras la actuacion este abierta; al cerrarse, el acceso por esta via se pierde (salvo que la persona siga cumpliendo R1, R2 o R3) |

!!! note "R1 y R4 son el mismo concepto"
    El **responsable directo** (R1) y el **designado en una actuacion** (R4) son lo mismo para el negocio: personas responsables del expediente. La diferencia es solo la vigencia: el alta directa dura hasta que se la quite, la de la actuacion dura mientras la actuacion siga abierta.

!!! note "Solo la reparticion directa"
    R2 y R3 se refieren al titular de la reparticion **directa** del sector, nunca al titular de una reparticion padre ni al Intendente. Si un sector no tiene titular cargado, esa via simplemente no aporta ningun visor: en ese caso, la unica forma de acceder es figurar como responsable (R1).

!!! danger "Nadie hace bypass"
    Ni el permiso de **busqueda global** de expedientes, ni pertenecer al sector, ni un super-rol, ni haber creado el expediente abren un expediente reservado fuera del modelo R1/R2/R3/R4. Para quien no cumple ninguna rama, el expediente no aparece en listados, contadores, busquedas ni tareas del Inicio, y abrirlo da *no encontrado*. Tampoco puede operarlo (pasar, asignar, archivar, vincular documentos ni subsanar). La unica excepcion es la busqueda por numero exacto para proponer un documento, que **no** abre el expediente (ver [Busqueda por numero](#busqueda-por-numero)).

### El creador y su propio expediente

El creador de un expediente **no tiene acceso por el solo hecho de haberlo creado**. Para que no quede afuera de su propio tramite al nacer, al crear un expediente reservado el sistema lo **auto-agrega como responsable**.

!!! question "Responsable de que, exactamente"
    Al crear un expediente reservado, el creador queda dado de alta automaticamente como **responsable ADMIN del expediente, en el Sector Administrador** del expediente. Es decir, responsable/actuante del propio expediente (la misma lista de responsables que usa R1), no de un documento ni de otra cosa. Ese alta es **removible** despues (por ejemplo con "sacarme como responsable"): si se lo quita, deja de verlo, salvo que acceda por otra via (R2/R3/R4).

    Si el expediente lo crea un **ciudadano** desde TAD, no se lo da de alta como responsable: el ciudadano lo ve porque el expediente se comparte automaticamente con el.

---

## Quien puede ver un documento reservado

Un documento de tipo reservado es visible unicamente para:

- **Firmantes** del documento (cualquier firma, pendiente o ya firmada).
- **El creador del borrador**, mientras lo redacta (para poder editarlo y mandarlo a firmar aunque todavia no tenga firmantes ni este vinculado a un expediente).
- Quien puede ver el **expediente reservado que lo contiene** (herencia): si sos responsable/titular del expediente reservado, ves los documentos reservados de adentro.

Las vias que **no** abren un documento reservado: el permiso de busqueda global de documentos, la coincidencia de sector, y el vinculo por legajo.

---

## Regla 1: integridad al vincular

Un documento reservado **solo puede vivir dentro de un expediente reservado**. Esta regla se valida al vincular o proponer un documento a un expediente, de modo que nunca exista un documento reservado dentro de un expediente publico.

| Documento | Expediente | Resultado |
|-----------|-----------|-----------|
| Normal | Normal | Permitido |
| Normal | Reservado | **Permitido** |
| Reservado | Reservado | Permitido |
| Reservado | Normal | **Rechazado** |

!!! question "Un expediente reservado, puede recibir documentos normales?"
    **Si.** Un expediente reservado puede contener documentos NO reservados sin problema. El contenedor reservado limita su propio acceso; el documento publico que adentro no es secreto y se rige por sus propias reglas de visibilidad.

!!! question "Un documento reservado, puede ir a un expediente normal?"
    **No.** Vincular o proponer un documento reservado a un expediente NO reservado se rechaza. Asi se evita de raiz que un item confidencial termine dentro de un contenedor publico.

---

## Regla 2: fuera de todo lo que expone contenido

El contenido de un documento reservado queda afuera de todos los procesos de IA y busqueda de contenido, **para todos los usuarios, incluidos sus firmantes** (sus firmantes lo abren normalmente, pero la IA nunca lo procesa):

- **No** se le genera resumen de IA.
- **No** se indexa su contenido para la busqueda inteligente por significado.
- **No** se transcribe su PDF (en documentos importados, su contenido nunca se procesa por IA).
- **No** aparece en busquedas por contenido ni por similitud.

Ademas, un documento reservado **nunca aporta datos** (numero, referencia, tipo) al resumen de IA de un expediente ni de un legajo.

El **asistente de IA (chat)** no cita ni menciona el contenido de un documento reservado.

!!! warning "Los expedientes reservados NO tienen resumen de IA"
    El resumen automatico de IA **no se genera** para ningun expediente de tipo reservado, aunque adentro tenga documentos no reservados. La busqueda inteligente solo muestra un expediente reservado a quien cumple R1/R2/R3/R4.

---

## Paridad de puertas

El mismo dato se expone por tres puertas: la **interfaz / API REST**, el **Gateway** y el **MCP** (asistente de IA). Las tres aplican exactamente los mismos permisos.

!!! tip "Regla de oro"
    Si un item reservado no se ve por la interfaz, **tampoco se ve por MCP ni por el Gateway**. Ninguna puerta es mas permisiva que otra para el mismo dato.

---

## Busqueda por numero

Un expediente o documento reservado al que no tenes acceso **no aparece** en la busqueda global, en los listados ni en los buscadores por texto. Se comporta igual que cualquier otra puerta: si no tenes acceso (segun R1/R2/R3/R4 para expedientes, o firmante/creador/herencia para documentos), no aparece.

!!! info "Excepcion: el numero exacto de un expediente reservado, para proponerle un documento"
    Quien escribe el **numero exacto y completo** de un expediente reservado al vincular un documento recibe un resultado **minimo**: solo el numero, con el candado y la leyenda *"Expediente reservado"*. **No** se muestra la referencia, el tipo, los sectores ni las fechas. Sirve para poder **proponerle** un documento al expediente; la propuesta la acepta o la rechaza alguien con acceso.

    Tener el numero revela que el expediente **existe**, no su **contenido**: abrir el expediente sigue respondiendo *no encontrado*. Aplica solo a expedientes; un documento reservado no se encuentra por su numero si no tenes acceso.

!!! note "Ver el numero no es el problema"
    El principio del modelo es que lo que hay que proteger es el **ingreso** y el **contenido** del item reservado. Que el numero de un expediente pueda figurar como dato lateral en otro contexto (por ejemplo, en la ficha de un documento vinculado que si podes ver) no se considera una fuga: lo que nunca debe pasar es que alguien sin acceso pueda **entrar** al expediente o **leer su contenido**.

---

## Aviso de responsable

Cuando a alguien lo nombran responsable de un expediente reservado, el aviso del **Inicio** ("Te nombraron responsable") muestra el numero y la referencia del expediente, **aunque despues lo hayan quitado** como responsable. Es intencional: si se ocultara, la persona nunca se enteraria de que la nombraron. Al intentar abrirlo sin acceso, el sistema lo rechaza.

---

!!! example "Estado de la funcionalidad"
    El comportamiento descripto en esta pagina esta **en produccion** y fue verificado contra el codigo en octubre de 2026. La version para usuarios finales esta en [Expedientes reservados](../usuarios/expedientes/reservados.md).
