"""Tests del enforcement FSM en xdd-gate.py (Incremento 1).

Verifica:
- I1.1 cadena de fases: no se firma una fase sin las previas aprobadas
- I1.2 separacion autor != aprobador (con escape hatch)
- I1.3 status muestra autor/aprobador/cadena
- overrides XDD_SKIP_CHAIN / XDD_SKIP_SEGREGATION
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "xdd-gate.py"

PHASE_ARTIFACTS = {
    "briefing": [".xdd/briefing/SPEC.md", ".xdd/briefing/FEATURES.md"],
    "spec": [".xdd/spec/DOMAIN.md", ".xdd/spec/THREATS.md"],
    "plan": [".xdd/plan/PLAN.md"],
}


def _run(args, cwd, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(GATE), "--project-root", str(cwd), *args],
        cwd=str(cwd), env=env, capture_output=True, text=True,
    )


def _make_artifacts(project, phase):
    for rel in PHASE_ARTIFACTS[phase]:
        p = project / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {phase} artifact con contenido suficiente para validar\n")


@pytest.fixture
def project(tmp_path):
    _run(["init"], tmp_path)
    return tmp_path


def _approve(project, phase, approver):
    _make_artifacts(project, phase)
    return _run(["approve", "--phase", phase, "--approver", approver], project)


# ── I1.1 cadena de fases ──────────────────────────────────────────────────────

def test_plan_blocked_without_chain(project):
    _make_artifacts(project, "plan")
    r = _run(["approve", "--phase", "plan", "--approver", "bob"], project)
    assert r.returncode == 1
    assert "cadena de fases incompleta" in r.stderr


def test_briefing_first_phase_no_chain(project):
    r = _approve(project, "briefing", "alice")
    assert r.returncode == 0


def test_full_chain_in_order_passes(project):
    assert _approve(project, "briefing", "alice").returncode == 0
    assert _approve(project, "spec", "bob").returncode == 0
    assert _approve(project, "plan", "carol").returncode == 0


def test_skip_chain_override(project):
    _make_artifacts(project, "plan")
    r = _run(["approve", "--phase", "plan", "--approver", "bob"],
             project, {"XDD_SKIP_CHAIN": "1"})
    assert r.returncode == 0
    assert "XDD_SKIP_CHAIN=1" in r.stderr


# ── I1.2 separacion autor != aprobador ────────────────────────────────────────

def test_segregation_blocks_self_approval(project):
    _approve(project, "briefing", "alice")
    _make_artifacts(project, "spec")
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "alice"], project)
    assert r.returncode == 1
    assert "no puede ser el autor" in r.stderr


def test_segregation_allows_different_approver(project):
    _approve(project, "briefing", "alice")
    _make_artifacts(project, "spec")
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "bob"], project)
    assert r.returncode == 0


def test_segregation_override(project):
    _approve(project, "briefing", "alice")
    _make_artifacts(project, "spec")
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "alice"],
             project, {"XDD_SKIP_SEGREGATION": "1"})
    assert r.returncode == 0
    assert "XDD_SKIP_SEGREGATION=1" in r.stderr


def test_set_author_writes_file(project):
    _run(["set-author", "--phase", "spec", "--author", "dave"], project)
    af = project / ".xdd" / "spec" / ".author"
    assert af.exists()
    assert af.read_text().strip() == "dave"


# ── I1.3 status ───────────────────────────────────────────────────────────────

def test_status_shows_author_and_approver(project):
    _approve(project, "briefing", "alice")
    _make_artifacts(project, "spec")
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    _run(["approve", "--phase", "spec", "--approver", "bob"], project)
    r = _run(["status", "--json"], project)
    data = json.loads(r.stdout)
    spec = next(e for e in data if e["phase"] == "spec")
    assert spec.get("author") == "alice"
    assert spec.get("approver") == "bob"
