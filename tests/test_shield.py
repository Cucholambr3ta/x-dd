"""Tests para scripts/xdd-shield.py (Sprint 12)."""
from __future__ import annotations
import sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("xdd_shield", SCRIPTS / "xdd-shield.py")
shield = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shield)


def test_audit_runs_all_rules():
    findings = []
    for rule in shield.RULES:
        rule(findings)
    # Pase lo que pase, no debe haber crit en el repo X-DD actual
    crit = [f for f in findings if f["severity"] == "crit"]
    assert len(crit) == 0, f"Critical findings in own repo: {crit}"


def test_rule_no_curl_pipe_bash_in_scripts():
    findings = []
    shield.rule_no_curl_pipe_bash(findings)
    # En scripts/ propios no debe haber curl|bash
    relevant = [f for f in findings if f["severity"] == "high"]
    assert len(relevant) == 0


def test_rule_gate_key_gitignored():
    findings = []
    shield.rule_gate_key_gitignored(findings)
    assert len(findings) == 0, "`.xdd/.gate-key` must be gitignored"


def test_rule_mcp_no_exec():
    findings = []
    shield.rule_mcp_tools_no_exec(findings)
    assert len(findings) == 0, "MCP tools must NOT expose xdd_exec/shell"


def test_rule_mcp_has_whitelist():
    findings = []
    shield.rule_mcp_get_artifacts_whitelist(findings)
    assert len(findings) == 0


def test_rule_threats_md_present():
    findings = []
    shield.rule_threats_md_present(findings)
    assert len(findings) == 0


def test_rule_dependencies_md_exists():
    findings = []
    shield.rule_dependencies_md_exists(findings)
    assert len(findings) == 0


def test_rule_registry_consistent():
    findings = []
    shield.rule_agents_registry_consistent(findings)
    # No debe haber agentes huérfanos ni duplicados
    crit = [f for f in findings if f["severity"] == "crit"]
    assert len(crit) == 0


def test_rule_workflows_all_have_description():
    findings = []
    shield.rule_workflows_have_description(findings)
    assert len(findings) == 0


def test_severity_order():
    assert shield.SEVERITY_ORDER["crit"] > shield.SEVERITY_ORDER["high"]
    assert shield.SEVERITY_ORDER["high"] > shield.SEVERITY_ORDER["warning"]
    assert shield.SEVERITY_ORDER["warning"] > shield.SEVERITY_ORDER["info"]
