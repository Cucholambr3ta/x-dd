#!/usr/bin/env bats
# Tests Sprint 29 / ADR-0039 — xdd-global-install.sh.
# Registra orquestador /<trigger> global en 6 IDEs. Self-bootstrap si dir vacío.

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  # Mock HOME para no contaminar real
  export ORIG_HOME="$HOME"
  export HOME="$(mktemp -d)/xdd-global-home"
  export XDG_CONFIG_HOME="$HOME/.config"
  export XDD_CODEX_HOME="$HOME/.codex/skills"
  mkdir -p "$HOME"
}

teardown() {
  [ -n "${HOME:-}" ] && [ "$HOME" != "$ORIG_HOME" ] && rm -rf "$HOME" 2>/dev/null
  export HOME="$ORIG_HOME"
}

@test "xdd-global-install --version" {
  run bash scripts/xdd-global-install.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-global-install v"* ]]
}

@test "xdd-global-install --help lista 6 IDEs" {
  run bash scripts/xdd-global-install.sh --help
  [ "$status" -eq 0 ]
  for ide in claude-code opencode cursor windsurf vscode-copilot codex; do
    [[ "$output" == *"$ide"* ]]
  done
}

@test "xdd-global-install --check detecta IDEs no instalados (HOME mock vacío)" {
  run bash scripts/xdd-global-install.sh --ides=all --check
  [ "$status" -eq 0 ]
  [[ "$output" == *"NOT INSTALLED"* ]]
}

@test "xdd-global-install --dry-run --ides=all no escribe nada en HOME" {
  run bash scripts/xdd-global-install.sh --ides=all --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"[dry-run]"* ]]
  [ ! -f "$HOME/.claude/commands/xdd.md" ]
  [ ! -f "$HOME/.cursor/rules/xdd.mdc" ]
}

@test "xdd-global-install instala claude-code en \$HOME/.claude/commands/" {
  run bash scripts/xdd-global-install.sh --ides=claude-code --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$HOME/.claude/commands/helios.md" ]
  grep -q "# /helios" "$HOME/.claude/commands/helios.md"
  grep -q "SELF-BOOTSTRAP CHECK" "$HOME/.claude/commands/helios.md"
}

@test "xdd-global-install instala cursor rule .mdc con frontmatter" {
  run bash scripts/xdd-global-install.sh --ides=cursor --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$HOME/.cursor/rules/helios.mdc" ]
  grep -q "^description:" "$HOME/.cursor/rules/helios.mdc"
  grep -q "Self-bootstrap" "$HOME/.cursor/rules/helios.mdc"
}

@test "xdd-global-install instala windsurf en \$HOME/.codeium/workflows/" {
  run bash scripts/xdd-global-install.sh --ides=windsurf --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$HOME/.codeium/workflows/helios.md" ]
}

@test "xdd-global-install instala vscode-copilot en XDG_CONFIG_HOME/Code/User/prompts/" {
  run bash scripts/xdd-global-install.sh --ides=vscode-copilot --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$XDG_CONFIG_HOME/Code/User/prompts/helios.prompt.md" ]
}

@test "xdd-global-install instala opencode en XDG_CONFIG_HOME/opencode/command/" {
  run bash scripts/xdd-global-install.sh --ides=opencode --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$XDG_CONFIG_HOME/opencode/command/helios.md" ]
}

@test "xdd-global-install --uninstall remueve archivos previos" {
  bash scripts/xdd-global-install.sh --ides=claude-code,cursor --trigger=helios >/dev/null 2>&1
  [ -f "$HOME/.claude/commands/helios.md" ]
  [ -f "$HOME/.cursor/rules/helios.mdc" ]
  run bash scripts/xdd-global-install.sh --ides=claude-code,cursor --trigger=helios --uninstall
  [ "$status" -eq 0 ]
  [ ! -f "$HOME/.claude/commands/helios.md" ]
  [ ! -f "$HOME/.cursor/rules/helios.mdc" ]
}

@test "xdd-global-install --check con IDE instalado reporta ✓" {
  bash scripts/xdd-global-install.sh --ides=claude-code --trigger=helios >/dev/null 2>&1
  run bash scripts/xdd-global-install.sh --ides=claude-code --trigger=helios --check
  [ "$status" -eq 0 ]
  [[ "$output" == *"✓ claude-code"* ]]
}

@test "xdd-global-install respeta XDG_CONFIG_HOME override (portabilidad CI)" {
  local custom_xdg="$(mktemp -d)/custom-xdg"
  export XDG_CONFIG_HOME="$custom_xdg"
  run bash scripts/xdd-global-install.sh --ides=opencode --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$custom_xdg/opencode/command/helios.md" ]
  rm -rf "$custom_xdg"
}

@test "xdd-global-install --ides=all instala 5 IDEs nuevos + delega codex (Sprint 24)" {
  run bash scripts/xdd-global-install.sh --ides=all --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$HOME/.claude/commands/helios.md" ]
  [ -f "$XDG_CONFIG_HOME/opencode/command/helios.md" ]
  [ -f "$HOME/.cursor/rules/helios.mdc" ]
  [ -f "$HOME/.codeium/workflows/helios.md" ]
  [ -f "$XDG_CONFIG_HOME/Code/User/prompts/helios.prompt.md" ]
  # Codex delegado vía xdd-adapt — verifica que se invocó
  [[ "$output" == *"codex"* ]]
}

@test "orchestrator generado contiene PRE-FLIGHT Sprint 28 + SELF-BOOTSTRAP Sprint 29" {
  bash scripts/xdd-global-install.sh --ides=claude-code --trigger=helios >/dev/null 2>&1
  local md="$HOME/.claude/commands/helios.md"
  [ -f "$md" ]
  # Sprint 29 self-bootstrap
  grep -q "SELF-BOOTSTRAP CHECK" "$md"
  grep -q "xdd-init.sh" "$md"
  # Sprint 28 PRE-FLIGHT enforcement (heredado)
  grep -q "PRE-FLIGHT BOOTSTRAP" "$md"
  grep -q "Sprint 28 / ADR-0038" "$md"
  # Sección delegación + cierre
  grep -q "DELEGACI" "$md"
  grep -q "cierre-fase" "$md"
}
