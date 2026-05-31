#!/bin/bash
# X-DD Init — bootstrap portable con manifest-driven install (Sprint 7).
# Soporta perfiles: minimal | core | developer | security | research | full
# Definidos en manifests/install-profiles.json + install-modules.json.
set -eu

XDD_VERSION="$(cat "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )/VERSION" 2>/dev/null || echo "0.1.0-dev")"

usage() {
  cat <<'EOF'
xdd-init — bootstrap portable de un proyecto X-DD nuevo.

Uso:
  bash scripts/xdd-init.sh [DEST] [--profile=NAME] [--modules=mod1,mod2] [--list-profiles]
  bash scripts/xdd-init.sh --help | --version

Perfiles soportados (manifests/install-profiles.json):
  minimal     Mínimo viable (core + workflows + memory)
  core        Recomendado para empezar (default)
  developer   Completo dev (core + hooks + MCP)
  security    SecDD énfasis (hooks strict + AgentShield cuando disponible)
  research    Investigación (eval-harness + continuous learning)
  full        Todo (incluyendo capacidades futuras de Sprint 9-12)

Opciones:
  --profile=NAME   Perfil de install (default: core)
  --modules=LIST   Override: módulos específicos coma-separados
  --list-profiles  Lista perfiles disponibles y sale

Args:
  DEST  Ruta del proyecto destino (default: $PWD).
        El destino NO puede ser el repo X-DD mismo.

Genera además:
  memoria.md, lecciones.md, xdd.profile.yml (desde templates).
  git init si no es repo.
EOF
}

list_profiles() {
  local manifest="$1"
  if [ -f "$manifest" ] && command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json
d = json.load(open('$manifest'))
for name, p in d['profiles'].items():
    n_mods = len(p['modules'])
    print(f'  {name:<10} ({n_mods} módulos) — {p[\"description\"]}')
"
  else
    echo "  (no se puede listar — manifest o python3 no disponible)"
  fi
}

# Defaults
PROFILE="core"
MODULES_OVERRIDE=""
DEST=""

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-init v${XDD_VERSION}"; exit 0 ;;
    --profile=*) PROFILE="${1#--profile=}"; shift ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --modules=*) MODULES_OVERRIDE="${1#--modules=}"; shift ;;
    --modules) MODULES_OVERRIDE="$2"; shift 2 ;;
    --list-profiles)
      XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"
      echo "Perfiles disponibles:"
      list_profiles "$XDD_ROOT/manifests/install-profiles.json"
      exit 0 ;;
    -*) echo "[xdd-init] ERROR: opción desconocida: $1" >&2; usage; exit 2 ;;
    *) DEST="$1"; shift ;;
  esac
done

# Directorio del repo X-DD (donde vive este script)
XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"
DEST="${DEST:-$PWD}"

if [ "$XDD_ROOT" = "$DEST" ]; then
  echo "[xdd-init] ERROR: el destino no puede ser el propio repo X-DD." >&2
  exit 1
fi

mkdir -p "$DEST"
cd "$DEST"

echo "[xdd-init] Origen: $XDD_ROOT"
echo "[xdd-init] Destino: $DEST"
echo "[xdd-init] Perfil: $PROFILE"

