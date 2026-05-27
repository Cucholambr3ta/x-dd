"""Tests para scripts/xdd-context.py (Sprint 19, ADR-0023)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xc", SCRIPTS / "xdd-context.py")
xc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xc)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_estimate_empty():
    assert xc.estimate_tokens("") == 0


def test_estimate_short_text():
    # "hello world" → ~3-4 tokens heurística
    n = xc.estimate_tokens("hello world")
    assert 1 <= n <= 10


def test_estimate_proportional():
    short = xc.estimate_tokens("abc " * 10)
    long = xc.estimate_tokens("abc " * 100)
    assert long > short
    assert long >= short * 5  # mostly linear


def test_cmd_estimate_text(capsys):
    rc = xc.cmd_estimate(_Args(text="hello world", file=None, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["tokens"] >= 1
    assert out["chars"] == 11


def test_cmd_estimate_file(tmp_path, capsys):
    p = tmp_path / "input.txt"
    p.write_text("a" * 4000)
    rc = xc.cmd_estimate(_Args(text=None, file=str(p), json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["chars"] == 4000
    assert out["tokens"] > 0


def test_cmd_check_ok(capsys):
    rc = xc.cmd_check(_Args(tokens=1000, budget=200000, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"


def test_cmd_check_warning(capsys):
    # 85% del budget
    rc = xc.cmd_check(_Args(tokens=170000, budget=200000, json=True))
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "warning"


def test_cmd_check_block(capsys):
    # 97% del budget
    rc = xc.cmd_check(_Args(tokens=194000, budget=200000, json=True))
    assert rc == 2
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "block"


def test_cmd_budget_show_default(capsys):
    rc = xc.cmd_budget(_Args(show=True, set=False, max_tokens=None, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["max_tokens"] == xc.DEFAULT_BUDGET
    assert out["warning_threshold"] == xc.WARNING_THRESHOLD


def test_thresholds_sane():
    assert 0 < xc.WARNING_THRESHOLD < xc.BLOCK_THRESHOLD < 1.0
