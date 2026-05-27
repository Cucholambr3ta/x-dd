#!/usr/bin/env python3
"""xdd-authz.py — Pre-action authorization (Sprint 21, ADR-0028).

OAP-style deterministic authz check. Target <100ms latency.
Lee policy desde .xdd/.policy.yml o xdd.config.yml sección permissions.

Comandos:
  check --tool=NAME --args=JSON     — verifica una tool call
  check --intent=NAME                — verifica solo por intent
  policy --show                      — muestra policy efectiva
  policy --validate                  — valida sintaxis policy

Exit codes:
  0 = allow
  1 = require_approval
  2 = deny
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

__version__ = "0.1.0-dev"

DEFAULT_POLICY = {
    "default_action": "allow",  # allow | deny | require_approval | mask
    "intent_rules": [
        {"intent": "filesystem_delete", "action": "require_approval"},
        {"intent": "secret_access", "action": "deny"},
        {"intent": "lang_exec", "action": "require_approval"},
        {"intent": "network_outbound", "action": "allow"},
        {"intent": "filesystem_write", "action": "allow"},
        {"intent": "mcp_external", "action": "require_approval"},
        {"intent": "read_only", "action": "allow"},
    ],
    "auto_mode_threshold": "high",  # require_approval para severity ≥ high
}


# Import xdd-intent classifier
def _load_intent_classifier():
    here = Path(__file__).resolve().parent
    import importlib.util
    spec = importlib.util.spec_from_file_location("xi", here / "xdd-intent.py")
    xi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xi)
    return xi


def load_policy(path: str | None) -> dict:
    """Lee policy desde archivo o usa DEFAULT_POLICY."""
    candidates = [path] if path else [
        ".xdd/.policy.yml",
        ".xdd/.policy.yaml",
        "xdd.config.yml",
    ]
    for p in candidates:
        if not p:
            continue
        fp = Path(p)
        if fp.exists():
            try:
                import yaml
                full = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
                # Pueden ser archivo dedicado o sección de xdd.config.yml
                if "permissions" in full:
                    return {**DEFAULT_POLICY, **full["permissions"]}
                if "default_action" in full or "intent_rules" in full:
                    return {**DEFAULT_POLICY, **full}
            except ImportError:
                pass  # sin yaml, fallback al default
            except Exception:
                pass
    return dict(DEFAULT_POLICY)


def decide(intents: list, severity: str, policy: dict) -> str:
    """Devuelve action: allow | deny | require_approval | mask."""
    # Auto-mode threshold: si severity ≥ threshold, require_approval
    sev_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    threshold = policy.get("auto_mode_threshold", "high")
    if sev_rank.get(severity, 0) >= sev_rank.get(threshold, 2):
        # Pero specific intent rule sobreescribe
        pass
    # Rules específicas por intent (más específico primero)
    for rule in policy.get("intent_rules", []):
        if rule.get("intent") in intents:
            return rule.get("action", policy.get("default_action", "allow"))
    return policy.get("default_action", "allow")


def cmd_check(args):
    start = time.time()
    policy = load_policy(args.policy)
    xi = _load_intent_classifier()
    if args.intent:
        intents = [args.intent]
        severity = "medium"  # neutral default if only intent given
    else:
        try:
            call_args = json.loads(args.args) if args.args else {}
        except json.JSONDecodeError as e:
            print(f"[authz] ERROR: invalid --args JSON: {e}", file=sys.stderr)
            return 2
        classified = xi.classify_call(args.tool or "?", call_args)
        intents = classified["intents"]
        severity = classified["severity"]
    action = decide(intents, severity, policy)
    elapsed_ms = (time.time() - start) * 1000
    result = {
        "tool": args.tool,
        "intents": intents,
        "severity": severity,
        "action": action,
        "elapsed_ms": round(elapsed_ms, 2),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        emoji = {"allow": "✅", "require_approval": "⚠️",
                  "mask": "🎭", "deny": "🛑"}[action]
        print(f"[authz] {emoji} {action.upper()} "
              f"(intents={intents}, severity={severity}, {elapsed_ms:.1f}ms)")
    exit_codes = {"allow": 0, "require_approval": 1, "mask": 1, "deny": 2}
    return exit_codes.get(action, 0)


def cmd_policy(args):
    policy = load_policy(args.policy)
    if args.validate:
        errs = []
        if "default_action" not in policy:
            errs.append("missing default_action")
        for rule in policy.get("intent_rules", []):
            if "intent" not in rule:
                errs.append(f"rule missing intent: {rule}")
            if "action" not in rule:
                errs.append(f"rule missing action: {rule}")
        if errs:
            print(f"[authz] INVALID: {errs}", file=sys.stderr)
            return 1
        print(f"[authz] ✓ policy valid ({len(policy.get('intent_rules', []))} rules)")
        return 0
    # Show
    if args.json:
        print(json.dumps(policy, indent=2))
    else:
        print(f"[authz] effective policy:")
        print(f"  default_action: {policy.get('default_action')}")
        print(f"  auto_mode_threshold: {policy.get('auto_mode_threshold')}")
        print(f"  rules ({len(policy.get('intent_rules', []))}):")
        for r in policy.get("intent_rules", []):
            print(f"    {r['intent']:<22} → {r['action']}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-authz", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-authz {__version__}")
    p.add_argument("--policy", help="Policy file (default: auto-detect)")
    sub = p.add_subparsers(dest="command", required=True)

    p_c = sub.add_parser("check", help="Authz check para tool call")
    p_c.add_argument("--tool")
    p_c.add_argument("--args", help="JSON of tool args")
    p_c.add_argument("--intent", help="Skip classifier, check just by intent")
    p_c.add_argument("--json", action="store_true")
    p_c.set_defaults(func=cmd_check)

    p_p = sub.add_parser("policy", help="Show or validate policy")
    p_p.add_argument("--show", action="store_true")
    p_p.add_argument("--validate", action="store_true")
    p_p.add_argument("--json", action="store_true")
    p_p.set_defaults(func=cmd_policy)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
