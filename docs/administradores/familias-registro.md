# Familias de Registro (RLM)

Gestiona las familias de registro del sistema. Las familias son plantillas que definen la estructura de los legajos: que campos tiene cada tipo de legajo, que sectores pueden operar con el, y que estados puede atravesar.

---

## Que es una Familia de Registro

Una familia de registro es una **plantilla reutilizable** que define como se estructura un tipo de legajo. Pensala como un formulario modelo: establece que datos se cargan, quien puede acceder y que ciclo de vida sigue el legajo.

!!! example "Ejemplo practico"
    La familia **ARQ** (Arquitectura) podria definir que cada legajo de obra debe tener: nombre del titular, numero de plano, fecha de presentacion, superficie en m2, y un campo de observaciones. Solo los sectores de Obras Privadas y Catastro pueden crear y ver estos legajos.

Cada familia tiene un **codigo unico** de entre 3 y 8 caracteres (ej: `ARQ`, `LUM`, `ORD`, `HABCOM`) que la identifica en todo el sistema.

---

## Familias Globales vs Personalizadas

El sistema maneja dos tipos de familias:

| Tipo | Descripcion |
|------|-------------|
| **Global** | Viene del catalogo global de GDI. Disponible para todas las organizaciones. No se puede modificar su estructura base |
| **Personalizada** | Creada por la organizacion para necesidades especificas del municipio. Totalmente configurable |

!!! info "Catalogo global"
    Las familias globales son mantenidas por GDI Latam y representan los tipos de legajo mas comunes en la gestion municipal. Tu organizacion puede habilitarlas desde el catalogo y ajustar los permisos por sector.

---

## Listado de Familias

La tabla muestra todas las familias habilitadas para la organizacion.

| Columna | Descripcion |
|---------|-------------|
| **Codigo** | Codigo unico de la familia (3-8 caracteres, ej: `ARQ`, `LUM`) |
| **Nombre** | Nombre descriptivo de la familia |
| **Campos** | Cantidad de campos configurados en el esquema de datos |
| **Sectores** | Cantidad de sectores con permisos asignados |
| **Estado** | `Activo` o `Inactivo` |

### Acciones del listado

| Accion | Descripcion |
|--------|-------------|
| **+ Nueva Familia** | Crear una familia personalizada |
| **+ Catalogo Global** | Habilitar una familia del catalogo global |

---

## Crear una Familia

Al presionar **+ Nueva Familia** se abre el formulario de creacion.

### Campos del formulario

| Campo | Descripcion |
|-------|-------------|
| **Codigo** | Codigo unico de 3 a 8 caracteres. Solo letras mayusculas y numeros. No se puede cambiar despues de creado |
| **Nombre** | Nombre descriptivo de la familia (ej: *Legajo de Obra Privada*) |
| **Descripcion** | Texto opcional que explica el uso de la familia |

!!! warning "El codigo es permanente"
    Una vez creada la familia, el codigo no se puede modificar. Elegi un codigo claro y representativo. Ejemplos: `ARQ` para Arquitectura, `LUM` para Luminarias, `ORD` para Ordenanzas, `HABCOM` para Habilitaciones Comerciales.

---

## Configurar Campos (Data Schema)

Cada familia define un esquema de datos: los campos que va a tener cada legajo creado con esa familia. Podes agregar, editar, reordenar y eliminar campos.

### Agregar un campo

Al agregar un campo, se configuran las siguientes propiedades:

| Propiedad | Descripcion |
|-----------|-------------|
| **Nombre** | Nombre del campo tal como lo ve el usuario (ej: *Nombre del titular*, *Superficie m2*) |
| **Tipo** | Tipo de dato del campo (ver tabla de tipos) |
| **Obligatorio** | Si el campo es requerido al crear o editar el legajo |
| **Vencimiento** | Si el campo tiene fecha de vencimiento asociada (aplica para campos tipo `date`) |
| **Verificacion** | Si el campo requiere verificacion por un usuario autorizado |

