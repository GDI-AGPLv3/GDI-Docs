# Digesto Normativo Público

El **Digesto Normativo** es la aplicación más directa del modelo de [Documentos y Legajos Públicos](documentos-publicos.md): publicar en internet, **sin login**, toda la normativa del municipio (ordenanzas, resoluciones, decretos, comunicaciones) de forma ordenada, buscable y consumible por sistemas propios.

!!! abstract "La idea en una frase"
    Cada norma vive como un **documento público firmado** (el PDF oficial) vinculado a un **legajo publico** (la ficha de la norma: número, tipo, materia, fecha, estado de vigencia). El sistema genera automáticamente la **base vectorial** que permite búsqueda inteligente, y una **API pública** de solo lectura entrega todo para el portal web del municipio.

El resultado: un digesto siempre actualizado, donde publicar una norma nueva es simplemente **firmarla y vincularla a su legajo** — sin cargas dobles ni sitios paralelos que mantener.

---

## Arquitectura del digesto

```mermaid
flowchart LR
    A[Tipos de documento<br/>publicos<br/>PLORD, PLRES, ...] --> B[Documentos firmados<br/>PDF oficial + texto]
    B --> C[Base vectorial<br/>automatica]
    D[Familia de registro<br/>publica NORMA] --> E[1 legajo = 1 norma]
    B --> E
    E --> F[API publica]
    C --> F
    F --> G[Portal / web<br/>del municipio]
```

| Pieza | Rol en el digesto |
|-------|-------------------|
| **Tipos de documento públicos** | Definen que clase de normas se publican (Ordenanza, Resolución, etc.) |
| **Documentos firmados** | El texto oficial de cada norma: PDF firmado + transcripción |
| **Base vectorial** | Se genera sola al subir cada documento; habilita la búsqueda por significado |
| **Familia de registro publica** | La ficha estructurada de cada norma (campos públicos y privados) |
| **Legajos** | Un legajo por norma: agrupa la norma, sus anexos y modificatorias |
| **API publica** | El punto de consumo para el portal de digesto del municipio |

---

## Paso 1 — Configurar los tipos de documento público

En [Tipos de Documentos](tipos-de-documentos.md) se crean los tipos que van a contener la normativa, con **Visibilidad: Público**. La convención recomendada para normativa del Poder Legislativo:

| Acrónimo | Nombre | Contiene |
|----------|--------|----------|
| **PLORD** | Poder Legislativo - Ordenanza | Ordenanzas del HCD |
| **PLRES** | Poder Legislativo - Resolución | Resoluciones del HCD |
| **PLCOM** | Poder Legislativo - Comunicación | Comunicaciones del HCD |
| **PLDEC** | Poder Legislativo - Decreto | Decretos del HCD |

Se pueden agregar los que el municipio necesite (por ejemplo decretos del Ejecutivo que reglamentan ordenanzas), siempre con el mismo criterio: **un tipo por clase de norma**.

