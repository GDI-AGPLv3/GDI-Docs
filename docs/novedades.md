---
description: Novedades de GDI, mes por mes, con el link a la guía de cada funcionalidad.
---

<!-- Esta página espeja el blog https://gdilatam.com/novedades.
     Fuente: GDI-WebLanding/src/lib/data/novedades.ts.
     Cuando sale una entrega nueva, se suma allá y acá arriba (la más nueva primero). -->

# Novedades

Lo nuevo en GDI, mes por mes. Cada entrega tiene su nota completa en el [blog de Novedades](https://gdilatam.com/novedades) y cada novedad, el link a la guía que explica cómo se usa.

## 27 de noviembre de 2026: Los expedientes se cierran, se archivan y se buscan con un asistente

Noviembre 2026: cierre y reapertura de expedientes, Archivo, Asistente de Búsqueda con chat de IA, Impresora GDI, formularios con grupo dentro de grupo y datos de formularios firmados por API y MCP. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-11-cierre-de-expedientes-archivo-asistente-de-busqueda).

- **El expediente muestra su estado y se cierra con un documento** (Nueva funcionalidad). Cada expediente muestra si está En trámite o Paralizado. Para cerrarlo se firma un documento de cierre (CIEX) y, si hay que retomarlo, se reabre mandándolo a un sector. [Ver la guía](usuarios/expedientes/detalle-expediente.md)
- **Archivo: ver y buscar los expedientes cerrados** (Nueva funcionalidad). Quien tiene el permiso Archivo ve y busca los expedientes cerrados. [Ver la guía](usuarios/expedientes/index.md)
- **Asistente de Búsqueda: palabras, números y un chat con IA** (Inteligencia Artificial). Reemplaza al buscador. Si algo existe pero no podés abrirlo, ves una ficha con lo básico. Al lado tenés el chat con IA. [Ver la guía](usuarios/busqueda/buscador-general.md)
- **Impresora GDI: imprimís desde tu PC y llega a GDI** (Nueva funcionalidad). El PDF que imprime el programa de la PC llega a la pantalla Importando desde PC. [Ver la guía](usuarios/documentos/documento-importado.md)
- **Formularios con un grupo adentro de otro** (Nueva funcionalidad). Por ejemplo, una persona y, adentro, sus actividades. El resumen de IA muestra un renglón por bloque. [Ver la guía](usuarios/documentos/documento-ffcc.md)
- **Un punto rojo en lo que te compartieron y no abriste** (Mejora). Las solapas de Documentos tienen ícono y texto, y Compartidos conmigo pasó al segundo lugar. [Ver la guía](usuarios/documentos/index.md#pestanas-de-filtrado)
- **El editor de un documento compartido puede cancelar la firma** (Firma). Además, cada tipo de documento muestra su clase y su tipo de firma con un ícono. [Ver la guía](usuarios/documentos/proceso-de-firma.md)
- **El tipo de expediente tiene un objetivo que usa el resumen de IA** (Inteligencia Artificial). El administrador lo escribe en el tipo de expediente. [Ver la guía](administradores/tipos-de-expedientes.md)
- **Vincular automáticamente, ahora con casilla** (Mejora). Si la destildás, el documento firmado queda propuesto y decide el responsable. [Ver la guía](usuarios/expedientes/vincular-documentos.md)
- **Formularios firmados con sus datos, por API y MCP** (Integración). El sistema externo recibe los valores cargados y la lista de campos. [Ver la guía](desarrollo/gateway/rest-api/expedientes.md)
- **Firmas completas y avisos claros** (Mejora). Una hoja con 14 firmantes o más muestra todas las firmas, los adjuntos de un PDF importado aparecen en el documento oficial y los avisos normales ya no salen como Error 500 o 502. [Ver la guía](usuarios/documentos/proceso-de-firma.md)

## 20 de noviembre de 2026: Borradores que se escriben entre dos y formularios con grupos que se repiten

Noviembre 2026: borradores compartidos por turnos, formularios controlados con grupos de campos que se repiten, documentos firmados propuestos a un expediente y adjuntos dentro del PDF de Notas y Memos. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-11-borradores-compartidos-formularios-grupos).

