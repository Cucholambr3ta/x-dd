#!/usr/bin/env python3
"""xdd-cost.py — Per-call LLM cost tracker (Sprint 18, ADR-0022).

Tabla pricing model-aware (USD/1M tokens). Persiste a SQLite ~/.xdd/cost.db.
Compat con xdd-state.py SQLite layout (no overlap).

Comandos:
  record --provider=P --model=M --input-tokens=N --output-tokens=N
                                                     — registra una call
  report [--since=N[h|d|w]] [--by=model|provider|day]
                                                     — reporte agregado
  pricing --list                                    — muestra tabla pricing actual
  pricing --update --model=M --input=X --output=Y   — override pricing local
  total                                              — suma total $ todos los days
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

__version__ = "0.1.0"

DEFAULT_DB = Path(os.environ.get("XDD_COST_DB",
                                  str(Path.home() / ".xdd" / "cost.db")))

# USD per 1M tokens (input, output). Sourced from public pricing 2026-Q1.
PRICING_DEFAULT = {
    # Anthropic
    "claude-haiku-4-5":  (0.25, 1.25),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-7":   (15.00, 75.00),
    # OpenAI
    "gpt-4o-mini":       (0.15, 0.60),
    "gpt-4o":            (2.50, 10.00),
    "o1-mini":           (3.00, 12.00),
    "o1":                (15.00, 60.00),
    # Google
    "gemini-2.0-flash":  (0.10, 0.40),
    "gemini-2.0-pro":    (1.25, 5.00),
    # Local (no cost)
    "llama3.1-8b":       (0.0, 0.0),
    "llama3.1-70b":      (0.0, 0.0),
    "nomic-embed-text":  (0.0, 0.0),
}


SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cost_usd REAL NOT NULL,
  session_id TEXT,
  task TEXT
);
CREATE INDEX IF NOT EXISTS idx_calls_ts ON calls(ts);
CREATE INDEX IF NOT EXISTS idx_calls_model ON calls(model);

CREATE TABLE IF NOT EXISTS pricing_overrides (
  model TEXT PRIMARY KEY,
  input_per_1m REAL NOT NULL,
  output_per_1m REAL NOT NULL
);
"""


def db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.row_factory = sqlite3.Row
    return conn


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pricing_for(model: str, conn: sqlite3.Connection) -> tuple[float, float]:
    row = conn.execute(
        "SELECT input_per_1m, output_per_1m FROM pricing_overrides WHERE model = ?",
        (model,)).fetchone()
    if row:
        return float(row[0]), float(row[1])
    return PRICING_DEFAULT.get(model, (0.0, 0.0))


def cost_for(model: str, input_t: int, output_t: int,
             conn: sqlite3.Connection) -> float:
    pi, po = pricing_for(model, conn)
    return (input_t / 1_000_000) * pi + (output_t / 1_000_000) * po


def cmd_record(args):
    conn = db(Path(args.db))
    cost = cost_for(args.model, args.input_tokens, args.output_tokens, conn)
    conn.execute(
        "INSERT INTO calls (ts, provider, model, input_tokens, output_tokens, "
        "cost_usd, session_id, task) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (utcnow(), args.provider, args.model, args.input_tokens,
         args.output_tokens, cost, args.session_id, args.task)
    )
    conn.commit()
    conn.close()
    if args.json:
        print(json.dumps({"ok": True, "cost_usd": round(cost, 6),
                          "model": args.model}))
    else:
        print(f"[cost] ✓ recorded {args.model}: ${cost:.6f} "
              f"({args.input_tokens}/{args.output_tokens} tokens)")
    return 0


