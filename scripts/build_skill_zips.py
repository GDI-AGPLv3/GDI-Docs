#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Empaqueta cada skill de `skills/` en un ZIP y en una referencia .txt descargables.

Fuente unica: `skills/<nombre>/` (SKILL.md + archivos de apoyo). El ZIP se genera
en el deploy y NO se versiona, asi nunca queda uno viejo publicado.

Formato: el ZIP contiene la carpeta `<nombre>/` con el SKILL.md adentro, que es
lo que pide claude.ai para subir una skill y lo que Claude Code espera en
`~/.claude/skills/`.

Uso:
    python scripts/build_skill_zips.py

Ademas arma `<nombre>-referencia.txt`: el SKILL.md y sus archivos de apoyo en
un solo texto plano. Es lo que baja el agente cuando el administrador le pega el
prompt de arranque (`docs/descargas/<nombre>-prompt.txt`): con un archivo y una
URL alcanza, no hace falta instalar la skill. Se genera en el deploy por lo
mismo que el ZIP: asi nunca queda una referencia vieja publicada.

Escribe: docs/descargas/<nombre>.zip y docs/descargas/<nombre>-referencia.txt
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
    build_referencia(name, base, files)


def build_referencia(name, base, files):
    """Todo el contenido de la skill en un .txt: SKILL.md primero, despues el resto."""
    skill = os.path.join(base, "SKILL.md")
    resto = [f for f in files if f != skill]
    partes = [
        "REFERENCIA COMPLETA: %s\n"
        "Fuente: https://docs.gdilatam.com (se regenera en cada publicacion).\n"
        "Contiene las instrucciones (SKILL.md) y, a continuacion, sus archivos de apoyo.\n"
        "Donde las instrucciones remiten a otro archivo (por ejemplo reference/endpoints.md),\n"
        "ese archivo esta MAS ABAJO en este mismo texto." % name
    ]
    for path in [skill] + resto:
        with open(path, encoding="utf-8") as f:
            texto = f.read().strip()
        rel = os.path.relpath(path, base).replace(os.sep, "/")
        partes.append("=" * 78 + "\nARCHIVO: %s\n" % rel + "=" * 78 + "\n\n" + texto)
    target = os.path.join(OUT, name + "-referencia.txt")
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n".join(partes) + "\n")
    print("OK: %s (%d archivos)" % (target, 1 + len(resto)))


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
    if not names:
        sys.exit("No hay skills en %s/" % SRC)
    for name in names:
        build(name)


if __name__ == "__main__":
    main()
