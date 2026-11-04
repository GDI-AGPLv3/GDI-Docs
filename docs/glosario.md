# Glosario

Terminos y conceptos utilizados en el sistema GDI, organizados por audiencia.

---

## Terminos de Usuario

**Actuacion Interna**
:   Accion que otorga acceso a un expediente a otro sector sin perder el control. El sector solicitante mantiene la administracion.

**Aperturas**
:   Contador que muestra cuantos sectores destinatarios abrieron una nota. Solo visible para el remitente.

**Archivar**
:   Accion de mover una nota recibida a la bandeja de archivadas. Equivale a "guardar" sin eliminar.

**Asignacion**
:   Accion de asignar un expediente a un sector responsable para su tramitacion.

**Borrador (Draft)**
:   Estado inicial de un documento. El creador puede editarlo libremente antes de enviarlo a firma.

**Caratula (CAEX)**
:   Documento autogenerado por el sistema al crear un expediente. Contiene los datos principales del tramite. No se crea manualmente.

**Certificado de origen**
:   PDF importado que ya trae la firma de certificación de otro organismo (por ejemplo, un escribano o una universidad). GDI lo guarda sin modificarlo: no le agrega la hoja de firma ni su firma digital. El número oficial figura en GDI, no dentro del PDF. Sus firmantes dan **Conformidad**.

**Chips rapidos**
:   Botones de acceso rapido en el Asistente AI del expediente (ej: "Quienes participaron", "Paso a Paso", "Que falta?").

**Conformidad**
:   Lo que registra un firmante en un PDF **certificado de origen**. El firmante aprueba el documento en GDI, pero no firma digitalmente el PDF ni usa el token. En la lista de firmantes aparece la insignia "Conformidad".

**Copiar instrucciones**
:   Funcion de la pantalla Home que copia al portapapeles las instrucciones para conectar un asistente AI externo (ChatGPT, Claude, etc.) con GDI.

**Departamento**
:   Division mayor de la estructura organizativa de la organizacion (ej: Intendencia, Legal, Hacienda). Cada departamento contiene uno o mas sectores.

**Documento**
:   Pieza documental oficial creada en el sistema. Puede ser de tipo HTML (redactado en el editor) o Importado (PDF cargado). Todo documento tiene una referencia, firmantes y un tipo.

**Documento justificante**
:   En el proceso de subsanacion, es el documento nuevo que reemplaza al documento erroneo en un expediente.

**Expediente**
:   Carpeta electronica que agrupa documentos relacionados a un tramite. Se identifica con un numero unico (ej: `EE-2026-000019-TXST-INTE`). Contiene documentos vinculados, movimientos y actuaciones.

**Firmante**
:   Usuario que debe firmar un documento. Puede haber multiples firmantes. Firman en el orden asignado.

**Nota**
:   Tipo especial de documento que incluye destinatarios (sectores) en modalidad Para/CC/CCO. Equivale a un memo o comunicacion interna oficial.

**Numerador**
:   Firmante especial que otorga el **numero oficial** al documento. Firma en ultimo lugar. Debe tener el rango adecuado para el tipo de documento.

**Numero oficial**
:   Identificador unico e inmutable asignado al documento cuando el numerador firma. Formato: `{SIGLA}-{ANO}-{SECUENCIAL}-{TENANT}-{DEPTO}`.

**Pase (PV)**
:   Documento autogenerado por el sistema al transferir un expediente de un sector a otro. No se crea manualmente.

**Propuesta de vinculacion**
:   Cuando se vincula un documento a un expediente desde el editor, la vinculacion queda como "propuesta". El administrador del expediente debe aceptarla para que sea oficial.

**Rango**
:   Nivel jerarquico de un usuario dentro del organismo. Determina que tipos de documento puede numerar (ej: un Decreto requiere rango de Intendente).

**Referencia**
:   Titulo descriptivo de un documento o expediente. Texto libre que describe el contenido o proposito (ej: *"Informe situacion patrimonial segundo trimestre"*).

**Resumen IA**
:   Texto generado automaticamente por inteligencia artificial que resume el contenido de un documento o el historial de un expediente.

**Sector**
:   Unidad organizativa dentro de un departamento. Los usuarios pertenecen a un sector (ej: PRIV = Privada, MESA = Mesa de Entradas). Los sectores son los destinatarios de las NOTAS.

**Sello**
:   Firma visual que se estampa en el PDF del documento. Cada usuario tiene un sello asignado con su nombre, cargo y sector.

