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


def test_python_scripts_version_matches():
    """Todo __version__ hardcoded en scripts/*.py debe coincidir con VERSION."""
    v = _canonical()
    offenders = []
    for f in glob.glob(str(ROOT / "scripts" / "*.py")):
        txt = Path(f).read_text(encoding="utf-8")
        for m in re.finditer(r'__version__\s*=\s*"([^"]+)"', txt):
            if m.group(1) != v:
                offenders.append((Path(f).name, m.group(1)))
    assert not offenders, f"__version__ divergente de VERSION={v}: {offenders}"


def test_agent_yaml_version_matches():
    v = _canonical()
    agent = ROOT / "agent.yaml"
    if not agent.exists():
        pytest.skip("agent.yaml ausente")
    txt = agent.read_text(encoding="utf-8")
    m = re.search(r'^version:\s*(.+)$', txt, re.MULTILINE)
    assert m, "agent.yaml sin campo version"
    assert m.group(1).strip().strip('"') == v, f"agent.yaml version != VERSION ({v})"
