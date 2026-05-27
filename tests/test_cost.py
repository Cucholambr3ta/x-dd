"""Tests para scripts/xdd-cost.py (Sprint 18, ADR-0022)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xc", SCRIPTS / "xdd-cost.py")
xc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xc)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "cost.db")


def test_record_haiku_call(db_path, capsys):
    rc = xc.cmd_record(_Args(db=db_path, provider="claude", model="claude-haiku-4-5",
                              input_tokens=1000, output_tokens=500,
                              session_id="s1", task="test", json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    # Haiku: 1000 in * 0.25/1M + 500 out * 1.25/1M = 0.00025 + 0.000625 = 0.000875
    assert abs(out["cost_usd"] - 0.000875) < 1e-9


def test_record_opus_more_expensive(db_path, capsys):
    xc.cmd_record(_Args(db=db_path, provider="claude", model="claude-opus-4-7",
                         input_tokens=1000, output_tokens=500,
                         session_id=None, task=None, json=True))
    out = json.loads(capsys.readouterr().out)
    # Opus: 1000 * 15/1M + 500 * 75/1M = 0.015 + 0.0375 = 0.0525
    assert abs(out["cost_usd"] - 0.0525) < 1e-9


def test_record_local_zero_cost(db_path, capsys):
    xc.cmd_record(_Args(db=db_path, provider="local", model="llama3.1-8b",
                         input_tokens=10000, output_tokens=5000,
                         session_id=None, task=None, json=True))
    out = json.loads(capsys.readouterr().out)
    assert out["cost_usd"] == 0.0


def test_report_aggregates_by_model(db_path, capsys):
    for _ in range(3):
        xc.cmd_record(_Args(db=db_path, provider="claude", model="claude-haiku-4-5",
                             input_tokens=1000, output_tokens=500,
                             session_id=None, task=None, json=True))
        capsys.readouterr()
    rc = xc.cmd_report(_Args(db=db_path, since=None, by="model", json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["total_calls"] == 3
    assert out["rows"][0]["bucket"] == "claude-haiku-4-5"
    assert out["rows"][0]["calls"] == 3


def test_pricing_list_includes_defaults(db_path, capsys):
    rc = xc.cmd_pricing(_Args(db=db_path, list=True, update=False, model=None,
                               input=None, output=None, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "claude-haiku-4-5" in out["defaults"]
    assert out["defaults"]["claude-haiku-4-5"] == [0.25, 1.25]


def test_pricing_override_persisted(db_path, capsys):
    rc = xc.cmd_pricing(_Args(db=db_path, list=False, update=True,
                               model="custom-model", input=1.0, output=5.0,
                               json=False))
    assert rc == 0
    capsys.readouterr()
    # Now record with override
    xc.cmd_record(_Args(db=db_path, provider="custom", model="custom-model",
                         input_tokens=1_000_000, output_tokens=1_000_000,
                         session_id=None, task=None, json=True))
    out = json.loads(capsys.readouterr().out)
    # 1M input * 1.0 + 1M output * 5.0 = 6.0
    assert abs(out["cost_usd"] - 6.0) < 1e-9


def test_total_command(db_path, capsys):
    xc.cmd_record(_Args(db=db_path, provider="x", model="claude-haiku-4-5",
                         input_tokens=1000, output_tokens=1000,
                         session_id=None, task=None, json=True))
    capsys.readouterr()
    rc = xc.cmd_total(_Args(db=db_path, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["total_calls"] == 1
    assert out["total_cost_usd"] > 0


def test_pricing_defaults_table_complete():
    expected = {"claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7",
                "gpt-4o-mini", "gpt-4o", "gemini-2.0-flash", "llama3.1-8b"}
    assert expected.issubset(set(xc.PRICING_DEFAULT.keys()))
