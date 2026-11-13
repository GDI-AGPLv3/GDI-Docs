#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guarda de publicacion: falla si la documentacion filtra datos internos.

Este repositorio NO tiene version privada: todo lo que entra se publica en
docs.gdilatam.com. Por eso el control corre ANTES del deploy y lo bloquea.

Uso:
    python scripts/check_publishable.py            # revisa docs/, skills/ y mkdocs.yml
    python scripts/check_publishable.py <ruta>...  # revisa rutas puntuales

Salida: 0 si esta limpio, 1 si encontro algo (con archivo:linea y que hacer).

Si un hallazgo es un falso positivo, agregalo a ALLOW (con su motivo) en vez de
apagar la regla: la proxima persona necesita saber por que ese caso es legitimo.
"""
import os
import re
import sys

# --------------------------------------------------------------------------
# Lo que SE MANTIENE a proposito: marca publica y ejemplos didacticos.
# Se evalua antes que las reglas; si la linea contiene alguno de estos, se salta.
# --------------------------------------------------------------------------
ALLOW = [
    "docs.gdilatam.com",            # este mismo sitio
    "www.gdilatam.com",             # web publica
    "mcp.gdilatam.com",             # endpoint MCP publico
    "ecosistema.gdilatam.com",      # portal publico
    "firmadorgdi.gdilatam.com",     # descarga publica del firmador
    "soporte@gdilatam.com",         # contacto publico
    "info@gdilatam.com",            # contacto publico
    "tu-municipio-gateway",         # placeholder didactico del manual
    "your-domain.com",              # placeholders de la doc
    "your-fly-org",
    "<your-",
    "100_test",                     # tenant de pruebas, publico a proposito
    "100_mt",                       # idem
    "101_ejemplo", "200_ejemplo", "100_example", "101_example",
    "gdi-ejemplo-",
    # placeholders genericos que la doc ya usa como ejemplo (no son clientes)
    "_muni", "tenant-municipio", "gdi-municipio",
    "{schema", "<schema", "schema_municipio", "{tenant", "<tenant",
    "USER:PASSWORD", "postgres:password", "user:pass",  # ejemplos de conexion
    "{uuid", "uuid_sin_guiones",
    "214c5d1695ea4865876de8e826ef3ece",  # UUID de ejemplo de nombre de archivo en R2
    "~/.claude",                          # ruta del USUARIO que conecta su cliente MCP
    "201_otra",                           # fila de ejemplo de la tabla de placeholders
    "example.com",
    "munitest.com",
]

# --------------------------------------------------------------------------
# Reglas. Cada una: (id, regex, que significa, como se corrige)
# --------------------------------------------------------------------------
RULES = [
    (
        "secreto:conexion",
        re.compile(r"(postgres(?:ql)?|mysql|mongodb|redis)://[^\s:@/]+:[^\s:@/]{6,}@", re.I),
        "cadena de conexion con contrasena en claro",
        "usa una variable de entorno; en los ejemplos escribi PASSWORD o <tu-password>",
    ),
    (
        "secreto:token-proveedor",
        re.compile(r"\b(sk-[A-Za-z0-9]{20,}|sk-or-v1-[A-Za-z0-9]|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9])"),
        "token de un proveedor (OpenAI/AWS/GitHub/Slack)",
        "nunca va en la doc: reemplazalo por <TU_TOKEN>",
    ),
    (
        "interno:registro-distribucion",
        re.compile(r"ghcr\.io/gdi-live|\bGDI-LIVE/", re.I),
        "direccion del registro privado de distribucion OnPremise o de un repo privado (GDI-LIVE)",
        "no se publica: el municipio la recibe en el mail de entrega. Usa <IMAGEN_INSTALADOR>",
    ),
    (
        "secreto:clave-privada",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
        "clave privada embebida",
        "sacala del repo y rotala",
    ),
    (
        "secreto:hash-o-key",
        re.compile(r"\b[0-9a-f]{32,64}\b"),
        "cadena hexadecimal larga (puede ser un hash de API key o un secret)",
        "si es un ejemplo usa <YOUR_API_KEY_HASH>; si es real, rotalo",
    ),
    (
        "infra:app-de-cliente",
        re.compile(r"\b(aries|arg|demo)-(backend|gateway|frontend|postgres|agentelang|backoffice-back|backoffice-front|notary|pdfcomposer|pgbouncer)\b", re.I),
        "nombre real de una aplicacion desplegada",
        "usa hml-* / prd-* o <tu-app>",
    ),
    (
        "infra:org-fly",
        re.compile(r"(org:\s*|-o\s+)(gdilatam|gdi-dev)\b", re.I),
        "nombre real de la organizacion de Fly.io",
        "usa <your-fly-org> / <your-fly-org-dev>",
    ),
    (
        "infra:toml-de-cliente",
        re.compile(r"\bfly\.(arg|aries|demo)(\.\w+)?\.toml\b", re.I),
        "archivo de despliegue especifico de un cliente",
        "usa fly.hml.toml / fly.prd.toml",
    ),
    (
        "infra:subdominio-instalacion",
        re.compile(r"\b(arg|aries|demo|enlace|r2|panel|auth|public|arg-gateway|aries-gateway|demo-gateway|arg-admin)\.gdilatam\.com\b", re.I),
        "subdominio de una instalacion real",
        "usa un dominio generico (cliente.your-domain.com)",
    ),
    (
        "cliente:schema",
        re.compile(r"\b[12]\d{2}_(?!test\b|mt\b|muni\b|demo\b|ejemplo\b|example\b|abcd\b|xxxx\b)[a-z]{4}(_audit)?\b"),
        "identificador de un schema de un municipio real",
        "usa 100_test, 101_ejemplo o 200_ejemplo",
    ),
    (
        "cliente:bucket",
        re.compile(r"\b(gdi|tenant)-(?!ejemplo|test|muni|municipio|public-pdf|tu-|your-)[a-z]{3,}-(oficial|tosign|publico|edicion)\b", re.I),
        "bucket de almacenamiento de un municipio real",
        "usa gdi-ejemplo-oficial / gdi-ejemplo-tosign",
    ),
    (
        "pii:email-personal",
        re.compile(r"[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo|live|proton(mail)?)\.[a-z]{2,}", re.I),
        "direccion de correo personal",
        "usa admin@example.com",
    ),
    (
        "pii:email-interno",
        re.compile(r"[A-Za-z0-9._%+-]+@gdilatam\.com", re.I),
        "correo interno del equipo",
        "usa @example.com (soporte@ e info@ estan permitidos)",
    ),
    (
        "pii:nombre-propio",
        re.compile(r"\b(aranguren|castorpolux|castor\s+polux)\b", re.I),
        "nombre de una persona real",
        "usa un nombre ficticio (Juan Perez)",
    ),
    (
        "interno:ruta-privada",
        re.compile(r"\b(OnTheWayProjects|GDI-ClaudeConfig|GDI-LIVE)\b|(^|[\s`(/])\.claude/"),
        "referencia a un repositorio o carpeta interna",
        "sacala: no existe para quien lee la doc publica",
    ),
    (
        "doc:bypass-inexistente",
        re.compile(r"se\s+(salta|saltea)\s+la\s+validacion\s+de\s+permisos|sin\s+filtrar\s+por\s+permisos", re.I),
        "la doc describe un bypass de permisos (aunque el codigo no lo tenga, invita a probarlo)",
        "documenta el comportamiento real: sin X-User-ID la API responde 401",
    ),
]

SKIP_DIRS = {".git", "site", "node_modules", "__pycache__", ".github"}
EXTS = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".yml", ".yaml", ".txt", ".js", ".css", ".html", ".json"}

# --------------------------------------------------------------------------
# Que se publica (D-162B, Santiago 12/11/2026): el sitio publico no cuenta como
# operamos por dentro. Lista de lo PERMITIDO dentro de docs/: todo lo demas
# (cualquier extension, cualquier carpeta) bloquea. La referencia tecnica
# interna vive en un repo privado.
# --------------------------------------------------------------------------
DOCS_CARPETAS_PERMITIDAS = (
    "usuarios/", "administradores/", "desarrollo/gateway/",
    "assets/", "stylesheets/", "javascripts/", "descargas/",
)
DOCS_ARCHIVOS_PERMITIDOS = {
    "index.md", "glosario.md", "novedades.md", "llms.txt", "robots.txt", "cname",
    "desarrollo/index.md",
}


def docs_fuera_de_lista(docs_dir="docs"):
    """Archivos de docs/ que no estan en la lista de lo permitido (todas las extensiones)."""
    fuera = []
    for root, dirs, names in os.walk(docs_dir, followlinks=True):
        for name in names:
            rel = os.path.relpath(os.path.join(root, name), docs_dir).replace("\\", "/")
            r = rel.lower()
            if r in DOCS_ARCHIVOS_PERMITIDOS or r.startswith(DOCS_CARPETAS_PERMITIDAS):
                continue
            fuera.append(os.path.join(docs_dir, rel))
    return fuera

# --------------------------------------------------------------------------
# Proveedores: la doc publica NUNCA nombra a los proveedores de infraestructura
# (Santiago, 12/11/2026). Se escribe "proveedor de autenticacion",
# "almacenamiento S3 compatible", "proveedor de modelos LLM", "servidores", etc.
# Esta regla NO usa ALLOW (un "<your-app>.fly.dev" tambien es una mencion).
# Se permiten los identificadores reales del codigo (AUTH0_DOMAIN,
# auth0_user_id, R2_BUCKET, @auth0/nextjs-auth0): se borran antes de buscar.
# --------------------------------------------------------------------------
PROVEEDOR_RX = re.compile(
    r"fly\.io|fly\.dev|\.flycast|\bflyctl\b|\bfly\b|\boracle\b|\bOCI\b|\bvercel\b|cloudflare"
    r"|\bauth0\b|openrouter|\bresend\b|backblaze|hetzner|keycloak|upstash|supabase|r2\.dev"
    r"|\bR2\b|\bB2\b",
    re.I,
)
# Las URLs se revisan enteras, antes de borrar identificadores
# (https://x.fly.dev/main.js no es un "archivo de codigo").
URL_RX = re.compile(r"[A-Za-z][\w+.-]*://[^\s`'\"<>)]+")
PLACEHOLDER_RX = re.compile(r"\{[^}]*\}")  # https://{AUTH0_DOMAIN}/... es una variable
PROVEEDOR_IDENTIFICADOR = re.compile(
    r"\b[A-Za-z0-9]\w*_\w*"   # variables, columnas: AUTH0_DOMAIN, AUTH0_M2M_*, auth0_user_id (no _enfasis_)
    r"|@auth0/[\w-]+"         # paquete npm
    r"|\bresend-\w[\w-]*"     # rutas de API: /resend-activation
    r"|[\w./-]+\.(?:py|ts|tsx|js)\b"  # archivos de codigo: cloudflare.py, src/lib/auth0.ts
    r"|\b(?:Auth0|Cloudflare)[A-Z]\w*"  # clases: Auth0Client, CloudflareR2Client
    r"|^\s*(?:from|import)\s+[\w.]+"   # imports de Python al inicio: from services.storage.cloudflare
    r"|\b(?:const|let|var)\s+\w+"      # variables de JS: const auth0 = ...
)
# Palabras que en una pagina puntual NO son un proveedor, con su motivo.
PROVEEDOR_PERMITIDO_POR_ARCHIVO = {
    # R1/R2/R3/R4 son las reglas de acceso a reservados, no el almacenamiento.
    "docs/administradores/reservados.md": {"R2"},
}
# Paginas que SI nombran proveedores, con su motivo.
PROVEEDOR_EXCEPCIONES = {
    # Manual de instalacion OnPremise: el tecnico del municipio crea las cuentas
    # clic por clic en cada proveedor (Santiago, 12/11/2026).
    "docs/administradores/onpremise/manual.md",
}


def menciona_proveedor(line, permitidas=()):
    urls = PLACEHOLDER_RX.sub(" ", " ".join(URL_RX.findall(line)))
    limpia = urls + " " + PROVEEDOR_IDENTIFICADOR.sub(" ", URL_RX.sub(" ", line))
    limpia = limpia.replace("_", " ")  # __Auth0__ (enfasis de markdown)
    for m in PROVEEDOR_RX.finditer(limpia):
        token = m.group(0)
        # R2 / B2 solo en mayuscula (r2 suelto aparece en hashes y nombres)
        if token.lower() in ("r2", "b2", "oci") and token != token.upper():
            continue
        if token in permitidas:
            continue
        return token
    return None


def should_skip(line):
    return any(a in line for a in ALLOW)


def scan_file(path):
    hits = []
    rel = os.path.relpath(path).replace("\\", "/")
    revisar_proveedor = rel not in PROVEEDOR_EXCEPCIONES
    permitidas = PROVEEDOR_PERMITIDO_POR_ARCHIVO.get(rel, set())
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if revisar_proveedor:
                    token = menciona_proveedor(line, permitidas)
                    if token:
                        hits.append((path, n, "infra:proveedor", token,
                                     "nombre de un proveedor de infraestructura (la doc publica nunca los nombra)",
                                     "usa el generico: proveedor de autenticacion, almacenamiento S3 compatible, "
                                     "proveedor de modelos LLM, proveedor de correo, servidores, hosting de frontends"))
                        continue
                if should_skip(line):
                    continue
                for rid, rx, what, fix in RULES:
                    m = rx.search(line)
                    if m:
                        hits.append((path, n, rid, m.group(0)[:60], what, fix))
                        break
    except OSError as e:
        print("  no se pudo leer %s: %s" % (path, e))
    return hits


def collect(targets):
    files = []
    for t in targets:
        if os.path.isfile(t):
            files.append(t)
            continue
        for root, dirs, names in os.walk(t):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in names:
                if os.path.splitext(name)[1].lower() in EXTS:
                    files.append(os.path.join(root, name))
    return sorted(files)


def main():
    targets = sys.argv[1:] or ["docs", "skills", "mkdocs.yml", "README.md"]
    targets = [t for t in targets if os.path.exists(t)]
    files = collect(targets)

    hits = []
    for f in files:
        hits.extend(scan_file(f))
    if os.path.isdir("docs"):
        for f in docs_fuera_de_lista("docs"):
            hits.append((f, 1, "interno:fuera-de-lista", f.replace("\\", "/"),
                         "archivo en docs/ fuera de lo que se publica (referencia tecnica interna, deploy, etc.)",
                         "lo interno va al repo privado de referencia tecnica; si es publico, "
                         "sumalo a DOCS_CARPETAS_PERMITIDAS con su motivo"))

    print("Guarda de publicacion: %d archivos revisados." % len(files))
    if not hits:
        print("OK: no se encontro nada que no deba publicarse.")
        return 0

    print("")
    print("=" * 78)
    print("BLOQUEADO: %d hallazgo(s). Este repo se publica en docs.gdilatam.com," % len(hits))
    print("asi que esto saldria a internet en cuanto se mergee a prd.")
    print("=" * 78)
    by_rule = {}
    for h in hits:
        by_rule.setdefault(h[2], []).append(h)
    for rid, group in sorted(by_rule.items()):
        print("")
        print("[%s] %s" % (rid, group[0][4]))
        print("   como se corrige: %s" % group[0][5])
        for path, n, _, match, _, _ in group[:12]:
            print("   %s:%d  ->  %s" % (path.replace("\\", "/"), n, match))
        if len(group) > 12:
            print("   ... y %d mas" % (len(group) - 12))
    print("")
    print("Si alguno es un falso positivo, agregalo a ALLOW en este script")
    print("(con su motivo) en vez de apagar la regla.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
