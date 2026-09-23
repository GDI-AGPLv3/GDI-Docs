# Orden de firma por niveles

Cuando un documento tiene varios firmantes, por defecto **a todos les llega a la vez** y firman en paralelo, salvo al numerador, que espera al final. Esa sigue siendo la manera normal de trabajar y no requiere ningun ajuste.

Cuando hace falta que la firma respete una secuencia (por ejemplo: primero un jefe de area, despues varios responsables tecnicos, y al final los que aprueban), se puede **activar un orden de firma por niveles**. Los firmantes se agrupan en niveles numerados: los del mismo nivel firman en paralelo, y un nivel no se habilita hasta que firmaron todos los del nivel anterior. El numerador siempre firma al final, fuera del orden configurable.

---

## Como se activa

En el editor de firmantes de un documento en borrador, arriba de la lista aparece el toggle **"Establecer orden de firma"**. Apagado (default): todos los comunes firman en paralelo. Prendido: cada firmante muestra un selector de nivel y la lista se agrupa por nivel.

Al reabrir un borrador que ya tenia niveles distintos configurados, el toggle aparece prendido automaticamente. Si todos los firmantes estan en el mismo nivel, aparece apagado.

---

## Como se arma un orden

Con el toggle prendido, a cada firmante comun se le asigna un numero de nivel (1, 2, 3, ...):

- **Mismo nivel = firman en paralelo.** Se habilitan todos juntos cuando termina el nivel anterior; el orden entre ellos no importa.
- **Niveles distintos = firman en secuencia.** El nivel 2 no se habilita hasta que firmaron todos los del nivel 1.
- **El numerador siempre queda al final**, con la etiqueta **"Ultimo"**, sin selector.

Al apagar el toggle, todos los comunes vuelven a nivel 1 (piden confirmacion si ya habia niveles armados).

---

## Que pasa cuando alguien firma antes de su turno

**No puede firmar.** En el visor del documento el boton **Firmar** aparece deshabilitado para el firmante que todavia no llego a su turno, con el mensaje *"Todavia no es tu turno: faltan firmar los del nivel N"*.

Para quien firma por API, Gateway REST o via un agente MCP, el backend responde **409** con el mismo mensaje, indicando el nivel que falta completar. No es un "reintentar en unos segundos": la espera puede ser de horas o dias.

---

## Rechazo

Si cualquier firmante rechaza el documento en cualquier nivel, se **corta el proceso completo**: el documento pasa a `rejected` y el resto de los firmantes pendientes tambien queda en `rejected`. El comportamiento es el mismo que hoy con firma en paralelo.

---

## Compatibilidad con documentos ya en circulacion

Los documentos que estaban en proceso de firma antes de esta funcionalidad, y los borradores viejos, siguen firmando en paralelo: **todos los comunes quedan en nivel 1** y el numerador sigue firmando al final. No hay que hacer nada: la migracion los deja en ese estado.

Al reabrir un borrador viejo, el toggle aparece apagado (porque todos estan en el mismo nivel).

---

## Ejemplo

Un decreto tiene siete firmantes: Jorge, Juan, Maria, Roberto, Josefina, Maria B. y Ana (numeradora). Se necesita que Jorge firme primero, despues los tres responsables tecnicos (en cualquier orden), despues las dos coordinadoras (en cualquier orden), y al final la numeradora.

Se activa **"Establecer orden de firma"** y se configura:

```
Nivel 1   Jorge Perez
Nivel 2   Juan Gomez · Maria Lopez · Roberto Diaz    (firman en paralelo)
Nivel 3   Josefina Ruiz · Maria Benitez              (firman en paralelo)
Ultimo    Ana Torres (numeradora)
```

Secuencia:

1. Al salir a firma, **solo Jorge** tiene el boton Firmar habilitado. Los demas ven el documento pero el boton esta deshabilitado.
2. Cuando Jorge firma, se habilitan **Juan, Maria y Roberto al mismo tiempo**. El orden entre ellos no importa.
3. Cuando firmaron los tres, se habilitan **Josefina y Maria B.** juntas.
4. Cuando firmaron las dos, se habilita **Ana** para numerar y cerrar el documento.

Si en cualquier nivel alguien rechaza, el documento se cierra como rechazado y nadie mas firma.
