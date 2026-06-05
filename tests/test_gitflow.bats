#!/usr/bin/env bats
# tests/test_gitflow.bats — Tests para xdd-gitflow.sh (Inc 7)

SCRIPT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)/scripts/xdd-gitflow.sh"

setup() {
  # Repo git temporal aislado
  TEST_REPO="$(mktemp -d)"
  cd "$TEST_REPO"
  git init -q
  git config user.email "test@xdd.test"
  git config user.name "Test"
  git checkout -b main -q
  git commit --allow-empty -m "init" -q
}

teardown() {
  rm -rf "$TEST_REPO"
}

# ── setup ────────────────────────────────────────────────────────────────────

@test "setup dev: crea branch develop" {
  run bash "$SCRIPT" setup --mode=dev
  [ "$status" -eq 0 ]
  git rev-parse --verify develop
}

@test "setup collab: guarda modo collab" {
  run bash "$SCRIPT" setup --mode=collab
  [ "$status" -eq 0 ]
  [ "$(cat .xdd/gitflow.mode)" = "collab" ]
}

@test "setup: modo invalido falla" {
  run bash "$SCRIPT" setup --mode=invalid
  [ "$status" -ne 0 ]
}

@test "setup: añade patrones X-DD al .gitignore" {
  run bash "$SCRIPT" setup --mode=dev
  [ "$status" -eq 0 ]
  grep -q "acuerdos/" .gitignore
  grep -q "memoria.md" .gitignore
  grep -q "lecciones.md" .gitignore
}

@test "setup: no duplica patrones en .gitignore" {
  bash "$SCRIPT" setup --mode=dev
  bash "$SCRIPT" setup --mode=dev
  count=$(grep -c "^acuerdos/$" .gitignore || true)
  [ "$count" -eq 1 ]
}

# ── sprint-start ─────────────────────────────────────────────────────────────

@test "sprint-start: crea branch feature/sprint-01-titulo" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1 --title=auth
  [ "$status" -eq 0 ]
  git rev-parse --verify "feature/sprint-01-auth"
}

@test "sprint-start: sin --sprint falla" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --title=auth
  [ "$status" -ne 0 ]
}

@test "sprint-start: sin --title falla" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1
  [ "$status" -ne 0 ]
}

@test "sprint-start: type=fix crea branch fix/sprint-01-titulo" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=1 --title=hotfix --type=fix
  [ "$status" -eq 0 ]
  git rev-parse --verify "fix/sprint-01-hotfix"
}

@test "sprint-start: normaliza numero de sprint a 2 digitos" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" sprint-start --sprint=3 --title=dashboard
  [ "$status" -eq 0 ]
  git rev-parse --verify "feature/sprint-03-dashboard"
}

# ── pre-push ─────────────────────────────────────────────────────────────────

@test "pre-push: XDD_SKIP_PREPUSH=1 pasa sin checks" {
  bash "$SCRIPT" setup --mode=dev
  run env XDD_SKIP_PREPUSH=1 bash "$SCRIPT" pre-push
  [ "$status" -eq 0 ]
}

@test "pre-push: bloquea si artefacto X-DD staged" {
  bash "$SCRIPT" setup --mode=dev
  mkdir -p acuerdos
  echo "test" > acuerdos/idea.md
  # -f porque acuerdos/ ya esta en .gitignore (correcto); el test simula override accidental
  git add -f acuerdos/idea.md
  run bash "$SCRIPT" pre-push
  [ "$status" -ne 0 ]
  [[ "$output" == *"Artefactos X-DD"* ]]
}

@test "pre-push: pasa si staging limpio de artefactos X-DD" {
  bash "$SCRIPT" setup --mode=dev
  echo "src code" > main.py
  git add main.py
  run env XDD_SKIP_GITLEAKS=1 bash "$SCRIPT" pre-push
  [ "$status" -eq 0 ]
}

# ── status ────────────────────────────────────────────────────────────────────

@test "status: muestra modo y branch actual" {
  bash "$SCRIPT" setup --mode=dev
  run bash "$SCRIPT" status
  [ "$status" -eq 0 ]
  [[ "$output" == *"Modo"* ]]
  [[ "$output" == *"dev"* ]]
}

# ── fuera de repo git ─────────────────────────────────────────────────────────

@test "sprint-start sin repo git falla con mensaje claro" {
  tmp=$(mktemp -d)
  cd "$tmp"
  run bash "$SCRIPT" sprint-start --sprint=1 --title=test
  [ "$status" -ne 0 ]
  [[ "$output" == *"No es un repositorio git"* ]]
  rm -rf "$tmp"
}

# ── setup repo: --local / --create (ADR-0052) ────────────────────────────────

@test "setup --local: escribe remote marker local + skip remoto" {
  run bash "$SCRIPT" setup --mode=dev --local
  [ "$status" -eq 0 ]
  [ "$(cat .xdd/gitflow.remote)" = "local" ]
}

@test "setup --create: requiere gh — err accionable si ausente" {
  # Stub PATH sin gh
  stubdir="$(mktemp -d)"
  ln -s "$(command -v git)" "$stubdir/git"
  ln -s "$(command -v bash)" "$stubdir/bash"
  ln -s "$(command -v mktemp)" "$stubdir/mktemp" 2>/dev/null || true
  run env PATH="$stubdir" bash "$SCRIPT" setup --mode=dev --create --name=x
  [ "$status" -ne 0 ]
  [[ "$output" == *"gh"* ]]
  rm -rf "$stubdir"
}

@test "setup --create: con gh stub crea repo + remote marker" {
  stubdir="$(mktemp -d)"
  cat > "$stubdir/gh" << 'STUB'
#!/bin/bash
case "$1" in
  auth) exit 0 ;;
  repo) [ "$2" = "create" ] && { git remote add origin "https://github.com/t/$3.git" 2>/dev/null; exit 0; } ;;
esac
exit 0
STUB
  chmod +x "$stubdir/gh"
  run env PATH="$stubdir:$PATH" bash "$SCRIPT" setup --mode=dev --create --name=myrepo --visibility=private
  [ "$status" -eq 0 ]
  [ "$(cat .xdd/gitflow.remote)" = "remote" ]
  rm -rf "$stubdir"
}

@test "setup --visibility invalida falla" {
  run bash "$SCRIPT" setup --mode=dev --local --visibility=secret
  [ "$status" -ne 0 ]
}
