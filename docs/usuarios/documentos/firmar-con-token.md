# Firmar con Token — FirmadorGDI

Para firmar documentos con tu token físico (Feitian ePass2003) necesitas tener instalado **FirmadorGDI**, el cliente de firma digital de GDI. Hay instalador para **Windows** y para **Mac**: es el mismo programa, pero cada sistema tiene su propio archivo de descarga.

!!! info "Primera vez"
    Si nunca instalaste FirmadorGDI en tu computadora, seguí primero los pasos de instalación más abajo.

---

## Instalacion de FirmadorGDI

### Requisitos previos

=== "Windows"

    - Windows 10 o superior (64 bits)
    - Token Feitian ePass2003 con certificado AC ONTI Argentina
    - **Controlador (driver) del token instalado** — es un programa aparte de FirmadorGDI y hay que instalarlo primero (paso 1)
    - Google Chrome o Microsoft Edge

=== "Mac"

    - macOS 12 (Monterey) o superior, con procesador Apple o Intel
    - Token Feitian ePass2003 con certificado AC ONTI Argentina
    - **Controlador (driver) del token para macOS instalado** — es un programa aparte de FirmadorGDI y hay que instalarlo primero (paso 1)
    - Google Chrome o Microsoft Edge
    - La contraseña de un usuario administrador de la Mac (la pide el instalador)

### Pasos

**1. Instalar el controlador del token**

FirmadorGDI no habla con el token directamente: usa el controlador **PKCS#11** que publica el fabricante del dispositivo. Si ese controlador falta, la firma corta con el error *"token no encontrado: no se encontró driver PKCS#11 compatible"*, aunque la computadora muestre el token conectado y con luz.

