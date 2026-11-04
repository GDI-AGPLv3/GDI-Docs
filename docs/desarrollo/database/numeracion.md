# Sistema de Numeración

El sistema genera números oficiales únicos para todos los documentos del sistema. Usa **advisory locks** de PostgreSQL para prevenir race conditions en entornos concurrentes.

## Formato del Número Oficial

```
{TIPO}-{ANIO}-{SECUENCIA:08d}-{MUNICIPIO}-{DEPARTAMENTO}
```

| Componente | Ejemplo | Origen |
|------------|---------|--------|
| TIPO | `IF`, `CAEX`, `PV` | Acrónimo del tipo de documento |
| ANIO | `2026` | Año actual |
| SECUENCIA | `00000001` | Secuencia global (8 dígitos, zero-padded) |
| MUNICIPIO | `TXST` | Acrónimo de la organización (de `public.municipalities`) |
| DEPARTAMENTO | `INTE` | Acrónimo del departamento del numerador |

**Ejemplos:**

```
IF-2026-00000001-TXST-INTE       -- Primer informe del anio
NOTA-2026-00000002-TXST-LEGAL    -- Segunda nota (secuencia global)
CAEX-2026-00000003-TXST-INNO     -- Caratula de expediente
PV-2026-00000004-TXST-INNO       -- Pase de expediente
RESOL-2026-00000005-TXST-HAC     -- Resolucion
```

## Secuencia Global

La secuencia es **global por año**: todos los tipos de documentos comparten la misma secuencia. Esto garantiza:

- No hay números duplicados entre tipos de documento
- Orden cronológico único entre todos los documentos de la organización
- Trazabilidad simple (el número más alto = último documento numerado)

La secuencia se resetea a 1 al cambiar de año.

## Advisory Lock

### Por qué Advisory Lock

PostgreSQL sequences (`nextval`) no sirven porque:

1. No se resetean por año automáticamente
2. Si una transacción hace rollback, el número se pierde (huecos permanentes)

El advisory lock permite:

- Serializar el acceso al SELECT MAX + INSERT
- Reutilizar números en caso de rollback (no hay huecos)
- Lock ultra corto (10-20ms)

### Lock IDs

| Lock ID | Uso | Donde se usa |
|---------|-----|--------------|
| `888888` | Numeración de documentos oficiales | `shared/numbering.py` |
| `999999` | Numeración de expedientes | `database.py` |

!!! warning "Lock IDs fijos"
    Los IDs `888888` y `999999` son arbitrarios pero deben ser únicos en todo el sistema. No cambiar sin verificar que no hay conflictos.

### Flujo de Numeración

```mermaid
sequenceDiagram
    participant S as Service (Backend)
    participant PG as PostgreSQL
    participant T as Tabla official_documents

    S->>PG: SELECT pg_advisory_xact_lock(888888)
    Note over PG: Lock adquirido (bloquea otros)

    S->>T: SELECT COALESCE(MAX(global_sequence), 0) + 1<br/>FROM official_documents<br/>WHERE year = 2026
    T-->>S: next_number = 42

    S->>S: Formatear: IF-2026-00000042-TXST-INTE

    Note over PG: Lock se libera al commit/rollback

    S->>T: INSERT INTO official_documents<br/>(..., global_sequence=42, ...)
    S->>PG: COMMIT
    Note over PG: Lock liberado
```

### Código (Python)

El módulo `shared/numbering.py` del Backend centraliza toda la lógica:

