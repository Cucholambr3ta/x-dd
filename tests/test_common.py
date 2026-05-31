"""Tests para scripts/_xdd_common.py — utilidades compartidas (S1, gap de cobertura).

Run: pytest tests/test_common.py -v
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("_xdd_common", SCRIPTS / "_xdd_common.py")
common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(common)


# ---------- timestamps ----------

def test_utcnow_iso_segundo():
    ts = common.utcnow_iso()
    # %Y-%m-%dT%H:%M:%SZ — precisión de segundo, sin fracción.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts), ts


def test_utcnow_iso_us_microsegundo():
    ts = common.utcnow_iso_us()
    # %Y-%m-%dT%H:%M:%S.%fZ — con fracción de microsegundo.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", ts), ts


def test_utcnow_alias_es_segundo():
    """`utcnow` debe ser alias de utcnow_iso (segundo), no de la variante us."""
    assert common.utcnow is common.utcnow_iso
    assert "." not in common.utcnow()


# ---------- read_version (3 caminos) ----------

def test_read_version_lee_archivo_VERSION():
    """En el repo (editable) read_version lee el archivo VERSION de la raíz."""
    v = common.read_version()
    canon = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == canon
    assert re.match(r"^\d+\.\d+\.\d+", v)


def test_read_version_fallback_es_semver():
    """El fallback literal embebido debe ser semver y coincidir con VERSION."""
    assert re.match(r"^\d+\.\d+\.\d+", common._VERSION_FALLBACK)
    assert common._VERSION_FALLBACK == (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_read_version_fallback_si_no_hay_archivo(tmp_path, monkeypatch):
    """Si VERSION no existe y no hay paquete instalado, cae al fallback literal.

    Se simula moviendo la resolución del archivo a un dir vacío."""
    fake_file = tmp_path / "VERSION"  # no existe
    monkeypatch.setattr(common, "__file__", str(tmp_path / "scripts" / "_xdd_common.py"))
    # Con __file__ apuntando a tmp, parent.parent/VERSION no existe.
    # Puede resolver vía importlib.metadata si 'x-dd' está instalado; si no, fallback.
    v = common.read_version()
    assert re.match(r"^\d+\.\d+\.\d+", v)  # siempre semver, nunca crashea
