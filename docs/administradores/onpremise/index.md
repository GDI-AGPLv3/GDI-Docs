# GDI en el servidor del municipio — Guía ejecutiva

Una página para quien decide y coordina. El paso a paso técnico está en
[el manual de instalación](manual.md), escrito para que lo ejecute un asistente de IA junto al técnico.

---

## Qué es

GDI (Gestión Documental Inteligente) instalado **en un servidor del municipio**: los
expedientes, los documentos firmados y los datos de los vecinos no salen de su
infraestructura. Es el mismo sistema que GDI Latam ofrece en la nube.

## Qué tiene que tener el municipio antes de empezar

| | Qué | Quién lo consigue |
|---|---|---|
| 1 | **Un servidor Linux** con 4 procesadores, 8 GB de memoria y 80 GB de disco, IP pública fija y los puertos 80 y 443 abiertos | Sistemas del municipio |
| 2 | **Un dominio** (por ejemplo `municipio.gob.ar`) donde se puedan crear 7 subdominios que apunten al servidor | Sistemas del municipio |
| 3 | **Una cuenta de Auth0** (el servicio de login). Es **obligatoria** y **gratuita** hasta 25.000 usuarios. Es del municipio | Sistemas del municipio |
| 4 | **Salida a internet** del servidor, permanente: la licencia se renueva sola cada semana | Redes del municipio |
| 5 | **El mail de quien va a administrar** | El municipio |
| 6 | **Token de descarga, código de activación y número de versión** | Los entrega **GDI Latam** al contratar |

**Recomendado, no obligatorio:**
- el **servidor de correo** del municipio (sin él, los accesos de cada empleado se entregan a mano);
- el **certificado de firma digital** del municipio (sin él, se firma con uno de prueba **sin validez legal**);
- una **clave de OpenRouter** si se van a usar las funciones de IA.

## Cómo es la instalación

1. **Preparar** el servidor y los 7 subdominios (Sistemas).
2. **Configurar Auth0** en su panel web, siguiendo el manual (unos 30 minutos).
3. **Instalar GDI**: el asistente de IA baja el sistema y lo configura. No se compila nada: todo
   llega armado y en una sola versión.
4. **Activar la licencia**: automático, con el código que entregó GDI Latam.
5. **Publicar con HTTPS**: los certificados se piden solos.
6. **Crear el municipio** desde el Panel: primero una instancia de **capacitación** para
   practicar, y después la de **producción**, que hereda toda la configuración.

Con todo lo del cuadro listo de antemano, la instalación entra en **una jornada**. Lo que más
demora suele ser lo que depende de terceros: los subdominios y la apertura de puertos.

## Decisiones que no tienen vuelta atrás

- **La sigla de producción** del municipio queda impresa en el número de cada documento firmado.
  No se puede cambiar después: elegirla con cuidado.
- **La clave maestra de certificados** que genera la instalación cifra las firmas del municipio.
  Si se pierde, los certificados cargados dejan de servir: va en el backup.

## Después de instalar

- **Actualizaciones:** GDI Latam avisa por mail cuando hay versión nueva. **Nada se actualiza
  solo**: el municipio elige el día y la hora, siempre con un backup hecho antes.
- **Backups:** son responsabilidad del municipio. El manual indica qué copiar (la base, los
  documentos, la configuración y la licencia) y recomienda una copia diaria **fuera** del servidor.
- **Licencia:** se renueva sola mientras el contrato esté vigente. Si se amplía el contrato (más
  municipios, módulos nuevos), la instalación lo recibe sin tocar el servidor.
- **Asistentes de IA:** los empleados pueden conectar su asistente (Claude, ChatGPT u otro) para
  operar GDI con sus mismos permisos. Cada uno lo autoriza con su propio usuario.

## Qué hace cada parte

| GDI Latam | El municipio |
|---|---|
| Entrega el software, la licencia y las actualizaciones | Pone el servidor, el dominio y la cuenta de Auth0 |
| Mantiene el registro central de siglas | Instala, opera y hace los backups |
| Da soporte ante problemas | Decide cuándo actualizar |
