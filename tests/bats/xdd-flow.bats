#!/usr/bin/env bats
# Tests para scripts/xdd-flow.py (Branch 2 — gate ejecutable de flujos).
# Run: bats tests/bats/xdd-flow.bats

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  TMP="$(mktemp -d)"
}

teardown() {
  rm -rf "$TMP"
}

@test "xdd-flow --version" {
  run python3 scripts/xdd-flow.py --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-flow"* ]]
}

@test "xdd-flow --self-test pasa (determinista, sin red)" {
  run python3 scripts/xdd-flow.py --self-test
  [ "$status" -eq 0 ]
  [[ "$output" == *"self-test OK"* ]]
}

@test "xdd-flow run con expected correcto → exit 0" {
  cat > "$TMP/f.json" <<'EOF'
{"agents":[{"name":"a","default":"ok"}],"mode":"sequential","input":"i","expected":"ok"}
EOF
  run python3 scripts/xdd-flow.py run --flow "$TMP/f.json" --trace "$TMP/t.json"
  [ "$status" -eq 0 ]
  [ -f "$TMP/t.json" ]
}

@test "xdd-flow run con expected incorrecto → exit 1" {
  cat > "$TMP/f.json" <<'EOF'
{"agents":[{"name":"a","default":"no"}],"mode":"sequential","input":"i","expected":"yes"}
EOF
  run python3 scripts/xdd-flow.py run --flow "$TMP/f.json" --no-write
  [ "$status" -eq 1 ]
}

@test "xdd-flow run con flujo inexistente → exit 2" {
  run python3 scripts/xdd-flow.py run --flow "$TMP/nope.json" --no-write
  [ "$status" -eq 2 ]
}
