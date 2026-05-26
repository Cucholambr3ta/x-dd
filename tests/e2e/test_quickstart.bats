#!/usr/bin/env bats
# E2E del Quickstart de X-DD (Sprint 7.6).
# Simula la experiencia de un usuario que clona el repo y arranca un proyecto.
# Objetivo: validar que el Quickstart documentado en README funciona end-to-end.

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  E2E_DIR="$(mktemp -d)/quickstart-test"
}

teardown() {
  [ -n "${E2E_DIR:-}" ] && [ -d "$(dirname "$E2E_DIR")" ] && rm -rf "$(dirname "$E2E_DIR")"
}

@test "E2E paso 1: doctor del repo X-DD termina con 0 críticos" {
  run bash scripts/xdd-doctor.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"0 faltantes críticos"* ]]
}

@test "E2E paso 2: lint-workflows.sh limpio" {
  run bash scripts/lint-workflows.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"0 errores"* ]]
}

@test "E2E paso 3: validate-registry.py limpio (strict)" {
  run python3 scripts/validate-registry.py --strict
  [ "$status" -eq 0 ]
  [[ "$output" == *"180 agents OK"* ]]
}

@test "E2E paso 4: tests del gate keeper 17/17" {
  run python3 -m pytest tests/test_gate.py -q
  [ "$status" -eq 0 ]
  [[ "$output" == *"17 passed"* ]]
}

@test "E2E paso 5: tests del MCP server 17/17" {
  run python3 -m pytest tests/test_mcp_server.py -q
  [ "$status" -eq 0 ]
  [[ "$output" == *"17 passed"* ]]
}

@test "E2E paso 6: xdd-init crea proyecto core funcional" {
  run bash scripts/xdd-init.sh "$E2E_DIR" --profile=core
  [ "$status" -eq 0 ]

  # Estructura mínima esperada
  [ -f "$E2E_DIR/memoria.md" ]
  [ -f "$E2E_DIR/lecciones.md" ]
  [ -f "$E2E_DIR/xdd.profile.yml" ]
  [ -d "$E2E_DIR/.git" ]
  [ -d "$E2E_DIR/scripts" ]
  [ -d "$E2E_DIR/.agent/workflows" ]
  [ -d "$E2E_DIR/prompts/agents" ]
}

@test "E2E paso 7: doctor en proyecto recién creado termina con 0 críticos" {
  bash scripts/xdd-init.sh "$E2E_DIR" --profile=core >/dev/null
  cd "$E2E_DIR"
  run bash scripts/xdd-doctor.sh
  [ "$status" -eq 0 ]
}

@test "E2E paso 8: gate keeper init genera .gate-key" {
  bash scripts/xdd-init.sh "$E2E_DIR" --profile=core >/dev/null
  cd "$E2E_DIR"
  # gate keeper requiere .xdd/ — lo creamos
  mkdir -p .xdd/briefing
  run python3 scripts/xdd-gate.py init
  [ "$status" -eq 0 ]
  [ -f .xdd/.gate-key ]
}

@test "E2E paso 9: xdd-adapt claude-code crea symlinks DRY" {
  bash scripts/xdd-init.sh "$E2E_DIR" --profile=developer >/dev/null
  cd "$E2E_DIR"
  run bash scripts/xdd-adapt.sh claude-code --dest=.
  [ "$status" -eq 0 ]
  [ -d .claude/commands ]
  count=$(ls .claude/commands | wc -l)
  [ "$count" -gt 30 ]
}

@test "E2E paso 10: MCP server smoke test responde 6 tools" {
  run python3 -m "xdd-mcp-server" --check
  [ "$status" -eq 0 ]
  count=$(echo "$output" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['tools']))")
  [ "$count" -eq 6 ]
}

@test "E2E paso 11: bats tests/bats/ todo verde" {
  run bats tests/bats/
  [ "$status" -eq 0 ]
}

@test "E2E paso 12: dogfooding del propio X-DD — fases briefing/spec/plan APROBADAS" {
  # Verificar que el dogfooding funciona en el repo X-DD mismo
  cd "$ROOT"
  for phase in briefing spec plan; do
    run python3 scripts/xdd-gate.py validate --phase "$phase"
    [ "$status" -eq 0 ]
  done
}
