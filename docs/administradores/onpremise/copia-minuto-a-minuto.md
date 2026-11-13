# Copia de la base minuto a minuto

Con el backup diario, si algo se rompe a las 18:00 se pierde el trabajo del día. Con la copia minuto a minuto
se pierde **como mucho 1 minuto**, y además se puede **volver a cualquier minuto** de los últimos días.

**Cómo funciona, con un ejemplo.** Postgres, antes de cambiar un dato, lo anota en un cuaderno (el WAL). La
copia completa es una foto; el WAL es la película de lo que pasó después. Con la foto de anoche y la película
se arma la base como estaba en cualquier minuto. ¿Alguien borró algo a las 14:37? Se arma la base de las 14:36.

La herramienta es **pgBackRest**, que ya viene en la imagen de postgres. Sube:

| Qué | Cada cuánto | Cuánto atrás |
|---|---|---|
| El WAL (cada cambio) | Cada **50 s** como máximo (la pérdida máxima queda en ~1 minuto) | `PITR_RETENCION_DIAS` (default 3 días = 72 h) |
| Una copia completa | 1 por día (`PITR_HORA_COMPLETA`, default 04:00) | Se borra cuando las más nuevas ya cubren los días pedidos: con 3 días pueden quedar hasta 4 copias (96 h) |

Todo sale **cifrado** con `PITR_CIFRADO`. **Si esa clave se pierde, las copias no sirven**: guardala también en papel.

Viene **apagada**. Es opcional y se prende en el `.env`.

Esta copia **no reemplaza** al [backup diario](backups.md): son dos copias con dos herramientas distintas, a propósito. Si una
falla, queda la otra.

## Prenderla

1. Un bucket S3 (de cualquier proveedor S3 compatible, o uno propio) y una clave con permiso **solo** sobre ese bucket.
2. En el `.env`: `BACKUP_PITR=on` y las variables `PITR_*` (están explicadas en `.env.example`). La clave de
   cifrado se genera con `openssl rand -base64 48`.
