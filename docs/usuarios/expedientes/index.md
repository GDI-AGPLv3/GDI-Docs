# Expedientes

Un **expediente electronico** es una carpeta digital que agrupa documentos oficiales relacionados a un mismo tramite o asunto administrativo. Funciona como el equivalente digital de una carpeta fisica de expediente: reune en un solo lugar todos los informes, dictamenes, resoluciones y demas documentos que forman parte de una gestion.

!!! video "Video tutorial"
    **GDI — Crear un expediente: paso a paso**

    <div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/j2Svh6K2L2k?list=PLRIZqApsdJ12JCSzhUxaZ73AheVHUEpDq" title="GDI — Crear un expediente: paso a paso" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>

---

![Listado de expedientes](../capturas/expedientes-lista.png)

## Identificacion del expediente

Cada expediente recibe un **numero oficial unico** al momento de su creacion, con el siguiente formato:

```
EE-{ANO}-{SECUENCIAL}-{TENANT}-{DEPARTAMENTO}
```

| Parte | Ejemplo | Descripcion |
|-------|---------|-------------|
| EE | `EE` | Prefijo fijo que identifica un expediente electronico |
| ANO | `2026` | Ano de creacion |
| SECUENCIAL | `000019` | Numero secuencial (6 digitos, unico por tenant) |
| TENANT | `TXST` | Codigo de la organizacion/tenant |
| DEPARTAMENTO | `INTE` | Acronimo del departamento iniciador |

Ejemplo completo: `EE-2026-000019-TXST-INTE`

---

## Composicion de un expediente

Al crearse un expediente, el sistema genera automaticamente una **caratula** (documento tipo CAEX) que contiene los datos basicos: tipo de expediente, motivo, reparticion iniciadora y numero oficial. Esta caratula queda como el primer documento del expediente.

Cada expediente tiene:

| Elemento | Descripcion |
|----------|-------------|
| **Tipo** | Categoria del tramite (ej: RRHH - Recursos Humanos, HABI - Habilitacion Comercial, COMP - Compras) |
| **Sector administrador** | El sector que tiene el control actual del expediente |
| **Responsables** | Usuarios designados para llevar adelante el tramite (administrador y adicionales) |
| **Documentos oficiales** | Documentos firmados y vinculados al expediente, numerados en orden |
| **Documentos propuestos** | Documentos cuya vinculacion fue propuesta pero aun no fue aceptada |

---

## Iniciador del expediente

Al crear un expediente, ademas del tipo y el motivo, se elige **quien lo inicia** con un selector de dos opciones:

| Opcion | Significado |
|--------|-------------|
| **Mi Ciudad** | El expediente lo inicia el propio municipio (comportamiento habitual) |
| **Ciudadano** | El expediente lo inicia un **vecino del padron**, a pedido suyo (por ejemplo, un tramite presentado en mesa de entradas) |

Al elegir **Ciudadano** aparece un buscador para seleccionar al vecino por nombre o CUIL (el CUIL se puede escribir con o sin guiones). Solo se puede elegir **un** ciudadano; los ciudadanos **bloqueados** no aparecen en el buscador ni pueden asociarse.

### Si el ciudadano no esta en el padron

Al final de la lista de resultados siempre aparece la opcion **Crear ciudadano**. Abre un formulario breve, sin salir de la pantalla:

| Campo | Regla |
|-------|-------|
| **Nombre y apellido** | Como figura en el documento |
| **CUIL** | 11 digitos, con o sin guiones. Se valida el digito verificador. Tambien vale el CUIT de una empresa |

Al confirmar, el ciudadano queda cargado en el padron y **elegido como iniciador**. A tener en cuenta:

- **Revisar los datos antes de crear**: el nombre y el CUIL no se pueden editar despues.
- El ciudadano nace en estado **Pendiente**. Alcanza para ser iniciador y para recibir el expediente; para **firmar o iniciar tramites desde el portal** un administrador tiene que validarlo en BackOffice > Ciudadanos.
- Si el CUIL **ya estaba cargado**, no se crea nada: se muestra el ciudadano existente con el boton **Usar este**. Si esta bloqueado, se avisa y no se puede usar.
- Lo puede hacer cualquier usuario del municipio. En BackOffice > Ciudadanos estas altas figuran con origen **App**.

La misma opcion esta en la caja **TAD** del Panel del expediente (**Compartir con un ciudadano**): ahi el ciudadano se crea y se le comparte el expediente en el mismo paso.

Reglas del expediente iniciado por un ciudadano:

- El **empleado sigue siendo el creador**: el expediente radica en el sector del empleado y la caratula (CAEX) la firma el, como cualquier expediente interno.
- El expediente se **comparte automaticamente** con el ciudadano, que pasa a verlo desde su portal de Tramites a Distancia (TAD).
- En la caja **TAD** del Panel, el ciudadano iniciador figura marcado como "Inicio el expediente" y **no puede ser quitado** del expediente.
- El movimiento queda registrado en el historial del expediente.

---

## Listado de expedientes

El listado muestra los expedientes como **tarjetas** (cards), una por expediente. Cada tarjeta tiene dos filas:

**Fila superior:** tipo del expediente (badge azul) | motivo | sector administrador | actuantes | numero oficial | boton copiar | fecha de ultima modificacion | estrella de favorito | flecha de ingreso.

**Fila inferior:** resumen breve generado por inteligencia artificial (en cursiva gris).

---

## Solapas de vista

En la parte superior del listado hay cinco solapas para filtrar la vista:

| Solapa | Muestra |
|--------|---------|
| **Todo** | Todos los expedientes a los que el usuario tiene acceso |
| **Personal** | Expedientes donde el usuario es responsable o actuante directo |
| **Administrador** | Expedientes donde el sector del usuario es el administrador |
| **Actuante** | Expedientes donde el sector del usuario participa como actuante |
| **Favoritos** | Expedientes que el usuario marco con la estrella de favorito |

Cada solapa muestra un contador con la cantidad de expedientes correspondientes (excepto "Todo", que muestra todos).

---

## Secciones de esta guia

| Pagina | Descripcion |
|--------|-------------|
| [Detalle del Expediente](detalle-expediente.md) | Vista principal del expediente: header, documentos oficiales, documentos propuestos, responsables y acciones disponibles incluyendo la descarga ZIP |
| [Movimientos](movimientos.md) | Historial de actividad, acciones en curso/finalizadas, y como crear actuaciones internas o transferencias |
| [Vincular Documentos](vincular-documentos.md) | Como vincular documentos oficiales a un expediente, aceptar o rechazar propuestas de vinculacion |
| [Subsanar en Expediente](subsanar-expediente.md) | Como reemplazar un documento dentro de un expediente aportando un justificante |
