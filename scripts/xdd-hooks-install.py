#!/usr/bin/env python3
"""xdd-hooks-install.py — materializa .agent/hooks/hooks.json (SSoT) en settings.json.

Cierra el gap detectado tras v0.1.1: los hooks de hooks.json estaban definidos y
validados, pero ningún script los traducía al formato que Claude Code lee
(settings.json → hooks.<Event>[].hooks[].command). Por eso `mempalace mine` nunca
se disparaba en Edit/Write.

Sólo se materializan los eventos que Claude Code soporta:
  PreToolUse, PostToolUse, SessionStart, Stop.
Los eventos propios del runtime X-DD (before_agent, before_model, wrap_model_call,
wrap_tool_call, after_model, after_agent) se omiten (los consume xdd-orchestrate,
no Claude Code).

Merge NO destructivo: preserva hooks ajenos (p.ej. caveman). Cada grupo materializado
lleva el marcador `_xdd_id` para poder re-sincronizar idempotentemente (sync borra
los `_xdd_id` previos y reescribe).

Destino: ~/.claude/settings.json (global) por defecto; --project escribe en
<repo>/.claude/settings.json.

Comandos:
  install   — materializa hooks del perfil activo en el settings destino.
  sync      — alias de install (idempotente: limpia los X-DD previos y reescribe).
  status    — muestra qué hooks del perfil están/faltan en el settings destino.
Flags: --profile NAME (o XDD_HOOK_PROFILE; default standard), --project, --dry-run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xdd_common import read_version  # noqa: E402

__version__ = read_version()

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_JSON = REPO_ROOT / ".agent" / "hooks" / "hooks.json"

# Eventos que Claude Code entiende; el resto son del runtime X-DD y se omiten.
CLAUDE_EVENTS = {"PreToolUse", "PostToolUse", "SessionStart", "Stop"}

VALID_PROFILES = ("minimal", "standard", "strict")


def active_profile(cli_value: str | None) -> str:
    p = cli_value or os.environ.get("XDD_HOOK_PROFILE") or "standard"
    if p not in VALID_PROFILES:
        print(f"[hooks] perfil inválido {p!r} (usa {VALID_PROFILES})", file=sys.stderr)
        sys.exit(2)
    return p


def load_catalog() -> dict:
    if not HOOKS_JSON.exists():
        print(f"[hooks] {HOOKS_JSON} no existe", file=sys.stderr)
        sys.exit(2)
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))


def settings_path(project: bool) -> Path:
    if project:
        return REPO_ROOT / ".claude" / "settings.json"
    return Path.home() / ".claude" / "settings.json"


def hook_command(hook: dict) -> str:
    """Comando que ejecuta el script del hook, resoluble desde cualquier CWD.

    El script vive en el repo X-DD. Guarda de existencia: si el CWD no es un repo
    X-DD (no hay .agent/hooks/scripts/), el comando es no-op silencioso. Importa
    porque el settings global aplica a TODOS los repos.

    Para hooks que BLOQUEAN (exit_on_match != 0, típicamente PreToolUse de
    seguridad) se preserva el exit code del script — NO se añade `|| true`, que
    anularía el bloqueo. Para hooks no-bloqueantes/async se traga el error para
    no interrumpir el flujo.
    """
    rel = hook["script"]  # p.ej. .agent/hooks/scripts/post-edit-mempalace-index.sh
    blocking = hook.get("exit_on_match", 0) != 0
    if blocking:
        # Si el script existe, su exit code manda (puede bloquear). Si no, no-op.
        return f'if [ -f "$PWD/{rel}" ]; then bash "$PWD/{rel}"; fi'
    return f'[ -f "$PWD/{rel}" ] && bash "$PWD/{rel}" || true'


def materialized_groups(catalog: dict, profile: str) -> dict[str, list[dict]]:
    """Construye {Event: [matcher-group, ...]} sólo para eventos Claude Code y
    hooks cuyo profile incluye el perfil activo."""
    out: dict[str, list[dict]] = {}
    for event, hooks in catalog.get("hooks", {}).items():
        if event not in CLAUDE_EVENTS:
            continue
        for h in hooks:
            if profile not in h.get("profile", []):
                continue
            entry = {"type": "command", "command": hook_command(h)}
            group: dict = {"_xdd_id": h["id"], "hooks": [entry]}
            # matcher sólo aplica a PreToolUse/PostToolUse; "*" o ausente para los demás.
            if event in ("PreToolUse", "PostToolUse"):
                group["matcher"] = h.get("matcher", "*")
            out.setdefault(event, []).append(group)
    return out


def strip_xdd(settings: dict) -> dict:
    """Quita los grupos X-DD previos (marcados con _xdd_id), preservando ajenos."""
    hooks = settings.get("hooks", {})
    for event in list(hooks.keys()):
        kept = [g for g in hooks[event] if "_xdd_id" not in g]
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    return settings


def merge(settings: dict, groups: dict[str, list[dict]]) -> dict:
    settings = strip_xdd(settings)
    hooks = settings.setdefault("hooks", {})
    for event, gs in groups.items():
        hooks.setdefault(event, []).extend(gs)
    return settings


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[hooks] settings ilegible {path}: {e}", file=sys.stderr)
        sys.exit(2)


def cmd_install(args) -> int:
    profile = active_profile(args.profile)
    catalog = load_catalog()
    groups = materialized_groups(catalog, profile)
    n = sum(len(v) for v in groups.values())
    dest = settings_path(args.project)
    settings = load_settings(dest)
    merged = merge(settings, groups)

    if args.dry_run:
        print(f"[hooks] (dry-run) perfil={profile} → {dest}")
        print(json.dumps(merged.get("hooks", {}), indent=2, ensure_ascii=False))
        print(f"[hooks] materializaría {n} hook(s) X-DD en {len(groups)} evento(s).")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"[hooks] ✓ {n} hook(s) X-DD (perfil {profile}) → {dest}")
    return 0


def cmd_status(args) -> int:
    profile = active_profile(args.profile)
    catalog = load_catalog()
    groups = materialized_groups(catalog, profile)
    dest = settings_path(args.project)
    settings = load_settings(dest)
    present = set()
    for gs in settings.get("hooks", {}).values():
        for g in gs:
            if "_xdd_id" in g:
                present.add(g["_xdd_id"])
    expected = {g["_xdd_id"] for gs in groups.values() for g in gs}
    missing = expected - present
    print(f"[hooks] perfil={profile} destino={dest}")
    print(f"[hooks] esperados: {len(expected)} · presentes: {len(expected & present)} · faltan: {len(missing)}")
    for hid in sorted(missing):
        print(f"  FALTA: {hid}")
    return 1 if missing else 0


def build_parser():
    # Opciones compartidas por todos los subcomandos (aceptadas antes o después).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--profile", help="minimal|standard|strict (o XDD_HOOK_PROFILE)")
    common.add_argument("--project", action="store_true",
                        help="escribe en <repo>/.claude/settings.json en vez de ~/.claude/")
    common.add_argument("--dry-run", action="store_true")

    p = argparse.ArgumentParser(prog="xdd-hooks-install", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                parents=[common])
    p.add_argument("-v", "--version", action="version",
                   version=f"xdd-hooks-install {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("install", parents=[common]).set_defaults(func=cmd_install)
    sub.add_parser("sync", parents=[common]).set_defaults(func=cmd_install)
    sub.add_parser("status", parents=[common]).set_defaults(func=cmd_status)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
