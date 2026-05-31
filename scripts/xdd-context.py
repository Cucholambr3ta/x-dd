#!/usr/bin/env python3
"""xdd-context.py — Context budget metering + check (Sprint 19, ADR-0023).

Estima tokens (heurística stdlib o tiktoken si instalado) vs budget configurado.

Comandos:
  estimate --text=STR | --file=PATH   — estima tokens del texto
  check --tokens=N [--budget=N]      — verifica vs budget (exit codes: 0=ok, 1=warn, 2=block)
  budget --show                       — muestra budget configurado
  budget --set --max-tokens=N         — set budget local
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import make_parser, read_version  # noqa: E402

__version__ = read_version()

# Default budget (Claude Sonnet/Opus 200k context window)
DEFAULT_BUDGET = 200_000
WARNING_THRESHOLD = 0.80  # 80%
BLOCK_THRESHOLD = 0.95    # 95%


def estimate_tokens(text: str) -> int:
    """Heurística stdlib: ~4 chars/token para texto normal. Si tiktoken disponible, úsalo."""
    if not text:
        return 0
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except (ImportError, Exception):
        pass
    # Heurística: aprox 4 chars/token + ajustes
    char_count = len(text)
    word_count = len(re.findall(r"\S+", text))
    # Promedio entre char/4 y word*1.3
    est_char = char_count / 4.0
    est_word = word_count * 1.3
    return int((est_char + est_word) / 2)


def load_budget_config() -> dict:
    """Lee xdd.config.yml sección context_budget si existe."""
    for candidate in ["xdd.config.yml", "xdd.config.yaml"]:
        p = Path(candidate)
        if p.exists():
            try:
                import yaml
                full = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return full.get("context_budget", {})
            except ImportError:
                # Sin yaml dep, parse línea por línea (limitado)
                in_section = False
                cfg = {}
                for line in p.read_text(encoding="utf-8").splitlines():
                    if line.startswith("context_budget:"):
                        in_section = True
                        continue
                    if in_section:
                        if line and not line[0].isspace():
                            break
                        m = re.match(r"\s+(\w+):\s*(.+)", line)
                        if m:
                            k, v = m.group(1), m.group(2).strip()
                            try:
                                cfg[k] = int(v)
                            except ValueError:
                                try:
                                    cfg[k] = float(v)
                                except ValueError:
                                    cfg[k] = v.strip('"\'')
                return cfg
    return {}


def cmd_estimate(args):
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    tokens = estimate_tokens(text)
    if args.json:
        print(json.dumps({"tokens": tokens, "chars": len(text)}))
    else:
        print(f"[ctx] estimated {tokens} tokens ({len(text)} chars)")
    return 0


def cmd_check(args):
    cfg = load_budget_config()
    budget = args.budget or cfg.get("max_tokens") or DEFAULT_BUDGET
    warn_thr = cfg.get("warning_threshold", WARNING_THRESHOLD)
    block_thr = cfg.get("block_threshold", BLOCK_THRESHOLD)
    tokens = args.tokens
    ratio = tokens / budget
    status = "ok"
    rc = 0
    if ratio >= block_thr:
        status = "block"
        rc = 2
    elif ratio >= warn_thr:
        status = "warning"
        rc = 1
    result = {
        "tokens": tokens,
        "budget": budget,
        "ratio": round(ratio, 3),
        "status": status,
        "warning_threshold": warn_thr,
        "block_threshold": block_thr,
    }
    if args.json:
        print(json.dumps(result))
    else:
        emoji = {"ok": "✅", "warning": "⚠️", "block": "🛑"}[status]
        print(f"[ctx] {emoji} {status}: {tokens}/{budget} tokens "
              f"({ratio*100:.1f}% of budget)")
    return rc


def cmd_budget(args):
    cfg = load_budget_config()
    if args.set:
        if not args.max_tokens:
            print("[ctx] ERROR: --set requires --max-tokens", file=sys.stderr)
            return 2
        # Para v0.1.0: instructive output. Escritura real via editar xdd.config.yml.
        print(f"[ctx] To set budget, add to xdd.config.yml:")
        print(f"  context_budget:")
        print(f"    max_tokens: {args.max_tokens}")
        print(f"    warning_threshold: {WARNING_THRESHOLD}")
        print(f"    block_threshold: {BLOCK_THRESHOLD}")
        return 0
    # Show
    budget = cfg.get("max_tokens", DEFAULT_BUDGET)
    warn_thr = cfg.get("warning_threshold", WARNING_THRESHOLD)
    block_thr = cfg.get("block_threshold", BLOCK_THRESHOLD)
    out = {
        "source": "xdd.config.yml" if cfg else "DEFAULT",
        "max_tokens": budget,
        "warning_threshold": warn_thr,
        "block_threshold": block_thr,
        "warn_at_tokens": int(budget * warn_thr),
        "block_at_tokens": int(budget * block_thr),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"[ctx] budget config (source: {out['source']}):")
        print(f"  max_tokens:        {budget:>10,}")
        print(f"  warning_threshold: {warn_thr:>10.0%}  (warn at {out['warn_at_tokens']:,} tokens)")
        print(f"  block_threshold:   {block_thr:>10.0%}  (block at {out['block_at_tokens']:,} tokens)")
    return 0


def build_parser():
    p, _ = make_parser("xdd-context", __doc__, with_subcommands=False, raw_description=True, short_version_flag=False)
    sub = p.add_subparsers(dest="command", required=True)

    p_e = sub.add_parser("estimate", help="Estimate tokens of text")
    p_e.add_argument("--text", help="Inline text")
    p_e.add_argument("--file", help="Read from file")
    p_e.add_argument("--json", action="store_true")
    p_e.set_defaults(func=cmd_estimate)

    p_c = sub.add_parser("check", help="Check tokens vs budget")
    p_c.add_argument("--tokens", type=int, required=True)
    p_c.add_argument("--budget", type=int)
    p_c.add_argument("--json", action="store_true")
    p_c.set_defaults(func=cmd_check)

    p_b = sub.add_parser("budget", help="Show or set budget")
    p_b.add_argument("--show", action="store_true")
    p_b.add_argument("--set", action="store_true")
    p_b.add_argument("--max-tokens", type=int)
    p_b.add_argument("--json", action="store_true")
    p_b.set_defaults(func=cmd_budget)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
