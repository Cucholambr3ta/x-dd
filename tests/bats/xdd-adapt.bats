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
  run bash scripts/xdd-adapt.sh claude-code --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/helios.md" ]
  grep -q "# /helios" "$DEST/.claude/commands/helios.md"
}

@test "vscode-copilot genera .github/prompts + .vscode/mcp.json key servers" {
  run bash scripts/xdd-adapt.sh vscode-copilot --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.github/prompts/helios.prompt.md" ]
  [ -f "$DEST/.vscode/mcp.json" ]
  grep -q '"servers"' "$DEST/.vscode/mcp.json"
}

@test "vscode-copilot genera tasks.json + settings.json env vars" {
  run bash scripts/xdd-adapt.sh vscode-copilot --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  # tasks.json con 4 tasks X-DD
  [ -f "$DEST/.vscode/tasks.json" ]
  grep -q "X-DD: doctor" "$DEST/.vscode/tasks.json"
  grep -q "X-DD: start orchestrator" "$DEST/.vscode/tasks.json"
  grep -q "X-DD: list workflows" "$DEST/.vscode/tasks.json"
  grep -q "X-DD: gate validate" "$DEST/.vscode/tasks.json"
  # settings.json env vars terminal
  [ -f "$DEST/.vscode/settings.json" ]
  grep -q "terminal.integrated.env.linux" "$DEST/.vscode/settings.json"
  grep -q "ANTHROPIC_API_KEY" "$DEST/.vscode/settings.json"
}

@test "vscode-copilot SKIP tasks.json + settings.json si ya existen (no overwrite)" {
  mkdir -p "$DEST/.vscode"
  echo '{"custom":"existing"}' > "$DEST/.vscode/tasks.json"
  echo '{"editor.fontSize":14}' > "$DEST/.vscode/settings.json"
  run bash scripts/xdd-adapt.sh vscode-copilot --dest="$DEST"
  [ "$status" -eq 0 ]
  # Preservados
  grep -q "custom" "$DEST/.vscode/tasks.json"
  grep -q "fontSize" "$DEST/.vscode/settings.json"
}

@test "cursor genera rules .mdc + mcp.json" {
  run bash scripts/xdd-adapt.sh cursor --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.cursor/rules/helios.mdc" ]
  [ -f "$DEST/.cursor/mcp.json" ]
}

@test "windsurf genera rules + mcp.json" {
  run bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.windsurf/rules/helios.md" ]
  [ -f "$DEST/.windsurf/mcp.json" ]
}

@test "antigravity mergea ~/.gemini config + .agents/skills + README (Sprint 25)" {
  GEMHOME="$(mktemp -d)/gemini"
  mkdir -p "$GEMHOME"
  echo '{"mcpServers":{"existing":{"command":"npx","args":["foo"]}}}' > "$GEMHOME/mcp_config.json"
  run env XDD_ANTIGRAVITY_HOME="$GEMHOME" bash scripts/xdd-adapt.sh antigravity --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.antigravity/README-xdd.md" ]
  # MCP merge: preserva existing + añade helios con CascadePluginCommandTemplate
  grep -q "existing" "$GEMHOME/mcp_config.json"
  grep -q "helios" "$GEMHOME/mcp_config.json"
  grep -q "CascadePluginCommandTemplate" "$GEMHOME/mcp_config.json"
  # Sprint 25: .agents/skills/ (plural, convención Antigravity) poblado
  [ -d "$DEST/.agents/skills" ]
  rm -rf "$(dirname "$GEMHOME")"
}

@test "opencode genera command/ + AGENTS.md" {
  run bash scripts/xdd-adapt.sh opencode --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -d "$DEST/.opencode/command" ]
  [ -f "$DEST/AGENTS.md" ]
}

@test "all genera los 6 IDEs" {
  GEMHOME="$(mktemp -d)/gemini"; mkdir -p "$GEMHOME"
  run env XDD_ANTIGRAVITY_HOME="$GEMHOME" bash scripts/xdd-adapt.sh all --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.claude/commands/helios.md" ]
  [ -f "$DEST/.opencode/command/helios.md" ]
  [ -f "$DEST/.cursor/rules/helios.mdc" ]
  [ -f "$DEST/.windsurf/rules/helios.md" ]
  [ -f "$DEST/.github/prompts/helios.prompt.md" ]
  [ -f "$DEST/.antigravity/README-xdd.md" ]
  [ -d "$DEST/.agents/skills" ]
  grep -q "helios" "$GEMHOME/mcp_config.json"
  rm -rf "$(dirname "$GEMHOME")"
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
