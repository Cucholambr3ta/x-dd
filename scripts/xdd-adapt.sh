#!/bin/bash
# X-DD Adapter — genera configuración específica por IDE desde SSoT.
# v0.2.0 (S22): MCP eliminado (ADR-0044). Copia REAL de workflows a 7 IDEs.
# No symlinks — Claude Code/Copilot los rechazan (lección S24).
set -eu

# XDD_DATA_DIR: raíz de data dirs inyectada por xdd_cli._run_shell() en modo pipx/wheel.
# Sin ella, BASH_SOURCE/../ en wheel apuntaba a xdd_cli/ sin VERSION → stale "0.1.0-dev".
_XDD_DATA="${XDD_DATA_DIR:-"$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"}"
XDD_VERSION="$(cat "$_XDD_DATA/VERSION" 2>/dev/null || echo "0.1.0-dev")"
ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-adapt — genera config IDE-específica desde el SSoT de X-DD.

Uso:
  bash scripts/xdd-adapt.sh <target> [--dest=PATH] [--trigger=NAME] [--dry-run]
  bash scripts/xdd-adapt.sh --help | --version | --list

Targets soportados:
  claude-code     .claude/commands/*.md (copia real) + CLAUDE.md
  opencode        AGENTS.md + .opencode/command/ + docs/equipo.md
  cursor          .cursor/rules/<trigger>.mdc (@-mention)
  windsurf        .windsurf/workflows/*.md (slash nativos) + rules + README
  vscode-copilot  .github/prompts/*.prompt.md + .vscode/tasks.json + settings.json
  antigravity     .agents/skills/ + .antigravity/README
  codex           ~/.codex/skills/<trigger>-orchestrator/ (SKILL.md + references)
  all             genera todos los 7

Opciones:
  --dest=PATH      destino (default: $PWD)
  --trigger=NAME   trigger custom (default: lee branding de xdd.profile.yml, fallback "xdd")
  --dry-run        no escribe; solo lista
  --list           lista targets + sale
EOF
}

list_targets() {
  cat <<EOF
Targets (todos copia real, sin MCP — ADR-0044):
  claude-code     — slash commands .md reales
  opencode        — AGENTS.md + .opencode/command/ + .agent/workflows/
  cursor          — .cursor/rules/*.mdc (@-mention)
  windsurf        — .windsurf/workflows/*.md + rules
  vscode-copilot  — .github/prompts/*.prompt.md + .vscode/{tasks,settings}.json
  antigravity     — .agents/skills/ (convención plural Antigravity)
  codex           — ~/.codex/skills/<trigger>-orchestrator/
  all             — los 7
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
    claude-code|opencode|cursor|windsurf|vscode-copilot|antigravity|codex|all)
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
  local src="$1" dst="$2"
  if [ $DRY_RUN -eq 1 ]; then emit "$dst (copia real ← $src)"; return; fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  emit "$dst"
}

# Copia workflows SSoT como commands reales. xdd.md → <trigger>.md si trigger != "xdd".
copy_commands() {
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
  if [ ! -e "$DEST/CLAUDE.md" ]; then
    write_file "$DEST/CLAUDE.md" "# Proyecto integrado con X-DD

Workflows: \`.claude/commands/\` (copia real desde \`.agent/workflows/\`).
Memoria: \`memoria.md\` · Lecciones: \`lecciones.md\` · Config: \`xdd.profile.yml\`.

Docs: https://github.com/Cucholambr3ta/x-dd"
  else
    echo "[xdd-adapt] SKIP CLAUDE.md (ya existe)"
  fi
}

adapt_opencode() {
  echo "[xdd-adapt] target: opencode → $DEST/.opencode/command/ + AGENTS.md + docs/equipo.md"
  copy_commands "$DEST/.opencode/command" "md"
  if [ ! -e "$DEST/.agent/workflows" ]; then
    if [ $DRY_RUN -eq 0 ]; then mkdir -p "$DEST/.agent"; ln -sf "$WF_DIR" "$DEST/.agent/workflows"; fi
    emit ".agent/workflows (symlink → $WF_DIR)"
  fi
  if [ ! -f "$DEST/AGENTS.md" ] && [ -f "$ROOT/AGENTS.md" ] && [ $DRY_RUN -eq 0 ]; then
    cp "$ROOT/AGENTS.md" "$DEST/AGENTS.md"
    echo "[xdd-adapt] ✓ AGENTS.md (governance) copiado"
  elif [ -f "$DEST/AGENTS.md" ]; then
    echo "[xdd-adapt] SKIP AGENTS.md (ya existe)"
  fi
  local registry="$ROOT/prompts/agents/registry.json"
  if [ -f "$registry" ] && command -v python3 >/dev/null 2>&1 && [ $DRY_RUN -eq 0 ]; then
    mkdir -p "$DEST/docs"
    python3 - "$registry" "$DEST/docs/equipo.md" <<'PY'
import json, sys
from collections import defaultdict
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
by_cat = defaultdict(list)
for a in data["agents"]:
    by_cat[a["category"]].append(a)
lines = ["# Directorio de Agentes — X-DD", "",
         f"> Auto-generado desde `prompts/agents/registry.json`. {len(data['agents'])} agentes en {len(by_cat)} categorias.", ""]
for cat in sorted(by_cat):
    lines.append(f"## {cat} ({len(by_cat[cat])})")
    lines.append("")
    for a in sorted(by_cat[cat], key=lambda a: a["name"].lower()):
        desc = (a.get("description") or "").split("\n")[0][:120]
        lines.append(f"- **{a['name']}** — {desc}")
    lines.append("")
Path(sys.argv[2]).write_text("\n".join(lines), encoding="utf-8")
print("[xdd-adapt] ✓ docs/equipo.md regenerado")
PY
  fi
}

adapt_cursor() {
  echo "[xdd-adapt] target: cursor → $DEST/.cursor/rules/"
  write_file "$DEST/.cursor/rules/${TRIGGER}.mdc" "$(cat <<EOF
---
description: Orquestador X-DD/$TRIGGER. Pipeline gated 6 fases.
globs:
alwaysApply: false
---
# /$TRIGGER — Orquestador X-DD

Activa con @$TRIGGER. Workflows en \`.agent/workflows/\`.
Lee \`memoria.md\` + \`lecciones.md\` + \`CLAUDE.md\` al iniciar (Constitucion Art. 3 y 9).
EOF
)"
}

adapt_windsurf() {
  local windsurf_home="${XDD_WINDSURF_HOME:-$HOME/.codeium}"
  echo "[xdd-adapt] target: windsurf"
  echo "  · Workflows: $DEST/.windsurf/workflows/"
  echo "  · Rules:     $DEST/.windsurf/rules/${TRIGGER}.md"

  # 1. Workflows nativos — Windsurf descubre .windsurf/workflows/*.md como slash commands.
  copy_commands "$DEST/.windsurf/workflows" "md"

  # Advertir si algún workflow excede 12000 chars (límite Windsurf documentado).
  if [ $DRY_RUN -eq 0 ] && [ -d "$DEST/.windsurf/workflows" ]; then
    local oversize=0
    for wf in "$DEST/.windsurf/workflows"/*.md; do
      [ -f "$wf" ] || continue
      local size; size=$(wc -c < "$wf")
      if [ "$size" -gt 12000 ]; then
        echo "[xdd-adapt] WARN: $(basename "$wf") = ${size} chars > 12000 (limite Windsurf)." >&2
        oversize=$((oversize+1))
      fi
    done
    [ $oversize -eq 0 ] || echo "[xdd-adapt] WARN: ${oversize} workflow(s) exceden limite Windsurf." >&2
  fi

  # 2. Rule @-mention
  write_file "$DEST/.windsurf/rules/${TRIGGER}.md" "$(cat <<EOF
# /$TRIGGER — Orquestador X-DD (Windsurf)

Activa con \`/$TRIGGER\` (slash nativo) o @$TRIGGER.
Pipeline gated 6 fases. Lee memoria/lecciones/CLAUDE al iniciar.
EOF
)"

  # 3. README
  write_file "$DEST/.windsurf/README-xdd.md" "$(cat <<EOF
# X-DD / $TRIGGER en Windsurf

## 1. Workflows nativos (slash commands)
\`.windsurf/workflows/*.md\` — Windsurf los descubre auto desde workspace.
Invoca con \`/$TRIGGER\` u otro nombre de workflow.

## 2. Rule orquestador (@-mention)
\`.windsurf/rules/${TRIGGER}.md\` — Cascade lo carga como contexto persistente.

## Re-sync tras editar SSoT
\`bash scripts/xdd-adapt.sh windsurf --dest=<proyecto>\`
EOF
)"
}

adapt_vscode_copilot() {
  echo "[xdd-adapt] target: vscode-copilot → .github/prompts/ + .vscode/{tasks,settings}.json"
  copy_commands "$DEST/.github/prompts" "prompt.md"
  if [ ! -e "$DEST/.vscode/tasks.json" ]; then
    write_file "$DEST/.vscode/tasks.json" "$(cat <<EOF
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "X-DD: doctor",
      "type": "shell",
      "command": "bash scripts/xdd-doctor.sh",
      "problemMatcher": [],
      "presentation": {"reveal": "always", "panel": "dedicated"}
    },
    {
      "label": "X-DD: start orchestrator",
      "type": "shell",
      "command": "bash scripts/xdd-start.sh",
      "problemMatcher": [],
      "presentation": {"reveal": "always", "panel": "dedicated"}
    },
    {
      "label": "X-DD: list workflows",
      "type": "shell",
      "command": "bash scripts/lint-workflows.sh && ls -1 .agent/workflows/*.md | head -20",
      "problemMatcher": []
    },
    {
      "label": "X-DD: gate validate",
      "type": "shell",
      "command": "python3 scripts/xdd-gate.py status",
      "problemMatcher": []
    }
  ]
}
EOF
)"
  else
    echo "[xdd-adapt] SKIP .vscode/tasks.json (ya existe)"
  fi
  if [ ! -e "$DEST/.vscode/settings.json" ]; then
    write_file "$DEST/.vscode/settings.json" "$(cat <<'EOF'
{
  "terminal.integrated.env.linux": {
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  },
  "terminal.integrated.env.osx": {
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  }
}
EOF
)"
  else
    echo "[xdd-adapt] SKIP .vscode/settings.json (ya existe)"
  fi
}

adapt_antigravity() {
  echo "[xdd-adapt] target: antigravity → $DEST/.agents/skills/"
  local skills_src="$ROOT/skills"
  local skills_dst="$DEST/.agents/skills"
  if [ -d "$skills_src" ]; then
    if [ $DRY_RUN -eq 1 ]; then
      emit ".agents/skills/ (copia skills X-DD)"
    else
      mkdir -p "$skills_dst"
      local count=0
      for skill_dir in "$skills_src"/*/; do
        [ -d "$skill_dir" ] || continue
        cp -r "$skill_dir" "$skills_dst/"
        count=$((count+1))
      done
      echo "[xdd-adapt] ✓ ${count} skills copiadas a $skills_dst/"
    fi
  fi
  write_file "$DEST/.antigravity/README-xdd.md" "$(cat <<EOF