3. Correr el instalador como siempre (`./scripts/instalar-desatendido.sh ...`, [Anexo B del manual](manual.md#anexo-b-instalacion-desatendida-sin-preguntas)). Con `BACKUP_PITR=on`:
   - suma `docker-compose.backup.yml` (las variables `PGBACKREST_*` del contenedor de postgres);
   - antes de arrancar la base, prueba que la imagen traiga pgBackRest y que el destino conteste;
   - prende el WAL continuo (va en el `command:` del agregado; la primera vez se recrea el contenedor de la base, unos segundos);
   - crea el destino (`pgbackrest stanza-create`) y prueba que el WAL llegue (`pgbackrest check`). Si algo de esto
     falla, vuelve atrás (la base queda sin subir WAL) y corta;
   - si el destino está vacío, saca la primera copia completa;
   - instala 2 timers de systemd (hace falta root): la copia completa diaria y el control cada 5 min.

Si una carpeta del bucket (`PITR_S3_PREFIX`) ya tiene copias de **otra** base (por ejemplo, de un servidor
anterior), el instalador corta: no las pisa. Se usa otra carpeta (por ejemplo `pitr/municipio-20261023`).

Para apagarla: `BACKUP_PITR` vacío y correr el instalador. La base deja de subir WAL y se quitan los timers. Las
copias que ya están en el bucket no se borran.

## Ver que anda

```bash
./scripts/backup-pitr.sh info                    # copias completas y WAL que hay en el destino
./scripts/backup-pitr.sh control                 # el mismo control que corre cada 5 min
systemctl list-timers 'gdi-pitr-*'               # cuándo corren las tareas
journalctl -u gdi-pitr-completa-gdi -n 50        # cómo salió la última copia completa
```

## Avisos (opcionales)

Con `HC_PING_PITR_FULL` y `HC_PING_PITR_WAL` (dos chequeos de healthchecks.io) llega un aviso si:

- la copia completa del día falla o no corre;
- hay WAL esperando subir hace más de 5 min (el destino no responde o lo rechaza);
- pgBackRest falló al subir en los últimos 10 min;
- se descartó WAL por la cola llena (ver abajo);
- no se puede leer el destino;
- el disco de la base pasa `PITR_DISCO_MAX` % (default 80 %);
- el control no corre (el servidor está apagado o el timer se cayó).

## El riesgo principal, y cómo se cubre

Si la subida se traba y nadie se entera, el WAL se junta en el disco y, si lo llena, **Postgres se frena**. Se
cubre con 3 cosas a la vez:

1. **Tope de la cola** (`PITR_COLA_MAX`, default 4 GiB): si el destino no responde por horas, pgBackRest
   **descarta** WAL antes de llenar el disco. Se pierde el minuto a minuto de ese lapso, pero la base sigue
   andando. Al volver el destino, conviene sacar una copia completa a mano (`./scripts/backup-pitr.sh completa`).
2. **Control cada 5 min**, con aviso.
3. **Aviso de disco** al 80 %.

La subida es asincrónica: un destino lento no hace esperar a la base.

## Volver a un minuto

```bash
./scripts/volver-a-un-minuto.sh "2026-10-23 14:36"
```

Arma la base como estaba en ese minuto (hora de `PITR_ZONA`, default Argentina) **al costado**: otro
contenedor (`gdi-al-costado`), otro volumen y el puerto `127.0.0.1:5439`. **Producción no se toca.** La base
de al costado no sube WAL. Tarda lo que tarda bajar la copia completa más el WAL de ese día (con una base de
~1 GB, unos minutos).

De ahí se sacan los datos borrados y se cargan en producción a mano:

```bash
docker exec -it -u postgres gdi-al-costado psql -U <DB_USER> -d <DB_NAME>           # mirar
docker exec -u postgres gdi-al-costado pg_dump -U <DB_USER> -d <DB_NAME> -Fc \
  -t '<schema>.<tabla>' > tabla.dump                                                  # sacar una tabla
./scripts/volver-a-un-minuto.sh --borrar                                              # al terminar
```

**Por qué al costado y no encima de producción.** Si se pisa producción con la base de las 14:36, los PDF
firmados después ya están guardados con sus números, y la base vuelve a ofrecer esos mismos números: la firma
de ese tipo de documento se traba. Por eso producción se arregla cargando a mano solo lo que se perdió.

## Desastre total (se perdió el disco de la base)

Ahí sí se arma producción, pero **hasta el último minuto**, no a uno viejo:

```bash
CONFIRMAR=RESTAURAR ./scripts/volver-a-un-minuto.sh --produccion-ultimo-minuto
```

Corta si postgres está corriendo o si el volumen de la base ya tiene una base: nunca pisa una base viva.
Después:

1. levantar GDI con el instalador (o `gdi up -d`);
2. sacar una copia completa: `./scripts/backup-pitr.sh completa`;
3. revisar la firma de cada tipo de documento: un PDF firmado en el último minuto antes del desastre puede
   tener un número que la base no registra.

## Cuánto cuesta

Con una base de ~1,3 GB y ~7 MB de cambios por día: USD 1 a 3 por mes en un proveedor S3 de bajo costo.

## Para tener en cuenta

- **El bucket:** si tiene versiones (por ejemplo, porque se le habilitó Object Lock), lo que pgBackRest borra por
  la retención queda oculto pero guardado, y el bucket crece sin techo. Hace falta una regla de ciclo de vida que
  borre de verdad lo oculto en la carpeta de la copia (por ejemplo, una regla que borre lo oculto a 1 día para el
  prefijo de `PITR_S3_PREFIX`).
- **Las claves** quedan en las variables del contenedor de postgres (se ven con `docker inspect`, como
  `DB_PASSWORD`): ahí están la clave de cifrado y una clave del S3 que puede borrar. Quien tenga acceso a Docker
  en el servidor las ve.
- **pgBackRest a mano**, siempre como el usuario `postgres` (`docker compose exec -u postgres postgres pgbackrest ...`).
  Como root deja un archivo de bloqueo que traba la copia diaria.
