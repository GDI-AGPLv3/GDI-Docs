# Roles y Sellos

Gestiona los rangos jerárquicos y sellos de firma de la organización. Los rangos determinan que tipos de documentos puede firmar cada funcionario. Los sellos definen la firma visual que aparece en los PDFs.

![Roles y Sellos](capturas/roles-y-sellos.png)

!!! video "Video tutorial"
    **GDI BackOffice — Sellos y rangos de firma**

    <div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/ZkPR6T5OkAE?list=PLbbUEsKhLkuc" title="GDI BackOffice — Sellos y rangos de firma" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>



---

## Cómo funciona la relación entre Sellos y Rangos

El sistema tiene dos conceptos separados que trabajan juntos:

- **Sello**: La firma visual que se estampa en el PDF (nombre, cargo, formato).
- **Rango**: El nivel jerárquico del funcionario (Intendente, Secretario, Director).

Cada **Rango** tiene un **Sello** vinculado en la columna "Firma". Esta vinculación es clave porque **el Rango puede pisar el sello individual del usuario**.

### Regla de prioridad de sello

Cada usuario tiene un **sello propio** asignado en su perfil (sección [Usuarios](usuarios.md)). Sin embargo, si el usuario es **Responsable de Departamento** y su rango tiene un sello vinculado, el sistema aplica la siguiente lógica:

1. El sistema verifica si el usuario tiene un **Rango** asignado como responsable de departamento
2. Si el Rango tiene un **Sello vinculado**, ese sello **pisa (sobreescribe)** el sello individual del usuario al momento de firmar
3. Si el usuario no tiene rango de responsable, se usa su **sello propio**

!!! example "Ejemplo práctico"
    - **Ana López** tiene asignado el sello *"Innovador"* en su perfil de usuario
    - Ana es **Responsable del departamento Hacienda** con rango de **Secretario** (Nivel 2)
    - El rango Secretario tiene vinculado el sello **"Secretario"**
    - Cuando Ana firma un documento, el sistema usa el sello **"Secretario"** (del rango), **no** el sello "Innovador" (de su perfil)

!!! warning "Importante"
    El sello que se ve en el perfil del usuario (sección Firma/Sello) es el sello **propio** del usuario. No refleja necesariamente el sello que se usará al firmar, ya que el rango puede pisarlo.

---

## Sellos de la Organización

Cada sello define un tipo de firma visual que se estampa en los documentos firmados. Son las "plantillas" de firma disponibles en la organización.

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Nombre del sello (ej: *Director*, *Intendente Municipal*, *Secretario*, *Innovador*) |
| **Descripción** | Texto descriptivo del sello |
| **Estado** | <span class="campo-tag campo-tag--obligatorio">vinculado</span> indica que el sello está asociado a un **Rango Jerárquico** |

!!! info "Qué significa vinculado"
    La etiqueta <span class="campo-tag campo-tag--obligatorio">vinculado</span> aparece cuando el sello está asociado a un Rango en la tabla de Rangos Jerárquicos (columna "Firma"). Un sello solo puede estar vinculado a **un** Rango. Los sellos sin etiqueta "vinculado" (como *Innovador*) son sellos independientes que se asignan directamente a usuarios sin pasar por un rango.

### Acciones por sello

| Acción | Descripción |
|--------|-------------|
| :material-pencil: **Editar** | Modificar nombre y descripción del sello |
| :material-delete: **Eliminar** | Eliminar el sello. Solo posible si **no** está vinculado a un Rango |
| **+ Agregar sello** | Crear un nuevo sello para la organización |

---

## Rangos Jerárquicos

Los rangos definen la jerarquía de la organización. Cada rango tiene un sello de firma vinculado y un nivel que determina que tipo de documentos puede numerar.

| Campo | Descripción |
|-------|-------------|
| **Nivel** | Posición en la jerarquía (1 = más alto). Determina que tipos de documento puede numerar |
| **Nombre** | Nombre del rango (ej: *Intendente*, *Secretario*, *Director*) |
| **Firma** | Sello vinculado a este rango. Se usa al firmar en lugar del sello propio del usuario |

### Ejemplo de configuración

| Nivel | Nombre | Firma (Sello vinculado) | Puede numerar |
|:-----:|--------|-------------------------|---------------|
| 1 | Intendente | Intendente Municipal | Decretos, Resoluciones, Disposiciones y todos los demás |
| 2 | Secretario | Secretario | Resoluciones, Disposiciones y tipos sin restricción |
| 3 | Director | Director | Disposiciones y tipos sin restricción |

!!! info "Relación Rango - Tipo de Documento"
    Algunos tipos de documento requieren un rango mínimo para poder ser numerados. Por ejemplo, un **Decreto** solo puede ser numerado por un funcionario con rango de **Intendente** (Nivel 1). Esta restricción se configura en [Tipos de Documentos](tipos-de-documentos.md) > Restricción por Rango.

### Acciones por rango

| Acción | Descripción |
|--------|-------------|
| :material-pencil: **Editar** | Modificar nombre y sello de firma del rango |
| :material-delete: **Eliminar** | Eliminar el rango |
| **+ Agregar rango** | Crear un nuevo nivel jerárquico |
