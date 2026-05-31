#!/usr/bin/env python3
"""xdd-trace-summarize.py — Comprimir traces N-million tokens → layered report (Sprint 22).

Inspirado en NexAU-AHE Agent Debugger.
Lee .xdd/traces/<session-id>.jsonl y produce markdown report con evidence sourced.

Comandos:
  last [--depth=summary|detail|full]      — summarize last session
  session --id=SID [--depth=...]          — summarize specific session
  events --id=SID --top=N                  — top N event types con counts
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

__version__ = "0.1.0"

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


def latest_session(base: Path) -> str | None:
    if not base.exists():
        return None
    files = sorted(base.glob("*.jsonl"), key=lambda p: p.stat().st_mtime,
                    reverse=True)
    if not files:
        return None
    return files[0].stem


def summarize(events: list, depth: str = "summary") -> dict:
    """Layered report: summary / detail / full."""
    if not events:
        return {"events": 0}
    counter = Counter(e.get("event", "?") for e in events)
    roles = Counter(e.get("role", "") for e in events if e.get("role"))
    first_ts = events[0].get("ts", "?")
    last_ts = events[-1].get("ts", "?")
    report = {
        "events_total": len(events),
        "first_ts": first_ts,
        "last_ts": last_ts,
        "event_types": dict(counter.most_common()),
        "roles": dict(roles.most_common()),
    }
    if depth in ("detail", "full"):
        # Detail: incluye sample de events por type
        samples = {}
        for ev_type, _ in counter.most_common(5):
            samples[ev_type] = [
                {"ts": e.get("ts"), "content": (e.get("content") or "")[:120]}
                for e in events if e.get("event") == ev_type
            ][:3]
        report["samples"] = samples
    if depth == "full":
        # Full: incluye all events excerpts
        report["all_events_excerpts"] = [
            {"ts": e.get("ts"), "event": e.get("event"),
             "content_preview": (e.get("content") or "")[:80]}
            for e in events
        ]
    return report


def render_markdown(report: dict, sid: str, depth: str) -> str:
    lines = [
        f"# Trace Summary — session={sid}",
        "",
        f"**Depth:** {depth}  ",
        f"**Total events:** {report.get('events_total', 0)}  ",
        f"**First:** {report.get('first_ts', '?')}  ",
        f"**Last:** {report.get('last_ts', '?')}  ",
        "",
        "## Event types (count)",
        "",
    ]
    for ev, n in report.get("event_types", {}).items():
        lines.append(f"- `{ev}`: {n}")
    if report.get("roles"):
        lines.append("\n## Roles")
        lines.append("")
        for r, n in report.get("roles", {}).items():
            lines.append(f"- `{r}`: {n}")
    if "samples" in report:
        lines.append("\n## Samples (top 5 event types, 3 each)")
        for ev_type, samples in report["samples"].items():
            lines.append(f"\n### `{ev_type}`")
            for s in samples:
                lines.append(f"- {s['ts']}: `{s['content']}`")
    if "all_events_excerpts" in report:
        lines.append("\n## All events (excerpts)")
        lines.append("")
        for e in report["all_events_excerpts"]:
            lines.append(f"- {e['ts']} `{e['event']}`: {e['content_preview']}")
    return "\n".join(lines)


def cmd_last(args):
    sid = latest_session(Path(args.dir or DEFAULT_DIR))
    if not sid:
        print("[trace-summarize] no sessions found", file=sys.stderr)
        return 1
    events = load_session(sid, Path(args.dir or DEFAULT_DIR))
    report = summarize(events, args.depth)
    if args.json:
        print(json.dumps({"session": sid, **report}, indent=2))
    else:
        print(render_markdown(report, sid, args.depth))
    return 0


def cmd_session(args):
    events = load_session(args.id, Path(args.dir or DEFAULT_DIR))
    if not events:
        print(f"[trace-summarize] session {args.id} not found or empty",
              file=sys.stderr)
        return 1
    report = summarize(events, args.depth)
    if args.json:
        print(json.dumps({"session": args.id, **report}, indent=2))
    else:
        print(render_markdown(report, args.id, args.depth))
    return 0


def cmd_events(args):
    events = load_session(args.id, Path(args.dir or DEFAULT_DIR))
    if not events:
        return 1
    counter = Counter(e.get("event", "?") for e in events)
    top = counter.most_common(args.top)
    if args.json:
        print(json.dumps([{"event": e, "count": n} for e, n in top], indent=2))
    else:
        print(f"[trace-summarize] top {args.top} events of session={args.id}:")
        for ev, n in top:
            print(f"  {ev:<24} {n}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-trace-summarize",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version",
                    version=f"xdd-trace-summarize {__version__}")
    p.add_argument("--dir", help=f"Traces dir (default: {DEFAULT_DIR})")
    sub = p.add_subparsers(dest="command", required=True)

    p_l = sub.add_parser("last", help="Summarize latest session")
    p_l.add_argument("--depth", choices=["summary", "detail", "full"],
                      default="summary")
    p_l.add_argument("--json", action="store_true")
    p_l.set_defaults(func=cmd_last)

    p_s = sub.add_parser("session", help="Summarize specific session")
    p_s.add_argument("--id", required=True)
    p_s.add_argument("--depth", choices=["summary", "detail", "full"],
                      default="summary")
    p_s.add_argument("--json", action="store_true")
    p_s.set_defaults(func=cmd_session)

    p_e = sub.add_parser("events", help="Top N event types")
    p_e.add_argument("--id", required=True)
    p_e.add_argument("--top", type=int, default=10)
    p_e.add_argument("--json", action="store_true")
    p_e.set_defaults(func=cmd_events)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
