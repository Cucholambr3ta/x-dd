#!/bin/bash
# xdd-global-install — Sprint 29 / ADR-0039: registra orquestador (/<trigger>) GLOBAL
# en los IDEs soportados. Permite invocar /<trigger> desde cualquier dir, incluso
# directorios vacíos. Self-bootstrap: si dir no tiene xdd.profile.yml, /<trigger>
# ejecuta xdd-init.sh automáticamente.
#
# Patrón: paridad Codex (~/.codex/skills/<trigger>-orchestrator/) extendido a los 6 IDEs.
#
# Lección retroactiva (proyecto piloto multi-IDE): usuario quería invocar /<trigger> en
# directorio nuevo sin pre-bootstrap. Sprint 28 PRE-FLIGHT bloqueaba con ABORT. Sprint 29
# permite self-bootstrap = workflow detecta dir vacío y dispara xdd-init.sh inline.
set -eu

XDD_VERSION="0.1.0-dev"
XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-global-install — registra orquestador X-DD (/<trigger>) GLOBAL en los IDEs.

Uso:
  bash scripts/xdd-global-install.sh [--trigger=NAME] [--ides=LIST] [--uninstall] [--check] [--dry-run]
  bash scripts/xdd-global-install.sh --help | --version

Opciones:
  --trigger=NAME   trigger del orquestador (default: xdd)
  --ides=LIST      IDEs específicos coma-separados (default: auto-detect)
                   Valores: claude-code,opencode,cursor,windsurf,vscode-copilot,codex,all
  --uninstall      remueve global install previo
  --check          verifica estado del global install (no escribe)
  --dry-run        muestra qué haría sin escribir

Ejemplos:
  bash scripts/xdd-global-install.sh                          # auto-detect, trigger=xdd
  bash scripts/xdd-global-install.sh --trigger=helios         # custom trigger global
  bash scripts/xdd-global-install.sh --ides=claude-code,cursor
  bash scripts/xdd-global-install.sh --check                  # ver qué está instalado

Resultado por IDE:
  claude-code     ~/.claude/commands/<trigger>.md (slash command global)
  opencode        ~/.config/opencode/command/<trigger>.md
  cursor          ~/.cursor/rules/<trigger>.mdc (rule global con @mention)
  windsurf        ~/.codeium/workflows/<trigger>.md
  vscode-copilot  ~/.config/Code/User/prompts/<trigger>.prompt.md
  codex           ~/.codex/skills/<trigger>-orchestrator/SKILL.md (ya soporta esto)

Self-bootstrap behaviour:
  Cuando invocas /<trigger> en dir sin xdd.profile.yml, el orquestador detecta y
  pregunta si querés ejecutar xdd-init.sh automático. Si confirmas, bootstrap full
  ocurre inline antes de continuar con la meta del día.
EOF
}

TRIGGER="xdd"
IDES_OVERRIDE=""
UNINSTALL=0
CHECK=0
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-global-install v${XDD_VERSION}"; exit 0 ;;
    --trigger=*) TRIGGER="${1#--trigger=}"; shift ;;
    --trigger) TRIGGER="$2"; shift 2 ;;
    --ides=*) IDES_OVERRIDE="${1#--ides=}"; shift ;;
    --ides) IDES_OVERRIDE="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    --check) CHECK=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "ERROR: arg desconocido: $1" >&2; usage; exit 2 ;;
  esac
done

# Detect IDEs (similar a xdd-init.sh:191-199)
detect_ides() {
  local detected=""
  command -v claude     >/dev/null 2>&1 && detected="$detected claude-code"
  command -v opencode   >/dev/null 2>&1 && detected="$detected opencode"
  { command -v cursor >/dev/null 2>&1 || [ -d "$HOME/.cursor" ]; }              && detected="$detected cursor"
  { command -v windsurf >/dev/null 2>&1 || [ -d "$HOME/.codeium" ]; }           && detected="$detected windsurf"
  { command -v code >/dev/null 2>&1 || [ -d "$HOME/.config/Code" ]; }           && detected="$detected vscode-copilot"
  { command -v codex >/dev/null 2>&1 || [ -d "$HOME/.codex" ]; }                && detected="$detected codex"
  echo "$detected"
}

