---
description: Cómo cargar una plantilla HTML en un tipo FFCC para que el documento salga redactado con los datos del formulario.
---

# Plantilla de un FFCC

Un tipo **FFCC** (Formulario Controlado) sale, por defecto, como una lista: un campo debajo del otro.

> **Fecha de visita:** 22/08/2026
> **Nombre de fantasía:** El kiosco de la esquina
> **CUIT:** 20-11111111-1

Con una **plantilla**, el mismo formulario sale como un documento redactado. Funciona como «Combinar correspondencia» de Word: vos escribís el texto una vez y marcás dónde va cada dato. El sistema completa los datos con lo que cargó el empleado.

> Se deja constancia de que el día 22/08/2026 personal de esta Dirección inspeccionó el comercio El kiosco de la esquina, CUIT 20-11111111-1, con el siguiente resultado: sin observaciones.

La plantilla es opcional. Un tipo FFCC sin plantilla sigue saliendo como lista.

---

## Cómo funciona

1. El administrador carga la plantilla en el detalle del tipo FFCC.
2. El empleado crea el documento y completa los campos, igual que siempre. No ve la plantilla y no la puede cambiar.
3. Al **Previsualizar** y al **firmar**, el sistema reemplaza cada marcador por el valor del campo.

El texto queda fijo cuando el documento se envía a firmar. Si después cambiás la plantilla, los documentos que ya están en firma salen con la plantilla anterior. Los documentos ya firmados no cambian nunca.

Si un documento se rechaza y se vuelve a enviar a firmar, toma la plantilla vigente en ese momento.

---

## Los marcadores

Un **marcador** es el **nombre del campo** entre llaves dobles: `{{cuit}}`.

- Va el **nombre** del campo (por ejemplo `fecha_visita`), no su etiqueta («Fecha de visita»). Los nombres se ven en la tabla de **Campos del Formulario** y en la lista de marcadores del bloque de la plantilla.
- Se aceptan espacios dentro de las llaves: `{{ cuit }}` es igual a `{{cuit}}`.
- Un mismo marcador se puede usar varias veces.
- El marcador va en el texto, nunca adentro de una etiqueta. `<a href="{{web}}">` no se acepta.

### Cómo sale cada valor

| Tipo de campo | Cómo sale en el documento |
|---|---|
| Fecha | `22/08/2026` |
| Sí / No | «Sí» o «No» |
| Selección (lista) | La opción elegida |
| Texto largo | Con sus saltos de línea |
| Documento adjunto | El número oficial del documento adjunto, solo si la persona que arma el documento puede ver ese documento. Si no lo puede ver, o si todavía no tiene número, sale ` -- N/A -- ` |
| Campo sin completar | ` -- N/A -- ` |

!!! info "Resumen automático y búsqueda"
    Cuando el tipo tiene plantilla, el resumen automático del documento y la búsqueda inteligente leen los campos **y también el texto de la plantilla**. Así el resumen dice qué hace el documento (por ejemplo, «se otorga», «se intima»), y no solo los datos cargados.

Lo que escribe el empleado sale siempre como texto. Si escribe `<b>hola</b>`, el documento muestra `<b>hola</b>`, sin negrita.

---

## Cargar la plantilla

1. En **Tipos de Documentos**, abrí el detalle del tipo FFCC.
2. Debajo de **Campos del Formulario** está el bloque **Plantilla del documento**. Tocá **Cargar plantilla** (o **Editar plantilla**, si ya tiene una).
3. Pegá el HTML en el cuadro, o tocá **Cargar desde archivo** y elegí un archivo `.html`. El archivo tiene que estar guardado en UTF-8 para que las tildes y la ñ lleguen bien.
4. Para sumar un marcador, tocá su nombre en la lista de marcadores: se copia y lo pegás donde va.
5. Tocá **Guardar**.

Si la plantilla rompe una regla, no se guarda. La pantalla muestra cada error con el pedazo de HTML que lo causa.

Para volver a la lista, tocá **Quitar plantilla**.

### Ejemplo

Tipo «Constancia de Inspección» de la Municipalidad del Futuro, con los campos `fecha_visita`, `nombre_fantasia`, `cuit` e `informe_visita`:

```html
<h2 class="ql-align-center">Constancia de Inspección</h2>
<p>Se deja constancia de que el día {{fecha_visita}} personal de esta Dirección
inspeccionó el comercio <strong>{{nombre_fantasia}}</strong>, CUIT {{cuit}},
con el siguiente resultado:</p>
<p style="padding: 6pt; border: 1pt solid #999999; background-color: #f2f2f2">{{informe_visita}}</p>
```

---

## Avisos y bloqueos

| Situación | Qué pasa |
|---|---|
| La plantilla no usa un campo del formulario | Se guarda, con un aviso: «a la plantilla le falta reflejar 1 campo: CUIT» |
| La plantilla usa un marcador que no es ningún campo | No se guarda |
| Borrás o renombrás un campo que la plantilla usa | No se guarda el cambio de campos. Primero cargá una plantilla nueva o quitá la plantilla |
| Borrás todos los campos del tipo | Se borra también la plantilla. La pantalla avisa antes |

