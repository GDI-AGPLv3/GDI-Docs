# Impresora GDI

La **Impresora GDI** sirve para mandar a GDI lo que sale de cualquier programa de la PC. Es útil con los programas que no guardan archivos y solo imprimen, como muchos sistemas contables.

Imprimís en la impresora **«GDI - <usuario>»** y se abre GDI con el PDF a la vista. Elegís el tipo, escribís la referencia, elegís el expediente y firmás. El documento queda firmado y vinculado al expediente, en un solo paso.

!!! example "Ejemplo"
    En la **Municipalidad del Futuro**, Ana López, de Contaduría, imprime la Orden de Pago 0001 desde el sistema contable en la impresora GDI. Se abre el navegador con el PDF. Elige el tipo de documento, escribe la referencia y toca el expediente `EX-2026-00123-MUNDEV`. Firma. Termina en ese expediente, con la orden ya vinculada.

---

## Instalar el programa

La impresora funciona con un programa chico para Windows 10 y 11: **GDI Connection**.

- Lo instala **Sistemas del municipio**. Hace falta permiso de administrador **una sola vez por PC**.
- Al instalarlo, se elige a qué GDI se conecta la PC.
- Cada usuario de Windows tiene **su propia impresora**: «GDI - <usuario>». Solo esa persona puede imprimir en ella y solo ella recibe sus impresiones.
- El programa arranca solo al iniciar sesión en Windows. Queda como un ícono al lado del reloj.
- El programa **no guarda tu usuario ni tu clave de GDI**. El documento se crea con la sesión que tenés abierta en el navegador.

!!! warning "La primera vez, el navegador pide permiso"
    La primera vez en cada PC, el navegador pregunta si permitís que el sitio acceda a los dispositivos de tu red local. Tocá **Permitir**. No vuelve a preguntar.

    Sistemas del municipio puede dejarlo aprobado de antemano para todas las PC.

---

## Imprimir en GDI

1. En tu programa, elegí **Imprimir**.
2. Elegí la impresora **«GDI - <usuario>»**, con tu usuario de Windows.
3. Imprimí. No aparece «Guardar como».
4. Se abre el navegador en la pantalla **Importando desde PC**, con el PDF a la izquierda.

Si no tenías la sesión abierta, primero entrás con tu usuario de siempre. Después volvés solo a la pantalla, con el PDF.

---

## Pantalla «Importando desde PC»

A la izquierda está el PDF. A la derecha, 3 datos. Los 3 son obligatorios.

| Dato | Qué hacés |
|------|-----------|
| **Tipo de documento** | Escribís o elegís el tipo. Solo aparecen los tipos de documento **importado** que **vos podés numerar** |
| **Referencia** | Escribís de qué trata el documento |
| **Vincular a** | Buscás el expediente por número o motivo, o tocás uno de los sugeridos |

En **Vincular a** solo aparecen los expedientes **donde podés vincular documentos**: los que administra o tiene asignados uno de tus sectores. Primero salen aquellos donde sos responsable.

Abajo hay 2 botones:

- **Cancelar:** no se crea nada en GDI.
- **Firmar y vincular:** se habilita con los 3 datos completos.

---

## Firmar y vincular

Al tocar **Firmar y vincular**, GDI hace todo solo: crea el documento, sube el PDF, lo manda a firma y lo firma.

- **Firmás solo vos.** No hay otros firmantes ni se comparte.
- La firma es la que pide el tipo de documento: firma electrónica o firma con token (ver [Firmar con Token](firmar-con-token.md)).
- Al terminar, se abre el **expediente** que elegiste, en la solapa de documentos, con el documento nuevo a la vista.

!!! info "Firmado, pero no vinculado"
    Es raro, pero puede pasar que no se pueda vincular. Por ejemplo, si entre que elegiste el expediente y firmaste te sacaron la asignación. En ese caso el documento queda **firmado** y **propuesto** al expediente. La pantalla te lo avisa y no te lleva al expediente.

!!! tip "Si algo falla antes de firmar"
    El borrador queda en **Mis documentos**, como cualquier documento importado. Tocá **Reintentar**: GDI sigue desde donde quedó y no crea otro borrador.

---

## Avisos que podés ver

| Aviso | Qué hacer |
|-------|-----------|
| **Esta impresión ya se usó o venció** | Cada impresión se abre una sola vez. Abrila de nuevo desde el ícono de GDI Connection, al lado del reloj de Windows, o volvé a imprimir |
| **El programa GDI Connection no responde** | Fijate que el ícono de GDI Connection esté al lado del reloj. Si no está, abrí el programa desde el menú Inicio y volvé a imprimir |
| **El navegador no deja leer la impresión** | El sitio tiene bloqueado el acceso a la red local. Entrá a la configuración del sitio (el ícono a la izquierda de la dirección), poné **Acceso a la red local** en **Permitir** y tocá **Reintentar** |
| **No hay ninguna impresión para cargar** | La pantalla se abre sola cuando imprimís en la impresora GDI. Volvé a imprimir desde tu programa |
| **Lo que llegó no es un PDF** | Volvé a imprimir. Si se repite, avisale a Sistemas |

Si la impresora no anda, siempre podés seguir por el camino de siempre: guardar el PDF y [crear el documento importado a mano](documento-importado.md).

---

## Preguntas frecuentes

??? question "¿A nombre de quién queda el documento?"
    A nombre de la persona que tiene la sesión abierta en el navegador. El programa de la PC no sabe tu usuario de GDI.

??? question "No me aparece el tipo de documento que quiero."
    Solo aparecen los tipos de documento importado que podés numerar. Si te falta uno, pedíselo al administrador de tu municipio.

??? question "No me aparece el expediente."
    Solo aparecen los expedientes donde podés vincular documentos. Un expediente cerrado o que todavía espera su carátula no aparece.

??? question "¿Qué controles tiene el PDF?"
    Los mismos que un PDF que subís desde la web. Ver [Documento Importado (PDF)](documento-importado.md).
