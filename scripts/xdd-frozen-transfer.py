#!/usr/bin/env python3
"""xdd-frozen-transfer.py — Frozen harness transfer experiments (Sprint 22).

Inspirado en NexAU-AHE frozen-harness transfer (Terminal-Bench → SWE-bench).

Toma skills/agents promotidos en proyecto source y los aplica congelados a target.
Mide pass@1 antes/después en eval-harness.

Comandos:
  run --source=PATH --target=PATH [--suite=NAME]   — ejecuta experiment
  list                                              — lista experiments previos
  show --id=EID                                     — muestra experiment

Reports persisten en .xdd/frozen-experiments/<exp-id>.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0-dev"

DEFAULT_EXP_DIR = Path(os.environ.get("XDD_FROZEN_EXP_DIR",
                                       str(Path.cwd() / ".xdd" / "frozen-experiments")))


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def list_skills(project_root: Path) -> list[str]:
    """Lista paths SKILL.md en skills/<name>/."""
    skills_dir = project_root / "skills"
    if not skills_dir.exists():
        return []
    return [str(p.relative_to(project_root))
            for p in skills_dir.glob("*/SKILL.md")]


def list_agents(project_root: Path) -> list[str]:
    """Lista paths agents desde registry.json."""
    reg = project_root / "prompts" / "agents" / "registry.json"
    if not reg.exists():
        return []
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
        return [a.get("prompt_file", "") for a in data.get("agents", [])
                if a.get("prompt_file")]
    except (json.JSONDecodeError, OSError):
        return []


def cmd_run(args):
    source = Path(args.source).resolve()
    target = Path(args.target).resolve()
    if not source.exists() or not source.is_dir():
        print(f"[frozen] ERROR: source invalid: {source}", file=sys.stderr)
        return 2
    if not target.exists() or not target.is_dir():
        print(f"[frozen] ERROR: target invalid: {target}", file=sys.stderr)
        return 2

    src_skills = list_skills(source)
    src_agents = list_agents(source)
    tgt_skills_before = list_skills(target)
    tgt_agents_before = list_agents(target)

    exp_id = "exp_" + hashlib.sha256(
        f"{source}-{target}-{utcnow_iso()}".encode()).hexdigest()[:12]

    transferred_skills = []
    transferred_agents = []

    if args.dry_run:
        transferred_skills = [s for s in src_skills if s not in tgt_skills_before]
        transferred_agents = [a for a in src_agents if a not in tgt_agents_before]
    else:
        # Real copy (preserva si target ya tiene)
        for s in src_skills:
            target_path = target / s
            if not target_path.exists():
                src_path = source / s
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_path.parent, target_path.parent,
                                 dirs_exist_ok=True)
                transferred_skills.append(s)

    experiment = {
        "experiment_id": exp_id,
        "timestamp": utcnow_iso(),
        "source": str(source),
        "target": str(target),
        "dry_run": args.dry_run,
        "suite": args.suite,
        "transferred": {
            "skills": transferred_skills,
            "agents_proposed_for_review": [a for a in src_agents
                                            if a not in tgt_agents_before],
        },
        "metrics": {
            "source_skills_count": len(src_skills),
            "target_skills_before": len(tgt_skills_before),
            "target_skills_after": len(tgt_skills_before) + len(transferred_skills),
        },
        "next_steps": [
            f"Run xdd-eval in target: python3 scripts/xdd-eval.py run --suite={args.suite or 'all'} --runs=1",
            f"Compare baseline vs after-transfer in target via xdd-meta-eval compare --last=2",
            f"If improvement ≥ 10%, mark frozen transfer SUCCESS",
        ],
    }

    DEFAULT_EXP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DEFAULT_EXP_DIR / f"{exp_id}.json"
    out_path.write_text(json.dumps(experiment, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(experiment, indent=2))
    else:
        print(f"[frozen] ✓ experiment {exp_id}")
        print(f"  source: {source}")
        print(f"  target: {target}")
        print(f"  transferred skills: {len(transferred_skills)}")
        print(f"  dry_run: {args.dry_run}")
        print(f"  report: {out_path}")
        print("  next steps:")
        for ns in experiment["next_steps"]:
            print(f"    - {ns}")
    return 0


def cmd_list(args):
    if not DEFAULT_EXP_DIR.exists():
        print("[]" if args.json else "[frozen] no experiments yet")
        return 0
    rows = []
    for f in sorted(DEFAULT_EXP_DIR.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            rows.append({
                "experiment_id": r["experiment_id"],
                "timestamp": r["timestamp"],
                "source": r["source"],
                "target": r["target"],
                "skills_transferred": len(r["transferred"]["skills"]),
            })
        except Exception:
            continue
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"[frozen] {len(rows)} experiments:")
        for r in rows:
            print(f"  {r['experiment_id']} {r['timestamp']} "
                  f"skills={r['skills_transferred']}")
    return 0


def cmd_show(args):
    p = DEFAULT_EXP_DIR / f"{args.id}.json"
    if not p.exists():
        print(f"[frozen] not found: {args.id}", file=sys.stderr)
        return 1
    print(p.read_text(encoding="utf-8"))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-frozen-transfer",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version",
                    version=f"xdd-frozen-transfer {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("run", help="Run frozen transfer experiment")
    p_r.add_argument("--source", required=True, help="Source project path")
    p_r.add_argument("--target", required=True, help="Target project path")
    p_r.add_argument("--suite", help="Eval suite to compare")
    p_r.add_argument("--dry-run", action="store_true",
                      help="No file copy, only list what would transfer")
    p_r.add_argument("--json", action="store_true")
    p_r.set_defaults(func=cmd_run)

    p_l = sub.add_parser("list", help="List previous experiments")
    p_l.add_argument("--json", action="store_true")
    p_l.set_defaults(func=cmd_list)

    p_s = sub.add_parser("show", help="Show experiment by ID")
    p_s.add_argument("--id", required=True)
    p_s.set_defaults(func=cmd_show)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
