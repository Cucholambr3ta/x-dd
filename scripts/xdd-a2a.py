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

import argparse  # kept for type hints
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version  # noqa: E402

__version__ = read_version()

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
    """S18: servidor HTTP A2A real con stdlib http.server (ADR-0030, v0.2.0).

    Endpoints:
      GET  /.well-known/agent     → Agent Card JSON
      POST /                      → JSON-RPC: agent/invoke, agent/list
    No deps externas (stdlib pura). Solo bind a 127.0.0.1 por defecto (sin TLS).
    """
    import http.server
    import urllib.parse

    root = Path(__file__).resolve().parent.parent

    class A2AHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt, *a):
            print(f"[a2a] {self.address_string()} {fmt % a}")

        def _send_json(self, data: dict, code: int = 200):
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path
            if path in ("/.well-known/agent", "/.well-known/agent.json"):
                try:
                    import importlib.util as _iu
                    _sp = _iu.spec_from_file_location("a2a", str(root / "scripts" / "xdd-a2a.py"))
                    _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
                    card = _m.build_agent_card()
                except Exception as e:
                    self._send_json({"error": str(e)}, 500); return
                self._send_json(card)
            else:
                self._send_json({"error": "not found"}, 404)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                req = json.loads(body)
            except json.JSONDecodeError:
                self._send_json({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}); return
            rid = req.get("id")
            method = req.get("method", "")
            params = req.get("params", {})
            if method == "agent/invoke":
                agent_id = params.get("agent") or params.get("agent_id", "?")
                result = {"agent_id": agent_id, "status": "delegated",
                          "note": "Invoke via xdd-orchestrate run --pattern=... --exec"}
                self._send_json({"jsonrpc": "2.0", "result": result, "id": rid})
            elif method in ("agent/list", "agents/list"):
                try:
                    import importlib.util as _iu
                    _sp = _iu.spec_from_file_location("a2a", str(root / "scripts" / "xdd-a2a.py"))
                    _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
                    patterns = _m.load_patterns()
                except Exception:
                    patterns = []
                self._send_json({"jsonrpc": "2.0", "result": {"agents": patterns}, "id": rid})
            else:
                self._send_json({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": rid,
                }, 404)

    addr = (args.bind, args.port)
    server = http.server.HTTPServer(addr, A2AHandler)
    print(f"[a2a] A2A server running on http://{args.bind}:{args.port}")
    print(f"[a2a]   GET /.well-known/agent  — Agent Card")
    print(f"[a2a]   POST /                  — JSON-RPC (agent/invoke, agent/list)")
    print(f"[a2a]   Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[a2a] server stopped.")
    return 0


def build_parser():
    p, sub = make_parser("xdd-a2a", __doc__, raw_description=True, short_version_flag=False)

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
