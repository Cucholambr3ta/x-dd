"""Tests de consistencia de versión (Branch 7 — VERSION como fuente única)."""
from __future__ import annotations

import glob
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"


def _canonical() -> str:
    assert VERSION_FILE.exists(), "Falta el archivo VERSION (fuente única de versión)"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def test_version_file_exists_and_semverish():
    v = _canonical()
    assert re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", v), f"VERSION inválida: {v!r}"


def test_shell_scripts_read_version_or_match():
    """Los scripts shell deben leer VERSION (con fallback) o coincidir con ella."""
    v = _canonical()
    offenders = []
    for f in glob.glob(str(ROOT / "scripts" / "*.sh")):
        txt = Path(f).read_text(encoding="utf-8")
        # Tomar la línea completa de asignación de XDD_VERSION.
        m = re.search(r'^XDD_VERSION=.*$', txt, re.MULTILINE)
        if not m:
            continue
        line = m.group(0)
        # Aceptable: lee de VERSION (cat ... VERSION) o contiene el valor canónico.
        reads_file = "VERSION" in line and "cat" in line
        fallback_ok = v in line
        if not (reads_file or fallback_ok):
            offenders.append((Path(f).name, line))
    assert not offenders, f"scripts con versión divergente de VERSION={v}: {offenders}"


def test_python_scripts_no_hardcoded_version():
    """Los scripts ya no deben hardcodear __version__: resuelven vía read_version().

    Tras la consolidación (v0.1.1), la versión sale de _xdd_common.read_version().
    Un literal `__version__ = "x.y.z"` reintroducido sería regresión; pero si alguien
    lo agrega y coincide con VERSION, se tolera (no diverge)."""
    v = _canonical()
    offenders = []
    for f in glob.glob(str(ROOT / "scripts" / "*.py")):
        txt = Path(f).read_text(encoding="utf-8")
        for m in re.finditer(r'__version__\s*=\s*"([^"]+)"', txt):
            if m.group(1) != v:
                offenders.append((Path(f).name, m.group(1)))
    assert not offenders, f"__version__ literal divergente de VERSION={v}: {offenders}"


def test_version_fallbacks_match():
    """Los fallbacks literales embebidos deben coincidir con VERSION.

    Son la última red cuando no hay archivo VERSION ni metadata de paquete:
    scripts/_xdd_common.py (_VERSION_FALLBACK) y src/xdd_cli/__init__.py."""
    v = _canonical()
    offenders = []

    common = ROOT / "scripts" / "_xdd_common.py"
    m = re.search(r'_VERSION_FALLBACK\s*=\s*"([^"]+)"', common.read_text(encoding="utf-8"))
    assert m, "_xdd_common.py sin _VERSION_FALLBACK"
    if m.group(1) != v:
        offenders.append(("_xdd_common.py", m.group(1)))

    cli = ROOT / "src" / "xdd_cli" / "__init__.py"
    cli_txt = cli.read_text(encoding="utf-8")
    m2 = re.search(r'return\s+"(\d+\.\d+\.\d+[^"]*)"', cli_txt)
    assert m2, "xdd_cli/__init__.py sin fallback de versión"
    if m2.group(1) != v:
        offenders.append(("xdd_cli/__init__.py", m2.group(1)))

    assert not offenders, f"fallback divergente de VERSION={v}: {offenders}"


def test_agent_yaml_version_matches():
    v = _canonical()
    agent = ROOT / "agent.yaml"
    if not agent.exists():
        pytest.skip("agent.yaml ausente")
    txt = agent.read_text(encoding="utf-8")
    m = re.search(r'^version:\s*(.+)$', txt, re.MULTILINE)
    assert m, "agent.yaml sin campo version"
    assert m.group(1).strip().strip('"') == v, f"agent.yaml version != VERSION ({v})"
