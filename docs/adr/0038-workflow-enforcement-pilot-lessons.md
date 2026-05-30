# ADR-0038 — Workflow enforcement: retroaplicación de lecciones del piloto multi-IDE

- **Fecha:** 2026-05-28
- **Estado:** Accepted
- **Sprint:** 28
- **Decididores:** Maintainer (Alejandro Placencia)
- **Relacionado:** ADR-0034 (Universal IDE adapter), ADR-0037 (Windsurf adapter parity), Sprint 7 (manifests + hooks), Sprint 4 (gate keeper HMAC)

## Contexto

Tras cerrar Sprints 26 (Windsurf adapter) y 27 (serie 6 guías técnicas IDE), el maintainer ejecutó dogfooding del framework usando un **proyecto piloto multi-IDE** real (primer proyecto creado con OpenCode + adapters X-DD). El pipeline gated de 6 fases completó (briefing → spec → plan → build → qa → retro) pero generó **14 entries de aprendizaje** en `lecciones.md` del proyecto piloto.

Análisis por categoría:

| # | Categoría | Cantidad |
|---|---|---|
| 1 | Proceso (orquestador omitió pasos canónicos) | 9 |
| 2 | Técnico (Tauri/npm/Rust) | 4 |
| 3 | Frontend (fallbacks visuales) | 1 |

**Insight crítico:** las 9 lecciones de proceso **NO son por falta de tooling** (scripts existen desde Sprint 4-13). Son por **falta de enforcement en workflows del orquestador**. El LLM ejecutó pasos parciales o saltó secuencias canónicas:

1. `git init` en Fase 2 (debió Fase 1 PRE-FLIGHT)
2. MemPalace no consultado antes de generar SPEC
3. `xdd-init.sh` no usado (bootstrap manual con `mkdir+write`)
4. Subagentes especializados no invocados (orquestador escribió SPEC directo)
5. Post-SPEC: solo `SPEC.md` creado, sin scaffolding físico de directorios
6. `xdd-doctor.sh` no re-ejecutado en sesiones siguientes
7. `xdd-gate.py approve` reemplazado por "APROBADO" verbal
8. `lecciones.md` no actualizado hasta solicitud explícita del usuario
9. `xdd-brand.sh` no ejecutado tras bootstrap (no había `/<trigger>` custom)

Sprint 26 (Windsurf) y Sprint 27 (guías) **no abordan estas lecciones** — son mejoras de adapter/documentación. Las 9 lecciones de proceso requieren modificación de:
- Workflows del orquestador (`/xdd`, `/cierre-fase`, `/project-architecture-gsd`)
- Bootstrap scripts (`xdd-init.sh`)
- Hooks SessionStart

## Decisión

**Retroaplicar las 9 lecciones de proceso al framework** mediante enforcement workflow + bootstrap + hook:

### 1. Workflow `/xdd` v1.3 — PRE-FLIGHT BOOTSTRAP bloqueante

Nueva sección `0. PRE-FLIGHT BOOTSTRAP` (bloqueante) con 4 sub-secciones:

- **0.1 Verifica BOOTSTRAP previo:** si `xdd.profile.yml` no existe → ABORT y solicita `xdd-init.sh`. Si `.xdd/` no existe → ejecuta `xdd-gate.py init`. Si branding custom declarado y NO aplicado → ejecuta `xdd-brand.sh`.
- **0.2 MEMORY SEAL & EXPERIENCE SYNC:** mantiene comportamiento existente (lee memoria/lecciones/CLAUDE/equipo).
- **0.3 AUDIT obligatorio:** `xdd-doctor.sh` bloqueante (exit != 0 escala al usuario). MemPalace search si dominio especificado.
- **0.4 Validación SessionStart hook:** verifica que el hook se ejecutó (output `=== Working Context ===` o `=== Memoria ===`).

Adicional: Sección 1 (PM Mode) recibe nota explícita **"Prohibido escribir código o specs directamente — siempre delega a subagente"**.

### 2. Workflow `/cierre-fase` v1.2 — CHECKS BLOQUEANTES

Nueva sección `0. CHECKS BLOQUEANTES` antes de Sección 1:

- Gate keeper criptográfico (`xdd-gate.py validate --phase=<X>`) — exit != 0 ABORTA cierre
- `lecciones.md` modificado en sesión (verificado vía `git diff`) — caso contrario BLOQUEA cierre
- `memoria.md` modificado en sesión — misma verificación

