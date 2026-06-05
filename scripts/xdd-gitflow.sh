#!/usr/bin/env bash
# xdd-gitflow.sh — GitFlow automatizado por sprint para proyectos X-DD.
#
# Subcomandos:
#   setup   --mode=dev|collab [--create|--local|--remote=URL] [--name=N] [--visibility=private|public]
#   sprint-start --sprint=NN --title=<titulo>  Crea branch feature/sprint-NN-<titulo>
#   sprint-close --sprint=NN                   Crea PR y verifica merge antes de continuar
#   pre-push                                    Hook pre-push: gitignore + gitleaks
#
# Variables de entorno:
#   XDD_GITFLOW_MODE=dev|collab     Override de modo (default: lee .xdd/gitflow.mode)
#   XDD_SKIP_PREPUSH=1              Salta checks pre-push (dev-local, warning visible)
#   XDD_SKIP_GITLEAKS=1             Salta gitleaks (si no instalado, warning visible)

set -euo pipefail

VERSION="1.0.0"
# XDD_DIR relativo al CWD (proyecto que se gestiona), no al script
XDD_DIR="$(pwd)/.xdd"
GITFLOW_STATE="${XDD_DIR}/gitflow.mode"

# ── helpers ───────────────────────────────────────────────────────────────────

log()  { echo "[xdd-gitflow] $*"; }
warn() { echo "[xdd-gitflow] WARN: $*" >&2; }
err()  { echo "[xdd-gitflow] ERROR: $*" >&2; exit 1; }

# Artefactos X-DD que NO deben entrar al repo del producto
XDD_GITIGNORE_PATTERNS=(
  "acuerdos/"
  "memoria.md"
  "lecciones.md"
  ".xdd/"
  "xdd.profile.yml"
  "AGENT_MEMORY.md"
  "memory/"
  "dialog/"
  "tool_result/"
)

sprint_num() {
  printf "%02d" "$1"
}

get_mode() {
  if [ -n "${XDD_GITFLOW_MODE:-}" ]; then
    echo "$XDD_GITFLOW_MODE"
    return
  fi
  if [ -f "$GITFLOW_STATE" ]; then
    cat "$GITFLOW_STATE"
  else
    echo "dev"
  fi
}

save_mode() {
  mkdir -p "$XDD_DIR"
  echo "$1" > "$GITFLOW_STATE"
  chmod 600 "$GITFLOW_STATE"
}

GITFLOW_REMOTE_STATE="${XDD_DIR}/gitflow.remote"

_save_remote_mode() {
  # "remote" o "local" — sprint-close consulta esto para decidir si hace push
  mkdir -p "$XDD_DIR"
  echo "$1" > "$GITFLOW_REMOTE_STATE"
  chmod 600 "$GITFLOW_REMOTE_STATE"
}

_get_remote_mode() {
  [ -f "$GITFLOW_REMOTE_STATE" ] && cat "$GITFLOW_REMOTE_STATE" || echo "remote"
}

_create_remote_repo() {
  # Crea repo en GitHub de forma autonoma (gh repo create). ADR-0052.
  local name="$1" visibility="$2"
  command -v gh >/dev/null 2>&1 || err "gh CLI no instalado. Instalar: https://cli.github.com/ o usar --remote=URL"
  gh auth status >/dev/null 2>&1 || err "gh no autenticado. Correr: gh auth login"

  # Nombre por defecto: nombre del directorio actual
  [ -z "$name" ] && name="$(basename "$(pwd)")"

  log "Creando repo GitHub: $name ($visibility)..."
  if gh repo create "$name" --"$visibility" --source=. --remote=origin 2>/dev/null; then
    local url
    url="$(git remote get-url origin 2>/dev/null || echo "?")"
    log "Repo creado y origin configurado: $url"
  else
    err "gh repo create fallo. Verificar que el nombre '$name' no exista ya en tu cuenta."
  fi
}

ensure_git() {
  git rev-parse --git-dir >/dev/null 2>&1 || err "No es un repositorio git. Ejecutar desde la raiz del proyecto."
}

current_branch() {
  git rev-parse --abbrev-ref HEAD
}

# ── setup ─────────────────────────────────────────────────────────────────────

