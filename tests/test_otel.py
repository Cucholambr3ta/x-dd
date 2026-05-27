"""Tests para scripts/xdd-otel.py (Sprint 18, ADR-0021)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xo", SCRIPTS / "xdd-otel.py")
xo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xo)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_span_start_writes_json(tmp_path, capsys):
    rc = xo.cmd_span_start(_Args(
        name="test.span", kind="llm.call", trace_id=None, parent=None,
        attrs=None, json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "span_id" in out
    assert "trace_id" in out
    p = Path(out["file"])
    assert p.exists()
    span = json.loads(p.read_text())
    assert span["name"] == "test.span"
    assert span["kind"] == "llm.call"
    assert span["status"] == "in_progress"


def test_span_end_closes(tmp_path, capsys):
    xo.cmd_span_start(_Args(name="x", kind="tool.call", trace_id=None,
                              parent=None, attrs=None, json=True, dir=str(tmp_path)))
    sid = json.loads(capsys.readouterr().out)["span_id"]
    rc = xo.cmd_span_end(_Args(id=sid, status="ok", attrs=None, json=True,
                                  dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"
    assert out["duration_ms"] >= 0


def test_emit_oneshot(tmp_path, capsys):
    rc = xo.cmd_emit(_Args(
        name="oneshot", kind="agent.invocation", duration_ms="42.5",
        trace_id=None, parent=None, attrs='{"k":"v"}', json=True,
        dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    span = json.loads(Path(out["file"]).read_text())
    assert span["duration_ms"] == 42.5
    assert span["attributes"] == {"k": "v"}


def test_list_empty(tmp_path, capsys):
    rc = xo.cmd_list(_Args(json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out == []


def test_list_multiple(tmp_path, capsys):
    for i in range(3):
        xo.cmd_emit(_Args(name=f"s{i}", kind="llm.call", duration_ms=str(i),
                            trace_id=None, parent=None, attrs=None, json=True,
                            dir=str(tmp_path)))
        capsys.readouterr()
    rc = xo.cmd_list(_Args(json=True, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 3


def test_export_otlp_format(tmp_path, capsys):
    xo.cmd_emit(_Args(name="e", kind="llm.call", duration_ms="1",
                        trace_id=None, parent=None, attrs=None, json=True,
                        dir=str(tmp_path)))
    capsys.readouterr()
    rc = xo.cmd_export(_Args(format="otlp", since=None, dir=str(tmp_path)))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "resourceSpans" in out
    assert out["resourceSpans"][0]["scopeSpans"][0]["scope"]["name"] == "xdd-otel"


def test_genai_kinds_includes_expected():
    expected = {"llm.call", "tool.call", "agent.invocation", "skill.execution"}
    assert expected.issubset(xo.GENAI_KINDS)
