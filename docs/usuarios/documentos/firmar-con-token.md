# Firmar con Token — FirmadorGDI

Para firmar documentos con tu token físico (Feitian ePass2003) necesitas tener instalado **FirmadorGDI**, el cliente de firma digital de GDI.

!!! info "Primera vez"
    Si nunca instalaste FirmadorGDI en tu computadora, seguí primero los pasos de instalación más abajo.

---

## Instalacion de FirmadorGDI

### Requisitos previos

- Windows 10 o superior (64 bits)
- Token Feitian ePass2003 con certificado AC ONTI Argentina
- Google Chrome o Microsoft Edge

### Pasos

**1. Descargar el instalador**

[Descargar FirmadorGDI-1.0.0.msi](https://your-r2-public.r2.dev/FirmadorGDI-1.0.0.msi){ .md-button .md-button--primary }

El archivo pesa menos de 1 MB.

**2. Ejecutar el instalador**

Abrir el archivo descargado. Windows puede mostrar esta advertencia:

!!! warning "Advertencia de Windows SmartScreen"
    Si aparece el mensaje *"Windows protegió tu PC"*, hacer clic en **"Más información"** y luego en **"Ejecutar de todas formas"**.

    Esto ocurre porque el instalador no tiene firma de código comercial. Es normal para software de gobiernos municipales.

Seguir los pasos del instalador (Next → Next → Install → Finish). No se requieren permisos de administrador.

**3. Verificar la instalación**

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
    Verificar que FirmadorGDI esté instalado: hacer doble clic en el acceso directo del menú Inicio. Si no está instalado, [descargarlo aquí](https://your-r2-public.r2.dev/FirmadorGDI-1.0.0.msi).

    Si está instalado y aun así no se abre, intentar con Chrome (recomendado) en lugar de otro navegador.

??? question "El token no es detectado"
    - Desconectar y volver a conectar el token USB
    - Probar en otro puerto USB
    - Verificar que el driver del token esté instalado (viene incluido con el token Feitian)
    - Si el problema persiste, contactar al administrador del sistema

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
