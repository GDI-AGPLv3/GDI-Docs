# Expedientes

Un **expediente electronico** es una carpeta digital que agrupa documentos oficiales relacionados a un mismo tramite o asunto administrativo. Funciona como el equivalente digital de una carpeta fisica de expediente: reune en un solo lugar todos los informes, dictamenes, resoluciones y demas documentos que forman parte de una gestion.

---

![Listado de expedientes](../capturas/expedientes-lista.png)

## Identificacion del expediente

Cada expediente recibe un **numero oficial unico** al momento de su creacion, con el siguiente formato:

```
EE-{ANO}-{SECUENCIAL}-{TENANT}-{DEPARTAMENTO}
```

| Parte | Ejemplo | Descripcion |
|-------|---------|-------------|
| EE | `EE` | Prefijo fijo que identifica un expediente electronico |
| ANO | `2026` | Ano de creacion |
| SECUENCIAL | `000019` | Numero secuencial (6 digitos, unico por tenant) |
| TENANT | `TXST` | Codigo de la organizacion/tenant |
| DEPARTAMENTO | `INTE` | Acronimo del departamento iniciador |

Ejemplo completo: `EE-2026-000019-TXST-INTE`

---

## Composicion de un expediente

Al crearse un expediente, el sistema genera automaticamente una **caratula** (documento tipo CAEX) que contiene los datos basicos: tipo de expediente, motivo, reparticion iniciadora y numero oficial. Esta caratula queda como el primer documento del expediente.

Cada expediente tiene:

| Elemento | Descripcion |
|----------|-------------|
| **Tipo** | Categoria del tramite (ej: RRHH - Recursos Humanos, HABI - Habilitacion Comercial, COMP - Compras) |
| **Sector administrador** | El sector que tiene el control actual del expediente |
| **Actuantes** | Usuarios asignados como responsables del seguimiento |
| **Documentos oficiales** | Documentos firmados y vinculados al expediente, numerados en orden |
| **Documentos propuestos** | Documentos cuya vinculacion fue propuesta pero aun no fue aceptada |

---

## Secciones de esta guia

| Pagina | Descripcion |
|--------|-------------|
| [Detalle del Expediente](detalle-expediente.md) | Vista principal del expediente: header, documentos oficiales, documentos propuestos y acciones disponibles |
| [Movimientos](movimientos.md) | Historial de actividad, acciones en curso/finalizadas, y como crear actuaciones internas o transferencias |
| [Vincular Documentos](vincular-documentos.md) | Como vincular documentos oficiales a un expediente, aceptar o rechazar propuestas de vinculacion |
| [Subsanar en Expediente](subsanar-expediente.md) | Como reemplazar un documento dentro de un expediente aportando un justificante |
