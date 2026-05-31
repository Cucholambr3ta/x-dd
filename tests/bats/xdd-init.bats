#!/usr/bin/env bats
# Tests para scripts/xdd-init.sh (Sprint 7.5).

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  DEST="$(mktemp -d)/xdd-test-project"
}

teardown() {
  [ -n "${DEST:-}" ] && [ -d "$(dirname "$DEST")" ] && rm -rf "$(dirname "$DEST")"
}

@test "xdd-init --version" {
  run bash scripts/xdd-init.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-init v"* ]]
}

@test "xdd-init --help muestra perfiles" {
  run bash scripts/xdd-init.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"--profile"* ]]
  [[ "$output" == *"minimal"* ]]
}

@test "xdd-init --list-profiles lista los 6 perfiles" {
  run bash scripts/xdd-init.sh --list-profiles
  [ "$status" -eq 0 ]
  for p in minimal core developer security research full; do
    [[ "$output" == *"$p"* ]]
  done
}

@test "xdd-init falla si destino == repo X-DD" {
  run bash scripts/xdd-init.sh "$ROOT"
  [ "$status" -eq 1 ]
}

@test "xdd-init perfil minimal crea estructura mínima" {
  run bash scripts/xdd-init.sh "$DEST" --profile=minimal
  [ "$status" -eq 0 ]
  [ -f "$DEST/memoria.md" ]
  [ -f "$DEST/lecciones.md" ]
  [ -f "$DEST/xdd.profile.yml" ]
  [ -d "$DEST/.git" ]
}

@test "xdd-init perfil minimal NO instala mcp-server ni hooks" {
  bash scripts/xdd-init.sh "$DEST" --profile=minimal >/dev/null
  [ ! -d "$DEST/xdd-mcp-server" ]
  [ ! -d "$DEST/.agent/hooks" ]
}

@test "xdd-init perfil developer SÍ instala mcp + hooks" {
  bash scripts/xdd-init.sh "$DEST" --profile=developer >/dev/null
  [ -d "$DEST/xdd-mcp-server" ]
  [ -d "$DEST/.agent/hooks" ]
}

@test "xdd-init perfil desconocido falla" {
  run bash scripts/xdd-init.sh "$DEST" --profile=nonexistent
  [ "$status" -eq 1 ]
}

@test "xdd-init es idempotente (segundo run no duplica)" {
  bash scripts/xdd-init.sh "$DEST" --profile=minimal >/dev/null
  run bash scripts/xdd-init.sh "$DEST" --profile=minimal
  [ "$status" -eq 0 ]
  [[ "$output" == *"SKIP existente"* ]]
}

@test "xdd-init instala git post-commit cuando el hook está presente (gap post-v0.1.1)" {
  # Perfil developer copia scripts/ (incluye scripts/hooks/post-commit).
  XDD_NO_ADAPT=1 XDD_NO_HOOKS=1 bash scripts/xdd-init.sh "$DEST" --profile=developer >/dev/null 2>&1
  if [ -f "$DEST/scripts/hooks/post-commit" ]; then
    run git -C "$DEST" config --get core.hooksPath
    [ "$status" -eq 0 ]
    [[ "$output" == *"scripts/hooks"* ]]
  else
    skip "perfil developer no copió scripts/hooks/post-commit"
  fi
}
