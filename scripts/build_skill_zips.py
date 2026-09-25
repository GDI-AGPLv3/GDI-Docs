#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma las descargas de cada skill de `skills/`: ZIP, prompt y referencia.

Fuente unica: `skills/<nombre>/` (SKILL.md + archivos de apoyo). Todo se genera
en el deploy y NO se versiona, asi nunca queda una descarga vieja publicada.

Escribe en docs/descargas/:
- `<nombre>.zip`: la carpeta `<nombre>/` con el SKILL.md adentro, que es lo que
  pide claude.ai para subir una skill y lo que Claude Code espera en
  `~/.claude/skills/`.
- `<nombre>-prompt.txt`: la MISMA skill (el SKILL.md sin su cabecera) con los
  datos de conexion arriba, para pegarla en una conversacion sin instalar nada.
  El prompt ES la skill: no hay un texto aparte que se pueda desfasar.
- `<nombre>-referencia.txt`: los archivos de apoyo (la referencia de endpoints)
  en texto plano. El paso 0 del SKILL.md le pide al agente bajarla de aca, asi
  trabaja siempre con la version vigente.

Uso:
    python scripts/build_skill_zips.py
"""
import os
import sys
import zipfile

SRC = "skills"
OUT = os.path.join("docs", "descargas")
# Fecha fija: el mismo contenido produce el mismo ZIP byte a byte.
FIXED_DATE = (2026, 1, 1, 0, 0, 0)

CABECERA_PROMPT = """\
Esta es la skill "{name}" de GDI. Seguí estas instrucciones durante toda la conversación.

DATOS DE CONEXIÓN (completar antes de pegar)
- GDI_BO_URL (URL de la API): <completar>
- GDI_BO_SCHEMA (identificador del municipio): <completar>
- GDI_BO_USER_ID (mi usuario, UUID): <completar>
- GDI_BO_API_KEY: la tenés en la variable de entorno GDI_BO_API_KEY o te la paso aparte. Nunca la muestres ni la escribas en archivos.

Empezá por el paso 0 (bajar la referencia de endpoints), después probá la conexión y esperá mi pedido.
"""


def build(name):
    base = os.path.join(SRC, name)
    skill = os.path.join(base, "SKILL.md")
    if not os.path.isfile(skill):
        sys.exit("%s no tiene SKILL.md" % base)
    files = []
    for root, dirs, names in os.walk(base):
        dirs.sort()
        for n in sorted(names):
            files.append(os.path.join(root, n))
    build_zip(name, files)
    build_prompt(name, skill)
    build_referencia(name, base, [f for f in files if f != skill])


def build_zip(name, files):
    target = os.path.join(OUT, name + ".zip")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files:
            arc = os.path.relpath(path, SRC).replace(os.sep, "/")
            info = zipfile.ZipInfo(arc, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as f:
                z.writestr(info, f.read())
    print("OK: %s (%d archivos)" % (target, len(files)))


def _sin_cabecera(texto):
    """Saca el bloque `---` del principio: es metadata de la skill, no instrucciones."""
    if texto.startswith("---"):
        fin = texto.find("\n---", 3)
        if fin != -1:
            return texto[fin + 4:].lstrip("\n")
    return texto


def _escribir(target, texto):
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def build_prompt(name, skill):
    with open(skill, encoding="utf-8") as f:
        cuerpo = _sin_cabecera(f.read()).strip()
    target = os.path.join(OUT, name + "-prompt.txt")
    _escribir(target, CABECERA_PROMPT.format(name=name) + "\n" + "=" * 78 + "\n\n" + cuerpo + "\n")
    print("OK: %s" % target)


def build_referencia(name, base, apoyo):
    if not apoyo:
        return
    partes = [
        "REFERENCIA DE ENDPOINTS: %s\n"
        "Fuente: https://docs.gdilatam.com (se regenera en cada publicacion).\n"
        "Es la lista completa y vigente de endpoints de la API: si un endpoint o un campo\n"
        "no esta aca, no existe." % name
    ]
    for path in apoyo:
        with open(path, encoding="utf-8") as f:
            texto = f.read().strip()
        rel = os.path.relpath(path, base).replace(os.sep, "/")
        partes.append("=" * 78 + "\nARCHIVO: %s\n" % rel + "=" * 78 + "\n\n" + texto)
    target = os.path.join(OUT, name + "-referencia.txt")
    _escribir(target, "\n\n".join(partes) + "\n")
    print("OK: %s (%d archivos)" % (target, len(apoyo)))


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
    if not names:
        sys.exit("No hay skills en %s/" % SRC)
    for name in names:
        build(name)


if __name__ == "__main__":
    main()
