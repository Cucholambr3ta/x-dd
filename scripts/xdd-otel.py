#!/usr/bin/env python3
"""xdd-otel.py — OpenTelemetry Gen AI span emitter (Sprint 18, ADR-0021).

Compat OpenLLMetry/OpenInference semantic conventions for GenAI.
Stdlib pure: no opentelemetry-sdk requerido para baseline (JSON output).
Si `opentelemetry-api` instalado, exporta vía OTLP también.

Comandos:
  span-start --name=NAME --kind=KIND [--attrs=JSON]   — abre span
  span-end --id=ID [--status=ok|error]                 — cierra span
  emit --name=NAME --duration-ms=N --attrs=JSON        — span one-shot
  list                                                  — lista spans guardados
  export --since=N[h|d] --format=jsonl|otlp            — exporta spans

Path persistente: $XDD_OTEL_DIR (default: .xdd/traces/spans/)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"

DEFAULT_DIR = Path(os.environ.get("XDD_OTEL_DIR",
                                    str(Path.cwd() / ".xdd" / "traces" / "spans")))

GENAI_KINDS = {
    "llm.call", "tool.call", "agent.invocation", "skill.execution",
    "workflow.step", "gate.transition", "phase.validation",
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def utcnow_ns() -> int:
    return time.time_ns()


def ensure_dir(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]


def new_trace_id() -> str:
    return uuid.uuid4().hex


def write_span(span: dict, out_dir: Path) -> Path:
    ensure_dir(out_dir)
    fname = f"{span['span_id']}.json"
    p = out_dir / fname
    p.write_text(json.dumps(span, indent=2), encoding="utf-8")
    return p


def cmd_span_start(args):
    if args.kind not in GENAI_KINDS:
        print(f"[otel] WARN: kind '{args.kind}' not in GENAI_KINDS, accepting anyway",
              file=sys.stderr)
    span = {
        "span_id": new_span_id(),
        "trace_id": args.trace_id or new_trace_id(),
        "parent_span_id": args.parent or None,
        "name": args.name,
        "kind": args.kind,
        "start_time": utcnow_iso(),
        "start_time_ns": utcnow_ns(),
        "end_time": None,
        "duration_ms": None,
        "status": "in_progress",
        "attributes": json.loads(args.attrs) if args.attrs else {},
    }
    p = write_span(span, Path(args.dir or DEFAULT_DIR))
    if args.json:
        print(json.dumps({"span_id": span["span_id"], "trace_id": span["trace_id"],
                          "file": str(p)}))
    else:
        print(f"[otel] ✓ span_id={span['span_id']} trace_id={span['trace_id']}")
        print(f"       file={p}")
    return 0


def cmd_span_end(args):
    d = Path(args.dir or DEFAULT_DIR)
    p = d / f"{args.id}.json"
    if not p.exists():
        print(f"[otel] ERROR: span {args.id} not found in {d}", file=sys.stderr)
        return 2
    span = json.loads(p.read_text(encoding="utf-8"))
    span["end_time"] = utcnow_iso()
    end_ns = utcnow_ns()
    span["duration_ms"] = (end_ns - span["start_time_ns"]) / 1_000_000
    span["status"] = args.status or "ok"
    if args.attrs:
        span["attributes"].update(json.loads(args.attrs))
    p.write_text(json.dumps(span, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps({"span_id": args.id, "duration_ms": span["duration_ms"],
                          "status": span["status"]}))
    else:
        print(f"[otel] ✓ closed span_id={args.id} duration={span['duration_ms']:.2f}ms "
              f"status={span['status']}")
    return 0


def cmd_emit(args):
    span = {
        "span_id": new_span_id(),
        "trace_id": args.trace_id or new_trace_id(),
        "parent_span_id": args.parent or None,
        "name": args.name,
        "kind": args.kind or "agent.invocation",
        "start_time": utcnow_iso(),
        "start_time_ns": utcnow_ns(),
        "end_time": utcnow_iso(),
        "duration_ms": float(args.duration_ms),
        "status": "ok",
        "attributes": json.loads(args.attrs) if args.attrs else {},
    }
    p = write_span(span, Path(args.dir or DEFAULT_DIR))
    if args.json:
        print(json.dumps({"span_id": span["span_id"], "file": str(p)}))
    else:
        print(f"[otel] ✓ emitted span_id={span['span_id']} dur={args.duration_ms}ms")
    return 0


def cmd_list(args):
    d = Path(args.dir or DEFAULT_DIR)
    if not d.exists():
        print("[]" if args.json else "[otel] no spans dir yet")
        return 0
    spans = []
    for f in sorted(d.glob("*.json")):
        try:
            spans.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    if args.json:
        print(json.dumps(spans, indent=2))
    else:
        print(f"[otel] {len(spans)} spans:")
        for s in spans:
            print(f"  {s['span_id']:<18} {s['kind']:<24} {s['name']:<30} "
                  f"dur={s.get('duration_ms') or '?':>8} status={s.get('status')}")
    return 0


def cmd_export(args):
    d = Path(args.dir or DEFAULT_DIR)
    if not d.exists():
        return 1
    spans = []
    for f in sorted(d.glob("*.json")):
        try:
            spans.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    if args.format == "jsonl":
        for s in spans:
            print(json.dumps(s))
    elif args.format == "otlp":
        out = {"resourceSpans": [{
            "resource": {"attributes": [{"key": "service.name",
                                         "value": {"stringValue": "x-dd"}}]},
            "scopeSpans": [{"scope": {"name": "xdd-otel", "version": __version__},
                            "spans": spans}]
        }]}
        print(json.dumps(out, indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-otel", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-otel {__version__}")
    p.add_argument("--dir", help=f"Spans dir (default: {DEFAULT_DIR})")
    sub = p.add_subparsers(dest="command", required=True)

    p_ss = sub.add_parser("span-start", help="Open a span")
    p_ss.add_argument("--name", required=True)
    p_ss.add_argument("--kind", required=True)
    p_ss.add_argument("--trace-id")
    p_ss.add_argument("--parent")
    p_ss.add_argument("--attrs", help="JSON")
    p_ss.add_argument("--json", action="store_true")
    p_ss.set_defaults(func=cmd_span_start)

    p_se = sub.add_parser("span-end", help="Close a span")
    p_se.add_argument("--id", required=True)
    p_se.add_argument("--status", choices=["ok", "error"])
    p_se.add_argument("--attrs", help="JSON")
    p_se.add_argument("--json", action="store_true")
    p_se.set_defaults(func=cmd_span_end)

    p_em = sub.add_parser("emit", help="One-shot span")
    p_em.add_argument("--name", required=True)
    p_em.add_argument("--kind")
    p_em.add_argument("--duration-ms", required=True)
    p_em.add_argument("--trace-id")
    p_em.add_argument("--parent")
    p_em.add_argument("--attrs", help="JSON")
    p_em.add_argument("--json", action="store_true")
    p_em.set_defaults(func=cmd_emit)

    p_ls = sub.add_parser("list", help="List stored spans")
    p_ls.add_argument("--json", action="store_true")
    p_ls.set_defaults(func=cmd_list)

    p_ex = sub.add_parser("export", help="Export spans (jsonl or otlp)")
    p_ex.add_argument("--format", choices=["jsonl", "otlp"], default="jsonl")
    p_ex.add_argument("--since", help="e.g. 7d, 24h (not yet enforced)")
    p_ex.set_defaults(func=cmd_export)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