```python
# Lock ID unico para numeracion de documentos oficiales
OFFICIAL_DOCUMENTS_LOCK_ID = 888888

async def generate_official_number(
    document_type_acronym: str,
    user_id: str,
    year: int,
    connection=None,
    *,
    schema_name: str    # SIEMPRE keyword-only
) -> Tuple[str, str, int]:
    """
    Genera un numero oficial unico.

    Returns:
        (official_number, department_id, global_sequence)
    """
    cursor = connection.cursor()

    # Paso 1: Obtener datos del usuario
    # - city_acronym de public.municipalities
    # - dept_acronym del departamento del usuario
    cursor.execute("""
        SELECT acronym as city_acronym
        FROM public.municipalities
        WHERE schema_name = %s
    """, (schema_name,))
    city_acronym = cursor.fetchone()['city_acronym']

    cursor.execute("""
        SELECT d.acronym as dept_acronym, d.id as department_id
        FROM users u
        LEFT JOIN sectors s ON u.sector_id = s.id
        LEFT JOIN departments d ON s.department_id = d.id
        WHERE u.id = %s
    """, (user_id,))
    user_info = cursor.fetchone()

    # Paso 2: Advisory lock + generar numero
    cursor.execute(f"SELECT pg_advisory_xact_lock({OFFICIAL_DOCUMENTS_LOCK_ID})")

    cursor.execute("""
        SELECT COALESCE(MAX(global_sequence), 0) + 1 as next_number
        FROM official_documents
        WHERE year = %s AND global_sequence IS NOT NULL
    """, (year,))
    next_number = cursor.fetchone()['next_number']

    # Paso 3: Formatear
    official_number = (
        f"{document_type_acronym}-{year}-{next_number:08d}"
        f"-{city_acronym}-{dept_acronym}"
    )

    return official_number, department_id, next_number
```

!!! note "schema_name keyword-only"
    La función `generate_official_number` recibe `schema_name` después de `*`, lo que lo hace keyword-only. Siempre debe llamarse como `schema_name=schema_name`.

## Numeración de Expedientes

Los expedientes usan un sistema similar con el lock ID `999999`:

```
EE-{ANIO}-{SECUENCIA:06d}-{MUNICIPIO}-{DEPARTAMENTO}
```

**Ejemplo:** `EE-2026-000001-TXST-INTE`

La secuencia de expedientes es independiente de la de documentos oficiales.

```python
def get_next_case_sequence(year: int = None, *, schema_name: str) -> int:
    """Obtener siguiente numero secuencial para expedientes."""
    with get_db_connection(schema_name) as conn:
        with conn.cursor() as cursor:
            # Lock exclusivo para expedientes (ID diferente)
            cursor.execute("SELECT pg_advisory_xact_lock(999999)")

            cursor.execute("""
                SELECT COALESCE(MAX(
                    CAST(SUBSTRING(case_number FROM '\\d{4}-(\\d+)-') AS INTEGER)
                ), 0) + 1 as next_sequence
                FROM cases
                WHERE EXTRACT(YEAR FROM created_at) = %s
            """, (year,))
            result = cursor.fetchone()
            conn.commit()

            return result['next_sequence']
```

## Documentos Automáticos

Dos tipos de documentos se generan automáticamente y usan el mismo sistema de numeración:

| Tipo | Acrónimo | Cuando se genera | Generador |
|------|----------|------------------|-----------|
| Carátula | CAEX | Al crear un expediente | `services/cases/cover_creator.py` |
| Pase | PV | Al transferir un expediente | `services/cases/transfer_document_creator.py` |

Ambos llaman a `generate_official_number()` del módulo `shared/numbering.py`.

## Tabla Resumen

| Aspecto | Documentos Oficiales | Expedientes |
|---------|---------------------|-------------|
| Lock ID | 888888 | 999999 |
| Formato | `{TIPO}-{ANIO}-{SEQ:08d}-{MUNI}-{DEPT}` | `EE-{ANIO}-{SEQ:06d}-{MUNI}-{DEPT}` |
| Secuencia | Global por año (8 dígitos) | Global por año (6 dígitos) |
| Columna | `official_documents.global_sequence` | Extraida de `cases.case_number` |
| Módulo | `shared/numbering.py` | `database.py` |
| Tipo lock | `pg_advisory_xact_lock` | `pg_advisory_xact_lock` |
| Duración lock | ~10-20ms | ~10-20ms |
