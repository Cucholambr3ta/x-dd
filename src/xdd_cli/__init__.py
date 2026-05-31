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

def _resolve_version() -> str:
    """Versión del paquete instalado; fallback literal si corre desde fuente."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("x-dd")
    except (PackageNotFoundError, ImportError):
        return "0.1.1"


__version__ = _resolve_version()


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


def _run_shell(script_name: str, args: list[str]) -> int:
    """Ejecuta un scripts/*.sh con bash, preservando args."""
    import subprocess

    script = _scripts_dir() / script_name
    if not script.exists():
        print(f"[xdd] script no encontrado: {script}", file=sys.stderr)
        return 2
    return subprocess.call(["bash", str(script), *args])


# Dispatcher unificado `xdd <subcomando>` (entry-point pipx, ADR-0045).
# Mapea subcomando → (tipo, script). NO reescribe: delega a los scripts existentes.
_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "gate": ("py", "xdd-gate.py"),
    "eval": ("py", "xdd-eval.py"),
    "flow": ("py", "xdd-flow.py"),
    "provider": ("py", "xdd-provider.py"),
    "shield": ("py", "xdd-shield.py"),
    "orchestrate": ("py", "xdd-orchestrate.py"),
    "doctor": ("sh", "xdd-doctor.sh"),
    "init": ("sh", "xdd-init.sh"),
    "start": ("sh", "xdd-start.sh"),
    "adapt": ("sh", "xdd-adapt.sh"),
    "global-install": ("sh", "xdd-global-install.sh"),
}


def _usage() -> None:
    print("xdd — orquestador/tooling X-DD (pip). Uso: xdd <subcomando> [args]\n")
    print("Subcomandos:")
    for name in sorted(_SUBCOMMANDS):
        print(f"  {name}")
    print("\nEj: xdd gate status · xdd flow --self-test · xdd doctor")


def main(argv: list[str] | None = None) -> int:
    """Entry-point `xdd`: despacha al script del subcomando."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        _usage()
        return 0
    if argv[0] in ("-v", "--version"):
        print(f"xdd {__version__}")
        return 0
    sub, rest = argv[0], argv[1:]
    if sub not in _SUBCOMMANDS:
        print(f"[xdd] subcomando desconocido: {sub!r}", file=sys.stderr)
        _usage()
        return 2
    kind, script = _SUBCOMMANDS[sub]
    if kind == "sh":
        return _run_shell(script, rest)
    sys.argv = [script, *rest]
    return _run(script)
