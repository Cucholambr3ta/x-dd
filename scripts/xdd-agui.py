#!/usr/bin/env python3
"""xdd-agui.py — AG-UI event-driven streaming spec (Sprint 23, ADR-0031).

Emite JSONL events que orchestrator/UI consume:
  turn_start, tool_call, tool_result, hitl_request, content_chunk, turn_end

Comandos:
  emit --event=NAME [--turn-id=N] [--data=JSON]   — emite 1 event
  stream --from-orchestrate                        — leer xdd-orchestrate output, emit AG-UI events
  schema                                            — muestra schema oficial de cada event type
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

__version__ = "0.1.0"


EVENT_SCHEMAS = {
    "turn_start": {
        "required": ["turn_id"],
        "optional": ["agent_id", "session_id"],
    },
    "tool_call": {
        "required": ["turn_id", "tool_name", "args"],
        "optional": ["tool_call_id", "intent", "severity"],
    },
    "tool_result": {
        "required": ["turn_id", "tool_call_id", "result"],
        "optional": ["error", "duration_ms"],
    },
    "hitl_request": {
        "required": ["turn_id", "prompt"],
        "optional": ["required", "default_answer", "timeout_sec"],
    },
    "content_chunk": {
        "required": ["turn_id", "content"],
        "optional": ["role", "chunk_index"],
    },
    "turn_end": {
        "required": ["turn_id"],
        "optional": ["status", "tokens_used", "cost_usd"],
    },
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def emit_event(event_type: str, data: dict) -> dict:
    if event_type not in EVENT_SCHEMAS:
        raise ValueError(f"unknown event: {event_type}")
    schema = EVENT_SCHEMAS[event_type]
    missing = [r for r in schema["required"] if r not in data]
    if missing:
        raise ValueError(f"missing required fields for {event_type}: {missing}")
    return {
        "spec": "agui/0.1",
        "ts": utcnow_iso(),
        "event": event_type,
        **data,
    }


def cmd_emit(args):
    data = json.loads(args.data) if args.data else {}
    if args.turn_id:
        data["turn_id"] = args.turn_id
    try:
        event = emit_event(args.event, data)
    except ValueError as e:
        print(f"[agui] ERROR: {e}", file=sys.stderr)
        return 2
    print(json.dumps(event))
    return 0


def cmd_stream(args):
    """Lee stdin (output xdd-orchestrate) y emite AG-UI events."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Heurística: convertir orchestrate steps a AG-UI events
        if "steps" in data:
            for i, step in enumerate(data["steps"]):
                role = step.get("role", "?")
                ev_type = "tool_call" if role == "specialist" else "content_chunk"
                turn_id = i + 1
                try:
                    out_event = emit_event(ev_type, {
                        "turn_id": turn_id,
                        "tool_name": step.get("result", {}).get("name", "?") if ev_type == "tool_call" else None,
                        "args": step.get("result", {}) if ev_type == "tool_call" else None,
                        "content": json.dumps(step) if ev_type == "content_chunk" else None,
                    })
                    print(json.dumps(out_event))
                except ValueError:
                    continue
    return 0


def cmd_schema(args):
    if args.json:
        print(json.dumps(EVENT_SCHEMAS, indent=2))
    else:
        print(f"[agui] event schemas ({len(EVENT_SCHEMAS)} event types):")
        for ev, sch in EVENT_SCHEMAS.items():
            req = sch["required"]
            opt = sch["optional"]
            print(f"  {ev}:")
            print(f"    required: {req}")
            print(f"    optional: {opt}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-agui", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-agui {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_e = sub.add_parser("emit", help="Emit 1 AG-UI event")
    p_e.add_argument("--event", required=True, choices=list(EVENT_SCHEMAS))
    p_e.add_argument("--turn-id", type=int)
    p_e.add_argument("--data", help="JSON data")
    p_e.set_defaults(func=cmd_emit)

    p_s = sub.add_parser("stream", help="Convert xdd-orchestrate output → AG-UI events")
    p_s.add_argument("--from-orchestrate", action="store_true")
    p_s.set_defaults(func=cmd_stream)

    p_sc = sub.add_parser("schema", help="Show event schemas")
    p_sc.add_argument("--json", action="store_true")
    p_sc.set_defaults(func=cmd_schema)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