### Tipos de campo disponibles

| Tipo | Descripcion | Ejemplo de uso |
|------|-------------|----------------|
| **text** | Texto corto, una linea | Nombre del titular, Numero de plano |
| **number** | Valor numerico | Superficie en m2, Cantidad de pisos |
| **date** | Fecha con selector de calendario | Fecha de presentacion, Fecha de vencimiento |
| **textarea** | Texto largo, multiples lineas | Observaciones, Descripcion de la obra |
| **select** | Lista desplegable con opciones predefinidas | Estado de la obra (En curso, Finalizada, Paralizada) |
| **boolean** | Casilla de verificacion (si/no) | Tiene plano aprobado, Requiere inspeccion |

!!! tip "Campos con vencimiento"
    Cuando marcas un campo como "con vencimiento", el sistema va a alertar automaticamente cuando la fecha cargada en ese campo este proxima a vencer o ya haya vencido. Esto es util para habilitaciones, certificados o permisos temporales.

!!! info "Campos con verificacion"
    Un campo marcado como "requiere verificacion" necesita que un usuario con permiso `can_verify` en ese sector lo valide. Hasta que no se verifique, el campo queda marcado como pendiente.

---

## Permisos por Sector

Cada familia define que sectores pueden operar con sus legajos y con que nivel de acceso. El sistema de permisos se basa en un sector "dueno" y sectores adicionales con permisos parciales.

### Sector dueno

Al crear una familia, se asigna un **sector dueno**. Este sector tiene automaticamente **todos los permisos** sobre los legajos de esa familia.

### Sectores adicionales

Ademas del sector dueno, se pueden agregar otros sectores con permisos especificos. Cada sector adicional recibe una combinacion de los siguientes permisos:

| Permiso | Descripcion |
|---------|-------------|
| **can_create** | Puede crear nuevos legajos de esta familia |
| **can_edit** | Puede editar los datos de legajos existentes |
| **can_view** | Puede ver y consultar los legajos |
| **can_verify** | Puede verificar campos que requieren verificacion |

!!! example "Ejemplo de configuracion de permisos"
    Para la familia **ARQ** (Arquitectura):

    | Sector | can_create | can_edit | can_view | can_verify |
    |--------|:----------:|:--------:|:--------:|:----------:|
    | **Obras Privadas** (dueno) | Si | Si | Si | Si |
    | Catastro | No | No | Si | Si |
    | Mesa de Entradas | Si | No | Si | No |
    | Intendencia | No | No | Si | No |

    En este ejemplo, Obras Privadas tiene control total. Mesa de Entradas puede crear legajos nuevos y verlos, pero no editarlos ni verificar campos. Catastro puede ver y verificar. Intendencia solo puede consultar.

!!! warning "Sector dueno vs adicionales"
    El sector dueno **siempre** tiene todos los permisos (`can_create`, `can_edit`, `can_view`, `can_verify`). No se le pueden quitar permisos individuales. Si necesitas que un sector tenga permisos parciales, agregalo como sector adicional, no como dueno.

---

## Estados Configurables

Cada familia puede definir sus propios **estados** que representan el ciclo de vida de un legajo. Los estados son personalizables por familia.

!!! example "Ejemplo de estados"
    La familia **HABCOM** (Habilitaciones Comerciales) podria tener los siguientes estados:

    - Ingresado
    - En revision
    - Observado
    - Aprobado
    - Rechazado
    - Vencido

Los estados permiten hacer seguimiento del progreso de cada legajo y filtrar legajos por su situacion actual.

---

## Resumen de configuracion

Para dejar una familia lista para usar, segui estos pasos:

1. **Crear la familia** con codigo, nombre y descripcion
2. **Definir los campos** del esquema de datos (tipos, obligatoriedad, vencimiento, verificacion)
3. **Asignar el sector dueno** que tendra control total
4. **Agregar sectores adicionales** con sus permisos especificos
5. **Configurar los estados** del ciclo de vida del legajo