---

## Qué se permite

La plantilla maneja **solo el cuerpo** del documento. El número, la fecha y el encabezado los pone el sistema. Las firmas van al final, como en cualquier documento. No hay marcador para el número: el número se asigna con la última firma.

**Etiquetas:** párrafos (`p`), títulos (`h1` a `h6`), negrita (`strong`, `b`), cursiva (`em`, `i`), subrayado (`u`), tachado (`s`), listas (`ul`, `ol`, `li`), tablas (`table`, `tr`, `th`, `td` y sus partes), enlaces (`a`), saltos (`br`), líneas (`hr`), `div`, `span`, `blockquote`.

**Clases del editor** (la forma más segura de dar formato):

| Clase | Qué hace |
|---|---|
| `ql-align-center`, `ql-align-right`, `ql-align-justify` | Centra, alinea a la derecha o justifica |
| `ql-size-small`, `ql-size-large`, `ql-size-huge` | Cambia el tamaño de la letra |
| `ql-font-serif`, `ql-font-monospace` | Cambia la letra |
| `ql-indent-1` a `ql-indent-8` | Sangría |

**El atributo `style`**, solo con estas propiedades:

| Propiedad | Límite |
|---|---|
| `font-family`, `font-weight`, `font-style` | — |
| `font-size` | Entre 6 y 36 pt |
| `text-align`, `text-decoration`, `vertical-align` | — |
| `color`, `background-color` | Nombre (`gray`), `#hex`, `rgb(…)` o `rgba(…)`. La letra no puede ser del mismo color que el fondo, ni transparente |
| `border` y sus variantes | Hasta 5 cm de ancho |
| `padding`, `margin` y sus variantes | Sin negativos, hasta 5 cm |
| `width` | Hasta 100 % (o 17 cm) |
| `line-height` | Entre 1 y 3, sin unidad |

Unidades: `pt`, `px`, `mm` y `cm`. El `%` va solo en `width`.

**Enlaces:** el `href` empieza con `http://`, `https://` o `mailto:`.

---

## Qué se rechaza

- Las etiquetas que no están en la lista: `script`, `style`, `img`, `iframe`, `html`, `head`, `body`, `meta`, `title`.
- Las imágenes. Por ahora la plantilla no lleva imágenes.
- Los atributos que no están en la lista, como `id` u `onclick`.
- Las clases que no son del editor, como `MsoNormal`.
- Los comentarios `<!-- -->` y `<!DOCTYPE>`.
- Una etiqueta abierta y sin cerrar.
- En `style`: otras propiedades (`position`, `display`, `float`, `height`, `opacity`, `background`…), valores fuera de límite, unidades `em`, `rem`, `vw` o `vh`, `url(`, `calc(` y cualquier otra función que no sea `rgb(` o `rgba(`, la barra invertida `\`, los comentarios `/* */`, `!important` y un `;` entre comillas.
- En las tablas, los atributos `border`, `cellpadding` y `cellspacing` con más de 189 (5 cm), o `colspan` y `rowspan` con más de 50.
- Un `{{` sin su `}}`, o un marcador cortado por una etiqueta (`{{cu<b>it}}`).
- Las llaves escritas como código de HTML (`&#123;`, `&lcub;`).
- El texto `end-text`: el sistema lo usa para ubicar la firma.
- Una plantilla de más de 50 KB.

**Por qué tantas reglas:** el número del documento va dentro de la primera página. Un texto que se mueve, se agranda o se esconde puede tapar el número o la firma de un documento oficial.

---

## Word no sirve

No se puede subir un archivo de Word (`.docx`). Tampoco sirve el HTML que deja Word con «Guardar como página web»: trae etiquetas, clases y estilos propios de Word que la plantilla rechaza.

Escribí la plantilla a mano en un editor de texto (el Bloc de notas alcanza), con las etiquetas de [Qué se permite](#que-se-permite). Partí del [ejemplo](#ejemplo) y cambiá el texto.

---

## Preguntas frecuentes

??? question "¿El empleado puede cambiar el texto de la plantilla?"
    No. El empleado solo completa los campos. El texto fijo lo escribe el administrador.

??? question "¿Puedo poner el número del documento dentro del texto?"
    No. El número se asigna con la última firma y va en el encabezado, como en cualquier documento.

??? question "¿Puedo mostrar un párrafo solo si un campo tiene cierto valor?"
    No. La plantilla no tiene condiciones ni filas que se repiten. Cada marcador se reemplaza por su valor.

??? question "¿Qué pasa con los documentos que ya se firmaron?"
    No cambian. La plantilla vale para lo que se envía a firmar después de guardarla.

??? question "¿La plantilla vale para los FFCC que completa el vecino en el portal?"
    Sí. El documento del portal sale con la misma plantilla del tipo.
