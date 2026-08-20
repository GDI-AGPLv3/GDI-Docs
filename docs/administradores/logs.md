# LOGs del Sistema

Panel de actividad del municipio: cuanto se esta usando GDI, quien entro ultimo y que se firmo en los ultimos dias.

---

## Descripcion General

La seccion **LOGs del Sistema** es la vista de pulso del municipio. No es un registro tecnico de errores ni una auditoria legal: es un tablero de **actividad real**, pensado para responder de un vistazo preguntas como *"¿cuanta gente esta usando el sistema?"*, *"¿que se firmo esta semana?"* o *"¿el area de Obras entro alguna vez?"*.

Toda la informacion es de **solo lectura**: desde aca no se modifica nada.

!!! info "Para la auditoria formal"
    Los cambios de configuracion (altas de usuario, permisos, tipos de documento) quedan registrados aparte, en la auditoria del sistema. Esta pantalla muestra **uso**, no cambios de configuracion.

---

## Rango de fechas

Arriba a la derecha se elige el periodo con **Desde** y **Hasta**. Al entrar viene cargado el rango de los **ultimos 14 dias**.

Despues de cambiar las fechas hay que apretar **Actualizar**: los datos no se recargan solos al tocar el calendario.

---

## Modo VIVO

El boton **VIVO** deja la pantalla refrescandose sola cada 8 segundos, sin tener que apretar Actualizar.

Sirve para acompanar en vivo una jornada de trabajo, una capacitacion o una prueba de carga: se ve entrar cada documento firmado a medida que ocurre. Se apaga con el mismo boton.

!!! tip "Cuando conviene apagarlo"
    En modo VIVO la pantalla consulta al servidor todo el tiempo. Para dejar la pestana abierta muchas horas, conviene apagarlo.

---

## Las seis metricas

| Metrica | Que cuenta |
|---------|-----------|
| **Exp. Activos** | Expedientes abiertos hoy. Abajo, el total historico |
| **Docs Firmados** | Documentos firmados en total. Abajo, cuantos en los ultimos 14 dias |
| **Usuarios Reg.** | Usuarios dados de alta en el municipio |
| **Activos 30d** | Cuantos de esos usuarios entraron al menos una vez en los ultimos 30 dias |
| **Departamentos** | Reparticiones activas del organigrama |
| **Sectores** | Sectores activos |

!!! note "La metrica que mas dice"
    **Activos 30d** sobre **Usuarios Reg.** es el mejor indicador de adopcion: si hay 200 usuarios cargados y solo 15 entraron en el ultimo mes, el problema no es el sistema sino el despliegue en las areas.

---

## Las tres tablas

Debajo de las metricas hay tres listados, cada uno con su boton **Exportar CSV** (abre en Excel o LibreOffice).

### Ultimos documentos firmados

Numero oficial, tipo de documento, referencia, reparticion y sector (`DPTO#SECTOR`), quien lo numero y cuando.

Es la forma mas rapida de confirmar que la firma esta funcionando en produccion y de ver que areas estan emitiendo documentos oficiales.

### Ultimos expedientes

Numero, caratula, estado, tipo de expediente, sector y quien lo creo.

### Ultimos accesos

Nombre, mail, sector y **ultimo acceso** de cada usuario.

Es la tabla que se usa para detectar usuarios que nunca entraron: si alguien figura sin fecha de ultimo acceso, probablemente nunca completo su primer login y hay que reinvitarlo desde [Usuarios](usuarios.md).

---

## Preguntas frecuentes

**¿Por que un usuario aparece sin ultimo acceso?**
Porque todavia no entro ni una vez. Se le puede reenviar la invitacion desde la ficha del usuario.

**¿Por que las tablas estan vacias?**
Casi siempre es el rango de fechas: si el periodo elegido no tiene actividad, no hay nada que mostrar. Ampliar el rango y apretar Actualizar.

**¿El CSV respeta el filtro de fechas?**
Si. Exporta exactamente lo que se esta viendo en pantalla.
