# LOGs del Sistema

Panel de actividad del municipio: cuanto se está usando GDI, quien entró último y que se firmó en los últimos días.

---

## Descripción General

La sección **LOGs del Sistema** es la vista de pulso del municipio. No es un registro técnico de errores ni una auditoría legal: es un tablero de **actividad real**, pensado para responder de un vistazo preguntas como *"¿cuanta gente está usando el sistema?"*, *"¿que se firmó esta semana?"* o *"¿el área de Obras entró alguna vez?"*.

Toda la información es de **solo lectura**: desde acá no se modifica nada.

!!! info "Para la auditoría formal"
    Los cambios de configuración (altas de usuario, permisos, tipos de documento) quedan registrados aparte, en la auditoría del sistema. Esta pantalla muestra **uso**, no cambios de configuración.

---

## Rango de fechas

Arriba a la derecha se elige el periodo con **Desde** y **Hasta**. Al entrar viene cargado el rango de los **últimos 14 días**.

Después de cambiar las fechas hay que apretar **Actualizar**: los datos no se recargan solos al tocar el calendario.

---

## Modo VIVO

El botón **VIVO** deja la pantalla refrescándose sola cada 8 segundos, sin tener que apretar Actualizar.

Sirve para acompañar en vivo una jornada de trabajo, una capacitación o una prueba de carga: se ve entrar cada documento firmado a medida que ocurre. Se apaga con el mismo botón.

!!! tip "Cuando conviene apagarlo"
    En modo VIVO la pantalla consulta al servidor todo el tiempo. Para dejar la pestaña abierta muchas horas, conviene apagarlo.

---

## Las seis métricas

| Métrica | Que cuenta |
|---------|-----------|
| **Exp. Activos** | Expedientes abiertos hoy. Abajo, el total histórico |
| **Docs Firmados** | Documentos firmados en total. Abajo, cuantos en los últimos 14 días |
| **Usuarios Reg.** | Usuarios dados de alta en el municipio |
| **Activos 30d** | Cuantos de esos usuarios entraron al menos una vez en los últimos 30 días |
| **Departamentos** | Reparticiones activas del organigrama |
| **Sectores** | Sectores activos |

!!! note "La métrica que más dice"
    **Activos 30d** sobre **Usuarios Reg.** es el mejor indicador de adopción: si hay 200 usuarios cargados y solo 15 entraron en el último mes, el problema no es el sistema sino el despliegue en las áreas.

---

## Las tres tablas

Debajo de las métricas hay tres listados, cada uno con su botón **Exportar CSV** (abre en Excel o LibreOffice).

### Últimos documentos firmados

Número oficial, tipo de documento, referencia, repartición y sector (`DPTO#SECTOR`), quien lo numeró y cuando.

Es la forma más rápida de confirmar que la firma está funcionando en producción y de ver que áreas están emitiendo documentos oficiales.

Al lado de quien lo numeró pueden aparecer dos marcas:

| Marca | Que significa |
|-------|---------------|
| **ciudadano** | Lo numeró un ciudadano desde TAD (Trámites a Distancia), no un empleado del municipio |
| **(conformidad)** | Es un documento **certificado de origen**: un PDF importado que ya venia certificado. Firmarlo de nuevo rompería esa certificación. Por eso quien lo numeró dio conformidad en GDI y no firmo digitalmente el PDF. Al pasar el mouse sobre la marca se ve esa explicación |

El CSV lleva las mismas marcas al lado del nombre: `(ciudadano)` y `(conformidad)`.

### Últimos expedientes

Número, carátula, estado, tipo de expediente, sector y quien lo creó.

### Últimos accesos

Nombre, mail, sector y **último acceso** de cada usuario.

Es la tabla que se usa para detectar usuarios que nunca entraron: si alguien figura sin fecha de último acceso, probablemente nunca completó su primer login y hay que reinvitarlo desde [Usuarios](usuarios.md).

---

## Preguntas frecuentes

**¿Por qué un usuario aparece sin último acceso?**
Porque todavía no entró ni una vez. Se le puede reenviar la invitación desde la ficha del usuario.

**¿Por qué las tablas están vacías?**
Casi siempre es el rango de fechas: si el periodo elegido no tiene actividad, no hay nada que mostrar. Ampliar el rango y apretar Actualizar.

**¿El CSV respeta el filtro de fechas?**
Sí. Exporta exactamente lo que se está viendo en pantalla.
