# Estampado de documentos

El módulo `app/document_stamper.py` aplica sellos informativos en documentos PDF,
agregando número de documento, ciudad y fecha en la página indicada.

## Qué es el estampado

El estampado agrega información administrativa a un PDF **antes** de la firma.
Se aplica opcionalmente cuando se envían `document_number` y `city` al endpoint `/sign-pdf`.

```
+-------------------------------------+
| Ciudad Autonoma, 15 de enero de 2025|  <-- city + fecha (Y=770)
| IF-2025-00001234-MUNI               |  <-- document_number (Y=755)
|                                      |
|         Contenido del documento      |
|                                      |
+-------------------------------------+
```

## Posición del estampado

Los valores están fijados en `document_stamper.py` y alineados al template HTML de WeasyPrint
(`@page { size: A4; margin: 10mm }`).

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `DOC_NUMBER_X` | 28 | Coordenada X (~10 mm, margen izquierdo del template HTML) |
| `DOC_NUMBER_Y` | 755 | Número de documento (pts desde borde inferior, ~87 pts desde top A4) |
| `CITY_DATE_X` | 28 | Coordenada X |
| `CITY_DATE_Y` | 770 | Ciudad y fecha (pts desde borde inferior, ~72 pts desde top A4) |
| Pagesize | A4 (595x842 pts) | Páginas del overlay |
| Fuente | Helvetica 11pt | Fuente del estampado |

!!! note "Posición del sello"
    El parámetro `stamp_position` controla en que página se aplica el estampado:

    - `'first'` (default): Primera página del documento
    - `'last'`: Última página del documento

## Función principal: stamp_document

```python
def stamp_document(
    pdf_content: bytes,
    document_number: str,
    city: str = "Bogota",
    page_position: str = "first"
) -> bytes:
```

### Proceso

1. Leer el PDF original con `PdfReader`
2. Crear overlay con el estampado (`create_stamp_overlay`)
3. Determinar la página objetivo según `page_position`
4. Combinar overlay con la página correspondiente
5. Retornar el PDF estampado

```python
for i, page in enumerate(pdf_reader.pages):
    if page_position == "last":
        is_target = (i == total_pages - 1)
    else:  # "first" por defecto
        is_target = (i == 0)

    if is_target:
        page.merge_page(stamp_page)
    pdf_writer.add_page(page)
```

## Formato de fecha

La fecha se genera automáticamente en español:

```python
def format_date_spanish() -> str:
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    month_name = months[now.month - 1]
    return f"{now.day} de {month_name} de {now.year}"
```

**Ejemplo:** `15 de enero de 2025`

## Texto del sello

```python
def create_stamp_text(document_number: str, city: str) -> Tuple[str, str]:
    document_line = document_number
    city_date_line = f"{city}, {format_date_spanish()}"
    return document_line, city_date_line
```

**Ejemplo de salida:**

- Línea 1 (arriba): `Ciudad Autonoma, 15 de enero de 2025`
- Línea 2 (abajo): `IF-2025-00001234-MUNI`

## Creación del overlay

```python
def create_stamp_overlay(document_number: str, city: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)  # A4: 595x842 pts

    # X=28 ≈ 10mm (margen izquierdo del template HTML de WeasyPrint)
    DOC_NUMBER_X = 28
    DOC_NUMBER_Y = 755   # ~87 pts desde top
    CITY_DATE_X  = 28
    CITY_DATE_Y  = 770   # ~72 pts desde top

    document_line, city_date_line = create_stamp_text(document_number, city)

    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(DOC_NUMBER_X, DOC_NUMBER_Y, document_line)
    c.drawString(CITY_DATE_X, CITY_DATE_Y, city_date_line)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
```

## Orden de operaciones en /sign-pdf

El estampado se aplica **antes** de la firma:

```mermaid
flowchart LR
    A[PDF original] --> B[Estampar]
    B --> C[Calcular posicion firma]
    C --> D[Firmar]
    D --> E[PDF final]
```

Esto es importante porque la firma PAdES protege la integridad del documento.
Si se estampará después de la firma, la firma quedaría invalidada.

## Excepciones

| Excepción | Causa |
|-----------|-------|
| `StampError` | Error al leer PDF o al aplicar el overlay |
