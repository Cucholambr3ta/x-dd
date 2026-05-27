#!/bin/bash
# xdd-wizard — Interactive bootstrap wizard (Sprint 14, ADR-0012).
# Guides user through profile selection, branding, workspace mode, then invokes xdd-init.
set -eu

XDD_VERSION="0.1.0-dev"
XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"

usage() {
  cat <<'EOF'
xdd-wizard — Interactive bootstrap wizard for X-DD.

Usage:
  bash scripts/xdd-wizard.sh [--dest=PATH] [--non-interactive]
  bash scripts/xdd-wizard.sh --help | --version

Flow:
  1) Destination path
  2) Profile selection (minimal/core/developer/security/research/full)
  3) Workspace mode (single project vs N projects in workspace)
  4) Branding (default X-DD vs custom)
  5) Optional persona (technical/friendly/casual/formal)
  6) Optional compact level (off/lite/standard/ultra)
  7) Confirm → invoke xdd-init.sh + xdd-brand.sh if branded
EOF
}

DEST=""
NON_INTERACTIVE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -v|--version) echo "xdd-wizard v${XDD_VERSION}"; exit 0 ;;
    --dest=*) DEST="${1#--dest=}"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    --non-interactive) NON_INTERACTIVE=1; shift ;;
    *) echo "[xdd-wizard] ERROR: unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

# Helper: prompt with default
ask() {
  local prompt="$1"
  local default="${2:-}"
  local answer
  if [ "$NON_INTERACTIVE" -eq 1 ]; then
    echo "$default"
    return 0
  fi
  if [ -n "$default" ]; then
    read -r -p "$prompt [$default]: " answer
    echo "${answer:-$default}"
  else
    read -r -p "$prompt: " answer
    echo "$answer"
  fi
}

# Helper: pick from list
pick() {
  local prompt="$1"
  shift
  local options=("$@")
  if [ "$NON_INTERACTIVE" -eq 1 ]; then
    echo "${options[0]}"
    return 0
  fi
  echo "$prompt" >&2
  local i=1
  for opt in "${options[@]}"; do
    echo "  $i) $opt" >&2
    i=$((i+1))
  done
  local choice
  read -r -p "Choice [1]: " choice
  choice="${choice:-1}"
  local idx=$((choice-1))
  if [ "$idx" -lt 0 ] || [ "$idx" -ge "${#options[@]}" ]; then
    echo "[xdd-wizard] Invalid choice, defaulting to ${options[0]}" >&2
    echo "${options[0]}"
  else
    echo "${options[$idx]}"
  fi
}

echo "🧙 X-DD Wizard v${XDD_VERSION}"
echo "========================="
echo ""

# 1) Destination
if [ -z "$DEST" ]; then
  DEST=$(ask "📁 Destination path" "$PWD/x-dd-project")
fi
echo "→ DEST=$DEST"
echo ""

# 2) Profile
PROFILE=$(pick "📦 Select install profile:" "core" "minimal" "developer" "security" "research" "full")
echo "→ PROFILE=$PROFILE"
echo ""

# 3) Workspace mode
WORKSPACE_MODE=$(pick "🗂️  Workspace mode:" "single (one project)" "workspace (multiple projects)")
echo "→ WORKSPACE_MODE=$WORKSPACE_MODE"
echo ""

WORKSPACE_PROJECTS=""
if [ "$WORKSPACE_MODE" = "workspace (multiple projects)" ]; then
  if [ "$NON_INTERACTIVE" -eq 0 ]; then
    echo "Enter project names (comma-separated, e.g.: api,web,worker):"
    read -r WORKSPACE_PROJECTS
  fi
  WORKSPACE_PROJECTS="${WORKSPACE_PROJECTS:-api,web}"
  echo "→ WORKSPACE_PROJECTS=$WORKSPACE_PROJECTS"
  echo ""
fi

# 4) Branding
BRAND_MODE=$(pick "🎨 Branding:" "default (X-DD)" "custom")
echo "→ BRAND_MODE=$BRAND_MODE"
echo ""

ECOSYSTEM_NAME="X-DD"
ECOSYSTEM_SLUG="xdd"
TRIGGER="xdd"
PERSONA="technical"
COMPACT="off"

