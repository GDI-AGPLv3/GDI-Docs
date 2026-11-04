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
proveedor soportado hoy (Keycloak dentro del compose está planificado).

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
| Disco | 80 GB (crece con los documentos si usás el almacenamiento local) |
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
| `storage.<BASE>` | documentos (almacenamiento local). **Solo con almacenamiento local**; con Cloudflare R2 son 6 |

**CHECK** (desde cualquier máquina): `dig +short gdi.<BASE>` y los otros seis devuelven `<IP>`.

### 1.5. Salida a internet (HTTPS, puerto 443)

| Destino | Para qué | Cuándo |
|---|---|---|
| `ghcr.io` y `pkg-containers.githubusercontent.com` | instalador e imágenes de GDI | al instalar y actualizar |
| `registry-1.docker.io` | proxy y Redis | al instalar y actualizar |
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
`docker-compose.storage.yml`, `.env.example`, `scripts/` y `docs/`, y
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
*Applications → APIs →* **Create API**

- **Name:** `GDI API`
- **Identifier:** `https://gdi-api`. Es un identificador, **no una URL real**. Va a `AUTH0_AUDIENCE`.
- Signing algorithm: RS256.
- **Access Policy → Within user-delegated access: All apps allowed.** Auth0 trae por defecto
  *Per-app authorization* en las APIs nuevas: con eso **nadie puede loguearse** en GDI.
- **Create**.

> Al crear la API, Auth0 agrega sola una aplicación "GDI API (Test Application)", de tipo Machine
> to Machine y con acceso a la API sin usuario. No se usa: **borrala** (*Applications →
> Applications*).

### 4.3. Tres aplicaciones de login
*Applications → Applications →* **Create Application** → **Regular Web Application**, tres veces:

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

1. *Actions → Library →* **Create Action → Create Custom Action** (en versiones viejas del panel
   el botón se llama *Build Custom*): nombre `GDI - email en el access token`, trigger
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
*Applications → Create Application →* **Machine to Machine**

- Autorizarla contra **Auth0 Management API** (la que viene de fábrica, **no** la del 4.2).
- Permisos: `read:users`, `create:users`, `update:users`, `create:user_tickets`. Exactamente esos.
- Su Client ID / Secret van a `AUTH0_M2M_CLIENT_ID` / `AUTH0_M2M_CLIENT_SECRET`.

> En el plan gratuito de Auth0 las aplicaciones Machine to Machine tienen un tope de **5.000
> tokens por mes**. GDI pide uno solo cuando crea o modifica usuarios, así que alcanza de sobra.
> Si el panel de Auth0 avisa que se acerca al tope, revisá que nada externo esté usando esa
> aplicación.

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
para su propia dirección. *Applications → APIs →* **Create API**:

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

> Al crear la API del punto c), Auth0 agrega sola una aplicación "GDI MCP (Test Application)",
> de tipo Machine to Machine y con acceso a la API sin usuario. No se usa: **borrala**.

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

> **Un `$` sin comillas** en un valor (`AUTH0_SECRET=abc$def`) lo interpreta Docker Compose como una
> variable, pero el instalador lo lee tal cual: el instalador **avisa** el nombre de la variable. Ponelo
> entre comillas dobles con el `$` escapado.
>
> **Formato de los valores.** El `.env` lo leen Docker Compose y los scripts de `scripts/` con las
> **mismas reglas**: un valor con `#` precedido de espacio, con `$`, con comillas, con una barra `\` o con
> espacios al borde va entre **comillas dobles** y escapa `\`, `"` y `$` con una barra (`"clave #1 \$x"`).
> Entre comillas simples (`'...'`) el valor es literal. Sin comillas, el valor termina en el primer ` #`.
> Los valores simples (letras, números, `@`, `.`, `-`) van sin comillas.

```bash
cd /opt/gdi
cp .env.example .env
chmod 600 .env
sudo ./scripts/generar-claves.sh
```

`generar-claves.sh` genera las claves internas, la contraseña de la base y las **dos cuentas del
almacenamiento** (la administradora, que solo se usa al arrancar, y la de la aplicación, que solo
ve sus propios buckets), y deja la carpeta `license/` con el dueño correcto (uid 999). Se puede
correr de nuevo sin riesgo: solo completa las claves que faltan (vacías o en `CAMBIAR`); las que
ya tienen valor no las toca.

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

# Almacenamiento local (las claves ya las puso generar-claves.sh; S3_REGION=us-east-1 ya viene)
CF_R2_ENDPOINT=https://storage.<BASE>         # el dominio PÚBLICO, nunca http://storage:7070
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

El remitente es **obligatorio** si configurás correo (no hay uno por defecto: el de GDI no te sirve, tu dominio no
lo autoriza). Con Resend va `FROM_EMAIL`; con SMTP, `SMTP_FROM` o, si no, `FROM_EMAIL`. Si falta, el instalador
corta con un mensaje que lo nombra.

