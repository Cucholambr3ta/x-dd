# The Longform Guide to X-DD

> Referencia exhaustiva por feature. Para quickstart visual:
> [`the-shortform-guide.md`](the-shortform-guide.md). Para seguridad:
> [`the-security-guide.md`](the-security-guide.md).

## Índice

1. [Arquitectura conceptual](#1-arquitectura-conceptual)
2. [Las 6 fases en detalle](#2-las-6-fases-en-detalle)
3. [Gate keeper firmado HMAC-SHA256](#3-gate-keeper-firmado-hmac-sha256)
4. [Registry tipado de agentes](#4-registry-tipado-de-agentes)
5. [MCP server propio](#5-mcp-server-propio)
6. [Hook system event-driven](#6-hook-system-event-driven)
7. [Manifest-driven install](#7-manifest-driven-install)
8. [IDE adapters](#8-ide-adapters)
9. [Trazabilidad y dogfooding](#9-trazabilidad-y-dogfooding)
10. [Configuración (profile + config)](#10-configuración-profile--config)
11. [Testing del propio framework](#11-testing-del-propio-framework)
12. [Roadmap post-v0.1.0](#12-roadmap-post-v010)

---

## 1. Arquitectura conceptual

### Bounded Contexts

X-DD modela su propio dominio (DDD aplicado al framework, ver
[`.xdd/spec/DOMAIN.md`](.xdd/spec/DOMAIN.md)):

```
[Pipeline Core] — Pipeline, Phase, Gate, Approval
[Authoring]     — Workflow, Agent, CompositionPattern
[Configuration] — Profile, Config, Capability
[Integration]   — Adapter, MCPTool, Orchestrator
[Persistence]   — MemPalaceWing, Lesson, ADR, Artifact
```

### Reglas invariantes

1. Una pasada del Pipeline = una `PipelineRun`. No hay re-ejecución parcial.
2. `Phase.gate.status == APROBADO` es precondición de la siguiente fase.
3. `Phase.gate.signature` debe verificarse contra la `.gate-key` actual.
4. Cada `Workflow` declara `precondition` y `postcondition` con `xdd-gate.py`.
5. Cada `Agent` está catalogado en el `registry.json`.
6. Toda decisión arquitectónica produce un `ADR` antes de implementarse.
7. `Profile` es declarativo; `Config` es operacional — sin overlap (ADR-0002).

## 2. Las 6 fases en detalle

### Fase 1 — Briefing
- Workflows: `/fase-requisitos`
- Artefactos: `SPEC.md`, `FEATURES.md`, `.feature` stubs (BDD)
- Metodologías: FDD (catálogo de features), BDD (Gherkin), ATDD (stubs)

### Fase 2 — Spec
- Workflows: `/project-architecture-gsd`
- Artefactos: `DOMAIN.md` (DDD), `THREATS.md` (STRIDE)
- Metodologías: DDD + Threat Modeling

### Fase 3 — Plan
- Workflows: `/plan-fases`
- Artefactos: `PLAN.md` organizado por features verticales (FDD)

### Fase 4 — Build
- Workflows: `/xdd-build`
- Artefactos: `src/`, `tests/`
- Metodologías: TDD (Rojo→Verde→Refactor) + STDD (security tests primero)

### Fase 5 — QA
- Workflows: `/qa-review`
- Artefactos: `QA_REPORT.md` con 3 tiers (estética, lógica, performance)
- Metodologías: BDD ejecutable + ATDD + SAST + DAST + Secrets scanning

### Fase 6 — Retro
- Workflows: `/cierre-fase`, `/release-cut`
- Artefactos: `lecciones.md`, `RELEASES/vX.Y.Z.md`

## 3. Gate keeper firmado HMAC-SHA256

### Por qué firma

Sin HMAC, `"APROBADO"` escrito en un archivo es trivialmente editable. Eso anula
el valor del gate. ADR-0006 documenta la decisión.

### Setup

```bash
python3 scripts/xdd-gate.py init   # genera .xdd/.gate-key (256-bit, gitignored)
```

### Uso típico

```bash
export XDD_APPROVER="aplacencia"

# Aprobar fase
python3 scripts/xdd-gate.py approve --phase briefing
# → ✓ APROBADO, firma cffaf210...

# Validar
python3 scripts/xdd-gate.py validate --phase briefing
# → ✓ firma válida

# Status global
python3 scripts/xdd-gate.py status --json
```

### Qué pasa si alguien edita un artefacto post-aprobación

El `.checksums` capturado al aprobar ya no coincide:
```bash
echo "tampered" >> .xdd/briefing/SPEC.md
python3 scripts/xdd-gate.py validate --phase briefing
# → ✗ Checksum mismatch en .xdd/briefing/SPEC.md
```

Si el cambio es **legítimo** (lint fix, refactor menor): re-aprobar con
`xdd-gate.py approve --phase briefing`. El audit trail queda en `.approvers`.

Si es **alteración no autorizada**: revertir y discutir.

Detalles en [`docs/GATE.md`](docs/GATE.md).

## 4. Registry tipado de agentes

180 agentes en 15 categorías. SSoT: `prompts/agents/registry.json`.

### Estructura por agente

```json
{
  "id": "engineering-backend-architect",
  "name": "Backend Architect",
  "category": "engineering",
  "description": "...",
  "emoji": "🏗️",
  "color": "blue",
  "prompt_file": "prompts/agents/engineering/engineering-backend-architect.md",
  "ide_compat": ["claude-code", "opencode", "mcp"],
  "skills": [],
  "constraints": [],
  "triggers": [],
  "fallback_agent": null
}
```

### Composition patterns (lead + specialists)

```json
{
  "name": "security_review",
  "lead": "engineering-code-reviewer",
  "specialists": ["engineering-security-engineer", "engineering-threat-detection-engineer"],
  "orchestration": "sequential",
  "gate_between": "peer_review"
}
```

### Añadir un agente

1. Crear `.md` en `prompts/agents/<cat>/<cat>-mi-agente.md` con frontmatter.
2. `python3 scripts/migrate-agents-to-registry.py`
3. `python3 scripts/validate-registry.py --strict`
4. `bash scripts/generate-equipo.sh` (regenera `docs/equipo.md`)

## 5. MCP server propio

`xdd-mcp-server/` (Python stdlib pura) expone 6 tools vía JSON-RPC stdio:

| Tool | Qué hace |
|------|----------|
| `xdd_validate_phase` | Valida fase + firma HMAC |
| `xdd_transition_phase` | Valida transición secuencial |
| `xdd_list_workflows` | Catálogo de workflows |
| `xdd_invoke_workflow` | Devuelve contenido del workflow (NO ejecuta) |
| `xdd_list_agents` | Registry (filtrable por categoría) |
| `xdd_get_phase_artifacts` | Whitelist `.xdd/` |

Setup por IDE en [`docs/MCP_INTEGRATION.md`](docs/MCP_INTEGRATION.md).

## 6. Hook system event-driven

8 hooks en `.agent/hooks/scripts/`. Definidos en `.agent/hooks/hooks.json`.
Profiles: `minimal | standard | strict`.

### Activación

```bash
export XDD_HOOK_PROFILE=strict
# Disable selectivo:
export XDD_DISABLED_HOOKS="pre:bash:dangerous-command,stop:git-check"
```

### Crear un hook propio

1. Bash script en `.agent/hooks/scripts/`.
2. Entrada JSON en `.agent/hooks/hooks.json`.
3. Validar: `python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('.agent/hooks/hooks.json')), json.load(open('schemas/hooks.schema.json')))"`.
4. Test bats.

Detalles en [`docs/HOOKS.md`](docs/HOOKS.md) y [`.agent/hooks/README.md`](.agent/hooks/README.md).

## 7. Manifest-driven install

### Profiles

| Profile | Modules | Para qué |
|---------|---------|----------|
| `minimal` | core + workflows + memory | Probar X-DD sin compromiso |
| `core` | + agents + gate + ci | Recomendado para empezar |
| `developer` | + hooks + MCP + IDE adapters | Dev activo con IA |
| `security` | + AgentShield (Sprint 12) | SecDD focus |
| `research` | + eval-harness (Sprint 10) + instincts (Sprint 9) | Investigación |
| `full` | todo | Adopción completa |

### Componentes finos

`manifests/install-components.json` permite cherry-pick a nivel individual
(ej. solo `gate` + `mcp` + `hooks-context-load`).

Detalles en [`docs/INSTALL_PROFILES.md`](docs/INSTALL_PROFILES.md).

## 8. IDE adapters

### Soportados v0.1.0 (ADR-0007)

| Mecanismo | IDEs |
|-----------|------|
| Adapter dedicado (`xdd-adapt.sh`) | Claude Code, OpenCode |
| MCP server nativo | Cursor, Continue, Zed, Cline, Windsurf |

### Adapter pattern DRY

`xdd-adapt.sh` enlaza workflows como symlinks (no duplica). El SSoT vive
en `.agent/workflows/`; cada IDE lee desde su path estándar (`.claude/commands/`
para Claude Code, `AGENTS.md` para OpenCode).

## 9. Trazabilidad y dogfooding

ADR-0001 establece **dogfooding visible**: X-DD se aplica a sí mismo en público.

| Artefacto | Qué muestra |
|-----------|-------------|
| `.xdd/briefing/{SPEC,FEATURES}.md` | X-DD v0.1.0 como producto |
| `.xdd/spec/{DOMAIN,THREATS}.md` | Modelo del propio framework |
| `.xdd/plan/PLAN.md` | Plan macro espejo |
| `.xdd/build/sprint-N/REPORT.md` | Sub-reporte por sprint |
| `.xdd/qa/QA_REPORT.md` | Tiers de calidad verificados |
| `.xdd/retro/lecciones.md` | Aprendizajes acumulados (Sprint 8 cierra) |
| `.xdd/<phase>/.signature` | HMAC firmadas |
| `docs/adr/` | 10 ADRs Nygard |
| `PROJ-MASTER-PLAN.md` | Gantt Mermaid de sprints |
| `docs/CHANGELOG.md` | Historia técnica |
| `RELEASES/` | Release notes user-facing |
| `memoria.md` | Bitácora de sesiones |
| `lecciones.md` | Lecciones manuales |
| `WORKING-CONTEXT.md` | Estado live del sprint actual |

## 10. Configuración (profile + config)

ADR-0002 separa **declarativo** vs **operacional**:

| Archivo | Tipo | Cambia |
|---------|------|--------|
| `xdd.profile.yml` | Declarativo | Raramente (cambio de profile) |
| `xdd.config.yml` | Operacional | Con cada bump (MemPalace versión, paths, triggers) |

Validables contra `schemas/xdd.config.schema.json`. Directiva `# yaml-language-server`
para autocompletado en IDEs modernos.

Detalles en [`docs/CONFIG.md`](docs/CONFIG.md).

## 11. Testing del propio framework

### Por capa

| Capa | Suite | Count |
|------|-------|-------|
| Scripts shell | `tests/bats/` | 35 |
| Gate keeper (Python) | `tests/test_gate.py` | 17 |
| MCP server | `tests/test_mcp_server.py` | 17 |
| Manifests | `tests/test_manifests.py` | 13 |
| Helpers/utils | `tests/test_*.py` | 3 |
| E2E Quickstart | `tests/e2e/test_quickstart.bats` | 12 |
| **Total** | | **97** |

### Correr

```bash
make test    # lint + doctor
bats tests/bats/
python3 -m pytest tests/ -q
bats tests/e2e/test_quickstart.bats
```

## 12. Roadmap post-v0.1.0

### Sprints completados en v0.1.0 (estado post-S13)

| Sprint | Capacidad | PR | Estado |
|--------|-----------|----|----|
| 0 | Reconciliación + 10 ADRs | #1 | ✅ |
| 1 | MemPalace externo + Quickstart | #2 | ✅ |
| 2 | CI base + plan formal | #3 | ✅ |
| 3 | xdd-doctor v2 + xdd.config.yml | #4 | ✅ |
| 4 | Gate keeper HMAC ⭐ | #5 | ✅ |
| 5 | Registry tipado de 180 agentes | #7 | ✅ |
| 6 | MCP Server propio ⭐ | #8 | ✅ |
| 7 | Adapters + 8 hooks + Manifests + install.ps1 | #9 | ✅ |
| 8 | Gobernanza OSS + 3-tier docs + commitlint + agent.yaml | #10 | ✅ |
| 9 | Continuous Learning (instincts + `/evolve` + SQLite) | #11 | ✅ |
| 10 | Skills + Eval-harness + xdd-talk-compact (compresión tokens propia) | #12 | ✅ |
| 11 | Multi-agent orchestration runtime (`/orchestrate`) | #13 | ✅ |
| 12 | AgentShield + Shannon dep AGPL híbrida + rename + ADR-0010 | #14 | ✅ |
| 13 | White-labeling + 4 personas + ADR-0011 | #15 | ✅ |
| 14 | Workspace mode + Wizard interactivo + ADR-0012 | #20 | ✅ |
| 15 | Monorepo 3 modos (isolated/shared/hybrid) + ADR-0013 | #21 | ✅ |
| 16 | SDD parity (`/clarify` + `/cross-validate` + constitution.md) + AI review + community skills voting + TF-IDF clustering + ADRs 14/15/20 | #22 | ✅ |
| 17 | Party Mode + Brainstorm + Web bundles spec + HITL checkpoints + Multi-provider router + ADRs 16/17/18/19 | #23 | ✅ |
| 18 | Observability Triad — OTel Gen AI spans + session replay + per-call cost + 6-stage middleware + ADRs 21/22 | #24 | ✅ |
| 19 | Context Engineering — budget metering + compact skill + fs-context + code-as-tool + ADRs 23/24 | #25 | ✅ |
| 20 | Eval benchmarks externos — Inspect AI + Terminal-Bench 2 + SWE-bench + LongMemEval + meta-eval + ADRs 25/26 | #26 | ✅ |
| 21 | Sandbox + Permissions hardening — intent + authz <100ms + 6-step governance + constitution YAML + ADRs 27/28 | #27 | ✅ |
| 22 | AHE-style /evolve — 3-layer observability + trace summarize + frozen transfer + ADR 29 | #28 | ✅ |
| 23 | Protocols + Skills ecosystem — A2A + AG-UI + bundle.py + plan_and_act + adapt_orch + ADRs 30/31/32 | #29 | ✅ |
| Add | GitNexus tier-1 companion paralelo MemPalace + ADR-0033 | #32 | ✅ |

### Pendientes para v0.1.0

| # | Trabajo | Días |
|---|---|---|
| Release | tag firmado v0.1.0 + RELEASES/v0.1.0.md + Template Repository | ~0.5 |

### Stack MCP recomendado (3 servers paralelos)

`xdd-start.sh` activa MemPalace + GitNexus automáticamente si CLI instalados:

| MCP Server | License | Tools | Función |
|---|---|---|---|
| **xdd-mcp-server** | MIT | 6 | Pipeline X-DD: gates HMAC + workflows + agents + phase artifacts |
| **MemPalace** | MIT | 29 | Memoria semántica (ChromaDB + SQLite) |
| **GitNexus** | PolyForm Noncomm ⚠️ | 16 | Code intelligence (AST grafo 14 langs, impact analysis, hybrid search BM25+semantic+RRF) |

Sin MemPalace/GitNexus instalados → X-DD degrada con `xdd-fs-context` baseline portable (Sprint 19).

### Post-v0.1.0 (v0.2.0 hipotético)

- Crecimiento autónomo Nivel 3 (auto-aprobación con clave delegada + audit retroactivo)
- SSE/HTTP transport para MCP server (hoy stdio)
- Multi-machine collaboration con `.gate-key` compartida
- Plantillas por industria (fintech, e-commerce, SaaS B2B)
- Web bundles MVP completo CLI (ADR-0017 spec ya en Sprint 23)
- Backend-impl per-sandbox (E2B/Daytona/Microsandbox runtime real, Sprint 21 ya tiene skill spec)
- A2A HTTP server real (Sprint 23 stub)

## Referencias

- [Plan vigente](MEJORAS-X-DD.md) — task tracking
- [33 ADRs](docs/adr/) — decisiones arquitectónicas (10 + 23 post-S13)
- [Research notes](docs/research/) — ECC + awesome-harness-engineering + agents-best-practices analysis
- [docs/BRANDING.md](docs/BRANDING.md), [docs/PENTEST.md](docs/PENTEST.md), [docs/WORKSPACE.md](docs/WORKSPACE.md), [docs/MONOREPO.md](docs/MONOREPO.md)
- [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md), [docs/CONTEXT_ENGINEERING.md](docs/CONTEXT_ENGINEERING.md)
- [docs/EXTERNAL_BENCHMARKS.md](docs/EXTERNAL_BENCHMARKS.md), [docs/PERMISSIONS.md](docs/PERMISSIONS.md), [docs/SANDBOXING.md](docs/SANDBOXING.md)
- [docs/AHE_EVOLVE.md](docs/AHE_EVOLVE.md), [docs/SKILLS_INTEROP.md](docs/SKILLS_INTEROP.md)
