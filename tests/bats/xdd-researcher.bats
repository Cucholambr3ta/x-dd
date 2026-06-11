#!/usr/bin/env bats
# Tests CLI para scripts/xdd-researcher.py (investigacion autonoma).
# Run: bats tests/bats/xdd-researcher.bats

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  TMP="$(mktemp -d)"
  DB="$TMP/state.db"
  OUT="$TMP/RESEARCH.md"
}

teardown() {
  rm -rf "$TMP"
}

@test "run genera RESEARCH.md y persiste (offline, sin red)" {
  run python3 scripts/xdd-researcher.py --db "$DB" run --scope system --out "$OUT"
  [ "$status" -eq 0 ]
  [ -f "$OUT" ]
  [[ "$output" == *"propuestas"* ]]
}

@test "RESEARCH.md no contiene emojis" {
  python3 scripts/xdd-researcher.py --db "$DB" run --scope system --out "$OUT"
  run grep -cP '[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}]' "$OUT"
  [ "$output" -eq 0 ]
}

@test "list muestra propuestas tras run" {
  python3 scripts/xdd-researcher.py --db "$DB" run --scope system --out "$OUT"
  run python3 scripts/xdd-researcher.py --db "$DB" list
  [ "$status" -eq 0 ]
  [[ "$output" == *"propuestas"* ]]
}

@test "apply con ID inexistente → exit 1" {
  python3 scripts/xdd-researcher.py --db "$DB" run --scope system --out "$OUT"
  run python3 scripts/xdd-researcher.py --db "$DB" apply rp_nope
  [ "$status" -eq 1 ]
}

@test "scope project filtra distinto a system" {
  run python3 scripts/xdd-researcher.py --db "$DB" --json run --scope project --out "$OUT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"\"ok\": true"* ]]
}
