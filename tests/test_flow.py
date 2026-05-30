"""Tests para scripts/xdd-flow.py (gate ejecutable de flujos, Branch 2)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xf", SCRIPTS / "xdd-flow.py")
xf = importlib.util.module_from_spec(_spec)
sys.modules["xf"] = xf  # dataclass resolución de tipos necesita el módulo registrado
_spec.loader.exec_module(xf)

_gspec = importlib.util.spec_from_file_location("xg", SCRIPTS / "xdd-gate.py")
xg = importlib.util.module_from_spec(_gspec)
_gspec.loader.exec_module(xg)


# --- runtime sequential / parallel ---

def test_sequential_pipes_output_to_next():
    flow = {
        "agents": [
            {"name": "a", "responses": {"hi": "HI"}},
            {"name": "b", "default": "done"},
        ],
        "mode": "sequential",
        "input": "hi",
    }
    t = xf.execute_flow(flow)
    assert len(t.steps) == 2
    assert t.steps[0].output == "HI"
    assert t.result == "done"


def test_parallel_deterministic_order_by_name():
    flow = {
        "agents": [{"name": "b", "default": "B"}, {"name": "a", "default": "A"}],
        "mode": "parallel",
        "input": "x",
    }
    t = xf.execute_flow(flow)
    assert [s.agent_name for s in t.steps] == ["a", "b"]
    assert t.result == ["A", "B"]


def test_execute_flow_is_deterministic():
    flow = {"agents": [{"name": "a", "default": "z"}], "mode": "sequential", "input": "q"}
    assert xf.execute_flow(flow).result == xf.execute_flow(flow).result == "z"


def test_empty_agents_raises():
    with pytest.raises(ValueError):
        xf.execute_flow({"agents": [], "mode": "sequential"})


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        xf.execute_flow({"agents": [{"name": "a", "default": "x"}], "mode": "bogus"})


# --- grader ---

def test_grade_exact_expected():
    flow = {"agents": [{"name": "a", "default": "ok"}], "mode": "sequential",
            "input": "i", "expected": "ok"}
    t = xf.execute_flow(flow)
    ok, _ = xf.grade_result(t, flow)
    assert ok


def test_grade_expected_mismatch_fails():
    flow = {"agents": [{"name": "a", "default": "no"}], "mode": "sequential",
            "input": "i", "expected": "yes"}
    t = xf.execute_flow(flow)
    ok, _ = xf.grade_result(t, flow)
    assert not ok


def test_grade_regex():
    flow = {"agents": [{"name": "a", "default": "abc123"}], "mode": "sequential",
            "input": "i", "expected_regex": r"\d+"}
    t = xf.execute_flow(flow)
    ok, _ = xf.grade_result(t, flow)
    assert ok


def test_grade_no_expected_passes_if_steps():
    flow = {"agents": [{"name": "a", "default": "x"}], "mode": "sequential", "input": "i"}
    t = xf.execute_flow(flow)
    ok, _ = xf.grade_result(t, flow)
    assert ok


# --- trace persistence + CLI ---

def test_run_writes_trace(tmp_path, monkeypatch):
    flow = tmp_path / "f.json"
    flow.write_text(json.dumps({
        "agents": [{"name": "a", "default": "ok"}], "mode": "sequential",
        "input": "i", "expected": "ok",
    }))
    out = tmp_path / "trace.json"
    rc = xf.main(["run", "--flow", str(flow), "--trace", str(out)])
    assert rc == 0
    data = json.loads(out.read_text())
    assert data["step_count"] == 1
    assert data["result"] == "ok"


def test_self_test_cli():
    assert xf.main(["--self-test"]) == 0


# --- gate integration: _check_flow_evidence ---

def _mk_build(tmp_path) -> Path:
    b = tmp_path / ".xdd" / "build"
    b.mkdir(parents=True)
    return b


def test_flow_evidence_skipped_when_no_flow_declared(tmp_path):
    _mk_build(tmp_path)
    assert xg._check_flow_evidence(tmp_path) == []


def test_flow_evidence_missing_trace_fails(tmp_path):
    b = _mk_build(tmp_path)
    (b / "flow.json").write_text("{}")
    errs = xg._check_flow_evidence(tmp_path)
    assert errs and "flow-trace.json" in errs[0]


def test_flow_evidence_empty_steps_fails(tmp_path):
    b = _mk_build(tmp_path)
    (b / "flow.json").write_text("{}")
    (b / "flow-trace.json").write_text(json.dumps({"step_count": 0, "steps": [], "result": None}))
    errs = xg._check_flow_evidence(tmp_path)
    assert errs and "sin steps" in errs[0]


def test_flow_evidence_valid_trace_passes(tmp_path):
    b = _mk_build(tmp_path)
    (b / "flow.json").write_text("{}")
    (b / "flow-trace.json").write_text(json.dumps({
        "step_count": 1,
        "steps": [{"agent_name": "a", "input": "i", "output": "o", "ts": 1.0, "duration_ms": 0.1}],
        "result": "o",
    }))
    assert xg._check_flow_evidence(tmp_path) == []
