# CHANGELOG técnico — X-DD

> Historia técnica del repositorio. Mantenida por `/xdd-trace` (cierre de sprint) y `/release-cut` (release).
> Formato basado en [Keep a Changelog](https://keepachangelog.com).
>
> Para release notes user-facing ver [RELEASES/](../RELEASES/) (a partir de v0.1.0).

---

## [Unreleased] — main

### Added — Sprint 3 (2026-05-26)
- **`scripts/xdd-doctor.sh` v2** — reescrito con comparación SemVer real
  (`semver_ge` + `sort -V`), salida `--json` opcional (sobre-mejora), checks
  separados en Núcleo obligatorio / recomendado / Orquestadores / Testing /
  Seguridad / Estructura / Configuración. Versiones mínimas declaradas:
  git ≥2.30, bash ≥4.0, python3 ≥3.9, node ≥20, mempalace ≥3.3, bats ≥1.10,
  gitleaks ≥8.18.
- **`xdd.config.yml`** — configuración operacional del propio repo X-DD
  (dogfooding); directiva `# yaml-language-server` para autocomplete.
- **`schemas/xdd.config.schema.json`** — JSON Schema draft 2020-12; cubre
  mempalace, pipeline (con `require_signature` para HMAC), agents (Sprint 5),
  ide_adapters (Sprint 7).
- **`docs/CONFIG.md`** — referencia completa de cada campo con defaults,
  enums, ejemplos de validación.
- **`.xdd/build/sprint-3/REPORT.md`** — sub-reporte de Build (1/5).

### Changed — Sprint 3
- **`xdd-doctor.sh`** ahora retorna `--json` machine-readable para CI/dashboards.
- **`memoria.md`** — estado actualizado a Sprint 3 / Fase 4-Build (1/5).

### Added — Sprint 2 (2026-05-26)
- **`.github/workflows/lint-shell.yml`** — ShellCheck en push/PR sobre `**.sh`.
- **`.github/workflows/lint-markdown.yml`** — markdownlint-cli2 sobre `**.md`.
- **`.github/workflows/gitleaks.yml`** — escaneo de secretos en cada PR y push a main.
- **`.github/workflows/validate-prompts.yml`** — 3 jobs: lint-workflows + smoke-doctor + verify --help/--version en scripts.
- **`.markdownlint.yaml`** — reglas alineadas al estilo del repo (línea ≤200, HTML inline, headings duplicados siblings-only).
- **`.pre-commit-config.yaml`** — hooks pre-commit: trailing whitespace, end-of-file, check-yaml/json, large files, mixed line ending, shellcheck, gitleaks, markdownlint, lint-xdd-workflows.
- **`.github/renovate.json`** — config Renovate con preset OSS, automerge minor/patch, MemPalace con review requerido, security alerts habilitados.
- **`.xdd/plan/PLAN.md`** — espejo formal del plan macro en el repo (Fase 3-Plan dogfooded).

### Changed — Sprint 2
- **`memoria.md`** — estado actualizado a Sprint 2 / Fase 3.

### Added — Sprint 1 (2026-05-26)
- **`DEPENDENCIES.md`** — matriz oficial de dependencias (núcleo, recomendado,
  orquestadores, testing, seguridad) con versión mínima, distribución, licencia
  y rol. Advertencia anti-impostores para MemPalace.
- **`.editorconfig`** — convenciones consistentes (LF, UTF-8, 2-space, max 100,
  4-space para py/sh, tab para Makefile).
- **`.gitattributes`** — normalización a LF + linguist overrides para que GitHub
  clasifique `templates/`, `docs/` y `prompts/agents/` como documentación.
- **`Makefile`** — UX unificada: `make doctor|start|init|lint|test|trace|cierre|version`.
- **`.xdd/spec/DOMAIN.md`** — modelo de dominio (DDD) con 5 bounded contexts,
  15+ entidades, value objects, agregados, ubiquitous language y 7 reglas
  invariantes. Diagrama Mermaid.
- **`.xdd/spec/THREATS.md`** — modelo de amenazas STRIDE: 23 amenazas tipificadas
  + 5 vectores específicos para sistemas IA-driven + plan de mitigación por
  sprint.
- **`--help` y `--version`** añadidos a `xdd-start.sh`, `xdd-init.sh`,
  `xdd-doctor.sh`, `lint-workflows.sh` (todos `v0.1.0-dev`).

### Changed — Sprint 1
- **`README.md`** — badges (license, last-commit, ADRs, workflows, MemPalace);
  framing corregido de MemPalace ("dependencia externa MIT" en lugar de "pieza
  del ecosistema"); descripción técnica corregida ("ChromaDB + SQLite" en lugar
  de "base de grafos"); nueva sección "Qué NO es X-DD"; principios de
  gobernanza incluyen firma HMAC del gate y dogfooding visible.
- **`memoria.md`** — estado actualizado a Sprint 1 / Fase 2.

### Added — Sprint 0 (2026-05-26)
- **Dogfooding inicial** — directorio `.xdd/briefing/` con `SPEC.md` y `FEATURES.md`
  del propio X-DD como producto.
- **10 ADRs** (`docs/adr/0000` a `0009`) cerrando las preguntas abiertas del
  plan MEJORAS-X-DD v1.1: mapeo a fases, dogfooding visible, profile vs
  config, Python como runtime, MemPalace externa, MCP server propio, gate
  HMAC, alcance de adapters, CLI diferido, política de `.xdd/`.
- **`docs/adr/README.md`** — índice cronológico de ADRs.
- **`PROJ-MASTER-PLAN.md`** — Gantt Mermaid de los 8 sprints + grafo de dependencias.
- **`docs/CHANGELOG.md`** — este archivo.
- **Anexo v1.2 de `MEJORAS-X-DD.md`** — consolida las decisiones meta y enlaza ADRs.

### Changed — Sprint 0
- **`memoria.md`** — actualizada con sección "Estado Actual" del Sprint 0 y log
  de las 10 decisiones arquitectónicas.

---

## Convenciones

- Cada sección de sprint usa subcategorías: `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed`, `Security`.
- Cada bullet enlaza al archivo o sección que cambió.
- Commits asociados siguen formato convencional: `feat(N.N): ...`, `fix(N.N): ...`,
  `docs(adr): NNNN ...`.
- `/release-cut` consolida `[Unreleased]` a `[v0.1.0] — YYYY-MM-DD`.
