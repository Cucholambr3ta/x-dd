#!/usr/bin/env python3
"""xdd-a2a.py — Google A2A Protocol compat stub server (Sprint 23, ADR-0030).

A2A (Agent-to-Agent) JSON-RPC: expone composition_patterns como agents
discoverable via Agent Card.

Comandos:
  agent-card                              — emite Agent Card JSON (discoverable)
  list-patterns                           — lista composition_patterns como A2A agents
  serve --port=N [--bind=ADDR]            — corre stub server JSON-RPC
  invoke --agent=NAME --params=JSON       — JSON-RPC client-side test invocation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

__version__ = "0.1.0-dev"

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "prompts" / "agents" / "registry.json"


def load_registry() -> dict:
    if not REGISTRY.exists():
        return {"agents": [], "composition_patterns": []}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def emit_agent_card() -> dict:
    """A2A Agent Card spec: descriptor JSON discoverable via /.well-known/agent."""
    reg = load_registry()
    patterns = reg.get("composition_patterns", [])
    card = {
        "spec_version": "a2a/0.1",
        "name": "x-dd",
        "description": "X-DD framework exposes composition_patterns as A2A agents.",
        "version": "0.1.0",
        "endpoint": "/.well-known/agent",
        "capabilities": {
            "streaming": False,
            "tools": [
                {
                    "name": p["name"],
                    "description": f"Composition pattern: {p.get('orchestration', '?')} "
                                    f"with lead={p.get('lead', '?')} + N specialists",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "exec": {"type": "boolean", "default": False},
                        },
                    },
                }
                for p in patterns
            ],
        },
        "metadata": {
            "license": "MIT",
            "vendor": "X-DD",
            "url": "https://github.com/Cucholambr3ta/x-dd",
        },
    }
    return card


def cmd_agent_card(args):
    card = emit_agent_card()
    if args.pretty:
        print(json.dumps(card, indent=2))
    else:
        print(json.dumps(card))
    return 0


def cmd_list_patterns(args):
    reg = load_registry()
    patterns = reg.get("composition_patterns", [])
    if args.json:
        print(json.dumps(patterns, indent=2))
    else:
        print(f"[a2a] {len(patterns)} composition_patterns as A2A agents:")
        for p in patterns:
            print(f"  {p['name']:<22} orchestration={p.get('orchestration')}")
    return 0


def cmd_invoke(args):
    """JSON-RPC client-side test invocation (stub: usa orchestrator)."""
    reg = load_registry()
    pattern = next((p for p in reg.get("composition_patterns", [])
                     if p["name"] == args.agent), None)
    if not pattern:
        print(f"[a2a] ERROR: agent (pattern) not found: {args.agent}",
              file=sys.stderr)
        return 2
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "agent/invoke",
        "params": {
            "agent": args.agent,
            "input": json.loads(args.params) if args.params else {},
        },
    }
    response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "agent": args.agent,
            "pattern": pattern,
            "invocation": "DRY-RUN (stub: real exec via xdd-orchestrate)",
            "next_step": f"python3 scripts/xdd-orchestrate.py run --pattern={args.agent} --exec",
        },
    }
    print(json.dumps({"request": request, "response": response}, indent=2))
    return 0


def cmd_serve(args):
    """Stub: imprime ready-to-use snippet en vez de iniciar HTTP server real.
    Implementación HTTP server completa diferida a v0.2.0."""
    print(f"[a2a] stub serve mode (port={args.port})")
    print(f"[a2a] real HTTP server diferido a v0.2.0")
    print(f"[a2a] Recommended: use proxy + xdd-mcp-server (Sprint 6) hasta entonces")
    print(f"[a2a] Agent Card available via: python3 scripts/xdd-a2a.py agent-card")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-a2a", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-a2a {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_c = sub.add_parser("agent-card", help="Emit A2A Agent Card")
    p_c.add_argument("--pretty", action="store_true")
    p_c.set_defaults(func=cmd_agent_card)

    p_l = sub.add_parser("list-patterns", help="List patterns as A2A agents")
    p_l.add_argument("--json", action="store_true")
    p_l.set_defaults(func=cmd_list_patterns)

    p_s = sub.add_parser("serve", help="Serve A2A JSON-RPC (stub v0.1.0)")
    p_s.add_argument("--port", type=int, default=8500)
    p_s.add_argument("--bind", default="127.0.0.1")
    p_s.set_defaults(func=cmd_serve)

    p_i = sub.add_parser("invoke", help="JSON-RPC test invocation")
    p_i.add_argument("--agent", required=True)
    p_i.add_argument("--params", help="JSON")
    p_i.set_defaults(func=cmd_invoke)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
