#!/usr/bin/env python3
"""xdd-intent.py — Intent taxonomy classifier (Sprint 21, ADR-0028).

Clasifica tool calls según taxonomía de riesgo (nah-style, ai-boost inspirada).

Intents:
  filesystem_delete    — rm, unlink, rmtree, drop table
  filesystem_write     — write file fuera de scope normal
  network_outbound     — curl, wget, http requests
  lang_exec            — eval, exec, subprocess
  secret_access        — read .env, credentials, ssh keys
  fork_subprocess      — spawn child processes
  mcp_external         — MCP tool de server no-trusted
  read_only            — solo lectura, baseline safe

Comandos:
  classify --tool=NAME --args=JSON     — clasifica una tool call
  taxonomy                              — lista intents + descriptions
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import read_version  # noqa: E402

__version__ = read_version()


# Pattern → intent. Order matters (first match wins; more specific first).
INTENT_PATTERNS = [
    # filesystem_delete: highest danger
    ("filesystem_delete", [
        r"\brm\b.*-rf?\b",
        r"\bunlink\b",
        r"\brmtree\b",
        r"\bdelete\b.*\bfrom\b",
        r"\bdrop\s+table\b",
        r"\btruncate\s+table\b",
    ]),
    # secret_access
    ("secret_access", [
        r"\.env\b",
        r"\.envrc\b",
        r"credentials?\.(json|yaml|yml)",
        r"\.ssh/(id_rsa|id_ed25519)",
        r"\.aws/credentials",
        r"\.gitconfig.*user\.email",
    ]),
    # network_outbound
    ("network_outbound", [
        r"\bcurl\b",
        r"\bwget\b",
        r"https?://(?!localhost|127\.0\.0\.1)",
        r"\bfetch\(",
        r"\bnc\b.*\s\d{2,}",
    ]),
    # lang_exec
    ("lang_exec", [
        r"\beval\(",
        r"\bexec\(",
        r"subprocess\.(call|run|Popen)",
        r"os\.system\(",
        r"shell=True",
    ]),
    # fork_subprocess
    ("fork_subprocess", [
        r"\bfork\(",
        r"spawn\b",
        r"&\s*$",
        r"\bnohup\b",
    ]),
    # filesystem_write (catch-all if writes)
    ("filesystem_write", [
        r">\s*\S+\.\w+",
        r">>\s*\S+",
    ]),
    # mcp_external — heuristic for MCP tool names
    ("mcp_external", [
        r"^mcp_(?!claude_ai_)",  # claude_ai_ prefix = trusted built-in
    ]),
]


# Tool name to default intent if pattern not specific enough
TOOL_DEFAULT_INTENT = {
    "Read": "read_only",
    "Glob": "read_only",
    "Grep": "read_only",
    "WebFetch": "network_outbound",
    "WebSearch": "network_outbound",
    "Bash": "lang_exec",  # default to exec, refined by args
    "Edit": "filesystem_write",
    "Write": "filesystem_write",
    "NotebookEdit": "filesystem_write",
}


def classify_call(tool: str, args: dict) -> dict:
    """Devuelve {intents: [...], severity: low|medium|high|critical, rationale: ...}."""
    matched = []
    # Combine all args into searchable text
    text = f"{tool} " + json.dumps(args, default=str)
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                if intent not in matched:
                    matched.append(intent)
                break  # next intent
    # Tool default if no pattern matched
    if not matched:
        default_intent = TOOL_DEFAULT_INTENT.get(tool, "read_only")
        matched = [default_intent]
    severity_map = {
        "filesystem_delete": "critical",
        "secret_access": "critical",
        "lang_exec": "high",
        "fork_subprocess": "high",
        "network_outbound": "medium",
        "filesystem_write": "medium",
        "mcp_external": "medium",
        "read_only": "low",
    }
    max_sev = max((severity_map.get(i, "low") for i in matched),
                   key=lambda s: ["low", "medium", "high", "critical"].index(s))
    rationale = f"matched intents: {matched}; tool={tool}"
    return {
        "tool": tool,
        "intents": matched,
        "severity": max_sev,
        "rationale": rationale,
    }


def cmd_classify(args):
    try:
        call_args = json.loads(args.args) if args.args else {}
    except json.JSONDecodeError as e:
        print(f"[intent] ERROR: invalid --args JSON: {e}", file=sys.stderr)
        return 2
    result = classify_call(args.tool, call_args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        emoji = {"low": "✅", "medium": "⚠️", "high": "🔶", "critical": "🛑"}[result["severity"]]
        print(f"[intent] {emoji} {result['severity'].upper()}: {result['intents']}")
        print(f"  tool: {result['tool']}")
        print(f"  rationale: {result['rationale']}")
    return 0


def cmd_taxonomy(args):
    out = []
    descriptions = {
        "filesystem_delete": "Borrar archivos/tablas (CRITICAL)",
        "filesystem_write": "Escribir archivos fuera de scope típico",
        "network_outbound": "Tráfico de red saliente (no localhost)",
        "lang_exec": "Ejecución de código dinámico (eval/exec/subprocess)",
        "secret_access": "Acceso a archivos con credenciales",
        "fork_subprocess": "Spawn de child processes / nohup",
        "mcp_external": "MCP tool de server externo no-trusted",
        "read_only": "Sólo lectura, baseline seguro",
    }
    for intent, desc in descriptions.items():
        out.append({"intent": intent, "description": desc})
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print("[intent] taxonomy:")
        for i in out:
            print(f"  {i['intent']:<22} {i['description']}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-intent", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-intent {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_c = sub.add_parser("classify", help="Classify a tool call")
    p_c.add_argument("--tool", required=True)
    p_c.add_argument("--args", help="JSON of tool args")
    p_c.add_argument("--json", action="store_true")
    p_c.set_defaults(func=cmd_classify)

    p_t = sub.add_parser("taxonomy", help="List intent taxonomy")
    p_t.add_argument("--json", action="store_true")
    p_t.set_defaults(func=cmd_taxonomy)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