# X-DD/$TRIGGER en Antigravity

## Skills (.agents/skills/ — convension plural Antigravity)
Skills X-DD copiadas a \`.agents/skills/\`. Antigravity las detecta automatico.
Activa con \`/$TRIGGER\` o trigger de cada skill.

## Re-sync
\`bash scripts/xdd-adapt.sh antigravity --dest=<proyecto>\`
EOF
)"
}

adapt_codex() {
  local codex_home="${XDD_CODEX_HOME:-$HOME/.codex/skills}"
  echo "[xdd-adapt] target: codex → $codex_home/${TRIGGER}-orchestrator/"

  if [ $DRY_RUN -eq 1 ]; then
    emit "$codex_home/${TRIGGER}-orchestrator/SKILL.md (orchestrator)"
    emit "$codex_home/${TRIGGER}-orchestrator/references/agents-index.json"
    emit "$codex_home/${TRIGGER}-orchestrator/references/workflows-index.md"
    return
  fi

  local orch_dir="$codex_home/${TRIGGER}-orchestrator"
  mkdir -p "$orch_dir/references" "$orch_dir/scripts"

  cat > "$orch_dir/SKILL.md" <<EOF
---
name: ${TRIGGER}-orchestrator
description: Use when the user starts with /${TRIGGER}, asks to coordinate X-DD pipeline (6 gated phases briefing/spec/plan/build/qa/retro), select specialist agents (180 in registry), execute *-Driven Development workflows (FDD/DDD/BDD/ATDD/TDD/SDD/STDD/SecDD), or invoke the X-DD orchestrator with HMAC gate validation.
---

# X-DD Orchestrator (${TRIGGER})

Coordinate the X-DD pipeline: gated 6-phase development with cryptographic signatures.

## Workflow

1. Clarify the user objective (read constitution Art. 7: zero ambiguity).
2. Identify current phase (briefing/spec/plan/build/qa/retro).
3. Read \`references/workflows-index.md\` to find the relevant workflow.
4. Load only the specialist agents needed (consult \`references/agents-index.json\`).
5. Execute or guide the requested phase.
6. Validate via gate keeper (HMAC-SHA256 signature) before phase transition.
7. Report outcome with audit trail.

## References

- \`references/agents-index.json\` — specialists in 15 categories
- \`references/workflows-index.md\` — workflows + when to invoke each
- \`references/x-dd-constitution.md\` — local law (10 articles)

## Trigger conventions

- \`/${TRIGGER} <objective>\` — invoke pipeline
- \`/${TRIGGER} validate <phase>\` — gate validation
- \`/${TRIGGER} list agents [category]\` — list specialists
EOF

  local registry="$ROOT/prompts/agents/registry.json"
  if [ -f "$registry" ] && command -v python3 >/dev/null 2>&1; then
    python3 - "$registry" "$orch_dir/references/agents-index.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
index = []
for a in data.get("agents", []):
    name = a["name"].lower().replace(" ", "-").replace("_", "-").replace(".", "-")
    name = "".join(c if c.isalnum() or c == "-" else "" for c in name)
    desc = (a.get("description") or "").split("\n")[0][:200]
    index.append({"id": a["id"], "name": name, "category": a["category"],
                  "description": desc, "source_file": a.get("prompt_file", "")})
json.dump(index, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
PY
  fi

  {
    echo "# X-DD Workflows Index"
    echo
    echo "> Auto-generated by xdd-adapt codex."
    echo
    for wf in "$WF_DIR"/*.md; do
      local base; base=$(basename "$wf" .md)
      [ "$base" = "readme" ] || [ "$base" = "README" ] && continue
      local desc
      desc=$(grep -m1 "^description:" "$wf" 2>/dev/null | sed 's/description:[[:space:]]*//' | tr -d '"' | tr -d "'")
      echo "- **${base}** — ${desc:-(sin descripcion)}"
    done
  } > "$orch_dir/references/workflows-index.md"

  [ -f "$ROOT/docs/constitucion.md" ] && cp "$ROOT/docs/constitucion.md" "$orch_dir/references/x-dd-constitution.md"

  cat > "$orch_dir/scripts/invoke_workflow.sh" <<'EOF'
#!/bin/bash
# Lee workflow desde project root (.agent/workflows/<name>.md).
set -eu
PROJECT="${1:-$PWD}"
NAME="${2:?workflow name required}"
WF="$PROJECT/.agent/workflows/${NAME}.md"
[ -f "$WF" ] || { echo "Workflow no encontrado: $WF" >&2; exit 1; }
cat "$WF"
EOF
  chmod +x "$orch_dir/scripts/invoke_workflow.sh"

  if [ -d "$ROOT/skills" ]; then
    local count=0
    for sd in "$ROOT/skills"/*/; do
      [ -d "$sd" ] || continue
      local sname; sname=$(basename "$sd")
      [ -d "$codex_home/$sname" ] && continue
      cp -r "$sd" "$codex_home/"
      count=$((count+1))
    done
    [ $count -gt 0 ] && echo "[xdd-adapt] ✓ ${count} skills X-DD copiadas a $codex_home/"
  fi

  echo "[xdd-adapt] ✓ orchestrator skill: $orch_dir"

  write_file "$DEST/.codex/README-xdd.md" "$(cat <<EOF
# X-DD / ${TRIGGER} en Codex

Skills en \`~/.codex/skills/\` (GLOBAL).
Orchestrator: \`~/.codex/skills/${TRIGGER}-orchestrator/\`

Uso:
  /${TRIGGER} <objetivo>
  /${TRIGGER} validate spec
  /${TRIGGER} list agents engineering
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
    codex)          adapt_codex ;;
  esac
}

if [ "$TARGET" = "all" ]; then
  for t in claude-code opencode cursor windsurf vscode-copilot antigravity codex; do
    run_target "$t"; echo
  done
else
  run_target "$TARGET"
fi

echo
echo "[xdd-adapt] Listo. Target: $TARGET · trigger: /$TRIGGER · dest: $DEST"
[ $DRY_RUN -eq 1 ] && echo "[xdd-adapt] (dry-run — no se escribio nada)"
