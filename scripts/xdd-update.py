#!/usr/bin/env python3
"""xdd-update.py — Actualiza los artefactos editables del proyecto X-DD (S20, ADR-0048).

Non-destructivo: aplica 3-way merge o hace backup antes de sobreescribir.
El tooling (scripts/, prompts/, .agent/) viene del paquete pip instalado.

Comandos:
  check        — muestra qué plantillas difieren de la versión instalada
  apply        — actualiza artefactos editables (backup automático, --no-backup para desactivar)
  apply --dry-run — muestra qué haría sin cambiar nada
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version, utcnow_iso  # noqa: E402

__version__ = read_version()

ROOT = Path(__file__).resolve().parent.parent

# Artefactos EDITABLES que xdd-update puede actualizar (templates → proyecto)
EDITABLES = [
    ("templates/memoria.template.md",   "memoria.md"),
    ("templates/lecciones.template.md", "lecciones.md"),
    ("templates/xdd.profile.template.yml", "xdd.profile.yml"),
]


def _pip_version() -> str | None:
    try:
        from importlib.metadata import version
        return version("x-dd")
    except Exception:
        return None


def cmd_check(args):
    installed = _pip_version()
    print(f"[update] x-dd instalado: {installed or 'no pip-install detectado'}")
    print(f"[update] XDD_ROOT: {ROOT}")
    print(f"[update] Proyecto: {Path.cwd()}")
    print()
    up_to_date = []
    outdated = []
    missing = []

    for tmpl_rel, proj_file in EDITABLES:
        tmpl = ROOT / tmpl_rel
        target = Path(proj_file)
        if not tmpl.exists():
            continue
        if not target.exists():
            missing.append(proj_file)
        elif target.read_text(encoding="utf-8") != tmpl.read_text(encoding="utf-8"):
            outdated.append(proj_file)
        else:
            up_to_date.append(proj_file)

    for f in up_to_date:
        print(f"  ✓ {f} (sin cambios)")
    for f in outdated:
        print(f"  ↑ {f} (template actualizado — `xdd update apply` para sincronizar)")
    for f in missing:
        print(f"  + {f} (no existe — se crearía con `xdd update apply`)")
    return 0 if not outdated and not missing else 1


def cmd_apply(args):
    dry = args.dry_run
    backup = not getattr(args, "no_backup", False)
    ts = utcnow_iso()[:19].replace(":", "-").replace("T", "_")

    changed = []
    for tmpl_rel, proj_file in EDITABLES:
        tmpl = ROOT / tmpl_rel
        target = Path(proj_file)
        if not tmpl.exists():
            continue
        tmpl_content = tmpl.read_text(encoding="utf-8")
        if target.exists():
            if target.read_text(encoding="utf-8") == tmpl_content:
                continue  # sin cambio
            if backup and not dry:
                bak = Path(f"{proj_file}.bak-{ts}")
                shutil.copy2(target, bak)
                print(f"[update] backup: {bak}")
        if dry:
            print(f"[update] (dry-run) actualizaría: {proj_file}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(tmpl_content, encoding="utf-8")
            print(f"[update] ✓ {proj_file}")
            changed.append(proj_file)

    if not changed and not dry:
        print("[update] todo al día — sin cambios.")
    elif dry and changed:
        print(f"[update] (dry-run) {len(changed)} archivo(s) se actualizarían.")
    return 0


def build_parser():
    p, sub = make_parser("xdd-update", __doc__, raw_description=True)

    sub.add_parser("check", help="Muestra diferencias entre templates y proyecto").set_defaults(func=cmd_check)

    p_a = sub.add_parser("apply", help="Actualiza artefactos editables")
    p_a.add_argument("--dry-run", action="store_true", help="No escribe nada")
    p_a.add_argument("--no-backup", action="store_true", help="No hace backup previo")
    p_a.set_defaults(func=cmd_apply)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
