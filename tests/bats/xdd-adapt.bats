#!/usr/bin/env bats
# Tests para scripts/xdd-adapt.sh (Sprint 7.5).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  DEST="$(mktemp -d)/xdd-adapt-test"
  mkdir -p "$DEST"
}

teardown() {
  [ -n "${DEST:-}" ] && [ -d "$(dirname "$DEST")" ] && rm -rf "$(dirname "$DEST")"
}

@test "xdd-adapt --version" {
  run bash scripts/xdd-adapt.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-adapt v"* ]]
}

@test "xdd-adapt --list incluye claude-code y opencode" {
  run bash scripts/xdd-adapt.sh --list
  [ "$status" -eq 0 ]
  [[ "$output" == *"claude-code"* ]]
  [[ "$output" == *"opencode"* ]]
}

@test "xdd-adapt sin target falla" {
  run bash scripts/xdd-adapt.sh
  [ "$status" -eq 2 ]
}

@test "xdd-adapt target desconocido falla" {
  run bash scripts/xdd-adapt.sh notavalidtarget
  [ "$status" -eq 2 ]
}

@test "xdd-adapt claude-code --dry-run no escribe nada" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST" --dry-run
  [ "$status" -eq 0 ]
  [ ! -d "$DEST/.claude" ]
  [[ "$output" == *"[dry-run]"* ]]
}

@test "xdd-adapt claude-code crea .claude/commands/ con symlinks" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -d "$DEST/.claude/commands" ]
  count=$(ls "$DEST/.claude/commands" | wc -l)
  [ "$count" -gt 30 ]
}

@test "xdd-adapt opencode crea AGENTS.md desde registry" {
  run bash scripts/xdd-adapt.sh opencode --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/AGENTS.md" ]
  grep -q "Generado automáticamente" "$DEST/AGENTS.md"
}

@test "xdd-adapt all ejecuta los dos" {
  run bash scripts/xdd-adapt.sh all --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -d "$DEST/.claude/commands" ]
  [ -f "$DEST/AGENTS.md" ]
}
