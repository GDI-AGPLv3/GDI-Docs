# Relaciones y vinculos

Un legajo no existe aislado. Puede vincularse a **documentos oficiales**, **expedientes** y **otros legajos** para construir una red de informacion conectada.

---

## Vincular documentos a un legajo

Podes asociar documentos oficiales del sistema a un legajo para respaldar la informacion registrada o agregar antecedentes.

### Como vincular un documento

1. Abri el legajo
2. Busca la seccion **Documentos vinculados**
3. Hace click en **"+ Vincular documento"**
4. Busca el documento por numero o referencia
5. Confirma la vinculacion

!!! example "Ejemplos de documentos vinculados"
    - Resolucion de habilitacion vinculada al legajo del comercio
    - Plano aprobado vinculado al legajo de la obra
    - Acta de inspeccion vinculada al legajo de una luminaria

Los documentos vinculados quedan listados en el legajo con su numero oficial, tipo y fecha.

---

## Vincular expedientes a un legajo

De la misma manera, podes asociar expedientes electronicos al legajo.

### Como vincular un expediente

1. Abri el legajo
2. Busca la seccion **Expedientes vinculados**
3. Hace click en **"+ Vincular expediente"**
4. Busca el expediente por numero o referencia
5. Confirma la vinculacion

!!! tip "Vinculacion bidireccional"
    Al vincular un expediente a un legajo, la relacion queda visible tanto desde el legajo como desde el expediente. No es necesario vincular desde ambos lados.

---

## Relaciones entre legajos

Podes crear relaciones entre legajos para representar conexiones logicas. Esto es util cuando multiples legajos estan relacionados entre si.

### Tipos de relacion

| Tipo | Codigo | Significado | Ejemplo |
|------|--------|-------------|---------|
| **Padre** | `parent` | El legajo actual es parte de otro legajo mayor | Una luminaria es parte de un circuito de alumbrado |
| **Hijo** | `child` | Otro legajo es parte del legajo actual | El circuito de alumbrado contiene varias luminarias |
| **Relacionado** | `related` | Los legajos tienen vinculacion tematica | Dos comercios en el mismo edificio |
| **Reemplaza** | `replaces` | El legajo actual sustituye a otro anterior | Nueva habilitacion que reemplaza a la vencida |
| **Hermano** | `sibling` | Los legajos estan al mismo nivel dentro de un grupo | Dos locales del mismo centro comercial |
| **Primo** | `cousin` | Los legajos tienen una relacion indirecta | Obras en la misma manzana de distintos titulares |

### Como crear una relacion

1. Abri el legajo desde el que queres crear la relacion
2. Busca la seccion **Legajos relacionados**
3. Hace click en **"+ Agregar relacion"**
4. Selecciona el **tipo de relacion**
5. Busca el legajo destino por numero o nombre
6. Confirma la relacion

!!! info "Relaciones reciprocas"
    Algunas relaciones se crean de forma reciproca automaticamente:

    - Si creas una relacion **padre**, el otro legajo recibe automaticamente la relacion **hijo**
    - Si creas una relacion **hermano**, el otro legajo tambien recibe la relacion **hermano**
    - Si creas una relacion **reemplaza**, el otro legajo queda marcado como **reemplazado por**

!!! example "Ejemplo: Red de relaciones de un circuito de alumbrado"
    ```
    Circuito de Alumbrado Zona Centro (padre)
    ├── Luminaria LED #4521 - Rotonda Belgrano (hijo)
    ├── Luminaria LED #4522 - Av. Mitre y San Martin (hijo, hermano de #4521)
    └── Luminaria LED #4523 - Plaza Central (hijo, hermano de #4521 y #4522)
    ```

---

## Historial de cambios

Cada legajo mantiene un **historial completo** de todas las acciones realizadas sobre el. El historial registra:

| Evento | Que se registra |
|--------|----------------|
| Creacion | Fecha, usuario que creo el legajo |
| Edicion de campo | Campo modificado, valor anterior, valor nuevo, usuario, fecha |
| Verificacion | Campo verificado, documento de respaldo, verificador, fecha |
| Cambio de estado | Estado anterior, estado nuevo, usuario, fecha |
| Vinculacion | Tipo de vinculo (documento, expediente o legajo), elemento vinculado, usuario, fecha |
| Generacion de IFRLM | Numero del informe generado, usuario, fecha |

### Como consultar el historial

1. Abri el legajo
2. Busca la pestana o seccion **Historial**
3. Se muestra una lista cronologica de todos los eventos

!!! tip "Auditoria completa"
    El historial no se puede editar ni eliminar. Cada accion queda registrada de forma inmutable, lo que garantiza la trazabilidad completa del legajo para fines de auditoria.
