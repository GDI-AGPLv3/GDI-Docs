# Expedientes y Documentos Reservados

Algunos trámites son confidenciales: sumarios, recursos humanos, asuntos legales o de seguridad. Para esos casos el municipio usa **tipos reservados**. Un expediente o documento de un tipo reservado lo ve **solo un grupo chico de personas**; para el resto del municipio, no existe.

!!! abstract "En una frase"
    Lo reservado se define por **tipo** (lo configura el administrador del municipio). Si el tipo es reservado, todo expediente o documento de ese tipo nace reservado, y nadie tiene que dar permisos a mano.

---

## Cómo reconocerlo

Los expedientes y documentos reservados se marcan con un **candado** :material-lock: al lado del título o del tipo. Al pasar el mouse por encima aparece la leyenda *"Expediente reservado"* o *"Documento reservado"*.

---

## Quién ve un expediente reservado

En un expediente reservado **no alcanza con ser del sector**. Lo ven solamente:

| Quién | Cuándo |
|-------|--------|
| **Los responsables del expediente** | Mientras figuren como responsables |
| **El titular de la repartición que lo administra** | El titular directo de la repartición del sector que tiene el expediente hoy |
| **El titular de cada repartición asignada** | El titular directo de la repartición de cada sector al que se le asignó el expediente |
| **Quien tiene una actuación abierta** | Mientras la actuación asignada a esa persona siga abierta |

!!! note "Qué NO da acceso"
    - Ser del mismo sector o de un sector asignado (salvo que seas el titular de la repartición).
    - Tener permiso de búsqueda global.
    - Haber creado el expediente, por sí solo (ver abajo).
    - Ser titular de una repartición superior o Intendente.

### Si lo creaste vos

Al crear un expediente reservado, el sistema te agrega **automáticamente como responsable**, así no quedás afuera de tu propio trámite. Si después te sacan como responsable (o te sacás vos), **dejás de verlo**, salvo que tengas acceso por otra vía de la tabla.

---

## Quién ve un documento reservado

Un documento de tipo reservado lo ven solamente:

- **Quienes lo firman** (con la firma pendiente o ya hecha).
- **Quien creó el borrador**, mientras lo redacta.
- **Quien puede ver el expediente reservado** al que está vinculado.

Ser del sector que lo firmó o tener permiso de búsqueda global **no alcanza**.

---

## Qué pasa si no tenés acceso

- El expediente o documento **no aparece** en tus listados, contadores, búsquedas ni tareas del Inicio.
- Si abrís un enlace directo, el sistema responde que **no se encontró**.
- No podés operarlo: ni pasarlo, ni asignarlo, ni archivarlo, ni vincularle documentos.

!!! info "Si tenés el número exacto de un expediente reservado"
    Al **vincular un documento a un expediente**, si escribís el número **exacto y completo** de un expediente reservado, aparece como resultado **solo el número**, con el candado y la leyenda *"Expediente reservado"*: sin referencia ni ningún otro dato. Sirve para **proponerle** tu documento; la propuesta la acepta o la rechaza alguien que sí tiene acceso. Igual no vas a poder abrir el expediente.

!!! info "El aviso de 'Te nombraron responsable'"
    Si te nombraron responsable de un expediente reservado, el aviso queda en tu **Inicio** con el número y la referencia, **aunque después te hayan sacado**. Así te enterás de que te nombraron. Si ya no tenés acceso, al intentar abrirlo el sistema no te deja.

---

## Reglas al vincular documentos

| Documento | Expediente | ¿Se puede? |
|-----------|-----------|:----------:|
| Normal | Normal | ✅ |
| Normal | Reservado | ✅ |
| Reservado | Reservado | ✅ |
| Reservado | Normal | ❌ |

Un documento reservado **solo puede ir dentro de un expediente reservado**. Por eso, al vincular documentos en un expediente que **no** es reservado, los documentos reservados directamente no aparecen en el buscador (ver [Vincular Documentos](vincular-documentos.md)).

---

## Reservados e inteligencia artificial

- Los documentos reservados **no se procesan con IA**: no tienen resumen, no se transcriben y no aparecen en la búsqueda inteligente. Esto vale para todos, incluso para quienes los firman.
- Los expedientes reservados **no tienen resumen de IA**.
- El asistente de IA nunca cita ni menciona el contenido de un documento reservado.

---

## Preguntas frecuentes

??? question "¿Por qué no veo un expediente que es de mi sector?"
    Probablemente es de un **tipo reservado**. En los reservados, ser del sector no alcanza: solo lo ven los responsables, los titulares de las reparticiones involucradas y quien tiene una actuación abierta. Si necesitás verlo, pedile a alguien con acceso que te agregue como responsable o te asigne una actuación.

??? question "¿Puedo convertir un expediente común en reservado (o al revés)?"
    No. Lo reservado depende del **tipo** de expediente o documento y se elige al crearlo. Un expediente ya creado no cambia de tipo.

??? question "Me sacaron como responsable y ya no puedo abrir el expediente. ¿Es un error?"
    No. En un expediente reservado, el acceso dura mientras seas responsable (o tengas otra vía de acceso). Al sacarte, dejás de verlo.

??? question "No puedo vincular un documento a un expediente. ¿Por qué?"
    Si el documento es **reservado** y el expediente **no**, el sistema no lo permite: un documento confidencial no puede quedar dentro de un expediente común.

!!! tip "Para administradores"
    El detalle técnico (cómo se configura un tipo reservado y las reglas completas) está en [Expedientes y Documentos Reservados — Administradores](../../administradores/reservados.md).