cmd_setup() {
  local mode="dev"
  local remote=""
  local create=0
  local local_only=0
  local repo_name=""
  local visibility="private"

  while [ $# -gt 0 ]; do
    case "$1" in
      --mode=*) mode="${1#*=}"; shift ;;
      --remote=*) remote="${1#*=}"; shift ;;
      --create) create=1; shift ;;
      --local) local_only=1; shift ;;
      --name=*) repo_name="${1#*=}"; shift ;;
      --visibility=*) visibility="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done

  [ "$mode" = "dev" ] || [ "$mode" = "collab" ] || err "Modo invalido: $mode. Usar dev o collab."
  [ "$visibility" = "private" ] || [ "$visibility" = "public" ] || err "Visibility invalida: usar private o public."

  ensure_git

  log "Configurando GitFlow modo=$mode"

  # Asegurar branch main existe
  if ! git rev-parse --verify main >/dev/null 2>&1; then
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
      # Repo vacio — crear commit inicial
      git checkout -b main
      git commit --allow-empty -m "chore: init repo"
      log "Commit inicial creado en main."
    else
      git checkout -b main 2>/dev/null || git checkout main
    fi
  fi

  # Asegurar branch develop existe
  if ! git rev-parse --verify develop >/dev/null 2>&1; then
    git checkout main
    git checkout -b develop
    log "Branch develop creada."
  fi

  # Resolucion del remoto: local-only / crear-nube / remoto-existente
  if [ "$local_only" = "1" ]; then
    _save_remote_mode "local"
    log "Modo local-only: sin remoto. No se hara push (sprint-close mantiene local)."
  elif [ "$create" = "1" ]; then
    _create_remote_repo "$repo_name" "$visibility"
    _save_remote_mode "remote"
  elif [ -n "$remote" ]; then
    if git remote get-url origin >/dev/null 2>&1; then
      git remote set-url origin "$remote"
      log "Remote origin actualizado: $remote"
    else
      git remote add origin "$remote"
      log "Remote origin añadido: $remote"
    fi
    _save_remote_mode "remote"
  fi

  # Guardar modo
  save_mode "$mode"
  log "Modo guardado: $mode"

  # Asegurar patrones X-DD en .gitignore
  _ensure_gitignore

  # Volver a develop
  git checkout develop 2>/dev/null || true

  echo ""
  log "GitFlow configurado:"
  log "  Modo:    $mode"
  log "  Branches: main + develop"
  [ -n "$remote" ] && log "  Remote:  $remote"
  echo ""
  if [ "$mode" = "dev" ]; then
    log "Dev-solo: PRs auto-mergeadas via gh cli (requiere gh instalado)."
  else
    log "Collab: PRs requieren 1 reviewer. Configurar CODEOWNERS si es necesario."
  fi
}

# ── sprint-start ──────────────────────────────────────────────────────────────

cmd_sprint_start() {
  local sprint=""
  local title=""
  local type="feature"

  while [ $# -gt 0 ]; do
    case "$1" in
      --sprint=*) sprint="${1#*=}"; shift ;;
      --title=*) title="${1#*=}"; shift ;;
      --type=*) type="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done

  [ -n "$sprint" ] || err "--sprint requerido"
  [ -n "$title" ] || err "--title requerido"
  [ "$type" = "feature" ] || [ "$type" = "fix" ] || err "--type debe ser feature o fix"

  ensure_git

  local snum
  snum=$(sprint_num "$sprint")
  local branch_name="${type}/sprint-${snum}-${title}"

  # Verificar que develop existe y está actualizado
  git rev-parse --verify develop >/dev/null 2>&1 || err "Branch develop no existe. Ejecutar: xdd-gitflow.sh setup"

  # Verificar que no hay sprint anterior sin PR mergeada
  _check_previous_sprint_merged "$snum"

  # Cambiar a develop y crear branch
  git checkout develop
  git checkout -b "$branch_name"

  log "Branch creada: $branch_name"
  log "Sprint $snum listo para desarrollo."
  echo ""
  log "Flujo del sprint:"
  log "  1. Implementar historias de acuerdos/historia-usuario-*/"
  log "  2. Tests verdes: python3 -m pytest -q"
  log "  3. Cerrar sprint: xdd-gitflow.sh sprint-close --sprint=$sprint"
}

# ── sprint-close ──────────────────────────────────────────────────────────────

