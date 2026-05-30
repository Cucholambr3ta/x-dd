#!/bin/bash
# xdd-organize.sh — Sprint 31 / ADR-0041
# Auto-organiza workspace según reglas declarativas en auto-organize.yml.
# Acciones:
#   - move: mueve archivo a destino canónico (SPEC/DOMAIN/THREATS → docs/)
#   - gitignore_only: añade pattern a .gitignore (no destruye archivo)
#   - gitignore_and_delete: añade + delete (con --apply, no --check)
#   - mkdir_with_gitkeep: crea dirs canónicos + .gitkeep + README placeholder
#
# Comandos:
#   bash xdd-organize.sh check    # preview qué haría (default)
#   bash xdd-organize.sh apply    # ejecuta acciones non-destructive
#   bash xdd-organize.sh apply --confirm-delete  # incluye deletes
#   bash xdd-organize.sh init     # crea estructura canónica (mkdir_with_gitkeep)
#
# Opt-out global: XDD_NO_ORGANIZE=1
set -eu

XDD_VERSION="$(cat "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )/VERSION" 2>/dev/null || echo "0.1.0-dev")"
XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-organize — auto-organiza workspace según reglas declarativas.

Uso:
  bash scripts/xdd-organize.sh <command> [--dest=PATH] [--rules=PATH] [--confirm-delete]
  bash scripts/xdd-organize.sh --help | --version

Comandos:
  check     Preview de acciones que se ejecutarían (no escribe)
  apply     Ejecuta acciones non-destructive (move + gitignore_only)
  init      Crea estructura canónica (mkdir_with_gitkeep)
  all       check + init + apply
  status    Reporte de salud del workspace (qué reglas matchean)

Opciones:
  --dest=PATH        Directorio destino (default: $PWD)
  --rules=PATH       Archivo reglas (default: .agent/auto-organize.yml local,
                     fallback al template del repo X-DD)
  --confirm-delete   Habilita acciones gitignore_and_delete (CON destrucción)

Override: XDD_NO_ORGANIZE=1 desactiva todo el flujo.

Reglas implementadas (ver templates/auto-organize.template.yml):
  - move_to_docs: SPEC/DOMAIN/THREATS → docs/
  - gitignore_framework_pollution: MEJORAS-X-DD.md, INSTALL.md, DEPENDENCIES.md
  - gitignore_framework_copies: prompts/, scripts/, skills/, templates/
  - gitignore_cache: node_modules, __pycache__, .venv, etc.
  - gitignore_secrets: .env, *.pem, *.key (SecDD)
  - move_research_to_subdir: *-inspiration-*.md → docs/research/
  - move_adrs: ADR-*.md → docs/adr/
  - ensure_canonical_dirs: idea/docs/api/design/assets/src/tests
EOF
}

CMD=""
DEST=""
RULES_OVERRIDE=""
CONFIRM_DELETE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-organize v${XDD_VERSION}"; exit 0 ;;
    --dest=*) DEST="${1#--dest=}"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    --rules=*) RULES_OVERRIDE="${1#--rules=}"; shift ;;
    --rules) RULES_OVERRIDE="$2"; shift 2 ;;
    --confirm-delete) CONFIRM_DELETE=1; shift ;;
    check|apply|init|all|status) CMD="$1"; shift ;;
    *) echo "[xdd-organize] ERROR: arg desconocido: $1" >&2; usage; exit 2 ;;
  esac
done

# Opt-out global
if [ "${XDD_NO_ORGANIZE:-0}" = "1" ]; then
  echo "[xdd-organize] SKIP (XDD_NO_ORGANIZE=1)"
  exit 0
fi

[ -z "$CMD" ] && CMD="check"
DEST="${DEST:-$PWD}"
[ ! -d "$DEST" ] && { echo "[xdd-organize] ERROR: dest no existe: $DEST" >&2; exit 2; }

# Resolver archivo de reglas
RULES=""
if [ -n "$RULES_OVERRIDE" ]; then
  RULES="$RULES_OVERRIDE"
elif [ -f "$DEST/.agent/auto-organize.yml" ]; then
  RULES="$DEST/.agent/auto-organize.yml"