**Cloudflare R2 en lugar del almacenamiento local:** usá el bloque "Opción B" del `.env.example`,
sin `STORAGE_DOMAIN` ni `S3_REGION`, y en los pasos 7 y 8 sacá `docker-compose.storage.yml` y el
host `storage.`.

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
gdi() { ( cd /opt/gdi && docker compose -f docker-compose.yml -f docker-compose.premium.yml -f docker-compose.storage.yml "$@" ); }
gdi up -d
```

La primera vez tarda unos minutos (baja las imágenes). En el resto del manual, **`gdi up -d`**
es este comando. La función dura lo que la sesión SSH: para dejarla fija, copiá esa misma línea
`gdi() { … }` a `~/.bashrc`. Corre siempre en `/opt/gdi` sin cambiarte de carpeta.

> ⚠️ **`gdi` no existe fuera de tu sesión.** En un `cron`, en un script o con `sudo` hay que
> escribir el comando completo (`docker compose -f … -f … -f …`): es lo que pasa con el backup
> automático del [paso 13](#13-backups).

**CHECK** (1 o 2 minutos después):

```bash
gdi ps -a --format '{{.Service}}\t{{.Status}}'
```

- `migrator`, `storage-users` y `storage-init` → **Exited (0)**. Cualquier otro código → [14](#14-problemas).
- Todos los servicios de larga vida (`postgres`, `redis`, `storage`, `backend`, `backend-worker`, `gateway`, `frontend`, `pdfcomposer`, `notary`, `npm` y los del premium) → `healthy` (desde esta versión todos traen healthcheck; antes faltaban varios). `autoheal` y `autoheal-proxy` → `Up`; se explican en [7.1](#71-reinicio-automatico-de-servicios-colgados-autoheal).

```bash
gdi logs storage-init | tail -1
```

- Tiene que decir `[OK] buckets listos: gdi-avatars, gdi-assets (lectura publica), gdi-certificates (privado)`.
- El resto → `Up`. Ninguno en `Restarting`.

```bash
gdi logs backoffice-back | grep -E '\[OK\]|\[FALTA\]|Licencia ACTIVADA'
```

- Tiene que aparecer `Licencia ACTIVADA contra el Panel: GDI-… para <municipio>`.
- Tiene que aparecer `[OK] Alta de usuarios: credenciales de Auth0 presentes`.
- `[FALTA] Correo NO CONFIGURADO` es esperable si no configuraste correo.
- Si dice `No se pudo escribir la licencia … Permission denied` → [14](#14-problemas).

### 7.1. Reinicio automático de servicios colgados (autoheal)

Docker reinicia un contenedor solo si el **proceso muere**. Si queda vivo pero sin responder (por
ejemplo, el worker de firma trabado), lo marca `unhealthy` y no hace nada: sin nadie mirando, la
firma queda frenada hasta que alguien entra por SSH. El servicio **`autoheal`** cierra ese hueco:
cada 10 segundos reinicia los contenedores que están `unhealthy` y que tienen la etiqueta
`autoheal=true`. Viene incluido y encendido; no hay que instalar nada.

**Qué se vigila.** Cada servicio tiene su `healthcheck`. El tiempo es el peor caso hasta que Docker
lo marca `unhealthy` (más ~10 s de autoheal y lo que tarda en volver a levantar):

| Servicio | Qué comprueba | Hasta `unhealthy` | Se reinicia solo |
|---|---|---|---|
| `backend` | responde `/health` (el event loop atiende) | 60 s | sí |
| `backend-worker` | `/health` del worker: 503 si la cola de firma, el webhook de TAD o el scheduler están caídos; sin respuesta si el proceso está trabado | 100 s | sí |
| `gateway` | responde el manifiesto MCP | 60 s | sí |
| `pdfcomposer` | responde `/health` (el proceso atiende). A propósito **no** usa `/health/details` (que genera un PDF de prueba): ese espera turno detrás de los PDF reales y, con muchas firmas a la vez, haría reiniciar un servicio sano. Para ver si el motor genera PDF: `/health/details` a mano | 60 s | sí |
| `notary` | `/health`: el pipeline de firma puede firmar (503 si no) | 69 s | sí |
| `frontend`, `backoffice-front`, `panel-front` | responde la API de estado de Next.js | 60 s | sí |
| `backoffice-back`, `panel-back` | responde `/health` | 60 s | sí |
| `agentelang` | `/health` con consulta real a la base + estado de su worker de IA (`stale`/`dead`) | 84 s | sí |
| `npm` (proxy) | la API de administración **y** nginx contestando en el puerto 80 | 90 s | sí |
| `storage` | `/health` del almacenamiento local | 60 s | sí |
| `postgres`, `redis` | `pg_isready` / `PING` | — | **no** |

**Qué NO se reinicia solo, y por qué.** `postgres` y `redis` tienen estado propio: reiniciar una base
en caliente obliga a recuperarla y, si el chequeo falló por *carga* y no por cuelgue, la deja peor;
esa decisión es de una persona. Los pasos que corren una vez y terminan (`migrator`, `storage-users`,
`storage-init`) no se vigilan. Tampoco se reinicia un servicio que **está parado a mano**
(`gdi stop …`) ni uno que ya está en `Restarting`.

**Si la base no está, no se reinicia nada por eso.** `backend-worker` y `agentelang` dependen de
Postgres: si no responden *y además* Postgres no acepta conexiones (se cayó, o se cortó el enlace
al servidor de datos), reiniciarlos no arregla nada y solo mete ruido. En ese caso el chequeo
**pasa** y deja escrito el motivo (`docker inspect --format '{{json .State.Health}}' <contenedor>`).
Con la base arriba y el servicio trabado, sí se reinicia.

**Cómo ver qué reinició.**

```bash
gdi logs --since 24h autoheal                          # una línea por reinicio (y por aviso enviado)
docker events --since 24h --filter event=restart       # historial del daemon, con la hora
gdi ps --format '{{.Service}}\t{{.Status}}'            # "Up 5 minutes (healthy)"; "(unhealthy)" = hoy está mal
docker inspect --format '{{json .State.Health}}' <contenedor>   # los últimos chequeos y su salida
```

Cada reinicio manda además **un mail a `ALERT_TO_EMAIL`**, por el mismo proveedor que las demás
alertas (Resend o SMTP, sección 5). Para no llenar la casilla: un mail por servicio cada 15 minutos;
y si el mismo servicio se reinicia **3 veces en 30 minutos**, llega un mail aparte, **«URGENTE»**,
porque ahí reiniciar no lo está arreglando y tiene que mirarlo una persona (`gdi logs --tail=200
<servicio>`). Si después sigue reiniciándose (nunca pasa media hora sin un reinicio), no llegan
más mails comunes de ese servicio: llega **«SIGUE EN BUCLE: <servicio> lleva N reinicios desde
<fecha>»** como máximo **una vez por hora** (`AUTOHEAL_LOOP_REMIND`, en segundos), hasta que se
arregle. Así un servicio que se cuelga toda la noche no queda en silencio después del primer
aviso. Sin `ALERT_TO_EMAIL`, o sin correo configurado, queda solo el log. Opcionalmente, un
webhook JSON (Slack, Mattermost, ntfy): `AUTOHEAL_WEBHOOK_URL` en el `.env`.

**Cómo desactivarlo.** Sin tocar el compose: en el `.env`, `AUTOHEAL_LABEL=autoheal-apagado`, y
`gdi up -d autoheal`. Sigue corriendo pero no coincide con ningún servicio, así que no reinicia
nada. Para volver: borrar esa línea y repetir. Para frenarlo del todo hasta el próximo `gdi up -d`:
`gdi stop autoheal autoheal-proxy`. Los demás valores (intervalo, esperas, avisos) están
comentados en `.env.example`, sección «Reinicio automático».

**Seguridad.** Reiniciar contenedores exige hablar con el daemon de Docker, y eso es poder de root
sobre el servidor. Por eso `autoheal` **no** monta `docker.sock`: lo monta `autoheal-proxy`
(Tecnativa/docker-socket-proxy), en una red interna sin salida a internet que solo ve `autoheal`, y
el proxy deja pasar únicamente *listar contenedores* y *stop/restart/kill* (nada de crear
contenedores, `exec`, volúmenes ni imágenes). Aun así puede detener cualquier contenedor del
servidor, y `autoheal` recibe las credenciales de correo para avisar. Ambas imágenes están
fijadas por *digest*; no las cambies a un tag.

**Prueba (después de instalar y antes de dar por terminado el paso 7).** Congela el worker de firma
y mirá que el sistema lo recupera solo en menos de 2 minutos:

```bash
C=$(gdi ps -q backend-worker)
docker pause "$C"                       # simula un cuelgue: el proceso sigue vivo pero no responde
watch -n 5 "docker inspect --format '{{.State.Health.Status}} reinicios-de-docker={{.RestartCount}}' $C; docker events --since 3m --until 1s --filter event=restart"
```

**CHECK:** a los ~100 s pasa a `unhealthy`, en los 10 s siguientes `gdi logs --tail=5 autoheal` dice
`found to be unhealthy - Restarting container`, y a los pocos segundos vuelve a `healthy` y a
contestar. Si en 3 minutos no se reinició, ver [14](#14-problemas) («autoheal no reinicia»). No hace
falta `docker unpause`; si el contenedor quedará en pausa después del reinicio, `docker unpause "$C"`.

### 7.2. Recursos por contenedor (CPU y memoria)

Cada servicio tiene un **tope de CPU** y se le puede poner uno de **memoria**. Sin topes, una
tanda de firmas (PDFComposer y Notary son CPU pura) le saca la CPU al backend —todos los clics se
ponen lentos— y a la base; y un servicio con una pérdida de memoria puede hacer que el kernel mate a
**Postgres**. Con un tope de memoria, el que se pasa muere **solo él** y Docker lo vuelve a levantar.

- **No hay que tocar nada para instalar.**
  - **CPU:** los defaults andan en el servidor mínimo de la [sección 1.3](#13-el-servidor) y ninguno
    pasa de 2 núcleos. Un tope de CPU **frena, no mata**: el servicio va más lento cuando se pasa, no
    se cae.
  - **Memoria: por defecto SIN TOPE** (`0`), como en las versiones anteriores. Un tope de memoria sí mata:
    si es más bajo de lo que el servicio necesita en un pico (una importación grande de PDF, la IA),
    el kernel lo corta aunque al servidor le sobre RAM. Con un solo municipio GDI usa ~2,1 GB en
    total, así que no hace falta ponerlos para que ande.
- **Cuándo conviene ponerlos de memoria:** si el servidor lo comparten varios servicios o varios
  municipios, o si tiene poca RAM. Ahí usá la tabla de abajo como punto de partida.
- La **base no tiene tope de memoria** a propósito (matarla tira todo GDI). Tiene una **reserva**
  (ante falta de RAM, el kernel recorta primero a los demás) y **prioridad de CPU**, igual que el
  backend y el gateway (`*_CPU_SHARES=2048`; lo normal es 1024).
- **Postgres también se dimensiona** (`POSTGRES_PERFIL`, opcional): Postgres de fábrica trae
  `shared_buffers` de 128 MB aunque el servidor tenga 32 GB. Con `POSTGRES_PERFIL=1gb`, `2gb`, `4gb`
  u `8gb` (según la memoria que le das a la base; los archivos están en `postgres/`) el instalador
  desatendido aplica `max_connections`, `shared_buffers`, `effective_cache_size`, `work_mem` y
  `maintenance_work_mem` con `ALTER SYSTEM` y reinicia la base solo si algún parámetro lo pide. Queda
  guardado dentro del volumen (sobrevive a reinicios y a `gdi up -d`) y correrlo de nuevo no cambia
  nada. Sin la variable, la base queda con los valores de fábrica, como hasta ahora. El perfil `8gb`
  sale de la misma receta que los otros (25 % y 75 %) y no está medido.
  La base además tiene `stop_grace_period: 60s` (un apagado con `shared_buffers` grande hace un
  checkpoint que tarda más que los 10 s de fábrica: cortado, la próxima vez arranca con recuperación de
  crash) y `shm_size: 256m` (`POSTGRES_SHM_SIZE`; el `/dev/shm` de Docker es de 64 MB y las consultas
  paralelas usan memoria compartida dinámica).
- Se cambian en el `.env` (bloque «Recursos por contenedor» de `.env.example`) y se aplican con
  `gdi up -d`, que recrea solo los servicios que cambiaron. `0` = sin tope.
- ⚠️ Un tope de CPU **mayor que los núcleos del servidor** no deja arrancar ese servicio
  (`range of CPUs is from 0.01 to N`). Por eso ningún default pasa de 2.
- **Aviso cuando un servicio muere por memoria.** El servicio `autoheal-oom` (viene en todas las
  instalaciones) escucha los eventos `oom` de Docker y deja una línea en `gdi logs autoheal-oom` y,
  si hay correo configurado, manda el mismo mail que los reinicios de autoheal («murió por falta de
  memoria (OOMKilled)»), con el mismo anti-ruido. Docker levanta solo al servicio muerto; sin este
  aviso nadie se enteraba. Escucha por el proxy de autoheal (`EVENTS` en solo lectura); al terminar, el
  instalador verifica que no esté reconectando en bucle (`RestartCount` en 0 y sin «reconecto» en el log) y
  si lo está avisa que **el aviso de OOM no está funcionando**.

**Valores de memoria por tamaño de servidor.** La memoria por defecto es `0` (sin tope); esta tabla
es lo que se puede poner. Los de CPU son los defaults. Vacío = dejar el default.

| Variable | Default (4 vCPU / 8 GB) | Chica: 4 vCPU / 16 GB (sin almacenamiento local ni Panel) | Mediana: 8 vCPU / 32 GB (varios municipios) |
|---|---|---|---|
| `POSTGRES_MEM_RESERVA` | 512m | 2g | 8g |
| `POSTGRES_CPUSET` / `APP_CPUSET` | — (todos comparten) | — | `0,1` / `2-7` (2 núcleos solo para la base) |
| `BACKEND_CPUS` / `BACKEND_MEM` | 2 / sin tope | 2 / 2g | 2 / 3g |
| `BACKEND_WORKER_CPUS` / `_MEM` | 2 / sin tope | 1 / 1g | 1.5 / 2g |
| `GATEWAY_CPUS` / `GATEWAY_MEM` | 2 / sin tope | 2 / 1g | 2 / 1536m |
| `PDFCOMPOSER_CPUS` / `_MEM` | 2 / sin tope | 1.5 / 1536m | 1.5 / 2g |
| `NOTARY_CPUS` / `NOTARY_MEM` | 2 / sin tope | 1.5 / 1536m | 1.5 / 2g |
| `AGENTELANG_CPUS` / `_MEM` | 2 / sin tope | 1 / 1536m | 1 / 2560m |
| `FRONTEND_CPUS` / `_MEM` | 1 / sin tope | 1 / 768m | 1 / 1536m |
| `BACKOFFICE_BACK_CPUS` / `_MEM` | 1 / sin tope | 1 / 1g | 1 / 1g |
| `BACKOFFICE_FRONT_CPUS` / `_MEM` | 1 / sin tope | 0.5 / 512m | 0.5 / 768m |
| `REDIS_CPUS` / `REDIS_MEM` / `REDIS_MEM_RESERVA` | 1 / sin tope / 128m | 0.5 / 256m / 64m | 0.5 / 1g / 256m |
| `NPM_CPUS` / `NPM_MEM` | 1 / sin tope | 0.5 / 384m | 0.5 / 512m |
| `STORAGE_CPUS` / `STORAGE_MEM` | 1 / sin tope | (sin almacenamiento local) | (sin almacenamiento local) |
| `PANEL_BACK_*` / `PANEL_FRONT_*` | 0.5 / sin tope | (sin Panel) | (sin Panel) |

Los topes de CPU **suman más que los núcleos** a propósito: son un techo por servicio, no un
reparto. Lo que reparte cuando todos piden a la vez es la prioridad (`*_CPU_SHARES`) y, en la
mediana, los núcleos propios de la base. **`POSTGRES_CPUSET` sin `APP_CPUSET` no reserva nada**:
la base queda en esos núcleos pero las aplicaciones también los usan.

⚠️ **Si ponés topes de memoria, la suma puede pasar la RAM**, y ahí el sobrecompromiso tiene un
límite. Medido con `docker compose config` (en GiB, con la reserva de la base y los dos `autoheal`;
los servicios sin tope **no suman**, así que sin topes la suma da poco y eso no la hace segura):

| Combinación de archivos | Suma de topes |
|---|---|
| `premium` + `storage`, defaults (memoria sin tope) | ≈0,9 (la base reserva 0,5; los demás no suman) |
| `premium` + `storage`, con los valores que tenía el compose antes (2g, 3g...) | ≈20,2 |

En el uso normal no importa (medido: ~2,1 GB en uso), pero el tope protege a cada servicio de **sí
mismo**, no al servidor: si varios se acercan a su tope a la vez (tanda de firmas + IA), la
**máquina** se queda sin RAM y el kernel elige a quién matar, y puede ser **Postgres** (la reserva
le da prioridad, no inmunidad).

- **Un servidor de 8 GB (o de 4, el mínimo de la [sección 1.3](#13-el-servidor)) arranca con los
  defaults**: Docker no compara la suma de topes con la RAM, y un tope es un techo que no consume
  nada hasta que el servicio lo usa. Si ponés topes, pueden sumar más que la RAM sin problema en el
  uso normal.
- **El instalador desatendido compara solo** (`scripts/memoria-compose.py`): suma los topes del
  compose ya fundido (el tope de cada servicio o, si no tiene, su reserva: la base) y los compara con
  `MemTotal` de `/proc/meminfo` menos **1 GiB** para el sistema (kernel, sshd, el demonio de Docker
  y la caché de archivos). En **modo onpremise** solo **avisa** y sigue; corta únicamente si el
  exceso es grosero: la suma supera **10 veces** la RAM disponible, o sea un servidor de menos de
  ~3 GB, que no alcanza ni para el uso normal.
- A mano, en cualquier modo: `gdi config --format json | python3 scripts/memoria-compose.py
  --compose-json - --ram-kib "$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"`. O sumá los `*_MEM`
  efectivos más `POSTGRES_MEM_RESERVA` y comparalo con `free -g`.
- Ninguno de los valores de la tabla se midió bajo carga: son un punto de partida. Si un servicio
  muere por memoria, subile el tope a ese y bajá otro.
- Señal de que pasó: `journalctl -k | grep -i 'out of memory'` muestra al kernel matando un proceso
  que no estaba en su tope (OOM del servidor, no del contenedor); `gdi logs autoheal-oom` muestra los
  que mató por superar su propio tope.

**CHECK:**

```bash
gdi config | grep -E '^  [a-z-]+:$|cpus:|memory:|cpuset:' | head -60   # cada servicio con su tope
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
gdi ps --format '{{.Service}} {{.State}}' | grep autoheal-oom            # el aviso de OOM está corriendo
```

En `docker stats`, la columna de memoria muestra `uso / tope`; sin tope muestra la RAM entera del
servidor. Para saber si un servicio murió por memoria:
`docker inspect -f '{{.State.OOMKilled}}' $(gdi ps -q <servicio>)` → `true`. Si se repite, ponele
un `*_MEM` más alto a ese servicio.

#### Firmas en paralelo

La firma rinde según **cuántas firmas van a Notary a la vez**, no según la CPU: cada firma pasa
~2,5 s en Notary y casi todo es espera de red. Con 1 a la vez salen ~20 firmas por minuto; con 16,
~180 (medido por GDI Latam en un ambiente de prueba). Tres perillas, que van juntas:

| Variable | Servicio | Default | Chica | Mediana |
|---|---|---|---|---|
| `ESCRI_CONCURRENCY` | `backend-worker`: firmas que procesa la cola a la vez | 4 | 4 | 8 |
| `NOTARY_SIGN_MAX_CONCURRENT` | `backend-worker`: firmas que deja ir a Notary a la vez | = `ESCRI_CONCURRENCY` | 4 | 8 |
| `NOTARY_BACKGROUND_MAX_CONCURRENT` | `notary`: firmas por worker de Notary | 2 | 2 | 4 |

- **Regla:** `NOTARY_SIGN_MAX_CONCURRENT` ≤ `NOTARY_WORKERS` × `NOTARY_BACKGROUND_MAX_CONCURRENT`.
  Si no, Notary contesta 503 (BACKGROUND_BUSY) y las firmas se reintentan.
- **Notary necesita memoria:** con 512 MB se queda sin memoria con 16 firmas a la vez. Con 8, darle 1 GB o más.
- Más firmas a la vez no ahorran nada si el servidor no las pide: solo suben el techo en un pico.

```bash
gdi exec backend-worker env | grep -E 'ESCRI_CONCURRENCY|NOTARY_SIGN_MAX'   # lo que tomó el worker
```

#### Procesos del Gateway y reciclado

Backend y Gateway corren con gunicorn: varios procesos de Python y uno que los vigila. Cada proceso se
**recicla** (se apaga y arranca uno nuevo) después de atender una cantidad de pedidos, para devolver la
memoria que Python no suelta solo. Mientras uno se recicla, queda un proceso menos atendiendo.

| Variable | Servicio | Default |
|---|---|---|
| `GATEWAY_WORKERS` | `gateway`: procesos | 2 |
| `GATEWAY_MAX_REQUESTS` / `GATEWAY_MAX_REQUESTS_JITTER` | `gateway`: pedidos por proceso antes de reciclar (+ un azar de 0 a jitter) | 50000 / 50000 |
| `BACKEND_MAX_REQUESTS` / `BACKEND_MAX_REQUESTS_JITTER` | `backend`: lo mismo | 50000 / 50000 |

- Vacío = el default de la imagen. En versiones anteriores era 2000 + 2000: con mucha carga el Gateway
  se reciclaba cada 30-50 s y daba errores 502 sueltos.
- **Regla del jitter:** jitter ≥ 1,5 × pedidos por segundo × segundos de separación que querés entre dos
  reciclados. Con jitter chico los dos procesos se reciclan juntos y el servicio se queda sin nadie.

```bash
gdi logs --since 30m gateway | grep -c 'Booting worker'   # reciclados en la última media hora
```

#### Pool de conexiones a la base: pgbouncer (opcional, apagado de fábrica)

pgbouncer es un portero entre la aplicación y la base: ordena las conexiones para que la base no se sature.
Sirve cuando hay mucho uso o varias copias del backend. Con el uso de un municipio normal no hace falta.

Para prenderlo:
1. Poné `PGBOUNCER_ACTIVO=true` en el `.env`.
2. Corré de nuevo el instalador (Anexo B). El instalador suma `docker-compose.pgbouncer.yml` y apaga el `jit` de la base.

Qué cambia:
- `backend` y `gateway` van a la base por `pgbouncer:6432`. `backend-worker`, BackOffice y AgenteLANG siguen directo.
- pgbouncer usa a lo sumo `PGBOUNCER_POOL_SIZE` + 5 conexiones reales de Postgres (default 30 + 5).
- Si operás a mano, sumá `-f docker-compose.pgbouncer.yml` al final de tu función `gdi()`. Si no, el próximo
  `gdi up -d` vuelve a conectar backend y gateway directo.

```bash
gdi exec gateway printenv DB_HOST DB_PORT    # con pgbouncer: pgbouncer 6432
```

Para apagarlo: `PGBOUNCER_ACTIVO=false` y correr de nuevo el instalador.

### 7.3. Rotación de logs

Docker guarda la salida de cada contenedor en un archivo (`json-file`) que **no rota por defecto**:
un servicio hablador, o uno que se reinicia en bucle, llena el disco del servidor y se lleva puesta a
la base. Todos los servicios de GDI limitan su log a **5 archivos de 10 MB (50 MB por contenedor)**.
`docker logs` y `gdi logs` andan igual; lo más viejo se descarta. Se cambia con `LOG_MAX_SIZE` y
`LOG_MAX_FILE` en el `.env` y se aplica con `gdi up -d`.

**CHECK:** `gdi config | grep -A3 'logging:' | head -20` muestra `max-size: 10m` y `max-file: "5"`.

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
./scripts/configurar-proxy.sh                   # con R2: SIN_STORAGE=1 ./scripts/configurar-proxy.sh
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
         mcp.<BASE>/health panel.<BASE> storage.<BASE>/health; do
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
gdi exec -T storage ls /srv/data
# → gdi-avatars, gdi-assets, gdi-certificates y 4 buckets por instancia:
#   gdi-<sigla>-oficial, -tosign, -preoficial y -publico
gdi logs backoffice-back | grep -E "CORS de subida directa|SIN CORS"
# → "CORS de subida directa ok" una vez por instancia. "SIN CORS" = nadie va a poder importar
#   PDF ni adjuntar archivos desde la pantalla: ver 14.
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

> 🛑 **Primero el backup** (paso 13). Una actualización aplica migraciones a la base: volver a
> las imágenes anteriores **no** revierte la base. La única vuelta atrás es restaurar ese backup.

GDI avisa por mail cuando hay una versión nueva. **Nada se actualiza solo**: el municipio elige
el día y la hora, fuera del horario de atención. El sistema queda cortado **uno o dos minutos**
(entre el `up` del punto 5 y que los servicios vuelven a estar `healthy`); la bajada de imágenes
del punto 4 no corta nada.

```bash
cd /opt/gdi
# 1. Backup completo (paso 13), copiado FUERA del servidor, y verificar que no quedó vacío.
# 2. La versión nueva (el número que vino en el aviso de GDI). Anotá también la actual:
#    es a la que se vuelve si algo sale mal.
NUEVA=2026.MM.NN                                 # ← el número real, sin < >
grep ^IMAGE_VERSION= .env | tee backups/version-anterior.txt
[[ $NUEVA =~ ^[0-9]{4}\.[0-9]{2}\.[0-9]+$ ]] && echo "OK $NUEVA" || echo "FALTA el número en NUEVA"
# 3. El instalador de la versión nueva. Pisa compose, scripts y manual; NO toca .env ni license/.
docker run --rm <IMAGEN_INSTALADOR>:$NUEVA | tar x -C /opt/gdi
# ¿Trae variables nuevas? Lista las que están en el ejemplo y no en tu .env:
comm -23 <(grep -oE '^[A-Z0-9_]+=' .env.example | sort -u) <(grep -oE '^[A-Z0-9_]+=' .env | sort -u)
sed -i "s/^IMAGE_VERSION=.*/IMAGE_VERSION=$NUEVA/" .env
# 4. Imágenes nuevas. No corta nada: los servicios siguen andando con las anteriores.
gdi pull
# 5. Contenedores nuevos (el migrator aplica las migraciones antes del backend).
gdi up -d
# 6. La configuración del proxy de la versión nueva. No pide certificados nuevos: los que ya
#    existen se conservan. (Desde 2026.09.15 evita que storage.<BASE> quede en 502 al actualizar.)
set -a; . ./npm-admin.txt; set +a
./scripts/configurar-proxy.sh                   # con R2: SIN_STORAGE=1 ./scripts/configurar-proxy.sh
```

- **Una etiqueta por servicio en el `.env`** (`BACKEND_TAG=`, `FRONTEND_TAG=`, etc.) manda sobre
  `IMAGE_VERSION`: ese servicio **no** toma la versión nueva. El instalador desatendido lo avisa con
  `AVISO: el .env fija etiqueta propia para …`. Si no la pusiste a pedido de GDI, borrá esa línea.
- **El `comm` del punto 3 lista algo** → el aviso de la versión dice qué valor lleva cada
  variable nueva. Agregala al `.env` con `nano .env` antes del punto 5. Si no lista nada, no hay
  variables nuevas.
- **El `pull` falla a la mitad** (red, token vencido) → todavía no cambió nada que importe: los
  servicios siguen con la versión anterior. Repetí `gdi pull` hasta que termine. Si no se puede
  hoy, dejá todo como estaba: `docker run --rm <IMAGEN_INSTALADOR>:<la anterior> | tar x -C /opt/gdi`
  y el `sed` del punto 3 con ese número (el que guardaste en `backups/version-anterior.txt`).
- **Saltar versiones** (de la `.13` a la `.15` sin pasar por la `.14`) se puede: el migrator
  aplica en orden todas las migraciones pendientes. Si una versión exige pasar por otra, el aviso
  de GDI lo dice.

**CHECK:** el mismo del paso 7, y además `curl -s https://panel.<BASE>/api/version | jq -r .paquete`
→ el número de `NUEVA`. Entrá al portal, abrí un expediente y firmá un documento de prueba: si algo
quedó mal, es ahora cuando querés enterarte, con el backup fresco.