!!! danger "Público es irreversible: decidir antes de crear"
    La visibilidad de un tipo de documento se elige **una sola vez, al crearlo**, y no se puede volver atrás. Todos los PDFs firmados de estos tipos quedan accesibles por cualquier persona en internet. Para un digesto esto es exactamente lo buscado — la normativa es pública por naturaleza — pero conviene verificar que por estos tipos **solo** vaya a circular normativa, nunca documentos con datos personales. Ver [Publicar un Tipo de Documento](documentos-publicos.md#publicar-un-tipo-de-documento).

!!! warning "El acrónimo del municipio queda congelado"
    Las URLs públicas dependen del acrónimo del municipio. Desde que existe el primer tipo publico, el acrónimo **no se puede cambiar**. Elegirlo bien antes de arrancar.

---

## Paso 2 — Subir los documentos (la base vectorial se genera sola)

Con los tipos creados, se sube la normativa: las normas nuevas por el circuito normal de firma, y el acervo histórico como **documentos importados** (PDF) que se firman digitalmente al ingresar.

Por cada documento firmado de un tipo publico, el sistema hace automáticamente:

1. **Publica el PDF oficial**: se copia al espacio público y queda accesible por una URL estable (`pdf_url`).
2. **Transcribe el contenido**: extrae el texto completo del PDF (incluso escaneados, vía OCR).
3. **Genera el resumen**: un resumen automático del contenido de la norma.
4. **Construye la base vectorial**: genera los *embeddings* del texto, que alimentan la búsqueda semántica.

!!! tip "No hay nada que configurar"
    La transcripción, el resumen y la base vectorial **vienen de fábrica**: no hay que activar ni configurar nada. Subir y firmar el documento alcanza; unos minutos después el contenido ya es buscable por significado (por ejemplo, buscar *"habilitación de comercios gastronómicos"* encuentra normas que no usan esas palabras exactas).

!!! info "Cargas masivas del acervo histórico"
    Para digitalizar anos de normativa acumulada (miles de PDFs), GDI acompana el proceso con un pipeline de carga masiva que sube, firma, transcribe y crea los legajos en tandas. Consultar al equipo de GDI antes de encarar una carga histórica a mano.

---

## Paso 3 — Crear la familia de legajos pública

La ficha de cada norma vive en un **legajo** de una [Familia de Registro](familias-registro.md) dedicada a normativa (convención: código **NORMA**). En la familia se definen **todos** los campos que el municipio quiere registrar — públicos y privados — y después se marca **cuáles se publican**.

Un esquema de datos típico para normativa:

| Campo | Ejemplo | ¿Publicarlo? |
|-------|---------|--------------|
| `tipo_norma` | Ordenanza | Sí |
| `numero_norma` | 5383 | Sí |
| `fecha_sancion` | 12/06/2026 | Sí |
| `materia` | Habilitaciones comerciales | Sí |
| `expediente` | 18045/24 | Según criterio del municipio |
| `sesion` | Ordinaria 08/2026 | Según criterio del municipio |
| Notas internas de seguimiento | — | No |

Luego se activa la **Publicación Pública** de la familia y se configura que se expone:

- **Campos públicos**: solo los tildados salen por la API; el resto nunca se publica.
- **Estados visibles**: por ejemplo, publicar solo los legajos en estado *Vigente*. Una norma **derogada** puede mantenerse visible (con su estado a la vista) o salir del digesto automáticamente al cambiar de estado — lo decide el municipio con los estados que marca.
- **Mostrar documentos vinculados**: activarlo — es lo que conecta la ficha de la norma con su PDF y su texto.
- **Mostrar legajos relacionados**: activarlo si se quiere navegar de una norma a sus modificatorias.

La mecánica completa (diálogos, validaciones, reversibilidad) está en [Familias de Registro públicas](documentos-publicos.md#familias-de-registro-publicas).

!!! tip "La familia pública es reversible"
    A diferencia de los tipos de documento, la publicación de la familia se puede **prender y apagar** cuando se quiera, y la configuración de campos y estados se ajusta en cualquier momento.

---

## Paso 4 — Vincular cada documento a su legajo

La regla de oro del digesto: **1 legajo = 1 normativa**. Por cada norma se crea un legajo de la familia NORMA, se completan sus campos y se le vinculan sus documentos:

- El documento principal (el texto de la ordenanza o resolución).
- Sus **anexos** (planos, tablas, nomencladores), cada uno como documento propio.
- Con el tiempo, sus **modificatorias y textos ordenados**, para que el legajo cuente la historia completa de la norma.

Así, quien consulta la Ordenanza 5383 ve **una sola ficha** con todos sus documentos, su estado de vigencia y sus normas relacionadas — en lugar de PDFs sueltos.

!!! tip "Normas extensas: separar en capítulos"
    Para normativas tipo **Código de Edificación, Código de Ordenamiento Territorial o Fiscal/Tributaria** (cientos de páginas), se recomienda **separar el texto en capítulos**, subiendo cada capítulo como un documento propio, todos vinculados al mismo legajo. Ventajas:

    - Los motores de IA procesan **mucho mejor** documentos acotados: la transcripción, el resumen y la búsqueda semántica ganan precisión cuando cada documento trata un solo tema.
    - Una modificación puntual (por ejemplo, un artículo del capítulo de usos del suelo) se resuelve reemplazando **un capítulo**, no re-procesando el código entero.
    - El ciudadano llega directo al capítulo que le interesa, sin descargar un PDF gigante.

!!! info "Relaciones entre normas"
    Las relaciones entre legajos permiten modelar el tejido normativo: una ordenanza *modifica* a otra, un decreto *reglamenta* una ordenanza, un texto ordenado *reemplaza* versiones anteriores. Ver [Relaciones y Vínculos](../usuarios/legajos/relaciones.md).

---

## Paso 5 — Conectar el digesto a la web del municipio

Con todo publicado, el digesto se consume desde la **API pública** de solo lectura: el municipio arma su portal de digesto (o integra el existente) contra estos endpoints, bajo `/api/v1/public/{muni}/...`:

| Necesidad del portal | Endpoint |
|----------------------|----------|
| Buscador del digesto (texto + significado) | `GET .../search?q=...` |
| Listado de normas, paginado y filtrable | `GET .../registries/NORMA/records` |
| Ficha de una norma (campos + documentos + relacionadas) | `GET .../records/{record_number}` |
| Texto completo de la norma en HTML | `GET .../documents/{document_id}/content` |
| Descarga del PDF oficial firmado | `pdf_url` (link directo, sin API Key) |

La referencia completa — autenticación con `X-API-Key`, parámetros, ejemplos de request/respuesta, códigos de error y buenas prácticas — está en [API pública](documentos-publicos.md#api-publica).

!!! warning "La API Key vive en el servidor del municipio"
    La API se consume **server-to-server**: el backend del portal municipal llama a GDI con su API Key y arma las páginas. La clave **nunca** debe viajar al navegador. El único recurso de acceso directo y anónimo es el `pdf_url` de cada PDF público.

!!! info "Flujo típico del portal de digesto"
    1. `GET /registries` → confirma la familia NORMA y sus campos públicos.
    2. `GET /registries/NORMA/records` → listado de normas para el buscador/indice.
    3. `GET /records/{record_number}` → ficha de la norma, con `pdf_url` y `document_id` de cada documento.
    4. `GET /documents/{document_id}/content` → texto HTML para mostrar la norma en la página (sanitizar antes de renderizar).

---

## Checklist de puesta en marcha

- [ ] Acrónimo del municipio definitivo (queda congelado al publicar).
- [ ] Tipos de documento públicos creados (PLORD, PLRES y los que correspondan).
- [ ] Normativa subida y firmada (nueva por circuito normal; histórica por carga masiva).
- [ ] Familia NORMA creada, con esquema de datos completo (campos públicos y privados).
- [ ] Publicación Pública de la familia activada: campos, estados y vinculados configurados.
- [ ] Un legajo por norma, con sus documentos vinculados (capítulos separados en códigos extensos).
- [ ] API Key del municipio entregada al equipo técnico por canal seguro.
- [ ] Portal del municipio integrado contra la API pública.

!!! note "Régimen permanente"
    Una vez en marcha, el digesto se mantiene solo: sancionada una norma nueva, se firma su documento (tipo público), se crea su legajo y se vincula. Aparece en el portal automáticamente, con su texto buscable — sin ningún paso extra de "publicación".
