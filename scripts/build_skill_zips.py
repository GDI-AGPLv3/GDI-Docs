#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta cada skill de `skills/` en un ZIP descargable desde el sitio.

Fuente unica: `skills/<nombre>/` (SKILL.md + archivos de apoyo). El ZIP se genera
en el deploy y NO se versiona, asi nunca queda uno viejo publicado.

Formato: el ZIP contiene la carpeta `<nombre>/` con el SKILL.md adentro, que es
lo que pide claude.ai para subir una skill y lo que Claude Code espera en
`~/.claude/skills/`.

Uso:
    python scripts/build_skill_zips.py

Escribe: docs/descargas/<nombre>.zip
"""
import os
import sys
import zipfile

SRC = "skills"
OUT = os.path.join("docs", "descargas")
# Fecha fija: el mismo contenido produce el mismo ZIP byte a byte.
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def build(name):
    base = os.path.join(SRC, name)
    if not os.path.isfile(os.path.join(base, "SKILL.md")):
        sys.exit("%s no tiene SKILL.md" % base)
    target = os.path.join(OUT, name + ".zip")
    files = []
    for root, dirs, names in os.walk(base):
        dirs.sort()
        for n in sorted(names):
            files.append(os.path.join(root, n))
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files:
            arc = os.path.relpath(path, SRC).replace(os.sep, "/")
            info = zipfile.ZipInfo(arc, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as f:
                z.writestr(info, f.read())
    print("OK: %s (%d archivos)" % (target, len(files)))


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
    if not names:
        sys.exit("No hay skills en %s/" % SRC)
    for name in names:
        build(name)


if __name__ == "__main__":
    main()
