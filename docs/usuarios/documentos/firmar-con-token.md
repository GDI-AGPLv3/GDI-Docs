# Firmar con Token — FirmadorGDI

Para firmar documentos con tu token físico (Feitian ePass2003) necesitas tener instalado **FirmadorGDI**, el cliente de firma digital de GDI.

!!! info "Primera vez"
    Si nunca instalaste FirmadorGDI en tu computadora, seguí primero los pasos de instalación más abajo.

---

## Instalacion de FirmadorGDI

### Requisitos previos

- Windows 10 o superior (64 bits)
- Token Feitian ePass2003 con certificado AC ONTI Argentina
- **Controlador (driver) del token instalado** — es un programa aparte de FirmadorGDI y hay que instalarlo primero (paso 1)
- Google Chrome o Microsoft Edge

### Pasos

**1. Instalar el controlador del token**

FirmadorGDI no habla con el token directamente: usa el controlador **PKCS#11** que publica el fabricante del dispositivo. Si ese controlador falta, la firma corta con el error *"token no encontrado: no se encontró driver PKCS#11 compatible"*, aunque Windows muestre el token conectado y con luz.

Para el token Feitian ePass2003 el controlador se llama **EnterSafe Middleware (ePass2003)**. Lo entrega la Autoridad Certificante o el distribuidor que te dio el token; varios organismos públicos también lo publican (por ejemplo, la [DTI del Servicio Penitenciario Bonaerense](https://dti.spb.gba.gob.ar/token.html)).

!!! warning "Desconectá el token antes de instalar el controlador"
    El instalador falla o queda a medias si el token está enchufado. Desconectalo, instalá el controlador, reiniciá si te lo pide, y **recién ahí** volvé a conectarlo.

A diferencia de FirmadorGDI, este instalador **sí pide permisos de administrador** (va a aparecer el cartel de Control de cuentas de usuario). Antes de ejecutarlo, verificá que esté firmado por *Feitian Technologies Co., Ltd.*: clic derecho sobre el archivo → **Propiedades** → pestaña **Firmas digitales**.

Cuando termine, tiene que existir el archivo `C:\Windows\System32\eps2003csp11.dll`. Esa es exactamente la ruta que busca FirmadorGDI.

**2. Descargar el instalador de FirmadorGDI**

[Descargar FirmadorGDI](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.msi){ .md-button .md-button--primary }

El archivo pesa menos de 1 MB.

**3. Ejecutar el instalador**

Abrir el archivo descargado. Windows puede mostrar esta advertencia:

!!! warning "Advertencia de Windows SmartScreen"
    Si aparece el mensaje *"Windows protegió tu PC"*, hacer clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.

    Esto ocurre porque el instalador no tiene firma de código comercial. Es normal para software de gobiernos municipales.

Seguir los pasos del instalador (Next → Next → Install → Finish). No se requieren permisos de administrador.

**4. Verificar la instalación**

Al terminar la instalación, hacer doble clic en el acceso directo de FirmadorGDI. Debe aparecer este mensaje:

> *FirmadorGDI está instalado y listo.*
> *Para firmar documentos, ingresá a tu sistema desde el navegador y hacé clic en "Firmar".*

Si aparece ese mensaje, la instalación fue exitosa. No es necesario abrir FirmadorGDI manualmente para firmar.

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

Ingresar el **PIN del token** y hacer clic en **"Firmar"**.

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
    Verificar que FirmadorGDI esté instalado: hacer doble clic en el acceso directo del menú Inicio. Si no está instalado, [descargarlo aquí](https://firmadorgdi.gdilatam.com/FirmadorGDI-latest.msi).

    Si está instalado y aun así no se abre, intentar con Chrome (recomendado) en lugar de otro navegador.

??? question "El token no es detectado"
    - Desconectar y volver a conectar el token USB
    - Probar en otro puerto USB
    - Verificar que el controlador del token esté instalado (paso 1 de la instalación). No se instala solo al enchufar el token: la mayoría de los ePass2003 no traen ninguna partición con el instalador.
    - Si el problema persiste, contactar al administrador del sistema

??? question "Aparece el error: 'token no encontrado: no se encontró driver PKCS#11 compatible'"
    Falta el controlador del token, o está instalado el de otra marca. No es un problema de FirmadorGDI ni del token en sí: el dispositivo puede estar perfectamente conectado y aun así dar este error.

    Instalá el controlador siguiendo el paso 1 de la instalación y volvé a intentar.

    FirmadorGDI reconoce estos controladores:

    | Token | Archivo que debe existir |
    |-------|--------------------------|
    | Feitian ePass2003 | `C:\Windows\System32\eps2003csp11.dll` |
    | SafeNet eToken | `C:\Windows\System32\eTPKCS11.dll` |
    | OpenSC (genérico) | `C:\Windows\System32\opensc-pkcs11.dll` |

    Si ninguno de esos archivos existe, el controlador no quedó instalado. Ojo con la versión: FirmadorGDI es de 64 bits, así que necesita el controlador de 64 bits.

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
