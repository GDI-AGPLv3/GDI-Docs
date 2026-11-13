# Verificación de datos

La verificación es un proceso en **2 pasos** que garantiza que los datos cargados en un legajo fueron contrastados contra documentación oficial. Esto le da confiabilidad a la información registrada.

---

## Cómo funciona

El proceso de verificación separa dos roles:

| Rol | Permiso | Que hace |
|-----|---------|----------|
| :material-pencil: **Editor** | `can_edit` | Carga o modifica los datos del campo |
| :material-check-decagram: **Verificador** | `can_verify` | Confirma que el dato es correcto adjuntando un documento oficial de respaldo |

!!! info "Pueden ser la misma persona"
    Un usuario puede tener ambos permisos (`can_edit` + `can_verify`), pero el sistema igualmente registra cada acción por separado. Lo importante es que la verificación sea un acto deliberado y no automático.

---

## Paso 1: Carga de datos (Editor)

El usuario con permiso de edición completa los campos del legajo con la información disponible.

!!! example "Ejemplo: Legajo de habilitación comercial"
    Un empleado del área de Comercio carga los datos del comercio:

    - **Titular**: Juan Pérez
    - **CUIT**: 20-12345678-9
    - **Rubro**: Panadería
    - **Dirección**: Mitre 890
    - **Fecha de habilitación**: 15/03/2026
    - **Vencimiento**: 15/03/2027

Al guardar, cada campo queda en estado **:material-clock-outline: Pendiente de verificación**.

---

## Paso 2: Verificación (Verificador)

El usuario con permiso de verificación revisa cada campo y lo contrasta con la documentación oficial.

Para verificar un campo:

1. Abrí el legajo
2. Hace click en el icono de verificación (:material-check-decagram:) junto al campo
3. Adjunta el **documento oficial** que respalda el dato (ej: constancia de AFIP, resolución de habilitación, plano aprobado)
4. Confirma la verificación

El campo pasa a estado **:material-check-circle: Verificado**, mostrando:

- Quien verificó
- Cuando verifico
- Que documento se adjunto como respaldo

!!! warning "Documento obligatorio"
    No es posible verificar un campo sin adjuntar un documento de respaldo. El sistema lo exige para garantizar la trazabilidad del dato.

---

## Campos con vencimiento

Algunos campos tienen una **fecha de vencimiento** (`expiration_date`). Esto es útil para datos que pierden vigencia con el tiempo.

!!! example "Ejemplos de campos con vencimiento"
    - **Habilitación comercial**: vence el 15/03/2027
    - **Certificado de bomberos**: vence el 01/12/2026
    - **Póliza de seguro**: vence el 30/06/2026
    - **Matrícula profesional**: vence el 31/12/2026

### Qué pasa cuando vence un campo

Cuando un campo alcanza su fecha de vencimiento, se muestra visualmente como **:material-alert-circle-outline: Vencido** en la interfaz. Esto indica que la información necesita renovarse.

!!! tip "Anticipate a los vencimientos"
    Revisa periódicamente los legajos de tu área para identificar campos próximos a vencer y gestionar la renovación de la documentación a tiempo. El sistema muestra la fecha de vencimiento más próxima en el listado de legajos.

---

## Estados de verificación de un campo

| Estado | Icono | Significado |
|--------|-------|-------------|
| Sin datos | :material-minus-circle-outline: | El campo no tiene valor cargado |
| Pendiente | :material-clock-outline: | El dato fue cargado pero aún no fue verificado |
| Verificado | :material-check-circle: | El dato fue verificado con documento de respaldo |
| Vencido | :material-alert-circle-outline: | La verificación vencio y se necesita renovar |
| Modificado | :material-pencil-circle-outline: | El dato fue editado después de ser verificado (requiere nueva verificación) |

---

## Impacto en el informe IFRLM

Cuando se genera un [informe IFRLM](crear-legajo.md#generar-informe-ifrlm), cada campo incluye su estado de verificación. Esto permite saber de un vistazo cuales datos están respaldados por documentación oficial y cuales no.

!!! info "Transparencia"
    El IFRLM muestra claramente que campos están verificados, pendientes o vencidos. Esto es clave para que el receptor del informe sepa el grado de confiabilidad de cada dato.