### 12.1. Volver atrás

Volver atrás **es restaurar el backup del punto 1** con la versión anterior. Se pierde **todo** lo
que se cargó después de ese backup, y los números de documento emitidos en el medio **se vuelven a
usar**. Por eso:

> ⛔ **Solo dentro de la ventana de la actualización**, antes de que los empleados trabajen con la
> versión nueva. Si ya firmaron documentos con ella, **no vuelvas atrás**: avisale a GDI, que
> corrige hacia adelante.

```bash
cd /opt/gdi
# 1. El instalador de la versión del backup (la que se guardó en el punto 2 de arriba).
ANTERIOR=$(cut -d= -f2 backups/version-anterior.txt) && echo $ANTERIOR
docker run --rm <IMAGEN_INSTALADOR>:$ANTERIOR | tar x -C /opt/gdi
# 2. Restaurar: borra base y documentos de este servidor y los reemplaza por los del backup,
#    junto con el .env (que vuelve a tener la versión anterior). Pide escribir RESTAURAR.
sudo ./scripts/restaurar.sh AAAA-MM-DD          # la fecha de los archivos del backup
# 3. El proxy de esa versión.
set -a; . ./npm-admin.txt; set +a
./scripts/configurar-proxy.sh
```

**CHECK:** el del paso 7, y `grep ^IMAGE_VERSION= .env` → la versión anterior. Firmá un documento
de prueba: tiene que salir con el número siguiente al último del backup.

