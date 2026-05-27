"""Tests para scripts/xdd-orchestrate.py (Sprint 11)."""
from __future__ import annotations
import json, sys, importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("xdd_orchestrate", SCRIPTS / "xdd-orchestrate.py")
xo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xo)


def _args(**kw):
    ns = type("A", (), {})()
    for k, v in kw.items(): setattr(ns, k, v)
    return ns


def test_load_registry():
    reg = xo.load_registry()
    assert "agents" in reg
    assert "composition_patterns" in reg
    assert len(reg["agents"]) >= 180


def test_find_pattern_exists():
    reg = xo.load_registry()
    p = xo.find_pattern(reg, "security_review")
    assert p is not None
    assert p["orchestration"] == "sequential"


def test_find_pattern_missing():
    reg = xo.load_registry()
    assert xo.find_pattern(reg, "nonexistent") is None


def test_find_agent_exists():
    reg = xo.load_registry()
    a = xo.find_agent(reg, "engineering-code-reviewer")
    assert a is not None
    assert a["category"] == "engineering"


def test_find_agent_missing():
    reg = xo.load_registry()
    assert xo.find_agent(reg, "fake-agent") is None


def test_invoke_dry():
    reg = xo.load_registry()
    a = xo.find_agent(reg, "engineering-code-reviewer")
    r = xo.invoke_agent_dry(a, "run_test")
    assert r["invocation"] == "DRY-RUN"


def test_invoke_exec_validates_prompt_exists():
    reg = xo.load_registry()
    a = xo.find_agent(reg, "engineering-code-reviewer")
    r = xo.invoke_agent_exec(a, "run_test")
    assert r["exists"] is True


def test_run_sequential():
    reg = xo.load_registry()
    p = xo.find_pattern(reg, "security_review")
    results = xo.run_sequential(p, reg, "run_test", exec_mode=False)
    assert len(results) >= 2
    assert results[0]["role"] == "lead"
    assert any(r["role"] == "specialist" for r in results)


def test_run_parallel():
    reg = xo.load_registry()
    p = xo.find_pattern(reg, "feature_squad")
    results = xo.run_parallel(p, reg, "run_test", exec_mode=False)
    assert len(results) >= 2


def test_run_parallel_then_sync_includes_sync_point():
    reg = xo.load_registry()
    p = xo.find_pattern(reg, "feature_squad")
    results = xo.run_parallel_then_sync(p, reg, "run_test", exec_mode=False)
    sync = [r for r in results if r["role"] == "sync_point"]
    assert len(sync) == 1


def test_cmd_run_dry_returns_0(capsys):
    rc = xo.cmd_run(_args(pattern="security_review", exec=False, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pattern"] == "security_review"
    assert out["exec_mode"] is False
    assert len(out["steps"]) >= 2


def test_cmd_run_invalid_pattern():
    rc = xo.cmd_run(_args(pattern="nonexistent", exec=False, json=True))
    assert rc == 2


def test_cmd_list_includes_3_patterns(capsys):
    rc = xo.cmd_list(_args(json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["patterns"]) == 3
