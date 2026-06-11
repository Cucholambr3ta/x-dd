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

import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version, utcnow_iso as utcnow  # noqa: E402

__version__ = read_version()
ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "prompts" / "agents" / "registry.json"


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
    """Execute: invoca el agente con LLM real vía AnthropicProvider (S7, v0.2).

    Sin ANTHROPIC_API_KEY o con XDD_PROVIDER_MOCK=1 (default): degrada a dry-run
    documentado (backwards-compatible). Con la key + XDD_PROVIDER_MOCK=0: llama
    al modelo especificado en el registry o claude-opus-4-8 por defecto.

    El prompt del agente se lee del prompt_file (SSoT). El sistema proporciona
    el contexto del run (run_id, category).
    """
    import importlib.util as _iu

    pf = ROOT / agent["prompt_file"]
    if not pf.exists():
        return {
            "agent_id": agent["id"],
            "name": agent["name"],
            "prompt_file": str(pf.relative_to(ROOT)),
            "invocation": "ERROR_PROMPT_NOT_FOUND",
            "run_id": run_id,
            "timestamp": utcnow(),
        }

    prompt = pf.read_text(encoding="utf-8")
    system = (
        f"Eres el agente '{agent['name']}' (categoría: {agent['category']}).\n"
        f"run_id: {run_id}. Aplica las directrices de tu prompt completo."
    )

    # Lazy-load provider (dep opcional; MockProvider si sin key/flag)
    try:
        _spec = _iu.spec_from_file_location("xdd_provider", ROOT / "scripts" / "xdd-provider.py")
        _pmod = _iu.module_from_spec(_spec)
        _spec.loader.exec_module(_pmod)
        provider = _pmod.get_provider(
            name=agent.get("preferred_provider", "anthropic"),
            model=agent.get("preferred_model", "claude-opus-4-8"),
        )
        invocation = "REAL_LLM"
    except Exception as e:
        # Degradación elegante: sin key / sin anthropic instalado → dry-run
        return {
            "agent_id": agent["id"],
            "name": agent["name"],
            "prompt_file": str(pf.relative_to(ROOT)),
            "invocation": "DRY_RUN_DEGRADED",
            "note": f"Provider no disponible ({e}). Instala x-dd[anthropic] y pon ANTHROPIC_API_KEY.",
            "run_id": run_id,
            "timestamp": utcnow(),
        }

    try:
        response = provider.complete(prompt, system=system)
    except Exception as e:
        response = f"[ERROR: {e}]"
        invocation = "REAL_LLM_ERROR"

    return {
        "agent_id": agent["id"],
        "name": agent["name"],
        "prompt_file": str(pf.relative_to(ROOT)),
        "invocation": invocation,
        "response_preview": response[:200],
        "response_len": len(response),
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
    """Parallel hasta sync_point con gate formal (S9, v0.2).

    1. Corre todos los agentes en paralelo.
    2. Espera con timeout que todos completen (futures.result() con timeout).
    3. Verifica que todos pasaron (no ERROR). Si fallan N → sync_status=failed.
    4. Registra el sync_point en xdd-state (best-effort).
    """
    sync_at = pattern.get("sync_point", "sync")
    timeout_s = pattern.get("sync_timeout_seconds", 300)

    # Correr paralelo con timeout real via ThreadPoolExecutor
    invoker = invoke_agent_exec if exec_mode else invoke_agent_dry
    results = []
    lead = find_agent(reg, pattern["lead"])
    if lead:
        results.append({"role": "lead", "result": invoker(lead, run_id)})

    specialists = [find_agent(reg, sp) for sp in pattern.get("specialists", [])]
    specialists = [s for s in specialists if s]

    with ThreadPoolExecutor(max_workers=min(len(specialists) or 1, 5)) as ex:
        futs = {ex.submit(invoker, sp, run_id): sp for sp in specialists}
        for fut in as_completed(futs, timeout=timeout_s):
            results.append({"role": "specialist", "result": fut.result()})

    # Gate de sincronización: todos deben haber completado sin ERROR_PROMPT_NOT_FOUND
    failed = [r for r in results
              if r.get("result", {}).get("invocation", "") == "ERROR_PROMPT_NOT_FOUND"]
    sync_status = "failed" if failed else "ok"

    # Persistir sync_point en state DB (best-effort)
    try:
        _spec = __import__("importlib.util", fromlist=["spec_from_file_location"])
        import importlib.util as _iu
        sp = _iu.spec_from_file_location("xdd_state", ROOT / "scripts" / "xdd-state.py")
        sm = _iu.module_from_spec(sp); sp.loader.exec_module(sm)
        sm.update_orchestration(run_id, sync_status, steps_done=len(results), sync_point=sync_at)
    except Exception:
        pass

    results.append({
        "role": "sync_point",
        "sync_at": sync_at,
        "sync_status": sync_status,
        "steps_evaluated": len(results),
        "failed_steps": len(failed),
        "note": f"S9 gate formal: {sync_status}. Timeout={timeout_s}s.",
    })
    return results


def run_party(pattern: dict, reg: dict, run_id: str, exec_mode: bool) -> list:
    """Party mode (Sprint 17, ADR-0016, inspirado en BMAD): N agentes sin lead,
    todos hablan, contribuciones libres. Mejor para brainstorm/exploración.
    Sin sync_point, sin orden."""
    invoker = invoke_agent_exec if exec_mode else invoke_agent_dry
    participants = [find_agent(reg, sp) for sp in pattern.get("participants",
                                                                pattern.get("specialists", []))]
    participants = [p for p in participants if p]
    results = []
    with ThreadPoolExecutor(max_workers=min(len(participants) or 1, 8)) as ex:
        futs = {ex.submit(invoker, p, run_id): p for p in participants}
        for fut in as_completed(futs):
            results.append({"role": "participant", "result": fut.result()})
    results.append({
        "role": "party_metadata",
        "mode": "party",
        "consensus_required": pattern.get("consensus_required", False),
        "moderator": pattern.get("moderator"),
        "note": "Party mode: contribuciones libres, no hay lead. Consenso opcional via moderator.",
    })
    return results


def maybe_retry(fn, max_attempts: int = 3, backoff: float = 1.5) -> dict:
    """Helper retry exponencial (Sprint 17). Devuelve dict con attempt + result."""
    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            return {"attempt": attempt, "ok": True, "result": fn()}
        except Exception as e:
            last_err = str(e)
            if attempt < max_attempts:
                time.sleep(backoff ** attempt)
    return {"attempt": max_attempts, "ok": False, "error": last_err}


def evaluate_conditional(pattern: dict, results_so_far: list) -> bool:
    """Sprint 17: pattern puede tener {conditional: {requires: 'role=lead;ok=true'}}
    sintaxis simple: campo=valor;campo=valor (AND)."""
    cond = pattern.get("conditional")
    if not cond:
        return True
    requires = cond.get("requires", "")
    if not requires:
        return True
    rules = [r.strip() for r in requires.split(";") if r.strip()]
    for r in rules:
        if "=" not in r:
            continue
        field, expected = r.split("=", 1)
        match = False
        for item in results_so_far:
            if str(item.get(field) or item.get("role")) == expected:
                match = True
                break
        if not match:
            return False
    return True


def has_hitl_checkpoint(pattern: dict, after_role: str) -> dict | None:
    """Sprint 17 + ADR-0018: HITL checkpoint definido en pattern como
    {hitl_after: 'lead', prompt: '...', required: true}."""
    cp = pattern.get("hitl_after")
    if cp and cp == after_role:
        return {
            "role": "hitl_checkpoint",
            "after": after_role,
            "prompt": pattern.get("hitl_prompt", "Continuar?"),
            "required": pattern.get("hitl_required", True),
            "blocked_until": "human_approval",
            "note": "Pause sintética; orquestador real (Claude Code/OpenCode) prompts al humano.",
        }
    return None


ORCHESTRATIONS = {
    "sequential": run_sequential,
    "parallel": run_parallel,
    "parallel_then_sync": run_parallel_then_sync,
    "party": run_party,
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

    # Persistir inicio en state DB (S9 runtime tracking; best-effort)
    _state_mod = None
    try:
        import importlib.util as _iu
        _sp = _iu.spec_from_file_location("xdd_state", ROOT / "scripts" / "xdd-state.py")
        _state_mod = _iu.module_from_spec(_sp); _sp.loader.exec_module(_state_mod)
        steps_total = 1 + len(pattern.get("specialists", []))
        _state_mod.record_orchestration(run_id, args.pattern, orch_type,
                                        exec_mode=args.exec, steps_total=steps_total)
    except Exception:
        pass

    start = time.time()
    results = ORCHESTRATIONS[orch_type](pattern, reg, run_id, args.exec)
    elapsed = round(time.time() - start, 3)

    # Actualizar estado final
    if _state_mod:
        try:
            any_fail = any(r.get("sync_status") == "failed" for r in results
                           if r.get("role") == "sync_point")
            _state_mod.update_orchestration(run_id, "failed" if any_fail else "completed",
                                            steps_done=len(results))
        except Exception:
            pass

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
    """Muestra orchestrations recientes desde la state DB (S9, v0.2)."""
    import importlib.util as _iu
    import os
    state_db = Path(os.environ.get("XDD_STATE_DB", Path.home() / ".xdd" / "state.db"))

    if not state_db.exists():
        print(f"[orch] state DB no existe ({state_db}). Corre `xdd init` o un patrón con --exec.")
        return 0

    try:
        _sp = _iu.spec_from_file_location("xdd_state", ROOT / "scripts" / "xdd-state.py")
        _sm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_sm)
        conn = _sm.db(state_db)
        rows = conn.execute(
            "SELECT run_id, pattern_name, orchestration_type, status, started_at, "
            "steps_done, steps_total FROM orchestrations ORDER BY started_at DESC LIMIT 20"
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"[orch] error leyendo state DB: {e}", file=sys.stderr)
        return 1

    if not rows:
        print("[orch] sin orchestrations registradas.")
        return 0

    import json as _json
    if args.json:
        print(_json.dumps([dict(r) for r in rows], indent=2))
    else:
        print(f"[orch] {len(rows)} orchestrations recientes:")
        for r in rows:
            status_icon = {"completed": "✓", "failed": "✗", "running": "⏳",
                           "sync_waiting": "⏸"}.get(r["status"], "?")
            print(f"  {status_icon} {r['run_id']:<28} {r['pattern_name']:<20} "
                  f"{r['status']:<15} {r['started_at']}")
    return 0


def build_parser():
    p, sub = make_parser("xdd-orchestrate", "Multi-agent orchestration runtime (Sprint 11).")

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
    p_s.add_argument("--json", action="store_true")
    p_s.set_defaults(func=cmd_status)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(args.func(args))
