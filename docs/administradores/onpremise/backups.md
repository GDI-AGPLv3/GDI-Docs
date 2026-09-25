# Copias de seguridad del servidor propio

Guía para el **técnico del municipio** que tiene GDI instalado en su propio servidor. (Si el
municipio usa GDI en la nube, la copia propia se hace con [GDI Sync](../backups.md).)

!!! danger "La copia va FUERA del servidor"
    Una copia guardada en el mismo disco no protege de nada: si se rompe el disco, se borra un
    volumen o se pierde la máquina, la copia se pierde con ella. Por eso GDI **no trae** un
    backup automático al mismo servidor: el destino y la frecuencia los decide el municipio.

---

## Qué hay que respaldar

Un servidor perdido se recupera con estas cinco cosas:

| Qué | Dónde está en el servidor | Sin esto… |
|---|---|---|
| **Base de datos** | contenedor `postgres` (se saca con `pg_dump`) | no hay nada |
| **Documentos** (PDF firmados, logos, certificados) | volumen `gdi_storage_data` → `/var/lib/docker/volumes/gdi_storage_data/_data` | la base apunta a archivos que no existen |
| **Configuración** | `/opt/gdi/.env` (y `/opt/gdi/npm-admin.txt`) | el sistema no levanta: claves, login, `CERT_MASTER_KEY` |
| **Licencia** | `/opt/gdi/license/` | arranca sin BackOffice ni IA hasta reactivar |
| **Imágenes** de la versión instalada | el registro de GDI, o una copia local | sin token activo no se puede reinstalar |

!!! tip "Los documentos son archivos comunes"
    Cada documento es un archivo PDF normal dentro de `data/<bucket>/<ruta>`, y sus datos (tipo de
    archivo, dueño, lectura pública) van al lado, en `meta/`. Cualquier herramienta de copia de
    archivos los respalda completos: no hace falta nada especial.

Si el nombre del volumen no coincide (depende de la carpeta donde se instaló), confirmalo con:

```bash
docker volume ls | grep storage_data
```

!!! warning "El .env y la licencia son secretos"
    Contienen las claves del sistema. El destino de la copia tiene que ser tan seguro como una
    contraseña, o la copia tiene que ir cifrada (el ejemplo de abajo la cifra).

---

## Dónde guardarla

Cualquier lugar **fuera** del servidor sirve. Lo habitual en un municipio:

| Destino | Ejemplo |
|---|---|
| **NAS u otro servidor** del municipio | acceso por SFTP (SSH) |
| **Disco externo** conectado al servidor | se monta, se copia y se desconecta |
| **Almacenamiento en la nube** compatible con S3 | Backblaze B2, Wasabi, el de un proveedor local |
| **La herramienta de backup que ya usa el municipio** | Veeam, Bacula, etc.: que copie lo de la tabla de arriba |

**Recomendado:** una copia **diaria**, conservar al menos **7 diarias, 4 semanales y 12 mensuales**,
y **probar una restauración** en otra máquina cada tanto. Una copia que nunca se restauró no está
probada.

---

## Ejemplo completo: copia diaria con restic

