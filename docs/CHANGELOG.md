# CHANGELOG técnico — X-DD

> Historia técnica del repositorio. Mantenida por `/xdd-trace` (cierre de sprint) y `/release-cut` (release).
> Formato basado en [Keep a Changelog](https://keepachangelog.com).
>
> Para release notes user-facing ver [RELEASES/](../RELEASES/) (a partir de v0.1.0).

---

## [Unreleased] — main

### Added — Sprint 5 (2026-05-26) — Registry tipado de agentes

- **`prompts/agents/registry.json`** — catálogo machine-readable con
  **180 agentes / 15 categorías** + **3 composition_patterns**
  (security_review, feature_squad, release_train) + **3 routing_rules**.
- **`prompts/agents/registry.schema.json`** — JSON Schema 2020-12 que define
  la estructura: agent (id, name, category, prompt_file, ide_compat,
  constraints, triggers, fallback_agent), composition_pattern y routing_rule.
- **`scripts/migrate-agents-to-registry.py`** — migrador automático.
  Parser YAML mínimo (no requiere PyYAML), genera ids kebab-case y atributos
  desde frontmatter. Re-ejecutable cuando se añaden agentes nuevos.
- **`scripts/validate-registry.py`** — valida schema + existencia de
  `prompt_file`. Modo `--strict` detecta id-refs rotas en composition_patterns
  y routing_rules.
- **`scripts/generate-equipo.sh`** — regenera `docs/equipo.md` desde el
  registry. SSoT-derived: elimina drift entre código y docs.
- **`.xdd/build/sprint-5/REPORT.md`** — Build (3/5).

### Changed — Sprint 5
- **`docs/equipo.md`** — ahora auto-generado desde registry. Header explícito:
  "NO editar a mano". Tablas por categoría con emoji/nombre/descripción/path.
- **`memoria.md`** — estado actualizado a Sprint 5 / Fase 4-Build (3/5).

### Fixed — entre sprints (2026-05-26) — PR #6

- **`.markdownlint.yaml`** — reescrito con 22 reglas cosméticas desactivadas
  (line-length, single-h1, blanks-around-*, table-column-style, bare-urls,
  list-marker-space). Mantiene solo reglas que detectan errores reales
  (estructura, links rotos, fenced code, encoding).
- **`.xdd/spec/DOMAIN.md`**, **`docs/GATE.md`**, **`prompts/agents/product/product-manager.md`**,
  **`prompts/agents/specialized/specialized-developer-advocate.md`** — 7 errores
  reales corregidos (tablas con `|` literal, blockquotes mal unidos, heading
  parseado mal).
- **CI `lint-markdown`** — pasó de 6603 errores en 295 archivos a **0 errores**.

### Operational — entre sprints (2026-05-26)

- **Política del repo cambiada a `delete_branch_on_merge=false`** —
  preserva las branches de cada sprint en GitHub para trazabilidad pública del
  trabajo realizado.
- **5 branches restauradas** desde reflog local y pusheadas:
  `feat/sprint-1-mempalace-quickstart`, `feat/sprint-2-ci-base`,
  `feat/sprint-3-doctor-config`, `feat/sprint-4-gate-hmac`, `feat/sprint-5-registry`.

### Added — Sprint 4 (2026-05-26) — Gate keeper HMAC ⭐

- **`scripts/xdd-gate.py`** — gate keeper programático con 5 subcomandos
  (`init`, `validate`, `transition`, `approve`, `status`) + salida `--json`.
  Implementa firma **HMAC-SHA256** sobre `(phase, sorted_checksums, approver,
  timestamp_utc_iso)` por cada aprobación. Cualquier alteración manual de
  artefactos / status / approvers / clave invalida la firma y `validate` lo
  detecta. Python ≥3.9, stdlib pura (sin deps PyPI).
- **`tests/test_gate.py`** — 17 tests pytest, todos verdes:
  init idempotente, approve con/sin key/approver, validate detecta tampering
  de artefactos / firma corrupta / clave rotada, transition no-secuencial,
  status reporta todas las fases.
- **`docs/GATE.md`** — referencia completa: setup, comandos, flujo típico,
  artefactos por fase, integración en workflows, rotación de clave,
  cobertura de amenazas (T1-T3 + V4 del threat model).
- **`.gitignore`** — `.xdd/.gate-key` explícito como secreto + Python/Node/IDE
  caches y env files (ADR-0009).
- **`.xdd/build/sprint-4/REPORT.md`** — Build (2/5).

### Dogfooding — Sprint 4

Las 3 fases ya completadas de X-DD aplicado a sí mismo están **APROBADAS y FIRMADAS**:

```
✓ briefing  APROBADO  (firma cffaf210…)
✓ spec      APROBADO  (firma 4fc4d8e6…)
✓ plan      APROBADO  (firma 232d9368…)
```

Transiciones validadas: `briefing→spec`, `spec→plan`, `plan→build` ✓.

### Changed — Sprint 4

- **`memoria.md`** — estado actualizado a Sprint 4 / Fase 4-Build (2/5).

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
