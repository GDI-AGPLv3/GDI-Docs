#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la referencia de endpoints de la skill del BackOffice desde el OpenAPI.

La skill `gdi-backoffice-admin` le da a la IA del administrador el catalogo
completo de la API del BackOffice. Escribirlo a mano se desactualiza en semanas;
por eso sale del OpenAPI del BackOffice-Back.

En PRD el OpenAPI esta apagado: se toma de DEV (o de una instancia local).

Uso:
    curl -s <url-backoffice-dev>/openapi.json -o openapi-backoffice.json
    python scripts/build_backoffice_endpoints.py openapi-backoffice.json

Escribe: skills/gdi-backoffice-admin/reference/endpoints.md
"""
import json
import os
import re
import sys
import textwrap

OUT = os.path.join("skills", "gdi-backoffice-admin", "reference", "endpoints.md")

# Lo que la skill NO expone.
#   - Onboarding / System: exigen login con JWT (no andan con API Key).
#   - Super Admin: es de GDI, no del municipio.
#   - MCP Server: es otra interfaz (solo lectura), no REST.
#   - Aprobar/rechazar propuestas de catalogo: escribe en el catalogo GLOBAL,
#     compartido por todos los municipios. No es tarea de un admin de municipio.
EXCLUDED_TAGS = {"Onboarding", "Super Admin", "MCP Server", "System"}
EXCLUDED_OPS = {
    ("POST", "/admin/catalog/proposals/{proposal_id}/approve"),
    ("POST", "/admin/catalog/proposals/{proposal_id}/reject"),
}

# Orden y titulo en castellano de cada grupo.
TAGS = [
    ("Admin - Users", "Usuarios"),
    ("Admin - Departments", "Reparticiones (departments)"),
    ("Admin - Sectors", "Sectores"),
    ("Admin - Ranks", "Rangos jerárquicos"),
    ("Admin - City Seals", "Sellos del municipio"),
    ("Admin - Document Types", "Tipos de documento"),
    ("Admin - Case Templates", "Tipos de expediente (case templates)"),
    ("Admin - Registry Families", "Familias de legajos"),
    ("Settings", "Configuración del municipio"),
    ("Admin - Citizens", "Ciudadanos (Base TAD)"),
    ("Admin - API Keys", "API Keys"),
    ("Admin - Certificates", "Certificados de firma"),
    ("Admin - Stats", "Estadísticas"),
    ("Admin - Audit", "Auditoría"),
    ("Admin - Organigrama", "Organigrama"),
    ("Admin - Catalog Proposals", "Propuestas al catálogo global"),
]

# Operaciones que borran o cortan acceso: la skill exige confirmacion explicita.
DESTRUCTIVE_HINTS = ("DELETE",)
DESTRUCTIVE_PATH_HINTS = ("/deactivate", "/archive", "/admin-role", "/email", "/auth-method")


def resolve(spec, schema):
    if not isinstance(schema, dict):
        return {}
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        return resolve(spec, spec["components"]["schemas"][name])
    if "allOf" in schema and len(schema["allOf"]) == 1:
        return resolve(spec, schema["allOf"][0])
    return schema


def type_of(spec, schema):
    schema = schema or {}
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "anyOf" in schema:
        parts = [type_of(spec, s) for s in schema["anyOf"] if s.get("type") != "null"]
        return " \\| ".join(parts) or "null"
    if "enum" in schema:
        return " \\| ".join("`%s`" % v for v in schema["enum"])
    if "const" in schema:
        return "`%s`" % schema["const"]
    t = schema.get("type", "")
    if t == "array":
        return "lista de %s" % type_of(spec, schema.get("items", {}))
    fmt = schema.get("format")
    return "%s (%s)" % (t, fmt) if fmt else (t or "objeto")


# Referencias internas (tickets, decisiones) que no le sirven al lector.
INTERNAL = re.compile(
    r"\(?\bGDI-\d+(?: F\d+)?\)?:?\s*|Regla decidida por [^:]+:\s*|Optimizacion S\d+-\d+:?\s*"
    r"|\s*\(Fernet \+ CERT_MASTER_KEY\)"
)
# Casillas internas del equipo: la guarda de publicacion no las deja pasar.
TEAM_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@gdilatam\.com")
# Texto repetido en casi todos los endpoints: ya lo dice el encabezado.
BOILERPLATE = re.compile(
    r"\*\*Endpoint exclusivo para Administradores del BackOffice\.\*\*\s*"
    r"|\*\*Requiere:\*\*\s*- Rol de Administrador\s*"
)


def clean(text):
    text = TEAM_EMAIL.sub("el equipo de GDI", INTERNAL.sub("", text or ""))
    return " ".join(text.split()).replace("|", "\\|")


def clean_block(text):
    """Descripcion larga del endpoint: conserva el markdown (listas, negritas)."""
    text = (text or "").strip("\n")
    if not text.strip():
        return ""
    # FastAPI deja la 1a linea sin sangria y el resto con la del docstring.
    first, _, rest = text.partition("\n")
    text = first.strip() + ("\n" + textwrap.dedent(rest) if rest else "")
    text = TEAM_EMAIL.sub("el equipo de GDI", BOILERPLATE.sub("", INTERNAL.sub("", text)))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def is_destructive(method, path):
    return method in DESTRUCTIVE_HINTS or any(path.endswith(h) for h in DESTRUCTIVE_PATH_HINTS)


def render_fields(spec, schema, lines):
    schema = resolve(spec, schema)
    props = schema.get("properties") or {}
    if not props:
        return False
    required = set(schema.get("required") or [])
    lines.append("| Campo | Tipo | Oblig. | Descripción |")
    lines.append("|---|---|---|---|")
    for name, prop in props.items():
        desc = clean(prop.get("description") or resolve(spec, prop).get("description"))
        if "default" in prop and prop["default"] is not None:
            desc = (desc + " " if desc else "") + "Default: `%s`." % json.dumps(prop["default"], ensure_ascii=False)
        lines.append("| `%s` | %s | %s | %s |" % (name, type_of(spec, prop), "sí" if name in required else "", desc))
    return True


def render_op(spec, method, path, op, lines):
    summary = clean(op.get("summary", "")).replace("[ADMIN] ", "")
    flag = " ⚠️ requiere confirmación" if is_destructive(method, path) else ""
    lines.append("### `%s %s`%s" % (method, path, flag))
    lines.append("")
    lines.append(summary)
    lines.append("")
    desc = clean_block(op.get("description"))
    if desc and clean(desc) != summary:
        lines.append(desc)
        lines.append("")

    params = [p for p in op.get("parameters", []) if p.get("in") in ("path", "query")]
    if params:
        lines.append("| Parámetro | Dónde | Tipo | Oblig. | Descripción |")
        lines.append("|---|---|---|---|---|")
        for p in params:
            lines.append("| `%s` | %s | %s | %s | %s |" % (
                p["name"], p["in"], type_of(spec, p.get("schema", {})),
                "sí" if p.get("required") else "", clean(p.get("description"))))
        lines.append("")

    body = op.get("requestBody", {}).get("content", {})
    if "application/json" in body:
        lines.append("Body JSON:")
        lines.append("")
        if not render_fields(spec, body["application/json"].get("schema"), lines):
            lines.append("_(objeto libre)_")
        lines.append("")
    elif "multipart/form-data" in body:
        lines.append("Body `multipart/form-data` (subida de archivo):")
        lines.append("")
        render_fields(spec, body["multipart/form-data"].get("schema"), lines)
        lines.append("")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))

    groups = {tag: [] for tag, _ in TAGS}
    unknown = []
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            method = method.upper()
            tag = (op.get("tags") or ["-"])[0]
            if tag in EXCLUDED_TAGS or (method, path) in EXCLUDED_OPS:
                continue
            if tag not in groups:
                unknown.append("%s %s (%s)" % (method, path, tag))
                continue
            groups[tag].append((method, path, op))
    if unknown:
        sys.exit("Tags sin titulo en TAGS (agregalos o excluilos):\n  " + "\n  ".join(unknown))

    total = sum(len(v) for v in groups.values())
    lines = [
        "# Referencia de endpoints — API del BackOffice GDI",
        "",
        "> Generado desde el OpenAPI del BackOffice con `scripts/build_backoffice_endpoints.py`.",
        "> No editar a mano: regenerar.",
        "",
        "Todos los endpoints llevan los 3 headers de autenticación (`X-API-Key`, `X-Tenant-Schema`,",
        "`X-User-ID`) y exigen que el usuario tenga rol **Administrador**. Las rutas son relativas",
        "a `$GDI_BO_URL`. Los marcados con ⚠️ borran datos o cortan accesos: se confirman con el",
        "administrador antes de ejecutarlos.",
        "",
        "%d endpoints." % total,
        "",
        "## Índice",
        "",
    ]
    for tag, title in TAGS:
        if groups[tag]:
            lines.append("- %s (%d)" % (title, len(groups[tag])))
    lines.append("")
    for tag, title in TAGS:
        if not groups[tag]:
            continue
        lines.append("## %s" % title)
        lines.append("")
        for method, path, op in groups[tag]:
            render_op(spec, method, path, op, lines)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    print("OK: %d endpoints -> %s" % (total, OUT))


if __name__ == "__main__":
    main()
