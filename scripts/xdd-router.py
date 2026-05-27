#!/usr/bin/env python3
"""xdd-router.py — Multi-provider LLM router (Sprint 17 + ADR-0019).

Selecciona el provider/model óptimo según task type, costo, latencia, privacy.
Inspirado en Mastra router (NOASSERT) pero implementación propia stdlib.

Providers soportados:
  - claude    (anthropic) — Haiku/Sonnet/Opus
  - openai    (gpt-4o-mini / gpt-4o)
  - local     (Ollama / llama.cpp)
  - none      (no-op)

Comandos:
  list                                  — lista providers configurados
  route --task=TYPE [--max-cost=X]      — sugiere provider+model óptimo
  route --task=TYPE --json              — output JSON para integración

Task types:
  fast_classify     — Haiku/gpt-4o-mini/local (latencia baja)
  code_review       — Sonnet/gpt-4o (calidad alta)
  deep_reasoning    — Opus (capacidad max)
  embedding         — local (privacy + free)
  bulk_extraction   — local o Haiku (volumen alto)

Configuración: xdd.config.yml sección router:
  router:
    default_provider: claude
    fallback: [openai, local]
    task_routes:
      fast_classify: {provider: local, model: llama3-8b}
      code_review:   {provider: claude, model: claude-sonnet-4-6}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

__version__ = "0.1.0-dev"

DEFAULTS = {
    "fast_classify": {"provider": "claude", "model": "claude-haiku-4-5",
                      "rationale": "Lowest latency + cost for classification"},
    "code_review": {"provider": "claude", "model": "claude-sonnet-4-6",
                    "rationale": "Best price/quality for code review"},
    "deep_reasoning": {"provider": "claude", "model": "claude-opus-4-7",
                       "rationale": "Highest capability for complex tasks"},
    "embedding": {"provider": "local", "model": "nomic-embed-text",
                  "rationale": "Privacy + free for vector ops"},
    "bulk_extraction": {"provider": "local", "model": "llama3.1-8b",
                        "rationale": "High-volume tasks; cloud cost prohibitive"},
}

PROVIDER_AVAILABILITY_ENV = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "local": "OLLAMA_HOST",
    "none": None,
}


def load_config(path: str | None) -> dict:
    if not path:
        for candidate in ["xdd.config.yml", "xdd.config.yaml"]:
            if Path(candidate).exists():
                path = candidate
                break
    if not path or not Path(path).exists():
        return {}
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            full = yaml.safe_load(f) or {}
        return full.get("router", {})
    except ImportError:
        return {}


def provider_available(provider: str) -> bool:
    env_var = PROVIDER_AVAILABILITY_ENV.get(provider)
    if env_var is None:
        return provider == "none"
    return bool(os.environ.get(env_var))


def cmd_list(args):
    cfg = load_config(args.config)
    rows = []
    for p in ["claude", "openai", "local", "none"]:
        env = PROVIDER_AVAILABILITY_ENV.get(p)
        available = provider_available(p)
        rows.append({
            "provider": p,
            "env_var": env,
            "available": available,
            "configured_default": cfg.get("default_provider") == p,
        })
    if args.json:
        print(json.dumps({"providers": rows, "config_loaded": bool(cfg)}, indent=2))
    else:
        print(f"[router] Providers ({sum(1 for r in rows if r['available'])} available):")
        for r in rows:
            mark = "✅" if r["available"] else "⚪"
            default = " (default)" if r["configured_default"] else ""
            env_info = f"need {r['env_var']}" if r["env_var"] and not r["available"] else ""
            print(f"  {mark} {r['provider']:<8} {env_info:<24} {default}")
    return 0


def cmd_route(args):
    cfg = load_config(args.config)
    task = args.task
    if not task:
        print("[router] ERROR: --task required", file=sys.stderr)
        return 2

    task_routes = cfg.get("task_routes", {})
    route = task_routes.get(task) or DEFAULTS.get(task)
    if not route:
        print(f"[router] ERROR: unknown task type: {task}", file=sys.stderr)
        print(f"[router] Available tasks: {', '.join(DEFAULTS.keys())}", file=sys.stderr)
        return 2

    chosen_provider = route["provider"]
    chosen_model = route["model"]
    fallback_chain = []

    if not provider_available(chosen_provider):
        fallbacks = cfg.get("fallback", []) or ["claude", "openai", "local", "none"]
        for fb in fallbacks:
            if provider_available(fb):
                fallback_chain.append({"from": chosen_provider, "to": fb,
                                       "reason": f"{chosen_provider} not configured"})
                chosen_provider = fb
                chosen_model = DEFAULTS.get(task, {}).get("model") or "default"
                break

    result = {
        "task": task,
        "provider": chosen_provider,
        "model": chosen_model,
        "rationale": route.get("rationale", ""),
        "fallback_chain": fallback_chain,
        "available": provider_available(chosen_provider),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[router] task={task}")
        print(f"  → provider: {result['provider']}")
        print(f"  → model:    {result['model']}")
        print(f"  → rationale: {result['rationale']}")
        if fallback_chain:
            print(f"  → fallback chain: {fallback_chain}")
    return 0 if result["available"] else 1


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-router", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"xdd-router {__version__}")
    p.add_argument("--config", help="Path xdd.config.yml (default: auto-detect)")
    sub = p.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List configured providers")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_route = sub.add_parser("route", help="Suggest provider+model for task")
    p_route.add_argument("--task", required=True,
                          help="Task type: fast_classify|code_review|deep_reasoning|embedding|bulk_extraction")
    p_route.add_argument("--max-cost", type=float, help="Max $/1M tokens (informational)")
    p_route.add_argument("--json", action="store_true")
    p_route.set_defaults(func=cmd_route)
    return p


def main(argv=None):
    return build_parser().parse_args(argv).func(build_parser().parse_args(argv))


if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(args.func(args))
