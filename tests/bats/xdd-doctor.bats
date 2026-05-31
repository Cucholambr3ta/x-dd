#!/usr/bin/env bats
# Tests para scripts/xdd-doctor.sh (Sprint 7.5).
# Run: bats tests/bats/xdd-doctor.bats

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
}

@test "xdd-doctor --version" {
  run bash scripts/xdd-doctor.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-doctor v"* ]]
}

@test "xdd-doctor --help" {
  run bash scripts/xdd-doctor.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"diagnóstico"* ]]
}

@test "xdd-doctor con flag desconocido falla" {
  run bash scripts/xdd-doctor.sh --bogus-flag
  [ "$status" -eq 2 ]
}

@test "xdd-doctor en repo X-DD termina con 0 críticos" {
  run bash scripts/xdd-doctor.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"0 faltantes críticos"* ]]
}

@test "xdd-doctor --json produce JSON parseable" {
  run bash scripts/xdd-doctor.sh --json
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "import json, sys; json.load(sys.stdin)"
}

@test "xdd-doctor --json incluye summary y checks" {
  run bash scripts/xdd-doctor.sh --json
  [ "$status" -eq 0 ]
  count=$(echo "$output" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['checks']))")
  [ "$count" -gt 10 ]
}

@test "xdd-doctor --json incluye mempalace_mode y gitnexus_enabled (S5)" {
  run bash scripts/xdd-doctor.sh --json
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert 'mempalace_mode' in d, 'falta mempalace_mode'
assert d['mempalace_mode'] in ('complete', 'base'), 'valor inválido'
assert 'gitnexus_enabled' in d, 'falta gitnexus_enabled'
assert isinstance(d['gitnexus_enabled'], bool), 'gitnexus_enabled debe ser bool'
"
}

@test "xdd-doctor human output muestra modo operativo (S5)" {
  run bash scripts/xdd-doctor.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"Modo operativo"* ]] || [[ "$output" == *"COMPLETO"* ]] || [[ "$output" == *"BASE"* ]]
}
