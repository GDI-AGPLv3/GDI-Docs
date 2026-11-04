# Páginas

Todas las páginas usan Next.js Pages Router. Cada archivo en `src/pages/` se mapea directamente a una ruta URL.

## Mapa de Rutas

| Ruta | Archivo | Autenticación | Descripción |
|------|---------|:-------------:|-------------|
| `/` | `index.tsx` | No | Landing page, redirect si autenticado |
| `/login` | `login/` | No | Login con Auth0 |
| `/select-tenant` | `select-tenant/` | Sí | Selector de organización (multi-tenant) |
| `/dashboard` | `dashboard/` | Sí | Panel principal con feed de actividad |
| `/documentos` | `documentos/` | Sí | Lista de documentos del usuario |
| `/creacion-documento` | `creacion-documento/` | Sí | Editor rich text de documentos |
| `/previsualizar-documento` | `previsualizar-documento/` | Sí | Preview PDF del documento |
| `/documentos-firma` | `documentos-firma/` | Sí | Vista de firma de documento |
| `/firma-conjunta` | `firma-conjunta/` | Sí | Firma por lotes (batch) |
| `/expedientes` | `expedientes/` | Sí | Lista de expedientes |
| `/expedientes/[id]` | `expedientes/[id].tsx` | Sí | Detalle de expediente (tabs) |
| `/expedientes/crear-expedientes` | `expedientes/crear-expedientes/` | Sí | Crear nuevo expediente |
| `/notas` | `notas/` | Sí | Notas internas (recibidas/enviadas/archivadas) |
| `/asistente` | `asistente/` | Sí | Chat con IA |
| `/mi-equipo` | `mi-equipo/` | Sí | Gestión de equipo/sector |
| `/notificaciones` | `notificaciones/` | Sí | Centro de notificaciones |
| `/design-system` | `design-system/` | No | Showcase del design system |
| `/no-access` | `no-access/` | No | Página de acceso denegado |
| `/loading` | `loading/` | No | Pantalla de carga |

## Detalle por Página

### `/` - Landing Page

**Archivo**: `src/pages/index.tsx`

- Muestra la página de bienvenida con botón de login
- Si el usuario ya está autenticado, ejecuta el flujo de onboarding:
    - Obtiene lista de tenants del usuario vía `useOnboarding`
    - Si tiene 1 solo tenant: auto-selecciona y redirige a `/dashboard`
    - Si tiene 2+ tenants: redirige a `/select-tenant`
- Muestra mensajes de sesión expirada (`?session_expired=true`) o logout exitoso (`?logged_out=true`)

**Hooks**: `useAuth`, `useOnboarding`

---

### `/dashboard` - Panel Principal

**Archivo**: `src/pages/dashboard/index.tsx`

- Feed de actividad con movimientos de expedientes del sector
- Barra de estadísticas (cantidad de expedientes en el sector)
- Filtros por tipo de movimiento y fecha
- Paginación del feed

**Componentes**: `FeedList`, `FeedCard`, `FeedFilters`, `FeedTabs`, `StatsBar`

---

### `/documentos` - Lista de Documentos

**Archivo**: `src/pages/documentos/index.tsx`

- Tabla paginada de documentos del usuario actual
- Filtros por tipo de documento, estado, fecha y sector
- Click en documento navega a `/creacion-documento` (edición) o `/documentos-firma` (firma) según estado
- Botón para crear nuevo documento

**Componentes**: `documentosTable`, `documentosPaginator`, `FilterSlider`
**Hooks**: `useDocumentTypes`

---

### `/creacion-documento` - Editor de Documentos

**Archivo**: `src/pages/creacion-documento/index.tsx`

- Editor rich text con React Quill para crear/editar documentos
- Panel lateral con información del documento (tipo, referencia, firmantes)
- Selección de firmantes con orden secuencial
- Para documentos tipo NOTA: selección de destinatarios (TO/CC/BCC)
- Opciones: guardar borrador, enviar a firma, previsualizar

**Parámetros URL**: `?document_id=UUID` (para editar existente), `?document_type=ACRONYM` (para crear nuevo)

**Componentes**: `Editor`, `creacionDocumentoHeader`, paneles dinámicos
**Hooks**: `useCreateDocument`, `useSaveDocument`, `useStartSigningProcess`, `useDocumentDetails`

---

### `/previsualizar-documento` - Preview PDF

**Archivo**: `src/pages/previsualizar-documento/index.tsx`

