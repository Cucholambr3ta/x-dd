"""Tests for scripts/xdd-gate.py (Sprint 4).

Run: pytest tests/test_gate.py -v
Requires: pytest
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Permite importar el script como módulo (sin pyproject por ahora).
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "xdd_gate", SCRIPTS_DIR / "xdd-gate.py"
)
xdd_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xdd_gate)  # type: ignore[union-attr]


# ---------- Fixtures ----------

@pytest.fixture
def proj(tmp_path: Path) -> Path:
    """Crea un proyecto X-DD mínimo en tmp con .xdd/<phase>/ y artefactos placeholder."""
    (tmp_path / ".xdd").mkdir()
    artefacts = {
        "briefing": [".xdd/briefing/SPEC.md", ".xdd/briefing/FEATURES.md"],
        "spec": [".xdd/spec/DOMAIN.md", ".xdd/spec/THREATS.md"],
        "plan": [".xdd/plan/PLAN.md"],
        "qa": [".xdd/qa/QA_REPORT.md"],
        "retro": [".xdd/retro/lecciones.md"],
    }
    for phase, files in artefacts.items():
        (tmp_path / ".xdd" / phase).mkdir()
        for f in files:
            (tmp_path / f).write_text(f"# placeholder for {f}\n")
    # build artifact es un directorio
    (tmp_path / ".xdd" / "build").mkdir()
    (tmp_path / ".xdd" / "build" / "REPORT.md").write_text("# build\n")
    return tmp_path


@pytest.fixture
def initialized(proj: Path) -> Path:
    """Proyecto con .gate-key generada."""
    args = type("A", (), {})()
    rc = xdd_gate.cmd_init(proj, args)
    assert rc == 0
    assert (proj / ".xdd" / ".gate-key").exists()
    return proj


# ---------- init ----------

def test_init_creates_key(proj: Path):
    args = type("A", (), {})()
    rc = xdd_gate.cmd_init(proj, args)
    assert rc == 0
    key_path = proj / ".xdd" / ".gate-key"
    assert key_path.exists()
    assert len(key_path.read_bytes()) == 32  # 256 bits


def test_init_idempotent(initialized: Path):
    """Llamar init dos veces no debe regenerar la clave."""
    original = (initialized / ".xdd" / ".gate-key").read_bytes()
    rc = xdd_gate.cmd_init(initialized, type("A", (), {})())
    assert rc == 0
    assert (initialized / ".xdd" / ".gate-key").read_bytes() == original


# ---------- approve ----------

def _approve(root: Path, phase: str, approver: str = "test-user", as_json: bool = False) -> int:
    args = type("A", (), {})()
    args.phase = phase
    args.approver = approver
    args.json = as_json
    return xdd_gate.cmd_approve(root, args)


def test_approve_writes_all_files(initialized: Path):
    rc = _approve(initialized, "briefing")
    assert rc == 0
    pdir = initialized / ".xdd" / "briefing"
    assert (pdir / ".status").read_text().strip() == "APROBADO"
    assert (pdir / ".checksums").exists()
    assert (pdir / ".signature").exists()
    assert (pdir / ".approvers").exists()
    cks = json.loads((pdir / ".checksums").read_text())
    assert ".xdd/briefing/SPEC.md" in cks
    assert all(len(v) == 16 for v in cks.values())  # SHA-256 truncado a 16


def test_approve_requires_approver(initialized: Path):
    """Sin --approver ni XDD_APPROVER debe fallar."""
    os.environ.pop("XDD_APPROVER", None)
    rc = _approve(initialized, "briefing", approver="")
    assert rc == 2


def test_approve_uses_env_approver(initialized: Path, monkeypatch):
    monkeypatch.setenv("XDD_APPROVER", "env-user")
    rc = _approve(initialized, "briefing", approver="")
    assert rc == 0
    apr = (initialized / ".xdd" / "briefing" / ".approvers").read_text()
    assert "env-user" in apr


def test_approve_fails_when_artifacts_missing(initialized: Path):
    """Si falta artefacto obligatorio, approve debe rechazar."""
    (initialized / ".xdd/briefing/SPEC.md").unlink()
    rc = _approve(initialized, "briefing")
    assert rc == 1


def test_approve_fails_without_gate_key(proj: Path):
    """Approve sin init previo debe fallar."""
    rc = _approve(proj, "briefing")
    assert rc == 2


# ---------- validate ----------

def _validate(root: Path, phase: str, as_json: bool = False) -> int:
    args = type("A", (), {})()
    args.phase = phase
    args.json = as_json
    return xdd_gate.cmd_validate(root, args)


def test_validate_passes_after_approve(initialized: Path):
    assert _approve(initialized, "briefing") == 0
    assert _validate(initialized, "briefing") == 0


def test_validate_detects_tampered_status(initialized: Path):
    """Editar manualmente .status debería invalidar la firma."""
    assert _approve(initialized, "briefing") == 0
    # No alteramos .status (sigue APROBADO) pero corrompemos un artefacto
    (initialized / ".xdd/briefing/SPEC.md").write_text("# tampered content\n")
    rc = _validate(initialized, "briefing")
    assert rc == 1


def test_validate_detects_invalid_signature(initialized: Path):
    """Alterar .signature debe ser detectado."""
    assert _approve(initialized, "briefing") == 0
    sig_path = initialized / ".xdd" / "briefing" / ".signature"
    sig_path.write_text("0" * 64 + "\n")
    rc = _validate(initialized, "briefing")
    assert rc == 1


def test_validate_detects_swapped_key(initialized: Path):
    """Regenerar manualmente la clave invalida firmas existentes."""
    assert _approve(initialized, "briefing") == 0
    import secrets as _s
    (initialized / ".xdd" / ".gate-key").write_bytes(_s.token_bytes(32))
    rc = _validate(initialized, "briefing")
    assert rc == 1


def test_validate_fails_when_status_missing(initialized: Path):
    rc = _validate(initialized, "briefing")
    assert rc == 1


# ---------- transition ----------

def _transition(root: Path, src: str, dst: str, as_json: bool = False) -> int:
    args = type("A", (), {})()
    args.phase = src
    args.to = dst
    args.json = as_json
    return xdd_gate.cmd_transition(root, args)


def test_transition_blocks_non_sequential(initialized: Path):
    """briefing → plan no debe permitirse."""
    rc = _transition(initialized, "briefing", "plan")
    assert rc == 1


def test_transition_requires_source_approved(initialized: Path):
    """briefing → spec falla si briefing no está APROBADO."""
    rc = _transition(initialized, "briefing", "spec")
    assert rc == 1


def test_transition_passes_when_source_approved(initialized: Path):
    assert _approve(initialized, "briefing") == 0
    rc = _transition(initialized, "briefing", "spec")
    assert rc == 0


def test_transition_unknown_phase(initialized: Path):
    rc = _transition(initialized, "briefing", "magic")
    assert rc == 2


# ---------- status ----------

def test_status_reports_all_phases(initialized: Path, capsys):
    args = type("A", (), {})()
    args.json = True
    rc = xdd_gate.cmd_status(initialized, args)
    assert rc == 0
    output = json.loads(capsys.readouterr().out)
    assert len(output) == len(xdd_gate.PHASE_IDS)
    ids = [e["phase"] for e in output]
    assert ids == list(xdd_gate.PHASE_IDS)