cmd_sprint_close() {
  local sprint=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --sprint=*) sprint="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done

  [ -n "$sprint" ] || err "--sprint requerido"

  ensure_git

  local snum
  snum=$(sprint_num "$sprint")
  local current
  current=$(current_branch)

  # Verificar que estamos en la branch del sprint
  echo "$current" | grep -q "sprint-${snum}" || warn "Branch actual '$current' no corresponde a sprint-${snum}. Continuar de todas formas."

  # Pre-push checks
  cmd_pre_push

  # Actualizar memoria del sprint
  if command -v python3 >/dev/null 2>&1; then
    python3 "${SCRIPT_DIR}/xdd-memory.py" --project="$(pwd)" sprint-close --sprint="$sprint" 2>/dev/null || true
  fi

  # Si es modo local-only: no hacer push ni PR (ADR-0052)
  if [ "$(_get_remote_mode)" = "local" ]; then
    log "Modo local-only: sprint cerrado sin push remoto ni PR."
    log "Sprint $snum cerrado (local)."
    return 0
  fi

  # Push a la branch actual
  git push -u origin "$current" 2>/dev/null || {
    warn "No se pudo hacer push a origin. Continuando sin push remoto."
  }

  local mode
  mode=$(get_mode)

  if command -v gh >/dev/null 2>&1 && git remote get-url origin >/dev/null 2>&1; then
    _create_pr "$current" "$snum" "$mode"
  else
    log "gh cli no disponible o sin remote. PR manual requerida."
    log "Branch lista para merge manual a develop."
  fi

  log "Sprint $snum cerrado."
}

_create_pr() {
  local branch="$1"
  local snum="$2"
  local mode="$3"

  local title="Sprint ${snum}: $(echo "$branch" | sed 's|.*/sprint-[0-9]*-||')"
  local body="## Sprint ${snum}

Cierre automatico via xdd-gitflow.sh.

### Checklist
- [ ] Tests verdes
- [ ] Shield 0 CRITICAL
- [ ] Lecciones registradas en acuerdos/lecciones/sprint-${snum}.md

🤖 Generated with X-DD xdd-gitflow.sh"

  if [ "$mode" = "dev" ]; then
    # Dev-solo: crear PR y auto-merge
    if gh pr create \
      --title "$title" \
      --body "$body" \
      --base develop \
      --head "$branch" 2>/dev/null; then
      log "PR creada (modo dev-solo)."
      # Intentar auto-merge
      if gh pr merge --squash --auto "$branch" 2>/dev/null; then
        log "PR marcada para auto-merge."
      else
        log "Auto-merge no disponible. Merge manual requerido."
      fi
    else
      log "PR ya existe o error al crear. Verificar en GitHub."
    fi
  else
    # Collab: crear PR sin auto-merge
    if gh pr create \
      --title "$title" \
      --body "$body" \
      --base develop \
      --head "$branch" 2>/dev/null; then
      log "PR creada (modo collab). Requiere reviewer antes de merge."
    else
      log "PR ya existe o error al crear. Verificar en GitHub."
    fi
  fi
}

# ── pre-push ──────────────────────────────────────────────────────────────────

cmd_pre_push() {
  if [ "${XDD_SKIP_PREPUSH:-0}" = "1" ]; then
    warn "XDD_SKIP_PREPUSH=1 — checks omitidos."
    return 0
  fi

  ensure_git

  log "Ejecutando checks pre-push..."

  # 1. Asegurar patrones X-DD en .gitignore
  _ensure_gitignore

  # 2. Verificar que artefactos X-DD NO están staged para push
  _check_xdd_artifacts_not_staged

  # 3. Gitleaks si disponible
  if [ "${XDD_SKIP_GITLEAKS:-0}" != "1" ]; then
    if command -v gitleaks >/dev/null 2>&1; then
      log "Ejecutando gitleaks..."
      if ! gitleaks detect --no-banner --exit-code 1 2>/dev/null; then
        err "gitleaks: secretos detectados. Resolver antes de push."
      fi
      log "gitleaks: limpio."
    else
      warn "gitleaks no instalado. Saltar con XDD_SKIP_GITLEAKS=1 o instalar: https://github.com/gitleaks/gitleaks"
    fi
  fi

  log "Pre-push: OK."
}

_ensure_gitignore() {
  local gitignore=".gitignore"
  local modified=0

  if [ ! -f "$gitignore" ]; then
    touch "$gitignore"
  fi

  for pattern in "${XDD_GITIGNORE_PATTERNS[@]}"; do
    if ! grep -qxF "$pattern" "$gitignore" 2>/dev/null; then
      echo "$pattern" >> "$gitignore"
      log "  .gitignore += $pattern"
      modified=1
    fi
  done

  if [ "$modified" = "1" ]; then
    log ".gitignore actualizado con patrones X-DD."
  fi
}

