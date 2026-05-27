#!/usr/bin/env python3
"""xdd-orchestrate.py — Multi-agent orchestration runtime (Sprint 11).

Ejecuta composition_patterns del registry tipado (Sprint 5).
Patterns: sequential, parallel, parallel_then_sync.

Comandos:
  list                       — lista composition_patterns disponibles
  run --pattern=NAME         — ejecuta pattern (modo dry-run por defecto)
  run --pattern=NAME --exec  — modo execute (invoca workflows reales vía MCP)
  status                     — orchestrations en curso (lee state SQLite Sprint 9)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0-dev"
ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "prompts" / "agents" / "registry.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict:
    if not REGISTRY.exists():
        print(f"[orch] {REGISTRY} no existe. Corré migrate-agents-to-registry.py",
              file=sys.stderr)
        sys.exit(2)
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def find_pattern(reg: dict, name: str) -> dict | None:
    for p in reg.get("composition_patterns", []):
        if p["name"] == name:
            return p
    return None


def find_agent(reg: dict, agent_id: str) -> dict | None:
    for a in reg.get("agents", []):
        if a["id"] == agent_id:
            return a
    return None


def invoke_agent_dry(agent: dict, run_id: str) -> dict:
    """Dry-run: no ejecuta, registra intent."""
    return {
        "agent_id": agent["id"],
        "name": agent["name"],
        "category": agent["category"],
        "prompt_file": agent["prompt_file"],
        "invocation": "DRY-RUN",
        "run_id": run_id,
        "timestamp": utcnow(),
    }


def invoke_agent_exec(agent: dict, run_id: str) -> dict:
    """Execute: invoca workflow real vía MCP server propio (Sprint 6).

    En v0.1.0, esto es un stub que solo confirma que el agente y su prompt_file
    existen. La invocación real (LLM call) la hace el orquestador (Claude
    Code, OpenCode, etc.) cuando recibe la tool call vía MCP.
    """
    pf = ROOT / agent["prompt_file"]
    exists = pf.exists()
    return {
        "agent_id": agent["id"],
        "name": agent["name"],
        "prompt_file": str(pf.relative_to(ROOT)),
        "exists": exists,
        "invocation": "EXEC_DELEGATED_TO_ORCHESTRATOR",
        "note": "Real LLM invocation happens via MCP server in your orchestrator (Claude Code/OpenCode/etc).",
        "run_id": run_id,
        "timestamp": utcnow(),
    }


def run_sequential(pattern: dict, reg: dict, run_id: str, exec_mode: bool) -> list:
    invoker = invoke_agent_exec if exec_mode else invoke_agent_dry
    results = []
    lead = find_agent(reg, pattern["lead"])
    if lead:
        results.append({"role": "lead", "result": invoker(lead, run_id)})
    for sp_id in pattern.get("specialists", []):
        sp = find_agent(reg, sp_id)
        if sp:
            results.append({"role": "specialist", "result": invoker(sp, run_id)})
    return results


def run_parallel(pattern: dict, reg: dict, run_id: str, exec_mode: bool) -> list:
    invoker = invoke_agent_exec if exec_mode else invoke_agent_dry
    results = []
    lead = find_agent(reg, pattern["lead"])
    specialists = [find_agent(reg, sp) for sp in pattern.get("specialists", [])]
    specialists = [s for s in specialists if s]

    if lead:
        results.append({"role": "lead", "result": invoker(lead, run_id)})

    with ThreadPoolExecutor(max_workers=min(len(specialists) or 1, 5)) as ex:
        futs = {ex.submit(invoker, sp, run_id): sp for sp in specialists}
        for fut in as_completed(futs):
            results.append({"role": "specialist", "result": fut.result()})
    return results


def run_parallel_then_sync(pattern: dict, reg: dict, run_id: str, exec_mode: bool) -> list:
    """Parallel hasta sync_point, luego continúa (v0.1.0 = solo paralelo).
    Sprint 12+ puede añadir gates de sincronización formales."""
    results = run_parallel(pattern, reg, run_id, exec_mode)
    results.append({
        "role": "sync_point",
        "sync_at": pattern.get("sync_point"),
        "note": "v0.1.0: sync point sólo registra; gates formales en Sprint 12+",
    })
    return results


ORCHESTRATIONS = {
    "sequential": run_sequential,
    "parallel": run_parallel,
    "parallel_then_sync": run_parallel_then_sync,
}


def cmd_list(args):
    reg = load_registry()
    patterns = reg.get("composition_patterns", [])
    if args.json:
        print(json.dumps({"patterns": patterns}, indent=2))
    else:
        print(f"[orch] {len(patterns)} composition_patterns:")
        for p in patterns:
            sps = ", ".join(p["specialists"])
            print(f"  - {p['name']:<20} lead={p['lead']:<35} orch={p['orchestration']}")
            print(f"      specialists: {sps}")
            if p.get("description"):
                print(f"      {p['description']}")
    return 0


def cmd_run(args):
    reg = load_registry()
    pattern = find_pattern(reg, args.pattern)
    if not pattern:
        print(f"[orch] pattern '{args.pattern}' no existe", file=sys.stderr)
        return 2

    orch_type = pattern["orchestration"]
    if orch_type not in ORCHESTRATIONS:
        print(f"[orch] orchestration type '{orch_type}' no soportada", file=sys.stderr)
        return 2

    run_id = f"run_{hashlib.sha256(f'{args.pattern}::{utcnow()}'.encode()).hexdigest()[:12]}"
    start = time.time()
    results = ORCHESTRATIONS[orch_type](pattern, reg, run_id, args.exec)
    elapsed = round(time.time() - start, 3)

    report = {
        "run_id": run_id,
        "pattern": args.pattern,
        "orchestration": orch_type,
        "exec_mode": args.exec,
        "elapsed_seconds": elapsed,
        "steps": results,
        "timestamp_start": utcnow(),
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[orch] {run_id} pattern={args.pattern} type={orch_type} "
              f"exec={args.exec} elapsed={elapsed}s")
        for s in results:
            role = s["role"]
            r = s.get("result", {})
            print(f"  [{role:<11}] {r.get('agent_id', s.get('note',''))}")
    return 0


def cmd_status(args):
    """Lee state SQLite (Sprint 9) si existe, para mostrar orchestrations en curso."""
    import os
    state_db = Path(os.environ.get("XDD_STATE_DB", Path.home() / ".xdd" / "state.db"))
    if not state_db.exists():
        print(f"[orch] state DB no existe ({state_db}). Sprint 9 no aplicado.")
        return 0
    print(f"[orch] state DB: {state_db}")
    print("[orch] runtime tracking de orchestrations llega en Sprint 12+ (eval-harness integration)")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-orchestrate",
        description="Multi-agent orchestration runtime (Sprint 11).")
    p.add_argument("-v", "--version", action="version", version=f"xdd-orchestrate v{__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_l = sub.add_parser("list", help="Lista composition_patterns")
    p_l.add_argument("--json", action="store_true")
    p_l.set_defaults(func=cmd_list)

    p_r = sub.add_parser("run", help="Ejecuta un composition_pattern")
    p_r.add_argument("--pattern", required=True)
    p_r.add_argument("--exec", action="store_true",
                      help="Modo execute (default: dry-run)")
    p_r.add_argument("--json", action="store_true")
    p_r.set_defaults(func=cmd_run)

    p_s = sub.add_parser("status", help="Estado de orchestrations en curso")
    p_s.set_defaults(func=cmd_status)

    return p


def main(argv=None):
    return build_parser().parse_args(argv).func(build_parser().parse_args(argv))


if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(args.func(args))