# === Sprint 32 / ADR-0042: lean profile requires wrapper global ===
LEAN_PROFS_MANIFEST="$XDD_ROOT/manifests/install-profiles.json"
if [ "$PROFILE" = "lean" ] && [ -f "$LEAN_PROFS_MANIFEST" ] && command -v python3 >/dev/null 2>&1; then
  REQUIRES_WRAPPER=$(python3 -c "
import json
p = json.load(open('$LEAN_PROFS_MANIFEST'))['profiles'].get('lean', {})
print('1' if p.get('requires_wrapper_global') else '0')
" 2>/dev/null || echo "0")
  if [ "$REQUIRES_WRAPPER" = "1" ]; then
    if [ ! -x "$HOME/.local/bin/xdd-mcp-server" ]; then
      echo "[xdd-init] ⚠ WARN: perfil 'lean' requiere wrapper global xdd-mcp-server pero NO está instalado."
      echo "[xdd-init]   Ejecuta primero: bash $XDD_ROOT/scripts/xdd-mcp-install-global.sh"
      echo "[xdd-init]   Continuando — bootstrap funcionará pero MCP runtime fallará hasta instalar wrapper."
    else
      echo "[xdd-init] ✓ wrapper global xdd-mcp-server detectado (~/.local/bin/xdd-mcp-server)"
    fi
  fi
fi

# Resolver módulos a instalar
PROFILES_MANIFEST="$XDD_ROOT/manifests/install-profiles.json"
MODULES_MANIFEST="$XDD_ROOT/manifests/install-modules.json"
FILES_TO_COPY=""

if [ -n "$MODULES_OVERRIDE" ]; then
  echo "[xdd-init] Módulos override: $MODULES_OVERRIDE"
  if command -v python3 >/dev/null 2>&1 && [ -f "$MODULES_MANIFEST" ]; then
    FILES_TO_COPY=$(python3 -c "
import json, sys
mods = json.load(open('$MODULES_MANIFEST'))['modules']
requested = '$MODULES_OVERRIDE'.split(',')
files = []
for m in requested:
    m = m.strip()
    if m not in mods:
        print(f'ERROR: módulo desconocido: {m}', file=sys.stderr); sys.exit(1)
    files.extend(mods[m]['files'])
print('\n'.join(sorted(set(files))))
" 2>&1) || { echo "$FILES_TO_COPY" >&2; exit 1; }
  fi
elif command -v python3 >/dev/null 2>&1 && [ -f "$PROFILES_MANIFEST" ] && [ -f "$MODULES_MANIFEST" ]; then
  FILES_TO_COPY=$(python3 -c "
import json, sys
profs = json.load(open('$PROFILES_MANIFEST'))['profiles']
mods = json.load(open('$MODULES_MANIFEST'))['modules']
if '$PROFILE' not in profs:
    print(f'ERROR: perfil desconocido: $PROFILE', file=sys.stderr); sys.exit(1)
modules = profs['$PROFILE']['modules']
files = []
for m in modules:
    if m not in mods:
        continue  # módulos futuros (available_from)
    files.extend(mods[m]['files'])
print('\n'.join(sorted(set(files))))
" 2>&1) || { echo "$FILES_TO_COPY" >&2; exit 1; }
else
  # Fallback: comportamiento legacy (sin manifests)
  echo "[xdd-init] WARN: manifests/python3 no disponibles, usando fallback legacy."
  FILES_TO_COPY=".agent .claude prompts scripts templates CLAUDE.md"
fi

echo "[xdd-init] Archivos a instalar:"
echo "$FILES_TO_COPY" | sed 's/^/  - /'

copy_if_absent () {
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    echo "[xdd-init] SKIP existente: $dst"
  else
    if [ -d "$src" ]; then
      mkdir -p "$(dirname "$dst")"
      cp -r "$src" "$dst"
    elif [ -f "$src" ]; then
      mkdir -p "$(dirname "$dst")"
      cp "$src" "$dst"
    else
      echo "[xdd-init] WARN: source no existe: $src" >&2
      return 0
    fi
    echo "[xdd-init] Copiado: $dst"
  fi
}

# Copiar cada archivo/dir según manifest
while IFS= read -r f; do
  [ -z "$f" ] && continue
  copy_if_absent "$XDD_ROOT/$f" "./$f"
done <<< "$FILES_TO_COPY"

# Templates de memoria (siempre, si no existen)
if [ ! -f "./memoria.md" ] && [ -f "$XDD_ROOT/templates/memoria.template.md" ]; then
  cp "$XDD_ROOT/templates/memoria.template.md" "./memoria.md"
  echo "[xdd-init] memoria.md creado desde template."
fi
if [ ! -f "./lecciones.md" ] && [ -f "$XDD_ROOT/templates/lecciones.template.md" ]; then
  cp "$XDD_ROOT/templates/lecciones.template.md" "./lecciones.md"
  echo "[xdd-init] lecciones.md creado desde template."
fi
if [ ! -f "./xdd.profile.yml" ] && [ -f "$XDD_ROOT/templates/xdd.profile.template.yml" ]; then
  cp "$XDD_ROOT/templates/xdd.profile.template.yml" "./xdd.profile.yml"
  echo "[xdd-init] xdd.profile.yml creado desde template."
fi

# Git init si no es repo
if [ ! -d ".git" ]; then
  git init -q
  echo "[xdd-init] Repositorio git inicializado."
fi

# Marcar scripts como ejecutables
chmod +x ./scripts/*.sh ./scripts/hooks/* ./.agent/hooks/scripts/*.sh 2>/dev/null || true

# === Instalar git hook post-commit (re-index MemPalace + GitNexus tras commit) ===
# Antes sólo lo hacía xdd-start.sh; ahora también xdd-init para que quede activo
# desde el bootstrap. Idempotente. Opt-out: XDD_NO_GITHOOK=1.
if [ "${XDD_NO_GITHOOK:-0}" != "1" ] && [ -d ".git" ] && [ -f "./scripts/hooks/post-commit" ]; then
  git config core.hooksPath ./scripts/hooks
  chmod +x ./scripts/hooks/post-commit 2>/dev/null || true
  echo "[xdd-init] ✓ git hook post-commit activado (core.hooksPath=./scripts/hooks)"
fi

# === Auto-detect IDEs + auto-adapt (Sprint 24) ===
# Detecta IDEs presentes (CLI o config dir) y genera config óptima por cada uno.
# Opt-out: XDD_NO_ADAPT=1
if [ "${XDD_NO_ADAPT:-0}" != "1" ] && [ -f "./scripts/xdd-adapt.sh" ]; then
  DETECTED=""
  # claude-code: siempre (orquestador primario). CLI o cualquier proyecto.
  DETECTED="claude-code"
  command -v opencode  >/dev/null 2>&1 && DETECTED="$DETECTED opencode"
  { command -v cursor >/dev/null 2>&1 || [ -d ".cursor" ]; }       && DETECTED="$DETECTED cursor"
  { command -v code   >/dev/null 2>&1 || [ -d ".vscode" ] || [ -d ".github" ]; } && DETECTED="$DETECTED vscode-copilot"
  { command -v windsurf >/dev/null 2>&1 || [ -d ".windsurf" ] || [ -d "$HOME/.codeium" ]; } && DETECTED="$DETECTED windsurf"
  { command -v antigravity >/dev/null 2>&1 || [ -d ".antigravity" ] || [ -d ".idx" ]; } && DETECTED="$DETECTED antigravity"
  { command -v codex >/dev/null 2>&1 || [ -d "$HOME/.codex" ]; } && DETECTED="$DETECTED codex"

  echo "[xdd-init] IDEs detectados para adapt: $DETECTED"
  for ide in $DETECTED; do
    bash ./scripts/xdd-adapt.sh "$ide" --dest="$DEST" 2>&1 | sed 's/^/  /' || \
      echo "  [xdd-init] WARN: adapt $ide falló (no bloqueante)"
  done
  echo "[xdd-init] ✓ IDE adapters generados (copia real + MCP auto-config)."
  echo "[xdd-init]   Override: XDD_NO_ADAPT=1 para saltar. Manual: bash scripts/xdd-adapt.sh all"
fi

# === Materializar hooks X-DD en Claude Code settings (gap post-v0.1.1) ===
# hooks.json (SSoT) → ~/.claude/settings.json. Sin esto, mempalace mine no se dispara
# en Edit/Write. Idempotente, no destructivo (preserva hooks ajenos). Opt-out: XDD_NO_HOOKS=1.
# Se corre desde $XDD_ROOT (no DEST): el script lee $XDD_ROOT/.agent/hooks/hooks.json,
# y el CWD aquí es DEST (que puede no tener scripts/ según el perfil).
if [ "${XDD_NO_HOOKS:-0}" != "1" ] && [ -f "$XDD_ROOT/scripts/xdd-hooks-install.py" ]; then
  if python3 "$XDD_ROOT/scripts/xdd-hooks-install.py" install 2>&1 | sed 's/^/  /'; then
    echo "[xdd-init] ✓ hooks X-DD materializados en ~/.claude/settings.json"
  else
    echo "[xdd-init] WARN: materialización de hooks falló (no bloqueante)"
  fi
  echo "[xdd-init]   Override: XDD_NO_HOOKS=1. Perfil: XDD_HOOK_PROFILE=minimal|standard|strict"
fi

# === Auto-trigger xdd-brand.sh si profile tiene branding custom (Sprint 28 / ADR-0038) ===
# Lección retroactiva: en proyecto piloto multi-IDE, branding declarado en profile NO se aplicó
# automáticamente porque xdd-brand.sh debía invocarse manualmente. Ahora auto-trigger.
# Opt-out: XDD_NO_BRAND=1
if [ "${XDD_NO_BRAND:-0}" != "1" ] && [ -f "./scripts/xdd-brand.sh" ] && [ -f "./xdd.profile.yml" ] && command -v python3 >/dev/null 2>&1; then
  TRIGGER_CUSTOM=$(python3 -c "
import sys
try:
    import yaml
    d = yaml.safe_load(open('./xdd.profile.yml')) or {}
    t = (d.get('branding') or {}).get('orchestrator_trigger', 'xdd')
    print(t if t != 'xdd' else '')
except Exception:
    print('')
" 2>/dev/null)
  if [ -n "$TRIGGER_CUSTOM" ]; then
    echo "[xdd-init] Branding custom detectado (trigger=/$TRIGGER_CUSTOM). Ejecutando xdd-brand..."
    bash ./scripts/xdd-brand.sh "$DEST" 2>&1 | sed 's/^/  /' || \
      echo "  [xdd-init] WARN: xdd-brand falló (no bloqueante). Re-ejecuta manual: bash scripts/xdd-brand.sh ."
    echo "[xdd-init] ✓ Branding aplicado (override: XDD_NO_BRAND=1 para saltar)."
  fi
fi

# === Init gate keeper (Sprint 28 / ADR-0038) ===
# Lección retroactiva: gate keeper criptográfico NO se inicializó en bootstrap.
# Resultado: cierres "APROBADO" verbal sin firma HMAC.
if [ "${XDD_NO_GATE_INIT:-0}" != "1" ] && [ -f "./scripts/xdd-gate.py" ] && [ ! -d "./.xdd" ] && command -v python3 >/dev/null 2>&1; then
  python3 ./scripts/xdd-gate.py init 2>&1 | sed 's/^/  /' || \
    echo "[xdd-init] WARN: xdd-gate init falló (no bloqueante). Re-ejecuta: python3 scripts/xdd-gate.py init"
  echo "[xdd-init] ✓ Gate keeper HMAC inicializado en .xdd/ (override: XDD_NO_GATE_INIT=1)."
fi

# === Auto-organize bootstrap (Sprint 31 / ADR-0041) ===
# Lección retroactiva: scaffolding 7 dirs canónicos no auto-generado en bootstrap.
# Resultado: SPEC/DOMAIN/THREATS en root, sin docs/. Repo contaminado.
# Auto-aplica: ensure_canonical_dirs + gitignore_cache + gitignore_secrets.
# NO destruye nada (apply mode, no --confirm-delete).
if [ "${XDD_NO_ORGANIZE:-0}" != "1" ] && [ -f "$XDD_ROOT/scripts/xdd-organize.sh" ]; then
  bash "$XDD_ROOT/scripts/xdd-organize.sh" init --dest=. 2>&1 | sed 's/^/  /' || \
    echo "[xdd-init] WARN: xdd-organize init falló (no bloqueante)."
  bash "$XDD_ROOT/scripts/xdd-organize.sh" apply --dest=. 2>&1 | sed 's/^/  /' || true
  echo "[xdd-init] ✓ Auto-organize aplicado (estructura canónica + .gitignore base)."
  echo "[xdd-init]   Override: XDD_NO_ORGANIZE=1. Manual: bash scripts/xdd-organize.sh check"
fi

cat <<EOF

[xdd-init] ✓ Bootstrap completado en: $DEST
[xdd-init]   Perfil: $PROFILE

Siguientes pasos:
  1. cd "$DEST"
  2. Edita memoria.md con la identidad del proyecto.
  3. Edita xdd.profile.yml: declara tipo de producto y stacks.
  4. Verifica el entorno:   bash ./scripts/xdd-doctor.sh
  5. Arranca X-DD:          bash ./scripts/xdd-start.sh

Otros perfiles disponibles: bash ./scripts/xdd-init.sh --list-profiles
EOF