_check_xdd_artifacts_not_staged() {
  local staged
  staged=$(git diff --cached --name-only 2>/dev/null || true)

  local violations=()
  for pattern in "${XDD_GITIGNORE_PATTERNS[@]}"; do
    # Quitar trailing slash para grep
    local clean="${pattern%/}"
    while IFS= read -r file; do
      if echo "$file" | grep -q "^${clean}"; then
        violations+=("$file")
      fi
    done <<< "$staged"
  done

  if [ ${#violations[@]} -gt 0 ]; then
    warn "Artefactos X-DD detectados en staging (no deben ir al repo del producto):"
    for v in "${violations[@]}"; do
      warn "  - $v"
    done
    warn "Ejecutar: git reset HEAD <archivo> para destagear."
    warn "Override: XDD_SKIP_PREPUSH=1 (no recomendado)"
    err "Pre-push bloqueado por artefactos X-DD en staging."
  fi
}

_check_previous_sprint_merged() {
  local current_snum="$1"
  local prev_snum

  # Sprint 01 no tiene anterior
  [ "$current_snum" = "01" ] && return 0

  prev_snum=$(printf "%02d" $((10#$current_snum - 1)))

  # Buscar branches feature/sprint-XX o fix/sprint-XX del sprint anterior
  local prev_branches
  prev_branches=$(git branch --list "*sprint-${prev_snum}*" 2>/dev/null || true)

  if [ -z "$prev_branches" ]; then
    # No hay branch local del sprint anterior — asumimos que ya fue mergeada
    return 0
  fi

  # Verificar que la branch del sprint anterior está mergeada en develop
  for branch in $prev_branches; do
    branch="${branch// /}"
    branch="${branch#\* }"
    if ! git merge-base --is-ancestor "$branch" develop 2>/dev/null; then
      warn "Branch '$branch' (sprint-${prev_snum}) no esta mergeada en develop."
      warn "Completar sprint anterior antes de iniciar sprint-${current_snum}."
      err "Sprint anterior sin merge. Resolver con: xdd-gitflow.sh sprint-close --sprint=$((10#$current_snum - 1))"
    fi
  done
}

# ── status ────────────────────────────────────────────────────────────────────

cmd_status() {
  ensure_git

  local mode
  mode=$(get_mode)
  local current
  current=$(current_branch)

  echo "[xdd-gitflow] Estado GitFlow"
  echo "  Modo:          $mode"
  echo "  Branch actual: $current"
  echo "  Branches de sprint:"
  git branch --list "*sprint-*" | sed 's/^/    /'
  echo "  .gitignore X-DD:"
  for pattern in "${XDD_GITIGNORE_PATTERNS[@]}"; do
    if grep -qxF "$pattern" .gitignore 2>/dev/null; then
      echo "    ✓ $pattern"
    else
      echo "    ✗ $pattern (faltante)"
    fi
  done
}

# ── main ──────────────────────────────────────────────────────────────────────

show_usage() {
  cat <<EOF
xdd-gitflow.sh v${VERSION} — GitFlow automatizado para proyectos X-DD

Uso: xdd-gitflow.sh <subcomando> [opciones]

Subcomandos:
  setup         --mode=dev|collab [--create|--local|--remote=URL] [--name=N] [--visibility=private|public]
  sprint-start  --sprint=NN --title=<titulo> [--type=feature|fix]
  sprint-close  --sprint=NN
  pre-push
  status
  --version

Ejemplos:
  xdd-gitflow.sh setup --mode=dev
  xdd-gitflow.sh setup --mode=collab --remote=https://github.com/org/repo
  xdd-gitflow.sh sprint-start --sprint=1 --title=auth-usuarios
  xdd-gitflow.sh sprint-close --sprint=1
  xdd-gitflow.sh status

Variables de entorno:
  XDD_GITFLOW_MODE=dev|collab   Override modo
  XDD_SKIP_PREPUSH=1            Saltar checks pre-push
  XDD_SKIP_GITLEAKS=1           Saltar gitleaks
EOF
}

case "${1:-}" in
  setup)        shift; cmd_setup "$@" ;;
  sprint-start) shift; cmd_sprint_start "$@" ;;
  sprint-close) shift; cmd_sprint_close "$@" ;;
  pre-push)     shift; cmd_pre_push "$@" ;;
  status)       shift; cmd_status "$@" ;;
  --version|-v) echo "xdd-gitflow.sh v${VERSION}" ;;
  --help|-h|"") show_usage ;;
  *) err "Subcomando desconocido: $1. Ver: xdd-gitflow.sh --help" ;;
esac
