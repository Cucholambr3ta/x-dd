"""Tests para scripts/xdd-replay.py (Sprint 18, ADR-0021)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xr", SCRIPTS / "xdd-replay.py")
xr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xr)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_record_appends_event(tmp_path, capsys):
    rc = xr.cmd_record(_Args(session="s1", event="turn_start", role="user",
                              content="hello", attrs=None, json=True,
                              dir=str(tmp_path)))
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True
    p = tmp_path / "s1.jsonl"
    assert p.exists()
    lines = p.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event"] == "turn_start"


def test_list_sessions_lists(tmp_path, capsys):
    for sid in ("a", "b", "c"):
        xr.cmd_record(_Args(session=sid, event="x", role=None, content=None,
                             attrs=None, json=True, dir=str(tmp_path)))
        capsys.readouterr()
    rc = xr.cmd_list(_Args(json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 3


def test_show_session_summary(tmp_path, capsys):
    for ev in ("a", "b", "a", "c"):
        xr.cmd_record(_Args(session="s", event=ev, role=None, content=None,
                             attrs=None, json=True, dir=str(tmp_path)))
        capsys.readouterr()
    rc = xr.cmd_show(_Args(id="s", json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["total_events"] == 4
    assert out["event_types"] == {"a": 2, "b": 1, "c": 1}


def test_show_missing_session_error():
    rc = xr.cmd_show(_Args(id="nonexistent", json=True, dir="/tmp/nowhere-zzz"))
    assert rc == 2


def test_diff_two_sessions(tmp_path, capsys):
    xr.cmd_record(_Args(session="a", event="e1", role=None, content=None,
                          attrs=None, json=True, dir=str(tmp_path)))
    capsys.readouterr()
    xr.cmd_record(_Args(session="a", event="shared", role=None, content=None,
                          attrs=None, json=True, dir=str(tmp_path)))
    capsys.readouterr()
    xr.cmd_record(_Args(session="b", event="e2", role=None, content=None,
                          attrs=None, json=True, dir=str(tmp_path)))
    capsys.readouterr()
    xr.cmd_record(_Args(session="b", event="shared", role=None, content=None,
                          attrs=None, json=True, dir=str(tmp_path)))
    capsys.readouterr()
    rc = xr.cmd_diff(_Args(a="a", b="b", json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["only_in_a"] == ["e1"]
    assert out["only_in_b"] == ["e2"]
    assert "shared" in out["common_event_types"]
