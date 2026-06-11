"""Tests para scripts/xdd-hooks-install.py — materializador hooks.json → settings.json.

Cierra el gap detectado tras v0.1.1 (hooks definidos pero no materializados).
Run: pytest tests/test_hooks_install.py -v
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("xdd_hooks_install",
                                               SCRIPTS / "xdd-hooks-install.py")
xhi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xhi)


# ---------- traducción ----------

def test_only_claude_events_materialized():
    """Los eventos propios de X-DD (before_model, wrap_tool_call…) NO se materializan."""
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "strict")
    assert set(groups).issubset(xhi.CLAUDE_EVENTS)
    # strict incluye todo el catálogo, pero ningún evento no-Claude debe colarse.
    assert "before_model" not in groups
    assert "wrap_tool_call" not in groups


def test_profile_filtering():
    """minimal sólo trae el hook mempalace (único con profile minimal)."""
    catalog = xhi.load_catalog()
    g_min = xhi.materialized_groups(catalog, "minimal")
    ids_min = {x["_xdd_id"] for v in g_min.values() for x in v}
    assert ids_min == {"post:edit:mempalace-index"}

    g_std = xhi.materialized_groups(catalog, "standard")
    ids_std = {x["_xdd_id"] for v in g_std.values() for x in v}
    assert "post:edit:mempalace-index" in ids_std
    assert "post:bash:pr-logger" in ids_std
    # strict ⊇ standard ⊇ minimal
    g_strict = xhi.materialized_groups(catalog, "strict")
    ids_strict = {x["_xdd_id"] for v in g_strict.values() for x in v}
    assert ids_std <= ids_strict
    assert ids_min <= ids_std


def test_matcher_only_for_tool_events():
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "strict")
    for g in groups.get("PreToolUse", []) + groups.get("PostToolUse", []):
        assert "matcher" in g
    for g in groups.get("SessionStart", []) + groups.get("Stop", []):
        assert "matcher" not in g


def test_blocking_hook_preserves_exit_code():
    """Hook con exit_on_match!=0 (bloqueante) NO lleva '|| true'."""
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "strict")
    cmds = {g["_xdd_id"]: g["hooks"][0]["command"] for v in groups.values() for g in v}
    blocking = cmds["pre:bash:dangerous-command"]
    assert "|| true" not in blocking
    assert "if [ -f" in blocking
    # async/no-bloqueante sí traga el error
    nonblock = cmds["post:edit:mempalace-index"]
    assert "|| true" in nonblock


def test_guard_present_in_command():
    """Todo command incluye guarda de existencia ($PWD/...) — no-op fuera de X-DD."""
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "strict")
    for v in groups.values():
        for g in v:
            assert '"$PWD/.agent/hooks/scripts/' in g["hooks"][0]["command"]


# ---------- merge / idempotencia ----------

def _foreign_settings() -> dict:
    """Simula settings con hooks ajenos (estilo caveman)."""
    return {
        "hooks": {
            "SessionStart": [
                {"hooks": [{"type": "command", "command": "node caveman.js"}]}
            ],
            "UserPromptSubmit": [
                {"hooks": [{"type": "command", "command": "node tracker.js"}]}
            ],
        }
    }


def test_merge_preserves_foreign_hooks():
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "standard")
    merged = xhi.merge(_foreign_settings(), groups)
    h = merged["hooks"]
    # caveman intacto
    assert any("caveman.js" in x["hooks"][0]["command"] for x in h["SessionStart"])
    assert any("tracker.js" in x["hooks"][0]["command"] for x in h["UserPromptSubmit"])
    # X-DD añadido
    xdd_ids = {g.get("_xdd_id") for v in h.values() for g in v if "_xdd_id" in g}
    assert "post:edit:mempalace-index" in xdd_ids


def test_merge_idempotent():
    """Correr merge 2× no duplica los grupos X-DD."""
    catalog = xhi.load_catalog()
    groups = xhi.materialized_groups(catalog, "standard")
    once = xhi.merge(_foreign_settings(), groups)
    twice = xhi.merge(once, xhi.materialized_groups(catalog, "standard"))

    def count_xdd(s):
        return sum(1 for v in s["hooks"].values() for g in v if "_xdd_id" in g)

    assert count_xdd(once) == count_xdd(twice)
    # y los ajenos no se multiplican
    assert len(twice["hooks"]["SessionStart"]) == len(once["hooks"]["SessionStart"])


def test_strip_xdd_removes_only_marked():
    settings = {"hooks": {"SessionStart": [
        {"hooks": [{"type": "command", "command": "foreign"}]},
        {"_xdd_id": "x", "hooks": [{"type": "command", "command": "xdd"}]},
    ]}}
    stripped = xhi.strip_xdd(settings)
    groups = stripped["hooks"]["SessionStart"]
    assert len(groups) == 1
    assert "_xdd_id" not in groups[0]


# ---------- I/O ----------

def test_install_writes_file(tmp_path, monkeypatch):
    dest = tmp_path / ".claude" / "settings.json"
    monkeypatch.setattr(xhi, "settings_path", lambda project: dest)
    args = type("A", (), {"profile": "standard", "project": False, "dry_run": False})()
    rc = xhi.cmd_install(args)
    assert rc == 0
    written = json.loads(dest.read_text(encoding="utf-8"))
    ids = {g.get("_xdd_id") for v in written["hooks"].values() for g in v}
    assert "post:edit:mempalace-index" in ids


def test_dry_run_does_not_write(tmp_path, monkeypatch, capsys):
    dest = tmp_path / ".claude" / "settings.json"
    monkeypatch.setattr(xhi, "settings_path", lambda project: dest)
    args = type("A", (), {"profile": "standard", "project": False, "dry_run": True})()
    rc = xhi.cmd_install(args)
    assert rc == 0
    assert not dest.exists()
    assert "(dry-run)" in capsys.readouterr().out


def test_status_reports_missing(tmp_path, monkeypatch):
    dest = tmp_path / ".claude" / "settings.json"  # no existe → todo falta
    monkeypatch.setattr(xhi, "settings_path", lambda project: dest)
    args = type("A", (), {"profile": "standard", "project": False, "dry_run": False})()
    rc = xhi.cmd_status(args)
    assert rc == 1  # faltan hooks


def test_main_parses_once():
    """main() despacha sin doble-parseo (misma regresión que orchestrate)."""
    rc = xhi.main(["status", "--profile", "minimal", "--project"])
    assert rc in (0, 1)
