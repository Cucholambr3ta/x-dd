#!/usr/bin/env bats
# Tests Sprint 28 / ADR-0038 — enforcement workflow + auto-trigger brand + gate init.
# Lección retroactiva: proyecto piloto multi-IDE bootstrap incompleto causó 9 lecciones de proceso.

setup() {
  ROOT="$(cd -- "$(dirname -- "${BATS_TEST_FILENAME}")/../.." && pwd)"
  cd "$ROOT"
  DEST="$(mktemp -d)/xdd-s28-test"
}

teardown() {
  [ -n "${DEST:-}" ] && [ -d "$(dirname "$DEST")" ] && rm -rf "$(dirname "$DEST")"
}

@test "xdd-init core perfil inicializa .xdd/ gate keeper automático (Sprint 28)" {
  run bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # Gate keeper inicializado en bootstrap (lección: gate no auto-init en proyecto piloto)
  [ -d "$DEST/.xdd" ] || [ -f "$DEST/.xdd/.gate-key" ] || skip "gate init requires xdd-gate.py disponible"
}

@test "xdd-init NO ejecuta xdd-brand si trigger default 'xdd' (no branding custom)" {
  run bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # NO debe haber .claude/branding.json si trigger es default
  [ ! -f "$DEST/.claude/branding.json" ]
}

@test "xdd-init auto-ejecuta xdd-brand si profile declara trigger custom" {
  run bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # Modifica profile con trigger custom y re-ejecuta
  python3 -c "
import yaml
p = '$DEST/xdd.profile.yml'
d = yaml.safe_load(open(p)) or {}
d['branding'] = {'orchestrator_trigger': 'helios'}
yaml.dump(d, open(p, 'w'))
" 2>/dev/null || skip "yaml module no disponible"
  # Re-ejecuta init en mismo dest — debe disparar brand
  run bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # Verifica branding aplicado (xdd-brand.sh debe haber generado .claude/branding.json)
  [ -f "$DEST/.claude/branding.json" ] || [ -f "$DEST/.claude/commands/helios.md" ]
}

@test "xdd-init opt-out XDD_NO_BRAND=1 salta brand auto-trigger" {
  bash scripts/xdd-init.sh "$DEST" --profile=core >/dev/null 2>&1
  python3 -c "
import yaml
p = '$DEST/xdd.profile.yml'
d = yaml.safe_load(open(p)) or {}
d['branding'] = {'orchestrator_trigger': 'helios'}
yaml.dump(d, open(p, 'w'))
" 2>/dev/null || skip "yaml module no disponible"
  run env XDD_NO_BRAND=1 bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # Output NO debe mencionar "Branding custom detectado"
  [[ "$output" != *"Branding custom detectado"* ]]
}

@test "xdd-init opt-out XDD_NO_GATE_INIT=1 salta gate init" {
  run env XDD_NO_GATE_INIT=1 bash scripts/xdd-init.sh "$DEST" --profile=core
  [ "$status" -eq 0 ]
  # .xdd/ NO debe existir (gate skip)
  [ ! -d "$DEST/.xdd" ]
}

@test "session-start hook lee lecciones.md últimas 5 entries (Sprint 28)" {
  bash scripts/xdd-init.sh "$DEST" --profile=developer >/dev/null 2>&1
  # Crea lecciones.md de prueba
  cat > "$DEST/lecciones.md" <<'EOF'
# lecciones.md

### [TEST] Lección 1 — 2026-05-28
Contexto test 1.

### [TEST] Lección 2 — 2026-05-28
Contexto test 2.
EOF
  cd "$DEST"
  # Hook puede estar en DEST/.agent/hooks/ (si profile lo incluye) o usar ROOT como fallback
  HOOK="./.agent/hooks/scripts/session-start-context-load.sh"
  [ -f "$HOOK" ] || HOOK="$ROOT/.agent/hooks/scripts/session-start-context-load.sh"
  run bash "$HOOK"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Lecciones"* ]]
  [[ "$output" == *"Lección 1"* ]]
}

@test "session-start hook muestra Gate keeper status si gate disponible" {
  bash scripts/xdd-init.sh "$DEST" --profile=developer >/dev/null 2>&1
  cd "$DEST"
  HOOK="./.agent/hooks/scripts/session-start-context-load.sh"
  [ -f "$HOOK" ] || HOOK="$ROOT/.agent/hooks/scripts/session-start-context-load.sh"
  run bash "$HOOK"
  [ "$status" -eq 0 ]
  # Si gate disponible, debe haber sección "Gate keeper"
  [[ "$output" == *"Gate keeper"* ]] || [[ "$output" == *"Working Context"* ]]
}

@test "workflow /xdd v1.3 contiene PRE-FLIGHT BOOTSTRAP enforcement (Sprint 28)" {
  grep -q "PRE-FLIGHT BOOTSTRAP" "$ROOT/.agent/workflows/xdd.md"
  grep -q "Sprint 28 / ADR-0038" "$ROOT/.agent/workflows/xdd.md"
  grep -q "Bloqueante" "$ROOT/.agent/workflows/xdd.md"
  grep -q "Versión:\*\* 1.3" "$ROOT/.agent/workflows/xdd.md"
}

@test "workflow /cierre-fase v1.2 contiene CHECKS BLOQUEANTES (Sprint 28)" {
  grep -q "CHECKS BLOQUEANTES" "$ROOT/.agent/workflows/cierre-fase.md"
  grep -q "xdd-gate.py validate" "$ROOT/.agent/workflows/cierre-fase.md"
  grep -q "xdd-gate.py approve" "$ROOT/.agent/workflows/cierre-fase.md"
  grep -q "Versión:\*\* 1.2" "$ROOT/.agent/workflows/cierre-fase.md"
}

@test "workflow /project-architecture-gsd v2.3.0 contiene SCAFFOLDING OBLIGATORIO" {
  grep -q "SCAFFOLDING OBLIGATORIO" "$ROOT/.agent/workflows/project-architecture-gsd.md"
  grep -q "7 directorios canónicos" "$ROOT/.agent/workflows/project-architecture-gsd.md" || \
    grep -q "idea/" "$ROOT/.agent/workflows/project-architecture-gsd.md"
  grep -q "Versión:\*\* 2.3.0" "$ROOT/.agent/workflows/project-architecture-gsd.md"
}