if [ "$BRAND_MODE" = "custom" ]; then
  ECOSYSTEM_NAME=$(ask "  Ecosystem name" "Helios")
  ECOSYSTEM_SLUG=$(ask "  Ecosystem slug (lowercase, no spaces)" "helios")
  TRIGGER=$(ask "  Orchestrator trigger (replaces /xdd)" "helios")
  PERSONA=$(pick "  Persona tone:" "technical" "friendly" "casual" "formal")
  COMPACT=$(pick "  Compact level:" "off" "lite" "standard" "ultra")
fi

# 5) Confirm
echo ""
echo "========================="
echo "🧙 Confirm configuration:"
echo "  DEST=$DEST"
echo "  PROFILE=$PROFILE"
echo "  WORKSPACE_MODE=$WORKSPACE_MODE"
[ -n "$WORKSPACE_PROJECTS" ] && echo "  WORKSPACE_PROJECTS=$WORKSPACE_PROJECTS"
echo "  ECOSYSTEM_NAME=$ECOSYSTEM_NAME"
echo "  ECOSYSTEM_SLUG=$ECOSYSTEM_SLUG"
echo "  TRIGGER=$TRIGGER"
echo "  PERSONA=$PERSONA"
echo "  COMPACT=$COMPACT"
echo "========================="
echo ""

CONFIRM=$(ask "Proceed? (y/n)" "y")
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  echo "Aborted."
  exit 0
fi

# 6) Invoke xdd-init
echo ""
echo "🚀 Invoking xdd-init..."
bash "$XDD_ROOT/scripts/xdd-init.sh" "$DEST" --profile="$PROFILE"

# 7) Workspace mode → write workspace section into xdd.profile.yml
if [ "$WORKSPACE_MODE" = "workspace (multiple projects)" ]; then
  PROFILE_FILE="$DEST/xdd.profile.yml"
  if [ -f "$PROFILE_FILE" ]; then
    {
      echo ""
      echo "workspace:"
      echo "  enabled: true"
      echo "  root: \"$DEST\""
      echo "  shared_memory: true"
      echo "  shared_gate_key: false"
      echo "  projects:"
      IFS=',' read -ra PROJS <<< "$WORKSPACE_PROJECTS"
      for p in "${PROJS[@]}"; do
        p_trim=$(echo "$p" | xargs)
        echo "    - name: \"$p_trim\""
        echo "      path: \"./$p_trim\""
        echo "      profile: \"$PROFILE\""
      done
    } >> "$PROFILE_FILE"
    echo "✅ workspace section appended to $PROFILE_FILE"

    IFS=',' read -ra PROJS <<< "$WORKSPACE_PROJECTS"
    for p in "${PROJS[@]}"; do
      p_trim=$(echo "$p" | xargs)
      mkdir -p "$DEST/$p_trim"
      echo "# $p_trim" > "$DEST/$p_trim/README.md"
    done
  fi
fi

# 8) Branding if custom
if [ "$BRAND_MODE" = "custom" ]; then
  PROFILE_FILE="$DEST/xdd.profile.yml"
  {
    echo ""
    echo "branding:"
    echo "  ecosystem_name: \"$ECOSYSTEM_NAME\""
    echo "  ecosystem_slug: \"$ECOSYSTEM_SLUG\""
    echo "  orchestrator_trigger: \"$TRIGGER\""
    echo "  orchestrator_persona:"
    echo "    tone: \"$PERSONA\""
    echo "  output:"
    echo "    compact: \"$COMPACT\""
    echo "  attribution_required: true"
  } >> "$PROFILE_FILE"
  echo "✅ branding section appended"

  if [ -x "$XDD_ROOT/scripts/xdd-brand.sh" ]; then
    bash "$XDD_ROOT/scripts/xdd-brand.sh" "$DEST" || echo "[xdd-wizard] WARN: xdd-brand.sh failed; run manually later"
  fi
fi

echo ""
echo "🎉 Wizard complete. Next:"
echo "  cd $DEST"
echo "  bash scripts/xdd-start.sh"
echo "  # then in your IDE: /$TRIGGER"
exit 0
