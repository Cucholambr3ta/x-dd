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
- **Fase X-DD activa:** **2-Spec**
- **Sprint en curso:** **Sprint 1 — MemPalace externo + Quickstart real** (rama `feat/sprint-1-mempalace-quickstart`)
- **Plan macro:** [.claude/plans/indicame-que-mejoras-implementarias-happy-sunbeam.md](/home/alejandro/.claude/plans/indicame-que-mejoras-implementarias-happy-sunbeam.md) (8 sprints, ~17.5 días)
- **Último hito:** Sprint 0 mergeado (PR #1, commit `af3241b`): 10 ADRs + briefing + Gantt + CHANGELOG.
- **Próximo paso:** Cerrar Sprint 1 con `DEPENDENCIES.md`, README reescrito, `.xdd/spec/DOMAIN.md` + `.xdd/spec/THREATS.md`, Makefile, badges. PR a main. Luego Sprint 2 (CI base).

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
