#!/usr/bin/env bats
# Tests para scripts/xdd-adapt.sh (Sprint 24 — universal IDE adapter, 6 IDEs + copia real + MCP).

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

@test "xdd-adapt --list incluye 6 targets" {
  run bash scripts/xdd-adapt.sh --list
  [ "$status" -eq 0 ]
  [[ "$output" == *"claude-code"* ]]
  [[ "$output" == *"opencode"* ]]
  [[ "$output" == *"cursor"* ]]
  [[ "$output" == *"windsurf"* ]]
  [[ "$output" == *"vscode-copilot"* ]]
  [[ "$output" == *"antigravity"* ]]
}

@test "xdd-adapt sin target falla" {
  run bash scripts/xdd-adapt.sh
  [ "$status" -eq 2 ]
}

@test "xdd-adapt target desconocido falla" {
  run bash scripts/xdd-adapt.sh notavalidtarget
  [ "$status" -eq 2 ]
}

@test "claude-code --dry-run no escribe nada" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST" --dry-run
  [ "$status" -eq 0 ]
  [ ! -d "$DEST/.claude" ]
  [[ "$output" == *"[dry-run]"* ]]
}

@test "claude-code genera copia REAL (no symlink)" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST" --trigger=xdd
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/xdd.md" ]
  [ ! -L "$DEST/.claude/commands/xdd.md" ]
}

@test "claude-code genera .mcp.json con mcpServers + xdd-mcp-server" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/.mcp.json" ]
  grep -q "mcpServers" "$DEST/.mcp.json"
  grep -q "xdd-mcp-server" "$DEST/.mcp.json"
}

@test "trigger custom renombra + rebrandea command principal" {
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/anmax.md" ]
  grep -q "# /anmax" "$DEST/.claude/commands/anmax.md"
}

@test "vscode-copilot genera .github/prompts + .vscode/mcp.json key servers" {
  run bash scripts/xdd-adapt.sh vscode-copilot --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.github/prompts/anmax.prompt.md" ]
  [ -f "$DEST/.vscode/mcp.json" ]
  grep -q '"servers"' "$DEST/.vscode/mcp.json"
}

@test "cursor genera rules .mdc + mcp.json" {
  run bash scripts/xdd-adapt.sh cursor --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.cursor/rules/anmax.mdc" ]
  [ -f "$DEST/.cursor/mcp.json" ]
}

@test "windsurf genera rules + mcp.json" {
  run bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.windsurf/rules/anmax.md" ]
  [ -f "$DEST/.windsurf/mcp.json" ]
}

@test "antigravity genera mcp.json + README (no slash)" {
  run bash scripts/xdd-adapt.sh antigravity --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.antigravity/mcp.json" ]
  [ -f "$DEST/.antigravity/README-xdd.md" ]
}

@test "opencode genera command/ + AGENTS.md" {
  run bash scripts/xdd-adapt.sh opencode --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -d "$DEST/.opencode/command" ]
  [ -f "$DEST/AGENTS.md" ]
}

@test "all genera los 6 IDEs" {
  run bash scripts/xdd-adapt.sh all --dest="$DEST" --trigger=anmax
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/anmax.md" ]
  [ -f "$DEST/.opencode/command/anmax.md" ]
  [ -f "$DEST/.cursor/rules/anmax.mdc" ]
  [ -f "$DEST/.windsurf/rules/anmax.md" ]
  [ -f "$DEST/.github/prompts/anmax.prompt.md" ]
  [ -f "$DEST/.antigravity/mcp.json" ]
}

@test "trigger resuelve desde branding xdd.profile.yml" {
  cat > "$DEST/xdd.profile.yml" <<'EOF'
profile: custom
branding:
  orchestrator_trigger: "helios"
EOF
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/helios.md" ]
}