[restic](https://restic.net/) es una herramienta libre de copias de seguridad: **incremental**
(después de la primera, solo copia lo nuevo), **cifrada** y con retención automática. Funciona con
todos los destinos de la tabla anterior.

### 1. Instalar y configurar (una sola vez)

```bash
sudo apt-get install -y restic
sudo install -m 600 /dev/null /root/gdi-backup.env
sudo nano /root/gdi-backup.env
```

Contenido de `/root/gdi-backup.env` (elegí **una** línea de `RESTIC_REPOSITORY`):

```bash
# Destino de la copia
RESTIC_REPOSITORY=sftp:backup@nas.municipio.local:/respaldos/gdi      # NAS u otro servidor (SSH)
# RESTIC_REPOSITORY=/mnt/disco-externo/gdi                             # disco externo montado
# RESTIC_REPOSITORY=s3:https://s3.proveedor.com/respaldos-gdi          # nube compatible con S3
# AWS_ACCESS_KEY_ID=...                                                # solo para S3
# AWS_SECRET_ACCESS_KEY=...                                            # solo para S3

# Contraseña de cifrado de la copia
RESTIC_PASSWORD_FILE=/root/.gdi-backup-pass
```

```bash
sudo sh -c 'openssl rand -hex 32 > /root/.gdi-backup-pass && chmod 600 /root/.gdi-backup-pass'
sudo sh -c 'set -a; . /root/gdi-backup.env; restic init'
```

!!! danger "Guardá la contraseña de cifrado FUERA del servidor"
    Sin `/root/.gdi-backup-pass` la copia **no se puede abrir**, ni siquiera por GDI Latam.
    Guardala en el gestor de contraseñas del municipio.

### 2. El script de copia

`/usr/local/sbin/gdi-backup.sh`:

```bash
#!/usr/bin/env bash
# Copia diaria de GDI: base + documentos + configuración, cifrada y fuera del servidor.
set -euo pipefail
set -a; . /root/gdi-backup.env; set +a

cd /opt/gdi
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.premium.yml -f docker-compose.storage.yml"
DUMP=$(mktemp /var/tmp/gdi-XXXXXX.dump)
trap 'rm -f "$DUMP"' EXIT

# 1. Base de datos. Se valida ANTES de guardarla: un dump cortado no es una copia.
$COMPOSE exec -T postgres pg_dump -U postgres railway -Fc > "$DUMP"
$COMPOSE exec -T postgres pg_restore -l < "$DUMP" > /dev/null
restic backup "$DUMP" --tag base

# 2. Documentos (el volumen completo: datos, metadatos y cuentas del almacenamiento)
restic backup /var/lib/docker/volumes/gdi_storage_data/_data --tag documentos

# 3. Configuración y licencia
restic backup /opt/gdi/.env /opt/gdi/license $( [ -f /opt/gdi/npm-admin.txt ] && echo /opt/gdi/npm-admin.txt ) --tag config

# 4. Retención: 7 diarias, 4 semanales, 12 mensuales
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune

echo "$(date -Is) copia OK"
```

```bash
sudo chmod 700 /usr/local/sbin/gdi-backup.sh
sudo /usr/local/sbin/gdi-backup.sh          # la primera corrida copia todo y tarda más
```

### 3. Programarla

```bash
sudo crontab -e
```

```cron
0 3 * * * /usr/local/sbin/gdi-backup.sh >> /var/log/gdi-backup.log 2>&1
```

!!! warning "Una copia automática que falla no avisa"
    Revisá `/var/log/gdi-backup.log` cada tanto: la última línea tiene que ser `copia OK` con la
    fecha de hoy. Para ver lo guardado: `sudo sh -c 'set -a; . /root/gdi-backup.env; restic snapshots'`.

---

## Restaurar

Con GDI instalado (o reinstalado con el [manual](manual.md) hasta el paso 7) y el mismo
`/root/gdi-backup.env` y contraseña de cifrado:

```bash
sudo -i
set -a; . /root/gdi-backup.env; set +a
cd /opt/gdi
gdi() { ( cd /opt/gdi && docker compose -f docker-compose.yml -f docker-compose.premium.yml -f docker-compose.storage.yml "$@" ); }

restic snapshots                                   # elegir la fecha (o usar "latest")

# 1. Configuración y licencia
restic restore latest --tag config --target /
chown -R 999:999 /opt/gdi/license && chmod 644 /opt/gdi/license/*.lic

# 2. Documentos (con el almacenamiento detenido)
gdi stop storage
restic restore latest --tag documentos --target /
gdi start storage

# 3. Base de datos
restic restore latest --tag base --target /var/tmp/restaurar
gdi exec -T postgres pg_restore -U postgres -d railway --clean --if-exists < "$(find /var/tmp/restaurar -name 'gdi-*.dump' | head -1)"

gdi up -d
```

**Verificar:** entrar al portal, abrir un expediente y un documento firmado. Si el PDF abre, la base
y los documentos quedaron alineados.

!!! tip "Probalo antes de necesitarlo"
    La mejor forma de saber que la copia sirve es restaurarla en **otra** máquina (una virtual
    alcanza) una vez cada tanto, siguiendo estos mismos pasos.
