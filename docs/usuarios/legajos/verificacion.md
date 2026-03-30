# Verificacion de datos

La verificacion es un proceso en **2 pasos** que garantiza que los datos cargados en un legajo fueron contrastados contra documentacion oficial. Esto le da confiabilidad a la informacion registrada.

---

## Como funciona

El proceso de verificacion separa dos roles:

| Rol | Permiso | Que hace |
|-----|---------|----------|
| :material-pencil: **Editor** | `can_edit` | Carga o modifica los datos del campo |
| :material-check-decagram: **Verificador** | `can_verify` | Confirma que el dato es correcto adjuntando un documento oficial de respaldo |

!!! info "Pueden ser la misma persona"
    Un usuario puede tener ambos permisos (`can_edit` + `can_verify`), pero el sistema igualmente registra cada accion por separado. Lo importante es que la verificacion sea un acto deliberado y no automatico.

---

## Paso 1: Carga de datos (Editor)

El usuario con permiso de edicion completa los campos del legajo con la informacion disponible.

!!! example "Ejemplo: Legajo de habilitacion comercial"
    Un empleado del area de Comercio carga los datos del comercio:

    - **Titular**: Juan Perez
    - **CUIT**: 20-12345678-9
    - **Rubro**: Panaderia
    - **Direccion**: Mitre 890
    - **Fecha de habilitacion**: 15/03/2026
    - **Vencimiento**: 15/03/2027

Al guardar, cada campo queda en estado **:material-clock-outline: Pendiente de verificacion**.

---

## Paso 2: Verificacion (Verificador)

El usuario con permiso de verificacion revisa cada campo y lo contrasta con la documentacion oficial.

Para verificar un campo:

1. Abri el legajo
2. Hace click en el icono de verificacion (:material-check-decagram:) junto al campo
3. Adjunta el **documento oficial** que respalda el dato (ej: constancia de AFIP, resolucion de habilitacion, plano aprobado)
4. Confirma la verificacion

El campo pasa a estado **:material-check-circle: Verificado**, mostrando:

- Quien verifico
- Cuando verifico
- Que documento se adjunto como respaldo

!!! warning "Documento obligatorio"
    No es posible verificar un campo sin adjuntar un documento de respaldo. El sistema lo exige para garantizar la trazabilidad del dato.

---

## Campos con vencimiento

Algunos campos tienen una **fecha de vencimiento** (`expiration_date`). Esto es util para datos que pierden vigencia con el tiempo.

!!! example "Ejemplos de campos con vencimiento"
    - **Habilitacion comercial**: vence el 15/03/2027
    - **Certificado de bomberos**: vence el 01/12/2026
    - **Póliza de seguro**: vence el 30/06/2026
    - **Matricula profesional**: vence el 31/12/2026

### Que pasa cuando vence un campo

Cuando un campo alcanza su fecha de vencimiento, se muestra visualmente como **:material-alert-circle-outline: Vencido** en la interfaz. Esto indica que la informacion necesita renovarse.

!!! tip "Anticipate a los vencimientos"
    Revisa periodicamente los legajos de tu area para identificar campos proximos a vencer y gestionar la renovacion de la documentacion a tiempo. El sistema muestra la fecha de vencimiento mas proxima en el listado de legajos.

---

## Estados de verificacion de un campo

| Estado | Icono | Significado |
|--------|-------|-------------|
| Sin datos | :material-minus-circle-outline: | El campo no tiene valor cargado |
| Pendiente | :material-clock-outline: | El dato fue cargado pero aun no fue verificado |
| Verificado | :material-check-circle: | El dato fue verificado con documento de respaldo |
| Vencido | :material-alert-circle-outline: | La verificacion vencio y se necesita renovar |
| Modificado | :material-pencil-circle-outline: | El dato fue editado despues de ser verificado (requiere nueva verificacion) |

---

## Impacto en el informe IFRLM

Cuando se genera un [informe IFRLM](crear-legajo.md#generar-informe-ifrlm), cada campo incluye su estado de verificacion. Esto permite saber de un vistazo cuales datos estan respaldados por documentacion oficial y cuales no.

!!! info "Transparencia"
    El IFRLM muestra claramente que campos estan verificados, pendientes o vencidos. Esto es clave para que el receptor del informe sepa el grado de confiabilidad de cada dato.
