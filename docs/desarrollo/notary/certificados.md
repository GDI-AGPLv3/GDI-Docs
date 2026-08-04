# Certificados digitales

Los certificados PKCS#12 (`.p12`) que usa Notary para firmar PAdES **no viven en el
microservicio**: se almacenan en **Cloudflare R2**, la metadata y el password
encriptado en **PostgreSQL**, y viajan a Notary por multipart en cada firma.

!!! info "Estado: implementado"
    El esquema de certificados en R2 dejo de ser roadmap. El almacenamiento local
    (`certs/{tenant_id}.p12` + `passwords.json`) quedo como modo legacy de desarrollo:
    el codigo sigue existiendo en `certificate_loader.py`, pero **Notary ya no lo usa
    para resolver certificados** (ver "Modo legacy" al final).

## Arquitectura

```
BackOffice-Back            R2                     Backend                Notary
     |                      |                        |                     |
  upload/finalize  ---->  .p12                       |                     |
  password (Fernet) --> public.tenant_certificates   |                     |
                                                     |                     |
                                          resolve_certificate()            |
                                          (BD + R2 + cache 5 min)          |
                                                     |                     |
                                          multipart: cert_file + ---->  load_certificate_from_bytes()
                                                     cert_password         |
                                                                    pyHanko firma PAdES
```

| Componente | Repo / archivo | Responsabilidad |
|---|---|---|
| Carga y armado del `.p12` | `GDI-BackOffice-Back/services/certificate_service.py` | Valida, encripta password, sube a R2, upsert en BD |
| Resolucion en firma | `GDI-Backend/services/shared/certificate_resolver.py` | Lee BD, desencripta password, descarga de R2, cachea |
| Carga en memoria | `GDI-Notary/app/certificate_loader.py` | `load_certificate_from_bytes()` + tempfile seguro |
| Firma | `GDI-Notary/app/pades_signer.py` | pyHanko PAdES-B-T |

## Almacenamiento

**R2** (bucket `CERT_R2_BUCKET`, default `gdi-certificates`):

```
gdi-certificates/
└── {tenant_id}/
    └── certificate.p12
```

**PostgreSQL** — tabla `public.tenant_certificates` (schema `public`, accesible desde
cualquier `search_path`), un registro por tenant (`ON CONFLICT (tenant_id) DO UPDATE`):

| Columna | Contenido |
|---|---|
| `tenant_id` | Schema del tenant. Es la clave: 1 certificado por municipio |
| `r2_bucket` / `r2_key` | Ubicacion del `.p12` |
| `encrypted_password` | Password del `.p12` encriptada con **Fernet** (`CERT_MASTER_KEY`) |
| `subject_cn`, `subject_org`, `issuer_cn`, `serial_number` | Metadata extraida del certificado |
| `not_valid_before`, `not_valid_after` | Vigencia |
| `fingerprint_sha256` | Huella SHA-256 (se muestra en el BackOffice) |
| `file_size_bytes`, `is_active`, `uploaded_by`, `created_at`, `updated_at` | Auditoria |

!!! warning "El password nunca se guarda en claro"
    Se encripta con Fernet usando `CERT_MASTER_KEY`. Si se rota esa key, **todos** los
    passwords guardados dejan de desencriptarse y hay que volver a subir los certificados.

## Variables de entorno

| Variable | Donde | Descripcion |
|---|---|---|
| `CERT_MASTER_KEY` | BackOffice-Back + Backend | Clave Fernet para encriptar/desencriptar el password del `.p12`. Debe ser **la misma** en ambos |
| `CERT_R2_BUCKET` | BackOffice-Back + Backend | Bucket de certificados (default `gdi-certificates`) |
| `CF_R2_ENDPOINT` | BackOffice-Back + Backend | Endpoint S3 de R2 |
| `CF_R2_ACCESS_KEY_ID` / `CF_R2_SECRET_ACCESS_KEY` | BackOffice-Back + Backend | Credenciales R2 |
| `S3_FORCE_PATH_STYLE` | Backend | `true` para MinIO (on-premise). R2 usa virtual-hosted |
| `FALLBACK_TO_VISUAL` | Notary | `false` en PRD: sin certificado, la firma falla en vez de degradar a visual |

## Endpoints de administracion (BackOffice-Back)

Todos bajo `/admin/certificates`, requieren rol Administrador. El `tenant_id` se
**bindea al schema del admin** (GDI-143): mandar otro devuelve `403`.

| Metodo | Endpoint | Proposito |
|---|---|---|
| POST | `/admin/certificates` | Sube un `.p12` + password (max 5MB) |
| POST | `/admin/certificates/generate-csr` | Genera key RSA 2048 + CSR para AC ONTI (no persiste nada) |
| POST | `/admin/certificates/finalize` | Combina el `.cer` de ONTI + el `.key` en un `.p12` y lo activa |
| GET | `/admin/certificates` | Lista el certificado del tenant |
| GET | `/admin/certificates/{tenant_id}` | Info del certificado |
| DELETE | `/admin/certificates/{tenant_id}` | Borra de R2 y BD |
| POST | `/admin/certificates/send-instructions` | Manda por mail el instructivo ONTI al admin |

### Flujo ONTI (generate-csr → finalize)

1. `generate-csr` arma una clave RSA 2048 y un CSR con el subject que exige AC ONTI:
   `CN`, `serialNumber = CUIT {11 digitos}`, `O`, `OU`, `C=AR`. Cada campo se valida a
   **64 octetos UTF-8** (no 64 caracteres). Devuelve `key_pem` + `csr_pem` con
   `Cache-Control: no-store` — **GDI no almacena la clave privada**.
