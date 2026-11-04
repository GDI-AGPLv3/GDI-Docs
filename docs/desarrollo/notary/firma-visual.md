# Firma Visual

El módulo `app/signature_inserter.py` implementa la firma visual de documentos PDF
usando **ReportLab** para generar el overlay y **pypdf** (>=4) para combinarlo con el PDF original.

!!! info "Uso actual"
    La firma visual se usa como fallback en ambiente `test` cuando no hay
    certificado disponible. En producción, se usa la firma combinada PAdES + visual.

## Diseño de la firma

```
+-------------------------------------------+
| Juan Perez                     (Bold 10pt) |
| Director                    (Regular 10pt) |
| Administracion              (Regular 10pt) |
| Municipalidad del Futuro    (Regular 10pt) |
|                                            |
| Digitally Signed by TEST SERVER | fecha  7pt |
+-------------------------------------------+
  200 pts ancho x 80 pts alto
```

- Rectángulo invisible (borde blanco)
- Nombre en negrita (Helvetica-Bold 10pt)
- Cargo, departamento, entidad en regular (Helvetica 10pt)
- Footer con identificador y fecha UTC (Helvetica 7pt)

## Función principal: sign_pdf_document

```python
def sign_pdf_document(
    pdf_content: bytes,
    signature_params: Dict[str, str],
    x: float,
    y: float
) -> bytes:
```

**Parámetros requeridos en `signature_params`:**

| Clave | Descripción |
|-------|-------------|
| `name` | Nombre del firmante |
| `seal` | Cargo o sello |
| `department` | Departamento |
| `entity` | Entidad |

### Proceso

1. Validar que todos los parámetros requeridos estén presentes
2. Leer el PDF original con `PdfReader`
3. Crear overlay con la firma visual
4. Combinar overlay con la **última página** del PDF
5. Retornar el PDF resultante

```python
# Solo firma la ultima pagina
for page_num, page in enumerate(pdf_reader.pages):
    if page_num == len(pdf_reader.pages) - 1:
        page.merge_page(signature_overlay)
    pdf_writer.add_page(page)
```

## Creación del overlay

```python
def create_signature_overlay(signature_params: Dict, x: float, y: float):
    overlay_buffer = io.BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=A4)

    # Rectangulo invisible
    c.setStrokeColor(white)
    c.setLineWidth(0.5)
    c.rect(x, y, SIGNATURE_WIDTH, SIGNATURE_HEIGHT)

    # Nombre (Bold)
    text_y = y + SIGNATURE_HEIGHT - 15
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 5, text_y, signature_params["name"])

    # Cargo, departamento, entidad (Regular)
    text_y -= 12
    c.setFont("Helvetica", 10)
    c.drawString(x + 5, text_y, signature_params["seal"])

    text_y -= 11
    c.drawString(x + 5, text_y, signature_params["department"])

    text_y -= 11
    c.drawString(x + 5, text_y, signature_params["entity"])

    # Footer
    text_y -= 14
    c.setFont("Helvetica", 7)
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    footer_text = f"Digitally Signed by TEST SERVER | {current_time}"
    c.drawString(x + 5, text_y, footer_text)

    c.save()
    overlay_buffer.seek(0)
    overlay_reader = PdfReader(overlay_buffer)
    return overlay_reader.pages[0]
```

## Diferencias con firma PAdES

| Aspecto | Firma Visual | Firma PAdES |
|---------|-------------|-------------|
| Criptografía | No | Sí (SHA256 + certificado) |
| Verificable en Adobe | No | Sí (clic en la firma) |
| Timestamp | Solo visual | TSA criptográfico (con reintentos + circuit breaker) |
| Footer | "Digitally Signed by TEST SERVER" | Sin footer (datos en metadatos) |
| Nombre | Normal | MAYUSCULAS |
| Fecha visible | Sí (en footer) | No (en metadatos) |
| Librería | ReportLab + pypdf | pyHanko |

## Excepciones

| Excepción | Causa |
|-----------|-------|
| `SignatureError` | Parámetro faltante o error al procesar PDF |
