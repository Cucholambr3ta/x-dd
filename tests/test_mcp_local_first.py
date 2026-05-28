"""Tests Sprint 25 + ADR-0035: tools.py local-first + global fallback resolvers."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("tools", ROOT / "xdd-mcp-server" / "tools.py")
tools = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(tools)


def test_resolve_project_root_default_is_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert tools._resolve_project_root() == tmp_path.resolve()


def test_resolve_project_root_explicit_overrides(tmp_path):
    assert tools._resolve_project_root(str(tmp_path)) == tmp_path.resolve()


def test_get_workflows_dir_local_first(tmp_path):
    local_wf = tmp_path / ".agent" / "workflows"
    local_wf.mkdir(parents=True)
    (local_wf / "custom.md").write_text("---\ndescription: local\n---\n")
    result = tools.get_workflows_dir(str(tmp_path))
    assert result == local_wf


def test_get_workflows_dir_global_fallback(tmp_path):
    # tmp_path no tiene .agent/workflows → fallback global
    result = tools.get_workflows_dir(str(tmp_path))
    assert result == tools.GLOBAL_WORKFLOWS_DIR


def test_get_registry_path_local_first(tmp_path):
    local_reg = tmp_path / "prompts" / "agents" / "registry.json"
    local_reg.parent.mkdir(parents=True)
    local_reg.write_text('{"agents": []}')
    result = tools.get_registry_path(str(tmp_path))
    assert result == local_reg


def test_get_registry_path_global_fallback(tmp_path):
    result = tools.get_registry_path(str(tmp_path))
    assert result == tools.GLOBAL_REGISTRY_PATH


def test_get_xdd_dir_always_local_no_fallback(tmp_path):
    """Sprint 25 ADR-0035: phase artifacts ESTRICTAMENTE per-project."""
    result = tools.get_xdd_dir(str(tmp_path))
    assert result == tmp_path / ".xdd"
    # Aun si no existe local — NO debe fallback a global
    assert result != tools.GLOBAL_WORKFLOWS_DIR.parent.parent / ".xdd"


def test_list_workflows_local_first_isolated(tmp_path):
    local_wf = tmp_path / ".agent" / "workflows"
    local_wf.mkdir(parents=True)
    (local_wf / "custom.md").write_text('---\ndescription: "custom local"\n---\n# /custom\n')
    out = tools.xdd_list_workflows(project_root=str(tmp_path))
    names = [w["name"] for w in out["workflows"]]
    assert "custom" in names
    assert out["is_local"] is True


def test_list_workflows_global_fallback_uses_repo_workflows():
    # Sin project_root con local → usa global (X-DD repo workflows)
    out = tools.xdd_list_workflows(project_root="/nonexistent/path/xyz")
    # Debería caer en global y devolver workflows del repo
    assert out["count"] > 0
    assert out["is_local"] is False


def test_invoke_workflow_local_takes_precedence(tmp_path):
    local_wf = tmp_path / ".agent" / "workflows"
    local_wf.mkdir(parents=True)
    (local_wf / "xdd.md").write_text("---\ndescription: LOCAL\n---\n# /xdd local\n")
    out = tools.xdd_invoke_workflow("xdd", project_root=str(tmp_path))
    assert out["ok"] is True
    assert out["is_local"] is True
    assert "LOCAL" in out["content"]


def test_get_phase_artifacts_strict_per_project(tmp_path):
    """No fallback global para phase artifacts (security: T4.3 + ADR-0035)."""
    out = tools.xdd_get_phase_artifacts("briefing", project_root=str(tmp_path))
    assert out["ok"] is True
    assert out["exists"] is False  # no .xdd/briefing/ en tmp_path
    assert out["project_root"] == str(tmp_path)


def test_get_phase_artifacts_reads_local(tmp_path):
    pdir = tmp_path / ".xdd" / "briefing"
    pdir.mkdir(parents=True)
    (pdir / "SPEC.md").write_text("spec content")
    (pdir / ".status").write_text("APROBADO")
    out = tools.xdd_get_phase_artifacts("briefing", project_root=str(tmp_path))
    assert out["ok"] is True
    assert out["exists"] is True
    assert out["status"] == "APROBADO"
    assert any("SPEC.md" in a["path"] for a in out["artifacts"])


def test_schemas_include_project_root_param():
    for tool_name in ("xdd_list_workflows", "xdd_invoke_workflow",
                       "xdd_list_agents", "xdd_get_phase_artifacts",
                       "xdd_validate_phase", "xdd_transition_phase"):
        schema = tools.TOOLS[tool_name]["schema"]
        props = schema["inputSchema"].get("properties", {})
        assert "project_root" in props, f"{tool_name} schema missing project_root"
