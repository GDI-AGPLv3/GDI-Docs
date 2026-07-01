# Notas

Las **Notas** son un tipo especial de documento que funciona como memorandos o comunicaciones internas oficiales entre sectores del organismo. A diferencia de otros documentos, las notas incluyen **destinatarios** (sectores) y un sistema de **tracking de aperturas** que permite al remitente saber quien leyo la comunicacion.

!!! video "Video tutorial"
    **GDI — Panel CCOO: gestion de Notas y Memos**

    <div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/lWYjNqkUO78?list=PLRIZqApsdJ12JCSzhUxaZ73AheVHUEpDq" title="GDI — Panel CCOO: gestion de Notas y Memos" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>



---

## Que es una Nota

Una nota es un documento oficial con las siguientes particularidades:

| Caracteristica | Descripcion |
|----------------|-------------|
| **Destinatarios** | Sectores del organismo a los que se dirige la comunicacion, en modalidades Para, CC y CCO |
| **Proceso de firma** | Pasa por el mismo proceso de firma que cualquier otro documento |
| **Envio automatico** | Al completarse la firma, el sistema envia la nota automaticamente a los sectores destinatarios |
| **Tracking de aperturas** | El remitente puede ver quien abrio la nota y cuando |
| **Numero oficial** | Recibe un numero con formato `NOTA-{ANO}-{SECUENCIAL}-{TENANT}-{DEPTO}` |

---

## Modalidades de destinatario

Al crear una nota se asignan destinatarios en tres modalidades:

| Modalidad | Descripcion | Obligatorio |
|-----------|-------------|:-----------:|
| **Para (TO)** | Sectores destinatarios principales de la comunicacion | Si (minimo 1) |
| **CC** | Sectores en copia. Reciben la nota para su conocimiento | No |
| **CCO (BCC)** | Sectores en copia oculta. Reciben la nota pero los demas destinatarios no pueden ver que la recibieron | No |

---

## Bandeja de Notas

![Comunicaciones Oficiales - Recibidos](../capturas/ccoo-recibidos.png)

La bandeja de notas organiza las comunicaciones en tres pestanas:

| Pestana | Contenido |
|---------|-----------|
| **Recibidas** | Notas dirigidas al sector del usuario (como Para o CC/CCO) |
| **Enviadas** | Notas creadas y firmadas por el sector del usuario |
| **Archivadas** | Notas que el usuario movio al archivo para mantener limpia la bandeja de recibidas |

---

## Flujo de una Nota

```
Crear documento tipo NOTA (con destinatarios Para/CC/CCO)
    |
    v
Editar contenido + asignar firmantes
    |
    v
Proceso de firma (igual que cualquier documento)
    |
    v
Firma completada -> Envio automatico a destinatarios
    |
    v
Nota aparece en bandeja "Recibidas" de los sectores destino
    |
    v
Remitente puede ver tracking de aperturas
```

---

## Crear una Nota

Para crear una nota, se utiliza el flujo de creacion de documentos seleccionando el tipo **NOTA**. Consultar la guia completa en [Crear y Editar Documento](../documentos/crear-editar-documento.md), prestando especial atencion a la seccion **Destinatarios (solo para tipo NOTA)**.

---

## Secciones de esta guia

| Pagina | Descripcion |
|--------|-------------|
| [Nota Enviada](nota-enviada.md) | Vista de una nota desde la perspectiva del remitente: PDF, destinatarios y tracking de aperturas |
| [Nota Recibida](nota-recibida.md) | Vista de una nota desde la perspectiva del receptor: PDF, destinatarios, resumen IA y boton archivar |