> Si la versión anterior es **anterior a 2026.09.16**, su instalador no trae `restaurar.sh`.
> Antes del punto 1 copialo de la versión actual: `cp scripts/restaurar.sh backups/`, y en el
> punto 2 corré `sudo ./backups/restaurar.sh AAAA-MM-DD`.

**No alcanza con volver a las imágenes viejas ni con un `pg_restore` encima** (probado el
07/10/2026): las tablas que agregó la versión nueva quedan en la base, y los PDF firmados después
del backup quedan en el almacenamiento. El primer documento que se firma choca contra uno de esos
PDF (`r2_worm_locked_numero_contaminado`) y **la firma de ese tipo queda trabada**. `restaurar.sh`
borra la base y los documentos antes de restaurar justamente por eso.

---

## 13. Backups

> **Los backups son del municipio y van FUERA de este servidor.** Una copia en el mismo disco no
> protege de nada: si se rompe el disco o se pierde la máquina, se pierde con ella. GDI no trae un
> backup automático a propósito: el destino (un NAS, un disco externo, otro servidor, un
> almacenamiento en la nube) y la frecuencia los decide el municipio con su herramienta.
> La guía [Copias de seguridad del servidor propio](backups.md) trae un ejemplo completo,
> incremental y cifrado, con su restauración.
>
> Además, GDI puede subir **cada cambio de la base** a un almacenamiento S3, para perder como mucho
> un minuto y volver a cualquier minuto de los últimos días. Viene **apagado**: ver
> [Copia de la base minuto a minuto](copia-minuto-a-minuto.md). No reemplaza a este backup.

