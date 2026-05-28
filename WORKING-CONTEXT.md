# WORKING CONTEXT — X-DD (live state)

> **Estado vivo del sprint actual.** Distinto a [memoria.md](memoria.md) que es
> bitácora inmutable. Este archivo se sobreescribe en cada cambio de sprint o
> hito. Inspiración: ECC `WORKING-CONTEXT.md`.
>
> El hook `session-start:context-load` (`.agent/hooks/scripts/session-start-context-load.sh`)
> imprime estas primeras 30 líneas al iniciar sesión del orquestador.

## Estado actual

- **Branch:** `docs/sync-post-pr40` (sync docs post Sprint 25 + VSCode + Codex + install fixes)
- **Fase X-DD:** F4 Build COMPLETO (Sprints 0-25 done + Codex adapter PR #40). Próximo: Release v0.1.0
- **Plan vigente:** Maximalista extendido. 26 sprints ejecutados. User pidió pausa release.
- **Caveman mode:** ON (ultra) — ~85% reducción tokens
- **Workspace global:** instalado en `<workspace>/` (X-DD core + Sprint 25 wrapper global + auto-detect 7 IDEs)

## PRs cerrados S14-recent

| PR | Sprint/fix | Highlight |
|---|---|---|
| #20-29 | Sprints 14-23 | workspace+monorepo+SDD+protocols+ecosystem+observ+context+evals+sandbox+AHE |
| #30 | fix CI lint workflows description | 4 workflows S16/S17/S19 |
| #32 | GitNexus tier-1 | doctor+start+ADR-0033 |
| #33 | docs sync post-S14-23 | 12 files macro |
| #34 | Sprint 24 Universal IDE adapter | copia real + 6 IDEs + MCP auto-config + ADR-0034 |
| #35 | fix Antigravity ruta real ~/.gemini | + scrub branding privado |
| #36 | Sprint 25 Global install architecture | wrapper PATH + tools.py local-first + ADR-0035 |
| #37 | feat VSCode tasks.json + settings.json | INSTALL_VSCODE.md limpio |
| #38 | fix install docs-governance + AGENTS template | constitucion + 5 docs core sync |
| #39 | fix manifests Sprints 13-25 | 10 módulos nuevos / 18 scripts integrados |
| #40 | feat Codex adapter (7° IDE) | global skills + agents-index + ADR-0036 |

## Métricas live

| Métrica | Valor |
|---------|-------|
| Tests verdes | **~330+** (S14-25 cumulativos) |
| Workflows | **55** |
| Agentes registry | 180 / 15 categorías |
| Composition patterns | 5 |
| Skills propias | **6** |
| Hooks event-driven | **14** (8 base + 6 stage middleware) |
| Install profiles | 6 (minimal/core/developer/security/research/full) |
| Install modules | **24** (14 base + 10 nuevos PR #39) |
| **ADRs Nygard** | **36** (10 base + 26 nuevos) |
| Scripts ejecutables | **27** (Sprints 0-25 completos) |
| **IDEs adapters** | **7** (claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity, codex) |
| MCP companion stack | 3 (xdd-mcp + MemPalace + GitNexus) |
| Branches preservadas remote | **35+** |

## Stack install garantizado (post PR #39)

`xdd-init full` produce:
- AGENTS.md + CLAUDE.md + docs/constitucion.md (governance)
- 5 docs governance (X-DD_Integration / RETROFIT / HOOKS / CONFIG / INSTALL_PROFILES)
- 27 scripts (Sprints 0-25 completos)
- 6 skills propias
- 4 personas presets
- prompts/skills/registry.json
- xdd-mcp-install-global.sh (wrapper Sprint 25)
- Auto-adapt 7 IDEs

## Tarea inmediata

Doc sync post PRs #38-40:
- ⏳ WORKING-CONTEXT.md (este archivo)
- ⏳ memoria.md / lecciones.md / PROJ-MASTER-PLAN.md
- ⏳ docs/CHANGELOG.md (entries PRs #38-40)
- ⏳ README es/en/pt-BR (7 IDEs + 36 ADRs)
- ⏳ shortform/longform/security guides
- ⏳ agent.yaml (companions stats)
- ⏳ INSTALL.md (Sprint 25 wrapper + Codex)

## Pendiente para v0.1.0

| Trabajo | Días | Bloquea release |
|---|---|---|
| docs-sync | ~30min | Sí (calidad pública) |
| Release v0.1.0 | ~0.5 | — |

## Blockers

Ninguno. Release pausado por decisión del user.

## Última actualización

2026-05-28 — docs/sync-post-pr40 en curso. 7 IDEs + 36 ADRs + 27 scripts.
