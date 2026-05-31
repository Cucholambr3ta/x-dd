#!/usr/bin/env python3
"""xdd-meta-eval.py — Meta-evaluator: compara mejoras ciclo a ciclo (Sprint 20).

Inspirado en NexAU-AHE iterative evaluate→analyze→improve loop.
Compara últimas N runs de xdd-eval para detectar regresión/progreso.

Comandos:
  compare --last=N [--suite=NAME]      — compara N runs más recientes
  trend --suite=NAME                    — gráfica trend (ASCII)
  baseline --set --suite=NAME           — congela baseline para comparaciones
  baseline --show                       — muestra baselines configuradas

Reports persisten en .xdd/eval-runs/<suite>/<timestamp>.json
"""
from __future__ import annotations

import argparse  # kept for type hints / argparse.ArgumentParser references
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version, utcnow_iso  # noqa: E402

__version__ = read_version()

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = Path(os.environ.get("XDD_EVAL_RUNS_DIR",
                                str(ROOT / ".xdd" / "eval-runs")))
BASELINES = ROOT / ".xdd" / "eval-baselines.json"


def load_runs(suite: str | None, limit: int) -> list[dict]:
    """Carga últimas `limit` runs (orden cronológico inverso)."""
    if not RUNS_DIR.exists():
        return []
    runs = []
    if suite:
        d = RUNS_DIR / suite
        if not d.exists():
            return []
        files = sorted(d.glob("*.json"), reverse=True)[:limit]
    else:
        files = []
        for sd in RUNS_DIR.iterdir():
            if sd.is_dir():
                files.extend(sd.glob("*.json"))
        files = sorted(files, reverse=True)[:limit]
    for f in files:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            r["_file"] = str(f)
            runs.append(r)
        except (json.JSONDecodeError, OSError):
            continue
    return runs


def load_baselines() -> dict:
    if not BASELINES.exists():
        return {}
    return json.loads(BASELINES.read_text(encoding="utf-8"))


def save_baselines(b: dict) -> None:
    BASELINES.parent.mkdir(parents=True, exist_ok=True)
    BASELINES.write_text(json.dumps(b, indent=2), encoding="utf-8")


