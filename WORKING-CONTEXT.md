# WORKING CONTEXT — X-DD (live state)

> **Estado vivo del sprint actual.** Distinto a [memoria.md](memoria.md) que es
> bitácora inmutable. Este archivo se sobreescribe en cada cambio de sprint o
> hito. Inspiración: ECC `WORKING-CONTEXT.md`.
>
> El hook `session-start:context-load` (`.agent/hooks/scripts/session-start-context-load.sh`)
> imprime estas primeras 30 líneas al iniciar sesión del orquestador.

## Estado actual

- **Sprint:** Sprint 8 ampliado (Gobernanza OSS + 3-tier docs + commitlint + WORKING-CONTEXT + agent.yaml + research/)
- **Branch:** `feat/sprint-8-governance-3tier-release`
- **Fase X-DD:** F6 Retro + Release initialization
- **Plan vigente:** maximalista (Sprints 7-12 todos para v0.1.0)
- **Próximos sprints:** 9 (Continuous Learning), 10 (Skills + Eval), 11 (Orchestration), 12 (AgentShield), Release v0.1.0

## Tarea inmediata

- Crear archivos de gobernanza OSS (CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/NOTICE) ✅
- Issue/PR templates en `.github/ISSUE_TEMPLATE/` ✅
- `devcontainer.json` + `postCreate.sh` ✅
- `agent.yaml` (manifesto plugin interop) ✅
- `commitlint.config.js` + workflow CI ✅
- `WORKING-CONTEXT.md` (este archivo) ✅
- 3-tier docs: `the-shortform-guide.md` / `the-longform-guide.md` / `the-security-guide.md` 🔄
- `docs/research/ECC-inspiration-analysis.md` 🔄
- Trazabilidad + commits + PR + merge

## Blockers

(ninguno actualmente)

## Métricas live

| Métrica | Valor |
|---------|-------|
| Tests totales | 97 (post-Sprint 7) |
| Branches en GitHub | 10 (main + 9 sprints/fixes) |
| Sprints cerrados | 7 de 12 (58%) |
| PRs cerrados | 9 |
| ADRs | 10 |
| Workflows X-DD | 49 |
| Agentes registry | 180 / 15 categorías |
| Hooks event-driven | 8 |
| Install profiles | 6 |

## Decisión pendiente (si aplica)

(ninguna actualmente)

## Última actualización

2026-05-26 — Sprint 8 en progreso. Próxima actualización al cerrar.
