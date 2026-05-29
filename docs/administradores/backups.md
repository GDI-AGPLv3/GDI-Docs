# Backups (GDI Sync)

Descarga y manten una copia local, siempre actualizada, de todos los datos y documentos de tu municipio.

---

## Descripcion General

**GDI Sync** es una herramienta que le permite a cada municipio tener una copia propia de su informacion, fuera de GDI Latam. Es el principio de **soberania de datos**: la informacion es del municipio, y el municipio puede tenerla en su poder cuando quiera.

| Beneficio | Que significa |
|-----------|---------------|
| **Soberania de datos** | El municipio manda sobre su informacion. No depende de nadie para tenerla. |
| **Incremental** | Solo descarga lo que cambio desde la ultima vez. Rapido y eficiente. |
| **Original garantizado** | Los PDF firmados se descargan tal cual fueron emitidos. |
| **Sin dependencias** | Es un script Python que corre en Windows, Mac y Linux. No instala nada raro. |

La copia queda en una base de datos **SQLite** (`backup.db`) mas una carpeta con los **PDF firmados** (`pdfs/`). Se puede abrir con cualquier herramienta de SQLite, Excel o un script de analisis.

---

## Como funciona

```
Tu maquina (script Python)  --->  Gateway de tu municipio  --->  Base de datos GDI
   sync.py + API Key                (HTTPS, solo lectura)
        |
        v
   backup.db (SQLite) + pdfs/
```

El script se conecta al Gateway de tu municipio con una **API Key de backup**, descarga lo que cambio desde la ultima corrida y lo guarda localmente. Es de **solo lectura**: nunca modifica datos en GDI.

---

## Activacion (una sola vez)

### Paso 1 — Solicitar la API Key

Para activar Sync necesitas una **API Key de backup**, distinta de las claves de API comunes. La genera GDI Latam y se entrega de forma segura.

Solicitala por mail a **info@gdilatam.com** con el asunto *"Solicitud API Key Sync"*, indicando tu municipio. Te van a enviar:

- La **API Key** (empieza con `bk-gdi-sync-...`)
- La **URL del Gateway** de tu municipio (por ejemplo `https://tu-municipio-gateway.gdilatam.com`)

!!! tip "Tambien desde el BackOffice"
    En el BackOffice, en la seccion **Sync**, encontras el boton para solicitar la activacion y el enlace de descarga del cliente.

### Paso 2 — Descargar el cliente

Desde la seccion **Sync** del BackOffice, descarga el archivo **`gdi-sync.zip`** y descomprimilo en una carpeta de tu maquina.

Necesitas tener **Python 3.8 o superior** instalado. No requiere instalar ninguna libreria adicional.

### Paso 3 — Configurar las credenciales

Dentro de la carpeta, copia el archivo `config.example.env` a un nuevo archivo llamado **`.env`** y completalo con los datos que te entrego GDI Latam:

```bash
GDI_API_KEY=bk-gdi-sync-xxxxxxxxxxxxxxxxxxxx
GDI_GATEWAY_URL=https://tu-municipio-gateway.gdilatam.com
```

Opcionalmente podes cambiar donde se guarda la copia:

```bash
# GDI_DB_PATH=backup.db   # archivo SQLite (default: backup.db)
# GDI_PDF_DIR=pdfs        # carpeta de PDF (default: pdfs)
```

!!! warning "Cuida tu API Key"
    La API Key da acceso de lectura a toda la informacion de tu municipio. Tratala como una contrasena: no la compartas ni la subas a repositorios publicos.

---

## Uso cotidiano

**Una vez configurado, cada vez que quieras actualizar tu copia, abri una terminal en la carpeta del cliente y ejecuta el script.** Eso es todo.

=== "Sync incremental (lo normal)"

    ```bash
    python sync.py
    ```

    Descarga **solo lo que cambio** desde la ultima vez. Es lo que vas a usar el 99% de las veces. Rapido, aunque tengas miles de documentos.

=== "Descarga completa"

    ```bash
    python sync.py --full
    ```

    Vuelve a descargar **todo desde cero**, ignorando lo que ya tenias. Util la primera vez, o si queres regenerar la copia.

=== "Incluir los PDF firmados"

    ```bash
    python sync.py --pdfs
    ```

    Ademas de los datos, descarga los **PDF de los documentos firmados** a la carpeta `pdfs/`. Los archivos que ya tenes no se vuelven a bajar.