def cmd_compare(args):
    runs = load_runs(args.suite, args.last)
    if len(runs) < 2:
        print(f"[meta-eval] Need at least 2 runs to compare (found {len(runs)}).",
              file=sys.stderr)
        return 1
    pass_rates = [r.get("pass_rate", 0.0) for r in runs]
    avg = mean(pass_rates)
    sd = stdev(pass_rates) if len(pass_rates) > 1 else 0.0
    last = pass_rates[0]
    second_last = pass_rates[1] if len(pass_rates) > 1 else None
    delta = (last - second_last) if second_last is not None else 0.0
    trend = "improving" if delta > 0.01 else ("regressing" if delta < -0.01 else "stable")
    result = {
        "suite": args.suite or "ALL",
        "runs_compared": len(runs),
        "pass_rates": pass_rates,
        "mean": round(avg, 4),
        "stdev": round(sd, 4),
        "latest_pass_rate": last,
        "previous_pass_rate": second_last,
        "delta": round(delta, 4),
        "trend": trend,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[meta-eval] suite={result['suite']} runs={len(runs)}")
        print(f"  latest:   {last:.3f}")
        print(f"  previous: {second_last:.3f}" if second_last else "  previous: (none)")
        print(f"  delta:    {delta:+.3f}  → {trend}")
        print(f"  mean:     {avg:.3f}")
        print(f"  stdev:    {sd:.3f}")
    return 0 if trend != "regressing" else 1


def cmd_trend(args):
    runs = load_runs(args.suite, 20)
    if not runs:
        print("[meta-eval] no runs available", file=sys.stderr)
        return 1
    pass_rates = [r.get("pass_rate", 0.0) for r in runs[::-1]]  # cronológico
    print(f"[meta-eval] trend for suite={args.suite or 'ALL'} (last {len(pass_rates)} runs):")
    print()
    for i, pr in enumerate(pass_rates):
        bar = "█" * int(pr * 30)
        print(f"  run {i+1:>3}: {pr:.3f} {bar}")
    print()
    return 0


def cmd_baseline(args):
    bl = load_baselines()
    if args.set:
        if not args.suite:
            print("[meta-eval] --set requires --suite", file=sys.stderr)
            return 2
        runs = load_runs(args.suite, 1)
        if not runs:
            print(f"[meta-eval] no runs for suite={args.suite}", file=sys.stderr)
            return 1
        latest = runs[0]
        bl[args.suite] = {
            "pass_rate": latest.get("pass_rate", 0.0),
            "set_at": utcnow_iso(),
            "from_run": latest.get("_file", "?"),
        }
        save_baselines(bl)
        print(f"[meta-eval] ✓ baseline saved for {args.suite}: "
              f"pass_rate={bl[args.suite]['pass_rate']:.3f}")
        return 0
    if args.show:
        if args.json:
            print(json.dumps(bl, indent=2))
        else:
            if not bl:
                print("[meta-eval] no baselines configured")
                return 0
            print(f"[meta-eval] {len(bl)} baselines:")
            for suite, info in bl.items():
                print(f"  {suite}: pass_rate={info['pass_rate']:.3f} "
                      f"set_at={info['set_at']}")
        return 0
    print("[meta-eval] use --set or --show", file=sys.stderr)
    return 2


def cmd_judge(args):
    """S14: judge-subagent — evalúa dos runs de eval con IA y emite APROBADO/REVISAR/RECHAZADO.

    Usa AnthropicProvider (lazy, degradación elegante sin API key → compara numéricamente).
    """
    runs = load_runs(args.suite, 2)
    if len(runs) < 2:
        print(f"[meta-eval] judge necesita ≥2 runs (hay {len(runs)}).", file=sys.stderr)
        return 1

    a, b = runs[1], runs[0]  # a=anterior, b=latest

    # Intentar AI judgment
    try:
        import importlib.util as _iu
        _sp = _iu.spec_from_file_location("xdd_provider", Path(__file__).parent / "xdd-provider.py")
        _pm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_pm)
        provider = _pm.get_provider(name="anthropic")
        prompt = (
            f"Eres un juez de evaluaciones de agentes de IA. Compara dos runs:\n\n"
            f"Run A (anterior): {json.dumps(a, indent=2)[:800]}\n\n"
            f"Run B (última): {json.dumps(b, indent=2)[:800]}\n\n"
            "Emite exactamente una de estas palabras como primera línea de tu respuesta: "
            "APROBADO, REVISAR, o RECHAZADO. Luego justifica en 2-3 oraciones."
        )
        response = provider.complete(prompt)
        first_line = response.strip().split("\n")[0].strip().upper()
        verdict = first_line if first_line in ("APROBADO", "REVISAR", "RECHAZADO") else "REVISAR"
        judge_mode = "AI"
    except Exception:
        # Fallback: comparación numérica
        delta = b.get("pass_rate", 0) - a.get("pass_rate", 0)
        verdict = "APROBADO" if delta >= 0 else "RECHAZADO"
        response = f"Fallback numérico: delta={delta:+.3f}"
        judge_mode = "numeric"

    result = {
        "suite": args.suite or "ALL",
        "run_a": a.get("suite", "?"),
        "run_b": b.get("suite", "?"),
        "verdict": verdict,
        "judge_mode": judge_mode,
        "reasoning": response[:300],
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        icon = {"APROBADO": "✅", "REVISAR": "⚠️", "RECHAZADO": "❌"}.get(verdict, "?")
        print(f"[meta-eval] judge [{judge_mode}]: {icon} {verdict}")
        print(f"  {result['reasoning'][:200]}")
    return 0 if verdict == "APROBADO" else 1


def build_parser():
    p, sub = make_parser("xdd-meta-eval", __doc__, raw_description=True, short_version_flag=False)

    p_c = sub.add_parser("compare", help="Compare last N runs")
    p_c.add_argument("--last", type=int, default=5)
    p_c.add_argument("--suite")
    p_c.add_argument("--json", action="store_true")
    p_c.set_defaults(func=cmd_compare)

    p_t = sub.add_parser("trend", help="ASCII trend chart")
    p_t.add_argument("--suite")
    p_t.set_defaults(func=cmd_trend)

    p_b = sub.add_parser("baseline", help="Manage baselines")
    p_b.add_argument("--set", action="store_true")
    p_b.add_argument("--show", action="store_true")
    p_b.add_argument("--suite")
    p_b.add_argument("--json", action="store_true")
    p_b.set_defaults(func=cmd_baseline)

    p_j = sub.add_parser("judge", help="S14: judge-subagent evalúa runs con IA")
    p_j.add_argument("--suite")
    p_j.add_argument("--json", action="store_true")
    p_j.set_defaults(func=cmd_judge)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