elif [ -f "$XDD_ROOT/templates/auto-organize.template.yml" ]; then
  RULES="$XDD_ROOT/templates/auto-organize.template.yml"
else
  echo "[xdd-organize] ERROR: no se encuentra archivo de reglas" >&2
  exit 2
fi

[ ! -f "$RULES" ] && { echo "[xdd-organize] ERROR: reglas no existen: $RULES" >&2; exit 2; }

echo "[xdd-organize] command:    $CMD"
echo "[xdd-organize] dest:       $DEST"
echo "[xdd-organize] rules:      $RULES"
echo

# Ejecutar lógica vía Python (parsing YAML + glob + acciones)
python3 - "$DEST" "$RULES" "$CMD" "$CONFIRM_DELETE" <<'PY'
import os, sys, re, shutil, glob
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[xdd-organize] ERROR: PyYAML requerido (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

dest_root = Path(sys.argv[1]).resolve()
rules_path = Path(sys.argv[2])
cmd = sys.argv[3]
confirm_delete = sys.argv[4] == "1"

rules = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}

ACTIONS_TAKEN = []
ACTIONS_PREVIEWED = []
WARNINGS = []

def in_root_only(rule_block):
    return rule_block.get("from_root_only", False)

def matches_pattern(path: Path, pattern: str) -> bool:
    rel = path.relative_to(dest_root).as_posix() if path.is_relative_to(dest_root) else str(path)
    # glob style match
    if pattern.endswith("/"):
        return path.is_dir() and path.name == pattern.rstrip("/")
    return Path(rel).match(pattern) or path.name == pattern

def append_gitignore(pattern: str):
    gi = dest_root / ".gitignore"
    if gi.exists():
        content = gi.read_text(encoding="utf-8")
        # Idempotente: skip si ya está
        if any(line.strip() == pattern.rstrip("/") or line.strip() == pattern for line in content.splitlines()):
            return False
        with gi.open("a", encoding="utf-8") as f:
            if not content.endswith("\n"):
                f.write("\n")
            f.write(f"{pattern}\n")
    else:
        gi.write_text(f"{pattern}\n", encoding="utf-8")
    return True

def find_matches(patterns, in_root):
    matches = []
    for pat in patterns:
        if in_root:
            # Solo root level
            for entry in dest_root.iterdir():
                if matches_pattern(entry, pat):
                    matches.append(entry)
        else:
            # Para patterns dir-style, normalizar (rglob no soporta trailing slash)
            rglob_pat = pat.rstrip("/")
            for p in dest_root.rglob(rglob_pat):
                rel_parts = p.relative_to(dest_root).parts
                # Skip si DENTRO de .git/.xdd
                if any(part == ".git" for part in rel_parts):
                    continue
                # Permite matchear __pycache__ raíz o subdirs, pero no archivos dentro
                if pat.endswith("/") and not p.is_dir():
                    continue
                matches.append(p)
    return matches

def is_already_in_gitignore(pattern: str) -> bool:
    gi = dest_root / ".gitignore"
    if not gi.exists():
        return False
    return any(line.strip() in (pattern.rstrip("/"), pattern) for line in gi.read_text(encoding="utf-8").splitlines())

dry = cmd in ("check", "status")

