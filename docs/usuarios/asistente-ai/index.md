# Asistente AI

El Asistente AI es una herramienta integrada en GDI que permite consultar informacion sobre expedientes y documentos usando **lenguaje natural**. Esta disponible dentro de cada expediente para consultar su contenido.

---

## Asistente en el Expediente

Dentro de la vista de detalle de un expediente, el tab **"Tu Asistente"** abre un chat integrado que permite hacer preguntas sobre ese expediente especifico.

![Asistente en expediente](../capturas/asistente-expediente.png)

### Como usarlo

1. Abrir un expediente desde la seccion Expedientes.
2. Hacer click en el tab **"Tu Asistente"**.
3. Si el expediente tiene un **resumen generado por IA**, el asistente lo muestra automaticamente al abrir el chat.
4. Escribir una pregunta en el campo de texto inferior o usar los **chips rapidos**.
5. El asistente responde con informacion del expediente.

---

### Chips rapidos

Los chips rapidos son botones de acceso directo que aparecen debajo del chat. Permiten hacer consultas frecuentes con un solo click.

| Chip | Que hace |
|------|----------|
| **Quienes participaron** | Lista los usuarios que intervinieron en el expediente |
| **Paso a Paso** | Describe la secuencia de movimientos y acciones del expediente en orden cronologico |
| **Que falta?** | Analiza la documentacion del expediente e indica si falta algun documento o paso pendiente |

---

### Campo de texto libre

Ademas de los chips rapidos, se puede escribir cualquier pregunta en el campo de texto con el placeholder *"En que te puedo ayudar?"*. El asistente interpreta la pregunta y responde con informacion del expediente.

Ejemplos de preguntas que se pueden hacer:

| Pregunta | Tipo de respuesta |
|----------|-------------------|
| *"Quien creo este expediente?"* | Nombre del creador y fecha |
| *"Que documentos tiene vinculados?"* | Lista de documentos con tipo, referencia y estado |
| *"Cual fue el ultimo movimiento?"* | Descripcion del ultimo movimiento con fecha y sector |
| *"Resume el expediente en 3 lineas"* | Resumen breve generado por IA |

!!! tip "Resumen previo del expediente"
    Si el expediente ya tiene un resumen IA generado, el asistente lo muestra automaticamente al abrir el chat. Este resumen es preparado en segundo plano por el sistema; no todos los expedientes lo tienen disponible desde el primer momento.

---

## Preguntas frecuentes

??? question "El asistente puede modificar documentos o expedientes?"
    No. El asistente es de **solo lectura**. Puede consultar informacion, generar resumenes y responder preguntas, pero no puede crear, editar ni firmar documentos.

??? question "Puedo usar el asistente del expediente sin conexion?"
    No. El asistente requiere conexion a internet para funcionar, ya que procesa las consultas en tiempo real.

??? question "Por que a veces el asistente tarda en responder?"
    El servicio de IA puede tardar unos segundos en activarse si estuvo inactivo. Una vez que responde la primera consulta, las siguientes son mas rapidas.
