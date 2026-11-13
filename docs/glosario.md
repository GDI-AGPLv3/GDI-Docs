# Glosario

Términos y conceptos utilizados en el sistema GDI, organizados por audiencia.

---

## Términos de Usuario

**Actuación Interna**
:   Acción que otorga acceso a un expediente a otro sector sin perder el control. El sector solicitante mantiene la administración.

**Aperturas**
:   Contador que muestra cuántos sectores destinatarios abrieron una nota. Solo visible para el remitente.

**Archivar**
:   Acción de mover una nota recibida a la bandeja de archivadas. Equivale a "guardar" sin eliminar.

**Asignación**
:   Acción de asignar un expediente a un sector responsable para su tramitación.

**Borrador (Draft)**
:   Estado inicial de un documento. El creador puede editarlo libremente antes de enviarlo a firma.

**Carátula (CAEX)**
:   Documento autogenerado por el sistema al crear un expediente. Contiene los datos principales del trámite. No se crea manualmente.

**Certificado de origen**
:   PDF importado que ya trae la firma de certificación de otro organismo (por ejemplo, un escribano o una universidad). GDI lo guarda sin modificarlo: no le agrega la hoja de firma ni su firma digital. El número oficial figura en GDI, no dentro del PDF. Sus firmantes dan **Conformidad**.

**Chips rápidos**
:   Botones de acceso rápido en el Asistente AI del expediente (ej: "Quienes participaron", "Paso a Paso", "Que falta?").

**Conformidad**
:   Lo que registra un firmante en un PDF **certificado de origen**. El firmante aprueba el documento en GDI, pero no firma digitalmente el PDF ni usa el token. En la lista de firmantes aparece la insignia "Conformidad".

**Copiar instrucciones**
:   Función de la pantalla Home que copia al portapapeles las instrucciones para conectar un asistente AI externo (ChatGPT, Claude, etc.) con GDI.

**Departamento**
:   División mayor de la estructura organizativa de la organización (ej: Intendencia, Legal, Hacienda). Cada departamento contiene uno o más sectores.

**Documento**
:   Pieza documental oficial creada en el sistema. Puede ser de tipo HTML (redactado en el editor) o Importado (PDF cargado). Todo documento tiene una referencia, firmantes y un tipo.

**Documento justificante**
:   En el proceso de subsanación, es el documento nuevo que reemplaza al documento erróneo en un expediente.

**Expediente**
:   Carpeta electrónica que agrupa documentos relacionados a un trámite. Se identifica con un número único (ej: `EE-2026-000019-TXST-INTE`). Contiene documentos vinculados, movimientos y actuaciones.

**Firmante**
:   Usuario que debe firmar un documento. Puede haber múltiples firmantes. Firman en el orden asignado.

**Nota**
:   Tipo especial de documento que incluye destinatarios (sectores) en modalidad Para/CC/CCO. Equivale a un memo o comunicación interna oficial.

**Numerador**
:   Firmante especial que otorga el **número oficial** al documento. Firma en último lugar. Debe tener el rango adecuado para el tipo de documento.

**Número oficial**
:   Identificador único e inmutable asignado al documento cuando el numerador firma. Formato: `{SIGLA}-{ANO}-{SECUENCIAL}-{TENANT}-{DEPTO}`.

**Pase (PV)**
:   Documento autogenerado por el sistema al transferir un expediente de un sector a otro. No se crea manualmente.

**Propuesta de vinculación**
:   Cuando se vincula un documento a un expediente desde el editor, la vinculación queda como "propuesta". El administrador del expediente debe aceptarla para que sea oficial.

**Rango**
:   Nivel jerárquico de un usuario dentro del organismo. Determina que tipos de documento puede numerar (ej: un Decreto requiere rango de Intendente).

**Referencia**
:   Título descriptivo de un documento o expediente. Texto libre que describe el contenido o propósito (ej: *"Informe situación patrimonial segundo trimestre"*).

**Resumen IA**
:   Texto generado automáticamente por inteligencia artificial que resume el contenido de un documento o el historial de un expediente.

**Sector**
:   Unidad organizativa dentro de un departamento. Los usuarios pertenecen a un sector (ej: PRIV = Privada, MESA = Mesa de Entradas). Los sectores son los destinatarios de las NOTAS.

**Sello**
:   Firma visual que se estampa en el PDF del documento. Cada usuario tiene un sello asignado con su nombre, cargo y sector.

