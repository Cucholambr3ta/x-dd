#!/bin/bash
# X-DD Adapter — genera configuración específica por IDE desde SSoT.
# v0.1.0 soporta: claude-code, opencode (ADR-0007).
# Otros IDEs (Cursor, Continue, Zed, Cline, Windsurf) consumen vía MCP server (Sprint 6).
set -eu

XDD_VERSION="0.1.0-dev"
ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-adapt — genera config IDE-específica desde el SSoT de X-DD.

Uso:
  bash scripts/xdd-adapt.sh <target> [--dest=PATH] [--dry-run]
  bash scripts/xdd-adapt.sh --help | --version | --list

Targets soportados (v0.1.0):
  claude-code   .claude/commands/ + CLAUDE.md (paths internos del proyecto)
  opencode      AGENTS.md + .agent/workflows/ (links a workflows SSoT)
  all           genera todos los soportados

Opciones:
  --dest=PATH   destino (default: $PWD del proyecto que aplica X-DD)
  --dry-run     no escribe; solo lista qué generaría
  --list        lista los targets soportados y sale

Otros IDEs (Cursor, Continue, Zed, Cline, Windsurf) usan el MCP server
propio de X-DD: ver docs/MCP_INTEGRATION.md.
EOF
}

list_targets() {
  cat <<EOF
Targets v0.1.0:
  claude-code  — slash commands en .claude/commands/ + CLAUDE.md
  opencode     — AGENTS.md + .agent/workflows/ (links al SSoT)
  all          — todos los soportados

Otros IDEs vía MCP server (no requieren adapter):
  cursor       — usa python3 -m xdd-mcp-server en .cursor/mcp.json
  continue     — ~/.continue/config.json
  zed          — ~/.config/zed/settings.json
  cline        — Settings → MCP Servers
  windsurf     — Settings → MCP
EOF
}

TARGET=""
DEST=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-adapt v${XDD_VERSION}"; exit 0 ;;
    --list) list_targets; exit 0 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --dest=*) DEST="${1#--dest=}"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    claude-code|opencode|all)
      TARGET="$1"; shift ;;
    *) echo "[xdd-adapt] ERROR: argumento desconocido: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$TARGET" ]; then
  echo "[xdd-adapt] ERROR: falta <target>." >&2
  usage
  exit 2
fi

DEST="${DEST:-$PWD}"
if [ ! -d "$DEST" ]; then
  echo "[xdd-adapt] ERROR: destino no existe: $DEST" >&2
  exit 2
fi

WF_DIR="$ROOT/.agent/workflows"
if [ ! -d "$WF_DIR" ]; then
  echo "[xdd-adapt] ERROR: no se encuentra $WF_DIR (SSoT de workflows)." >&2
  exit 2
fi

emit() {
  if [ $DRY_RUN -eq 1 ]; then
    echo "  [dry-run] write: $1"
  else
    echo "  ✓ write: $1"
  fi
}

write_file() {
  local target="$1" content="$2"
  if [ $DRY_RUN -eq 1 ]; then
    emit "$target"
    return
  fi
  mkdir -p "$(dirname "$target")"
  printf '%s\n' "$content" > "$target"
  emit "$target"
}