Sección 5 (Sello de cierre) refactorizada: ejecuta `xdd-gate.py approve --phase=<X>` con firma HMAC-SHA256 (NO "APROBADO" verbal).

### 3. Workflow `/project-architecture-gsd` v2.3.0 — SCAFFOLDING OBLIGATORIO POST-SPEC

Nueva sección `0.bis. SCAFFOLDING OBLIGATORIO POST-SPEC` con pasos enforcement:

- Generar 7 directorios canónicos: `idea/`, `docs/`, `api/`, `design/`, `assets/`, `src/`, `tests/`
- `.gitkeep` en dirs vacíos + `README.md` placeholder (1 línea propósito)
- Mover `SPEC.md` raíz → `docs/SPEC.md` si aplica
- Scaffolding stack-específico según `xdd.profile.yml` (Cargo.toml / package.json / pyproject.toml)
- Generar `conductor.json` si no existe
- **NO transicionar a PLAN si scaffolding incompleto**

### 4. `xdd-init.sh` — auto-trigger `xdd-brand.sh` + gate init

Bloque nuevo post-IDE-adapters:

```bash
# Auto-trigger xdd-brand.sh si profile.branding.orchestrator_trigger != "xdd"
if [ "${XDD_NO_BRAND:-0}" != "1" ] && [ -f "./xdd.profile.yml" ]; then
  TRIGGER_CUSTOM=$(python3 -c "... parse profile ...")
  [ -n "$TRIGGER_CUSTOM" ] && bash ./scripts/xdd-brand.sh "$DEST"
fi

# Auto-init gate keeper si .xdd/ no existe
if [ "${XDD_NO_GATE_INIT:-0}" != "1" ] && [ ! -d "./.xdd" ]; then
  python3 ./scripts/xdd-gate.py init
fi
```

Opt-out env vars: `XDD_NO_BRAND=1` y `XDD_NO_GATE_INIT=1`.

### 5. Hook `SessionStart` reforzado

Extensión del script `.agent/hooks/scripts/session-start-context-load.sh`:

- Lee `lecciones.md` últimas 5 entries (previene repetición de errores)
- Ejecuta `xdd-doctor.sh` resumen (tail -5) — visibilidad de salud
- Ejecuta `xdd-gate.py status` — fase actual + estado

Visibilidad forzada al inicio de cada sesión.

## Alternativas consideradas

### A. Documentar lecciones en doc separado sin modificar workflows

Rechazada. Doc-only no fuerza comportamiento del LLM orquestador. Las 9 lecciones surgieron justamente porque docs existentes (CLAUDE.md, Constitución) no eran consultadas en bootstrap.

### B. Crear nuevo workflow `/bootstrap-check` invocable manualmente

Rechazada. Añade fricción al flujo. Los checks deben ser PRE-FLIGHT automático del workflow `/xdd` ya existente.

### C. Mover enforcement a CI/pre-commit hooks externos

Rechazada. CI corre post-commit — demasiado tarde para enforcement de proceso durante sesión interactiva. Hooks SessionStart son el punto correcto.

### D. Crear un agente `Bootstrap-Auditor` que valide bootstrap

Rechazada. Multiplica abstracciones — los checks son pocas líneas bash que viven mejor inline en `xdd-init.sh` + workflow del orquestador.

### E. Aceptar las lecciones como "cosas que el LLM aprende en runtime"

Rechazada. Repetir 9 errores documentados en cada proyecto nuevo es desperdicio. El framework debe codificar las lecciones, no esperar que cada LLM las redescubra.

## Consecuencias

### Positivas

- **Lecciones retroaplicadas:** las 9 fallas de proceso del piloto se vuelven imposibles de repetir en proyectos nuevos
- **Bootstrap completo automático:** `xdd-init.sh` ahora ejecuta init + gate + brand en single command
- **Cierre auditable:** "APROBADO" verbal imposible — firma HMAC obligatoria
- **Visibilidad lecciones cada sesión:** orquestador ve últimas 5 entries siempre
- **Scaffolding post-SPEC:** PLAN tiene terreno físico donde aterrizar, no solo `SPEC.md` huérfano
- **Opt-outs documentados:** `XDD_NO_BRAND`, `XDD_NO_GATE_INIT` para casos especiales

