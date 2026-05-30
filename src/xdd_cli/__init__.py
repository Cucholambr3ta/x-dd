"""xdd_cli — entry-points pip para los scripts X-DD existentes.

NO reescribe los scripts (respeta ADR-0008: consolidación a Click diferida).
Cada entry-point es un dispatcher fino que ejecuta el script `scripts/xdd-*.py`
correspondiente vía runpy, preservando argv. Empaqueta lo que ya existe.

Resolución de `scripts/`:
  1. XDD_SCRIPTS_DIR si está seteada.
  2. instalación editable: scripts/ junto al repo (../../scripts desde src/xdd_cli).
  3. data del wheel: scripts/ empaquetado dentro del paquete.
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

__version__ = "0.1.0-dev"


def _scripts_dir() -> Path:
    env = os.environ.get("XDD_SCRIPTS_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    # editable: repo_root/src/xdd_cli → repo_root/scripts
    repo_scripts = here.parent.parent / "scripts"
    if repo_scripts.is_dir():
        return repo_scripts
    # wheel: scripts empaquetado como data dentro del paquete
    bundled = here / "scripts"
    if bundled.is_dir():
        return bundled
    raise FileNotFoundError(
        "No encuentro scripts/ X-DD. Setea XDD_SCRIPTS_DIR al directorio scripts/."
    )


def _run(script_name: str) -> int:
    """Ejecuta scripts/<script_name> con el argv actual (sin el nombre del wrapper)."""
    script = _scripts_dir() / script_name
    if not script.exists():
        print(f"[xdd] script no encontrado: {script}", file=sys.stderr)
        return 2
    # runpy ejecuta el script como __main__; argv ya tiene los args tras el prog name
    sys.argv = [str(script)] + sys.argv[1:]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else (0 if e.code is None else 1)
    return 0


def gate() -> int:
    return _run("xdd-gate.py")


def eval_() -> int:
    return _run("xdd-eval.py")


def flow() -> int:
    return _run("xdd-flow.py")


def provider() -> int:
    return _run("xdd-provider.py")


def shield() -> int:
    return _run("xdd-shield.py")


def orchestrate() -> int:
    return _run("xdd-orchestrate.py")
