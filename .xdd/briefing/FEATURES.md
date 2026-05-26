# FEATURES — X-DD v0.1.0

> Catálogo FDD de features verticales para el release v0.1.0.
> Cada feature mapea a un sprint del plan macro.

## Convenciones

- **ID:** `FEAT-NN-slug`
- **Priorización:** RICE simplificado (Reach × Impact × Confidence ÷ Effort), 1-10.
- **Sprint owner:** sprint donde se construye la feature.

---

## FEAT-00 — Reconciliación arquitectónica
- **Sprint:** 0
- **RICE:** R=10 I=10 C=10 E=1 → score 100 (bloquea todo lo demás)
- **Descripción:** Generar los 10 ADRs (0000-0009) que cierran las preguntas abiertas del plan: mapeo a fases, dogfooding visible, gate firmado, MCP server propio, alcance de adapters, etc.
- **Entregables:** `docs/adr/0000-*.md`...`0009-*.md`, `.xdd/briefing/{SPEC,FEATURES}.md`, `PROJ-MASTER-PLAN.md`, `docs/CHANGELOG.md`.
- **DoD:** `/cierre-fase` ejecutado, PR merged a main.

## FEAT-01 — MemPalace declarada como dependencia externa + Quickstart real
- **Sprint:** 1
- **RICE:** R=10 I=10 C=10 E=3 → 33
- **Descripción:** Reescribir README para corregir framing de MemPalace, crear `DEPENDENCIES.md`, auditar scripts vs README, añadir `Makefile`/`.editorconfig`/badges.
- **Entregables:** `DEPENDENCIES.md`, `README.md` reescrito, `.xdd/spec/{DOMAIN,THREATS}.md`, `Makefile`, badges.
- **DoD:** clonar repo + Quickstart < 10 min sin manual.

## FEAT-02 — CI base + plan formalizado
- **Sprint:** 2
- **RICE:** R=10 I=8 C=10 E=2 → 40
- **Descripción:** GitHub Actions (shellcheck, markdownlint, gitleaks, validate-prompts), pre-commit, Renovate, branch protection.
- **Entregables:** `.github/workflows/*.yml`, `.pre-commit-config.yaml`, `.github/renovate.json`, `.xdd/plan/PLAN.md`.
- **DoD:** todos los PR muestran CI verde antes de mergear.

## FEAT-03 — `xdd-doctor.sh` v2 + `xdd.config.yml`
- **Sprint:** 3
- **RICE:** R=10 I=7 C=9 E=3 → 21
- **Descripción:** Doctor con SemVer real + `--json`, config centralizada con schema y autocomplete.
- **Entregables:** `scripts/xdd-doctor.sh` v2, `xdd.config.yml`, `schemas/xdd.config.schema.json`, `docs/CONFIG.md`, `tests/xdd-doctor.bats`.
- **DoD:** doctor pasa limpio en Ubuntu + macOS; config valida contra schema en CI.

## FEAT-04 — Gate keeper firmado (HMAC) ⭐
- **Sprint:** 4
- **RICE:** R=10 I=10 C=8 E=5 → 16 (alto valor, alto esfuerzo)
- **Descripción:** `xdd-gate.py` con validate/transition/approve + firma HMAC-SHA256. Integración en todos los workflows existentes.
- **Entregables:** `scripts/xdd-gate.py`, `tests/test_gate.py`, `.xdd/<fase>/.signature`, todos los workflows con pre/post-condition.
- **DoD:** intentar saltar fase falla; alterar artefacto invalida firma.

## FEAT-05 — Registry tipado de agentes
- **Sprint:** 5
- **RICE:** R=8 I=8 C=9 E=4 → 14.4
- **Descripción:** Migrar los 77+ agentes a `registry.json` (con migración automática), schema, validador, generador de `docs/equipo.md` desde registry, patrones de composición.
- **Entregables:** `prompts/agents/registry.json` + schema, `scripts/{migrate-agents-to-registry,validate-registry}.py`, `scripts/generate-equipo.sh`.
- **DoD:** `docs/equipo.md` regenerado automáticamente; SSoT en registry.

## FEAT-06 — MCP server propio de X-DD ⭐
- **Sprint:** 6
- **RICE:** R=10 I=10 C=7 E=5 → 14 (estratégico)
- **Descripción:** Exponer gates, fases, workflows y agentes como herramientas MCP. Reduce adaptadores IDE de 9 a 2.
- **Entregables:** `xdd-mcp-server/{server.py,pyproject.toml,tests/}`, ≥6 tools, `docs/MCP_INTEGRATION.md`.
- **DoD:** Cursor/Continue/Zed pueden conectar al server y listar tools sin adapter específico.

## FEAT-07 — Adapters IDE + tests E2E + QA del propio X-DD
- **Sprint:** 7
- **RICE:** R=8 I=9 C=8 E=4 → 14.4
- **Descripción:** `xdd-adapt.sh` para Claude Code + OpenCode, suite completa de tests (bats + pytest), E2E del Quickstart, `/qa-review` del propio repo.
- **Entregables:** `scripts/xdd-adapt.sh`, `tests/{**/*.bats,**/*.py,e2e/}`, `.xdd/qa/QA_REPORT.md`.
- **DoD:** Sprint 7 cierra con 5/6 fases de X-DD aprobadas (todas menos retro).

## FEAT-08 — Gobernanza OSS + release v0.1.0
- **Sprint:** 8
- **RICE:** R=10 I=10 C=10 E=2 → 50
- **Descripción:** Archivos de gobernanza, devcontainer, Template Repository, release workflow, tag firmado, CHANGELOG consolidado.
- **Entregables:** `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `NOTICE`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `devcontainer.json`, `RELEASES/v0.1.0.md`, `CHANGELOG.md`, tag `v0.1.0`.
- **DoD:** tag `v0.1.0` firmado en GitHub; los 6 archivos `.xdd/<fase>/.status` están en APROBADO.

---

## Orden de implementación

FEAT-00 → FEAT-01 || FEAT-02 → FEAT-03 → FEAT-04 → FEAT-05 || FEAT-06 → FEAT-07 → FEAT-08

(`||` indica que se pueden empezar en paralelo si hay capacidad.)

## Total RICE acumulado: ~302 puntos
