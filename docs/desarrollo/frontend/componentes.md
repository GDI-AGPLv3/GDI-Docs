# Componentes

Todos los componentes están en `src/components/`, organizados por módulo funcional. Se usan componentes funcionales con TypeScript strict y Tailwind CSS.

## Componentes UI Base (shadcn/ui)

Ubicación: `src/components/ui/`

Estos son componentes de shadcn/ui (variante New York) construidos sobre Radix UI primitives:

| Componente | Archivo | Base | Props principales |
|------------|---------|------|-------------------|
| Button | `button.tsx` | CVA + Slot | `variant`, `size`, `asChild` |
| Input | `input.tsx` | - | `type`, `placeholder`, `className` |
| Badge | `badge.tsx` | CVA | `variant` |
| Card | `card.tsx` | - | `CardHeader`, `CardTitle`, `CardContent`, `CardFooter` |
| Dialog | `dialog.tsx` | Radix Dialog | `open`, `onOpenChange` |
| Select | `select.tsx` | Radix Select | `value`, `onValueChange` |
| Tabs | `tabs.tsx` | Radix Tabs | `value`, `onValueChange`, `defaultValue` |
| Table | `table.tsx` | - | `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell` |
| Popover | `popover.tsx` | Radix Popover | `open`, `onOpenChange` |
| Command | `command.tsx` | cmdk | `CommandInput`, `CommandList`, `CommandItem` |
| DropdownMenu | `dropdown-menu.tsx` | Radix DropdownMenu | `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem` |
| Tooltip | `tooltip.tsx` | Radix Tooltip | `TooltipTrigger`, `TooltipContent` |
| SectorBadge | `sector-badge.tsx` | CVA | `label`, `color`, `variant`, `tooltipText` |
| Accordion | `accordion.tsx` | Radix Accordion | `type`, `collapsible` |
| Alert | `alert.tsx` | CVA | `variant` |

### SectorBadge

Componente especializado para mostrar badges de sectores con colores dinámicos:

```tsx
// Con color del API (preferido)
<SectorBadge label="SECOBRA" color="#006CDB" tooltipText="Secretaria de Obras" />

// Sin color (fallback gris)
<SectorBadge label="SECOBRA" />

// Con variante estatica (legacy, evitar)
<SectorBadge label="ADMIN" variant="admin" />
```

La prop `color` genera automáticamente background (`color + 18` alpha), border (`color + 60` alpha) y texto del color base.

---

## Componentes por Módulo

### Documentos

Ubicación: `src/components/documentos/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `documentosTable` | Tabla de documentos con columnas: fecha, sector, editor, tipo, número, referencia, estado | `/documentos` |
| `documentosPaginator` | Paginación con navegación de páginas | `/documentos` |
| `FilterSlider` | Panel deslizable de filtros (tipo, estado, fecha, sector) | `/documentos` |

### Creación de Documento

Ubicación: `src/components/creacion-documento/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `creacionDocumentoHeader` | Header con título, tipo de documento y acciones (guardar, enviar a firma) | `/creacion-documento` |
| `paneles/` | Paneles dinámicos: firmantes, destinatarios NOTA, expedientes vinculados | `/creacion-documento` |

### Documentos Firma

Ubicación: `src/components/documentos-firma/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `firmadorHeader` | Header del firmador con nombre del documento y progreso | `/documentos-firma` |
| `paneles/` | Paneles: progreso de firmas, info del documento, acciones | `/documentos-firma` |

### Firma Conjunta (Batch)

Ubicación: `src/components/firma-conjunta/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `BatchSignTable` | Tabla de documentos pendientes con checkbox de selección | `/firma-conjunta` |
| `BatchSignProgress` | Barra de progreso durante la firma batch | `/firma-conjunta` |
| `BatchSignResults` | Resultados con éxitos y errores de la firma batch | `/firma-conjunta` |

### Expedientes

