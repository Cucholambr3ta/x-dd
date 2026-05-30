# Sprint 8 — Build Report (Gobernanza OSS + 3-tier docs + commitlint + agent.yaml + research)

> Fase 6-Retro initialization. Prepara el repo para release v0.1.0.

## Tareas MEJORAS abordadas
- **8.1** — Archivos de gobernanza OSS
- **9.1** — Versionado + release workflow
- **Sobre-mejoras de inspiración ECC** (plan v1.2):
  - 3-tier docs (shortform / longform / security)
  - commitlint enforced
  - WORKING-CONTEXT.md vs memoria.md separados
  - agent.yaml manifesto plugin
  - docs/research/ con análisis de inspiración

## Entregables

### Gobernanza OSS
- `CONTRIBUTING.md` — guía completa para contribuidores
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `SECURITY.md` — política de divulgación, hardening, modelo de amenazas
- `NOTICE` — atribuciones a ECC, MemPalace, Anthropic, etc.
- `.github/ISSUE_TEMPLATE/{bug,feature,ide-adapter,agent}.md` (4 templates)
- `.github/PULL_REQUEST_TEMPLATE.md` con checklist X-DD obligatorio

### Devcontainer / Codespace 1-click
- `.devcontainer/devcontainer.json` (Python 3.12 + Node 20 + gh + Docker-in-Docker)
- `.devcontainer/postCreate.sh` (bats, pytest, jsonschema, pyyaml, pre-commit, MemPalace opcional)

### 3-tier docs (inspiración ECC)
- `the-shortform-guide.md` — 15 min, Quickstart visual
- `the-longform-guide.md` — referencia exhaustiva por feature
- `the-security-guide.md` — modelo de amenazas + SecDD + hardening

### Manifesto plugin interop
- `agent.yaml` — descriptor X-DD para futuro plugin marketplace
  (workflows, agents, MCP, hooks, gate keeper, config, install, dependencies, dogfooding, testing, docs)

### Commitlint enforced
- `commitlint.config.js` — conventional commits + scope, integrado con CONTRIBUTING.md
- `.github/workflows/lint-commits.yml` — valida commits del PR en CI

### Live state (separación clara vs memoria)
- `WORKING-CONTEXT.md` — estado live del sprint actual (sobreescribible)
- `memoria.md` se mantiene como bitácora inmutable (sesiones acumulativas)

### Research
- `docs/research/ECC-inspiration-analysis.md` — análisis comparativo X-DD vs ECC:
  qué se tomó como inspiración, qué se descartó, qué X-DD tiene que ECC no,
  filosofías comparadas

### Release infrastructure
- `.github/workflows/release.yml` — tag-triggered release con validación de
  gates (las 6 fases deben estar APROBADAS) + extracción de notas del CHANGELOG

## Decisiones técnicas

1. **3-tier docs en raíz** (no en docs/) — convención ECC, mejor SEO + descubrimiento
2. **agent.yaml en raíz** (no en .agent/) — convención ECC para discovery por plugin systems
3. **WORKING-CONTEXT.md como live state** — separado de memoria.md (bitácora)
4. **commitlint level 1 para scope-empty** — warn, no bloquea (flexible para commits puntuales)
5. **devcontainer con MemPalace opcional** — no falla si pip install falla
6. **release.yml valida gates antes de release** — paridad con la disciplina X-DD

## Cobertura del plan v1.2

| Tarea v1.2 | Estado |
|------------|--------|
| Gobernanza OSS (CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/NOTICE) | ✅ |
| Issue/PR templates | ✅ |
| devcontainer.json | ✅ |
| Template Repository (config GitHub) | (acción manual del owner) |
| Release workflow | ✅ |
| 3-tier docs | ✅ |
| commitlint | ✅ |
| WORKING-CONTEXT.md vs memoria.md | ✅ |
| agent.yaml | ✅ |
| docs/research/ con análisis ECC | ✅ |
| .xdd/retro/lecciones.md consolidado | (post-Sprint 12, justo antes del release) |
| `/release-cut` → v0.1.0 | (post-Sprint 12) |

## Próximo paso
**Sprint 9** — Continuous Learning (instincts + `/evolve` + SQLite state-store).
