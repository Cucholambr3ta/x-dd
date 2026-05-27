#!/usr/bin/env bats
# Tests para scripts/xdd-brand.sh (Sprint 13).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  TEST_DIR="$(mktemp -d)/brand-test"
  mkdir -p "$TEST_DIR"
}

teardown() {
  [ -n "${TEST_DIR:-}" ] && [ -d "$(dirname "$TEST_DIR")" ] && rm -rf "$(dirname "$TEST_DIR")"
}

@test "xdd-brand --version" {
  run bash scripts/xdd-brand.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-brand v"* ]]
}

@test "xdd-brand --help" {
  run bash scripts/xdd-brand.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"white-labeling"* ]]
}

@test "xdd-brand sin xdd.profile.yml no falla" {
  run bash scripts/xdd-brand.sh "$TEST_DIR"
  [ "$status" -eq 0 ]
}

@test "xdd-brand defaults (sin branding section)" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: custom
EOF
  run bash scripts/xdd-brand.sh --show "$TEST_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"ecosystem_name:"*"X-DD"* ]]
  [[ "$output" == *"orchestrator_trigger:"*"/xdd"* ]]
}

@test "xdd-brand aplica trigger custom" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: custom
branding:
  ecosystem_name: "Helios"
  ecosystem_slug: "helios"
  orchestrator_trigger: "helios"
EOF
  run bash scripts/xdd-brand.sh "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ -L "$TEST_DIR/.claude/commands/helios.md" ] || [ -f "$TEST_DIR/.claude/commands/helios.md" ]
}

@test "xdd-brand escribe branding.json con config" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: saas
branding:
  ecosystem_name: "ACME"
  orchestrator_trigger: "acme"
  orchestrator_persona:
    tone: "casual"
EOF
  run bash scripts/xdd-brand.sh "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ -f "$TEST_DIR/.claude/branding.json" ]
  grep -q '"ecosystem_name": "ACME"' "$TEST_DIR/.claude/branding.json"
  grep -q '"persona": "casual"' "$TEST_DIR/.claude/branding.json"
}

@test "xdd-brand copia persona file" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: custom
branding:
  orchestrator_persona:
    tone: "friendly"
EOF
  run bash scripts/xdd-brand.sh "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ -f "$TEST_DIR/.claude/orchestrator-persona.md" ]
  grep -q "friendly" "$TEST_DIR/.claude/orchestrator-persona.md"
}

@test "xdd-brand --show no escribe nada" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: custom
branding:
  orchestrator_trigger: "test"
EOF
  bash scripts/xdd-brand.sh --show "$TEST_DIR"
  [ ! -d "$TEST_DIR/.claude" ]
}

@test "xdd-brand idempotente" {
  cat > "$TEST_DIR/xdd.profile.yml" <<'EOF'
profile: custom
branding:
  orchestrator_trigger: "test"
EOF
  bash scripts/xdd-brand.sh "$TEST_DIR" >/dev/null
  run bash scripts/xdd-brand.sh "$TEST_DIR"
  [ "$status" -eq 0 ]
}

@test "4 personas presets existen" {
  for p in technical friendly casual formal; do
    [ -f "$ROOT/prompts/orchestrator/personas/$p.md" ]
  done
}