# === Regla: move_to_docs ===
for rule_name in ("move_to_docs", "move_research_to_subdir", "move_adrs"):
    block = rules.get(rule_name)
    if not block: continue
    target_dir = block.get("to", "docs/")
    patterns = block.get("patterns", [])
    skip_exists = block.get("skip_if_exists", True)
    for src in find_matches(patterns, in_root_only(block)):
        dst = dest_root / target_dir / src.name
        if dst.exists() and skip_exists:
            continue
        action = f"MOVE {src.relative_to(dest_root)} → {target_dir}{src.name}"
        if dry:
            ACTIONS_PREVIEWED.append(f"[{rule_name}] {action}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            ACTIONS_TAKEN.append(f"[{rule_name}] {action}")

# === Reglas gitignore_* ===
for rule_name in ("gitignore_framework_pollution", "gitignore_framework_copies", "gitignore_cache", "gitignore_secrets"):
    block = rules.get(rule_name)
    if not block: continue
    patterns = block.get("patterns", [])
    action_type = block.get("action", "gitignore_only")
    in_root = in_root_only(block)
    matches = find_matches(patterns, in_root)
    for src in matches:
        rel = src.relative_to(dest_root).as_posix()
        # Determinar pattern a añadir al .gitignore
        gi_pattern = src.name if src.is_dir() else rel
        if src.is_dir() and not gi_pattern.endswith("/"):
            gi_pattern = gi_pattern + "/"
        # Si ya estaba tracked en git, WARN (SecDD)
        if block.get("block_if_already_tracked", False) and (dest_root / ".git").exists():
            # Check si está tracked (best effort)
            try:
                import subprocess
                r = subprocess.run(["git", "-C", str(dest_root), "ls-files", "--error-unmatch", rel],
                                   capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    WARNINGS.append(f"SECURITY: {rel} ya tracked en git (SecDD violation) — ejecutá `git rm --cached '{rel}'` + nuevo commit")
            except Exception:
                pass
        if is_already_in_gitignore(gi_pattern):
            continue  # Idempotente
        if dry:
            ACTIONS_PREVIEWED.append(f"[{rule_name}] GITIGNORE += '{gi_pattern}' (matched: {rel})")
        else:
            append_gitignore(gi_pattern)
            ACTIONS_TAKEN.append(f"[{rule_name}] GITIGNORE += '{gi_pattern}' (matched: {rel})")
        # Si action es gitignore_and_delete y --confirm-delete
        if action_type == "gitignore_and_delete" and confirm_delete and not dry:
            try:
                if src.is_dir():
                    shutil.rmtree(src)
                else:
                    src.unlink()
                ACTIONS_TAKEN.append(f"[{rule_name}] DELETE {rel}")
            except Exception as e:
                WARNINGS.append(f"DELETE falló: {rel} → {e}")
        elif action_type == "gitignore_and_delete" and not confirm_delete:
            if dry:
                ACTIONS_PREVIEWED.append(f"[{rule_name}] (DELETE pendiente — usar `apply --confirm-delete`): {rel}")
            else:
                WARNINGS.append(f"DELETE de '{rel}' requiere --confirm-delete (no se borró)")

# === Regla: ensure_canonical_dirs ===
if cmd in ("init", "all") or (cmd == "apply" and rules.get("ensure_canonical_dirs", {}).get("auto_on_apply", False)):
    block = rules.get("ensure_canonical_dirs", {})
    dirs_to_create = block.get("dirs", [])
    create_readme = block.get("create_readme_placeholder", True)
    for d in dirs_to_create:
        dp = dest_root / d
        if not dp.exists():
            if dry:
                ACTIONS_PREVIEWED.append(f"[ensure_canonical_dirs] MKDIR {d}/")
            else:
                dp.mkdir(parents=True, exist_ok=True)
                # .gitkeep
                (dp / ".gitkeep").touch()
                if create_readme and not (dp / "README.md").exists():
                    placeholder = f"# {d}\n\nDirectorio canónico del proyecto (X-DD scaffolding). Borrá este placeholder al añadir contenido real.\n"
                    (dp / "README.md").write_text(placeholder, encoding="utf-8")
                ACTIONS_TAKEN.append(f"[ensure_canonical_dirs] MKDIR {d}/ (+.gitkeep+README.md)")

# === Output ===
if cmd in ("check", "all", "status"):
    if ACTIONS_PREVIEWED:
        print("Acciones que se ejecutarían (preview):")
        for a in ACTIONS_PREVIEWED:
            print(f"  - {a}")
    else:
        print("No hay acciones pendientes.")
    print()

if ACTIONS_TAKEN:
    print("Acciones ejecutadas:")
    for a in ACTIONS_TAKEN:
        print(f"  ✓ {a}")
    print()

if WARNINGS:
    print("Warnings:", file=sys.stderr)
    for w in WARNINGS:
        print(f"  ⚠ {w}", file=sys.stderr)
    print()

print(f"Total: {len(ACTIONS_TAKEN)} ejecutadas, {len(ACTIONS_PREVIEWED)} pendientes, {len(WARNINGS)} warnings.")
sys.exit(0)
PY
