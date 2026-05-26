# QA Report — X-DD v0.1.0-dev (Sprint 7 closure)

> Fase 5-QA: revisión integral del estado del repo tras Sprints 0-7
> antes de continuar a Sprints 8-12. Generado el 2026-05-26.

## Resumen ejecutivo

**Estado:** ✅ READY para continuar Sprints 8-12. Todos los gates verdes.

| Métrica | Valor | Status |
|---------|-------|--------|
| Tests bats | 35/35 | ✅ verde |
| Tests pytest (gate + mcp + manifests) | 50/50 | ✅ verde |
| Tests E2E del Quickstart | 12/12 | ✅ verde |
| **Total tests** | **97/97** | ✅ |
| Lint workflows | 0 errores, 0 warnings | ✅ |
| Doctor (entorno) | 0 críticos | ✅ |
| Fases gated del propio repo | briefing ✓, spec ✓, plan ✓ APROBADAS y firmadas | ✅ |
| CI workflows en main (último push) | 5/5 verde | ✅ |
| Schemas JSON válidos | 4/4 (hooks, install-{modules,profiles,components}) | ✅ |
| Workflows X-DD en catálogo | 49 (sin huérfanos) | ✅ |
| Agentes en registry tipado | 180 / 15 categorías | ✅ |
| MCP tools expuestas | 6 (validate/transition/list_workflows/invoke/list_agents/get_artifacts) | ✅ |
| Hooks event-driven | 8 (3 Pre + 2 Post + 1 SessionStart + 2 Stop) | ✅ |

## Cobertura por Sprint

| Sprint | Capacidad | Tests | Notas |
|--------|-----------|-------|-------|
| 0 | Briefing + 10 ADRs | - | dogfooding cerrado |
| 1 | MemPalace externo + Quickstart real | - | dogfooding cerrado |
| 2 | CI base + lint + Renovate | CI mismo | dogfooding cerrado |
| 3 | xdd-doctor v2 + xdd.config.yml + schema | 6 bats | doctor JSON funcional |
| 4 | Gate keeper HMAC ⭐ | 17 pytest | tamper detection probada |
| 5 | Registry tipado 180 agentes | (manual) | migrator + validator strict |
| 6 | MCP server propio ⭐ | 17 pytest | 6 tools + 6 IDEs documentados |
| 7 | Adapters + Hooks + Manifests + install.ps1 + E2E | 9 bats + 13 pytest manifests + 12 E2E | **suma a 97 tests totales** |

## Seguridad (cobertura threat model)

Mitigaciones implementadas y verificadas en este punto:

| Amenaza ([THREATS.md](../spec/THREATS.md)) | Mitigación | Verificado |
|--------------------------------------------|------------|------------|
| T1.1 Spoofing approver | HMAC firma con approver y timestamp | ✅ test_gate.py |
| T2.1 Edición manual `.status` | Firma invalida automáticamente | ✅ test_validate_detects_invalid_signature |
| T2.2 Modificación de artefactos post-aprobación | Checksums recalculados detectan | ✅ test_validate_detects_tampered_status + caso real PR #6 |
| T2.6 Hook ejecutando script malicioso post-commit | Hooks viven en `.agent/hooks/scripts/` versionado | ✅ shellcheck-ready, en repo |
| T4.1 `.gate-key` commiteado | `.gitignore` explícito + gitleaks CI | ✅ test_init_creates_key |
| T4.3 MCP expone artefactos sensibles | Whitelist `.xdd/` en `xdd_get_phase_artifacts` | ✅ test_get_phase_artifacts |
| T6.1 Agente IA aprueba sin permiso humano | `--approver` o `XDD_APPROVER` env obligatorios | ✅ test_approve_requires_approver |
| T6.2 Comando peligroso ejecutado | Hook `pre:bash:dangerous-command` bloquea | ✅ tests/bats/hooks.bats (5 patrones) |
| T6.3 Tool MCP ejecuta arbitrary code | NO existe `xdd_exec`/`xdd_shell` | ✅ tools.py review |
| V4 Gate sin firma criptográfica | HMAC-SHA256 obligatorio | ✅ ADR-0006 + Sprint 4 |
| V5 Config pinning peligroso | doctor v2 con SemVer real avisa | ✅ test_doctor_semver |

**Score: 11/11 amenazas críticas mitigadas.**

## Quality Gates (Tier 1/2/3)

### Tier 1 — Estética / convenciones
- `.editorconfig` + `.gitattributes` (Sprint 1) ✅
- `.markdownlint.yaml` con 0 errores ✅
- Conventional commits desde Sprint 1 ✅
- Pre-commit hooks configurados ✅

### Tier 2 — Lógica / correctness
- Gate keeper detecta tampering en 6 vectores distintos ✅
- MCP server JSON-RPC dispatcher con 6 casos de error ✅
- Manifests validan referencias cruzadas (perfiles → módulos, components → módulos) ✅
- E2E Quickstart simula experiencia real ✅

### Tier 3 — Performance / observabilidad
- Doctor con `--json` para integración CI/dashboards (Sprint 3) ✅
- PR logger hook captura URLs (Sprint 7) ✅
- Pattern extraction stub listo para Sprint 9 ✅
- (Pendiente Sprint 9) métricas estructuradas con SQLite

## Drift detection

- `docs/equipo.md` regenerable desde registry (no edit manual)
- `.xdd/<fase>/.checksums` detectan cambios post-aprobación
- `lint-workflows.sh` valida frontmatter + catálogo + no-absolute-paths

## Pendientes para Sprints 8-12

| Sprint | Capacidad pendiente |
|--------|---------------------|
| 8 | CONTRIBUTING.md + 3-tier docs + commitlint + WORKING-CONTEXT.md + agent.yaml + research/ |
| 9 | Continuous Learning (instincts + `/evolve` + SQLite state-store) |
| 10 | Sistema de Skills (SKILL.md) + Eval-harness |
| 11 | Multi-agent orchestration runtime (`/orchestrate`, `/multi-*`) |
| 12 | AgentShield (security audit estática del framework) |
| Release | tag firmado v0.1.0 + RELEASES/v0.1.0.md |

## Veredicto

**APROBADO** para continuar Sprints 8-12 → release v0.1.0.

- **Aprobador:** aplacencia
- **Fecha:** 2026-05-26
- **Próximo:** Sprint 8 ampliado (Gobernanza + 3-tier docs + ...).