- Visualización del PDF generado del documento
- Información de firmantes y estado
- Botón para volver al editor o enviar a firma

**Parámetros URL**: `?document_id=UUID`

**Componentes**: `PDFViewer`
**Hooks**: `usePreviewDocumentInfo`, `usePdfDownload`

---

### `/documentos-firma` - Firma de Documento

**Archivo**: `src/pages/documentos-firma/index.tsx`

- Vista del PDF del documento a firmar
- Progreso de firmas (completadas/total)
- Botones de firmar o rechazar
- Modal de confirmación de firma exitosa
- Modal de rechazo con motivo

**Parámetros URL**: `?document_id=UUID`

**Componentes**: `firmadorHeader`, `PDFViewer`, `modalSuccesFirma`, `modalRejectDocument`
**Hooks**: `useSignDocument`, `useRejectDocument`, `useUnifiedDocumentDetails`

---

### `/firma-conjunta` - Firma por Lotes

**Archivo**: `src/pages/firma-conjunta/index.tsx`

- Tabla de documentos pendientes de firma del usuario
- Selección múltiple para firma en lote
- Progreso de firma batch con resultados

**Componentes**: `BatchSignTable`, `BatchSignProgress`, `BatchSignResults`
**Hooks**: `useBatchSign`

---

### `/expedientes` - Lista de Expedientes

**Archivo**: `src/pages/expedientes/index.tsx`

- Tabla paginada de expedientes accesibles por el usuario
- Filtros por trata (tipo), sector, fecha y búsqueda libre
- Badges de color por sector (administrador/actuantes)
- Click navega a `/expedientes/[id]`

**Componentes**: `expedientesTable`, `expedientesFilters`, `expedientesPaginator`, `sectorFilter`, `fechaFilter`

---

### `/expedientes/[id]` - Detalle de Expediente

**Archivo**: `src/pages/expedientes/[id].tsx`

- Header con número, trata, motivo y sectores
- Tres tabs principales:
    - **Información**: Documentos vinculados, documentos propuestos
    - **Acciones**: Asignar sector, transferir, vincular documento, subsanar
    - **Asistente**: Chat IA contextual al expediente
- Timeline de movimientos del expediente

**Parámetros URL**: `id` (UUID del expediente, parámetro de ruta dinámica)

**Componentes**: `ExpedienteHeader`, `ExpedienteTabs`, `DocumentsList`, `ActionSelectionMenu`, `AssignmentForm`, `TransferForm`, `CaseHistoryTimeline`, `MovementsPanel`, `ChatContainer`
**Hooks**: `useExpedienteData`, `useExpedienteDocuments`, `useCaseHistory`, `useCaseMovements`, `useChatFastAPI`

---

### `/expedientes/crear-expedientes` - Crear Expediente

**Archivo**: `src/pages/expedientes/crear-expedientes/index.tsx`

- Formulario para crear un nuevo expediente
- Selección de plantilla/trata
- Campo de referencia (motivo)
- Selección de sector administrador

**Componentes**: `crearExpedientes`

---

### `/notas` - Notas Internas

**Archivo**: `src/pages/notas/index.tsx`

- Tres tabs: Recibidas, Enviadas, Archivadas
- Tabla paginada con filtros por fecha y búsqueda
- Indicador de lectura para notas recibidas
- Click abre detalle de la nota con PDF y metadata

**Componentes**: `NotasTableReceived`, `NotasTableSent`, `NotasFilter`, `NotasPaginator`, `NoteDetailHeader`, `NoteDetailSidebar`
**Hooks**: `useNotesReceived`, `useNotesSent`, `useNotesArchived`, `useNoteDetail`, `useArchiveNote`

---

### `/asistente` - Chat con IA

**Archivo**: `src/pages/asistente/index.tsx`

- Chat general con el asistente IA (GDI-AgenteLANG)
- Markdown rendering para respuestas
- Fuentes de documentos usadas (RAG)

**Componentes**: `ChatContainer`, `ChatInput`, `ChatMessage`, `AsistenteWelcome`
**Hooks**: `useChatFastAPI`

---

### `/design-system` - Showcase

**Archivo**: `src/pages/design-system/index.tsx`

- Página sin autenticación para referencia visual del design system
- Muestra todos los componentes shadcn/ui con variantes
- Colores, badges, botones, inputs, tablas, modales, etc.
- Incluye SectorBadge con colores dinámicos

!!! info "Uso interno"
    Esta página es solo para desarrollo. No aparece en la navegación de la aplicación.