if [ -n "$IDES_OVERRIDE" ]; then
  if [ "$IDES_OVERRIDE" = "all" ]; then
    IDES="claude-code opencode cursor windsurf vscode-copilot codex"
  else
    IDES=$(echo "$IDES_OVERRIDE" | tr ',' ' ')
  fi
else
  IDES=$(detect_ides)
fi

emit() {
  if [ $DRY_RUN -eq 1 ]; then
    echo "  [dry-run] $1"
  else
    echo "  ✓ $1"
  fi
}

write_orchestrator_md() {
  # Genera el contenido del orquestador global con self-bootstrap.
  # $1 = path destino, $2 = trigger
  local dst="$1" trig="$2"
  local content
  content=$(cat <<EOF
---
description: Orquestador Principal X-DD/$trig — global (Sprint 29 / ADR-0039). Self-bootstrap si dir vacío.
---
# /$trig — Orquestador X-DD GLOBAL

> **Sprint 29 enforcement:** este orquestador está instalado GLOBAL — funciona desde cualquier directorio.

## 0. SELF-BOOTSTRAP CHECK (NUEVO Sprint 29)

Antes de cualquier acción:
1. Verifica si \`xdd.profile.yml\` existe en el dir actual.
2. Si NO existe:
   - **Pregunta al usuario:** "Este directorio no tiene X-DD inicializado. ¿Bootstrap ahora? Perfil sugerido: developer. [SI/NO/perfil-custom]"
   - Si responde **SI**: ejecuta \`bash $XDD_ROOT/scripts/xdd-init.sh . --profile=developer\` inline.
   - Si responde **NO**: aborta con mensaje "Ejecuta \`bash $XDD_ROOT/scripts/xdd-init.sh . --profile=<X>\` manualmente".
   - Si responde **perfil-custom**: usa ese perfil.
3. Si EXISTE: continúa con PRE-FLIGHT BOOTSTRAP estándar (Sección 1).

## 1. PRE-FLIGHT BOOTSTRAP (Sprint 28 / ADR-0038 — ENFORCEMENT)

> Bloqueante. NO procedas a Sección 2 si cualquier check falla.

### 1.1 Verifica BOOTSTRAP previo
- Si \`.xdd/\` no existe → \`python3 $XDD_ROOT/scripts/xdd-gate.py init\`.
- Si \`xdd.profile.yml\` declara \`branding.orchestrator_trigger != "xdd"\` Y NO existe \`.claude/branding.json\` → \`bash $XDD_ROOT/scripts/xdd-brand.sh .\`.

### 1.2 MEMORY SEAL & EXPERIENCE SYNC (Art. 3 & 9)
- Lee \`memoria.md\`, \`lecciones.md\` y \`CLAUDE.md\` de la raíz sin preguntar.
- Carga \`docs/equipo.md\` (directorio de agentes).
- Reporta lecciones previas relevantes a la meta del día.

### 1.3 AUDIT obligatorio
- \`bash $XDD_ROOT/scripts/xdd-doctor.sh\` — NO continuar si exit != 0.
- MemPalace search si dominio especificado.

## 2. MISIÓN Y PREGUNTAS CLAVE (PM MODE)
Como **Project Manager**, dirige la orquesta técnica — NO escribas código directo.

1. Resumen ultra-rápido: "Ayer nos quedamos en [X]."
2. Pregunta: "¿Cuál es la meta del día?"
3. Análisis de viabilidad → propón subagente adecuado.

## 3. DELEGACIÓN ESPECIALIZADA
- **Estrategia**: Product-Manager
- **Arquitectura**: Architect
- **Dominio**: Domain-Expert
- **UI/Features**: Builder
- **Calidad**: QA-Reviewer
- **Seguridad**: SecOps
- **Mantenimiento**: Maintainer

## 4. GATED PIPELINE (ART. 2)
Exige "APROBADO" antes de cambios persistentes o masivos.

## 5. CIERRE
Invoca \`/cierre-fase\` para resumen + lecciones.md update + gate approve HMAC.

---
*X-DD Global Orchestrator — Sprint 29 / ADR-0039*
EOF
)
  if [ $DRY_RUN -eq 1 ]; then
    emit "write: $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  printf '%s\n' "$content" > "$dst"
  emit "write: $dst"
}

install_claude_code() {
  local dst="$HOME/.claude/commands/${TRIGGER}.md"
  echo "[xdd-global] claude-code → $dst"
  write_orchestrator_md "$dst" "$TRIGGER"
}

install_opencode() {
  local dst="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/command/${TRIGGER}.md"
  echo "[xdd-global] opencode → $dst"
  write_orchestrator_md "$dst" "$TRIGGER"
}

install_cursor() {
  local dst="$HOME/.cursor/rules/${TRIGGER}.mdc"
  echo "[xdd-global] cursor → $dst"
  # Cursor rules .mdc tiene frontmatter específico
  local content
  content=$(cat <<EOF
---
description: Orquestador X-DD/$TRIGGER GLOBAL — self-bootstrap si dir vacío. Sprint 29.
globs:
alwaysApply: false
---
# /$TRIGGER — Orquestador X-DD GLOBAL

Para activar: @$TRIGGER o invoca tool MCP \`xdd_invoke_workflow\` name="xdd".

## Self-bootstrap (Sprint 29)
Si dir actual NO tiene \`xdd.profile.yml\`: pregunta al usuario si bootstrap. Si SI: \`bash $XDD_ROOT/scripts/xdd-init.sh . --profile=developer\`.

## Pipeline gated 6 fases
Workflows en \`.agent/workflows/\` del proyecto OR via MCP \`xdd_invoke_workflow\`.

MCP server: ver \`~/.cursor/mcp.json\` o \`.cursor/mcp.json\` project.
EOF
)
  if [ $DRY_RUN -eq 1 ]; then
    emit "write: $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  printf '%s\n' "$content" > "$dst"
  emit "write: $dst"
}

install_windsurf() {
  local dst="$HOME/.codeium/workflows/${TRIGGER}.md"
  echo "[xdd-global] windsurf → $dst"
  write_orchestrator_md "$dst" "$TRIGGER"
}

install_vscode_copilot() {
  # VSCode + Copilot Chat usa prompt files. Path global: ~/.config/Code/User/prompts/<name>.prompt.md
  # https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files
  local prompts_dir="${XDG_CONFIG_HOME:-$HOME/.config}/Code/User/prompts"
  local dst="$prompts_dir/${TRIGGER}.prompt.md"
  echo "[xdd-global] vscode-copilot → $dst"
  write_orchestrator_md "$dst" "$TRIGGER"
}

install_codex() {
  # Codex ya tiene patrón global (Sprint 24 / ADR-0036). Reusa adapt_codex sin --dest.
  local codex_skills="${XDD_CODEX_HOME:-$HOME/.codex/skills}"
  echo "[xdd-global] codex → $codex_skills/${TRIGGER}-orchestrator/ (ya soportado vía xdd-adapt codex)"
  if [ $DRY_RUN -eq 1 ]; then
    emit "delegate: bash $XDD_ROOT/scripts/xdd-adapt.sh codex --trigger=$TRIGGER --dry-run"
  else
    # Codex no necesita --dest (skills global). Solo trigger.
    bash "$XDD_ROOT/scripts/xdd-adapt.sh" codex --dest="$XDD_ROOT" --trigger="$TRIGGER" 2>&1 | sed 's/^/  /' || true
  fi
}

uninstall_one() {
  local ide="$1"
  case "$ide" in
    claude-code)    rm -f "$HOME/.claude/commands/${TRIGGER}.md" 2>/dev/null || true ;;
    opencode)       rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/command/${TRIGGER}.md" 2>/dev/null || true ;;
    cursor)         rm -f "$HOME/.cursor/rules/${TRIGGER}.mdc" 2>/dev/null || true ;;
    windsurf)       rm -f "$HOME/.codeium/workflows/${TRIGGER}.md" 2>/dev/null || true ;;
    vscode-copilot) rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/Code/User/prompts/${TRIGGER}.prompt.md" 2>/dev/null || true ;;
    codex)          rm -rf "${XDD_CODEX_HOME:-$HOME/.codex/skills}/${TRIGGER}-orchestrator" 2>/dev/null || true ;;
  esac
  echo "  ✓ $ide uninstalled"
}

check_one() {
  local ide="$1" path=""
  case "$ide" in
    claude-code)    path="$HOME/.claude/commands/${TRIGGER}.md" ;;
    opencode)       path="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/command/${TRIGGER}.md" ;;
    cursor)         path="$HOME/.cursor/rules/${TRIGGER}.mdc" ;;
    windsurf)       path="$HOME/.codeium/workflows/${TRIGGER}.md" ;;
    vscode-copilot) path="${XDG_CONFIG_HOME:-$HOME/.config}/Code/User/prompts/${TRIGGER}.prompt.md" ;;
    codex)          path="${XDD_CODEX_HOME:-$HOME/.codex/skills}/${TRIGGER}-orchestrator/SKILL.md" ;;
  esac
  if [ -f "$path" ] || [ -d "$(dirname "$path")" -a "$ide" = "codex" -a -f "$path" ]; then
    echo "  ✓ $ide: $path"
  else
    echo "  ✗ $ide: NOT INSTALLED ($path)"
  fi
}

run_one() {
  local ide="$1"
  case "$ide" in
    claude-code)    install_claude_code ;;
    opencode)       install_opencode ;;
    cursor)         install_cursor ;;
    windsurf)       install_windsurf ;;
    vscode-copilot) install_vscode_copilot ;;
    codex)          install_codex ;;
    *) echo "[xdd-global] WARN: IDE desconocido: $ide" >&2 ;;
  esac
}

# === Main ===
echo "[xdd-global] xdd-global-install v${XDD_VERSION}"
echo "[xdd-global] trigger: /$TRIGGER"
echo "[xdd-global] IDEs:  $IDES"

if [ -z "$IDES" ]; then
  echo "[xdd-global] WARN: ningún IDE detectado. Usa --ides=all para forzar." >&2
  exit 0
fi

if [ $CHECK -eq 1 ]; then
  echo "[xdd-global] === Check (qué está instalado) ==="
  for ide in $IDES; do
    check_one "$ide"
  done
  exit 0
fi

if [ $UNINSTALL -eq 1 ]; then
  echo "[xdd-global] === Uninstalling /$TRIGGER global ==="
  for ide in $IDES; do
    uninstall_one "$ide"
  done
  exit 0
fi

echo "[xdd-global] === Installing /$TRIGGER global ==="
for ide in $IDES; do
  run_one "$ide"
  echo
done

cat <<EOF

[xdd-global] ✓ Global install completo.

Próximos pasos:
  1. Abre cualquier IDE soportado
  2. Crea/abre cualquier directorio (incluso vacío)
  3. Invoca: /$TRIGGER quiero armar un proyecto X-DD
  4. El orquestador detectará dir vacío y propondrá bootstrap auto

Verifica estado:
  bash scripts/xdd-global-install.sh --check

Override portabilidad:
  XDG_CONFIG_HOME=<path>  (afecta opencode + vscode paths)
  XDD_CODEX_HOME=<path>   (afecta codex skills global)

Re-aplica con trigger custom:
  bash scripts/xdd-global-install.sh --trigger=miproyecto

Uninstall:
  bash scripts/xdd-global-install.sh --uninstall --trigger=$TRIGGER
EOF
[ $DRY_RUN -eq 1 ] && echo "[xdd-global] (dry-run — no se escribió nada)"
exit 0
