# Archivo

El **Archivo** es donde quedan los expedientes **cerrados**. Cuando el sector administrador cierra un expediente (ver [Cerrar el expediente](atributos.md#cerrar-el-expediente)), el expediente sale de los listados de todos los sectores y de Inicio, y pasa al Archivo.

No es una oficina ni un sector: el expediente no se mueve a ningún lado. El Archivo es una pantalla que junta todos los cerrados del municipio.

---

## Quién lo ve

Solo las personas que tienen el permiso **Archivo**. Lo da el administrador del municipio en el BackOffice, en la ficha del usuario (ver [Usuarios](../../administradores/usuarios.md#permisos-para-ver)).

- Con el permiso, ves en el menú la opción **Archivo** y encontrás **todos** los cerrados del municipio, de cualquier secretaría.
- Sin el permiso, no ves la opción en el menú y un expediente cerrado no aparece en ningún buscador, tampoco con el número exacto. Pasa lo mismo con el sector que lo administraba y con quienes trabajaron en él.

!!! warning "Expedientes reservados"
    Un expediente [reservado](reservados.md) cerrado lo ve solo quien tiene el permiso **Archivo** y además es **titular de la repartición que lo cerró**. Si cambia el titular, lo ve el nuevo. Tener el permiso sin ser titular no alcanza, y ser titular sin el permiso tampoco.

---

## Cómo buscar

La pantalla **Archivo** muestra una lista de los cerrados, con:

| Columna | Qué es |
|---------|--------|
| **Número** | El número del expediente |
| **Referencia** | El texto de la carátula |
| **Tipo** | El tipo de expediente |
| **Sector de origen** | El sector que lo administraba cuando se cerró |
| **Fecha de cierre** | Cuándo se cerró |

Podés buscar por **número** (también por una parte) o por **texto** de la referencia.

Por ejemplo, en la **Municipalidad del Futuro**, Lucía, de Mesa de Entradas, tiene el permiso Archivo. Escribe `000414` y encuentra `EE-2026-000414-MUNDEV-HABI`, "Habilitación de panadería La Espiga del Futuro", cerrado por Mesa de Entradas de Habilitaciones.

---

## Leer sin reabrir

Un expediente del Archivo se abre y se lee completo, sin reabrirlo:

- **Panel**, con los datos del expediente;
- **Docs Oficiales**, con todos sus documentos, incluido el "Cierre de Expediente" (`CIEX`);
- **Atributos e Historial**, con la línea de tiempo, los comentarios y los atributos.

**Tu Asistente** también funciona: le podés preguntar, por ejemplo, *"¿por qué se cerró este expediente?"* o *"¿qué dijo el informe de Bromatología?"*.

Todos los botones de acción están apagados. Lo único que se puede hacer es **reabrirlo** (y vincular un legajo).

---

## Reabrir un expediente

Lo reabre quien tiene el permiso **Archivo**, desde la tarjeta **Estado** del expediente.

1. Elegí **Reabrir**.
2. Elegí el **sector que lo recibe**. Puede ser el mismo que lo cerró u otro.
3. Escribí el **motivo**.

El expediente vuelve a **En trámite** en el sector que elegiste. Ese sector pasa a ser el administrador. Además, el sistema hace un **pase normal** al sector elegido, con su PV, igual que cualquier pase. En el Historial queda "Reabrió el expediente" y el pase.

Por ejemplo, el vecino de la panadería pide ampliar la habilitación. Lucía reabre `EE-2026-000414-MUNDEV-HABI` y lo manda a Bromatología con el motivo *"Pedido de ampliación del local"*. Tomás, de Bromatología, ve el expediente otra vez en su bandeja y puede seguir trabajando.

---

## Preguntas frecuentes

??? question "Trabajé en un expediente y ahora no lo encuentro. ¿Se borró?"
    No. Seguramente se cerró y está en el Archivo. Pedíselo a alguien con permiso de Archivo de tu municipio.

??? question "¿Puedo sacar un expediente del Archivo solo para mirarlo?"
    No hace falta. Con el permiso Archivo lo abrís y lo leés completo sin reabrirlo.

??? question "Soy titular de la repartición y no encuentro un reservado que cerramos."
    Para verlo necesitás las dos cosas: ser titular de esa repartición y tener el permiso Archivo. Pedile el permiso al administrador del municipio.
