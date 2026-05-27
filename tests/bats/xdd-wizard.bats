#!/usr/bin/env bats
# Tests para scripts/xdd-wizard.sh (Sprint 14, ADR-0012).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  TEST_DIR="$(mktemp -d)/wizard-test"
  mkdir -p "$TEST_DIR"
}

teardown() {
  [ -n "${TEST_DIR:-}" ] && [ -d "$(dirname "$TEST_DIR")" ] && rm -rf "$(dirname "$TEST_DIR")"
}

@test "xdd-wizard --version" {
  run bash scripts/xdd-wizard.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-wizard v"* ]]
}

@test "xdd-wizard --help" {
  run bash scripts/xdd-wizard.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Interactive bootstrap wizard"* ]]
  [[ "$output" == *"--non-interactive"* ]]
}

@test "xdd-wizard unknown option rejects" {
  run bash scripts/xdd-wizard.sh --bogus
  [ "$status" -ne 0 ]
}

@test "xdd-wizard --non-interactive picks defaults (core profile, single, X-DD)" {
  run bash scripts/xdd-wizard.sh --dest="$TEST_DIR/proj" --non-interactive
  [ "$status" -eq 0 ]
  [ -f "$TEST_DIR/proj/xdd.profile.yml" ]
  [ -f "$TEST_DIR/proj/memoria.md" ]
  # Non-interactive default profile=core, no workspace section, no custom branding
  ! grep -q "^workspace:" "$TEST_DIR/proj/xdd.profile.yml"
  ! grep -q "^branding:" "$TEST_DIR/proj/xdd.profile.yml"
}

@test "xdd-wizard schema includes workspace section" {
  run python3 -c "
import json
s = json.load(open('schemas/xdd.profile.schema.json'))
assert 'workspace' in s['properties'], 'workspace missing'
assert 'projects' in s['properties']['workspace']['properties']
assert 'shared_memory' in s['properties']['workspace']['properties']
print('OK')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OK"* ]]
}
