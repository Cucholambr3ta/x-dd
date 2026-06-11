#!/usr/bin/env python3
"""xdd-migrate.py — Migra un proyecto X-DD de v0.1 (copia congelada) a v0.2 (pip).

Detecta automáticamente si el proyecto es v0.1 (copia congelada de scripts/) o
ya v0.2 (tooling desde pip, solo editables en el proyecto). Si v0.1, hace backup
completo y migra al modelo v0.2.

Comandos:
  status       — detecta la versión del proyecto y reporta el estado
  run          — ejecuta la migración v0.1→v0.2 (con backup automático)
  run --dry-run — muestra qué haría sin cambiar nada
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version, utcnow_iso  # noqa: E402

__version__ = read_version()

# Archivos/dirs que indican "copia congelada v0.1" en el proyecto destino
V1_SIGNALS = [
    "scripts/xdd-gate.py",
    "scripts/xdd-init.sh",
    "prompts/agents/",
    ".agent/workflows/",
]

# Editables que se preservan en la migración
EDITABLES = [
    "memoria.md", "lecciones.md", "xdd.profile.yml", "xdd.config.yml",
    "CLAUDE.md", "AGENTS.md",
    ".xdd/",
]

# Directorios copiados en v0.1 que en v0.2 vienen de pip
TOOLING_DIRS = [
    "scripts/", "prompts/", ".agent/", "templates/", "manifests/",
    "schemas/", "skills/", "evals/",
]


def _is_v1_project(dest: Path) -> bool:
    return any((dest / s).exists() for s in V1_SIGNALS)


def cmd_status(args):
    dest = Path(args.dest) if args.dest else Path.cwd()
    v1 = _is_v1_project(dest)
    pip_v = None
    try:
        from importlib.metadata import version
        pip_v = version("x-dd")
    except Exception:
        pass

    print(f"[migrate] Proyecto: {dest}")
    print(f"[migrate] x-dd pip instalado: {pip_v or 'no'}")
    if v1:
        print(f"[migrate] Estado: v0.1 (copia congelada — tooling copiado localmente)")
        print(f"[migrate]   → Ejecutar `xdd migrate run` para migrar a v0.2 (pip)")
    else:
        print(f"[migrate] Estado: v0.2+ (tooling desde pip) o proyecto nuevo")
    return 0 if not v1 else 1


def cmd_run(args):
    dry = args.dry_run
    dest = Path(args.dest) if args.dest else Path.cwd()

    if not _is_v1_project(dest):
        print(f"[migrate] No es un proyecto v0.1 — sin migración necesaria.")
        return 0

    pip_v = None
    try:
        from importlib.metadata import version
        pip_v = version("x-dd")
    except Exception:
        pass

    if not pip_v:
        print("[migrate] ERROR: instala x-dd vía pip antes de migrar.", file=sys.stderr)
        print("[migrate]   pip install x-dd", file=sys.stderr)
        return 2

    ts = utcnow_iso()[:19].replace(":", "-").replace("T", "_")
    backup_dir = dest / f".xdd-backup-pre-migrate-{ts}"

    if not dry:
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"[migrate] Backup en: {backup_dir}")

    # Backup editables
    preserved = []
    for editable in EDITABLES:
        src = dest / editable
        if not src.exists():
            continue
        if not dry:
            bak = backup_dir / editable
            bak.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(str(src), str(bak), dirs_exist_ok=True)
            else:
                shutil.copy2(src, bak)
        preserved.append(editable)

    # Remove tooling dirs (now come from pip)
    removed = []
    for tooling in TOOLING_DIRS:
        td = dest / tooling.rstrip("/")
        if td.exists():
            if dry:
                print(f"[migrate] (dry-run) eliminaría tooling: {tooling}")
            else:
                shutil.rmtree(str(td), ignore_errors=True)
                print(f"[migrate] eliminado (tooling ahora en pip): {tooling}")
            removed.append(tooling)

    # Restore editables from backup
    if not dry:
        for editable in preserved:
            bak = backup_dir / editable
            target = dest / editable
            if bak.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if bak.is_dir():
                    shutil.copytree(str(bak), str(target), dirs_exist_ok=True)
                else:
                    shutil.copy2(bak, target)

    if dry:
        print(f"\n[migrate] (dry-run) preservaría {len(preserved)} editables, "
              f"eliminaría {len(removed)} dirs de tooling.")
    else:
        print(f"\n[migrate] ✓ Migración completada.")
        print(f"  Backup: {backup_dir}")
        print(f"  Editables preservados: {preserved}")
        print(f"  Tooling eliminado (ahora desde pip): {removed}")
        print(f"\n  Siguiente paso: `xdd init --pip-mode {dest}` para regenerar config")
    return 0


def build_parser():
    p, sub = make_parser("xdd-migrate", __doc__, raw_description=True)

    p_s = sub.add_parser("status", help="Detecta versión del proyecto")
    p_s.add_argument("--dest", help="Ruta del proyecto (default: CWD)")
    p_s.set_defaults(func=cmd_status)

    p_r = sub.add_parser("run", help="Ejecuta migración v0.1→v0.2")
    p_r.add_argument("--dest", help="Ruta del proyecto (default: CWD)")
    p_r.add_argument("--dry-run", action="store_true")
    p_r.set_defaults(func=cmd_run)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
