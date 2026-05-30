"""Tests para el empaquetado pip (Branch 3 — src/xdd_cli + pyproject.toml)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import xdd_cli  # noqa: E402


def test_scripts_dir_resolves_to_repo(monkeypatch):
    monkeypatch.delenv("XDD_SCRIPTS_DIR", raising=False)
    d = xdd_cli._scripts_dir()
    assert d.is_dir()
    assert (d / "xdd-gate.py").exists()


def test_scripts_dir_respects_env(monkeypatch, tmp_path):
    monkeypatch.setenv("XDD_SCRIPTS_DIR", str(tmp_path))
    assert xdd_cli._scripts_dir() == tmp_path


def test_run_missing_script_returns_2(monkeypatch, tmp_path):
    monkeypatch.setenv("XDD_SCRIPTS_DIR", str(tmp_path))
    assert xdd_cli._run("nope.py") == 2


def test_dispatcher_provider_self_test(monkeypatch, capsys):
    monkeypatch.delenv("XDD_SCRIPTS_DIR", raising=False)
    monkeypatch.setattr(sys, "argv", ["xdd-provider", "--self-test"])
    rc = xdd_cli.provider()
    assert rc == 0
    assert "self-test OK" in capsys.readouterr().out


def test_dispatcher_flow_self_test(monkeypatch, capsys):
    monkeypatch.delenv("XDD_SCRIPTS_DIR", raising=False)
    monkeypatch.setattr(sys, "argv", ["xdd-flow", "--self-test"])
    rc = xdd_cli.flow()
    assert rc == 0


def test_pyproject_declares_entry_points():
    pp = (ROOT / "pyproject.toml").read_text()
    for ep in ["xdd-gate", "xdd-eval", "xdd-flow", "xdd-provider"]:
        assert ep in pp, f"entry-point {ep} ausente en pyproject.toml"
    assert 'packages = ["src/xdd_cli"]' in pp
