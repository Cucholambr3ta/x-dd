"""Tests para scripts/xdd-router.py (Sprint 17 + ADR-0019)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xr", SCRIPTS / "xdd-router.py")
xr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xr)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_load_config_no_file_returns_empty(tmp_path):
    cfg = xr.load_config(str(tmp_path / "missing.yml"))
    assert cfg == {}


def test_provider_available_none_always_true():
    assert xr.provider_available("none") is True


def test_provider_available_claude_depends_env(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert xr.provider_available("claude") is False
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert xr.provider_available("claude") is True


def test_cmd_list_json(capsys):
    rc = xr.cmd_list(_Args(config=None, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["providers"]) == 4
    provs = [p["provider"] for p in out["providers"]]
    assert set(provs) == {"claude", "openai", "local", "none"}


def test_cmd_route_known_task_with_fallback(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    rc = xr.cmd_route(_Args(config=None, task="fast_classify",
                             max_cost=None, json=True))
    assert rc in (0, 1)  # fallback to "none" available
    out = json.loads(capsys.readouterr().out)
    assert out["task"] == "fast_classify"
    # claude no disponible → fallback chain debe tener al menos 1 entrada
    assert out["provider"] in {"claude", "openai", "local", "none"}


def test_cmd_route_unknown_task(capsys):
    rc = xr.cmd_route(_Args(config=None, task="not_a_real_task",
                             max_cost=None, json=False))
    assert rc == 2


def test_defaults_complete():
    expected_tasks = {"fast_classify", "code_review", "deep_reasoning",
                      "embedding", "bulk_extraction"}
    assert set(xr.DEFAULTS.keys()) == expected_tasks
    for task, route in xr.DEFAULTS.items():
        assert "provider" in route
        assert "model" in route
        assert "rationale" in route
