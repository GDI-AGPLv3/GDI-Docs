# Organigrama

Crea nuevos sectores y asigna usuarios a tus espacios de trabajo. El organigrama define la estructura organizativa de la organizacion: reparticiones (departamentos) y sectores.

---

## Diseño general

La pantalla tiene tres zonas principales:

| Zona | Descripcion |
|------|-------------|
| **Panel izquierdo** | Arbol de reparticiones (colapsable y redimensionable) |
| **Panel central** | Detalle de la reparticion seleccionada: header con responsable, stats, sub-reparticiones y sectores |
| **Modales centrados** | Crear reparticion, crear sector, detalle de sector y detalle de reparticion se abren como dialogos modales (ya no como panel lateral deslizable) |

El panel izquierdo se puede colapsar con el boton lateral y redimensionar arrastrando el borde.

---

## Arbol de Reparticiones

El panel izquierdo muestra todas las reparticiones de la organizacion en formato jerarquico. Cada reparticion tiene un **color** identificatorio y puede contener sub-reparticiones anidadas.

Al seleccionar una reparticion, el panel central se actualiza con su detalle.

---

## Header de Reparticion

Al seleccionar una reparticion, el panel central muestra en el encabezado:

- **Color** de la reparticion (barra de color superior)
- **Nombre** y **acronimo** de la reparticion
- **Responsable** de la reparticion (si esta asignado). Hacer clic abre un modal para asignar, cambiar o quitar el responsable
- Boton **Editar** para abrir el modal de detalle/edicion de la reparticion

### Responsable

Cada reparticion puede tener un responsable (titular del departamento). El boton de responsable en el header permite:

| Accion | Descripcion |
|--------|-------------|
| **Asignar responsable** | Buscar y seleccionar un usuario activo. Al asignarlo, se lo mueve automaticamente al sector PRIV del departamento y se le asigna el sello del rango del departamento |
| **Cambiar responsable** | Si ya hay un responsable asignado, se puede reemplazar. El sistema pide confirmacion antes de hacer el cambio |
| **Quitar responsable** | Quita al responsable actual. El departamento queda sin titular asignado |

---

## Estadisticas de la Reparticion

Debajo del header se muestran cuatro estadisticas de la reparticion seleccionada:

| Estadistica | Descripcion |
|-------------|-------------|
| **Empleados** | Cantidad total de usuarios asignados |
| **Sub-reparticiones** | Cantidad de reparticiones hijas |
| **Sectores** | Cantidad de sectores dentro de la reparticion |
| **Tipos de exp.** | Cantidad de tipos de expediente habilitados para la reparticion |

---

## Sub-reparticiones y Sectores

Debajo de las estadisticas aparecen las sub-reparticiones como tarjetas clicables (cada una muestra su color, acronimo, nombre y cantidad de empleados). Hacer clic en una sub-reparticion la selecciona en el arbol y actualiza el panel central.

Al final de las tarjetas hay un boton **+ Agregar sub-reparticion** para crear una reparticion hija de la seleccionada.

La lista de **sectores** aparece debajo, con un boton **+ Crear sector**.

### Detalle de Sector

Al hacer clic en el icono de configuracion de un sector se abre un modal con:

| Dato | Descripcion |
|------|-------------|
| **Acronimo** | Sigla del sector. Editable (excepto en el sector PRIV, que es de sistema) |
| **Color del sector** | Selector de color con paleta predefinida |
| **Usuarios asignados** | Cantidad de usuarios en el sector |

!!! info "Sector PRIV"
    El sector **PRIV** es el sector de sistema que se crea automaticamente al crear una reparticion. Solo se puede cambiar su color; el acronimo esta fijo.

---

## Crear Reparticion

El boton **+ Anadir reparticion** (en el header de la pagina o dentro de sub-reparticiones) abre un modal:

| Campo | Obligatorio | Descripcion |
|-------|:-----------:|-------------|
| **Reparticion padre** | Si | Reparticion a la que pertenece |
| **Rango** | No | Rango jerarquico del responsable |
| **Nombre** | Si | Nombre completo (2-100 caracteres) |
| **Acronimo** | Si | Solo letras y numeros, max 20 caracteres, unico |

Al crear la reparticion, el sistema genera automaticamente un sector **PRIV** para ella.

---

## Crear Sector

El boton **+ Crear Sector** abre un modal:

| Campo | Obligatorio | Descripcion |
|-------|:-----------:|-------------|
| **Reparticion** | Si | Reparticion a la que pertenece (pre-seleccionada si se usa el boton de la reparticion activa) |
| **Acronimo** | Si | Solo letras y numeros, max 10 caracteres, unico dentro de la reparticion |
| **Color** | No | Color identificatorio con paleta predefinida |

---

## Auditoria

El boton **Auditoria** en el header de la pagina abre una vista a pantalla completa con el historial de cambios del organigrama.

Muestra una bitacora de todas las operaciones registradas automaticamente sobre reparticiones y sectores:

| Columna | Descripcion |
|---------|-------------|
| **Operacion** | Tipo de cambio: `Creo`, `Edito` o `Elimino` |
| **Entidad** | Objeto afectado: Reparticion o Sector |
| **Quien** | Usuario que realizo el cambio |
| **Cuando** | Fecha y hora de la operacion |
| **Detalle** | Campos modificados con valores anterior y nuevo |

Se puede filtrar por tipo de entidad (Reparticiones, Sectores) y buscar por texto. La auditoria se actualiza en tiempo real.

---

## Color de Departamento

Al editar el detalle de una reparticion se puede modificar su **color primario**. El color se aplica a la barra superior del header y al avatar de la reparticion. Tambien se puede ajustar el color individual de cada sector hijo desde el mismo panel.