Un servidor perdido se recupera con **cinco** cosas:

| Qué | Dónde | Sin esto… |
|---|---|---|
| Base de datos | volumen `gdi_postgres_data` | no hay nada |
| Documentos (solo almacenamiento local) | volumen `gdi_storage_data` | la base apunta a archivos que no existen |
| `.env` | `/opt/gdi/.env` | no levanta: claves, Auth0, `CERT_MASTER_KEY` |
| Licencia | `/opt/gdi/license/` | arranca sin BackOffice ni IA hasta reactivar |
| Imágenes | el registro, o una copia local | si el token no está activo, no se puede reinstalar |

```bash
cd /opt/gdi && mkdir -p backups && FECHA=$(date +%F)
gdi exec -T postgres pg_dump -U postgres railway -Fc > backups/gdi-$FECHA.dump
gdi stop storage     # unos segundos: que no entre un documento a medio guardar
docker run --rm -v gdi_storage_data:/srv:ro -v /opt/gdi/backups:/backup redis:7-alpine tar czf /backup/documentos-$FECHA.tar.gz -C /srv .
gdi start storage
tar czf backups/config-$FECHA.tar.gz .env license/ $( [ -f npm-admin.txt ] && echo npm-admin.txt )
# Solo al actualizar (una vez por versión):
gdi images | awk 'NR>1 {print $2":"$3}' | sort -u > backups/imagenes-$FECHA.txt
docker save $(cat backups/imagenes-$FECHA.txt) | gzip > backups/imagenes-$FECHA.tar.gz
ls -lh backups/
```

