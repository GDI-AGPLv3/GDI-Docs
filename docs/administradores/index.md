---
hide:
  - toc
---

# Administradores - BackOffice

**Panel de administración** del Sistema de Gestión Documental Inteligente para gobiernos LATAM.

Esta sección documenta el uso del BackOffice, la herramienta de administración para gestionar organizaciones, usuarios, permisos, sectores y configuración del sistema.

---

<div class="grid cards" markdown>

-   :material-information:{ .lg .middle } **Información General**

    ---

    Datos institucionales de la organización: nombre, acrónimo, ciudad de firma, logo y color institucional.

    [:octicons-arrow-right-24: Ver sección](informacion-general.md)

-   :material-stamp:{ .lg .middle } **Roles y Sellos**

    ---

    Rangos jerárquicos y sellos de firma. Define quien puede numerar cada tipo de documento.

    [:octicons-arrow-right-24: Ver sección](roles-y-sellos.md)

-   :material-sitemap:{ .lg .middle } **Organigrama**

    ---

    Estructura organizativa: reparticiones, sectores, usuarios asignados y responsables.

    [:octicons-arrow-right-24: Ver sección](organigrama.md)

-   :material-file-cog:{ .lg .middle } **Tipos de Documentos**

    ---

    Configurar tipos de documento habilitados, restricciones por sector y por rango. Catálogo global.

    [:octicons-arrow-right-24: Ver sección](tipos-de-documentos.md)

-   :material-folder-cog:{ .lg .middle } **Tipos de Expedientes**

    ---

    Configurar tipos de expediente habilitados, departamentos permitidos y catálogo global.

    [:octicons-arrow-right-24: Ver sección](tipos-de-expedientes.md)

-   :material-lock:{ .lg .middle } **Expedientes y Documentos Reservados**

    ---

    Modelo de confidencialidad por tipo (`is_reserved`): quien ve un ítem reservado, integridad al vincular y contenido fuera de la IA.

    [:octicons-arrow-right-24: Ver sección](reservados.md)

-   :material-earth:{ .lg .middle } **Documentos y Legajos Públicos**

    ---

    Tercera pata de visibilidad: abrir documentos y legajos a la ciudadanía sin login. Configuración por tipo/familia, API pública y reglas de seguridad.

    [:octicons-arrow-right-24: Ver sección](documentos-publicos.md)

-   :material-book-open-page-variant:{ .lg .middle } **Digesto Normativo Público**

    ---

    Guía paso a paso para publicar el digesto del municipio: tipos públicos, carga de normas, legajos NORMA y conexión del portal vía API.

    [:octicons-arrow-right-24: Ver sección](digesto-normativo.md)

-   :material-folder-multiple:{ .lg .middle } **Familias de Registro**

    ---

    Plantillas para legajos: campos, permisos por sector, estados configurables y códigos de familia.

    [:octicons-arrow-right-24: Ver sección](familias-registro.md)

-   :material-account-group:{ .lg .middle } **Usuarios**

    ---

    Administrar usuarios: crear, editar, asignar sectores, roles, sellos y permisos de búsqueda.

    [:octicons-arrow-right-24: Ver sección](usuarios.md)

-   :material-shield-account:{ .lg .middle } **Administración**

    ---

    Gestionar que usuarios tienen permisos de administrador en el BackOffice.

    [:octicons-arrow-right-24: Ver sección](administracion.md)

-   :material-certificate:{ .lg .middle } **Certificados**

    ---

    Gestionar certificados digitales para firma electrónica de documentos.

    [:octicons-arrow-right-24: Ver sección](certificados.md)

-   :material-backup-restore:{ .lg .middle } **Backups (GDI Sync)**

    ---

    Descarga una copia local y siempre actualizada de todos los datos y documentos del municipio.

    [:octicons-arrow-right-24: Ver sección](backups.md)

-   :material-scale-balance:{ .lg .middle } **Implementación GDI**

    ---

    Guía de implementación en el municipio: marco normativo, hoja de ruta y modelos de ordenanza, decreto y resolución.

    [:octicons-arrow-right-24: Ver sección](implementacion/index.md)

</div>

---

## Menú del BackOffice

El sidebar izquierdo del BackOffice contiene las siguientes secciones:

| Sección | Descripción | Estado |
|---------|-------------|--------|
| **Información general** | Datos y branding de la organización | Documentado |
| **Roles y Sellos** | Jerarquías y sellos de firma | Documentado |
| **Organigrama** | Estructura organizativa | Documentado |
| **Tipos de Documentos** | Catálogo de tipos de documento | Documentado |
| **Tipos de Expedientes** | Catálogo de tipos de expediente | Documentado |
| **Familias de Registro** | Plantillas para legajos (campos, permisos, estados) | Documentado |
| **Usuarios** | Gestión de usuarios | Documentado |
| **Administración** | Permisos de admin | Documentado |
| **Certificados** | Certificados digitales | Próximamente |
| **Backups** | Copia local de datos y documentos (GDI Sync) | Documentado |
| **Integraciones** | Integraciones externas | No disponible |
| **API Key** | Claves de API | No disponible |
| **Auditorías** | Registros de auditoría | No disponible |

## Acceso al BackOffice

El BackOffice es accesible en un puerto separado (`:3013`) y requiere credenciales de administrador. Solo usuarios con permisos de administración pueden acceder a estas funcionalidades.

| Componente | Puerto | URL |
|-----------|--------|-----|
| BackOffice Frontend | `:3013` | `https://backoffice.gdi.app` |
| BackOffice Backend | `:8010` | API interna |