### Neutras

- Workflow `/xdd` pasa de v1.2 a v1.3
- Workflow `/cierre-fase` pasa de v1.1 a v1.2
- Workflow `/project-architecture-gsd` pasa de v2.2.0 a v2.3.0
- Suite tests bats crece con `xdd-init-sprint28.bats` (10 casos)

### Negativas (aceptadas)

- Bootstrap toma más tiempo (auto-brand + gate init añaden ~2-3 segundos)
- Cierre de fase requiere `lecciones.md` modificado siempre — proyectos sin lecciones nuevas deben añadir entry "Sin lecciones nuevas esta sesión" como mínimo
- SessionStart hook crece de ~20 líneas a ~45 (más output al iniciar — controlado por cap 8000 chars)

## Implementación

### Files modificados

| Path | Cambio |
|---|---|
| `.agent/workflows/xdd.md` | v1.2 → v1.3 — nueva Sección 0 PRE-FLIGHT BOOTSTRAP bloqueante |
| `.agent/workflows/cierre-fase.md` | v1.1 → v1.2 — nuevas Secciones 0 (CHECKS BLOQUEANTES) y 5 refactor (gate approve) |
| `.agent/workflows/project-architecture-gsd.md` | v2.2.0 → v2.3.0 — nueva Sección 0.bis SCAFFOLDING OBLIGATORIO |
| `scripts/xdd-init.sh` | +30 líneas — auto-trigger brand + gate init + opt-outs |
| `.agent/hooks/scripts/session-start-context-load.sh` | +25 líneas — lecciones + doctor + gate status |

### Files nuevos

| Path | Propósito |
|---|---|
| `tests/bats/xdd-init-sprint28.bats` | 10 casos cubriendo auto-brand, gate init, opt-outs, hook output, workflow versions |
| `docs/adr/0038-workflow-enforcement-pilot-lessons.md` | Este ADR |

### Tests

- 10/10 verde en `tests/bats/xdd-init-sprint28.bats`
- Regresión limpia: `xdd-init.bats` 9 tests existentes verde
- Lint workflows: 0 errores, 0 warnings

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Usuario quiere bootstrap sin branding aunque profile lo declare | `XDD_NO_BRAND=1` opt-out documentado |
| Usuario quiere bootstrap sin gate keeper | `XDD_NO_GATE_INIT=1` opt-out documentado |
| Cierre bloqueado por `lecciones.md` no modificado en sesión trivial | Mínimo aceptado: 1 entry tipo "Sin nuevas lecciones esta sesión" |
| `xdd-brand.sh` falla durante init | WARN no bloqueante + instrucción re-ejecutar manual |
| Hook SessionStart genera output > 8000 chars | Cap interno + `head -N` por sección |

## Verificación end-to-end

```bash
# Tests Sprint 28
bats tests/bats/xdd-init-sprint28.bats              # 10/10 verde

# Regresión
bats tests/bats/xdd-init.bats                       # 9/9 verde
bats tests/bats/xdd-adapt.bats                      # 18/18 verde (Sprint 26)
bats tests/bats/xdd-adapt-windsurf.bats             # 11/11 verde (Sprint 26)

# Lint
bash scripts/lint-workflows.sh                       # 0 errores

# Smoke test bootstrap completo
mkdir /tmp/test-s28 && bash scripts/xdd-init.sh /tmp/test-s28 --profile=developer
ls /tmp/test-s28/.xdd/.gate-key                      # gate init OK
cat /tmp/test-s28/xdd.profile.yml                    # profile creado
```

## Referencias

- `lecciones.md` proyecto piloto multi-IDE (14 entries, 9 categoría PROCESO) — NO commiteado al repo público (privado del maintainer)
- `.agent/workflows/xdd.md` v1.3 — orquestador con enforcement
- `.agent/workflows/cierre-fase.md` v1.2 — cierre auditable
- `.agent/workflows/project-architecture-gsd.md` v2.3.0 — scaffolding obligatorio
- `scripts/xdd-init.sh` — bootstrap completo single-command
- `.agent/hooks/scripts/session-start-context-load.sh` — visibilidad lecciones + doctor + gate
- ADR-0004 (Sprint 4) — Gate keeper HMAC origen
- Sprint 13 — White-labeling `xdd-brand.sh` origen
- Sprint 7 — Manifests `install-profiles.json` origen
