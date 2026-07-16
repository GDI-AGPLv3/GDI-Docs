# Expedientes y Documentos Reservados

Los **expedientes y documentos reservados** son items confidenciales cuya existencia y contenido solo son visibles para un conjunto acotado de personas. Sirven para tramites sensibles (sumarios, RRHH, legales, seguridad) que no deben aparecer en busquedas, listados ni en el asistente de IA para quien no tiene acceso.

!!! abstract "La idea en una frase"
    La reserva se marca **por TIPO** (no item por item) con un flag `is_reserved`. Con ese flag activado, todas las puertas del sistema (interfaz, API REST, Gateway y MCP) aplican solas las mismas reglas de acceso, sin necesidad de dar permisos a mano.

---

## Que es un item reservado

La confidencialidad se define a nivel de **tipo**, no de cada expediente o documento individual:

| Donde se marca | Campo | Efecto |
|----------------|-------|--------|
| Tipo de Documento (`document_types`) | `is_reserved` | Todo documento de ese tipo nace reservado |
| Tipo de Expediente (`case_templates`) | `is_reserved` | Todo expediente de ese tipo nace reservado |

La ventaja de hacerlo por tipo: cero tablas nuevas de permisos y cero pantallas para dar acceso manual. Las reglas son fijas y viven en el flag del tipo.

!!! warning "El flag es irreversible y solo se activa en tipos virgenes"
    - Marcar un tipo como reservado **solo se permite si el tipo no tiene ningun item creado** (0 expedientes o 0 documentos). Un tipo con items ya usados no se puede pasar a reservado.
    - Una vez marcado como reservado, el flag **no se puede desactivar** (es irreversible).

    Esto garantiza que nunca exista un item que haya sido publico antes y luego se oculte (o al reves), y elimina cualquier ambiguedad historica.

Quien puede activar el flag: el mismo administrador del BackOffice que edita hoy los tipos de documento y expediente. El toggle "Reservado" aparece en el ABM de **Tipos de Documentos** y **Tipos de Expedientes**, con un aviso de que el cambio es inmediato e irreversible.

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
    Ni el permiso de **busqueda global** de expedientes, ni un super-rol, ni la busqueda por numero exacto abren un expediente reservado fuera del modelo R1/R2/R3/R4. No hay excepciones.

### El creador y su propio expediente

El creador de un expediente **no tiene acceso por el solo hecho de haberlo creado**. Para que no quede afuera de su propio tramite al nacer, al crear un expediente reservado el sistema lo **auto-agrega como responsable**.

!!! question "Responsable de que, exactamente"
    Al crear un expediente reservado, el creador queda dado de alta automaticamente como **responsable del expediente de tipo ADDITIONAL, en el Sector Administrador** del expediente. Es decir, responsable/actuante del propio expediente (la misma lista de responsables que usa R1), no de un documento ni de otra cosa. Ese alta es **removible** despues: si se lo quita, deja de verlo, salvo que acceda por otra via (R1/R2/R3).

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

El contenido de un documento reservado queda afuera de todos los procesos de IA y busqueda de contenido, **salvo para sus firmantes**:

- **No** se le genera resumen de IA.
- **No** se indexa su contenido para la busqueda inteligente por significado.
- **No** se transcribe su PDF (en documentos importados, su contenido nunca se procesa por IA).
- **No** aparece en busquedas por contenido ni por similitud.

El **asistente de IA (chat)** no cita ni menciona el contenido de un documento reservado a quien no tiene acceso a el.

!!! info "Los expedientes reservados si tienen resumen"
    Un expediente reservado que contiene documentos NO reservados **si obtiene su resumen de IA**, armado a partir de esos documentos no reservados. La reserva bloquea el contenido de los documentos reservados, no impide que el expediente tenga su resumen.

---

## Paridad de puertas

El mismo dato se expone por tres puertas: la **interfaz / API REST**, el **Gateway** y el **MCP** (asistente de IA). Las tres aplican exactamente los mismos permisos.

!!! tip "Regla de oro"
    Si un item reservado no se ve por la interfaz, **tampoco se ve por MCP ni por el Gateway**. Ninguna puerta es mas permisiva que otra para el mismo dato.

---

## Busqueda por numero

Un expediente o documento reservado al que no tenes acceso **nunca aparece por busqueda exacta de numero**, ni por la busqueda global, ni tildandolo en ningun buscador. Se comporta igual que cualquier otra puerta: si no tenes acceso (segun R1/R2/R3/R4 para expedientes, o firmante/creador/herencia para documentos), no aparece. Punto.

!!! note "Ver el numero no es el problema"
    El principio del modelo es que lo que hay que proteger es el **ingreso** y el **contenido** del item reservado. Que el numero de un expediente pueda figurar como dato lateral en otro contexto (por ejemplo, en la ficha de un documento vinculado que si podes ver) no se considera una fuga: lo que nunca debe pasar es que alguien sin acceso pueda **entrar** al expediente o **leer su contenido**.

---

!!! example "Estado de la funcionalidad"
    El comportamiento descripto en esta pagina corresponde al **modelo disenado** de expedientes y documentos reservados. La implementacion se esta verificando en el ambiente de desarrollo (DEV) durante julio de 2026. Si detectas una diferencia entre lo documentado aca y lo que ves en la aplicacion, prevalece este modelo como comportamiento esperado.
