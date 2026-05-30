#!/usr/bin/env python3
"""xdd-flow.py — Gate ejecutable de flujos declarativos (Branch 2).

Cierra el hueco que motivó el Sprint 32 un paso más: el gate de X-DD razona
sobre artefactos-archivo (markdown + regex); aquí se valida un FLUJO de agentes
EJECUTADO end-to-end, no solo que un .md exista.

Un flujo es JSON declarativo:
  {
    "agents": [{"name": "A", "responses": {"in": "out"}, "default": "x"}],
    "mode": "sequential" | "parallel",
    "input": "...",
    "expected": "..."        # opcional: el grader valida result contra esto
  }

Se ejecuta con MockProvider (xdd-provider.py) → determinista, sin red. Emite
ExecutionTrace (steps con ts/duration_ms) a .xdd/build/flow-trace.json. El gate
(xdd-gate.py:_check_flow_evidence) exige ese trace con steps>0 para la fase build.

Portado del runtime de agentix; graders reusados de xdd-eval.py.

Uso:
  xdd-flow.py run --flow demo.json [--trace OUT.json]
  xdd-flow.py run --flow demo.json --expected-from-flow   # valida result vs expected
  xdd-flow.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

__version__ = "0.1.0-dev"

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# Reuso del MockProvider (sin red) — import por ruta (script con guion).
_spec = importlib.util.spec_from_file_location("xdd_provider", SCRIPTS / "xdd-provider.py")
_xp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_xp)
MockProvider = _xp.MockProvider
get_provider = _xp.get_provider


@dataclass
class Step:
    agent_name: str
    input: str
    output: str
    ts: float
    duration_ms: float


@dataclass
class ExecutionTrace:
    """Traza estructurada de un run (portado de agentix.runtime)."""

    mode: str
    steps: list[Step] = field(default_factory=list)
    result: object = None  # str | list[str] | None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "steps": [asdict(s) for s in self.steps],
            "result": self.result,
            "step_count": len(self.steps),
        }


class _FlowAgent:
    """Agente mínimo del flujo: nombre + MockProvider determinista."""

    def __init__(self, name: str, responses: dict | None = None, default: str | None = None,
                 system: str | None = None):
        self.name = name
        self.system = system
        self.provider = MockProvider(responses=responses, default=default)

    def run(self, prompt: str) -> str:
        return self.provider.complete(prompt, system=self.system)


def _run_one(agent: _FlowAgent, input_str: str) -> Step:
    t0 = time.perf_counter()
    ts = time.time()
    out = agent.run(input_str)
    dur = (time.perf_counter() - t0) * 1000
    return Step(agent.name, input_str, out, ts, dur)


def run_sequential(agents: list[_FlowAgent], input_str: str) -> ExecutionTrace:
    """Cada agente recibe la salida del anterior."""
    trace = ExecutionTrace(mode="sequential")
    cur = input_str
    for agent in agents:
        step = _run_one(agent, cur)
        trace.steps.append(step)
        cur = step.output
    trace.result = cur
    return trace


def run_parallel(agents: list[_FlowAgent], input_str: str,
                 max_workers: int | None = None) -> ExecutionTrace:
    """Agentes concurrentes sobre el mismo input. Orden determinista por name."""
    trace = ExecutionTrace(mode="parallel")
    with ThreadPoolExecutor(max_workers=max_workers or len(agents) or 1) as ex:
        steps = list(ex.map(lambda a: _run_one(a, input_str), agents))
    steps.sort(key=lambda s: s.agent_name)
    trace.steps = steps
    trace.result = [s.output for s in steps]
    return trace


def build_agents(spec: list[dict]) -> list[_FlowAgent]:
    agents = []
    for a in spec:
        agents.append(_FlowAgent(
            name=a["name"],
            responses=a.get("responses"),
            default=a.get("default"),
            system=a.get("system"),
        ))
    return agents


def execute_flow(flow: dict) -> ExecutionTrace:
    """Ejecuta un flujo declarativo y devuelve su trace."""
    agents = build_agents(flow.get("agents", []))
    if not agents:
        raise ValueError("flujo sin 'agents'")
    mode = flow.get("mode", "sequential")
    inp = flow.get("input", "")
    if mode == "sequential":
        return run_sequential(agents, inp)
    if mode == "parallel":
        return run_parallel(agents, inp)
    raise ValueError(f"modo desconocido: {mode!r}")


def grade_result(trace: ExecutionTrace, flow: dict) -> tuple[bool, str]:
    """Valida result contra expected (exact o regex). Sin expected → solo exige steps>0."""
    if not trace.steps:
        return False, "flujo sin steps ejecutados (result vacío)"
    if "expected" not in flow and "expected_regex" not in flow:
        return True, f"{len(trace.steps)} steps ejecutados (sin expected declarado)"
    result = trace.result
    if "expected_regex" in flow:
        text = result if isinstance(result, str) else json.dumps(result)
        if re.search(flow["expected_regex"], text):
            return True, "result matched expected_regex"
        return False, f"result no matchea expected_regex={flow['expected_regex']!r}"
    if result == flow["expected"]:
        return True, "result == expected"
    return False, f"result != expected (got={result!r})"


def cmd_run(args) -> int:
    flow_path = Path(args.flow)
    if not flow_path.exists():
        print(f"[flow] flujo no encontrado: {flow_path}", file=sys.stderr)
        return 2
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    trace = execute_flow(flow)
    ok, detail = grade_result(trace, flow)

    out = args.trace or ".xdd/build/flow-trace.json"
    out_path = Path(out)
    if not args.no_write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(trace.to_dict(), indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({"ok": ok, "detail": detail, "trace": trace.to_dict()}, indent=2))
    else:
        mark = "✓" if ok else "✗"
        print(f"[flow] {mark} {trace.mode}: {detail}")
        if not args.no_write:
            print(f"[flow] trace → {out_path}")
    return 0 if ok else 1


def _self_test() -> int:
    """Verifica seq + parallel deterministas, sin red."""
    seq = {
        "agents": [
            {"name": "up", "responses": {"hi": "HI"}},
            {"name": "echo", "default": "done"},
        ],
        "mode": "sequential",
        "input": "hi",
        "expected": "done",
    }
    t = execute_flow(seq)
    ok, _ = grade_result(t, seq)
    assert ok, "sequential grade failed"
    assert len(t.steps) == 2
    assert t.steps[0].output == "HI"

    par = {
        "agents": [
            {"name": "b", "default": "B"},
            {"name": "a", "default": "A"},
        ],
        "mode": "parallel",
        "input": "x",
    }
    t2 = execute_flow(par)
    assert [s.agent_name for s in t2.steps] == ["a", "b"], "parallel no determinista"
    assert t2.result == ["A", "B"]
    print("[flow] self-test OK — seq+parallel deterministas, sin red.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="xdd-flow", description=__doc__)
    ap.add_argument("--version", action="version", version=f"xdd-flow {__version__}")
    ap.add_argument("--self-test", action="store_true", help="verifica runtime determinista")
    sub = ap.add_subparsers(dest="cmd")
    pr = sub.add_parser("run", help="ejecuta un flujo declarativo")
    pr.add_argument("--flow", required=True, help="ruta al flujo JSON")
    pr.add_argument("--trace", help="ruta de salida del trace (default .xdd/build/flow-trace.json)")
    pr.add_argument("--no-write", action="store_true", help="no escribir trace a disco")
    pr.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if args.cmd == "run":
        return cmd_run(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
