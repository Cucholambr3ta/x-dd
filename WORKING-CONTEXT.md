# WORKING CONTEXT — X-DD (live state)

> **Estado vivo del sprint actual.** Distinto a [memoria.md](memoria.md) que es
> bitácora inmutable. Este archivo se sobreescribe en cada cambio de sprint o
> hito. Inspiración: ECC `WORKING-CONTEXT.md`.
>
> El hook `session-start:context-load` (`.agent/hooks/scripts/session-start-context-load.sh`)
> imprime estas primeras 30 líneas al iniciar sesión del orquestador.

## Estado actual

- **Branch:** `fix/docs-sync-s9-s13` (hotfix de doc drift post-S13)
- **Fase X-DD:** F4 Build ext done (Sprints 9-13). Próximo: S14 + release v0.1.0
- **Plan vigente:** Maximalista (S0-13 done, S14 pausado tras docs sync, luego release)
- **Caveman mode:** ON (full) — ahorro tokens ~60% en respuestas al user

## Sprints cerrados (15 PRs)

| # | Sprint | PR | Highlight |
|---|---|---|---|
| 0 | Reconciliación | #1 | 10 ADRs + briefing dogfooded |
| 1 | MemPalace externo + Quickstart | #2 | DEPENDENCIES.md, README reescrito, DOMAIN+THREATS |
| 2 | CI + plan formal | #3 | 4 GitHub Actions + Renovate + pre-commit |
| 3 | doctor v2 + xdd.config | #4 | SemVer real + --json + schema |
| 4 | Gate keeper HMAC ⭐ | #5 | 17 tests pytest + dogfooding firmado |
| 5 | Registry agentes tipado | #7 | 180 agentes auto-migrados + SSoT-derived equipo.md |
| 6 | MCP server propio ⭐ | #8 | 6 tools stdlib pura + docs 6 IDEs |
| 7 | Adapters + Hooks + Manifests | #9 | 8 hooks + 6 profiles + install.ps1 + 97 tests |
| 8 | Gobernanza OSS + 3-tier | #10 | CONTRIBUTING/COC/SECURITY + 3 guides + agent.yaml |
| 9 | Continuous Learning | #11 | xdd-state.py SQLite + /evolve workflow |
| 10 | Skills + Eval-harness | #12 | xdd-talk-compact (compresión tokens propia) + 5 grader types |
| 11 | Multi-agent orchestration | #13 | xdd-orchestrate.py stdlib pura |
| 12 | AgentShield + Shannon dep | #14 | 13 reglas SAST + wrapper shn híbrido + rename + ADR-0010 |
| 13 | White-labeling | #15 | 4 personas + xdd-brand.sh + ADR-0011 |
| -- | fix CI markdownlint | #6 | (entre S5/S6) |

## Métricas live

| Métrica | Valor |
|---------|-------|
| Tests totales verdes | **160+** (102 pytest + 45 bats + 12 E2E) |
| Workflows X-DD | **51** (+/evolve +/orchestrate) |
| Agentes registry | 180 / 15 categorías |
| Skills propias | 2 (xdd-talk-compact, agent-eval) |
| Hooks event-driven | 8 |
| Install profiles | 6 |
| Install modules | 13 |
| ADRs Nygard | **11** (added 0010 Shannon, 0011 white-labeling) |
| Scripts ejecutables | 11 (doctor/init/start/adapt/gate/state/eval/orchestrate/shield/pentest/brand) + install.ps1 |
| AgentShield rules | 13 |
| Branches preservadas en remote | 16 |
| AgentShield audit | **0 crit/high/warning** con `--severity=high` ✓ |

## Tarea inmediata

Sync doc drift detectado:
- README ✅
- CLAUDE.md ✅
- WORKING-CONTEXT.md ✅ (este archivo)
- PROJ-MASTER-PLAN.md (pendiente)
- docs/CHANGELOG.md (pendiente entries S10-13)
- agent.yaml (pendiente)
- INSTALL.md (pendiente)
- 3-tier guides shortform/longform (pendiente)
- lecciones.md (agregar lección de drift)

## Pendiente para v0.1.0

| # | Trabajo | Días | Bloquea release |
|---|---|---|---|
| docs-sync | (este branch) | ~1h | Sí (calidad pública) |
| Sprint 14 | Workspace mode + Wizard interactivo + ADR-0012 | ~3 | Sí |
| Release | tag firmado v0.1.0 + RELEASES/v0.1.0.md + Template Repo activado | ~0.5 | — |

## Blockers

(ninguno)

## Última actualización

2026-05-27 — Branch fix/docs-sync-s9-s13 en curso (~1h trabajo).
