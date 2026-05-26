# Contributing to X-DD

¡Gracias por considerar contribuir a X-DD! Esta guía es para developers que quieren añadir workflows, agentes, hooks, skills, adapters IDE o documentación.

## Antes de empezar

1. **Leé el plan vigente** — [MEJORAS-X-DD.md](MEJORAS-X-DD.md) + anexo v1.2.
2. **Leé los ADRs** — [docs/adr/](docs/adr/) explica las decisiones meta.
3. **Leé las 3 guías:**
   - [`the-shortform-guide.md`](the-shortform-guide.md) — 15 min, qué es X-DD
   - [`the-longform-guide.md`](the-longform-guide.md) — referencia exhaustiva
   - [`the-security-guide.md`](the-security-guide.md) — threat model + SecDD
4. **Verificá el entorno:** `bash scripts/xdd-doctor.sh` debe dar 0 críticos.

## Setup local

```bash
# Clonar
git clone https://github.com/Cucholambr3ta/x-dd.git
cd x-dd

# Doctor (instala lo que falte si lo pide)
bash scripts/xdd-doctor.sh

# Pre-commit (instala hooks de git locales)
pip install pre-commit && pre-commit install

# Suite de tests
bats tests/bats/                    # 35 tests shell
python3 -m pytest tests/ -q         # 50 tests Python
bats tests/e2e/test_quickstart.bats # 12 tests E2E
```

## Reglas duras

1. **ADR antes de implementar** decisiones arquitectónicas. Workflow `/adr-new` o copy
   `templates/adr.template.md` a `docs/adr/NNNN-slug.md` (siguiente número).
2. **Branch por sprint o por fix:** `feat/sprint-N-slug` o `fix/area-slug`.
3. **Conventional commits con scope:** `feat(N.N): descripción` donde N.N es la tarea
   de MEJORAS-X-DD.md o categoría (`docs(adr)`, `chore(trace)`, `fix(ci)`, etc.).
   Enforced por commitlint en CI.
4. **Cualquier "gotcha"** se registra en `lecciones.md` durante el sprint.
5. **`/cierre-fase` + `/xdd-trace`** obligatorios antes del merge (actualiza
   `memoria.md`, `lecciones.md`, `PROJ-MASTER-PLAN.md`, `docs/CHANGELOG.md`).
6. **Squash merge** del PR a `main`, **sin** `--delete-branch` (preservamos historia
   por sprint).
7. **Sin secretos** (gitleaks en pre-commit y CI los bloquea).
8. **Sin rutas absolutas** del host (Portabilidad Absoluta — Constitución Art. 4).
9. **Tests verdes obligatorios** — sin skip a menos que esté justificado en PR.
10. **Si modificás un artefacto de fase ya aprobada**, re-ejecutá
    `python3 scripts/xdd-gate.py approve --phase <fase>` para regenerar la firma
    HMAC (el gate detectará el tampering si no lo hacés).

## Cómo añadir cada tipo de contribución

### Añadir un workflow nuevo

```bash
# 1. Crear el .md con frontmatter `description:`
$EDITOR .agent/workflows/mi-workflow.md

# 2. Añadir entrada al catálogo
$EDITOR prompts/workflows/03_workflows_catalog.md

# 3. Lint
bash scripts/lint-workflows.sh
```

### Añadir un agente nuevo

```bash
# 1. Crear el .md con frontmatter (name, description, color, emoji, vibe)
$EDITOR prompts/agents/<categoria>/<categoria>-mi-agente.md

# 2. Regenerar registry
python3 scripts/migrate-agents-to-registry.py

# 3. Validar
python3 scripts/validate-registry.py --strict

# 4. Regenerar docs/equipo.md
bash scripts/generate-equipo.sh
```

### Añadir un hook nuevo

```bash
# 1. Crear el script bash
$EDITOR .agent/hooks/scripts/<event>-<matcher>-<name>.sh
chmod +x .agent/hooks/scripts/*.sh

# 2. Registrar en hooks.json
$EDITOR .agent/hooks/hooks.json

# 3. Validar schema + test
python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('.agent/hooks/hooks.json')), json.load(open('schemas/hooks.schema.json')))"
bats tests/bats/hooks.bats
```

### Añadir un IDE adapter nuevo

1. Hoy soportamos solo `claude-code` y `opencode` ([ADR-0007](docs/adr/0007-adapters-iniciales-claude-opencode-mcp.md)).
2. Para Cursor/Continue/Zed/Cline/Windsurf, usá el MCP server propio (`docs/MCP_INTEGRATION.md`).
3. Si querés añadir un adapter nuevo: abrí issue con justificación, ADR, y prueba de demanda (≥3 usuarios pidiéndolo).

### Añadir una skill nueva (Sprint 10)

Cuando Sprint 10 esté disponible:
```bash
mkdir -p skills/mi-skill
$EDITOR skills/mi-skill/SKILL.md   # con frontmatter name/description/origin/when_to_use
```

## Pull Requests

### Checklist obligatorio en el PR

- [ ] **Tests verdes:** bats + pytest + E2E
- [ ] **Lint limpio:** `lint-workflows.sh` + `xdd-doctor.sh` + `markdownlint`
- [ ] **Conventional commit message:** `feat(scope): ...` / `fix(scope): ...` / `docs(adr): ...`
- [ ] **ADR si aplica** (decisión arquitectónica)
- [ ] **Lección si aplica** (en `lecciones.md`)
- [ ] **`/cierre-fase` + `/xdd-trace`** ejecutados antes del merge
- [ ] **Branch protection:** CI verde antes de mergear

### Squash merge sin borrar branch

```bash
gh pr merge <N> --squash --admin --subject "..." --body "..."
# (sin --delete-branch — preservamos la branch)
```

## Estándares de código

| Lenguaje | Estilo | Herramienta |
|----------|--------|-------------|
| Bash | shellcheck severity=warning | ShellCheck via pre-commit |
| Python | ruff format (cuando aplique) | python3 stdlib pura preferido |
| Markdown | `.markdownlint.yaml` del repo | markdownlint-cli2 |
| YAML | yamllint (futuro) | manual |
| JSON | indent=2, schema validation | jsonschema en CI |

## Reportar issues

| Tipo | Template | Donde |
|------|----------|-------|
| Bug | `.github/ISSUE_TEMPLATE/bug.md` | GitHub Issues |
| Feature request | `.github/ISSUE_TEMPLATE/feature.md` | GitHub Issues |
| Pedido de IDE adapter | `.github/ISSUE_TEMPLATE/ide-adapter.md` | GitHub Issues (requiere ≥3 +1) |
| Pedido de agente | `.github/ISSUE_TEMPLATE/agent.md` | GitHub Issues |
| Vulnerabilidad de seguridad | **NO** abras issue — `SECURITY.md` | Email privado |

## Code of Conduct

Este proyecto adopta [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Al participar
te comprometés a cumplirlo.

## Licencia

Tus contribuciones se publican bajo la licencia [MIT](LICENSE) del proyecto. Al
abrir un PR aceptás esta condición.

## ¿Dudas?

- Discusiones generales: GitHub Discussions
- Bugs: Issues
- Privado (seguridad, conducta): contacto en `SECURITY.md`

¡Gracias por contribuir! 🚀
