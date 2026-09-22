# GDI OnPremise — Manual de instalación

> **Para quién es.** Este manual está escrito para que lo ejecute un **agente de IA** (Claude,
> ChatGPT o el que use el municipio) con acceso SSH al servidor, acompañado por el **técnico del
> municipio**. Una persona también lo puede seguir tal cual: cada paso dice qué hacer, cómo
> verificar que salió bien y qué hacer si no.
>
> La versión corta, para quien decide y coordina, está en [la guía ejecutiva](index.md).
>
> Validado de punta a punta en una instalación limpia el 22/09/2026 (set `2026.09.9`): servidor
> nuevo, licencia por código, 7 certificados, municipio de capacitación y de producción, firma
> de documentos y asistente de IA conectado por MCP.

---

## 0. Reglas para el agente

1. **Seguí los pasos en orden.** Cada paso termina en un bloque **CHECK**. No avances si un CHECK
   falla: andá a [14. Problemas](#14-problemas) con el síntoma exacto.
2. **No inventes valores.** Todo lo que el sistema necesita está en la
   [sección 1](#1-antes-de-empezar-lo-que-tiene-que-existir). Si falta algo, pedilo y esperá.
3. **Los pasos marcados 👤 los hace una persona**, no vos: panel web de Auth0, registros DNS,
   login en el navegador. Decile exactamente qué hacer (este manual lo trae escrito), esperá su
   confirmación y **verificá vos** con el CHECK.
4. **Los secretos no pasan por el chat.** Tokens, client secrets y contraseñas los carga el
   técnico directo en el servidor (`nano /opt/gdi/.env` o `read -rsp`), o vos los pasás por
   stdin desde un gestor de secretos. Nunca los imprimas, nunca los pongas como argumento de un
   comando, nunca los pegues en tu respuesta.
5. **No "mejores" lo que el manual fija.** Versión del proxy, permisos de `license/`, nombres de
   claims, identificadores de Auth0: están así por algo que se aprendió instalando, y cada paso
   explica por qué.
6. **Let's Encrypt tiene cupo.** No reinstales de cero en loop ni repitas pasos que piden
   certificados nuevos ([paso 8](#8-proxy-y-certificados-https)).
7. **Nada de esto requiere a GDI Latam** una vez que tenés lo de la sección 1. Si un paso dice
   "avisale a GDI", es porque del lado de GDI hay algo mal (una versión no publicada, un token
   vencido), no porque haga falta un permiso.

**Variables que usa este manual** (reemplazalas en cada comando):

| Variable | Qué es | Ejemplo |
|---|---|---|
| `<BASE>` | dominio base del municipio | `tu-municipio.gob.ar` |
| `<VERSION>` | versión del set de GDI (formato `AAAA.MM.N`) | `2026.09.10` |
| `<AUTH0_DOMAIN>` | dominio del tenant de Auth0 | `tu-municipio.us.auth0.com` |
| `<IP>` | IP pública del servidor | `203.0.113.10` |
| `<IMAGEN_INSTALADOR>` | dirección de la imagen del instalador | te la indica GDI en el mail de entrega |

---

## 1. Antes de empezar: lo que TIENE que existir

Sin **todo** lo de la tabla 1.1 la instalación no termina. Juntalo antes de tocar el servidor.

### 1.1. Obligatorio

| # | Qué | De dónde sale | Para qué | Si falta |
|---|---|---|---|---|
| 1 | **Token de `ghcr.io`** | lo entrega GDI Latam | bajar el instalador y las 12 imágenes | no baja nada |
| 2 | **Código de activación** (`GDI-XXXX-XXXX-XXXX`) | lo entrega GDI Latam | el servidor se baja solo su licencia | sin BackOffice, sin IA, sin poder crear municipios |
| 3 | **Número de versión** (`AAAA.MM.N`) y **dirección del instalador** | lo entrega GDI Latam | la misma versión para el instalador y las imágenes | `manifest unknown` |
| 4 | **Servidor Linux** | el municipio | ver 1.3 | — |
| 5 | **Dominio con 7 registros DNS** tipo A → `<IP>` | el municipio | ver 1.4 | sin HTTPS no hay login |
| 6 | **Tenant de Auth0** | el municipio (cuenta gratis) | el login de todas las personas | **no hay alternativa**: ver 1.2 |
| 7 | **Salida a internet** del servidor | la red del municipio | ver 1.5 | la licencia no se activa ni se renueva |
| 8 | **Un mail de administrador** | el municipio | entra al Panel (`PANEL_ADMIN_EMAILS`) | nadie puede crear municipios |

> **No confundas el código con el número de licencia.** El código tiene tres grupos de 4
> (`GDI-K7M2-P4XQ-9TVR`) y sirve para activar. El número de licencia (`GDI-` + 16 caracteres,
> el de las facturas) **no** activa nada.

### 1.2. Auth0 es obligatorio

GDI no tiene login propio: **todas** las personas (empleados, administradores, el Panel) entran
por Auth0, y las altas de usuarios las hace GDI contra Auth0. No hay modo "sin Auth0" ni otro
proveedor soportado hoy (Keycloak dentro del compose está planificado: card GDI-432).

- El plan gratuito de Auth0 alcanza (cubre hasta 25.000 usuarios activos por mes).
- El tenant es **del municipio**, no de GDI: lo crea y lo administra el municipio.
- La configuración completa está en el [paso 4](#4-auth0-el-login): unos 30 minutos de clics
  en el panel web de Auth0.

### 1.3. El servidor

| Recurso | Valor |
|---|---|
| Sistema | Ubuntu 22.04 o 24.04 (probado en 24.04). Windows solo con WSL2, sin soporte |
| CPU | 4 vCPU |
| RAM | 8 GB recomendado · 4 GB mínimo (medido: ~2,1 GB en uso con los 16 contenedores) |
| Disco | 80 GB (crece con los documentos si usás MinIO local) |
| IP | pública y fija |
| Puertos de entrada | **80 y 443 abiertos a internet** (Let's Encrypt valida por el 80; la gente entra por el 443) · 22 para administrar |
| Acceso | SSH con un usuario con `sudo` |

El puerto 81 (panel del proxy) **no** se abre: escucha solo en `localhost` a propósito.

### 1.4. Los 7 registros DNS

Todos tipo **A**, apuntando a `<IP>`, cargados **antes** del paso 8:

| Registro | Sirve |
|---|---|
| `gdi.<BASE>` | portal de los empleados |
| `api.<BASE>` | API del backend |
| `admin.<BASE>` | BackOffice (administración) |
| `admin-api.<BASE>` | API del BackOffice |
| `mcp.<BASE>` | conexión de asistentes de IA (MCP) |
| `panel.<BASE>` | Panel: crear y activar municipios |
| `storage.<BASE>` | documentos (MinIO). **Solo con MinIO local**; con Cloudflare R2 son 6 |

**CHECK** (desde cualquier máquina): `dig +short gdi.<BASE>` y los otros seis devuelven `<IP>`.

### 1.5. Salida a internet (HTTPS, puerto 443)

| Destino | Para qué | Cuándo |
|---|---|---|
| `ghcr.io` y `pkg-containers.githubusercontent.com` | instalador e imágenes de GDI | al instalar y actualizar |
| `registry-1.docker.io`, `quay.io` | proxy, Redis y MinIO | al instalar y actualizar |
| `download.docker.com`, `get.docker.com` | instalar Docker | una vez |
| `license.gdilatam.com` | activar y **renovar** la licencia (cada semana) | **siempre** |
| `acronimos.gdilatam.com` | registro central de siglas (no puede haber dos municipios con la misma) | al crear municipios |
| `<AUTH0_DOMAIN>` | validar logins y dar de alta usuarios | **siempre** |
| `acme-v02.api.letsencrypt.org` | certificados HTTPS | al instalar y en cada renovación (~60 días) |
| `openrouter.ai` | IA (si se usa) | siempre |
| el servidor SMTP del municipio | mails (si se usa) | siempre |

**No existe modo sin conexión.** La licencia se activa y se renueva solo contra GDI.

### 1.6. Opcional (funciona sin esto, con límites)

| Qué | Sin esto… |
|---|---|
| **Correo**: SMTP del municipio o cuenta de Resend | no salen mails: el enlace de activación de cada usuario aparece en pantalla y hay que pasarlo a mano. Las alertas del sistema quedan solo en los logs |
| **Clave de OpenRouter** (`sk-or-…`) | la IA no responde (resúmenes, búsqueda inteligente, asistente) |
| **Certificado de firma del municipio** (`.p12`) | se firma con un certificado **autofirmado** que el sistema genera solo: sirve para probar, **no tiene validez legal** ([paso 10](#10-certificado-de-firma)) |
| **Credenciales propias de Google** (Google Cloud) | para login con Google en producción: Auth0 trae claves de desarrollo que no son para producción |

---

## 2. Preparar el servidor

```bash
sudo apt-get update && sudo apt-get install -y curl jq
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER      # después: cerrar la sesión SSH y volver a entrar
```

**CHECK:** `docker --version` y `docker compose version` responden (Compose v2 o superior), y
`docker ps` corre sin `sudo` (si pide permiso, falta volver a entrar por SSH).

---

## 3. Bajar el instalador

El instalador (compose, `.env.example`, scripts y este manual) viene **como una imagen más** del
registro de GDI, con la misma versión que los servicios. Se baja con el mismo token.

**3.1. Login al registro.** El token lo pega el técnico; no queda en el historial:

```bash
read -rsp "Token de GDI (ghcr.io): " GDI_TOKEN && echo
echo "$GDI_TOKEN" | docker login ghcr.io -u gdi --password-stdin
unset GDI_TOKEN
```

> El usuario (`-u`) no importa para ghcr.io con un token clásico: cualquier texto sirve.

**3.2. Descargar la versión `<VERSION>`:**

```bash
sudo mkdir -p /opt/gdi && sudo chown $USER /opt/gdi
docker run --rm <IMAGEN_INSTALADOR>:<VERSION> | tar x -C /opt/gdi
cd /opt/gdi && ls
```

**CHECK:** en `/opt/gdi` están `docker-compose.yml`, `docker-compose.premium.yml`,
`docker-compose.minio.yml`, `.env.example`, `scripts/` y `docs/`, y
`grep ^IMAGE_VERSION= .env.example` dice `<VERSION>`.

- No apareció `Login Succeeded` → token mal copiado o vencido: [14](#14-problemas).
- `manifest unknown` o `not found` → esa versión no está publicada. **No bajes otra**: avisale a GDI.
- `denied` → el token no tiene acceso: avisale a GDI.

> No hace falta `git` ni otro token, y la instalación **no es un repo**: no queda ningún token
> escrito en `/opt/gdi`. El `docker login` guarda la credencial en `~/.docker/config.json` del
> usuario; si preferís no dejarla, `docker logout ghcr.io` al terminar el paso 7, y volvé a
> loguearte para actualizar.

---

## 4. Auth0 (el login)

👤 **Todo este paso lo hace una persona en el panel web de Auth0** (`manage.auth0.com`). El
agente le dicta cada punto y al final verifica con el CHECK. Se puede hacer mientras el servidor
baja imágenes, pero **tiene que estar terminado antes del paso 9**.

Anotá a medida que avanzás (van al `.env` en el paso 5): el dominio del tenant y **cuatro pares
Client ID / Client Secret** (Frontend, BackOffice, Panel y Machine to Machine).

### 4.1. Tenant
Crear una cuenta en [auth0.com](https://auth0.com) y un tenant. Su dominio (por ejemplo
`tu-municipio.us.auth0.com`) es `<AUTH0_DOMAIN>`.

### 4.2. API principal
*Applications → APIs → **Create API***
- **Name:** `GDI API`
- **Identifier:** `https://gdi-api`. Es un identificador, **no una URL real**. Va a `AUTH0_AUDIENCE`.
- Signing algorithm: RS256 → **Create**.

### 4.3. Tres aplicaciones de login
*Applications → Applications → **Create Application** → **Regular Web Application***, tres veces:

| Aplicación | Allowed Callback URLs | Allowed Logout URLs y Allowed Web Origins | Va a |
|---|---|---|---|
| `GDI Frontend` | `https://gdi.<BASE>/auth/callback` | `https://gdi.<BASE>` | `AUTH0_FRONTEND_CLIENT_ID/SECRET` |
| `GDI BackOffice` | `https://admin.<BASE>/auth/callback` | `https://admin.<BASE>` | `AUTH0_BACKOFFICE_CLIENT_ID/SECRET` |
| `GDI Panel` | `https://panel.<BASE>/auth/callback` | `https://panel.<BASE>` | `AUTH0_PANEL_CLIENT_ID/SECRET` |

Las **Logout URLs** importan: si no coinciden, nadie puede cerrar sesión.

### 4.4. Conexiones en las tres aplicaciones
En **cada una** de las tres: pestaña **Connections** → activar **Username-Password-Authentication**
(y **google-oauth2** si van a entrar con Google). Una aplicación sin conexión da *"Client is not
authorized to use this connection"*.

### 4.5. Cerrar el registro libre
*Authentication → Database → Username-Password-Authentication* → **Disable Sign Ups: ON** → Save.

Las cuentas las crea GDI desde el BackOffice: nadie necesita registrarse solo. Con el registro
abierto, cualquiera puede crearse un usuario en el Auth0 del municipio.

### 4.6. El email dentro del token (sin esto nadie entra)
GDI identifica a cada persona por su email, y Auth0 no lo pone en el token por defecto.

1. *Actions → Library → **Build Custom***: nombre `GDI - email en el access token`, trigger
   **Login / Post Login**, runtime **Node 22**.
2. Pegar este código → **Deploy**:
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     if (event.user.email) {
       api.accessToken.setCustomClaim('https://gdilatam.com/email', event.user.email);
     }
     if (event.user.name) {
       api.accessToken.setCustomClaim('https://gdilatam.com/name', event.user.name);
     }
   };
   ```
3. *Actions → Triggers → post-login*: arrastrar la Action al flujo → **Apply**.

El nombre del claim (`https://gdilatam.com/...`) es **fijo**: lo espera el código. No lo cambies
por el dominio del municipio.

### 4.7. Aplicación Machine to Machine (sin esto no se crean usuarios)
*Applications → Create Application → **Machine to Machine***
- Autorizarla contra **Auth0 Management API** (la que viene de fábrica, **no** la del 4.2).
- Permisos: `read:users`, `create:users`, `update:users`, `create:user_tickets`. Exactamente esos.
- Su Client ID / Secret van a `AUTH0_M2M_CLIENT_ID` / `AUTH0_M2M_CLIENT_SECRET`.

### 4.8. Asistentes de IA (MCP)
Por `mcp.<BASE>` un asistente de IA opera GDI **a nombre del empleado**, con sus mismos permisos.
El asistente se registra solo en Auth0 y el empleado lo autoriza con su login. Hacen falta
**cuatro** cosas: si falta una sola, el asistente no conecta.

**a) Registro automático de asistentes.** *Settings → Advanced* → **Dynamic Client Registration
(DCR): ON**. El interruptor se guarda solo: el botón *Save* que está más abajo es de otra
sección. Aparece **DCR Security Mode**: dejalo en **Strict**.

**b) Conexiones a nivel de dominio.** Los asistentes que se registran solos solo pueden usar
conexiones "promovidas":
- *Authentication → Database → Username-Password-Authentication* → **Promote Connection to
  Domain Level: ON** → Save.
- Si usan Google: *Authentication → Social → google-oauth2 → Advanced* → **Promote Connection
  to Domain Level: ON** → Save. Sin esto, el asistente solo ofrece usuario y contraseña.

**c) Una segunda API, con la dirección del MCP.** El servidor MCP solo acepta tokens emitidos
para su propia dirección. *Applications → APIs → **Create API***:
- **Name:** `GDI MCP`
- **Identifier:** `https://mcp.<BASE>/`, **con la barra final**, exacto. Es lo que piden los
  asistentes, y no se puede cambiar después.
- Signing algorithm: RS256.
- **Access Policy → Within user-delegated access: All apps allowed.**
- **Within client access: Per-app authorization** (no lo cambies).
- **Create**.

**d) En esa API nueva, pestaña Settings:**
- **Allow Offline Access: ON**, para que el asistente renueve su sesión sin pedir login cada
  vez → Save.
- **Default Permissions for third-party applications:**
  - **User-delegated Access: Authorized.** La lista de permisos aparece **vacía, y está bien**:
    los permisos que pide el asistente (`openid`, `profile`, `email`, `offline_access`) son de
    login estándar y Auth0 los da siempre. No son permisos de la API.
  - **Client Access: Unauthorized.** Así ningún programa entra sin un empleado logueado.
  - Save.

> **Qué queda abierto con esto.** `https://<AUTH0_DOMAIN>/oidc/register` acepta registros sin
> credenciales (Auth0 lo limita a 5 por segundo). Quien se registre así **no accede a ningún
> dato** sin que un empleado se loguee y lo autorice, no puede entrar como "aplicación sin
> usuario" y solo obtiene lo del punto d). Cada tanto revisá *Applications* y borrá las que
> empiezan con `tpc_` y no reconozcas. Es el mismo esquema que usa GDI en la nube.

> Al crear la API del punto c), Auth0 agrega sola una aplicación "GDI MCP (Test Application)".
> No se usa: se puede borrar.

### 4.9. Google en producción (solo si usan Google)
La conexión `google-oauth2` viene con **claves de desarrollo de Auth0**, y el propio Auth0 avisa
que no son para producción. Crear credenciales OAuth en Google Cloud Console y cargarlas en
*Authentication → Social → google-oauth2 → Client ID / Client Secret*.

**CHECK del paso 4.** El agente lo puede comprobar sin entrar a Auth0:

```bash
curl -s https://<AUTH0_DOMAIN>/.well-known/openid-configuration | jq -r .issuer
# → https://<AUTH0_DOMAIN>/
```

Además, el técnico confirma que tiene los **4 pares** Client ID / Secret. El resto de Auth0 se
verifica funcionando: login y alta de usuarios en el paso 9, MCP en el paso 11.

---

## 5. Configurar el `.env`

```bash
cd /opt/gdi
cp .env.example .env
chmod 600 .env
sudo ./scripts/generar-claves.sh
```

`generar-claves.sh` genera las claves internas y las contraseñas de la base y de MinIO, y deja la
carpeta `license/` con el dueño correcto (uid 999). Se puede correr de nuevo sin riesgo: lo que
ya tiene valor y no se puede cambiar (`CERT_MASTER_KEY`, `DB_PASSWORD`, contraseñas de MinIO)
no lo toca.

> ⚠️ **`CERT_MASTER_KEY` no se cambia ni se pierde nunca.** Cifra los certificados de firma: sin
> la original, los certificados cargados no se pueden volver a usar. Viaja en el backup (paso 13).

**Completar el resto.** Estos son los valores que faltan. Los marcados 🔐 son secretos: los
carga el técnico con `nano .env` (regla 4).

```env
IMAGE_VERSION=<VERSION>                       # ya viene; confirmá que coincida

# Auth0 (paso 4)
AUTH0_DOMAIN=<AUTH0_DOMAIN>
AUTH0_AUDIENCE=https://gdi-api
AUTH0_FRONTEND_CLIENT_ID=...
AUTH0_FRONTEND_CLIENT_SECRET=...              # 🔐
AUTH0_BACKOFFICE_CLIENT_ID=...
AUTH0_BACKOFFICE_CLIENT_SECRET=...            # 🔐
AUTH0_PANEL_CLIENT_ID=...
AUTH0_PANEL_CLIENT_SECRET=...                 # 🔐
AUTH0_M2M_CLIENT_ID=...
AUTH0_M2M_CLIENT_SECRET=...                   # 🔐

# Dominios
FRONTEND_URL=https://gdi.<BASE>
NEXT_PUBLIC_API_URL=https://api.<BASE>
BACKOFFICE_URL=https://admin.<BASE>
BACKOFFICE_API_URL=https://admin-api.<BASE>
GATEWAY_URL=https://mcp.<BASE>
PANEL_URL=https://panel.<BASE>

# Almacenamiento con MinIO local
CF_R2_ENDPOINT=https://storage.<BASE>         # el dominio PÚBLICO, nunca http://minio:9000
STORAGE_DOMAIN=storage.<BASE>                 # el mismo host, sin https://
CF_R2_AVATARS_PUBLIC_URL=https://api.<BASE>/avatars
CF_R2_PUBLIC_URL=https://storage.<BASE>/gdi-assets
AUTOFIRMA_STORAGE_URL=https://api.<BASE>/digital-signature/storage

# Quién entra al Panel (separados por coma). SIN ESTO NO ENTRA NADIE.
PANEL_ADMIN_EMAILS=sistemas@<BASE>
# A quién le llegan las alertas del sistema (hueco de numeración, firma fallida, errores 500)
ALERT_TO_EMAIL=sistemas@<BASE>

# Licencia (sección 1.1, punto 2)
GDI_ACTIVATION_CODE=GDI-XXXX-XXXX-XXXX        # 🔐

# IA: la clave de OpenRouter, o VACÍO si no se usa IA (no dejes el ejemplo sk-or-xxx)
OPENROUTER_API_KEY=                           # 🔐
```

Las variables de almacenamiento parecen redundantes y no lo son. El backend firma los enlaces de
descarga con `CF_R2_ENDPOINT` y el navegador del empleado los abre directo. `STORAGE_DOMAIN` hace
que ese mismo nombre se resuelva **dentro** de Docker, sin depender del router del municipio:
sin eso, con muchos routers el sistema no puede guardar ni un PDF. **No borres
`S3_FORCE_PATH_STYLE=true` ni `GDI_LICENSE_HEARTBEAT_URL`**: ya vienen en el `.env.example`.

**Correo (opcional, sección 1.6).** Descomentá y completá en el `.env` **una** de estas dos:
- SMTP propio: `SMTP_HOST`, `SMTP_PORT` (587 = STARTTLS; con 465 agregá `SMTP_SSL=true`),
  `SMTP_USER`, `SMTP_PASSWORD` 🔐 y `FROM_EMAIL=Municipio <noreply@<BASE>>`.
- Resend: `RESEND_API_KEY` 🔐 y `FROM_EMAIL`. Si están las dos, manda por Resend.

**Cloudflare R2 en lugar de MinIO:** usá el bloque "Opción B" del `.env.example`, sin
`STORAGE_DOMAIN`, y en los pasos 7 y 8 sacá `docker-compose.minio.yml` y el host `storage.`.

**CHECK:**

```bash
cd /opt/gdi
grep -c CAMBIAR .env                               # → 0
grep -c $'\r' .env                                 # → 0 (sin fines de línea de Windows)
grep -E '^(AUTH0_DOMAIN|AUTH0_[A-Z]+_CLIENT_ID|PANEL_ADMIN_EMAILS|GATEWAY_URL)=$' .env   # → nada
stat -c %u license                                 # → 999
```

Si el segundo da más de 0: `sed -i 's/\r$//' .env`.

---

## 6. La licencia

No hay que hacer nada más. Con `GDI_ACTIVATION_CODE` en el `.env`, en el primer arranque el
BackOffice canjea el código contra `license.gdilatam.com`, baja la licencia a `/opt/gdi/license/`
y desde ahí **la renueva sola cada semana**. La licencia dura 30 días y se va corriendo mientras
el contrato esté vigente: que diga "faltan 28 días" es normal.

- Si GDI no contesta el día de la instalación, el sistema arranca igual (BackOffice e IA en
  pausa) y reintenta en cada arranque. Reintentar **no gasta** el código.
- El código es de **esta** instalación. Reinstalar el mismo servidor funciona; cada activación
  queda registrada con la fecha y el nombre del servidor.
- ⛔ **No endurezcas los permisos de `license/` ni del `.lic`.** La carpeta tiene que ser del
  uid 999 y el `.lic`, `644`. Los contenedores no corren como root: con otros permisos el
  sistema ve la licencia pero no la puede abrir, y el BackOffice dice que está vencida.

---

## 7. Levantar GDI

Definí un alias para no equivocarte de archivos (con R2, sin el último `-f`):

```bash
cd /opt/gdi
alias gdi='docker compose -f docker-compose.yml -f docker-compose.premium.yml -f docker-compose.minio.yml'
gdi up -d
```

La primera vez tarda unos minutos (baja las imágenes). En el resto del manual, **`gdi up -d`**
es este comando. El alias dura lo que la sesión SSH: para dejarlo fijo,
`echo "alias gdi='cd /opt/gdi && docker compose -f docker-compose.yml -f docker-compose.premium.yml -f docker-compose.minio.yml'" >> ~/.bashrc`.

**CHECK** (1 o 2 minutos después):

```bash
gdi ps -a --format '{{.Service}}\t{{.Status}}'
```
- `migrator` y `minio-init` → **Exited (0)**. Cualquier otro código → [14](#14-problemas).
- `postgres`, `redis`, `minio`, `backend`, `gateway` y `panel-front` → `healthy`.
- El resto → `Up`. Ninguno en `Restarting`.

```bash
gdi logs backoffice-back | grep -E '\[OK\]|\[FALTA\]|Licencia ACTIVADA'
```
- Tiene que aparecer `Licencia ACTIVADA contra el Panel: GDI-… para <municipio>`.
- Tiene que aparecer `[OK] Alta de usuarios: credenciales de Auth0 presentes`.
- `[FALTA] Correo NO CONFIGURADO` es esperable si no configuraste correo.
- Si dice `No se pudo escribir la licencia … Permission denied` → [14](#14-problemas).

---

## 8. Proxy y certificados HTTPS

El proxy (nginx-proxy-manager) publica los 7 dominios y pide los certificados a Let's Encrypt.
Todo se hace con un script, sin cargar formularios.

**8.1. Crear el administrador del proxy.** El proxy nace **sin** usuario y el primero que lo crea
se queda con él: hacelo apenas levantaste. Desde el servidor (el panel escucha solo en
`localhost`):

```bash
cd /opt/gdi
curl -s localhost:81/api/ | jq .setup           # → false = todavía no hay administrador
NPM_EMAIL=sistemas@<BASE>                       # recibe los avisos de Let's Encrypt
NPM_PASSWORD=$(openssl rand -hex 16)
curl -s -X POST localhost:81/api/users -H 'Content-Type: application/json' \
  -d "{\"name\":\"Admin GDI\",\"nickname\":\"admin\",\"email\":\"$NPM_EMAIL\",\"roles\":[\"admin\"],\"is_disabled\":false,\"auth\":{\"type\":\"password\",\"secret\":\"$NPM_PASSWORD\"}}" | jq -c '{id,email}'
( umask 077; printf 'NPM_EMAIL=%s\nNPM_PASSWORD=%s\n' "$NPM_EMAIL" "$NPM_PASSWORD" > npm-admin.txt )
unset NPM_PASSWORD
curl -s localhost:81/api/ | jq .setup           # → true
```

Las credenciales quedan en `/opt/gdi/npm-admin.txt`, legible solo por su dueño. Si el técnico
prefiere hacerlo a mano: túnel `ssh -L 8181:localhost:81 usuario@<IP>`, abrir
`http://localhost:8181` y crear el usuario en la primera pantalla.

**8.2. Los 7 hosts y los certificados.** Antes, confirmá que los 7 DNS resuelven a `<IP>`
(sección 1.4): si no, Let's Encrypt no emite.

```bash
cd /opt/gdi
set -a; . ./npm-admin.txt; set +a
./scripts/configurar-proxy.sh                   # con R2: SIN_MINIO=1 ./scripts/configurar-proxy.sh
```

El script crea cada host con su destino, los buffers que necesita el login de Auth0 (sin ellos
el primer login da 502), la ruta `/avatars` y el certificado. Se puede correr de nuevo: si un
host ya tiene certificado, no pide otro.

> ⚠️ **Cupo de Let's Encrypt: 5 certificados iguales por semana** para los mismos dominios. Cada
> instalación pide uno por dominio, así que reinstalar el servidor de cero los vuelve a pedir:
> después de 5 reinstalaciones en una semana, los certificados no salen hasta que se libera el
> cupo. No reinstales de cero para "probar": si hay que rehacer algo, rehacé solo esa parte.

**CHECK:**

```bash
for u in gdi.<BASE> api.<BASE>/health admin.<BASE> admin-api.<BASE>/health \
         mcp.<BASE>/health panel.<BASE> storage.<BASE>/minio/health/live; do
  printf '%-45s %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 https://$u)"
done
# → 200 en los 7
gdi exec backend getent hosts storage.<BASE>    # → una IP interna (172.x), NO <IP>
```

Si un dominio no tiene certificado, el script imprime `Let's Encrypt no emitio` con un
`motivo:`. **Leé el motivo**, no adivines: [14](#14-problemas).

---

## 9. Crear los municipios (Panel)

👤 **Lo hace el administrador en el navegador**; el agente verifica.

Cada municipio tiene **dos instancias**: una de **capacitación** (para practicar) y una de
**producción** (la de verdad). Cuántas se pueden crear lo dice la licencia, en *Mi Licencia*
("Capacitación: 0 de 1 · Producción: 0 de 1").

**9.1. Capacitación.** Entrar a `https://panel.<BASE>` con un mail de `PANEL_ADMIN_EMAILS` →
**Crear Instancia**: nombre, color y **administrador** (mail y nombre). La sigla de capacitación
la asigna el sistema.
- Si el administrador no existía en Auth0, se le crea el usuario. Sin correo configurado, el
  Panel muestra en pantalla el **enlace de activación**: sirve una sola vez, vence a los 5 días
  y se pasa por un canal seguro. Si ya existía, entra con su clave de siempre.

**9.2. Preparar la capacitación.** En el BackOffice (`https://admin.<BASE>`), el administrador
carga lo que después va a heredar producción: tipos de documento, reparticiones, sectores, sellos
y usuarios de prueba. Los tipos de documento con **formulario controlado** nacen **inactivos**:
hay que activarlos para que aparezcan en el portal.

**9.3. Producción.** *Instancias* → en la fila de la capacitación, **Crear Tenant PRD**:
- el nombre del municipio **tal como va a figurar en los documentos** (sin el prefijo de
  capacitación);
- la **sigla definitiva** (2 a 8 letras o números), escrita dos veces;
- el **administrador de producción** (mail y nombre).

La producción **copia la configuración** de la capacitación: tipos de documento con sus campos,
tipos de expediente, reparticiones, sectores, sellos y roles. **No** copia expedientes ni
documentos. La capacitación sigue funcionando, y cada capacitación genera **una sola** producción.

> 🔴 **La sigla de producción no se cambia nunca.** Queda impresa en el número de cada documento
> firmado (`IF-2026-00000001-SIGLA-…`) y de ella salen el schema y los buckets. GDI consulta su
> registro central para que no haya dos municipios con la misma: si ya existe, el alta se
> rechaza sin crear nada; si el registro no contesta, el alta no sigue.

**CHECK** (agente):

```bash
gdi exec -T postgres psql -U postgres railway -At -c \
  "select schema_name from information_schema.schemata where schema_name ~ '^[0-9]{3}_' order by 1"
# → un schema por instancia (por ejemplo 100_ab12cd = capacitación, 101_sigla = producción)
gdi exec -T postgres psql -U postgres railway -At -c \
  "select count(*) from information_schema.tables where table_schema='<schema>'"
# → 46
gdi exec -T minio sh -c 'ls /data'
# → 4 buckets por instancia: gdi-<sigla>-oficial, -tosign, -preoficial y -publico
```

Si el Panel abre pero la lista sale vacía → `SUPERADMIN_KEY` sin valor: [14](#14-problemas).
Si no deja entrar → el mail no está en `PANEL_ADMIN_EMAILS` (tener usuario de Auth0 no alcanza).

---

## 10. Certificado de firma

Al crear cada instancia, el sistema le genera un **certificado autofirmado**: con él los
documentos se firman y se numeran desde el primer minuto. **Sirve para probar; no tiene validez
legal.**

Para producción: BackOffice → **Certificados** → *Subir .p12 directamente* → el archivo
`.p12`/`.pfx` del municipio y su contraseña. La pantalla tiene que mostrar **sujeto, emisor y
validez**; si quedan vacíos, el archivo no se guardó. Si todavía no hay certificado, la misma
pantalla guía para pedirlo (*Solicitar certificado ONTI*).

**CHECK** (👤 + agente): el administrador firma un documento de prueba en `https://gdi.<BASE>` y
el agente confirma el número oficial:

```bash
gdi exec -T postgres psql -U postgres railway -At -c \
  "select document_number, status from \"<schema>\".document_draft order by created_at desc limit 3"
# → IF-2026-0000000N-<SIGLA>-<REPARTICION> | signed
```

---

## 11. Conectar un asistente de IA (MCP)

**CHECK del servidor:**

```bash
curl -s https://mcp.<BASE>/.well-known/oauth-protected-resource | jq -c '{resource,authorization_servers}'
# → {"resource":"https://mcp.<BASE>","authorization_servers":["https://<AUTH0_DOMAIN>"]}
```

Tiene que apuntar al Auth0 **del municipio**, nunca a `gdilatam.com`.

**Conectar** (ejemplo con Claude Code; otros asistentes piden la misma URL):

```bash
claude mcp add --transport http gdi https://mcp.<BASE>/mcp
```

👤 Al conectarse, el asistente abre el login de Auth0. El empleado entra y ve una **pantalla de
consentimiento** ("¿autorizás a este asistente?"): es correcto que aparezca, porque está
autorizando a un programa a actuar en su nombre.

**CHECK:** el asistente lista sus herramientas (43) y `list_my_tenants` devuelve las instancias
del empleado. Si Auth0 muestra *"Oops!, something went wrong"* → [14](#14-problemas).

---

## 12. Actualizar GDI

> 🛑 **Primero el backup** (paso 13). Una actualización aplica migraciones a la base y **eso no
> tiene vuelta atrás**: volver a la imagen anterior no revierte el schema.

GDI avisa por mail cuando hay una versión nueva. **Nada se actualiza solo**: el municipio elige
el día y la hora, fuera del horario de atención.

```bash
cd /opt/gdi
# 1. Backup completo (paso 13) y verificar que no quedó vacío.
# 2. El instalador de la versión nueva. Pisa compose, scripts y manual; NO toca .env ni license/.
docker run --rm <IMAGEN_INSTALADOR>:<VERSION_NUEVA> | tar x -C /opt/gdi
# 3. La versión en el .env: una sola línea, la misma para todo.
sed -i 's/^IMAGE_VERSION=.*/IMAGE_VERSION=<VERSION_NUEVA>/' .env
# 4. Imágenes nuevas y contenedores nuevos (el migrator aplica las migraciones antes del backend).
gdi pull && gdi up -d
```

**CHECK:** el mismo del paso 7, y además `curl -s https://panel.<BASE>/api/version | jq -r .paquete`
→ `<VERSION_NUEVA>`. Entrá al portal y abrí un expediente: si algo quedó mal, es ahora cuando
querés enterarte, con el backup fresco.

**Volver atrás** son **dos** cosas, y las dos hacen falta: el instalador y la versión anteriores
(los mismos pasos 2 y 3 con la versión vieja) **y restaurar el dump** (paso 13). Hacer solo lo
primero deja la base migrada contra código viejo: no es volver atrás, es otro sistema roto.

---

## 13. Backups

Un servidor perdido se recupera con **cinco** cosas:

| Qué | Dónde | Sin esto… |
|---|---|---|
| Base de datos | volumen `gdi_postgres_data` | no hay nada |
| Documentos (solo MinIO) | volumen `gdi_minio_data` | la base apunta a archivos que no existen |
| `.env` | `/opt/gdi/.env` | no levanta: claves, Auth0, `CERT_MASTER_KEY` |
| Licencia | `/opt/gdi/license/` | arranca sin BackOffice ni IA hasta reactivar |
| Imágenes | el registro, o una copia local | si el token no está activo, no se puede reinstalar |

```bash
cd /opt/gdi && mkdir -p backups && FECHA=$(date +%F)
gdi exec -T postgres pg_dump -U postgres railway -Fc > backups/gdi-$FECHA.dump
docker run --rm -v gdi_minio_data:/data -v /opt/gdi/backups:/backup alpine tar czf /backup/minio-$FECHA.tar.gz -C /data .
tar czf backups/config-$FECHA.tar.gz .env license/ npm-admin.txt
# Solo al actualizar (una vez por versión):
gdi images | awk 'NR>1 {print $2":"$3}' | sort -u > backups/imagenes-$FECHA.txt
docker save $(cat backups/imagenes-$FECHA.txt) | gzip > backups/imagenes-$FECHA.tar.gz
ls -lh backups/
```

**CHECK:** ningún archivo pesa unos pocos KB. Un dump de 5 KB es un error, no un backup.

**Reglas:** backup diario automático (`cron` con las tres primeras líneas), copia **fuera** del
servidor, y al menos una restauración de prueba en otra máquina. El `.env` y el `.lic` son
secretos: guardalos como contraseñas.

**Restaurar:**

```bash
cd /opt/gdi
gunzip -c backups/imagenes-AAAA-MM-DD.tar.gz | docker load        # si no hay acceso al registro
tar xzf backups/config-AAAA-MM-DD.tar.gz
gdi up -d postgres
gdi exec -T postgres pg_restore -U postgres -d railway --clean --if-exists < backups/gdi-AAAA-MM-DD.dump
docker run --rm -v gdi_minio_data:/data -v /opt/gdi/backups:/backup alpine tar xzf /backup/minio-AAAA-MM-DD.tar.gz -C /data
sudo chown -R 999:999 license && sudo chmod 644 license/*.lic
gdi up -d
```

---

## 14. Problemas

Buscá el **síntoma exacto**. Para cualquier servicio: `gdi ps` y `gdi logs --tail=100 <servicio>`.
Cuando la solución dice `gdi up -d`, es ese comando: un `restart` **no** relee el `.env`.

### Instalación

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `docker login` no dice `Login Succeeded` | token mal copiado o vencido | volver a pegarlo; si sigue, pedir uno nuevo a GDI |
| `manifest unknown` al bajar el instalador o las imágenes | esa versión no está publicada, o `IMAGE_VERSION` está mal escrita | revisar el formato `AAAA.MM.N`. **No bajar otra versión**: avisar a GDI |
| `denied` / `unauthorized` en un `pull` | el token no tiene acceso, o se perdió el `docker login` | rehacer 3.1; si sigue, avisar a GDI |
| `migrator` en `Exited (1)` y el backend no arranca | falló una migración | `gdi logs migrator` y escribirle a GDI con ese log. **No forzar** el arranque |
| Un contenedor en `Restarting` | falta una variable del `.env` | `gdi logs <servicio>` dice cuál; completarla y `gdi up -d` |
| Fallan cosas sueltas (base, login) después de editar el `.env` desde Windows | fines de línea de Windows | `sed -i 's/\r$//' .env` y `gdi up -d` |

### Licencia

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `No se pudo escribir la licencia … Permission denied` | `license/` no es del uid 999 | `sudo chown 999:999 /opt/gdi/license && gdi restart backoffice-back` (el código se puede volver a canjear) |
| `Heartbeat: error de red`, `Name or service not known` o timeout | el servidor no llega a `license.gdilatam.com:443` | revisar DNS y firewall de salida (sección 1.5) |
| "El sistema no puede leer el archivo de licencia" | permisos del `.lic` | `sudo chown -R 999:999 /opt/gdi/license && sudo chmod 644 /opt/gdi/license/*.lic`; se destraba solo en un minuto |
| El vencimiento en *Mi Licencia* no se mueve nunca | falta `GDI_LICENSE_HEARTBEAT_URL` o no hay `.lic` | `grep GDI_LICENSE_HEARTBEAT_URL .env` tiene que aparecer sin `#` adelante; `gdi up -d` |

### Proxy y certificados

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `Let's Encrypt no emitio` y el motivo habla de DNS o de un desafío | el dominio no resuelve a `<IP>` o el puerto 80 está cerrado | `dig +short <dominio>`; abrir el 80; volver a correr el script (no repide lo ya emitido) |
| `Let's Encrypt no emitio` con `too many certificates already issued` | se agotó el cupo semanal (5) | esperar a que se libere (7 días desde la emisión más vieja). No reintentar |
| `Let's Encrypt no emitio` con `data/meta must NOT have additional properties` | el proxy no es la versión que fija el compose | volver `jc21/nginx-proxy-manager` a la versión del compose y `gdi up -d` |
| Primer login: el sitio carga, Auth0 pide la clave y vuelve con **502** | faltan los buffers del proxy | volver a correr `configurar-proxy.sh` |
| `Invalid email or password` al correr el script | no son las credenciales del administrador del proxy | usar las de `npm-admin.txt` |

### Login y usuarios

| Síntoma | Causa | Qué hacer |
|---|---|---|
| "callback mismatch" | la Callback URL de Auth0 no coincide | 4.3: `https://<dominio>/auth/callback`, exacto |
| "Client is not authorized to use this connection" | la aplicación no tiene la conexión habilitada | 4.4 |
| El BackOffice recarga en bucle; el log dice `No se pudo obtener email del token` | falta la Action del email, o la sesión es anterior a crearla | 4.6; cerrar sesión y volver a entrar |
| Al crear un usuario: "Sistema de autenticación no disponible" | falta la aplicación M2M | 4.7; confirmar con `gdi logs backoffice-back \| grep FALTA` |
| No se puede cerrar sesión | Logout URLs de Auth0 | 4.3 |
| No entra al Panel teniendo usuario | el mail no está en `PANEL_ADMIN_EMAILS` | agregarlo y `gdi up -d` |
| El Panel abre pero no lista municipios | `SUPERADMIN_KEY` vacía | `sudo ./scripts/generar-claves.sh` y `gdi up -d` |
| El usuario nunca recibe el mail de activación | no hay correo, o el SMTP rechaza | paso 5 (correo); mientras tanto, usar el enlace que muestra la pantalla |
| Error de CORS en el navegador | `FRONTEND_URL` / `BACKOFFICE_URL` mal | tienen que ser los dominios exactos, con `https://` |

### Asistentes de IA (MCP)

| Síntoma | Causa | Qué hacer |
|---|---|---|
| Auth0 muestra *"Oops!, something went wrong"* y en *Monitoring → Logs* dice `Service not found: https://mcp.<BASE>/` | falta la API del MCP | 4.8 c). Si el log muestra la dirección **sin** barra final, crear la API con ese identificador exacto |
| El asistente dice `dynamic client registration is disabled` | DCR apagado | 4.8 a) |
| El login del asistente solo ofrece usuario y contraseña (falta Google) | `google-oauth2` no está promovida | 4.8 b) |
| El empleado se loguea pero el asistente no puede hacer nada (401) | faltan los permisos por defecto de la API del MCP | 4.8 d) |

### Documentos

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NoSuchBucket` al subir un documento | los buckets no se crearon, o falta `S3_FORCE_PATH_STYLE=true` | `gdi logs minio-init`; revisar el `.env` |
| La URL de un documento tiene el bucket como subdominio (`https://gdi-oficial.storage.<BASE>/…`) | falta `S3_FORCE_PATH_STYLE=true` | agregarlo y `gdi up -d` |
| `SignatureDoesNotMatch` / `AccessDenied` al abrir un PDF | `CF_R2_ENDPOINT` apunta a `minio:9000` | `CF_R2_ENDPOINT=https://storage.<BASE>` y `gdi up -d` |
| Los documentos no cargan nunca | `STORAGE_DOMAIN` falta o no coincide | `gdi exec backend getent hosts storage.<BASE>` tiene que dar una IP interna; corregir y `gdi up -d` |
| Documento firmado, pero la API da 500 "No se pudo generar URL" o el portal TAD da 404 | al `gateway` le faltan las variables `CF_R2_*` | `gdi exec gateway env \| grep CF_R2` → tienen que salir tres; si no, el instalador está desactualizado |
| Ningún documento se firma y `gdi logs notary` dice `host no permitido` | `STORAGE_DOMAIN` desalineado con `CF_R2_ENDPOINT` | alinearlos y `gdi up -d` |
| Un tipo de documento nuevo tarda en aparecer | caché sin Redis | `gdi ps redis` → `healthy` |
| Después de firmar, "Ver Documento" muestra el documento como pendiente y el visor dice "No se pudo abrir" (versión 2026.09.9) | la pantalla muestra un estado viejo; el documento **sí** quedó firmado | salir y volver a entrar al documento. Se corrige en una próxima versión |

---

¿Trabado en algo que no está acá? Escribile a soporte de GDI Latam con la salida de `gdi ps` y
`gdi logs --tail=200 <servicio>`.