def parse_since(spec: str) -> str:
    """e.g. '7d' → cutoff iso 7 days ago."""
    if not spec:
        return "1970-01-01T00:00:00Z"
    unit = spec[-1]
    n = int(spec[:-1])
    delta = {"h": timedelta(hours=n), "d": timedelta(days=n),
             "w": timedelta(weeks=n)}.get(unit, timedelta(days=n))
    return (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_report(args):
    conn = db(Path(args.db))
    cutoff = parse_since(args.since) if args.since else "1970-01-01T00:00:00Z"
    by_col = {"model": "model", "provider": "provider",
              "day": "substr(ts,1,10)"}.get(args.by, "model")
    rows = conn.execute(
        f"SELECT {by_col} AS bucket, COUNT(*) AS calls, "
        f"SUM(input_tokens) AS in_tok, SUM(output_tokens) AS out_tok, "
        f"SUM(cost_usd) AS total_usd "
        f"FROM calls WHERE ts >= ? GROUP BY bucket ORDER BY total_usd DESC",
        (cutoff,)).fetchall()
    total = sum(r["total_usd"] for r in rows)
    out = {
        "since": cutoff,
        "by": args.by,
        "total_calls": sum(r["calls"] for r in rows),
        "total_cost_usd": round(total, 4),
        "rows": [dict(r) for r in rows],
    }
    conn.close()
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"[cost] report since={out['since']} by={args.by}")
        print(f"  total_calls: {out['total_calls']}")
        print(f"  total_cost_usd: ${out['total_cost_usd']}")
        print(f"  {'bucket':<24} {'calls':>6} {'in_tok':>10} {'out_tok':>10} {'$':>10}")
        for r in rows:
            print(f"  {(r['bucket'] or '?'):<24} {r['calls']:>6} "
                  f"{r['in_tok']:>10} {r['out_tok']:>10} ${r['total_usd']:>9.4f}")
    return 0


def cmd_pricing(args):
    conn = db(Path(args.db))
    if args.update:
        if not (args.model and args.input is not None and args.output is not None):
            print("[cost] ERROR: --update requires --model + --input + --output",
                  file=sys.stderr)
            return 2
        conn.execute(
            "INSERT OR REPLACE INTO pricing_overrides VALUES (?, ?, ?)",
            (args.model, args.input, args.output))
        conn.commit()
        print(f"[cost] ✓ pricing override saved for {args.model}")
        return 0
    # List
    overrides = {r["model"]: (r["input_per_1m"], r["output_per_1m"])
                  for r in conn.execute(
                      "SELECT * FROM pricing_overrides").fetchall()}
    merged = dict(PRICING_DEFAULT)
    merged.update(overrides)
    if args.json:
        print(json.dumps({"defaults": PRICING_DEFAULT, "overrides": overrides,
                          "merged": merged}, indent=2))
    else:
        print(f"[cost] pricing table (USD per 1M tokens):")
        print(f"  {'model':<24} {'input':>10} {'output':>10}")
        for m, (i, o) in sorted(merged.items()):
            mark = " *" if m in overrides else ""
            print(f"  {m:<24} {i:>10.2f} {o:>10.2f}{mark}")
        if overrides:
            print(f"  (* = local override)")
    conn.close()
    return 0


def cmd_total(args):
    conn = db(Path(args.db))
    total = conn.execute("SELECT SUM(cost_usd) FROM calls").fetchone()[0] or 0.0
    n = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    conn.close()
    if args.json:
        print(json.dumps({"total_calls": n, "total_cost_usd": round(total, 4)}))
    else:
        print(f"[cost] all-time total: {n} calls, ${total:.4f}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-cost", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-cost {__version__}")
    p.add_argument("--db", default=str(DEFAULT_DB))
    sub = p.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("record", help="Record an LLM call")
    p_r.add_argument("--provider", required=True)
    p_r.add_argument("--model", required=True)
    p_r.add_argument("--input-tokens", type=int, required=True)
    p_r.add_argument("--output-tokens", type=int, required=True)
    p_r.add_argument("--session-id")
    p_r.add_argument("--task")
    p_r.add_argument("--json", action="store_true")
    p_r.set_defaults(func=cmd_record)

    p_rp = sub.add_parser("report", help="Aggregated cost report")
    p_rp.add_argument("--since", help="e.g. 7d, 24h, 2w")
    p_rp.add_argument("--by", choices=["model", "provider", "day"], default="model")
    p_rp.add_argument("--json", action="store_true")
    p_rp.set_defaults(func=cmd_report)

    p_pr = sub.add_parser("pricing", help="View or override pricing table")
    p_pr.add_argument("--list", action="store_true")
    p_pr.add_argument("--update", action="store_true")
    p_pr.add_argument("--model")
    p_pr.add_argument("--input", type=float)
    p_pr.add_argument("--output", type=float)
    p_pr.add_argument("--json", action="store_true")
    p_pr.set_defaults(func=cmd_pricing)

    p_tot = sub.add_parser("total", help="All-time total")
    p_tot.add_argument("--json", action="store_true")
    p_tot.set_defaults(func=cmd_total)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
