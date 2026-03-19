# Gestion de Usuarios

Administra los usuarios del sistema: crear, editar, asignar sectores, roles, sellos y permisos.

![Gestion de Usuarios](capturas/gestion-usuarios.png)

---

## Listado de Usuarios

La tabla muestra todos los usuarios de la organizacion con paginacion.

| Columna | Descripcion |
|---------|-------------|
| **Usuario** | Avatar con inicial, nombre completo y email |
| **Sector / Depto** | Sector principal y departamento al que pertenece |
| **Roles** | Rol asignado: `Funcionario`, `Administrador` |
| **Estado** | `Activo` o `Inactivo` |
| **Ultimo Acceso** | Fecha del ultimo login (*Nunca* si no ha ingresado) |

### Acciones del listado

| Accion | Descripcion |
|--------|-------------|
| **Buscar** | Filtrar por nombre o email |
| **Creacion Masiva** | Crear multiples usuarios a la vez |
| **Nuevo Usuario** | Crear un usuario individual |

---

## Crear Usuario

Al presionar **Nuevo Usuario** se abre el formulario de creacion.

### Campos del formulario

| Campo | Descripcion |
|-------|-------------|
| **Email** | Correo electronico del usuario (ej: `usuario@municipio.gob.ar`) |
| **Nombre completo** | Nombre y apellido |
| **Metodo de acceso** | Como va a iniciar sesion el usuario (ver abajo) |
| **Sector** | Sector principal al que se asigna |

### Metodo de acceso

Al crear un usuario se elige como va a iniciar sesion:

| Metodo | Descripcion |
|--------|-------------|
| **Login Social (Google / Microsoft)** | El usuario ingresa con su cuenta de Google o Microsoft. Ideal para emails institucionales con Google Workspace o Microsoft 365. Es la opcion por defecto |
| **Email y Contrasena** | El usuario recibe un email con un link de activacion para crear su contrasena. El link vence en 5 dias. Usar para emails que no son Google ni Microsoft |

!!! tip "Cuando usar cada metodo"
    - **Login Social**: Para la mayoria de los casos. Si el email es de Google (`@gmail.com`, dominios con Google Workspace) o Microsoft (`@outlook.com`, dominios con Microsoft 365), elegir esta opcion.
    - **Email y Contrasena**: Para dominios que no usan Google ni Microsoft como proveedor de email (ej: servidores de correo propios del municipio).

---

## Detalle de Usuario

Al hacer clic en un usuario se muestra su ficha completa:

![Detalle de Usuario](capturas/detalle-usuario.png)

### Informacion

| Campo | Descripcion |
|-------|-------------|
| **Nombre completo** | Nombre y apellido del usuario |
| **Email** | Correo electronico institucional |
| **Metodo de acceso** | Como inicia sesion: `Email y Contrasena`, `Google`, `Microsoft` o `Pendiente activacion` si todavia no activo su cuenta |
| **Sector** | Sector principal asignado (ej: *Tesoreria # PRIV*) |
| **Numero de Identificacion Nacional (ID)** | Documento de identidad del usuario (si fue cargado) |

### Responsable de Departamento

Si el usuario es titular de un departamento, se muestra aqui.

| Campo | Descripcion |
|-------|-------------|
| **Titular** | Indica que el usuario es responsable del departamento |
| **Departamento** | Nombre del departamento (ej: *Tesoreria*) |

### Sectores Adicionales

Lista de sectores adicionales a los que el usuario tiene acceso, ademas de su sector principal.

### Firma / Sello

| Campo | Descripcion |
|-------|-------------|
| **Sello actual** | Nombre y descripcion del sello de firma asignado (ej: *Director - Sello de Director*) |

### Permisos de Busqueda

| Permiso | Descripcion |
|---------|-------------|
| **Busqueda Global por Numero Documento** | Puede buscar documentos oficiales de cualquier sector |
| **Busqueda Global por Numero Expediente** | Puede buscar expedientes de cualquier sector |

### Roles

Roles asignados al usuario: `Funcionario`, `Administrador`.

### Estado

Estado actual del usuario: `Activo` o `Inactivo`.

### Activacion pendiente

Si el usuario todavia no activo su cuenta, se muestra esta seccion con la opcion de reenviar la invitacion. Esto aplica para usuarios creados con el metodo **Email y Contrasena** que no completaron el proceso de activacion.

| Accion | Descripcion |
|--------|-------------|
| **Reenviar invitacion** | Envia un nuevo email de activacion al usuario para que cree su contrasena |

### Zona de Peligro

| Accion | Descripcion |
|--------|-------------|
| **Desactivar usuario** | Desactiva el acceso del usuario al sistema. El usuario no podra iniciar sesion |

### Actividad

| Campo | Descripcion |
|-------|-------------|
| **Ultimo acceso** | Fecha y hora del ultimo login |
| **Fecha de creacion** | Fecha en que se creo el usuario en el sistema |