Esta es la copia **puntual**, la que se hace antes de actualizar (paso 12). Deja los archivos en
`/opt/gdi/backups/` solo de paso: **copialos fuera del servidor** y borralos de acá.

**CHECK:** ningún archivo pesa unos pocos KB. Un dump de 5 KB es un error, no un backup.

Los documentos son archivos comunes (`data/<bucket>/<ruta>`) y sus datos (tipo de archivo, dueño,
lectura pública) van al lado en `meta/`: un `tar` común alcanza, no hacen falta opciones especiales.
Se copian **con el almacenamiento detenido** porque cada documento se guarda en esas dos partes: si
justo entra uno durante la copia, puede quedar una sin la otra. La base va **antes** que los
documentos: así todo lo que la base nombra ya está en la copia.

**Automatizarlo** (base + documentos + configuración, todos los días, hacia el destino del
municipio): ver la [guía de copias de seguridad](backups.md). Si se arma con `cron`, ahí
**no existe** la función `gdi`: va el comando completo.

**Reglas:** siempre **fuera** del servidor, y al menos una restauración de prueba en otra máquina.
El `.env` y el `.lic` son secretos: guardalos como contraseñas.

### 13.1. Restaurar en un servidor nuevo

Para volver atrás una actualización en el mismo servidor, ver el paso 12.1 (*Volver atrás*). Acá:
el servidor se perdió y hay que levantar GDI en otro, con el backup.

> ⛔ **En el servidor nuevo NO hagas los pasos 4 a 7.** `generar-claves.sh` inventa una contraseña
> de base nueva y `gdi up` crea la base con ella; después el `.env` restaurado trae la vieja y
> **no levanta ningún servicio** (`password authentication failed`, probado el 07/10/2026). Auth0
> ya existe (paso 4) y el `.env` viene en el backup.

1. **DNS** (sección 1.4): si el servidor nuevo tiene otra IP, cambiá los 7 registros y esperá
   a que resuelvan. Los dominios tienen que ser **los mismos**: si cambian, avisale a GDI.
2. **Pasos 2 y 3** del manual, con el instalador de **la versión del backup** (no la última).
   Si no sabés cuál es, está en el `.env` del backup:
   `tar xzf config-AAAA-MM-DD.tar.gz -O .env | grep ^IMAGE_VERSION=`.
3. **Los archivos del backup** (`gdi-…dump`, `documentos-…tar.gz` y `config-…tar.gz`) en
   `/opt/gdi/backups/`. Sin acceso al registro, también `imagenes-…tar.gz`, y antes de seguir:
   `gunzip -c backups/imagenes-AAAA-MM-DD.tar.gz | docker load`.
4. **Restaurar.** Pide escribir RESTAURAR. Baja las imágenes, crea la base con la contraseña del
   `.env` del backup y deja base, documentos, `.env`, licencia y `npm-admin.txt` como estaban:

    ```bash
    cd /opt/gdi
    sudo ./scripts/restaurar.sh AAAA-MM-DD       # con R2: sudo SIN_STORAGE=1 ./scripts/restaurar.sh …
    ```

