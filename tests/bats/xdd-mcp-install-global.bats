#!/usr/bin/env bats
# Tests para scripts/xdd-mcp-install-global.sh (Sprint 25 + ADR-0035).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  BINDIR="$(mktemp -d)/bin"
  mkdir -p "$BINDIR"
}

teardown() {
  [ -n "${BINDIR:-}" ] && [ -d "$(dirname "$BINDIR")" ] && rm -rf "$(dirname "$BINDIR")"
}

@test "xdd-mcp-install-global --version" {
  run bash scripts/xdd-mcp-install-global.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-mcp-install-global v"* ]]
}

@test "xdd-mcp-install-global --help" {
  run bash scripts/xdd-mcp-install-global.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"PATH"* ]]
  [[ "$output" == *"wrapper"* ]]
}

@test "install genera wrapper ejecutable con PYTHONPATH baked" {
  run bash scripts/xdd-mcp-install-global.sh --bin-dir="$BINDIR"
  [ "$status" -eq 0 ]
  [ -x "$BINDIR/xdd-mcp-server" ]
  grep -q "PYTHONPATH=" "$BINDIR/xdd-mcp-server"
  grep -q "$ROOT" "$BINDIR/xdd-mcp-server"
  grep -q "python3 -m xdd-mcp-server" "$BINDIR/xdd-mcp-server"
}

@test "wrapper instalado responde --version" {
  bash scripts/xdd-mcp-install-global.sh --bin-dir="$BINDIR" >/dev/null 2>&1
  run "$BINDIR/xdd-mcp-server" --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-mcp-server"* ]]
}

@test "--check sin install reporta NOT installed" {
  run bash scripts/xdd-mcp-install-global.sh --check --bin-dir="$BINDIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"NOT installed"* ]]
}

@test "--check tras install reporta version" {
  bash scripts/xdd-mcp-install-global.sh --bin-dir="$BINDIR" >/dev/null 2>&1
  run bash scripts/xdd-mcp-install-global.sh --check --bin-dir="$BINDIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"installed"* ]]
  [[ "$output" == *"version:"* ]]
}

@test "--uninstall remueve wrapper" {
  bash scripts/xdd-mcp-install-global.sh --bin-dir="$BINDIR" >/dev/null 2>&1
  [ -x "$BINDIR/xdd-mcp-server" ]
  run bash scripts/xdd-mcp-install-global.sh --uninstall --bin-dir="$BINDIR"
  [ "$status" -eq 0 ]
  [ ! -e "$BINDIR/xdd-mcp-server" ]
}

@test "install con --xdd-root inválido falla" {
  run bash scripts/xdd-mcp-install-global.sh --bin-dir="$BINDIR" --xdd-root=/tmp
  [ "$status" -ne 0 ]
}