Ubicación: `src/components/expedientes/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `expedientesTable` | Tabla: fecha, trata, número, motivo, admin/actuantes con SectorBadge | `/expedientes` |
| `expedientesFilters` | Contenedor de filtros combinados | `/expedientes` |
| `expedientesFilter` | Filtro individual genérico | `/expedientes` |
| `expedientesPaginator` | Paginación de expedientes | `/expedientes` |
| `expedientesHeader` | Header de la página de expedientes | `/expedientes` |
| `sectorFilter` | Combobox de filtro por sector | `/expedientes` |
| `fechaFilter` | Filtro por rango de fechas | `/expedientes` |
| `ExpedienteHeader` | Header del detalle con número, trata, sectores | `/expedientes/[id]` |
| `ExpedienteTabs` | Tabs: Información, Acciones, Asistente | `/expedientes/[id]` |
| `DocumentsList` | Lista de documentos vinculados al expediente | `/expedientes/[id]` |
| `ActionSelectionMenu` | Menú de acciones: asignar, transferir, vincular, subsanar | `/expedientes/[id]` |
| `AssignmentForm` | Formulario para asignar expediente a un sector | `/expedientes/[id]` |
| `TransferForm` | Formulario para transferir expediente a otro sector | `/expedientes/[id]` |
| `CaseHistoryTimeline` | Timeline de historial del expediente | `/expedientes/[id]` |
| `MovementsPanel` | Panel de movimientos recientes | `/expedientes/[id]` |
| `crearExpedientes` | Formulario de creación de expediente | `/expedientes/crear-expedientes` |
| `VerificationPanel` | Panel de verificación de datos | `/expedientes/[id]` |
| `PermissionErrorModal` | Modal de error de permisos | `/expedientes/[id]` |
| `DuplicateAssignmentModal` | Modal para asignación duplicada | `/expedientes/[id]` |

### Notas

Ubicación: `src/components/notas/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `NotasTableReceived` | Tabla de notas recibidas con indicador de lectura | `/notas` (tab recibidas) |
| `NotasTableSent` | Tabla de notas enviadas con contador de aperturas | `/notas` (tab enviadas) |
| `NotasFilter` | Filtros de notas (fecha, búsqueda) | `/notas` |
| `NotasPaginator` | Paginación de notas | `/notas` |
| `NoteDetailHeader` | Header del detalle: remitente, destinatarios, fecha | `/notas` (detalle) |
| `NoteDetailSidebar` | Sidebar con metadatos: aperturas, estado de lectura | `/notas` (detalle) |

### Chat / Asistente

Ubicación: `src/components/chat/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `ChatContainer` | Contenedor principal del chat con scroll y mensajes | `/asistente`, `/expedientes/[id]` |
| `ChatInput` | Input de mensaje con botón de enviar | `/asistente`, `/expedientes/[id]` |
| `ChatMessage` | Burbuja de mensaje (enviado/recibido) con markdown | `/asistente`, `/expedientes/[id]` |

### Dashboard

Ubicación: `src/components/dashboard/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `FeedCard` | Card de un movimiento del feed con tipo, caso y documento | `/dashboard` |
| `FeedList` | Lista paginada de FeedCards | `/dashboard` |
| `FeedFilters` | Filtros del feed por tipo de movimiento | `/dashboard` |
| `FeedTabs` | Tabs para alternar vistas del feed | `/dashboard` |
| `StatsBar` | Barra de estadísticas del sector | `/dashboard` |

### Búsqueda

Ubicación: `src/components/search/`

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `UnifiedSearchInput` | Input de búsqueda con detección de tipo y dropdown | Header global |
| `SearchResultsTable` | Tabla de resultados dividida por documentos y expedientes | Header global |

### Componentes Globales

Ubicación: `src/components/` (raíz)

| Componente | Descripción | Donde se usa |
|------------|-------------|--------------|
| `Editor.tsx` | Editor rich text (React Quill) | `/creacion-documento` |
| `PDFViewer.tsx` | Visualizador de PDFs | `/previsualizar-documento`, `/documentos-firma` |
| `menuLateral.tsx` | Menú lateral de navegación principal | Layout global |
| `modalRejectDocument.tsx` | Modal para rechazar documento con motivo | `/documentos-firma` |
| `modalSuccesFirma.tsx` | Modal de confirmación de firma exitosa | `/documentos-firma` |
| `newDocumentoPopUp.tsx` | Popup para seleccionar tipo de documento nuevo | `/documentos` |
| `DocumentResume.tsx` | Resumen de documento (AI summary) | Varios |
| `DocumentSearchInput.tsx` | Input de búsqueda de documentos | Varios |
| `PersonalCardPopUp.tsx` | Popup con datos del usuario | Header |
| `PdfDropzone.tsx` | Zona de drag & drop para PDFs importados | `/creacion-documento` |
| `VincularDocumentoModal.tsx` | Modal para vincular documento a expediente | `/expedientes/[id]` |
| `Spinner.tsx` | Indicador de carga | Global |
| `AsistenteWelcome.tsx` | Mensaje de bienvenida del asistente | `/asistente` |
| `alertDocumentRejected.tsx` | Alerta de documento rechazado | `/creacion-documento` |