2. El municipio presenta el `.csr` ante ONTI y recibe un `.cer`.
3. `finalize` recibe `.cer` + `.key` + password y:
    - carga el `.cer` soportando **PEM, DER y PKCS#7** (`.p7b`/`.p7c`), con o sin cadena;
    - valida vigencia (no vencido, no futuro);
    - verifica que la clave publica del `.key` coincida con la del `.cer` (bloqueante:
      evita generar un `.p12` roto);
    - serializa el `.p12` con `BestAvailableEncryption` incluyendo la cadena;
    - delega en `upload_certificate()` (misma ruta que la subida directa).

### Validaciones al subir

| Regla | Valor |
|---|---|
| Extension | `.p12` (subida directa) · `.cer/.crt/.pem/.p7b/.p7c/.der` (finalize) |
| Tamano `.p12` | 5 MB |
| Tamano `.cer` | 1 MB |
| Tamano `.key` | 512 KB |
| Password (finalize) | Minimo 8 caracteres |
| Contenido | El `.p12` debe traer clave privada **y** certificado, y abrir con el password |

## Resolucion en tiempo de firma (Backend)

`resolve_certificate(tenant_id, *, schema_name)` devuelve `(p12_bytes, password)`:

1. Cache en memoria, **TTL 300s** (`_cache`, protegido por lock). `invalidate_cache()`
   permite purgar un tenant o todos.
2. `SELECT r2_bucket, r2_key, encrypted_password FROM public.tenant_certificates
   WHERE tenant_id = $1 AND is_active = true`.
3. Desencripta el password con Fernet.
4. Descarga el `.p12` de R2.

El resultado se manda a Notary como multipart (`cert_file` + `cert_password`) desde
`services/shared/notary_api.py`.

!!! note "El cache es por proceso"
    Cada worker de Gunicorn tiene su propio cache. Tras reemplazar un certificado,
    la firma puede seguir usando el anterior hasta 5 minutos.

## Carga en Notary

`load_certificate_from_bytes(p12_bytes, password, tenant_id)` carga el PKCS#12 en
memoria y escribe un tempfile porque **pyHanko requiere un path**:

- Prefiere `/dev/shm` (tmpfs en memoria — el material clave nunca toca disco).
  En Windows/dev-local cae a `tempfile.gettempdir()`.
- Aplica `chmod 0o600` **antes** de escribir el contenido.
- Ante error al preparar el archivo, cierra el fd y borra el tempfile.

`LoadedCertificate` guarda `_password` y `_temp_file` con `repr=False` para que no
aparezcan en logs.

### Modos de firma en `/sign-pdf`

| Modo | Condicion | Resultado |
|---|---|---|
| **1 — multipart** | Llegan `cert_file` + `cert_password` y `use_pades=true` | Firma PAdES. **Unico modo activo** |
| **2 — local** | Solo llega `tenant_id` | Deshabilitado: loguea warning. Con `FALLBACK_TO_VISUAL=false` devuelve `400 CERTIFICATE_NOT_PROVIDED` |

## Validacion del certificado

`validate_certificate()` verifica vigencia y `key_usage.digital_signature`:

```python
def validate_certificate(cert: LoadedCertificate) -> Tuple[bool, str]:
    now = datetime.now(timezone.utc)
    if now < cert.certificate.not_valid_before_utc:
        return False, "Certificado aun no es valido"
    if now > cert.certificate.not_valid_after_utc:
        return False, "Certificado expirado"
    # key_usage: si la extension no existe, se asume valido
    ...
```

## Seguridad: path traversal (modo legacy)

`get_certificate_path()` verifica contencion de path, y `validators.py` valida el
formato del `tenant_id` con `^[a-zA-Z0-9_-]+$`:

```python
certs_dir = Path(CERTS_DIR).resolve()
cert_path = (certs_dir / f"{tenant_id}.p12").resolve()
if not cert_path.is_relative_to(certs_dir):
    raise CertificateError("Invalid tenant_id: path traversal detected")
```

## Excepciones

| Excepcion | Causa |
|---|---|
| `CertificateNotFoundError` | No existe `.p12` para el tenant (modo legacy) |
| `PasswordNotFoundError` | No hay password en `passwords.json` (modo legacy) |
| `CertificateLoadError` | Password incorrecto, formato invalido, o `.p12` sin key/cert |
| `CertificateError` | Error generico de certificado |

## Modo legacy: certificados locales (solo desarrollo)

`certs/{tenant_id}.p12` + `certs/passwords.json` siguen soportados por
`load_certificate()`, pero **Notary ya no los usa** para firmar: el certificado llega
siempre por multipart. Sirven para tests unitarios y para generar material de prueba.

```bash
python scripts/generate_test_cert.py \
  --tenant 100_test \
  --cn "GESTION DOCUMENTAL INTELIGENTE" \
  --org "Municipalidad del Futuro" \
  --password test123
```

| Opcion | Default | Descripcion |
|---|---|---|
| `--tenant` / `-t` | (requerido) | ID del tenant |
| `--password` / `-p` | `test123` | Password del `.p12` |
| `--output` / `-o` | `../certs` | Directorio de salida |
| `--days` / `-d` | `365` | Dias de validez |
| `--cn` | Auto-generado | Common Name |
| `--org` | Auto-generado | Organization |
| `--no-passwords-file` | - | No actualizar `passwords.json` |

El certificado generado es RSA 2048 / SHA-256, con Key Usage *Digital Signature +
Content Commitment*, pais AR.

!!! danger "Solo para pruebas"
    Son certificados **auto-firmados**: no sirven para produccion. En PRD el
    certificado lo carga el municipio desde el BackOffice
    (ver [Certificados — Administradores](../../administradores/certificados.md)).