- **Borradores compartidos, una persona escribe por vez** (Nueva funcionalidad). Compartís un borrador desde la caja «Compartir» y otra persona lo edita y lo puede mandar a firma. Uno escribe y los demás miran: «Tomar edición» y «Soltar» pasan el turno. El editor también suma tablas. [Ver la guía](usuarios/documentos/crear-editar-documento.md#compartir-un-borrador-y-editarlo-por-turnos)
- **Lo que editaste, en Mis Documentos** (Mejora). Cuando se firma un borrador que editaste, el documento aparece en tu lista de Mis Documentos y lo encontrás por referencia. [Ver la guía](usuarios/documentos/index.md#pestanas-de-filtrado)
- **Formularios controlados con grupos que se repiten** (Nueva funcionalidad). El administrador arma un grupo de campos (por ejemplo, Nombre, Apellido y DNI) y el usuario lo repite con «+ Agregar persona», sin saber de antemano cuántas personas van. Si el grupo no tiene campos obligatorios y no lo tocás, el documento se firma igual. [Ver la guía](usuarios/documentos/documento-ffcc.md#grupos-que-se-repiten)
- **Formularios controlados con texto redactado** (Nueva funcionalidad). El administrador carga una plantilla y el documento sale como un texto redactado con los datos del formulario. El resumen de IA lee también ese texto, así dice qué resolvió el acto. [Ver la guía](administradores/plantilla-ffcc.md)
- **Proponer un documento a un expediente que ves** (Nueva funcionalidad). Si ves el expediente pero no podés vincular, igual le proponés un documento firmado. El área responsable lo acepta o lo rechaza. [Ver la guía](usuarios/expedientes/vincular-documentos.md)
- **Adjuntos dentro de Notas y Memos** (Mejora). Una nota o un memo lleva sus adjuntos dentro del PDF firmado, y los destinatarios los ven y los descargan. [Ver la guía](usuarios/notas/index.md#archivos-adjuntos-en-la-nota)
- **El legajo, ordenado en solapas** (Mejora). El detalle del legajo se divide en solapas, y el estado se cambia desde la caja Estado de la solapa Datos. [Ver la guía](usuarios/legajos/index.md#solapas-del-detalle-de-legajo)
- **Etiquetas de sector que se leen siempre** (Mejora). Toda etiqueta de sector lleva el color del sector de fondo y un texto que se lee sobre cualquier color. Al pasar el mouse dice la repartición y el sector. [Ver la guía](usuarios/expedientes/index.md#etiquetas-de-sector)
- **El PDF se abre bien en el celular** (Mejora). En el celular, «Ver PDF» abre el documento en una pestaña nueva con la dirección de GDI de tu municipio. [Ver la guía](usuarios/documentos/index.md#ver-el-pdf-desde-el-celular)
- **Sellos de firma parejos** (Firma). Todos los sellos llevan letra del mismo tamaño: una línea larga se parte en dos renglones. [Ver la guía](usuarios/documentos/proceso-de-firma.md#como-queda-la-firma-en-el-pdf)
- **Se firma un importado con muchas firmas de afuera** (Firma). Un PDF que ya trae muchas firmas de otro sistema se firma en GDI, y sus firmas de origen siguen válidas. [Ver la guía](usuarios/documentos/proceso-de-firma.md#como-queda-la-firma-en-el-pdf)
- **Aviso claro cuando un archivo es demasiado grande** (Mejora). Si un archivo pasa el tope, GDI dice cuál es el máximo y qué hacer. [Ver la guía](usuarios/documentos/documento-importado.md#avisos-al-importar-un-pdf)
- **Cuentagotas para el color institucional** (Administración). En el BackOffice tomás el color del logo con un clic. [Ver la guía](administradores/informacion-general.md#tomar-el-color-del-logo-con-el-cuentagotas)
- **Alta de legajo sin duplicados por API** (Integraciones). Si un sistema reintenta el alta de un legajo, GDI no crea uno repetido. [Ver la guía](desarrollo/gateway/rest-api/legajos.md#reintentos-seguros-idempotency-key)

## 27 de octubre de 2026: Cada uno ve lo de su sector, y los documentos llevan imágenes

Octubre 2026: filtro por sector para todo GDI, imágenes en Notas y Memos, buscador dentro de los legajos y alta del vecino desde el expediente. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-10-filtro-por-sector-imagenes-en-notas).

- **Si trabajás en varios sectores, elegís desde cuál mirar** (Nueva funcionalidad). Tocás tu foto en el menú y aparece el organigrama: marcás uno o varios sectores y el Inicio, Expedientes, Documentos, Legajos y Comunicaciones muestran solo lo de esos sectores. Si no elegís nada, ves todo como siempre. Los buscadores siguen buscando en todo el municipio. [Ver la guía](usuarios/inicio/index.md)
- **Imágenes adentro de Notas y Memos** (Mejora). El botón de imagen del editor ahora también está en Notas y Memos. Subís la foto del lugar, un plano o una captura y queda dentro del documento, sin mandarla aparte. [Ver la guía](usuarios/notas/index.md)
- **Buscador en los documentos vinculados de un legajo** (Mejora). Un legajo con muchos documentos ya no se recorre a mano: escribís el número o la referencia y lo encontrás. La lista viene por páginas, así que abre rápido aunque tenga cientos. [Ver la guía](usuarios/legajos/index.md)
- **Cargás al vecino sin salir del expediente** (Mejora). Si el vecino que inicia el trámite todavía no está cargado en GDI, lo das de alta ahí mismo, desde el expediente. No hace falta ir a otra pantalla y volver. [Ver la guía](usuarios/expedientes/index.md)

## 16 de septiembre de 2026: Entrás, ves qué te toca y firmás todo junto

Septiembre 2026: menciones con @ en el Inicio, PortaFirma para firmar varios documentos con un solo PIN y un tablero de uso del sistema para administradores. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-09-portafirma-menciones-logs).

- **Entrás y ves qué te toca hoy, y dónde te mencionaron** (Nueva funcionalidad). La pantalla de Inicio junta todo lo que depende de vos: lo que esperás firmar, los memos sin leer, las notas al sector y los expedientes donde te nombraron responsable. Si alguien te menciona con @ en un comentario, la mención aparece en tu Inicio aunque el expediente no sea de tu área. [Ver la guía](usuarios/inicio/index.md)
- **PortaFirma: firmá varios documentos a la vez** (Firma). En el PortaFirma seleccionás los documentos que querés firmar juntos y los firmás de una, escribiendo el PIN del token una sola vez (con el FirmadorGDI actualizado). Mientras el sistema los numera y los guarda, seguís con lo tuyo. [Ver la guía](usuarios/documentos/firmar-con-token.md)
- **LOGs del Sistema: el pulso del municipio en una pantalla** (Administración). En el panel de administración: cuántos de los usuarios cargados entraron en los últimos 30 días, qué se firmó esta semana y qué áreas del organigrama están activas. Seis indicadores en una vista, con rango de fechas, tablas que se exportan a CSV y un modo VIVO que se actualiza solo. [Ver la guía](administradores/logs.md)

## 18 de agosto de 2026: GDI te organiza el día: el sistema te busca a vos

Agosto 2026: pantalla de Inicio con lo que te toca hoy, firma desde el celular y expedientes que nacen con el vecino adentro. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-08-home-nuevo-firma-en-el-celular).

- **El Inicio nuevo: entrás y ves qué te toca hoy** (Nueva funcionalidad). Una sola pantalla al entrar: qué esperás firmar, qué expedientes te asignaron y dónde te nombraron responsable. Cada aviso se cierra solo cuando entrás al expediente. Se acabó recorrer bandejas para saber por dónde empezar. [Ver la guía](usuarios/inicio/index.md)
- **La firma llegó al celular** (Firma). Botón "Firmar ahora" en el teléfono, con las comunicaciones oficiales completas y el detalle de cada documento. El que está en una recorrida o en una reunión firma igual: el expediente no espera a que nadie vuelva a la oficina. [Ver la guía](usuarios/documentos/proceso-de-firma.md)
- **El vecino, en el expediente desde el minuto cero** (Nueva funcionalidad). Al crear un expediente elegís qué vecino lo inicia, con un buscador integrado. El trámite nace con el ciudadano adentro, y todo lo que pasa le llega a él también. [Ver la guía](usuarios/expedientes/index.md)

## 28 de julio de 2026: Trámites a Distancia, mejor lectura de escaneados y GDI en el celular

Julio 2026: el vecino recibe notificaciones y firma dentro del expediente, GDI lee documentos escaneados viejos y el expediente se ve bien en el teléfono. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-07-tramites-a-distancia-escaneados-celular).

- **Trámites a Distancia: el vecino, dentro del expediente** (Nueva funcionalidad). El vecino ya no necesita ir al municipio: recibe las notificaciones oficiales, ve los documentos de su trámite y firma desde donde esté. Todo queda registrado en el expediente. Si el municipio ya tiene portal de trámites, se conecta. [Ver la guía](usuarios/expedientes/index.md)
- **Ahora lee bien hasta los papeles viejos** (Inteligencia Artificial). Subís una ordenanza escaneada de hace veinte años y GDI la lee, la resume y la deja buscable por texto. Lo que estaba en una caja del archivo aparece en segundos. [Ver la guía](usuarios/documentos/documento-importado.md)
- **El expediente, también desde el celular** (Mejora). Abrís el expediente desde el teléfono y ves primero lo importante: en qué está, quién lo tiene y qué falta firmar. Para resolver fuera de la oficina, sin volver a la computadora. [Ver la guía](usuarios/expedientes/detalle-expediente.md)

## 16 de julio de 2026: Expedientes reservados, un editor más completo y adjuntos embebidos

Julio 2026: expedientes y documentos con acceso restringido, editor con imágenes y formato, y archivos adjuntos dentro de cualquier documento. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-07-reservados-editor-adjuntos).

- **Expedientes y documentos Reservados** (Nueva funcionalidad). Podés marcar un expediente o un documento como Reservado: solo acceden las personas designadas. El resto no lo ve en los listados ni puede abrirlo por link, y un candado lo identifica en todo el sistema. Pensado para legajos, sumarios y temas de personal. [Ver la guía](usuarios/expedientes/reservados.md)
- **El editor inserta imágenes y da formato** (Mejora). El editor de documentos suma imágenes, títulos, tipografía y tamaño de texto. Redactás actos, notas y memos con mejor presentación, directo dentro de GDI y sin depender de Word. [Ver la guía](usuarios/documentos/crear-editar-documento.md)
- **Archivos adjuntos dentro de cualquier documento** (Mejora). Podés embeber archivos (PDF, imágenes) dentro de cualquier documento, verlos listados en el visor del documento oficial y descargarlos con un clic. Todo el respaldo del trámite queda en un solo lugar. [Ver la guía](usuarios/documentos/previsualizar-documento.md)

## 29 de junio de 2026: Integración con X-Road, historial de expedientes e IA que lee documentos

Junio 2026: GDI se integra con X-Road EDI-RIL, el expediente suma un historial tipo conversación y el asistente de IA lee los documentos del trámite. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-06-x-road-historial-ia-lee-documentos).

- **GDI se conecta con X-Road EDI-RIL** (Integración). GDI se integra con X-Road EDI-RIL, el estándar de interoperabilidad entre organismos públicos. Los expedientes intercambian datos con otros sistemas de gobierno de forma directa, sin carga manual ni intermediarios.
- **El historial del expediente, con mensajes y anotaciones** (Mejora). Cada expediente tiene una solapa de Historial: todos los movimientos como una conversación, con la posibilidad de agregar mensajes o anotaciones sin generar un documento nuevo. Menos correos paralelos, más contexto donde corresponde. [Ver la guía](usuarios/expedientes/movimientos.md)
- **El asistente de IA del expediente lee tus documentos** (Inteligencia Artificial). El asistente de IA integrado en cada expediente accede a los documentos adjuntos y responde con el contexto real del trámite. Le podés preguntar lo que quieras sobre cualquier expediente abierto. [Ver la guía](usuarios/asistente-ai/index.md)

## 11 de junio de 2026: Tres novedades para mover más rápido los expedientes

Junio 2026: crear el documento desde el propio expediente, formularios controlados para los trámites de siempre y reparto de tareas por persona y por sector. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-06-documento-desde-el-expediente-ffcc-tareas).

- **Creá el documento desde el propio expediente** (Nueva funcionalidad). Crear o importar un documento, firmarlo y vincularlo al expediente es un solo paso, sin salir de la pantalla. Al firmar, se vincula solo. [Ver la guía](usuarios/expedientes/vincular-documentos.md)
- **Formularios controlados para los trámites de siempre** (Nueva funcionalidad). Completás unos pocos campos y GDI arma el documento y guarda el dato. Menos tipeo, menos errores y la información queda ordenada para consultar o reportar después. [Ver la guía](usuarios/documentos/documento-ffcc.md)
- **Repartí tareas por persona y por sector** (Nueva funcionalidad). Dentro del expediente asignás tareas a una persona puntual o a un sector, con responsables y seguimiento. Sabés quién tiene que hacer qué, no solo en qué área está el expediente. [Ver la guía](usuarios/expedientes/detalle-expediente.md)

## 5 de junio de 2026: Responsables, favoritos y mejoras de administración

Junio 2026: responsables asignados a cada expediente, expedientes favoritos y una administración más completa de reparticiones y usuarios. [Leer la nota en el blog](https://gdilatam.com/novedades/2026-06-responsables-favoritos-administracion).

- **Asigná responsables a cada expediente** (Nueva funcionalidad). Podés asignar uno o varios responsables a un expediente. Cada movimiento queda registrado con nombre, foto y sector, así sabés quién tiene qué en todo momento. [Ver la guía](usuarios/expedientes/panel.md)
- **Marcá expedientes como favoritos** (Nueva funcionalidad). Poné una estrella en los expedientes que seguís de cerca y tenelos siempre a mano. [Ver la guía](usuarios/expedientes/index.md)
- **Mejoras en Administración** (Administración). Transferencia de reparticiones y gestión de nombres, jerarquías y colores. Gestión de usuarios completa, con exportaciones y auditoría detallada. [Ver la guía](administradores/organigrama.md)

