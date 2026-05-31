#!/usr/bin/env python3
"""xdd-replay.py — Session trace replay (Sprint 18, ADR-0021).

Reads .xdd/traces/<session-id>.jsonl and reconstructs the session.

Comandos:
  list                       — lista sessions disponibles
  show --id=SID             — muestra summary de una session
  replay --id=SID [--step]  — replay events linealmente
  diff --a=SID1 --b=SID2   — compara dos sessions

Trace event schema (cada línea JSONL):
  {ts, event, span_id?, trace_id?, role?, content?, attributes?, ...}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import read_version, utcnow_iso_us as utcnow_iso  # noqa: E402

__version__ = read_version()

DEFAULT_DIR = Path(os.environ.get("XDD_TRACES_DIR",
                                    str(Path.cwd() / ".xdd" / "traces")))


def load_session(sid: str, base: Path) -> list:
    p = base / f"{sid}.jsonl"
    if not p.exists():
        return []
    events = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def list_sessions(base: Path) -> list[dict]:
    if not base.exists():
        return []
    rows = []
    for f in sorted(base.glob("*.jsonl")):
        sid = f.stem
        events = load_session(sid, base)
        rows.append({
            "session_id": sid,
            "events": len(events),
            "first_ts": events[0].get("ts") if events else None,
            "last_ts": events[-1].get("ts") if events else None,
            "path": str(f),
        })
    return rows


def cmd_list(args):
    rows = list_sessions(Path(args.dir or DEFAULT_DIR))
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"[replay] {len(rows)} sessions in {args.dir or DEFAULT_DIR}:")
        for r in rows:
            print(f"  {r['session_id']:<32} events={r['events']:>5}  "
                  f"{r['first_ts']} → {r['last_ts']}")
    return 0


def cmd_show(args):
    events = load_session(args.id, Path(args.dir or DEFAULT_DIR))
    if not events:
        print(f"[replay] ERROR: session '{args.id}' not found or empty",
              file=sys.stderr)
        return 2
    summary = {
        "session_id": args.id,
        "total_events": len(events),
        "event_types": {},
        "first_ts": events[0].get("ts"),
        "last_ts": events[-1].get("ts"),
        "duration_seconds": None,
    }
    for e in events:
        ev = e.get("event", "unknown")
        summary["event_types"][ev] = summary["event_types"].get(ev, 0) + 1
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"[replay] session={args.id}")
        print(f"  total_events: {summary['total_events']}")
        print(f"  first_ts:     {summary['first_ts']}")
        print(f"  last_ts:      {summary['last_ts']}")
        print(f"  event_types:")
        for k, v in sorted(summary["event_types"].items(),
                           key=lambda x: -x[1]):
            print(f"    {k:<24} {v}")
    return 0


def cmd_replay(args):
    events = load_session(args.id, Path(args.dir or DEFAULT_DIR))
    if not events:
        print(f"[replay] ERROR: session '{args.id}' not found", file=sys.stderr)
        return 2
    print(f"[replay] replaying {len(events)} events from session={args.id}")
    print("=" * 60)
    for i, e in enumerate(events, 1):
        ts = e.get("ts", "?")
        ev = e.get("event", "?")
        role = e.get("role", "")
        content = (e.get("content") or "")[:120].replace("\n", " ")
        print(f"[{i:>4}] {ts} {ev:<18} {role:<10} {content}")
        if args.step and i < len(events):
            try:
                input("[press enter for next, Ctrl-C to stop] ")
            except KeyboardInterrupt:
                print("\n[replay] interrupted")
                return 0
    print("=" * 60)
    print(f"[replay] done. {len(events)} events shown.")
    return 0


def cmd_diff(args):
    a = load_session(args.a, Path(args.dir or DEFAULT_DIR))
    b = load_session(args.b, Path(args.dir or DEFAULT_DIR))
    if not a or not b:
        print(f"[replay] ERROR: one or both sessions missing", file=sys.stderr)
        return 2
    a_evs = {e.get("event", "?") for e in a}
    b_evs = {e.get("event", "?") for e in b}
    only_a = a_evs - b_evs
    only_b = b_evs - a_evs
    common = a_evs & b_evs
    result = {
        "a": {"session_id": args.a, "events": len(a)},
        "b": {"session_id": args.b, "events": len(b)},
        "only_in_a": sorted(only_a),
        "only_in_b": sorted(only_b),
        "common_event_types": sorted(common),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[replay] diff:")
        print(f"  a={args.a} ({len(a)} events)  b={args.b} ({len(b)} events)")
        print(f"  only in a: {sorted(only_a) or '∅'}")
        print(f"  only in b: {sorted(only_b) or '∅'}")
        print(f"  common: {len(common)} event types")
    return 0


def cmd_record(args):
    """Append an event to a session jsonl (helper for instrumented scripts)."""
    base = Path(args.dir or DEFAULT_DIR)
    base.mkdir(parents=True, exist_ok=True)
    p = base / f"{args.session}.jsonl"
    event = {
        "ts": utcnow_iso(),
        "event": args.event,
        "session_id": args.session,
    }
    if args.role:
        event["role"] = args.role
    if args.content:
        event["content"] = args.content
    if args.attrs:
        event["attributes"] = json.loads(args.attrs)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    if args.json:
        print(json.dumps({"ok": True, "session": args.session, "event": args.event}))
    else:
        print(f"[replay] ✓ recorded event={args.event} → {p}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-replay", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-replay {__version__}")
    p.add_argument("--dir", help=f"Traces dir (default: {DEFAULT_DIR})")
    sub = p.add_subparsers(dest="command", required=True)

    p_ls = sub.add_parser("list", help="List sessions")
    p_ls.add_argument("--json", action="store_true")
    p_ls.set_defaults(func=cmd_list)

    p_sh = sub.add_parser("show", help="Show session summary")
    p_sh.add_argument("--id", required=True)
    p_sh.add_argument("--json", action="store_true")
    p_sh.set_defaults(func=cmd_show)

    p_rp = sub.add_parser("replay", help="Replay session events linearly")
    p_rp.add_argument("--id", required=True)
    p_rp.add_argument("--step", action="store_true", help="Pause between events")
    p_rp.set_defaults(func=cmd_replay)

    p_df = sub.add_parser("diff", help="Diff two sessions")
    p_df.add_argument("--a", required=True)
    p_df.add_argument("--b", required=True)
    p_df.add_argument("--json", action="store_true")
    p_df.set_defaults(func=cmd_diff)

    p_rc = sub.add_parser("record", help="Append event to session (helper)")
    p_rc.add_argument("--session", required=True)
    p_rc.add_argument("--event", required=True)
    p_rc.add_argument("--role")
    p_rc.add_argument("--content")
    p_rc.add_argument("--attrs", help="JSON")
    p_rc.add_argument("--json", action="store_true")
    p_rc.set_defaults(func=cmd_record)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
