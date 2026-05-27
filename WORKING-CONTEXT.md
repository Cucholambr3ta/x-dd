# WORKING CONTEXT — X-DD (live state)

> **Estado vivo del sprint actual.** Distinto a [memoria.md](memoria.md) que es
> bitácora inmutable. Este archivo se sobreescribe en cada cambio de sprint o
> hito. Inspiración: ECC `WORKING-CONTEXT.md`.
>
> El hook `session-start:context-load` (`.agent/hooks/scripts/session-start-context-load.sh`)
> imprime estas primeras 30 líneas al iniciar sesión del orquestador.

## Estado actual

- **Branch:** `docs/sync-post-gitnexus` (sync docs post-S14-23 + GitNexus tier-1)
- **Fase X-DD:** F4 Build COMPLETO (Sprints 0-23 done). Próximo: Release v0.1.0
- **Plan vigente:** Maximalista extendido (S0-23 done = 33 ADRs + 11 docs nuevas + 12 scripts nuevos pre-release). User pidió pausa release.
- **Caveman mode:** ON (full) — ~75% reducción tokens
- **Workspace global:** instalado en `/home/alejandro/Documentos/Desarrollos/` (X-DD core profile, post-purga ANMAX, GitNexus tier-1 syncd)

## Sprints cerrados (10 PRs nuevos S14-23 + #30 fix + #32 GitNexus)

| # | Sprint | PR | Highlight |
|---|---|---|---|
| 14 | Workspace + Wizard | #20 | xdd-wizard.sh 7-step + workspace section schema |
| 15 | Monorepo 3 modos | #21 | isolated/shared/hybrid + xdd-monorepo.sh 9 tools |
| 16 | SDD parity + AI review + TF-IDF | #22 | /clarify + /cross-validate + constitution.md + xdd-ai-review + ADRs 14/15/20 |
| 17 | Party + Brainstorm + HITL + Router | #23 | xdd-router.py + party orchestration + ADRs 16/17/18/19 |
| 18 | Observability Triad | #24 | xdd-otel + xdd-replay + xdd-cost + 6-stage middleware + ADRs 21/22 |
| 19 | Context Engineering | #25 | xdd-context budget + xdd-compact + fs-context + code-as-tool + ADRs 23/24 |
| 20 | Eval benchmarks externos | #26 | Inspect AI + TB2 + SWE-bench + LongMemEval + xdd-meta-eval + ADRs 25/26 |
| 21 | Sandbox + Permissions | #27 | xdd-intent + xdd-authz <100ms + sandbox skill + ADRs 27/28 |
| 22 | AHE /evolve | #28 | 3-layer obs + xdd-trace-summarize + xdd-frozen-transfer + ADR 29 |
| 23 | Protocols + Skills ecosystem | #29 | xdd-a2a + xdd-agui + xdd-bundle + plan_and_act + adapt_orch + ADRs 30/31/32 |
| -- | fix lint workflows description | #30 | 4 workflows S16/S17/S19 |
| -- | GitNexus tier-1 companion | #32 | doctor + start + DEPENDENCIES + ADR-0033 |

## Métricas live

| Métrica | Valor |
|---------|-------|
| Tests totales verdes | **~300+** (S14-23 +95 nuevos sobre 160 base S13) |
| Workflows X-DD | **55** (+brainstorm, clarify, cross-validate, code-as-tool) |
| Agentes registry | 180 / 15 categorías |
| Composition patterns | **5** (security_review, feature_squad, release_train, plan_and_act, adapt_orch) |
| Skills propias | **6** (xdd-talk-compact, agent-eval, xdd-ai-review, xdd-compact, xdd-fs-context, xdd-sandbox) |
| Hooks event-driven | **14** (8 base + 6 stage middleware S18) |
| Install profiles | 6 |
| Install modules | 13 |
| **ADRs Nygard** | **33** (10 base + 12 + 11 S14-23 + 0033 GitNexus) |
| Scripts ejecutables | **23** (doctor/init/start/adapt/gate/state/eval/orchestrate/shield/pentest/brand/wizard/monorepo/otel/replay/cost/context/meta-eval/intent/authz/trace-summarize/frozen-transfer/a2a/agui/bundle/router) + install.ps1 |
| MCP companion stack | **3** (xdd-mcp-server MIT + MemPalace MIT + GitNexus PolyForm Noncomm) |
| Eval suites externos | **4** scaffolds (TB2, SWE-bench, Promptfoo, LongMemEval) |
| Sandbox backends declarados | 5 (E2B, Daytona, Microsandbox, docker, none) |
| Permission intents | 8 (filesystem_delete/secret_access/lang_exec/network_outbound/fork_subprocess/filesystem_write/mcp_external/read_only) |
| Bundles ejemplo | 1 (security-bundle.xddbundle) |
| Branches preservadas en remote | **27+** (delete_branch_on_merge=false estricto) |

## Tarea inmediata

Doc sync post-S14-23 + GitNexus tier-1 (este branch):
- ✅ the-shortform-guide.md (sección Sprints 14-23 + Stack MCP)
- ✅ the-longform-guide.md (tabla Sprints completa + stack MCP)
- ✅ the-security-guide.md (sandbox/intent/authz/HITL added + license disclaimers)
- ✅ INSTALL.md (GitNexus install + license disclaimer)
- ✅ agent.yaml (companions MCP + dependencies.recommended)
- ✅ docs/CHANGELOG.md (entries S14-23 + GitNexus)
- ✅ README.en.md / README.pt-BR.md (sync con README.md diagrama + start.sh)
- ✅ WORKING-CONTEXT.md (este archivo)
- ⏳ memoria.md + lecciones.md + PROJ-MASTER-PLAN.md pendientes

## Pendiente para v0.1.0

| # | Trabajo | Días | Bloquea release |
|---|---|---|---|
| docs-sync | (este branch) | ~30min | Sí (calidad pública) |
| Release | tag firmado v0.1.0 + RELEASES/v0.1.0.md + Template Repo activado | ~0.5 | — |

## Blockers

Ninguno. Release pausado por decisión del user (lo activa cuando quiera).

## Última actualización

2026-05-27 — Branch docs/sync-post-gitnexus en curso. Workspace global Desarrollos/ sincronizado con GitNexus tier-1.
