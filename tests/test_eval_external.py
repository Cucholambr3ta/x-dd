"""Tests para Sprint 20: grader_inspect_ai_compat + grader_pass_at_one_external + meta-eval."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xe", SCRIPTS / "xdd-eval.py")
xe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xe)

_spec2 = importlib.util.spec_from_file_location("xm", SCRIPTS / "xdd-meta-eval.py")
xm = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(xm)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


# ---------- inspect_ai_compat grader ----------

def test_inspect_ai_compat_match_pass():
    case = {"input": "?", "target": "foo", "output": "foo"}
    grader = {"scorers": ["match"]}
    ok, _ = xe.grader_inspect_ai_compat(case, grader)
    assert ok is True


def test_inspect_ai_compat_match_fail():
    case = {"input": "?", "target": "foo", "output": "bar"}
    grader = {"scorers": ["match"]}
    ok, _ = xe.grader_inspect_ai_compat(case, grader)
    assert ok is False


def test_inspect_ai_compat_includes_case_insensitive():
    case = {"target": "Paris", "output": "the capital is paris and is beautiful"}
    grader = {"scorers": ["includes"]}
    ok, _ = xe.grader_inspect_ai_compat(case, grader)
    assert ok is True


def test_inspect_ai_compat_regex():
    case = {"target": r"^\d{4}-\d{2}-\d{2}$", "output": "2026-05-27"}
    grader = {"scorers": ["regex"]}
    ok, _ = xe.grader_inspect_ai_compat(case, grader)
    assert ok is True


def test_inspect_ai_compat_multiple_scorers_all_pass():
    case = {"target": "Paris", "output": "Paris"}
    grader = {"scorers": ["match", "includes"]}
    ok, _ = xe.grader_inspect_ai_compat(case, grader)
    assert ok is True


# ---------- pass_at_one_external grader ----------

def test_pass_at_one_external_match():
    case = {"task_id": "tb-001", "actual_pass": True, "expected_outcome": "pass"}
    ok, msg = xe.grader_pass_at_one_external(case, {})
    assert ok is True
    assert "tb-001" in msg


def test_pass_at_one_external_mismatch():
    case = {"task_id": "swe-002", "actual_pass": False, "expected_outcome": "pass"}
    ok, msg = xe.grader_pass_at_one_external(case, {})
    assert ok is False
    assert "swe-002" in msg


def test_graders_registry_includes_new_types():
    assert "inspect_ai_compat" in xe.GRADERS
    assert "pass_at_one_external" in xe.GRADERS


# ---------- meta-eval ----------

def test_compare_needs_2_runs(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(xm, "RUNS_DIR", tmp_path)
    rc = xm.cmd_compare(_Args(last=5, suite=None, json=True))
    assert rc == 1  # not enough


def test_compare_two_runs(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(xm, "RUNS_DIR", tmp_path)
    d = tmp_path / "suite1"
    d.mkdir()
    (d / "run-001.json").write_text(json.dumps({"suite": "suite1", "pass_rate": 0.8}))
    (d / "run-002.json").write_text(json.dumps({"suite": "suite1", "pass_rate": 0.9}))
    rc = xm.cmd_compare(_Args(last=5, suite="suite1", json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["runs_compared"] == 2
    assert out["trend"] == "improving"


def test_compare_regression(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(xm, "RUNS_DIR", tmp_path)
    d = tmp_path / "suite1"
    d.mkdir()
    (d / "run-001.json").write_text(json.dumps({"suite": "suite1", "pass_rate": 0.6}))
    (d / "run-002.json").write_text(json.dumps({"suite": "suite1", "pass_rate": 0.9}))
    # Más reciente primero (sort reverse) → run-002 = latest = 0.6 si nombrado al revés
    # En realidad sorted reverse de nombres: 002 > 001, así que latest=run-002 (0.9)
    # Para forzar regresión: nombrar el regresivo MÁS RECIENTE
    (d / "run-003.json").write_text(json.dumps({"suite": "suite1", "pass_rate": 0.4}))
    rc = xm.cmd_compare(_Args(last=5, suite="suite1", json=True))
    out = json.loads(capsys.readouterr().out)
    assert out["latest_pass_rate"] == 0.4
    assert out["trend"] == "regressing"
    assert rc == 1


def test_baseline_set_and_show(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(xm, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(xm, "BASELINES", tmp_path / "baselines.json")
    d = tmp_path / "s"
    d.mkdir()
    (d / "r1.json").write_text(json.dumps({"suite": "s", "pass_rate": 0.75}))
    rc = xm.cmd_baseline(_Args(set=True, show=False, suite="s", json=False))
    assert rc == 0
    capsys.readouterr()
    rc = xm.cmd_baseline(_Args(set=False, show=True, suite=None, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["s"]["pass_rate"] == 0.75


# ---------- external evals structure ----------

def test_external_evals_have_required_files():
    base = ROOT / "evals" / "external"
    for suite in ["terminal-bench-2", "swe-bench-verified",
                  "promptfoo-compat", "longmemeval"]:
        d = base / suite
        assert d.exists(), f"missing dir: {d}"
        assert (d / "cases.jsonl").exists(), f"missing cases.jsonl in {suite}"
        assert (d / "grader.yaml").exists(), f"missing grader.yaml in {suite}"
        assert (d / "README.md").exists(), f"missing README.md in {suite}"