5. **La función `gdi`** del paso 7 (en `~/.bashrc`) y su **CHECK**, sin el `gdi up -d`: ya lo
   hizo el script.
6. **Paso 8 completo.** El proxy no viaja en el backup: hay que crear su administrador y correr
   `configurar-proxy.sh`, que pide los certificados de nuevo.

**CHECK:** el del paso 8, y en el portal: los documentos firmados antes del backup se abren, y un
documento nuevo se firma con el número siguiente al último del backup.

> `restaurar.sh` sirve también para el ensayo que piden las reglas de arriba: una máquina virtual,
> los pasos 2 y 3, el backup y el script. Unos 2 minutos más el paso 8.

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
| `migrator` en `Exited (1)` con `password authentication failed` después de restaurar | se instaló con los pasos 5 a 7 y después se restauró el `.env` del backup: la base tiene otra contraseña | `sudo ./scripts/restaurar.sh AAAA-MM-DD` (13.1): borra esa base y la crea con la del backup |
| Después de volver atrás, ningún documento de un tipo se firma: `r2_worm_locked_numero_contaminado` | se restauró la base pero no se vació el almacenamiento: un PDF firmado después del backup tiene el número que la base vuelve a ofrecer | `sudo ./scripts/restaurar.sh AAAA-MM-DD` con el mismo backup (12.1) |
| Los documentos quedan en «firmando» y no avanzan, pero la web anda | `backend-worker` está parado, o `unhealthy` y `autoheal` no lo reinició (es el que procesa la cola de firma, el webhook de TAD y los jobs nocturnos; si queda colgado, `autoheal` lo reinicia solo en ~2 min, [7.1](#71-reinicio-automatico-de-servicios-colgados-autoheal)) | `gdi ps backend-worker`; `gdi logs backend-worker \| tail -50`; `gdi up -d backend-worker`. Si se lo frenó con `gdi stop backend-worker`, al arrancarlo de nuevo las firmas vencidas se destraban solas en unos minutos. **No escalarlo a más de 1 réplica** |
| Un servicio está `unhealthy` y no se reinicia solo (autoheal no reinicia) | `autoheal` apagado (`AUTOHEAL_LABEL` cambiada, o parado), o el servicio está parado a mano, o Postgres no responde (en ese caso reiniciar no ayuda) | `gdi ps autoheal autoheal-proxy` (los dos `Up`); `gdi logs --tail=30 autoheal`; `grep AUTOHEAL .env`. Si el log dice `unix socket` o `Could not resolve` → `gdi up -d autoheal-proxy autoheal`. Con la base caída, primero levantar la base |
| Llega el mail «URGENTE: … se reinició 3 veces» (o, cada hora, «SIGUE EN BUCLE: … lleva N reinicios») | el servicio vuelve a colgarse después de cada reinicio: la causa no es un cuelgue pasajero | `gdi logs --tail=200 <servicio>` y `docker inspect --format '{{json .State.Health}}' <contenedor>`; si no se entiende, escribirle a GDI con ese log. No apagar `autoheal` para «callar» el aviso |
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
| `Let's Encrypt no emitio` con `data/meta must NOT have additional properties` | el proxy no es la versión que fija el compose | volver la imagen del proxy a la versión que fija el compose y `gdi up -d` |
| Primer login: el sitio carga, Auth0 pide la clave y vuelve con **502** | faltan los buffers del proxy | volver a correr `configurar-proxy.sh` |
| `Invalid email or password` al correr el script | no son las credenciales del administrador del proxy | usar las de `npm-admin.txt` |
| Después de actualizar o de un `gdi up -d`, **todos** los documentos y logos dan **502** (`storage.<BASE>`) y el log del proxy dice `connect() failed (111: Connection refused)` | el proxy quedó apuntando a la dirección vieja del almacenamiento: pasa en instalaciones configuradas con un `configurar-proxy.sh` anterior a la versión `2026.09.15` | ya mismo: `gdi restart npm`. Para que no vuelva a pasar: volver a correr `configurar-proxy.sh` una vez (no pide certificados nuevos) |

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
| `NoSuchBucket` al subir un documento | los buckets no se crearon, o falta `S3_FORCE_PATH_STYLE=true` | `gdi logs storage-init`; revisar el `.env` |
| `AuthorizationHeaderMalformed` o `IncorrectRegion` en los logs del backend | `S3_REGION` en el `.env` tiene otro valor que `us-east-1` (el almacenamiento local no acepta otra región, ni `auto`) | dejar `S3_REGION=us-east-1` (o borrar la línea) y `gdi up -d` |
| `storage-users` o `storage-init` terminan con error | las claves `STORAGE_ROOT_*` o `CF_R2_*` siguen en `CAMBIAR` o vacías | `gdi logs storage-users storage-init`; `sudo ./scripts/generar-claves.sh` y `gdi up -d`. Cambiar las claves `CF_R2_*` después es seguro: al arrancar, la cuenta nueva pasa a ser dueña de todo y la anterior se borra |
| Importar un PDF o adjuntar un archivo no hace nada o da error, y la consola del navegador (F12) dice **CORS** | el bucket `-tosign` de esa instancia no tiene la regla de subida directa: la instancia se creó con `TOSIGN_UPLOAD_CORS_ORIGINS` vacía y `FRONTEND_URL` mal, o el log dice `SIN CORS` | revisar que `FRONTEND_URL` sea la dirección exacta del front de usuarios (con `https://`, sin barra final) y `gdi up -d`. Las instancias que **ya existían** no se corrigen solas: avisar a GDI |
| `SIN regla de vencimiento de 'uploads/'` en los logs del BackOffice al crear una instancia | el almacenamiento local no implementa el vencimiento automático | **es esperado**, no hace falta hacer nada: GDI borra cada subida al confirmarla y limpia las abandonadas de cada usuario la próxima vez que sube algo |
| La URL de un documento tiene el bucket como subdominio (`https://gdi-oficial.storage.<BASE>/…`) | `S3_FORCE_PATH_STYLE` quedó en `false` en el `.env` | dejarlo en `true` (o borrar la línea) y `gdi up -d` |
| `SignatureDoesNotMatch` / `AccessDenied` al abrir un PDF | `CF_R2_ENDPOINT` apunta a `storage:7070` (el nombre interno) | `CF_R2_ENDPOINT=https://storage.<BASE>` y `gdi up -d` |
| Los documentos no cargan nunca | `STORAGE_DOMAIN` falta o no coincide | `gdi exec backend getent hosts storage.<BASE>` tiene que dar una IP interna; corregir y `gdi up -d` |
| Documento firmado, pero la API da 500 "No se pudo generar URL" o el portal TAD da 404 | al `gateway` le faltan las variables `CF_R2_*` | `gdi exec gateway env \| grep CF_R2` → tienen que salir tres; si no, el instalador está desactualizado |
| Ningún documento se firma y `gdi logs notary` dice `host no permitido` | `STORAGE_DOMAIN` desalineado con `CF_R2_ENDPOINT` | alinearlos y `gdi up -d` |
| Un tipo de documento nuevo tarda en aparecer | caché sin Redis | `gdi ps redis` → `healthy` |
| Después de firmar, "Ver Documento" muestra el documento como pendiente y el visor dice "No se pudo abrir" (versión 2026.09.9) | la pantalla muestra un estado viejo; el documento **sí** quedó firmado | salir y volver a entrar al documento. Corregido en `2026.09.10`: actualizar |

---

¿Trabado en algo que no está acá? Escribile a soporte de GDI Latam con la salida de `gdi ps` y
`gdi logs --tail=200 <servicio>`.

---

## Anexo B. Instalación desatendida (sin preguntas)

Para automatizar la instalación (un `cloud-init`, un script del municipio): con el instalador
desplegado (paso 3) y un `.env` **completo**, `scripts/instalar-desatendido.sh` hace los pasos 7
y, opcionalmente, 8 y 13.1 sin intervención. **No arma el `.env`**: no inventa claves ni pide
datos; lo valida y corta si falta algo.

```bash
cd /opt/gdi
GHCR_TOKEN_FILE=/root/ghcr.token ./scripts/instalar-desatendido.sh --modo onpremise --env /root/gdi.env --proxy
```

| Opción | Qué hace |
|---|---|
| `--modo onpremise` | **obligatoria** |
| `--env <archivo>` | **obligatoria**. Se copia a `/opt/gdi/.env` con permisos 600 |
| `--sin-storage` | municipio con Cloudflare R2 (sin almacenamiento local) |
| `--restaurar-dump <archivo>` | carga un `pg_dump -Fc` en una base **nueva** antes de levantar (ver abajo «Restaurar un dump»). Si ya hay un volumen de postgres, corta salvo `--pisar-base` (lo borra). Errores de `pg_restore` cortan salvo `--restore-tolerante` |
| `--sin-comparar-migraciones` | con `--restaurar-dump`: **salida de emergencia**. No compara las migraciones del dump con las de las imágenes (por ejemplo, un ambiente anterior al runner). Deja un `AVISO` grande en el log y la última línea sale con `migraciones=SIN-COMPARAR` |
| `--restaurar-backup AAAA-MM-DD` | solo `onpremise`: el backup del paso 13 con `restaurar.sh` (el `.env` del backup reemplaza al de `--env`) |
| `--proxy` | configura el proxy (paso 8). Si no tiene administrador lo crea con `NPM_EMAIL` del `.env` y deja las credenciales en `npm-admin.txt` |
| `--espera <s>` | cuánto esperar a que todo quede sano (default 900) |

El token de `ghcr.io` va por entorno (`GHCR_TOKEN` o `GHCR_TOKEN_FILE`), **nunca** como argumento.
Sin ninguno de los dos, usa el login que ya tenga el usuario.

Qué hace, en orden: verifica Docker y Compose → valida el `.env` (sin valores de ejemplo —`CAMBIAR…`,
`sk-or-xxx`—, con `LICENSE_MODE=onpremise` explícito, misma versión que el instalador, `docker compose config`
sin errores, el compose ya fundido verificado con `scripts/verificar-env.py` —un hallazgo es un aviso— y los topes
de memoria contra la RAM del servidor, [7.2](#72-recursos-por-contenedor-cpu-y-memoria)) → login a `ghcr.io`
(y `docker logout` al terminar si el login lo hizo el instalador con `GHCR_TOKEN`) → baja las imágenes (3 intentos)
→ aplica `POSTGRES_PERFIL` si lo pusiste → restaura si se pidió → `up -d` → espera a que los de una sola corrida
terminen en `Exited (0)` y el resto quede `healthy` → proxy si se pidió.

**Resultado.** La última línea es `GDI_INSTALACION=OK modo=<modo> version=<versión>` o
`GDI_INSTALACION=FALLA paso=<paso> codigo=<n>`. Códigos: `0` ok · `2` uso · `3` `.env` · `4`
Docker/Compose · `5` login o imágenes · `6` restauración · `7` no quedó sano · `8` proxy. Correrlo
de nuevo con el mismo `.env` no rompe nada (solo recrea lo que cambió); `--restaurar-dump` no se
repite sin `--pisar-base`.

**Restaurar un dump (`--restaurar-dump`).** La imagen de postgres **siembra** la base de la aplicación
al primer arranque (tablas, extensiones, catálogo). Por eso el instalador **no** restaura encima con
`pg_restore --clean`: tira esa base sembrada, crea una **vacía** (a partir de `template0`) y carga el
dump ahí con `--no-owner --no-acl`. El clúster y su tuning no se tocan. Antes de levantar nada compara
`public.schema_migrations` del dump con las migraciones de las imágenes (las que siembra la imagen de
postgres más las del `migrator`):

| Situación | Qué hace |
|---|---|
| El dump está al día, o le faltan solo las **últimas** | sigue; el `migrator` aplica las pendientes sobre los datos |
| Le falta una migración **de las imágenes** (`/migrations`) anterior a la más nueva que sí tiene | **corta** (código 6) y la nombra: el `migrator` aplica todo archivo cuya versión no esté registrada, o sea que la aplicaría fuera de orden sobre datos reales |
| Le falta una versión que solo figura en la base **semilla** de la imagen de postgres (baseline o archivo) | **avisa y sigue**: el `migrator` no la mira (no es un archivo de `/migrations`); es normal en un ambiente que nació antes del runner |
| Trae migraciones que las imágenes no conocen (el dump es más nuevo que el software) | **corta** y las nombra: usá imágenes de esa versión o posterior |
| No trae `public.schema_migrations` | **corta**: no parece una base de GDI |

La base nueva sale de `template0`, que ya trae el esquema `public`: si el dump lo incluye en su tabla de
contenidos (`SCHEMA - public`), el instalador lo saca de la lista con `pg_restore -l` y `-L`, y lo demás
entra igual. Con `--restaurar-dump`, `DB_NAME` no puede ser `postgres`, `template0` ni `template1` (se la
tiraría) y tiene que ser solo letras, números y `_`.

Si falla a mitad (`pg_restore` con errores, corte de luz, disco lleno) queda un volumen **a medias** y
no se levanta ninguna aplicación. Para reintentar, corré el **mismo comando con `--pisar-base`**: baja
todo, borra el volumen y arranca de cero; el archivo del dump no se toca. El detalle de los errores
queda en `restaurar-dump-<fecha>.log` en la carpeta del instalador.

> El proxy en modo `onpremise` pide certificados a Let's Encrypt: los DNS tienen que resolver
> **antes** de correr con `--proxy` (sección 1.4), y vale el cupo de 5 por semana.
