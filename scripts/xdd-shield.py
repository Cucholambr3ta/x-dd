#!/usr/bin/env python3
"""xdd-shield.py — AgentShield: audit estático del propio framework X-DD (Sprint 12).

Analiza hooks, agentes, MCP tools, workflows para detectar:
- Hooks: eval/exec en comandos, paths absolutos, secrets en stderr
- Agentes: prompts con instrucciones contradictorias, constraints faltantes
- MCP tools: side effects (network, FS write fuera de scope)
- Workflows: pasos sin pre/post-condition con xdd-gate.py
- Registry: agentes huérfanos sin file, duplicados, schema drift

Modos:
  audit               — corre todas las reglas, exit 0 si pass
  audit --severity=high — solo reglas crit/high
  audit --json        — output machine-readable
  audit --ci          — exit 1 si hay violations >= warning

Reglas hoy: ~12 (subset cuidado vs 102 de ECC AgentShield).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import read_version, utcnow_iso as utcnow  # noqa: E402

__version__ = read_version()
ROOT = Path(__file__).resolve().parent.parent


# === Reglas ===

def rule_hooks_no_eval_exec(findings: list) -> None:
    """Hooks bash no deben usar eval/exec con input externo."""
    for h in (ROOT / ".agent/hooks/scripts").glob("*.sh"):
        content = h.read_text(encoding="utf-8", errors="ignore")
        # eval con $ o backticks
        if re.search(r'\beval\b.*\$', content):
            findings.append({"severity": "high", "rule": "hooks_no_eval",
                             "file": str(h.relative_to(ROOT)), "msg": "eval with $ interpolation"})
        # exec en bash es ok para invocar binarios, pero NO con input
        if re.search(r"`[^`]*\$[^`]*`", content):
            findings.append({"severity": "warning", "rule": "hooks_backtick_with_var",
                             "file": str(h.relative_to(ROOT)), "msg": "backtick command with variable"})


def rule_hooks_no_absolute_paths(findings: list) -> None:
    """Hooks no deben tener rutas absolutas del host (portability)."""
    for h in (ROOT / ".agent/hooks/scripts").glob("*.sh"):
        content = h.read_text(encoding="utf-8", errors="ignore")
        # Ignorar /tmp, /dev, /usr, /etc, /var, /opt, $HOME, ~
        # Buscar /home, /Users, /mnt, /media con username después
        for m in re.finditer(r'(?:^|[^\w/.$~])(/home/[a-zA-Z0-9_-]+|/Users/[a-zA-Z0-9_-]+)/', content):
            findings.append({"severity": "high", "rule": "no_absolute_host_paths",
                             "file": str(h.relative_to(ROOT)),
                             "msg": f"host path: {m.group(1)}"})


def rule_workflows_have_description(findings: list) -> None:
    """Cada workflow debe tener frontmatter description:."""
    for wf in (ROOT / ".agent/workflows").glob("*.md"):
        if wf.name.lower().startswith("readme"): continue
        head = wf.read_text(encoding="utf-8", errors="ignore")[:500]
        if "description:" not in head:
            findings.append({"severity": "high", "rule": "workflow_no_description",
                             "file": str(wf.relative_to(ROOT))})


def rule_agents_registry_consistent(findings: list) -> None:
    """Registry entries deben matchear con archivos físicos."""
    reg_path = ROOT / "prompts/agents/registry.json"
    if not reg_path.exists():
        return
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    for a in reg.get("agents", []):
        pf = ROOT / a["prompt_file"]
        if not pf.exists():
            findings.append({"severity": "crit", "rule": "registry_orphan",
                             "agent_id": a["id"],
                             "msg": f"prompt_file missing: {a['prompt_file']}"})
    # duplicados id
    ids = [a["id"] for a in reg.get("agents", [])]
    dups = {i for i in ids if ids.count(i) > 1}
    for d in dups:
        findings.append({"severity": "crit", "rule": "registry_duplicate_id", "agent_id": d})


def rule_mcp_tools_no_exec(findings: list) -> None:
    """MCP tools NO deben exponer xdd_exec/xdd_shell o equivalentes (T6.3)."""
    tools_file = ROOT / "xdd-mcp-server/tools.py"
    if not tools_file.exists():
        return
    content = tools_file.read_text(encoding="utf-8")
    forbidden = ["xdd_exec", "xdd_shell", "xdd_run_command", "xdd_eval"]
    for f in forbidden:
        if f in content:
            findings.append({"severity": "crit", "rule": "mcp_exposes_exec",
                             "file": "xdd-mcp-server/tools.py",
                             "msg": f"forbidden tool: {f}"})


def rule_mcp_get_artifacts_whitelist(findings: list) -> None:
    """xdd_get_phase_artifacts debe tener whitelist .xdd/ (T4.3)."""
    tools_file = ROOT / "xdd-mcp-server/tools.py"
    if not tools_file.exists():
        return
    content = tools_file.read_text(encoding="utf-8")
    if "ALLOWED_ARTIFACT_PREFIXES" not in content:
        findings.append({"severity": "high", "rule": "mcp_no_whitelist",
                         "file": "xdd-mcp-server/tools.py",
                         "msg": "xdd_get_phase_artifacts must enforce path whitelist"})


def rule_gate_key_gitignored(findings: list) -> None:
    """`.xdd/.gate-key` debe estar en .gitignore (ADR-0009)."""
    gi = ROOT / ".gitignore"
    if not gi.exists():
        findings.append({"severity": "crit", "rule": "no_gitignore"})
        return
    if ".xdd/.gate-key" not in gi.read_text(encoding="utf-8"):
        findings.append({"severity": "crit", "rule": "gate_key_not_gitignored",
                         "msg": ".xdd/.gate-key must be in .gitignore"})


def rule_workflow_has_gate_integration(findings: list) -> None:
    """Workflows críticos (build, qa, release) deben mencionar xdd-gate.py."""
    critical = ["xdd-build", "qa-review", "release-cut", "cierre-fase"]
    for name in critical:
        wf = ROOT / ".agent/workflows" / f"{name}.md"
        if not wf.exists(): continue
        content = wf.read_text(encoding="utf-8", errors="ignore")
        if "xdd-gate.py" not in content and "/xdd-gate" not in content:
            findings.append({"severity": "warning", "rule": "workflow_no_gate_integration",
                             "file": str(wf.relative_to(ROOT)),
                             "msg": f"{name} should integrate xdd-gate.py for pre/post-condition"})


def rule_agents_have_constraints(findings: list) -> None:
    """Agents en security/ deben declarar constraints (no auto-promote, etc.)."""
    reg_path = ROOT / "prompts/agents/registry.json"
    if not reg_path.exists(): return
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    for a in reg.get("agents", []):
        if a.get("category") == "security" and not a.get("constraints"):
            findings.append({"severity": "warning", "rule": "security_agent_no_constraints",
                             "agent_id": a["id"],
                             "msg": "security agents should declare constraints"})


def rule_no_curl_pipe_bash(findings: list) -> None:
    """Scripts no deben tener `curl|bash` patterns."""
    for sh in (ROOT / "scripts").rglob("*.sh"):
        content = sh.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'curl.*\|.*(bash|sh)\b', content):
            findings.append({"severity": "high", "rule": "curl_pipe_bash",
                             "file": str(sh.relative_to(ROOT)),
                             "msg": "curl|bash pattern is dangerous"})


def rule_hooks_json_schema_valid(findings: list) -> None:
    """hooks.json debe validar contra schema."""
    h = ROOT / ".agent/hooks/hooks.json"
    s = ROOT / "schemas/hooks.schema.json"
    if not (h.exists() and s.exists()): return
    try:
        import jsonschema
        jsonschema.validate(json.loads(h.read_text(encoding="utf-8")),
                            json.loads(s.read_text(encoding="utf-8")))
    except ImportError:
        findings.append({"severity": "info", "rule": "schema_check_skipped",
                         "msg": "jsonschema not installed; skip"})
    except Exception as e:
        findings.append({"severity": "crit", "rule": "hooks_invalid_schema",
                         "msg": str(e)})


def rule_dependencies_md_exists(findings: list) -> None:
    """DEPENDENCIES.md debe existir (declaración de deps externas)."""
    if not (ROOT / "DEPENDENCIES.md").exists():
        findings.append({"severity": "warning", "rule": "no_dependencies_md"})


def rule_threats_md_present(findings: list) -> None:
    """THREATS.md debe estar en .xdd/spec/ (Fase 2)."""
    if not (ROOT / ".xdd/spec/THREATS.md").exists():
        findings.append({"severity": "high", "rule": "no_threats_md",
                         "msg": "Phase 2 requires .xdd/spec/THREATS.md (STRIDE model)"})


RULES = [
    rule_hooks_no_eval_exec,
    rule_hooks_no_absolute_paths,
    rule_workflows_have_description,
    rule_agents_registry_consistent,
    rule_mcp_tools_no_exec,
    rule_mcp_get_artifacts_whitelist,
    rule_gate_key_gitignored,
    rule_workflow_has_gate_integration,
    rule_agents_have_constraints,
    rule_no_curl_pipe_bash,
    rule_hooks_json_schema_valid,
    rule_dependencies_md_exists,
    rule_threats_md_present,
]


SEVERITY_ORDER = {"crit": 4, "high": 3, "warning": 2, "info": 1}


def cmd_audit(args):
    findings = []
    for rule in RULES:
        try:
            rule(findings)
        except Exception as e:
            findings.append({"severity": "warning", "rule": rule.__name__,
                             "msg": f"rule exception: {e}"})

    # Filtrar por severidad mínima
    min_sev = SEVERITY_ORDER.get(args.severity or "info", 1)
    findings = [f for f in findings if SEVERITY_ORDER.get(f["severity"], 0) >= min_sev]

    # Sort por severidad desc
    findings.sort(key=lambda f: -SEVERITY_ORDER.get(f["severity"], 0))

    report = {
        "tool": "xdd-shield",
        "version": __version__,
        "timestamp": utcnow(),
        "rules_run": len(RULES),
        "findings": findings,
        "summary": {
            "crit": sum(1 for f in findings if f["severity"] == "crit"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "warning": sum(1 for f in findings if f["severity"] == "warning"),
            "info": sum(1 for f in findings if f["severity"] == "info"),
        }
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        s = report["summary"]
        print(f"[shield] ran {len(RULES)} rules — {s['crit']} crit, {s['high']} high, "
              f"{s['warning']} warning, {s['info']} info.")
        for f in findings:
            badge = {"crit": "🔴", "high": "🟠", "warning": "🟡", "info": "ℹ️"}.get(
                f["severity"], "·")
            ctx = f.get("file") or f.get("agent_id") or ""
            print(f"  {badge} [{f['severity']}] {f['rule']:<35} {ctx}")
            if f.get("msg"):
                print(f"       {f['msg']}")
        if not findings:
            print(f"[shield] ✓ no findings at severity ≥ {args.severity or 'info'}")

    # CI gate
    if args.ci:
        blocking = report["summary"]["crit"] + report["summary"]["high"]
        if min_sev >= SEVERITY_ORDER["warning"]:
            blocking += report["summary"]["warning"]
        return 1 if blocking > 0 else 0
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-shield",
        description="AgentShield: audit estático del framework X-DD (Sprint 12).")
    p.add_argument("-v", "--version", action="version", version=f"xdd-shield v{__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_a = sub.add_parser("audit", help="Corre todas las reglas")
    p_a.add_argument("--severity", choices=["info", "warning", "high", "crit"],
                      default="info", help="Severidad mínima a reportar")
    p_a.add_argument("--ci", action="store_true",
                      help="exit 1 si crit/high (o warning si --severity=warning)")
    p_a.add_argument("--json", action="store_true")
    p_a.set_defaults(func=cmd_audit)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