**Subsanación**
:   Proceso de corrección de un documento rechazado. El creador edita el documento y lo vuelve a enviar a firma.

**Tenant / Organización**
:   Cada organización es un "inquilino" independiente en el sistema con su propia base de datos, configuración, tipos de documento y usuarios.

**Transferencia**
:   Movimiento que traspasa el control de un expediente de un sector a otro. El sector original pierde la administración.

**Verificación Documental IA**
:   Acción disponible en expedientes que solicita a la IA verificar la completitud de la documentación.

**Vinculación oficial**
:   Estado de un documento cuando el administrador del expediente acepta la propuesta de vinculación.

---

## Términos de Administración

**BackOffice**
:   Panel de administración del sistema. Permite gestionar organizaciones, usuarios, permisos, sectores y configuración.

**Multi-Tenant**
:   Arquitectura donde cada organización tiene su propio schema PostgreSQL. El schema se determina por el `tenant_id` del JWT.

**Rank**
:   Nivel jerárquico de un funcionario dentro del organigrama. Determina que tipos de documentos puede firmar.

**Titular**
:   Funcionario con el rank más alto de un sector. Puede firmar Decretos, Resoluciones y Disposiciones.

---

## Términos Técnicos

**Advisory Lock**
:   Lock a nivel de PostgreSQL (`pg_advisory_xact_lock`) usado para garantizar numeración secuencial sin colisiones. GDI usa el key `888888`.

**Almacenamiento S3**
:   Almacenamiento de objetos compatible con S3 donde se guardan los PDFs generados y firmados.

**API Gateway**
:   Módulo en GDI-Backend (`api_gateway/`) que expone endpoints REST y MCP Server para integración con IAs externas (Claude, ChatGPT, Gemini).

**CAEX**
:   Carátula de Expediente. PDF autogenerado que sirve como portada del expediente.

**Decreto**
:   Tipo de documento oficial. Requiere firma del funcionario con rank de Titular.

**Disposición**
:   Tipo de documento oficial. Requiere firma del funcionario con rank de Titular.

**execute_query**
:   Función central en `db.py` del Backend para ejecutar queries SQL con schema multi-tenant.

**fetchWithAuth**
:   Función wrapper en el Frontend que agrega el token del proveedor de autenticación a todas las peticiones HTTP.

**JWT (JSON Web Token)**
:   Token de autenticación emitido por el proveedor de autenticación. Contiene tenant_id, user_id, email, permissions.

**keyword-only**
:   Convención Python donde `schema_name` siempre se pasa como argumento nombrado: `schema_name=schema_name`.

**LangGraph**
:   Framework de LangChain para agentes IA con grafos de estado. Usado en GDI-AgenteLANG.

**MCP (Model Context Protocol)**
:   Protocolo de Anthropic para conectar modelos de IA con herramientas. GDI-Backend expone un MCP Server.

**Numeración**
:   Sistema que asigna números secuenciales a documentos y expedientes por tipo, sector y año. Usa advisory lock.

**PAdES**
:   PDF Advanced Electronic Signatures. Estándar de firma digital para PDFs usado por GDI-Notary.

**pgvector**
:   Extensión de PostgreSQL para búsqueda por similaridad vectorial. Usado para RAG en GDI-AgenteLANG.

**Proveedor de autenticación**
:   Servicio de autenticación externo (OIDC/OAuth 2.0). El Frontend obtiene los tokens JWT y el Backend los valida.

**Proveedor de modelos LLM**
:   Servicio que da acceso a varios modelos LLM (Claude, GPT, etc.) con una sola API.

**Providencia**
:   Documento interno que se genera automáticamente en ciertos flujos (asignación, transferencia de expedientes).

**PV (Providencia)**
:   Abreviatura de Providencia. Documento auto-generado.

**pyHanko**
:   Librería Python para firma digital PAdES. Core del servicio Notary.

**Resolución**
:   Tipo de documento oficial. Requiere firma del funcionario con rank adecuado.

**Schema (PostgreSQL)**
:   Namespace de base de datos. `public` contiene tablas globales (tenants, users). Cada organización tiene su propio schema (ej: `200_muni`).

**shadcn/ui**
:   Librería de componentes React usada en el Frontend. Basada en Radix UI + Tailwind.

**TenantMiddleware**
:   Middleware FastAPI que extrae `tenant_id` del JWT y lo inyecta en el request state.

**Visual Signature**
:   Representación gráfica de la firma en el PDF. Incluye nombre, cargo, sector y fecha.
