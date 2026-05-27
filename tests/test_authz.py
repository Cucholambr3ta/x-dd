"""Tests para scripts/xdd-authz.py (Sprint 21, ADR-0028)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xa", SCRIPTS / "xdd-authz.py")
xa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xa)


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_decide_secret_access_deny():
    action = xa.decide(["secret_access"], "critical", xa.DEFAULT_POLICY)
    assert action == "deny"


def test_decide_filesystem_delete_require_approval():
    action = xa.decide(["filesystem_delete"], "critical", xa.DEFAULT_POLICY)
    assert action == "require_approval"


def test_decide_read_only_allow():
    action = xa.decide(["read_only"], "low", xa.DEFAULT_POLICY)
    assert action == "allow"


def test_decide_lang_exec_require_approval():
    action = xa.decide(["lang_exec"], "high", xa.DEFAULT_POLICY)
    assert action == "require_approval"


def test_decide_multiple_intents_first_match():
    # filesystem_delete (require_approval) listed antes que read_only en DEFAULT
    action = xa.decide(["filesystem_delete", "read_only"], "critical",
                        xa.DEFAULT_POLICY)
    assert action == "require_approval"


def test_decide_unknown_intent_falls_to_default():
    custom_policy = {"default_action": "allow", "intent_rules": []}
    action = xa.decide(["custom_intent"], "low", custom_policy)
    assert action == "allow"


def test_load_policy_returns_default_when_no_file(tmp_path):
    # Cambiar directorio para evitar .xdd local
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        p = xa.load_policy(None)
        assert p["default_action"] == "allow"
        assert len(p["intent_rules"]) >= 5
    finally:
        os.chdir(old)


def test_cmd_check_secret_access_returns_2(capsys):
    rc = xa.cmd_check(_Args(tool="Read", args='{"path": "/home/x/.env"}',
                              intent=None, json=True, policy=None))
    assert rc == 2
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "deny"


def test_cmd_check_read_only_returns_0(capsys):
    rc = xa.cmd_check(_Args(tool="Read", args='{"file_path": "/tmp/safe.md"}',
                              intent=None, json=True, policy=None))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "allow"


def test_cmd_check_elapsed_under_100ms(capsys):
    xa.cmd_check(_Args(tool="Read", args='{"file_path": "/tmp/x"}',
                        intent=None, json=True, policy=None))
    out = json.loads(capsys.readouterr().out)
    assert out["elapsed_ms"] < 100  # OAP target


def test_cmd_policy_validate_default():
    rc = xa.cmd_policy(_Args(show=False, validate=True, json=False, policy=None))
    assert rc == 0
