#!/bin/bash
# xdd-monorepo — Monorepo tool detector + mode suggester (Sprint 15, ADR-0013).
set -eu

XDD_VERSION="$(cat "$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )/VERSION" 2>/dev/null || echo "0.1.0-dev")"

usage() {
  cat <<'EOF'
xdd-monorepo — Detect monorepo tool + suggest mode.

Usage:
  bash scripts/xdd-monorepo.sh detect [PATH]      # detect tool only
  bash scripts/xdd-monorepo.sh suggest [PATH]     # detect + suggest mode + sample yaml
  bash scripts/xdd-monorepo.sh --help | --version

Modes (ADR-0013): isolated | shared | hybrid
Tools detected: nx, turborepo, pnpm-workspaces, yarn-workspaces, lerna, rush, bazel, cargo-workspaces, go-workspaces

Exit codes:
  0 = monorepo detected
  1 = not a monorepo (single-package project)
  2 = error
EOF
}

if [ $# -eq 0 ]; then usage; exit 2; fi
case "$1" in
  -h|--help) usage; exit 0 ;;
  -v|--version) echo "xdd-monorepo v${XDD_VERSION}"; exit 0 ;;
esac

CMD="$1"; shift || true
TARGET="${1:-$PWD}"

if [ ! -d "$TARGET" ]; then
  echo "[xdd-monorepo] ERROR: not a directory: $TARGET" >&2
  exit 2
fi

detect_tool() {
  local p="$1"
  if [ -f "$p/nx.json" ]; then echo "nx"; return 0; fi
  if [ -f "$p/turbo.json" ]; then echo "turborepo"; return 0; fi
  if [ -f "$p/pnpm-workspace.yaml" ] || [ -f "$p/pnpm-workspace.yml" ]; then echo "pnpm-workspaces"; return 0; fi
  if [ -f "$p/lerna.json" ]; then echo "lerna"; return 0; fi
  if [ -f "$p/rush.json" ]; then echo "rush"; return 0; fi
  if [ -f "$p/WORKSPACE" ] || [ -f "$p/WORKSPACE.bazel" ] || [ -f "$p/MODULE.bazel" ]; then echo "bazel"; return 0; fi
  if [ -f "$p/Cargo.toml" ] && grep -q "^\[workspace\]" "$p/Cargo.toml" 2>/dev/null; then echo "cargo-workspaces"; return 0; fi
  if [ -f "$p/go.work" ]; then echo "go-workspaces"; return 0; fi
  if [ -f "$p/package.json" ] && python3 -c "import json,sys; d=json.load(open('$p/package.json')); sys.exit(0 if 'workspaces' in d else 1)" 2>/dev/null; then
    echo "yarn-workspaces"; return 0
  fi
  echo ""
  return 1
}

suggest_mode() {
  local tool="$1"
  case "$tool" in
    nx|turborepo|bazel) echo "hybrid" ;;
    pnpm-workspaces|yarn-workspaces) echo "shared" ;;
    lerna|rush) echo "isolated" ;;
    cargo-workspaces|go-workspaces) echo "shared" ;;
    *) echo "isolated" ;;
  esac
}

case "$CMD" in
  detect)
    tool=$(detect_tool "$TARGET") || tool=""
    if [ -z "$tool" ]; then
      echo "[xdd-monorepo] not a monorepo: $TARGET" >&2
      exit 1
    fi
    echo "$tool"
    exit 0
    ;;
  suggest)
    tool=$(detect_tool "$TARGET") || tool=""
    if [ -z "$tool" ]; then
      echo "[xdd-monorepo] not a monorepo: $TARGET" >&2
      exit 1
    fi
    mode=$(suggest_mode "$tool")
    echo "tool: $tool"
    echo "suggested_mode: $mode"
    echo ""
    echo "# Suggested xdd.profile.yml section:"
    cat <<EOF
monorepo:
  mode: $mode
  tool: $tool
  packages_dir: packages
  packages:
    - {name: "example", path: "packages/example", profile: "core"}
EOF
    exit 0
    ;;
  *)
    echo "[xdd-monorepo] unknown command: $CMD" >&2
    usage
    exit 2
    ;;
esac
