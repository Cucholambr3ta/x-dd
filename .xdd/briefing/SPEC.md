# SPEC — X-DD v0.1.0

> **Especificación del propio X-DD aplicado como producto OSS publicable.**
> Este es el SPEC.md macro de la Fase 1-Briefing del pipeline X-DD,
> ejecutado sobre el repositorio X-DD para dogfooding visible (ADR-0001).

## 1. Identidad del producto

- **Nombre:** X-DD — Cross-Driven Development System
- **Tipo:** Framework metodológico OSS multi-IDE para desarrollo agéntico
- **Distribución:** Repositorio público GitHub + (futuro) `pip install xdd-cli`
- **Licencia:** MIT
- **Audiencia:** equipos que desarrollan con asistentes de IA y quieren disciplina de proceso (TDD/BDD/DDD/SecDD) sin atarse a un IDE específico

## 2. Problema que resuelve

Los equipos que adoptan asistentes de IA (Claude Code, Cursor, OpenCode, Windsurf, Copilot, etc.) caen en uno de dos extremos:

1. **Vibe-coding sin disciplina:** velocidad alta inicial, pero deuda técnica y vulnerabilidades acumuladas; imposible auditar decisiones.
2. **Proceso pesado anti-IA:** Scrum/SAFe que no aprovecha la velocidad de los agentes.

X-DD ofrece el punto medio: **pipeline gated de 6 fases** con metodologías embebidas (FDD/BDD/ATDD/DDD/TDD/STDD/SecDD/Threat-Driven), **agnóstico de IDE** vía adaptadores + MCP, y **memoria persistente** vía MemPalace.

## 3. Objetivos de v0.1.0

| # | Objetivo | Medición |
|---|----------|----------|
| O1 | Cualquier dev clona el repo y arranca en < 10 min | `tests/e2e/test_quickstart.bats` verde en CI |
| O2 | Funciona en ≥3 IDEs sin modificación del usuario | adapter para Claude Code + OpenCode + MCP genérico |
| O3 | Gate keeper auditable (no editable) | HMAC-SHA256 firma cada APROBADO |
| O4 | 100% portable: cero rutas absolutas en el repo | gitleaks + grep en CI |
| O5 | El propio X-DD pasa por sus 6 fases públicamente | `.xdd/{briefing,spec,plan,build,qa,retro}/` con `.status=APROBADO` |
| O6 | Repo OSS publicable | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, CI verde, devcontainer |

## 4. Restricciones (constraints inmutables)

- **C1 — Constitución Art. 9:** No agregar fases nuevas al pipeline de 6.
- **C2 — Portabilidad absoluta:** cero rutas `/home/...`, `C:\\...`, etc.
- **C3 — Sin lock-in de IDE:** ningún workflow puede vivir solo en `.claude/`.
- **C4 — MemPalace es dep externa (ADR-0004):** X-DD no la fork ni la empaqueta.
- **C5 — Local-first:** ninguna telemetría obligatoria; opt-in si llega a existir.
- **C6 — Dogfooding visible (ADR-0001):** `.xdd/` y artefactos de fase commiteables.

## 5. No-objetivos (lo que X-DD NO es para v0.1.0)

- No es un test runner (orquesta Vitest/Playwright/pytest, no los reemplaza).
- No es un framework de aplicación (no reemplaza React/Express/Django).
- No es MemPalace (lo consume; ver `DEPENDENCIES.md`).
- No es compatible con monorepos sin adaptación (roadmap post-v0.1.0).
- No expone telemetría a la nube.
- No soporta automatización de PRs ni issues de GitHub (eso lo hace el orquestador, no X-DD).

## 6. Stakeholders

- **Maintainer:** Alejandro Placencia (@Cucholambr3ta) — decisión final, sign-off de releases.
- **Usuarios target:** developers que ya usan ≥1 asistente IA y quieren disciplina sin perder velocidad.
- **Contribuyentes futuros:** vía issues + PRs con CI verde.

## 7. Métricas de éxito v0.1.0

- 8/8 sprints cerrados con `/cierre-fase` + `/xdd-trace`.
- 6/6 fases del propio X-DD con `.status=APROBADO` firmadas.
- ≥10 ADRs en `docs/adr/`.
- 100% de CI workflows verdes en `main`.
- Quickstart E2E < 10 min en Ubuntu y macOS.
- ≥6 tools expuestas por `xdd-mcp-server`.

## 8. Cronograma macro

Ver [PROJ-MASTER-PLAN.md](../../PROJ-MASTER-PLAN.md) (Gantt Mermaid de 8 sprints, ~17.5 días de trabajo).

## 9. Aprobación

- **Estado:** Propuesto — pendiente de aprobación al cerrar Sprint 0.
- **Aprobador:** Alejandro Placencia.
- **Próximo gate:** transición a Fase 2-Spec (Sprint 1).
