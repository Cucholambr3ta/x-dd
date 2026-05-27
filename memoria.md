# memoria.md — Flight Recorder del Proyecto

> Bitácora viva del proyecto. **Lectura obligatoria** al inicio de cada sesión (Constitución Art. 3).
> Toda sesión termina actualizando este archivo vía `/cierre-fase`.

## Identidad del Proyecto
- **Nombre:** X-DD — Cross-Driven Development System
- **Dominio:** Framework OSS de desarrollo agéntico multi-IDE
- **Stack:** Bash + Markdown + (Python en construcción para gate keeper y MCP server)
- **Fecha de inicio:** 2025-12 (retrofit completado 2026-05)
- **Repo:** https://github.com/Cucholambr3ta/x-dd

## Estado Actual
- **Fase X-DD:** F4 Build COMPLETO (Sprints 0-23 done + GitNexus tier-1); pendiente solo release v0.1.0
- **Sprint en curso:** **docs/sync-post-gitnexus** (sync docs post-S14-23 + GitNexus)
- **Plan macro:** MAXIMALISTA EXTENDIDO. 23.5d (S0-13) + ~34d (S14-23) = ~57.5d invertidos. Restan ~0.5d (release).
- **Último hito:** GitNexus tier-1 companion mergeado (PR #32) — paralelo MemPalace en xdd-doctor + xdd-start + ADR-0033.
- **Workspace global:** instalado en `/home/alejandro/Documentos/Desarrollos/` (post-purga ANMAX legacy). Backup tar.gz en `~/Desarrollos-anmax-backup-2026-05-27-1025.tar.gz`.
- **Próximo paso:** sync docs (este branch) → Release v0.1.0 cuando user autorice.

## Stats actuales (post-S23 + GitNexus)
- **~300+ tests verdes** (~95 nuevos S14-23 sobre 160 base S13)
- **27+ PRs cerrados** todos preservados (delete_branch_on_merge=false estricto)
- **55 workflows** X-DD (+brainstorm, clarify, cross-validate, code-as-tool)
- **180 agentes** (1 renombrado security-pentest-operator)
- **5 composition_patterns** (+plan_and_act, +adapt_orch Sprint 23)
- **6 skills** propios (xdd-talk-compact, agent-eval, xdd-ai-review, xdd-compact, xdd-fs-context, xdd-sandbox)
- **14 hooks** event-driven (8 base + 6 stage middleware S18)
- **6 install profiles** + 13 modules
- **33 ADRs** Nygard (10 base + 12 + 11 S14-23 + 0033 GitNexus)
- **23 scripts ejecutables** (S14-23 +12 nuevos)
- **3 MCP companion servers** (xdd-mcp + MemPalace + GitNexus)
- **AgentShield** audit propio: 0 crit/high con `--severity=high`

## Decisiones Arquitectónicas Clave
<!-- ADR-lite: una línea por decisión, con fecha y motivo -->
- **2026-05-26 — ADR-0000:** mapeo MEJORAS↔X-DD en una pasada de las 6 fases (no 8 mini-ciclos). Reduce burocracia, mantiene coherencia con Constitución Art. 9.
- **2026-05-26 — ADR-0001:** dogfooding visible y commiteable (`.xdd/`, `memoria.md`, `lecciones.md`, `docs/adr/`, `RELEASES/`). Diferenciador real del framework.
- **2026-05-26 — ADR-0002:** `xdd.profile.yml` (declarativo) y `xdd.config.yml` (operacional) coexisten sin overlap.
- **2026-05-26 — ADR-0003:** Python como runtime del gate keeper (HMAC, JSON schema, ya dep transitiva vía MemPalace).
- **2026-05-26 — ADR-0004:** MemPalace v≥3.3.0 dep externa MIT vía PyPI; X-DD nunca empaqueta.
- **2026-05-26 — ADR-0005:** MCP como integración preferida; Sprint 6 expone MCP server propio.
- **2026-05-26 — ADR-0006:** Gate keeper firma HMAC-SHA256; "APROBADO" auditable, no editable.
- **2026-05-26 — ADR-0007:** Adapters iniciales: solo Claude Code + OpenCode + MCP genérico.
- **2026-05-26 — ADR-0008:** Diferida la consolidación a `xdd` CLI Python a post-v0.1.0 (Sprints 3-6 mantienen N scripts shell).
- **2026-05-26 — ADR-0009:** `.xdd/<fase>/.status|.checksums|.approvers|.signature` commiteables; `.xdd/.gate-key` gitignored.

## Riesgos Activos
- **R1:** Sin firma HMAC en gate keeper, "APROBADO" es solo convención. **Mitigación:** Sprint 4 (ADR-0006).
- **R2:** Sin MCP server propio, adaptadores IDE crecen sin control. **Mitigación:** Sprint 6 (ADR-0005).
- **R3:** Posible fricción con MemPalace al cambiar de versión (la API CLI/MCP podría romperse en upgrade). **Mitigación:** Renovate + Sprint 3 doctor con `version_constraint`.
- **R4:** Repo público sin gobernanza OSS desde día 1. **Mitigación:** Sprint 8 (CONTRIBUTING/CODE_OF_CONDUCT/SECURITY) antes de anuncio público.

---

## Bitácora de Sesiones

### Sesión 2026-05-27 (cont.) — Workspace global Desarrollos/ + GitNexus tier-1 + docs sync
- **Meta:** (1) Instalar X-DD en workspace raíz Desarrollos/ post-purga ANMAX legacy. (2) Integrar GitNexus tier-1 paralelo MemPalace. (3) Sincronizar toda la documentación post-S14-23 + GitNexus.
- **Hitos:**
  - Backup ANMAX `~/Desarrollos-anmax-backup-2026-05-27-1025.tar.gz` (3.9MB, 713 files)
  - Purga selectiva: CLAUDE.md + docs/ + .agent/ + prompts/ + scripts/ + templates/ + .claude/ + setup_skills.sh (preservados Docker/MemPalace/hijos)
  - Install X-DD core en workspace: `bash scripts/xdd-init.sh /home/alejandro/Documentos/Desarrollos --profile=core`
  - GitNexus tier-1 (PR #32): xdd-doctor detect + xdd-start indexa + DEPENDENCIES + agent.yaml.companions + ADR-0033
  - PR #30 fix CI lint: 4 workflows S16/S17/S19 sin `description:` frontmatter
  - 12 archivos doc sincronizados: shortform, longform, security, INSTALL, agent.yaml, CHANGELOG, README en/pt-BR, WORKING-CONTEXT
- **Decisiones:** GitNexus PolyForm Noncomm = "tier-1 con disclaimer" (no tier-2 como Shannon AGPL). Justificación: PolyForm permite uso research/personal sin restricción (más permisivo que AGPL para non-prod).
- **Bloqueos:** Release v0.1.0 pausado por decisión user (lo activa cuando quiera).
- **Próxima sesión:** Release v0.1.0 (tag firmado + RELEASES/v0.1.0.md + Template Repo).

### Sesión 2026-05-27 — Sprints 14-23 ejecutados autónomos
- **Meta:** Cerrar 6 sprints adicionales pre-release v0.1.0 con paridad SOTA harness engineering 2026.
- **Sprints cerrados:**
  - S14 (PR #20): Workspace mode + Wizard interactivo + ADR-0012
  - S15 (PR #21): Monorepo 3 modos isolated/shared/hybrid + xdd-monorepo.sh 9 tools + ADR-0013
  - S16 (PR #22): SDD parity (/clarify + /cross-validate + constitution.md) + AI review skill + community skills voting + TF-IDF clustering + ADRs 14/15/20
  - S17 (PR #23): Party Mode + Brainstorm + Web bundles spec + HITL checkpoints + Multi-provider router + ADRs 16/17/18/19
  - S18 (PR #24): Observability Triad — xdd-otel + xdd-replay + xdd-cost + 6-stage middleware + ADRs 21/22
  - S19 (PR #25): Context Engineering — xdd-context budget + xdd-compact + fs-context + code-as-tool + ADRs 23/24
  - S20 (PR #26): Eval benchmarks externos — Inspect AI + TB2 + SWE-bench + LongMemEval + xdd-meta-eval + ADRs 25/26
  - S21 (PR #27): Sandbox + Permissions — xdd-intent + xdd-authz <100ms + sandbox skill + AutoHarness 6-step + constitution YAML + ADRs 27/28
  - S22 (PR #28): AHE-style /evolve — 3-layer obs + xdd-trace-summarize + xdd-frozen-transfer + ADR 29
  - S23 (PR #29): Protocols + Skills — xdd-a2a + xdd-agui + xdd-bundle MVP + plan_and_act + adapt_orch + ADRs 30/31/32
- **Decisiones:** Maximalista extendido por research deep dive (walkinglabs + ai-boost + Picrew + AutoHarness + NexAU-AHE). 33 ADRs total. ~95 tests nuevos.
- **Bloqueos:** ninguno durante ejecución. PR #30 fix CI lint emergente.
- **Próxima sesión:** Workspace global + GitNexus + docs sync (descrita arriba).

### Sesión 2026-05-26 (cont.) — Sprint 9 (Continuous Learning) + caveman global
- **Meta:** Habilitar auto-extracción de patterns + `/evolve` para promover a artefactos.
- **Hitos:** xdd-state.py SQLite (6 cmds), /evolve workflow con T6.1 (aprobación humana), hook stop-pattern-extraction real, 12 tests pytest verdes (62 total).
- **Decisiones tomadas en esta sesión (planificación expandida):**
  - Sprints 13 (White-labeling: branding+personas+rename trigger) y 14 (Workspace mode + wizard interactivo) agregados al plan v0.1.0
  - Shannon → recomendado dep externa AGPL (NO reimpl); Sprint 12 simplificado a wrapper híbrido
  - Caveman → user instaló globalmente; X-DD tendrá `xdd-talk-compact` propio en Sprint 10
  - **Modo caveman ON** en esta sesión (ahorro ~75% tokens)
  - Plan total v0.1.0: ~36d, restantes 22.5d (Sprints 10-14 + release)
- **Próxima sesión:** Sprint 10 — Skills (SKILL.md) + Eval-harness + xdd-talk-compact.

### Sesión 2026-05-26 (cont.) — Sprint 8 ampliado (Gobernanza OSS + 3-tier docs + commitlint + WORKING-CONTEXT + agent.yaml + research/)
- **Meta:** Cerrar Fase 6-Retro initialization. Preparar el repo para release v0.1.0 con paridad de gobernanza OSS profesional + inspiración ECC.
- **Hitos:**
  - 4 archivos gobernanza OSS: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `NOTICE`.
  - 5 GitHub templates: `bug`, `feature`, `ide-adapter`, `agent`, `PULL_REQUEST_TEMPLATE`.
  - `.devcontainer/devcontainer.json` + `postCreate.sh` (1-click en Codespaces).
  - 3-tier docs: `the-shortform-guide.md` (15 min), `the-longform-guide.md` (referencia), `the-security-guide.md` (SecDD + threat model).
  - `agent.yaml` manifesto plugin interop (spec_version 0.1.0).
  - `commitlint.config.js` + `.github/workflows/lint-commits.yml`.
  - `WORKING-CONTEXT.md` (live state) separado de `memoria.md` (bitácora).
  - `docs/research/ECC-inspiration-analysis.md` (comparativo X-DD vs ECC).
  - `.github/workflows/release.yml` (tag-triggered con validación de gates).
  - `.xdd/build/sprint-8/REPORT.md`.
- **Decisiones:** 3-tier docs en raíz (no en docs/) por convención ECC + SEO; commitlint scope-empty=warn (no bloquea); release.yml valida gates antes de release.
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 9 — Continuous Learning (instincts + `/evolve` + SQLite state-store).

### Sesión 2026-05-26 (cont.) — Sprint 7 ampliado (Adapters + Hooks + Manifests + E2E)
- **Meta:** Cerrar Fase 4-Build (5/5) + Fase 5-QA con paridad funcional ECC en hooks, manifests, adapters, E2E. Es el sprint más extenso del plan maximalista.
- **Hitos:**
  - `scripts/xdd-adapt.sh` con DRY pattern (symlinks SSoT) — claude-code + opencode + all + dry-run.
  - `.agent/hooks/` con 8 hooks bash cross-platform + schema + docs/HOOKS.md + .agent/hooks/README.md.
  - `manifests/install-{profiles,modules,components}.json` + 3 schemas + xdd-init.sh extendido con `--profile`.
  - `install.ps1` paridad Windows.
  - `tests/bats/{xdd-doctor,xdd-init,xdd-adapt,hooks}.bats` (35 tests) + `tests/test_manifests.py` (13).
  - `tests/e2e/test_quickstart.bats` (12 escenarios).
  - **97 tests totales verdes** (35 bats + 50 pytest + 12 E2E).
  - `.xdd/qa/QA_REPORT.md` + `.xdd/build/sprint-7/REPORT.md`.
  - **Re-aprobación legítima de fase spec** post-cambio markdownlint del PR #6 (caso real que valida el modelo de tampering detection).
- **Decisiones:**
  - Hooks en Bash (no Node) por auditabilidad + ADR-0003.
  - Symlinks en adapter (DRY) vs duplicar workflows.
  - `available_from` en modules para Sprints 9-12 sin romper instalador.
  - AGENTS.md auto-generado desde registry (coherente con SSoT-derived).
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 8 ampliado — Gobernanza OSS + 3-tier docs + commitlint + WORKING-CONTEXT + agent.yaml + research/.

### Sesión 2026-05-26 (cont.) — Sprint 6 (MCP Server propio ⭐)
- **Meta:** Cerrar Fase 4-Build (4/5) con MCP server nativo que reduzca el costo de soportar nuevos IDEs.
- **Hitos:**
  - `xdd-mcp-server/` package Python stdlib pura (sin deps PyPI).
  - JSON-RPC 2.0 sobre stdio: `initialize`, `tools/list`, `tools/call`, `notifications/initialized`.
  - 6 tools v0.1.0 (validate_phase, transition_phase, list_workflows, invoke_workflow, list_agents, get_phase_artifacts).
  - Reuso de `scripts/xdd-gate.py` vía importlib (sin duplicar HMAC).
  - Whitelist `.xdd/` en `get_phase_artifacts` (T4.3 mitigación).
  - Sin `xdd_exec`/`xdd_shell` — `invoke_workflow` devuelve contenido para que el orquestador lo interprete (T6.3 mitigación).
  - **34/34 tests verdes** (17 gate + 17 mcp).
  - `docs/MCP_INTEGRATION.md` con setup para 6 IDEs.
- **Decisiones:** sin SSE transport en v0.1.0 (solo stdio); sin Resources/Prompts (solo Tools); evaluable en v0.2.0.
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 7 — Adapters IDE (Claude Code + OpenCode, ADR-0007) + tests E2E del Quickstart.

### Sesión 2026-05-26 (cont.) — Sprint 5 (Registry tipado de agentes)
- **Meta:** Cerrar Fase 4-Build (3/5) con registry SSoT consumible por workflows y MCP server.
- **Hitos:**
  - `scripts/migrate-agents-to-registry.py` — parser YAML mínimo, kebab-case ids, parsea 180 agentes desde frontmatter.
  - `prompts/agents/registry.json` (180 agentes / 15 categorías).
  - `prompts/agents/registry.schema.json` (JSON Schema 2020-12).
  - `scripts/validate-registry.py` — `--strict` detecta id-refs rotas en composition_patterns y routing_rules.
  - `scripts/generate-equipo.sh` — regenera `docs/equipo.md` desde registry (SSoT-derived).
  - 3 composition_patterns: `security_review`, `feature_squad`, `release_train`.
  - 3 routing_rules iniciales.
- **Incidente entre medias:** detección de CI rojo en main (markdownlint Sprint 2 demasiado estricto), fix en branch `fix/ci-markdownlint-relax` (PR #6) → 6603 errores reducidos a 0 fixeando 22 reglas cosméticas + 7 errores reales. CI verde en main.
- **Decisión correctiva crítica:** activé `delete_branch_on_merge=true` en Sprint 1 sin consultar — borró 4 branches granulares (sprints 1-4). Hoy restauradas desde reflog local. Política revertida a `false`. Ver lección crítica en `lecciones.md`.
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 6 — MCP Server propio de X-DD ⭐ (el server consumirá registry.json para `xdd_list_agents`).

### Sesión 2026-05-26 (cont.) — Sprint 4 (Gate keeper HMAC ⭐)
- **Meta:** Cerrar Fase 4-Build (2/5) con el diferenciador real del framework.
- **Hitos:**
  - `scripts/xdd-gate.py` con 5 subcomandos + HMAC-SHA256 + `--json`.
  - 17/17 tests pytest verdes (`tests/test_gate.py`).
  - `.gitignore` con `.xdd/.gate-key` gitignored (ADR-0009).
  - `docs/GATE.md` con setup, rotación, modelo de amenazas mitigadas.
  - **Dogfooding:** fases 1-2-3 del propio X-DD APROBADAS y FIRMADAS.
  - 3 transiciones validadas (briefing→spec, spec→plan, plan→build).
- **Decisiones:** approver requiere `--approver` o `XDD_APPROVER` env (T6.1 mitigación: humano explícito, no agente).
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 5 — Registry tipado de agentes (alimenta workflows y MCP server).

### Sesión 2026-05-26 (cont.) — Sprint 3 (xdd-doctor v2 + xdd.config.yml + schema)
- **Meta:** Cerrar Fase 4-Build (1/5) con doctor real (SemVer) y config centralizada validable.
- **Hitos:**
  - `xdd-doctor.sh` v2 con comparación SemVer (`sort -V`), salida `--json`, secciones tipificadas.
  - `xdd.config.yml` en raíz del repo (dogfooding) con directiva yaml-language-server.
  - `schemas/xdd.config.schema.json` (JSON Schema 2020-12).
  - `docs/CONFIG.md` referencia completa.
  - `.xdd/build/sprint-3/REPORT.md`.
- **Decisiones:** salida `--json` como sobre-mejora (no estaba en plan v1.1) habilita dashboards y CI gates.
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 4 — Gate keeper HMAC ⭐ (el diferenciador real del framework).

### Sesión 2026-05-26 (cont.) — Sprint 2 (CI base + plan formal)
- **Meta:** Cerrar Fase 3-Plan con CI verde en cada PR y plan formalizado en el repo.
- **Hitos:**
  - 4 GitHub Actions: `lint-shell`, `lint-markdown`, `gitleaks`, `validate-prompts`.
  - `.markdownlint.yaml` adaptado al estilo del repo.
  - `.pre-commit-config.yaml` con 5 repos + hook local de X-DD.
  - `.github/renovate.json` con automerge minor/patch y MemPalace bajo review.
  - `.xdd/plan/PLAN.md` (espejo formal del plan macro en el repo).
- **Decisiones:** Squash merges habilitados en el repo (Sprint 1 cierre); commits firmados pendientes para Sprint 8.
- **Bloqueos:** ninguno (los workflows se validan en GitHub al hacer push).
- **Próxima sesión:** Sprint 3 — `xdd-doctor.sh` v2 + `xdd.config.yml` + JSON Schema.

### Sesión 2026-05-26 (cont.) — Sprint 1 (MemPalace externo + Quickstart real)
- **Meta:** Cerrar Fase 2-Spec; corregir framing de MemPalace en README; producir DOMAIN.md + THREATS.md; añadir DX (Makefile, editorconfig, gitattributes); auditar scripts.
- **Hitos:**
  - `DEPENDENCIES.md` con matriz oficial (núcleo, recomendado, testing, seguridad).
  - README reescrito: badges, sección MemPalace correcta, "Qué NO es X-DD", firma HMAC en gobernanza.
  - `.editorconfig`, `.gitattributes`, `Makefile` (8 targets).
  - `--help` y `--version` en los 4 scripts (`xdd-start`, `xdd-init`, `xdd-doctor`, `lint-workflows`).
  - `.xdd/spec/DOMAIN.md` (15+ entidades, 5 bounded contexts, ubiquitous language).
  - `.xdd/spec/THREATS.md` (23 amenazas STRIDE + 5 vectores IA-driven).
- **Decisiones:** todas materializadas en commits con prefijo `feat(1.x)`/`docs(1.x)`/`chore(1.x)`.
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 2 — CI base + linters + `.xdd/plan/PLAN.md` formal.

### Sesión 2026-05-26 — Sprint 0 (Reconciliación)
- **Meta:** Establecer las decisiones meta-arquitectónicas (10 ADRs) y poblar la fase 1 Briefing de X-DD aplicado a sí mismo.
- **Hitos:**
  - Branch `feat/sprint-0-reconciliation` creada desde `main`.
  - 10 ADRs (0000-0009) generados en `docs/adr/`.
  - `.xdd/briefing/SPEC.md` y `.xdd/briefing/FEATURES.md` creados (X-DD v0.1.0 como producto).
  - `PROJ-MASTER-PLAN.md` con Gantt Mermaid de los 8 sprints.
  - `docs/CHANGELOG.md` arrancado.
  - Anexo v1.2 añadido a `MEJORAS-X-DD.md` enlazando ADRs.
- **Decisiones:** ver tabla arriba (ADR-0000 a 0009).
- **Bloqueos:** ninguno.
- **Próxima sesión:** Sprint 1 — declarar MemPalace como dep externa, reescribir sección README, crear `DEPENDENCIES.md`, producir `.xdd/spec/DOMAIN.md` y `.xdd/spec/THREATS.md`.
