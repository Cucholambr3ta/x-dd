"""Tests for xdd-mcp-server (Sprint 6).

Run: pytest tests/test_mcp_server.py -v
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# El paquete tiene guion en el nombre → import vía importlib.
SERVER_MOD = importlib.import_module("xdd-mcp-server.server")
TOOLS_MOD = importlib.import_module("xdd-mcp-server.tools")
MAIN_MOD = importlib.import_module("xdd-mcp-server.__main__")


# ---------- Dispatcher protocol ----------

def test_initialize_returns_server_info():
    msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    resp = SERVER_MOD.dispatch(msg)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    info = resp["result"]["serverInfo"]
    assert info["name"] == "xdd-mcp-server"
    assert "version" in info
    assert resp["result"]["protocolVersion"] == SERVER_MOD.PROTOCOL_VERSION


def test_tools_list_returns_six_tools():
    msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    resp = SERVER_MOD.dispatch(msg)
    names = [t["name"] for t in resp["result"]["tools"]]
    assert len(names) == 6
    assert "xdd_validate_phase" in names
    assert "xdd_transition_phase" in names
    assert "xdd_list_workflows" in names
    assert "xdd_invoke_workflow" in names
    assert "xdd_list_agents" in names
    assert "xdd_get_phase_artifacts" in names


def test_unknown_method_returns_error():
    msg = {"jsonrpc": "2.0", "id": 99, "method": "nonexistent/method"}
    resp = SERVER_MOD.dispatch(msg)
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_notifications_initialized_returns_none():
    """Las notifications no responden."""
    msg = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert SERVER_MOD.dispatch(msg) is None


def test_unknown_tool_returns_error():
    msg = {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
           "params": {"name": "evil_tool", "arguments": {}}}
    resp = SERVER_MOD.dispatch(msg)
    assert "error" in resp
    assert resp["error"]["code"] == -32602


def test_invalid_arguments_returns_error():
    msg = {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
           "params": {"name": "xdd_list_agents",
                      "arguments": {"unknown_arg": "x"}}}
    resp = SERVER_MOD.dispatch(msg)
    assert "error" in resp


# ---------- Individual tools ----------

def test_list_workflows_finds_real_workflows():
    result = TOOLS_MOD.xdd_list_workflows()
    assert result["count"] > 40   # tenemos 49+ workflows
    names = [w["name"] for w in result["workflows"]]
    assert "xdd-build" in names
    assert "qa-review" in names


def test_list_agents_unfiltered_returns_180():
    result = TOOLS_MOD.xdd_list_agents()
    assert result["ok"] is True
    assert result["count"] == 180


def test_list_agents_filtered_by_category():
    result = TOOLS_MOD.xdd_list_agents(category="security")
    assert result["ok"] is True
    assert all(a["category"] == "security" for a in result["agents"])


def test_invoke_workflow_returns_content():
    result = TOOLS_MOD.xdd_invoke_workflow("xdd-build")
    assert result["ok"] is True
    assert "content" in result
    assert "note" in result   # confirma que NO se ejecuta


def test_invoke_workflow_rejects_invalid_name():
    result = TOOLS_MOD.xdd_invoke_workflow("../../../etc/passwd")
    assert result["ok"] is False


def test_invoke_workflow_rejects_missing():
    result = TOOLS_MOD.xdd_invoke_workflow("nonexistent-workflow")
    assert result["ok"] is False


def test_get_phase_artifacts_briefing():
    result = TOOLS_MOD.xdd_get_phase_artifacts("briefing")
    assert result["ok"] is True
    paths = [a["path"] for a in result["artifacts"]]
    assert all(p.startswith(".xdd/") for p in paths)   # T4.3 mitigación


def test_get_phase_artifacts_unknown_phase():
    result = TOOLS_MOD.xdd_get_phase_artifacts("invalid")
    assert result["ok"] is False


def test_validate_phase_via_dispatcher():
    msg = {"jsonrpc": "2.0", "id": 10, "method": "tools/call",
           "params": {"name": "xdd_validate_phase",
                      "arguments": {"phase": "briefing"}}}
    resp = SERVER_MOD.dispatch(msg)
    assert "result" in resp
    payload = json.loads(resp["result"]["content"][0]["text"])
    assert payload["phase"] == "briefing"
    assert "ok" in payload


def test_transition_phase_non_sequential():
    result = TOOLS_MOD.xdd_transition_phase("briefing", "build")
    assert result["ok"] is False
    assert "secuencial" in result["error"]


# ---------- Smoke test del check ----------

def test_check_main_returns_zero(capsys):
    rc = MAIN_MOD.main(["--check"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["server"] == "xdd-mcp-server"
    assert len(data["tools"]) == 6