=== "Todo desde cero + PDF"

    ```bash
    python sync.py --full --pdfs
    ```

    Combinacion completa: regenera la base y baja todos los PDF.

### Que vas a ver

```
GDI Sync System
  Gateway : https://tu-municipio-gateway.gdilatam.com
  DB      : backup.db
  Modo    : INCREMENTAL

  Tenant  : 101_municipio
  Tablas  : 33

  OK   cases                                      +12 nuevas
  OK   official_documents                         +47 nuevas
  OK   users                                      sin cambios
  ...

  Total: 59 filas nuevas/actualizadas.
```

La **primera corrida** descarga todo (puede tardar varios minutos segun el volumen). Las **siguientes** son casi instantaneas porque solo traen lo nuevo.

---

## Que obtenes

| Resultado | Descripcion |
|-----------|-------------|
| **`backup.db`** | Base de datos SQLite con todas las tablas de tu municipio (usuarios, expedientes, documentos, notas, legajos, etc). |
| **`pdfs/`** | Carpeta con los PDF de los documentos firmados (solo si usaste `--pdfs`). El nombre de cada archivo es su numero oficial. |

Para abrir `backup.db` podes usar herramientas gratuitas:

- [DB Browser for SQLite](https://sqlitebrowser.org/) — Windows, Mac y Linux
- [DBeaver](https://dbeaver.io/) — multiplataforma
- Tambien desde Excel, Python, o cualquier herramienta de analisis de datos

---

## Que se sincroniza

La copia incluye **33 tablas** con toda la informacion operativa del municipio:

| Grupo | Contenido |
|-------|-----------|
| **Estructura** | Reparticiones, sectores, rangos, sellos |
| **Usuarios** | Usuarios, roles, sellos asignados, permisos de sector, estados |
| **Documentos** | Documentos oficiales, firmantes, rechazos |
| **Tipos** | Tipos de documento y sus habilitaciones por sector y rango |
| **Expedientes** | Expedientes, movimientos, templates, documentos vinculados, responsables, favoritos |
| **Notas y Memos** | Destinatarios, aperturas, memos |
| **Legajos (RLM)** | Familias de registro, permisos, registros, historial, relaciones y vinculos |

!!! note "Datos sensibles protegidos"
    De la tabla de usuarios solo se exporta informacion segura (nombre, email, sector). **Nunca** se descargan contrasenas, tokens ni credenciales de acceso.

    Los documentos con numero **reservado pero no firmado** o **cancelados** no se incluyen: solo se copian documentos oficiales validos.

---

## Automatizar (opcional)

Podes programar el sync para que corra solo, por ejemplo una vez por dia o por hora.

=== "Windows (Programador de tareas)"

    1. Abri el **Programador de tareas**
    2. **Crear tarea basica**
    3. Accion: iniciar un programa → `python`
    4. Argumentos: `C:\ruta\gdi-sync\sync.py`
    5. Disparador: diario o cada X horas

=== "Linux / Mac (cron)"

    Para correr cada hora:

    ```bash
    0 * * * * cd /ruta/gdi-sync && python sync.py >> sync.log 2>&1
    ```

---

## Preguntas frecuentes

??? question "Si corro el sync dos veces seguidas, se duplican los datos?"
    No. El sync actualiza los registros existentes y agrega solo los nuevos. Podes correrlo cuantas veces quieras.

??? question "Cada cuanto deberia correrlo?"
    Depende de cuan actualizada quieras tu copia. Para la mayoria de los municipios, una vez por dia es suficiente. Si necesitas algo mas fresco, podes automatizarlo cada hora.

??? question "Que pasa si pierdo la conexion a mitad de la descarga?"
    No pasa nada: la proxima vez que corras el script retoma desde donde quedo. El sync es incremental y seguro de reintentar.

??? question "Puedo mover la copia a otra carpeta o disco?"
    Si. El archivo `backup.db` y la carpeta `pdfs/` son autocontenidos. Podes copiarlos, moverlos o respaldarlos donde quieras.

??? question "La API Key se vence?"
    La API Key puede tener fecha de vencimiento segun como se configure. Si deja de funcionar, escribi a info@gdilatam.com para renovarla.
