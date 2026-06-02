# Crear y editar legajo

Esta pagina explica como crear un legajo nuevo, completar sus campos, cambiar su estado y generar informes IFRLM.

---

## Crear un legajo nuevo

![Crear legajo](../capturas/legajo-crear.png)

### Paso 1: Seleccionar la familia de registro

Desde la pantalla principal de **Legajos**, hace click en el boton **"+ Crear"**. El sistema abre el formulario de nuevo legajo con un selector de familias de registro.

!!! tip "Solo ves las familias que tenes habilitadas"
    El selector muestra unicamente las familias activas en las que tenes permiso `can_create`. Si no aparece la familia que necesitas, contacta al administrador del sistema.

Selecciona la familia que corresponda al tipo de legajo que queres crear (ej: Arquitectura, Luminarias, Ordenanzas).

### Paso 2: Completar el nombre del legajo

El campo **Legajo** es el nombre identificatorio del legajo. Debe ser claro y descriptivo para que cualquier usuario entienda de que se trata.

!!! example "Ejemplos de nombres"
    - `Obra Av. San Martin 1250 - Gonzalez`
    - `Luminaria LED #4521 - Rotonda Belgrano`
    - `Ordenanza 3847/2025 - Uso de suelo zona norte`
    - `Habilitacion - Panaderia Don Carlos - Mitre 890`

### Paso 3: Completar los campos de la familia

Una vez seleccionada la familia, aparecen los campos especificos de esa familia. Los campos pueden ser de distintos tipos:

| Tipo de campo | Ejemplo |
|---------------|---------|
| Texto libre | Nombre del titular, observaciones |
| Numero | Superficie en m2, numero de medidor |
| Fecha | Fecha de habilitacion, fecha de vencimiento |
| Seleccion | Estado de la obra (en curso, finalizada, paralizada) |
| Archivo adjunto | Plano aprobado, foto del frente |

!!! warning "Campos obligatorios"
    Los campos marcados con asterisco (*) son obligatorios. El sistema valida que esten completos antes de crear el legajo. Si falta algun campo obligatorio, se muestra un mensaje indicando cuales faltan.

Al confirmar con **"Crear Legajo"**, el sistema asigna automaticamente el **numero oficial** con formato `RLM-{ANO}-{SEQ}-{TENANT}-{CODIGO}` y redirige al detalle del legajo recien creado.

---

![Detalle de legajo con datos y verificacion](../capturas/legajo-detalle-datos.png)

## Editar campos de un legajo

Para modificar los datos de un legajo existente:

1. Abri el legajo desde el listado
2. En la pestana **Datos**, hace click en el campo que queres modificar para editarlo directamente (edicion inline), o usa el boton de edicion global para modificar varios campos a la vez
3. Ingresa el nuevo valor
4. Guarda los cambios

!!! info "Campos verificados"
    Si un campo ya fue verificado por un verificador, al editarlo se pierde la verificacion y el campo vuelve a estado **pendiente de verificacion**. Ver [Verificacion](verificacion.md).

Todos los cambios quedan registrados en la pestana **Movimientos** del legajo con fecha, usuario y valor anterior.

---

## Cambiar el estado de un legajo

Desde la vista de detalle del legajo, hace click en el boton **"Acciones"** (arriba a la derecha) y selecciona **"Cambiar Estado"**.

Los estados disponibles dependen de la familia de registro. Podes cambiar de cualquier estado a cualquier otro sin restricciones. El sistema registra cada cambio en el historial con fecha, usuario y motivo.

!!! tip "Motivo del cambio"
    Al cambiar de estado podes agregar un motivo opcional. Es recomendable hacerlo para mantener la trazabilidad del legajo.

---

## Generar informe IFRLM

El **IFRLM (Informe de Registro Legajo Multiproposito)** es una foto del legajo en un momento determinado. Genera un documento oficial con todos los datos del legajo tal como estan al momento de emitirlo.

### Como generarlo

1. Abri el legajo del que queres emitir el informe
2. Hace click en **"Acciones"** (arriba a la derecha) y selecciona **"Generar Informe IFRLM"**
3. El sistema crea un documento tipo IFRLM con:
    - Todos los campos del legajo y sus valores actuales
    - Estado de verificacion de cada campo
    - Fecha y hora de emision
    - Numero oficial del informe

!!! tip "Usos tipicos del IFRLM"
    - Adjuntar a un expediente como constancia del estado actual de un registro
    - Responder un pedido de informe sobre una habilitacion vigente
    - Documentar el estado de una obra antes de una inspeccion

El informe generado queda disponible en la seccion **Documentos** y puede vincularse a expedientes como cualquier otro documento oficial.

!!! info "El IFRLM es un snapshot"
    El informe refleja los datos al momento de su emision. Si los datos del legajo cambian despues, el informe no se actualiza. Para obtener datos actualizados, genera un nuevo IFRLM.