Para el token Feitian ePass2003 el controlador se llama **EnterSafe Middleware (ePass2003)**. Lo entrega la Autoridad Certificante o el distribuidor que te dio el token; varios organismos públicos también lo publican (por ejemplo, la [DTI del Servicio Penitenciario Bonaerense](https://dti.spb.gba.gob.ar/token.html)).

!!! warning "Desconectá el token antes de instalar el controlador"
    El instalador falla o queda a medias si el token está enchufado. Desconectalo, instalá el controlador, reiniciá si te lo pide, y **recién ahí** volvé a conectarlo.

=== "Windows"

    A diferencia de FirmadorGDI, este instalador **sí pide permisos de administrador** (va a aparecer el cartel de Control de cuentas de usuario). Antes de ejecutarlo, verificá que esté firmado por *Feitian Technologies Co., Ltd.*: clic derecho sobre el archivo → **Propiedades** → pestaña **Firmas digitales**.

    Cuando termine, tiene que existir el archivo `C:\Windows\System32\eps2003csp11.dll`. Esa es exactamente la ruta que busca FirmadorGDI.

=== "Mac"

    Pedí la versión **para macOS** del controlador: el de Windows no sirve.

    Cuando termine, tiene que existir uno de estos dos archivos (depende de la versión del controlador). Son exactamente las rutas que busca FirmadorGDI:

    - `/usr/local/lib/libcastle_v2.1.0.0.dylib`
    - `/usr/local/lib/libcastle.1.0.0.dylib`

    Para comprobarlo: en el Finder, menú **Ir → Ir a la carpeta…**, escribir `/usr/local/lib` y buscar el archivo.

**2. Descargar el instalador de FirmadorGDI**

=== "Windows"

    [Descargar FirmadorGDI para Windows](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.msi){ .md-button .md-button--primary }

    El archivo pesa menos de 1 MB.

=== "Mac"

    [Descargar FirmadorGDI para Mac](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.pkg){ .md-button .md-button--primary }

    Es un solo instalador para todas las Mac, con procesador Apple o Intel.

**3. Ejecutar el instalador**

=== "Windows"

    Abrir el archivo descargado. Windows puede mostrar esta advertencia:

    !!! warning "Advertencia de Windows SmartScreen"
        Si aparece el mensaje *"Windows protegió tu PC"*, hacer clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.

        Esto ocurre porque el instalador no tiene firma de código comercial. Es normal para software de gobiernos municipales.

    Seguir los pasos del instalador (Next → Next → Install → Finish). No se requieren permisos de administrador.

=== "Mac"

    Abrir el archivo `.pkg` descargado. macOS puede negarse a abrirlo:

    !!! warning "macOS dice que no puede verificar al desarrollador"
        Si aparece un mensaje como *"Apple no pudo verificar que FirmadorGDI no contenga software malicioso"*, cerrá el cartel y andá a **Ajustes del Sistema → Privacidad y seguridad**. Más abajo en esa pantalla aparece FirmadorGDI con el botón **"Abrir igualmente"**: hacé clic ahí y confirmá.

        Esto ocurre porque el instalador no tiene la firma de desarrollador de Apple. Es el equivalente de la advertencia de SmartScreen de Windows.

    Seguir los pasos del instalador (Continuar → Continuar → Instalar). **Pide la contraseña de un administrador de la Mac.**

    FirmadorGDI queda en la carpeta **Aplicaciones**. No aparece en el Dock: no hace falta abrirlo a mano para firmar.

**4. Verificar la instalación**

=== "Windows"

    Al terminar la instalación, hacer doble clic en el acceso directo de FirmadorGDI.

=== "Mac"

    Al terminar la instalación, abrir **FirmadorGDI** desde la carpeta **Aplicaciones**. Tarda un par de segundos.

Debe aparecer este mensaje:

> *FirmadorGDI está instalado y listo.*
> *Para firmar documentos, ingresá a tu sistema desde el navegador y hacé clic en "Firmar".*

Si aparece ese mensaje, la instalación fue exitosa. No es necesario abrir FirmadorGDI manualmente para firmar.

### Si tu organismo tiene GDI en su propio servidor

Esto es **solo** para organismos que instalaron GDI en servidores propios (on-premise). Si usás GDI Latam en la nube, no hay que hacer nada: salteá esta parte.

FirmadorGDI solo le obedece a los servidores que tiene autorizados. El servidor de tu organismo lo tiene que autorizar el área de sistemas en cada computadora, y hacen falta permisos de administrador:

=== "Windows"

    El instalador lo pregunta: en la pantalla **"¿Dónde está tu GDI?"** elegir *"Mi organismo tiene GDI en su propio servidor"* y escribir la dirección (solo el nombre, por ejemplo `api.mi-municipio.gob.ar`).

    Para una instalación desatendida:

    ```
    msiexec /i FirmadorGDI-latest.msi SERVIDORGDI="api.mi-municipio.gob.ar"
    ```

=== "Mac"

    El instalador no lo pregunta. Después de instalar, un administrador abre la **Terminal** y ejecuta estas dos líneas, cambiando el nombre del servidor por el suyo:

    ```bash
    sudo mkdir -p "/Library/Application Support/GDILatam/FirmadorGDI"
    echo "api.mi-municipio.gob.ar" | sudo tee "/Library/Application Support/GDILatam/FirmadorGDI/HostsAutorizados"
    ```

    Solo el nombre del servidor: sin `https://`, sin barras, sin puerto y sin comodines. Si son varios, uno por línea. No se pierde al actualizar FirmadorGDI.

---

## Como firmar un documento con token

Una vez instalado FirmadorGDI, el proceso de firma desde GDI es el siguiente:

**1. Conectar el token**

Antes de hacer clic en "Firmar", conectá el token Feitian al puerto USB. Si lo conectás después, FirmadorGDI no lo detecta y la firma se cancela automáticamente.

**2. Iniciar el proceso de firma**

Desde la [previsualización del documento](previsualizar-documento.md), hacer clic en **"Comenzar proceso de firma"** y luego en el botón **"Firmar"** cuando sea tu turno.

**3. Autorizar la apertura de FirmadorGDI**

Chrome muestra un cuadro de diálogo preguntando si permitís abrir FirmadorGDI. Hacer clic en **"Abrir FirmadorGDI"** (o "Permitir").

**4. Ingresar el PIN**

FirmadorGDI muestra una ventana con los datos de tu token:

- Nombre del titular
- CUIL
- Fecha de vencimiento del certificado
- El servidor al que van las firmas

Ingresar el **PIN del token** y hacer clic en **"Firmar"**.

!!! warning "Mirá el servidor antes de poner el PIN"
    Tiene que ser el de tu sistema GDI. Si no lo reconocés, no pongas el PIN: cancelá y avisá al área de sistemas.

!!! warning "PIN incorrecto"
    Tenés 3 intentos para ingresar el PIN. Si los tres fallan, el token se bloquea y necesitás desbloquearlo con el PUK ante la AC ONTI.

**5. Esperar confirmación**

FirmadorGDI firma el documento localmente y envía el resultado al sistema. El navegador muestra el resultado:

| Resultado | Qué significa |
|-----------|---------------|
| ✅ Firma realizada con éxito | El documento quedó firmado correctamente |
| Número oficial (ej: `INF-2026-00000042-TXST-AREA`) | Solo aparece si sos el numerador (último firmante) |

---

## Problemas frecuentes

??? question "FirmadorGDI no se abre al hacer clic en Firmar"
    Verificar que FirmadorGDI esté instalado: en Windows, hacer doble clic en el acceso directo del menú Inicio; en Mac, abrirlo desde la carpeta Aplicaciones. Si no está instalado, descargarlo: [Windows](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.msi) · [Mac](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.pkg).

    Si está instalado y aun así no se abre, intentar con Chrome (recomendado) en lugar de otro navegador.

    En Mac, si recién lo instalaste y el navegador dice que no hay ninguna aplicación para abrir el enlace, cerrá la sesión de la Mac y volvé a entrar.

??? question "El token no es detectado"
    - Desconectar y volver a conectar el token USB
    - Probar en otro puerto USB
    - Verificar que el controlador del token esté instalado (paso 1 de la instalación). No se instala solo al enchufar el token: la mayoría de los ePass2003 no traen ninguna partición con el instalador.
    - Si el problema persiste, contactar al administrador del sistema

??? question "Aparece el error: 'token no encontrado: no se encontró driver PKCS#11 compatible'"
    En la computadora no hay instalado ningún controlador de token. No es un problema de FirmadorGDI ni del token en sí: el dispositivo puede estar perfectamente conectado y aun así dar este error.

    Instalá el controlador siguiendo el paso 1 de la instalación y volvé a intentar.

    FirmadorGDI reconoce estos controladores:

    | Token | Archivo que debe existir en Windows | Archivo que debe existir en Mac |
    |-------|-------------------------------------|---------------------------------|
    | Feitian ePass2003 | `C:\Windows\System32\eps2003csp11.dll` | `/usr/local/lib/libcastle_v2.1.0.0.dylib` o `/usr/local/lib/libcastle.1.0.0.dylib` |
    | SafeNet eToken | `C:\Windows\System32\eTPKCS11.dll` | `/usr/local/lib/libeTPkcs11.dylib` |
    | OpenSC (genérico) | `C:\Windows\System32\opensc-pkcs11.dll` | `/Library/OpenSC/lib/opensc-pkcs11.so` |

    Si ninguno de esos archivos existe, el controlador no quedó instalado. Ojo con la versión: en Windows, FirmadorGDI es de 64 bits, así que necesita el controlador de 64 bits.

??? question "Aparece el error: 'token no encontrado: no hay tokens conectados'"
    Hay controladores instalados, pero ninguno detecta un token. El mensaje nombra los controladores que se probaron.

    - Si el token no está enchufado, conectalo y volvé a intentar.
    - Si está enchufado, el controlador instalado es **el de otra marca**: falta el de tu token. Instalalo siguiendo el paso 1 de la instalación.

    Se pueden tener instalados los controladores de varias marcas a la vez (por ejemplo, Feitian y SafeNet): desde la versión 1.8.0, FirmadorGDI usa el que corresponde al token que está enchufado. Con una versión anterior, en ese caso daba este mismo error aunque el token estuviera conectado: actualizá FirmadorGDI.

??? question "En una Mac con procesador Apple el controlador está instalado y el token igual no se detecta"
    Puede ser un controlador viejo, hecho solo para Mac con Intel: una aplicación para procesador Apple no puede cargarlo.

    Lo mejor es instalar una versión más nueva del controlador. Si no existe, se puede abrir FirmadorGDI en modo Intel: en el Finder, carpeta **Aplicaciones**, seleccionar FirmadorGDI → menú **Archivo → Obtener información** → tildar **"Abrir con Rosetta"**.

??? question "Soporte me pide el registro (log) de FirmadorGDI"
    - **Windows:** escribir `%TEMP%\firmadorgdi.log` en la barra de direcciones del Explorador de archivos.
    - **Mac:** en el Finder, menú **Ir → Ir a la carpeta…** y escribir `~/Library/Logs/FirmadorGDI`. El archivo es `firmadorgdi.log`.

    La primera línea de cada firma dice qué versión de FirmadorGDI está instalada.

??? question "El PIN es correcto pero dice que es incorrecto"
    El certificado del token puede haber vencido. Verificar la fecha de vencimiento que muestra FirmadorGDI en el diálogo. Si venció, solicitar renovación ante la AC ONTI Argentina.

??? question "Aparece el error: 'token bloqueado'"
    El token se bloqueó por demasiados intentos de PIN incorrectos. Contactar a la AC ONTI Argentina para desbloquearlo con el PUK.

??? question "La firma se cancela sola sin mostrar nada"
    La sesión de firma expira en 4 minutos. Si tardaste más de ese tiempo en completar los pasos, volvé a iniciar el proceso desde el sistema GDI.

---

## Ver también

- [Proceso de Firma](proceso-de-firma.md) — cómo funciona el circuito completo de firmas
- [Previsualizar Documento](previsualizar-documento.md) — cómo iniciar el proceso
