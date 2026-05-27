# X-DD — Cross-Driven Development System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/Cucholambr3ta/x-dd)](https://github.com/Cucholambr3ta/x-dd/commits/main)
[![ADRs](https://img.shields.io/badge/ADRs-11-blue)](docs/adr/)
[![Workflows](https://img.shields.io/badge/workflows-51-green)](.agent/workflows/)
[![Agents](https://img.shields.io/badge/agents-180-orange)](docs/equipo.md)
[![Tests](https://img.shields.io/badge/tests-160%2B%20green-brightgreen)](tests/)
[![MemPalace](https://img.shields.io/badge/MemPalace-%E2%89%A53.3.0-purple)](DEPENDENCIES.md)
[![Shannon](https://img.shields.io/badge/Shannon-optional%20AGPL--3.0-red)](docs/PENTEST.md)

**Pipeline de desarrollo de alta calidad** que integra múltiples metodologías *-Driven Development* como capas sobre un Gated Pipeline de 6 fases. Orquestable desde **cualquier asistente IA/IDE** que soporte MCP o slash commands markdown (lista completa abajo). Apoyado por agencia de 180 subagentes + 51 workflows + 8 hooks + AgentShield.

> 📌 X-DD se aplica a sí mismo: ver [.xdd/](.xdd/), [docs/adr/](docs/adr/), [PROJ-MASTER-PLAN.md](PROJ-MASTER-PLAN.md) y [docs/CHANGELOG.md](docs/CHANGELOG.md) para el dogfooding visible (ver [ADR-0001](docs/adr/0001-dogfooding-visible-commiteable.md)).

## Compatibilidad universal IDE / Asistentes IA

X-DD funciona con **cualquier orquestador agéntico** que cumpla al menos uno de estos protocolos: MCP (Model Context Protocol), slash commands markdown, o lectura de `AGENTS.md` / `CLAUDE.md`. Probado/documentado con:

| Asistente / IDE | Mecanismo | Adapter dedicado | Doc |
|---|---|---|---|
| **Claude Code** (Anthropic CLI) | slash commands `.claude/commands/` | ✅ `xdd-adapt claude-code` | [INSTALL.md](INSTALL.md) |
| **OpenCode** (multi-proveedor OSS) | `AGENTS.md` + `.agent/workflows/` | ✅ `xdd-adapt opencode` | [INSTALL.md](INSTALL.md) |
| **Cursor** | MCP server + `.cursor/rules` | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Continue.dev** (VSCode/JetBrains extension) | MCP server en `~/.continue/config.json` | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Zed AI** | MCP `context_servers` | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Cline / Roo Code** (VSCode extension) | MCP server settings | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Windsurf** (Codeium) | MCP server | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Google Antigravity** | MCP server | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **VSCode** (cualquier extensión que use MCP) | Continue/Cline/Claude Code extension | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **GitHub Copilot** | `.github/copilot-instructions.md` (limitado) | parcial | (roadmap v0.2.0) |
| **Hermes Agent** (Nous Research) | local agent, lee `prompts/agents/` | parcial (slash commands) | (ver Hermes docs) |
| **Codex** (OpenAI) / **Gemini** / **Qwen** | TOML/JSON config con MCP | vía MCP | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |
| **Cualquier IDE futuro MCP-compat** | MCP stdio | vía `xdd-mcp-server` | [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) |

**Filosofía:** ([ADR-0005](docs/adr/0005-mcp-preferido-y-server-propio.md)) X-DD expone capacidades vía MCP server propio (6 tools: `xdd_validate_phase`, `xdd_transition_phase`, `xdd_list_workflows`, `xdd_invoke_workflow`, `xdd_list_agents`, `xdd_get_phase_artifacts`). Reduce de N adapters a 1 server compartido. Adapters dedicados solo para Claude Code + OpenCode ([ADR-0007](docs/adr/0007-adapters-iniciales-claude-opencode-mcp.md)).

## Integraciones externas opcionales

| Producto | Tipo | Licencia | Rol | Doc |
|---|---|---|---|---|
| **MemPalace** ([repo](https://github.com/MemPalace/mempalace)) | Memoria semántica local | MIT | Persistencia + RAG codebase + MCP server con 29 tools | [DEPENDENCIES.md](DEPENDENCIES.md), [ADR-0004](docs/adr/0004-mempalace-dep-externa-no-fork.md) |
| **Shannon CLI** ([repo](https://github.com/KeygraphHQ/shannon)) | Pentest dinámico white-box | **AGPL-3.0** ⚠️ | Sandbox exploits + verify findings. Wrapper híbrido `xdd-pentest.sh` degrada sin él (STRIDE + source review estático funcionan) | [docs/PENTEST.md](docs/PENTEST.md), [ADR-0010](docs/adr/0010-shannon-external-dep-pentest-operator-naming.md) |
| **Caveman** ([repo](https://github.com/juliusbrussee/caveman)) | Token compression skill global | MIT | Reducción ~75% tokens output. X-DD tiene `xdd-talk-compact` propio inspirado en él | [skills/xdd-talk-compact](skills/xdd-talk-compact/SKILL.md) |

> ⚠️ **Shannon AGPL-3.0:** X-DD **NO** bundle Shannon. Instalarlo en tu equipo = uso libre. Modificarlo + redistribuir/SaaS = AGPL aplica. Tu proyecto X-DD NO se contamina por usar Shannon vía wrapper. Decisión es tuya. Ver disclaimer en `docs/PENTEST.md`.

---

## ¿Qué es X-DD?

X-DD es un ecosistema de desarrollo de software que combina las mejores metodologías en un solo pipeline coherente, sin agregar fases nuevas — cada metodología se embebe en la fase donde más aporta:

```
FASE 1 (Briefing)  ──► + FDD (catálogo de features) + BDD (Gherkin) + ATDD (stubs)
FASE 2 (Spec)      ──► + DDD (modelo de dominio)    + Threat Modeling (THREATS.md)
FASE 3 (Plan)      ──► + FDD (plan por features verticales)
FASE 4 (Build)     ──► + TDD (Rojo→Verde→Refactor)  + STDD (security tests primero)
FASE 5 (QA)        ──► + BDD ejecutable + ATDD + SAST + DAST + Secrets scanning
FASE 6 (Retro)     ──► Learning Loop → lecciones.md
```

## Metodologías integradas

| Metodología | Qué aporta |
|-------------|------------|
| **SDD** — Spec-Driven | Eje central: ningún código sin especificación aprobada |
| **FDD** — Feature-Driven | Plan por features verticales de valor, no por capas técnicas |
| **BDD** — Behavior-Driven | Escenarios Gherkin `.feature` ejecutables desde Fase 1 |
| **ATDD** — Acceptance TDD | Tests de aceptación como contrato antes de codificar |
| **DDD** — Domain-Driven | Modelo de dominio explícito (`DOMAIN.md`) con ubiquitous language |
| **TDD** — Test-Driven | Ciclo Rojo→Verde→Refactor obligatorio para lógica de negocio |
| **STDD** — Security TDD | Security tests escritos *antes* del código para funciones críticas |
| **SecDD** — Security-Driven | SAST + DAST + Secrets scanning en el pipeline QA |
| **Threat-Driven** | Modelado STRIDE sobre el dominio antes de codificar |

## Estructura del repositorio

```
x-dd/
├── CLAUDE.md                    ← Manifiesto raíz (leer primero)
├── README.md                    ← Este archivo
├── INSTALL.md                   ← Guía de instalación de herramientas
│
├── docs/
│   ├── constitucion.md          ← Ley suprema del ecosistema (9 artículos)
│   ├── equipo.md                ← Directorio de 77+ agentes especializados
│   └── X-DD_Integration_Guide.md ← Pipeline completo + todas las metodologías
│
├── .agent/
│   └── workflows/               ← 29 workflows slash commands (Claude Code / OpenCode)
│       ├── xdd.md               ← /xdd — Orquestador principal
│       ├── xdd-build.md         ← /xdd-build — Build con TDD/STDD
│       ├── qa-review.md         ← /qa-review — QA completo (3 Tiers)
│       ├── fase-requisitos.md   ← /fase-requisitos — Briefing
│       ├── security-audit.md    ← /security-audit
│       └── ...                  (25 workflows adicionales)
│
├── .claude/
│   └── settings.json            ← Hook PostToolUse: re-indexa MemPalace tras cada Write/Edit
│
├── scripts/
│   ├── xdd-start.sh             ← Arranque unificado: MemPalace + git hooks + orquestador
│   └── hooks/
│       └── post-commit          ← Git hook: re-indexa MemPalace tras cada commit
│
└── prompts/
    ├── agents/                  ← 77+ subagentes especializados (16 categorías)
    │   ├── engineering/         ← Senior dev, architect, devops, security...
    │   ├── design/              ← UX, UI, brand, accessibility...
    │   ├── security/            ← SecOps, threat detection, security engineer
    │   ├── product/             ← Product manager, researcher...
    │   ├── finance/             ← Financial analyst, FP&A, tax...
    │   └── ...                  (11 categorías más)
    ├── phases/                  ← Prompts por metodología (TDD, BDD, DDD, SecDD...)
    ├── skills/                  ← Catálogo de skills inyectables
    ├── templates/               ← Plantillas de artefactos (SPEC, DOMAIN, THREATS...)
    ├── workflows/               ← Catálogo de workflows
    └── ecosystem/               ← Estructura del ecosistema
```

## Inicio rápido

1. **Instalar herramientas** → ver [INSTALL.md](./INSTALL.md). Mínimo: Claude Code **u** OpenCode + Git + Node 20+. Recomendado: + MemPalace.
2. **Verificar entorno:**
   ```bash
   bash ./scripts/xdd-doctor.sh
   ```
3. **Bootstrap del proyecto** (copia estructura, crea `memoria.md` y `lecciones.md` desde plantillas, inicializa git):
   ```bash
   bash ./scripts/xdd-init.sh /ruta/a/mi-proyecto
   cd /ruta/a/mi-proyecto
   ```
4. **Arrancar X-DD** — indexa MemPalace, activa los git hooks y lanza el orquestador (Claude Code u OpenCode, el que esté instalado):
   ```bash
   bash ./scripts/xdd-start.sh
   ```
5. **Ejecutar `/xdd`** para arrancar el orquestador principal.

### Perfiles de instalación

| Perfil | Cuándo usarlo | Qué incluye |
|--------|---------------|-------------|
| **Core** | Empezar rápido, scripts y tools internas | Claude Code/OpenCode + Git + Node + MemPalace |
| **Standard** | Producto con tests E2E y BDD | Core + Vitest + Playwright |
| **Full (SecDD)** | Producto cliente, compliance, producción | Standard + Semgrep + Gitleaks + Trivy + ZAP + Nuclei |

`xdd-doctor.sh` te dice qué te falta para cada perfil.

### Capacidades del producto (retrofit por tipo)

X-DD incluye un retrofit de capacidades activables vía `xdd.profile.yml`. Workflows extendidos para:

| Tipo de producto | Capacidades sugeridas |
|------------------|------------------------|
| **SaaS web** | i18n, feature flags, analytics, privacy, observability, FinOps, perf-budget, a11y, end-user docs |
| **App móvil** | mobile-release, feature flags, analytics, privacy, perf-budget, observability, onboarding |
| **Librería / SDK** | api-contract, contract-test, release-cut, end-user docs, adrs, perf-budget |
| **Tool interna** | onboarding, adrs, observability (si persistente), db-migrations |

Ver [docs/RETROFIT_GUIDE.md](./docs/RETROFIT_GUIDE.md) para el detalle de los 19 workflows extendidos y 10 agentes nuevos.

## MemPalace — Memoria Semántica Local (dependencia externa)

> **MemPalace es un proyecto externo, no parte de X-DD.** Licencia MIT, distribuido vía PyPI (`pip install mempalace`). X-DD lo integra como dependencia recomendada — ver [DEPENDENCIES.md](DEPENDENCIES.md) y [ADR-0004](docs/adr/0004-mempalace-dep-externa-no-fork.md).
> - Repo oficial: https://github.com/MemPalace/mempalace
> - Sitio oficial: https://mempalaceofficial.com
> - ⚠️ Cuidado con dominios impostores (ej. `mempalace.tech` no es oficial).

MemPalace es un sistema de memoria semántica local-first: indexa el codebase, documentación, decisiones y lecciones del proyecto combinando **ChromaDB (vector store)** y **SQLite (knowledge graph temporal)**, sin enviar nada a la nube. Expone una CLI y un **MCP server con 29 tools** consumibles por cualquier cliente MCP.

### ¿Por qué es clave para el desarrollo con IA?

El mayor problema al desarrollar con agentes de IA es la **pérdida de contexto**: cuando se agotan los tokens, se cierra la sesión o se cambia de herramienta, el agente "olvida" todo lo que se discutió, decidió y construyó. MemPalace resuelve esto:

| Sin MemPalace | Con MemPalace |
|---------------|---------------|
| Cada sesión empieza desde cero | El agente retoma donde se dejó, con contexto completo |
| Hay que re-explicar decisiones técnicas en cada sesión | Las decisiones de arquitectura, dominio y seguridad están indexadas |
| El agente no conoce el historial del proyecto | El agente consulta lecciones aprendidas antes de proponer soluciones |
| Tokens desperdiciados re-cargando contexto | Contexto cargado eficientemente desde el índice semántico |
| Los errores se repiten entre sesiones | `lecciones.md` indexado evita repetir los mismos "gotchas" |

### Ventajas concretas en el desarrollo

**Continuidad entre sesiones** — Al agotar tokens o reabrir el proyecto días después, `xdd-start.sh` re-indexa y el orquestador tiene acceso inmediato al estado real del proyecto: qué se construyó, qué decisiones se tomaron, qué errores se evitaron.

**RAG sobre el codebase propio** — Los agentes pueden consultar semánticamente el código, specs y docs del proyecto. Preguntás "¿cómo manejamos la autenticación en este proyecto?" y el agente encuentra la respuesta en el código real, no en su entrenamiento genérico.

**Trazabilidad de decisiones** — Cada decisión arquitectónica, cada bounded context definido en `DOMAIN.md`, cada amenaza en `THREATS.md` queda indexada. El agente puede justificar por qué el código es como es.

**Acumulación de inteligencia** — Con cada sesión el índice crece. Un proyecto de 3 meses tiene indexadas sus lecciones, patrones y anti-patrones. El agente que llega a la sesión 50 es significativamente más útil que el de la sesión 1.

**Local-first y privado** — Todo se almacena en `~/.mempalace/` en la máquina local. El código, las decisiones y el contexto del proyecto nunca salen del equipo.

### Automatización en X-DD

MemPalace se re-indexa automáticamente en tres momentos clave, sin intervención manual:

| Momento | Mecanismo | Archivo |
|---------|-----------|---------|
| Arranque de sesión | `xdd-start.sh` ejecuta `mempalace mine` antes del orquestador | `scripts/xdd-start.sh` |
| Cada Write/Edit del agente | Hook `PostToolUse` dispara `mempalace mine` en background | `.claude/settings.json` |
| Cada `git commit` | Hook `post-commit` re-indexa en background | `scripts/hooks/post-commit` |

```
Agente edita archivo  →  PostToolUse hook  →  mempalace mine (background)
git commit            →  post-commit hook  →  mempalace mine (background)
Nueva sesión          →  xdd-start.sh      →  mempalace mine → orquestador
```

## Árbol de decisión — ¿qué metodologías usar?

| Escenario | Camino |
|-----------|--------|
| Módulo nuevo con lógica de negocio compleja | **COMPLETO**: FDD + DDD + SDD + BDD + ATDD + TDD + Threat + STDD + SecDD |
| Feature con usuario/cliente definido | **ESTÁNDAR**: FDD + SDD + ATDD + BDD + TDD + SecDD |
| Tool interna / script | **ÁGIL**: FDD + SDD + TDD |
| Bugfix > 20 líneas | **MÍNIMO**: SDD + TDD |
| Bugfix < 10 líneas | **DIRECTO**: sin pipeline (Art. 8) |

## Capacidades avanzadas (Sprints 9-13)

| Capacidad | Sprint | Doc |
|---|---|---|
| **Continuous Learning** — auto-extrae instincts a SQLite + `/evolve` propone skills/agents/commands. Aprobación humana obligatoria (T6.1) | 9 | [`scripts/xdd-state.py`](scripts/xdd-state.py), [`.agent/workflows/evolve.md`](.agent/workflows/evolve.md) |
| **Skills + Eval-harness** — sistema `skills/<name>/SKILL.md` + 5 grader types (structural/behavioral/output_match/pass_at_k/token_count_reduction) | 10 | [`skills/`](skills/), [`scripts/xdd-eval.py`](scripts/xdd-eval.py) |
| **xdd-talk-compact** — compresión output del orquestador inspirada en [caveman](https://github.com/juliusbrussee/caveman) (MIT). 3 niveles. Ahorro ~50-75% tokens manteniendo precisión técnica | 10 | [`skills/xdd-talk-compact/SKILL.md`](skills/xdd-talk-compact/SKILL.md) |
| **Multi-agent orchestration runtime** — ejecuta `composition_patterns` del registry (sequential/parallel/parallel_then_sync) | 11 | [`scripts/xdd-orchestrate.py`](scripts/xdd-orchestrate.py), [`.agent/workflows/orchestrate.md`](.agent/workflows/orchestrate.md) |
| **AgentShield** — audit estático del propio framework (13 reglas SAST). Hooks, registry, MCP tools, workflows | 12 | [`scripts/xdd-shield.py`](scripts/xdd-shield.py) |
| **Shannon integration (híbrido)** — wrapper para [Shannon CLI](https://github.com/KeygraphHQ/shannon) AGPL-3.0 (dep externa opcional). STRIDE + source review sin Shannon; dynamic fuzzing + verify con Shannon | 12 | [`scripts/xdd-pentest.sh`](scripts/xdd-pentest.sh), [`docs/PENTEST.md`](docs/PENTEST.md) |
| **White-labeling** — branding por org. ecosystem_name, custom trigger (`/xdd` → `/helios`), 4 personas presets (technical/friendly/casual/formal) + custom | 13 | [`scripts/xdd-brand.sh`](scripts/xdd-brand.sh), [`docs/BRANDING.md`](docs/BRANDING.md) |

## Qué NO es X-DD

- **No es un framework de aplicación** — no reemplaza React/Express/Django/Rails.
- **No es un test runner** — orquesta Vitest/Playwright/pytest, no los reemplaza.
- **No es MemPalace** — lo consume como dep externa MIT ([DEPENDENCIES.md](DEPENDENCIES.md)).
- **No requiere Claude Code** — funciona también con OpenCode, Cursor, Continue, Zed, Cline, Windsurf vía MCP ([ADR-0005](docs/adr/0005-mcp-preferido-y-server-propio.md), Sprint 6 del [plan v0.1.0](MEJORAS-X-DD.md)).
- **No envía datos a la nube** — todo local-first, incluida la memoria semántica.
- **No es compatible con monorepos sin adaptación** — en roadmap post-v0.1.0.

## Principios de gobernanza

- **Ambigüedad Cero** — El sistema se detiene si hay parámetros indefinidos
- **Gated Pipeline** — Se requiere `"APROBADO"` antes de pasar de fase. A partir de v0.1.0 (Sprint 4), la aprobación está **firmada con HMAC-SHA256** (ver [ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md)).
- **Spec First** — No existe `src/` sin `SPEC.md` previo aprobado
- **TDD First** — No existe función de negocio sin su test previo
- **Portabilidad Absoluta** — Sin rutas absolutas; todo relativo a `./`
- **Dogfooding Visible** — El propio X-DD pasa por sus 6 fases en público ([ADR-0001](docs/adr/0001-dogfooding-visible-commiteable.md))

---

*X-DD System — Pipeline de desarrollo con excelencia operativa*