**Subsanacion**
:   Proceso de correccion de un documento rechazado. El creador edita el documento y lo vuelve a enviar a firma.

**Tenant / Organizacion**
:   Cada organizacion es un "inquilino" independiente en el sistema con su propia base de datos, configuracion, tipos de documento y usuarios.

**Transferencia**
:   Movimiento que traspasa el control de un expediente de un sector a otro. El sector original pierde la administracion.

**Verificacion Documental IA**
:   Accion disponible en expedientes que solicita a la IA verificar la completitud de la documentacion.

**Vinculacion oficial**
:   Estado de un documento cuando el administrador del expediente acepta la propuesta de vinculacion.

---

## Terminos de Administracion

**BackOffice**
:   Panel de administracion del sistema. Permite gestionar organizaciones, usuarios, permisos, sectores y configuracion.

**Multi-Tenant**
:   Arquitectura donde cada organizacion tiene su propio schema PostgreSQL. El schema se determina por el `tenant_id` del JWT.

**Rank**
:   Nivel jerarquico de un funcionario dentro del organigrama. Determina que tipos de documentos puede firmar.

**Titular**
:   Funcionario con el rank mas alto de un sector. Puede firmar Decretos, Resoluciones y Disposiciones.

---

## Terminos Tecnicos

**Advisory Lock**
:   Lock a nivel de PostgreSQL (`pg_advisory_xact_lock`) usado para garantizar numeracion secuencial sin colisiones. GDI usa el key `888888`.

**API Gateway**
:   Modulo en GDI-Backend (`api_gateway/`) que expone endpoints REST y MCP Server para integracion con IAs externas (Claude, ChatGPT, Gemini).

**Auth0**
:   Servicio de autenticacion externo. Frontend obtiene JWT tokens, Backend los valida.

**CAEX**
:   Caratula de Expediente. PDF autogenerado que sirve como portada del expediente.

**Cloudflare R2**
:   Object storage compatible con S3 donde se almacenan los PDFs generados y firmados.

**Decreto**
:   Tipo de documento oficial. Requiere firma del funcionario con rank de Titular.

**Disposicion**
:   Tipo de documento oficial. Requiere firma del funcionario con rank de Titular.

**execute_query**
:   Funcion central en `db.py` del Backend para ejecutar queries SQL con schema multi-tenant.

**fetchWithAuth**
:   Funcion wrapper en el Frontend que agrega token Auth0 a todas las peticiones HTTP.

**JWT (JSON Web Token)**
:   Token de autenticacion emitido por Auth0. Contiene tenant_id, user_id, email, permissions.

**keyword-only**
:   Convencion Python donde `schema_name` siempre se pasa como argumento nombrado: `schema_name=schema_name`.

**LangGraph**
:   Framework de LangChain para agentes IA con grafos de estado. Usado en GDI-AgenteLANG.

**MCP (Model Context Protocol)**
:   Protocolo de Anthropic para conectar modelos de IA con herramientas. GDI-Backend expone un MCP Server.

**Numeracion**
:   Sistema que asigna numeros secuenciales a documentos y expedientes por tipo, sector y anio. Usa advisory lock.

**OpenRouter**
:   Servicio que provee acceso a multiples modelos LLM (Claude, GPT, etc.) via una API unificada.

**PAdES**
:   PDF Advanced Electronic Signatures. Estandar de firma digital para PDFs usado por GDI-Notary.

**pgvector**
:   Extension de PostgreSQL para busqueda por similaridad vectorial. Usado para RAG en GDI-AgenteLANG.

**Providencia**
:   Documento interno que se genera automaticamente en ciertos flujos (asignacion, transferencia de expedientes).

**PV (Providencia)**
:   Abreviatura de Providencia. Documento auto-generado.

**pyHanko**
:   Libreria Python para firma digital PAdES. Core del servicio Notary.

**Resolucion**
:   Tipo de documento oficial. Requiere firma del funcionario con rank adecuado.

**Schema (PostgreSQL)**
:   Namespace de base de datos. `public` contiene tablas globales (tenants, users). Cada organizacion tiene su propio schema (ej: `200_muni`).

**shadcn/ui**
:   Libreria de componentes React usada en el Frontend. Basada en Radix UI + Tailwind.

**TenantMiddleware**
:   Middleware FastAPI que extrae `tenant_id` del JWT y lo inyecta en el request state.

**Visual Signature**
:   Representacion grafica de la firma en el PDF. Incluye nombre, cargo, sector y fecha.
