#!/usr/bin/env python3
"""xdd-eval.py — Eval-harness para skills/workflows X-DD (Sprint 10).

Valida output de skills/agents contra graders objetivos. Python stdlib pura.

Comandos:
  list                 — lista suites disponibles en evals/
  run --suite=NAME     — corre eval suite específica
  run --all            — corre todas
  run --all --ci       — exit 1 si alguna falla (gate CI)
  show --suite=NAME    — muestra último report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import read_version, utcnow_iso as utcnow  # noqa: E402

__version__ = read_version()

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"


def count_tokens(text: str, ignore_code: bool = False) -> int:
    """Aproximación: 1 token ≈ 4 chars / 0.75 word. Heurística stdlib."""
    if ignore_code:
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]*`", "", text)
    words = len(text.split())
    return int(words / 0.75)


def grader_structural(case: dict, grader: dict) -> tuple[bool, str]:
    output = case.get("output", "")
    pattern = grader.get("regex")
    if not pattern:
        return False, "structural grader requires 'regex' field"
    if re.search(pattern, output):
        return True, "regex matched"
    return False, f"regex '{pattern}' did NOT match output"


def grader_behavioral(case: dict, grader: dict) -> tuple[bool, str]:
    output = case.get("output", "").lower()
    keywords = grader.get("required_keywords") or []
    missing = [k for k in keywords if k.lower() not in output]
    if missing:
        return False, f"missing keywords: {missing}"
    return True, f"all {len(keywords)} keywords present"


def grader_output_match(case: dict, grader: dict) -> tuple[bool, str]:
    if case.get("output") == case.get("expected"):
        return True, "exact match"
    return False, "output != expected"


def grader_pass_at_k(case: dict, grader: dict) -> tuple[bool, str]:
    runs = case.get("runs", [])
    k = grader.get("k", len(runs))
    threshold = grader.get("threshold_pct", 50.0) / 100.0
    if not runs:
        return False, "no runs provided"
    passed = sum(1 for r in runs if r.get("passed"))
    ratio = passed / len(runs)
    if ratio >= threshold:
        return True, f"{passed}/{len(runs)} passed (≥{threshold*100:.0f}%)"
    return False, f"only {passed}/{len(runs)} passed (<{threshold*100:.0f}%)"


def grader_token_reduction(case: dict, grader: dict) -> tuple[bool, str]:
    baseline = case.get(grader.get("baseline_output_field", "baseline"), "")
    compact = case.get(grader.get("test_output_field", "compact"), "")
    threshold_pct = grader.get("threshold_pct", 30.0)
    ignore_code = grader.get("ignore_code_blocks", True)

    base_t = count_tokens(baseline, ignore_code)
    comp_t = count_tokens(compact, ignore_code)
    if base_t == 0:
        return False, "baseline empty"
    reduction = (base_t - comp_t) / base_t * 100
    if reduction >= threshold_pct:
        return True, f"reduction {reduction:.1f}% (≥{threshold_pct}%)"
    return False, f"reduction only {reduction:.1f}% (<{threshold_pct}%)"


def grader_inspect_ai_compat(case: dict, grader: dict) -> tuple[bool, str]:
    """Sprint 20 ADR-0025: ejecutar suite formato Inspect AI.
    Case schema: {input, target, scorers: [match|includes|regex]}.
    Devuelve True si todos los scorers pasan."""
    target = case.get("target", "")
    output = case.get("output", case.get("actual", ""))
    scorers = grader.get("scorers", ["match"])
    results = []
    for scorer in scorers:
        if scorer == "match":
            results.append(output.strip() == target.strip())
        elif scorer == "includes":
            results.append(target.lower() in output.lower())
        elif scorer == "regex":
            try:
                results.append(bool(re.search(target, output)))
            except re.error:
                results.append(False)
        else:
            results.append(False)
    ok = all(results)
    detail = f"scorers={scorers} results={results}"
    return ok, detail


def grader_pass_at_one_external(case: dict, grader: dict) -> tuple[bool, str]:
    """Sprint 20 ADR-0026: external benchmark pass@1 (Terminal-Bench, SWE-bench).
    Espera case con {actual_pass: bool, task_id: str, expected_outcome: pass|fail}."""
    actual = case.get("actual_pass", False)
    expected = case.get("expected_outcome", "pass") == "pass"
    if actual == expected:
        return True, f"pass@1 ok task={case.get('task_id', '?')}"
    return False, f"pass@1 fail task={case.get('task_id', '?')} expected={expected} got={actual}"


GRADERS = {
    "structural": grader_structural,
    "behavioral": grader_behavioral,
    "output_match": grader_output_match,
    "pass_at_k": grader_pass_at_k,
    "token_count_reduction": grader_token_reduction,
    "inspect_ai_compat": grader_inspect_ai_compat,
    "pass_at_one_external": grader_pass_at_one_external,
}


def load_yaml_simple(path: Path) -> dict:
    """Parser YAML mínimo para grader.yaml (no requiere PyYAML)."""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            v = v.strip().strip('"').strip("'")
            # type conversion
            if v.lower() in ("true", "false"):
                v = v.lower() == "true"
            else:
                try:
                    if "." in v: v = float(v)
                    else: v = int(v)
                except ValueError:
                    pass
            out[k.strip()] = v
    return out


def run_suite(suite_dir: Path) -> dict:
    """Carga cases.jsonl + grader.yaml, ejecuta grader, retorna report."""
    cases_file = suite_dir / "cases.jsonl"
    grader_file = suite_dir / "grader.yaml"

    if not cases_file.exists():
        return {"suite": suite_dir.name, "error": "cases.jsonl not found", "passed": False}
    if not grader_file.exists():
        return {"suite": suite_dir.name, "error": "grader.yaml not found", "passed": False}

    grader = load_yaml_simple(grader_file)
    grader_type = grader.get("type")
    if grader_type not in GRADERS:
        return {"suite": suite_dir.name, "error": f"unknown grader type: {grader_type}",
                "passed": False}

    fn = GRADERS[grader_type]
    results = []
    for line in cases_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as e:
            results.append({"passed": False, "reason": f"invalid JSON: {e}"})
            continue
        ok, reason = fn(case, grader)
        results.append({"input": case.get("input", "")[:80], "passed": ok, "reason": reason})

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "suite": suite_dir.name,
        "grader_type": grader_type,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "all_passed": passed == total and total > 0,
        "results": results,
        "timestamp": utcnow(),
    }


def cmd_list(args):
    if not EVALS_DIR.exists():
        print(f"[eval] {EVALS_DIR.relative_to(ROOT)} no existe.")
        return 0
    suites = sorted([d.name for d in EVALS_DIR.iterdir() if d.is_dir()])
    if args.json:
        print(json.dumps({"suites": suites}))
    else:
        print(f"[eval] {len(suites)} suite(s):")
        for s in suites:
            print(f"  - {s}")
    return 0


def cmd_run(args):
    if not EVALS_DIR.exists():
        print(f"[eval] {EVALS_DIR.relative_to(ROOT)} no existe.", file=sys.stderr)
        return 1

    if args.all:
        suites = [d for d in EVALS_DIR.iterdir() if d.is_dir()]
    elif args.suite:
        suites = [EVALS_DIR / args.suite]
        if not suites[0].exists():
            print(f"[eval] suite '{args.suite}' no existe.", file=sys.stderr)
            return 2
    else:
        print("[eval] requiere --suite=NAME o --all", file=sys.stderr)
        return 2

    all_passed = True
    reports = []
    for suite_dir in suites:
        report = run_suite(suite_dir)
        reports.append(report)
        # Persistir
        reports_dir = suite_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        (reports_dir / "latest.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        if not report.get("all_passed"):
            all_passed = False

    if args.json:
        print(json.dumps({"suites_run": len(reports), "all_passed": all_passed,
                          "reports": reports}, indent=2))
    else:
        for r in reports:
            mark = "✓" if r.get("all_passed") else "✗"
            print(f"  {mark} {r['suite']:<30} {r.get('passed',0)}/{r.get('total',0)} "
                  f"({r.get('grader_type','?')})")
            if not r.get("all_passed"):
                for res in r.get("results", []):
                    if not res.get("passed"):
                        print(f"      ✗ {res.get('reason','')}")
        print(f"\n[eval] {len(reports)} suite(s) {'all OK' if all_passed else 'with FAILURES'}.")

    if args.ci and not all_passed:
        return 1
    return 0


def cmd_show(args):
    rpt = EVALS_DIR / args.suite / "reports" / "latest.json"
    if not rpt.exists():
        print(f"[eval] no report for '{args.suite}'. Run first.", file=sys.stderr)
        return 2
    print(rpt.read_text(encoding="utf-8"))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-eval",
        description="Eval-harness para skills/workflows X-DD (Sprint 10).")
    p.add_argument("-v", "--version", action="version", version=f"xdd-eval v{__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    p_l = sub.add_parser("list", help="Lista suites disponibles")
    p_l.add_argument("--json", action="store_true")
    p_l.set_defaults(func=cmd_list)

    p_r = sub.add_parser("run", help="Corre eval suite(s)")
    p_r.add_argument("--suite", help="Nombre de suite específica")
    p_r.add_argument("--all", action="store_true", help="Corre todas")
    p_r.add_argument("--ci", action="store_true", help="exit 1 si alguna falla")
    p_r.add_argument("--json", action="store_true")
    p_r.set_defaults(func=cmd_run)

    p_s = sub.add_parser("show", help="Muestra último report")
    p_s.add_argument("--suite", required=True)
    p_s.set_defaults(func=cmd_show)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
