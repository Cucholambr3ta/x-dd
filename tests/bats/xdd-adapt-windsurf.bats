#!/usr/bin/env bats
# Tests Sprint 26 / ADR-0037 — adapter Windsurf paridad completa.
# Cubre: workflows nativos, MCP merge global, idempotencia, edge cases.
# Portabilidad: HOME mocked via mktemp; CI ubuntu-latest + macos-latest.

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  DEST="$(mktemp -d)/xdd-windsurf-dest"
  WINDSURF_HOME="$(mktemp -d)/codeium-mock"
  mkdir -p "$DEST" "$WINDSURF_HOME"
}

teardown() {
  [ -n "${DEST:-}" ] && [ -d "$(dirname "$DEST")" ] && rm -rf "$(dirname "$DEST")"
  [ -n "${WINDSURF_HOME:-}" ] && [ -d "$(dirname "$WINDSURF_HOME")" ] && rm -rf "$(dirname "$WINDSURF_HOME")"
}

@test "windsurf copia workflows SSoT a .windsurf/workflows/ (slash nativos)" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -d "$DEST/.windsurf/workflows" ]
  [ -f "$DEST/.windsurf/workflows/helios.md" ]
  # Copia REAL (no symlink)
  [ ! -L "$DEST/.windsurf/workflows/helios.md" ]
  # Frontmatter description preservado
  grep -q "^description:" "$DEST/.windsurf/workflows/helios.md"
  # Custom trigger renaming aplicado (xdd → helios)
  grep -q "# /helios" "$DEST/.windsurf/workflows/helios.md"
}

@test "windsurf mergea MCP entry en \$XDD_WINDSURF_HOME/mcp_config.json (NO project-local)" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$WINDSURF_HOME/mcp_config.json" ]
  grep -q "mcpServers" "$WINDSURF_HOME/mcp_config.json"
  grep -q "helios" "$WINDSURF_HOME/mcp_config.json"
  # NO Cascade $typeName (eso es Antigravity-only)
  ! grep -q "CascadePluginCommandTemplate" "$WINDSURF_HOME/mcp_config.json"
}

@test "windsurf MERGE no destructivo — preserva otros mcpServers existentes" {
  echo '{"mcpServers":{"existing-server":{"command":"npx","args":["foo"]}}}' > "$WINDSURF_HOME/mcp_config.json"
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  # Existente preservado
  grep -q "existing-server" "$WINDSURF_HOME/mcp_config.json"
  grep -q "helios" "$WINDSURF_HOME/mcp_config.json"
}

@test "windsurf MCP merge crea archivo si no existe" {
  # WINDSURF_HOME tiene dir pero NO mcp_config.json
  [ ! -f "$WINDSURF_HOME/mcp_config.json" ]
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$WINDSURF_HOME/mcp_config.json" ]
  grep -q "helios" "$WINDSURF_HOME/mcp_config.json"
}

@test "windsurf MCP merge ABORT si JSON corrupto (no destruir)" {
  echo 'NOT VALID JSON {{{' > "$WINDSURF_HOME/mcp_config.json"
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -ne 0 ]
  # Archivo corrupto NO destruido
  grep -q "NOT VALID JSON" "$WINDSURF_HOME/mcp_config.json"
}

@test "windsurf idempotente — corre adapter 2 veces, resultado consistente" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  local first_hash
  first_hash=$(python3 -c "import json; d=json.load(open('$WINDSURF_HOME/mcp_config.json')); print(sorted(d['mcpServers'].keys()))")
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  local second_hash
  second_hash=$(python3 -c "import json; d=json.load(open('$WINDSURF_HOME/mcp_config.json')); print(sorted(d['mcpServers'].keys()))")
  [ "$first_hash" = "$second_hash" ]
}

@test "windsurf genera rule + stub mcp.json + README local" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$DEST/.windsurf/rules/helios.md" ]
  [ -f "$DEST/.windsurf/mcp.json" ]
  # Stub project-local con comment explicativo
  grep -q "_comment" "$DEST/.windsurf/mcp.json"
  grep -q "~/.codeium/mcp_config.json" "$DEST/.windsurf/mcp.json"
  # README local
  [ -f "$DEST/.windsurf/README-xdd.md" ]
  grep -q "Workflows nativos" "$DEST/.windsurf/README-xdd.md"
  grep -q "12000 chars" "$DEST/.windsurf/README-xdd.md"
}

@test "windsurf --dry-run no escribe nada (ni global ni project)" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --dry-run
  [ "$status" -eq 0 ]
  [ ! -d "$DEST/.windsurf/workflows" ]
  [ ! -f "$WINDSURF_HOME/mcp_config.json" ]
  [[ "$output" == *"[dry-run]"* ]]
}

@test "windsurf trigger default xdd genera xdd.md (no rebrand cuando trigger=xdd)" {
  run env XDD_WINDSURF_HOME="$WINDSURF_HOME" bash scripts/xdd-adapt.sh windsurf --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/.windsurf/workflows/xdd.md" ]
  [ -f "$DEST/.windsurf/rules/xdd.md" ]
}

@test "windsurf XDD_WINDSURF_HOME override funciona (portabilidad)" {
  local custom_home="$(mktemp -d)/custom-codeium"
  mkdir -p "$custom_home"
  run env XDD_WINDSURF_HOME="$custom_home" bash scripts/xdd-adapt.sh windsurf --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  [ -f "$custom_home/mcp_config.json" ]
  grep -q "helios" "$custom_home/mcp_config.json"
  # Default $HOME/.codeium NO tocado si override activo
  ! grep -q "helios" "$HOME/.codeium/mcp_config.json" 2>/dev/null || true
  rm -rf "$(dirname "$custom_home")"
}

@test "windsurf integrado en target 'all' — 7 IDEs (incluye fixes Sprint 26)" {
  GEMHOME="$(mktemp -d)/gemini"; mkdir -p "$GEMHOME"
  CODEX_HOME="$(mktemp -d)/codex"; mkdir -p "$CODEX_HOME"
  run env XDD_ANTIGRAVITY_HOME="$GEMHOME" XDD_CODEX_HOME="$CODEX_HOME" XDD_WINDSURF_HOME="$WINDSURF_HOME" \
      bash scripts/xdd-adapt.sh all --dest="$DEST" --trigger=helios
  [ "$status" -eq 0 ]
  # Windsurf outputs nuevos Sprint 26
  [ -d "$DEST/.windsurf/workflows" ]
  [ -f "$DEST/.windsurf/workflows/helios.md" ]
  [ -f "$DEST/.windsurf/README-xdd.md" ]
  [ -f "$WINDSURF_HOME/mcp_config.json" ]
  grep -q "helios" "$WINDSURF_HOME/mcp_config.json"
  rm -rf "$(dirname "$GEMHOME")" "$(dirname "$CODEX_HOME")"
}
