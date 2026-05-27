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

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

__version__ = "0.1.0-dev"

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = Path(os.environ.get("XDD_EVAL_RUNS_DIR",
                                str(ROOT / ".xdd" / "eval-runs")))
BASELINES = ROOT / ".xdd" / "eval-baselines.json"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-meta-eval", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-meta-eval {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

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

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
