#!/usr/bin/env bats
# Tests Sprint 31 / ADR-0041 — xdd-organize.sh auto-organize + auto-gitignore.

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  DEST="$(mktemp -d)/xdd-organize-test"
  mkdir -p "$DEST"
}

teardown() {
  [ -n "${DEST:-}" ] && [ -d "$(dirname "$DEST")" ] && rm -rf "$(dirname "$DEST")"
}

@test "xdd-organize --version" {
  run bash scripts/xdd-organize.sh --version
  [ "$status" -eq 0 ]
  [[ "$output" == *"xdd-organize v"* ]]
}

@test "xdd-organize --help" {
  run bash scripts/xdd-organize.sh --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"auto-organize"* ]]
  [[ "$output" == *"check"* ]]
  [[ "$output" == *"apply"* ]]
  [[ "$output" == *"init"* ]]
}

@test "xdd-organize init crea 7 dirs canónicos + .gitkeep + README" {
  run bash scripts/xdd-organize.sh init --dest="$DEST"
  [ "$status" -eq 0 ]
  for d in idea docs api design assets src tests; do
    [ -d "$DEST/$d" ]
    [ -f "$DEST/$d/.gitkeep" ]
    [ -f "$DEST/$d/README.md" ]
  done
}

@test "xdd-organize check NO escribe nada (dry-run default)" {
  touch "$DEST/SPEC.md" "$DEST/.env"
  run bash scripts/xdd-organize.sh check --dest="$DEST"
  [ "$status" -eq 0 ]
  # SPEC.md NO movido (dry-run)
  [ -f "$DEST/SPEC.md" ]
  [ ! -f "$DEST/docs/SPEC.md" ]
  # .gitignore NO creado
  [ ! -f "$DEST/.gitignore" ]
}

@test "xdd-organize apply mueve SPEC.md → docs/" {
  touch "$DEST/SPEC.md"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  [ ! -f "$DEST/SPEC.md" ]
  [ -f "$DEST/docs/SPEC.md" ]
}

@test "xdd-organize apply mueve DOMAIN.md THREATS.md DISCOVERY.md → docs/" {
  for f in DOMAIN.md THREATS.md DISCOVERY.md PLAN.md; do
    touch "$DEST/$f"
  done
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  for f in DOMAIN.md THREATS.md DISCOVERY.md PLAN.md; do
    [ ! -f "$DEST/$f" ]
    [ -f "$DEST/docs/$f" ]
  done
}

@test "xdd-organize apply gitignore caches (node_modules, __pycache__, .venv)" {
  mkdir -p "$DEST/node_modules" "$DEST/__pycache__" "$DEST/.venv"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/.gitignore" ]
  grep -q "^node_modules" "$DEST/.gitignore"
  grep -q "^__pycache__" "$DEST/.gitignore"
  grep -q "^\.venv" "$DEST/.gitignore"
  # NO destruye dirs (gitignore_only, no delete)
  [ -d "$DEST/node_modules" ]
}

@test "xdd-organize apply gitignore secrets (.env, *.pem, *.key) — SecDD" {
  touch "$DEST/.env" "$DEST/cert.pem" "$DEST/server.key"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  [ -f "$DEST/.gitignore" ]
  grep -q "^\.env" "$DEST/.gitignore"
  grep -q "pem" "$DEST/.gitignore"
  grep -q "key" "$DEST/.gitignore"
  # Archivos preservados (solo gitignore, no delete)
  [ -f "$DEST/.env" ]
}

@test "xdd-organize apply gitignore framework copies (prompts/scripts/skills/templates)" {
  mkdir -p "$DEST/prompts" "$DEST/scripts" "$DEST/skills" "$DEST/templates"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  for pat in prompts scripts skills templates; do
    grep -q "^${pat}" "$DEST/.gitignore"
  done
}

@test "xdd-organize apply idempotente (2x = mismo .gitignore)" {
  touch "$DEST/.env"
  bash scripts/xdd-organize.sh apply --dest="$DEST" >/dev/null 2>&1
  local first
  first=$(wc -l < "$DEST/.gitignore")
  bash scripts/xdd-organize.sh apply --dest="$DEST" >/dev/null 2>&1
  local second
  second=$(wc -l < "$DEST/.gitignore")
  [ "$first" = "$second" ]
}

@test "xdd-organize apply NO mueve si destino ya existe (skip_if_exists)" {
  mkdir -p "$DEST/docs"
  echo "OLD CONTENT" > "$DEST/docs/SPEC.md"
  echo "NEW CONTENT" > "$DEST/SPEC.md"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  # docs/SPEC.md NO sobrescrito
  grep -q "OLD CONTENT" "$DEST/docs/SPEC.md"
  # SPEC.md root preservado (no movido porque destino existe)
  [ -f "$DEST/SPEC.md" ]
}

@test "xdd-organize apply mueve ADR-*.md → docs/adr/" {
  touch "$DEST/ADR-0001-test.md"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  [ ! -f "$DEST/ADR-0001-test.md" ]
  [ -f "$DEST/docs/adr/ADR-0001-test.md" ]
}

@test "xdd-organize opt-out XDD_NO_ORGANIZE=1 skip todo" {
  touch "$DEST/SPEC.md"
  run env XDD_NO_ORGANIZE=1 bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"SKIP"* ]]
  # SPEC.md NO movido
  [ -f "$DEST/SPEC.md" ]
}

@test "xdd-organize apply mueve framework pollution MEJORAS-X-DD.md + INSTALL.md" {
  touch "$DEST/MEJORAS-X-DD.md" "$DEST/INSTALL.md" "$DEST/DEPENDENCIES.md"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  for pat in "MEJORAS-X-DD.md" "INSTALL.md" "DEPENDENCIES.md"; do
    grep -q "$pat" "$DEST/.gitignore"
  done
}

@test "xdd-organize status genera reporte sin escribir" {
  touch "$DEST/SPEC.md" "$DEST/.env"
  run bash scripts/xdd-organize.sh status --dest="$DEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"preview"* ]] || [[ "$output" == *"Total"* ]]
  # No escribe
  [ -f "$DEST/SPEC.md" ]
  [ ! -f "$DEST/.gitignore" ]
}

@test "xdd-organize preserva .gitignore existente del usuario (no destruye)" {
  cat > "$DEST/.gitignore" <<'EOF'
# Existing user gitignore
my-custom-file
build/output/
EOF
  touch "$DEST/.env"
  run bash scripts/xdd-organize.sh apply --dest="$DEST"
  [ "$status" -eq 0 ]
  # Custom existente preservado
  grep -q "^my-custom-file" "$DEST/.gitignore"
  grep -q "build/output/" "$DEST/.gitignore"
  # Nueva entry añadida
  grep -q "^\.env" "$DEST/.gitignore"
}
