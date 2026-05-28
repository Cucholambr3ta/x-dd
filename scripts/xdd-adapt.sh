#!/bin/bash
# X-DD Adapter — genera configuración específica por IDE desde SSoT.
# v0.1.0 (Sprint 24): claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity.
# Copia REAL (no symlinks — Claude Code/Copilot los rechazan). MCP auto-config por IDE.
set -eu

XDD_VERSION="0.1.0-dev"
ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-adapt — genera config IDE-específica desde el SSoT de X-DD.

Uso:
  bash scripts/xdd-adapt.sh <target> [--dest=PATH] [--trigger=NAME] [--dry-run]
  bash scripts/xdd-adapt.sh --help | --version | --list

Targets soportados (Sprint 24):
  claude-code     .claude/commands/*.md (copia real) + .mcp.json + CLAUDE.md
  opencode        AGENTS.md + .opencode/command/ + .agent/workflows/
  cursor          .cursor/rules/xdd.mdc + .cursor/mcp.json
  windsurf        .windsurf/rules/xdd.md + MCP note
  vscode-copilot  .github/prompts/*.prompt.md (slash /anmax en Copilot) + .vscode/mcp.json
  antigravity     .antigravity/mcp.json (o mcp config Google IDE)
  all             genera todos los soportados (auto-detect aplica si --dest tiene markers)

Opciones:
  --dest=PATH      destino (default: $PWD)
  --trigger=NAME   trigger custom (default: lee branding de xdd.profile.yml, fallback "xdd")
  --dry-run        no escribe; solo lista
  --list           lista targets + sale
EOF
}

list_targets() {
  cat <<EOF
Targets Sprint 24 (todos copia real + MCP auto-config):
  claude-code     — slash commands .md reales + .mcp.json
  opencode        — AGENTS.md + .opencode/command/ + .agent/workflows/
  cursor          — .cursor/rules/*.mdc + .cursor/mcp.json
  windsurf        — .windsurf/rules/*.md + MCP
  vscode-copilot  — .github/prompts/*.prompt.md (slash /<trigger>) + .vscode/mcp.json
  antigravity     — .antigravity/mcp.json
  all             — los 6
EOF
}

TARGET=""
DEST=""
DRY_RUN=0
TRIGGER=""

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-adapt v${XDD_VERSION}"; exit 0 ;;
    --list) list_targets; exit 0 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --dest=*) DEST="${1#--dest=}"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    --trigger=*) TRIGGER="${1#--trigger=}"; shift ;;
    --trigger) TRIGGER="$2"; shift 2 ;;
    claude-code|opencode|cursor|windsurf|vscode-copilot|antigravity|all)
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

# Resolver trigger: --trigger > branding xdd.profile.yml > "xdd"
resolve_trigger() {
  if [ -n "$TRIGGER" ]; then echo "$TRIGGER"; return; fi
  local profile="$DEST/xdd.profile.yml"
  if [ -f "$profile" ] && command -v python3 >/dev/null 2>&1; then
    local t
    t=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('$profile')) or {}
    print((d.get('branding') or {}).get('orchestrator_trigger', 'xdd'))
except Exception:
    print('xdd')
" 2>/dev/null)
    echo "${t:-xdd}"
  else
    echo "xdd"
  fi
}
TRIGGER="$(resolve_trigger)"

emit() {
  if [ $DRY_RUN -eq 1 ]; then echo "  [dry-run] write: $1"; else echo "  ✓ write: $1"; fi
}

write_file() {
  local target="$1" content="$2"
  if [ $DRY_RUN -eq 1 ]; then emit "$target"; return; fi
  mkdir -p "$(dirname "$target")"
  printf '%s\n' "$content" > "$target"
  emit "$target"
}

copy_real() {
  # copy_real <src> <dst>  — copia archivo REAL (no symlink)
  local src="$1" dst="$2"
  if [ $DRY_RUN -eq 1 ]; then emit "$dst (copia real ← $src)"; return; fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  emit "$dst"
}

# === MCP config generator (formato por IDE) ===
# mcpServers (Claude Code/Cursor/Antigravity) vs servers (VSCode)
gen_mcp_json() {
  # gen_mcp_json <path> <key>   key = mcpServers | servers
  local path="$1" key="$2"
  local content
  content=$(cat <<EOF
{
  "$key": {
    "$TRIGGER": {
      "command": "python3",
      "args": ["-m", "xdd-mcp-server"],
      "cwd": "$DEST"
    }
  }
}
EOF
)
  write_file "$path" "$content"
}

# === Commands reales desde workflows SSoT ===
# Copia los workflows como commands reales. El trigger principal (xdd.md) se
# copia con nombre <trigger>.md.
copy_commands() {
  # copy_commands <dst_dir> <ext>   ext = "md" | "prompt.md"
  local dst_dir="$1" ext="$2"
  local count=0
  for wf in "$WF_DIR"/*.md; do
    local base; base=$(basename "$wf" .md)
    case "$base" in readme|README) continue ;; esac
    local outname
    if [ "$base" = "xdd" ] && [ "$TRIGGER" != "xdd" ]; then
      outname="$TRIGGER"
    else
      outname="$base"
    fi
    copy_real "$wf" "$dst_dir/${outname}.${ext}"
    if [ "$base" = "xdd" ] && [ "$TRIGGER" != "xdd" ] && [ $DRY_RUN -eq 0 ] && command -v python3 >/dev/null 2>&1; then
      python3 - "$dst_dir/${outname}.${ext}" "$TRIGGER" <<'PY'
import sys, re
path, trig = sys.argv[1], sys.argv[2]
t = open(path, encoding="utf-8").read()
t = re.sub(r"description:.*", f"description: Orquestador Principal X-DD (trigger /{trig}).", t, count=1)
t = t.replace("# /xdd", f"# /{trig}", 1)
open(path, "w", encoding="utf-8").write(t)
PY
    fi
    count=$((count+1))
  done
  echo "[xdd-adapt] ✓ ${count} commands (copia real, trigger=/$TRIGGER)."
}

adapt_claude_code() {
  echo "[xdd-adapt] target: claude-code → $DEST/.claude/commands/ (copia real)"
  copy_commands "$DEST/.claude/commands" "md"
  gen_mcp_json "$DEST/.mcp.json" "mcpServers"
  if [ ! -e "$DEST/CLAUDE.md" ]; then
    write_file "$DEST/CLAUDE.md" "# Proyecto integrado con X-DD\n\nWorkflows: \`.claude/commands/\` (copia real desde \`.agent/workflows/\`).\nMCP: \`.mcp.json\` apunta a xdd-mcp-server.\nMemoria: \`memoria.md\` · Lecciones: \`lecciones.md\` · Config: \`xdd.profile.yml\`.\n\nDocs: https://github.com/Cucholambr3ta/x-dd"
  else
    echo "[xdd-adapt] SKIP CLAUDE.md (ya existe)"
  fi
}

adapt_opencode() {
  echo "[xdd-adapt] target: opencode → $DEST/.opencode/command/ + AGENTS.md"
  copy_commands "$DEST/.opencode/command" "md"
  # .agent/workflows symlink al SSoT (OpenCode lo lee directo; symlink OK aquí, no es slash command file)
  if [ ! -e "$DEST/.agent/workflows" ]; then
    if [ $DRY_RUN -eq 0 ]; then mkdir -p "$DEST/.agent"; ln -sf "$WF_DIR" "$DEST/.agent/workflows"; fi
    emit ".agent/workflows (symlink → $WF_DIR)"
  fi
  local registry="$ROOT/prompts/agents/registry.json"
  if [ -f "$registry" ] && command -v python3 >/dev/null 2>&1 && [ $DRY_RUN -eq 0 ]; then
    python3 - "$registry" "$DEST/AGENTS.md" <<'PY'
import json, sys
from collections import defaultdict
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
by_cat = defaultdict(list)
for a in data["agents"]:
    by_cat[a["category"]].append(a)
lines = ["# AGENTS — X-DD", "", f"> {len(data['agents'])} agentes en {len(by_cat)} categorías.", ""]
for cat in sorted(by_cat):
    lines.append(f"### {cat} ({len(by_cat[cat])})")
    for a in sorted(by_cat[cat], key=lambda a: a["name"].lower()):
        desc = (a.get("description") or "").split("\n")[0][:120]
        lines.append(f"- **{a['name']}** — {desc}")
    lines.append("")
Path(sys.argv[2]).write_text("\n".join(lines), encoding="utf-8")
print("[xdd-adapt] ✓ AGENTS.md generado")
PY
  fi
}

adapt_cursor() {
  echo "[xdd-adapt] target: cursor → $DEST/.cursor/"
  # Cursor: rules .mdc (no slash exec, pero @-mention) + MCP config
  write_file "$DEST/.cursor/rules/${TRIGGER}.mdc" "$(cat <<EOF
---
description: Orquestador X-DD/$TRIGGER. Pipeline gated 6 fases.
globs:
alwaysApply: false
---
# /$TRIGGER — Orquestador X-DD

Para activar el orquestador, menciona @$TRIGGER o invoca la tool MCP \`xdd_invoke_workflow\` con name="xdd".

Workflows disponibles en \`.agent/workflows/\`. Lee \`memoria.md\` + \`lecciones.md\` + \`CLAUDE.md\` al iniciar (Constitución Art. 3 y 9).

MCP server: ver \`.cursor/mcp.json\`.
EOF
)"
  gen_mcp_json "$DEST/.cursor/mcp.json" "mcpServers"
}

adapt_windsurf() {
  echo "[xdd-adapt] target: windsurf → $DEST/.windsurf/"
  write_file "$DEST/.windsurf/rules/${TRIGGER}.md" "$(cat <<EOF
# /$TRIGGER — Orquestador X-DD (Windsurf)

Activa el orquestador vía tool MCP \`xdd_invoke_workflow\` (name="xdd") o mención @$TRIGGER.
Pipeline gated 6 fases. Workflows en \`.agent/workflows/\`. Lee memoria/lecciones/CLAUDE al iniciar.

MCP server: añade a Windsurf Settings → MCP la config de abajo.
\`\`\`json
{"mcpServers": {"$TRIGGER": {"command": "python3", "args": ["-m", "xdd-mcp-server"], "cwd": "$DEST"}}}
\`\`\`
EOF
)"
  gen_mcp_json "$DEST/.windsurf/mcp.json" "mcpServers"
}

adapt_vscode_copilot() {
  echo "[xdd-adapt] target: vscode-copilot → $DEST/.github/prompts/ (slash /$TRIGGER) + .vscode/mcp.json"
  # VSCode Copilot: .github/prompts/*.prompt.md → aparecen como /<name> en Copilot Chat
  copy_commands "$DEST/.github/prompts" "prompt.md"
  # VSCode usa key "servers" (no "mcpServers")
  gen_mcp_json "$DEST/.vscode/mcp.json" "servers"
}

adapt_antigravity() {
  echo "[xdd-adapt] target: antigravity → $DEST/.antigravity/mcp.json"
  # Antigravity (Google IDE): consume vía MCP. Sin slash custom markdown.
  gen_mcp_json "$DEST/.antigravity/mcp.json" "mcpServers"
  write_file "$DEST/.antigravity/README-xdd.md" "$(cat <<EOF
# X-DD en Antigravity

Antigravity NO soporta slash commands markdown custom. Consume X-DD vía **MCP server**.

1. Config MCP: \`.antigravity/mcp.json\` (generado). Impórtalo en Antigravity Settings → MCP.
2. Invoca tools MCP:
   - \`xdd_invoke_workflow\` name="xdd" → arranca orquestador /$TRIGGER
   - \`xdd_list_workflows\` → lista workflows
   - \`xdd_list_agents\` → 180 agentes
3. NO escribas /$TRIGGER (no es slash en Antigravity). Usa las tools MCP.
EOF
)"
}

run_target() {
  case "$1" in
    claude-code)    adapt_claude_code ;;
    opencode)       adapt_opencode ;;
    cursor)         adapt_cursor ;;
    windsurf)       adapt_windsurf ;;
    vscode-copilot) adapt_vscode_copilot ;;
    antigravity)    adapt_antigravity ;;
  esac
}

if [ "$TARGET" = "all" ]; then
  for t in claude-code opencode cursor windsurf vscode-copilot antigravity; do
    run_target "$t"; echo
  done
else
  run_target "$TARGET"
fi

echo
echo "[xdd-adapt] Listo. Target: $TARGET · trigger: /$TRIGGER · dest: $DEST"
[ $DRY_RUN -eq 1 ] && echo "[xdd-adapt] (dry-run — no se escribió nada)"
exit 0