adapt_claude_code() {
  echo "[xdd-adapt] target: claude-code → $DEST/.claude/"

  # Claude Code lee .claude/commands/*.md como slash commands.
  # Reusamos los workflows SSoT vía symlinks (no duplicación).
  if [ $DRY_RUN -eq 0 ]; then
    mkdir -p "$DEST/.claude/commands"
  fi
  local count=0
  for wf in "$WF_DIR"/*.md; do
    local base; base=$(basename "$wf")
    case "$base" in README.md|readme.md) continue ;; esac
    if [ $DRY_RUN -eq 1 ]; then
      emit ".claude/commands/$base (symlink → $wf)"
    else
      ln -sf "$wf" "$DEST/.claude/commands/$base"
    fi
    count=$((count+1))
  done
  echo "[xdd-adapt] ✓ ${count} slash commands enlazados (DRY: comparten SSoT con .agent/workflows/)."

  # CLAUDE.md: si no existe, crear stub que apunta a X-DD root.
  if [ ! -e "$DEST/CLAUDE.md" ]; then
    write_file "$DEST/CLAUDE.md" "$(cat <<'EOF'
# Proyecto integrado con X-DD

Este proyecto usa el framework X-DD (Cross-Driven Development).

- Workflows disponibles: \`.claude/commands/\` (enlazados desde \`.agent/workflows/\`)
- MCP server X-DD: añadí \`xdd-mcp-server\` a tu config MCP (ver \`docs/MCP_INTEGRATION.md\` del repo X-DD)
- Memoria del proyecto: \`memoria.md\`
- Lecciones: \`lecciones.md\`
- Configuración: \`xdd.profile.yml\` (perfil) + \`xdd.config.yml\` (operacional)

Documentación completa: https://github.com/Cucholambr3ta/x-dd
EOF
)"
  else
    echo "[xdd-adapt] SKIP CLAUDE.md (ya existe)"
  fi
}

adapt_opencode() {
  echo "[xdd-adapt] target: opencode → $DEST/AGENTS.md + $DEST/.agent/workflows/"

  # OpenCode lee AGENTS.md como índice + .agent/workflows/ directamente.
  # No necesita symlinks porque .agent/workflows/ ya es la convención.
  if [ ! -e "$DEST/.agent/workflows" ]; then
    if [ $DRY_RUN -eq 0 ]; then
      mkdir -p "$DEST/.agent"
      ln -sf "$WF_DIR" "$DEST/.agent/workflows"
    fi
    emit ".agent/workflows (symlink → $WF_DIR)"
  else
    echo "[xdd-adapt] SKIP .agent/workflows (ya existe)"
  fi

  # AGENTS.md: índice generado desde registry si está disponible.
  local registry="$ROOT/prompts/agents/registry.json"
  if [ -f "$registry" ] && command -v python3 >/dev/null 2>&1; then
    if [ $DRY_RUN -eq 1 ]; then
      emit "AGENTS.md (generado desde registry.json)"
    else
      python3 - "$registry" "$DEST/AGENTS.md" <<'PY'
import json, sys
from collections import defaultdict
from pathlib import Path
registry = Path(sys.argv[1])
output = Path(sys.argv[2])
data = json.loads(registry.read_text(encoding="utf-8"))
agents = data["agents"]
by_cat = defaultdict(list)
for a in agents:
    by_cat[a["category"]].append(a)
lines = []
lines.append("# AGENTS — X-DD")
lines.append("")
lines.append(f"> Generado automáticamente desde el registry de X-DD. {len(agents)} agentes "
             f"en {len(by_cat)} categorías. Consumible por OpenCode, Claude Code, y otros "
             f"orquestadores que entiendan AGENTS.md.")
lines.append("")
lines.append("## Por categoría")
lines.append("")
for cat in sorted(by_cat):
    lines.append(f"### {cat} ({len(by_cat[cat])})")
    lines.append("")
    for a in sorted(by_cat[cat], key=lambda a: a["name"].lower()):
        desc = (a.get("description") or "").split("\n")[0][:120]
        lines.append(f"- **{a['name']}** — {desc}")
    lines.append("")
output.write_text("\n".join(lines), encoding="utf-8")
print(f"[xdd-adapt] ✓ AGENTS.md generado ({len(agents)} agentes)")
PY
    fi
  else
    if [ ! -e "$DEST/AGENTS.md" ]; then
      write_file "$DEST/AGENTS.md" "# AGENTS — X-DD\n\n> Registro de agentes. Ejecutá scripts/migrate-agents-to-registry.py + xdd-adapt.sh opencode para regenerar."
    else
      echo "[xdd-adapt] SKIP AGENTS.md (ya existe)"
    fi
  fi
}

case "$TARGET" in
  claude-code) adapt_claude_code ;;
  opencode)    adapt_opencode ;;
  all)
    adapt_claude_code
    echo
    adapt_opencode
    ;;
esac

echo
echo "[xdd-adapt] Listo. Target: $TARGET, dest: $DEST"
if [ $DRY_RUN -eq 1 ]; then
  echo "[xdd-adapt] (dry-run — no se escribió nada)"
fi
exit 0
