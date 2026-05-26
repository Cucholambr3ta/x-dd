# Sprint 7 — Build Report (Adapters + Hooks + Manifests + install.ps1 + E2E)

> Fase 4-Build (5/5). Cierre de la fase de construcción más extensa del plan
> maximalista. Suma 97 tests al framework (35 bats + 50 pytest + 12 E2E).

## Tareas MEJORAS abordadas
- **1.4** (alcance reducido por ADR-0007): adapter claude-code + opencode
- **4.1-4.4** (testing del framework): suite bats + pytest + E2E
- **Sobre-mejoras de inspiración ECC** (plan v1.2):
  - Hook system event-driven (8 hooks bash cross-platform)
  - Manifest-driven install con 6 perfiles
  - `install.ps1` Windows-friendly
  - Schema JSON para cada manifest

## Entregables

| Sub-fase | Artefacto | Estado |
|----------|-----------|--------|
| 7.1 | `scripts/xdd-adapt.sh` (claude-code, opencode, all, --dry-run, --list) | ✅ |
| 7.2 | `.agent/hooks/{hooks.json, scripts/*.sh, README.md}` + `schemas/hooks.schema.json` + `docs/HOOKS.md` | ✅ |
| 7.3 | `manifests/install-{profiles,modules,components}.json` + `schemas/install-*.schema.json` + `docs/INSTALL_PROFILES.md` + `scripts/xdd-init.sh` extendido con `--profile`/`--modules`/`--list-profiles` | ✅ |
| 7.4 | `install.ps1` cross-platform paridad con install.sh | ✅ |
| 7.5 | `tests/bats/{xdd-doctor,xdd-init,xdd-adapt,hooks}.bats` (35 tests) + `tests/test_manifests.py` (13 tests) | ✅ |
| 7.6 | `tests/e2e/test_quickstart.bats` (12 escenarios E2E) | ✅ |
| 7.7 | `.xdd/qa/QA_REPORT.md` + este REPORT | ✅ |

## Estadísticas

| Métrica | Valor |
|---------|-------|
| Archivos creados | 26 |
| Archivos modificados | 3 (scripts/xdd-init.sh, .agent/hooks/scripts/pre-write-doc-warning.sh, scripts/xdd-adapt.sh fix) |
| LOC añadidas | ~2100 |
| Tests añadidos | 60 (35 bats + 13 pytest manifests + 12 E2E) |
| Schemas JSON nuevos | 4 (hooks + install-{profiles,modules,components}) |
| Hooks event-driven | 8 (3 PreToolUse, 2 PostToolUse, 1 SessionStart, 2 Stop) |
| Profiles de install | 6 (minimal, core, developer, security, research, full) |
| Modules de install | 13 (9 disponibles, 4 reservados para Sprints 9-12) |

## Validaciones

```bash
# Lint
bash scripts/lint-workflows.sh
# → 0 errores, 0 warnings

# Doctor
bash scripts/xdd-doctor.sh
# → 0 críticos

# Bats suite
bats tests/bats/
# → 35/35 verde

# Pytest suite
python3 -m pytest tests/ -q
# → 50/50 verde (17 gate + 17 mcp + 13 manifests + 3 nuevos)

# E2E Quickstart
bats tests/e2e/test_quickstart.bats
# → 12/12 verde

# Manifests validan contra schemas
python3 -m pytest tests/test_manifests.py -v
# → 13/13 verde
```

## Sobre-mejoras vs plan original

| Sobre-mejora | Origen | Implementada |
|--------------|--------|--------------|
| Hook system event-driven (8 hooks) | ECC inspiration | ✅ con whitelist patterns peligrosos |
| Manifest-driven install profiles | ECC inspiration | ✅ con --modules override |
| install.ps1 cross-platform | ECC inspiration | ✅ paridad con install.sh |
| Schemas para hooks + manifests | (decisión X-DD) | ✅ |
| Tests E2E del Quickstart | plan original ampliado | ✅ |

## Decisiones técnicas

1. **Hooks en Bash, no Node** — sigue ADR-0003 (Python stdlib pura); Bash es más auditable
2. **Symlinks en xdd-adapt.sh** (DRY pattern) — workflows SSoT compartidos con .claude/commands
3. **`XDD_HOOK_PROFILE`, `XDD_DISABLED_HOOKS`, `XDD_ALLOW_CONFIG_EDIT`** — runtime control vía env (patrón ECC)
4. **`available_from` en modules** — declara módulos futuros (Sprint 9-12) sin romper instalador
5. **AGENTS.md auto-generado** desde registry — coherente con SSoT-derived docs/equipo.md
6. **Re-aprobación legítima de fases** post-cambio — caso real Sprint 7 con DOMAIN.md tras PR #6

## Cobertura threat model

Ver [QA_REPORT.md](../../qa/QA_REPORT.md) sección Seguridad: 11/11 amenazas críticas mitigadas.

## Aprendizajes
Ver entradas Sprint 7 en `../../../lecciones.md`.

## Próximo paso
**Sprint 8 ampliado** — Gobernanza OSS + 3-tier docs + commitlint + WORKING-CONTEXT.md + agent.yaml + research/.
