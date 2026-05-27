#!/usr/bin/env bats
# Tests para scripts/xdd-monorepo.sh (Sprint 15, ADR-0013).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  TEST_DIR="$(mktemp -d)/monorepo-test"
  mkdir -p "$TEST_DIR"
}

teardown() {
  [ -n "${TEST_DIR:-}" ] && [ -d "$(dirname "$TEST_DIR")" ] && rm -rf "$(dirname "$TEST_DIR")"
}

@test "xdd-monorepo --version" {
  run bash scripts/xdd-monorepo.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-monorepo v"* ]]
}

@test "xdd-monorepo --help" {
  run bash scripts/xdd-monorepo.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"isolated"* ]]
  [[ "$output" == *"shared"* ]]
  [[ "$output" == *"hybrid"* ]]
}

@test "detect: empty dir not a monorepo (exit 1)" {
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 1 ]
}

@test "detect: nx.json → nx" {
  echo '{}' > "$TEST_DIR/nx.json"
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "nx" ]
}

@test "detect: turbo.json → turborepo" {
  echo '{}' > "$TEST_DIR/turbo.json"
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "turborepo" ]
}

@test "detect: pnpm-workspace.yaml → pnpm-workspaces" {
  echo "packages:" > "$TEST_DIR/pnpm-workspace.yaml"
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "pnpm-workspaces" ]
}

@test "detect: Cargo.toml workspace → cargo-workspaces" {
  cat > "$TEST_DIR/Cargo.toml" <<'EOF'
[workspace]
members = ["api"]
EOF
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "cargo-workspaces" ]
}

@test "detect: go.work → go-workspaces" {
  echo 'go 1.21' > "$TEST_DIR/go.work"
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "go-workspaces" ]
}

@test "detect: package.json with workspaces → yarn-workspaces" {
  cat > "$TEST_DIR/package.json" <<'EOF'
{"name":"r","workspaces":["packages/*"]}
EOF
  run bash scripts/xdd-monorepo.sh detect "$TEST_DIR"
  [ "$status" -eq 0 ]
  [ "$output" = "yarn-workspaces" ]
}

@test "suggest: nx → hybrid mode + sample yaml" {
  echo '{}' > "$TEST_DIR/nx.json"
  run bash scripts/xdd-monorepo.sh suggest "$TEST_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"tool: nx"* ]]
  [[ "$output" == *"suggested_mode: hybrid"* ]]
  [[ "$output" == *"monorepo:"* ]]
  [[ "$output" == *"mode: hybrid"* ]]
}

@test "suggest: lerna → isolated" {
  echo '{}' > "$TEST_DIR/lerna.json"
  run bash scripts/xdd-monorepo.sh suggest "$TEST_DIR"
  [ "$status" -eq 0 ]
  [[ "$output" == *"suggested_mode: isolated"* ]]
}

@test "schema: monorepo section válido y con 3 modos" {
  run python3 -c "
import json
s = json.load(open('schemas/xdd.profile.schema.json'))
m = s['properties']['monorepo']
assert m['required'] == ['mode']
assert set(m['properties']['mode']['enum']) == {'isolated', 'shared', 'hybrid'}
assert 'nx' in m['properties']['tool']['enum']
print('OK')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OK"* ]]
}
