<div align="center">

# X-DD — Excelencia Operativa en Desarrollo Asistido por IA

[![pre-release](https://img.shields.io/badge/status-pre--release-orange)](https://github.com/Cucholambr3ta/x-dd/releases)
[![Constitución](https://img.shields.io/badge/Constituci%C3%B3n-v1.5-blue)](docs/constitucion.md)
[![Tests](https://img.shields.io/badge/tests-378%20(230%20pytest%20%2B%20148%20bats)-brightgreen)](tests/)
[![Agentes](https://img.shields.io/badge/agentes-180-blueviolet)](prompts/agents/registry.json)
[![IDEs](https://img.shields.io/badge/IDEs-7-informational)](docs/)

**Un sistema operativo para el desarrollo de software asistido por IA.**

</div>

---

## ¿Qué es X-DD?

X-DD transforma cualquier proyecto en un entorno gobernado donde **agentes de IA especializados** colaboran bajo reglas estrictas para producir software de alta calidad. Integra múltiples metodologías *-Driven Development* (SDD, FDD, BDD, ATDD, DDD, TDD, STDD, SecDD, Threat-Driven) como capas sobre un Gated Pipeline de 6 fases.

| Pilar | Descripción |
|---|---|
| **Metodología** | Pipeline de 6 fases (Briefing → Spec → Plan → Build → QA → Retro), cada una con checkpoint de aprobación humana |
| **Gobernanza** | [Constitución v1.5](docs/constitucion.md) (9 artículos) + Gate keeper criptográfico que bloquea avances de fase sin aprobación firmada |
| **Subagentes** | **180** agentes especializados con registry tipado en `prompts/agents/` |
| **Multi-IDE** | **7** adapters: Claude Code, Cursor, opencode, Windsurf, VSCode/Copilot, Antigravity, Codex |
| **Trazabilidad** | **43** ADRs (`docs/adr/`), **55** workflows, CHANGELOG + releases versionados |
| **Calidad** | **378 tests** (230 pytest + 148 bats); la suite unitaria corre como gate de CI en cada PR |
| **Memoria** | Flight recorder (`memoria.md`) + Continuous Learning (instincts SQLite) entre sesiones |

## Capacidades destacadas

- **Gate keeper HMAC-SHA256** — cada transición de fase se firma criptográficamente (`xdd-gate.py`); no hay "APROBADO" verbal.
- **CI como ley** — `.github/workflows/tests.yml` corre pytest + bats + AgentShield en cada PR. La cláusula "tests verdes antes de merge" (Constitución Art. 7 §4) es un gate ejecutable, no una promesa.
- **AgentShield** — audit estático de seguridad del propio framework (`xdd-shield.py`): 13 reglas sobre hooks, agentes, MCP tools y workflows.
- **MCP server propio** — `xdd-mcp-server` (Python stdlib pura) expone agentes, workflows y artefactos vía Model Context Protocol. ⚠️ _Deprecado v0.2.0 ([ADR-0044](docs/adr/0044-deprecar-mcp-no-necesario.md)): la copia real a IDEs lo reemplaza._
- **Instalación modular** — perfiles `minimal | core | developer | security | research | full | lean` con manifests declarativos validados por JSON Schema.
- **White-labeling** — `xdd-brand.sh` aplica branding y persona del orquestador por proyecto.
- **Observabilidad** — spans OTel, session replay, cost tracker, context budget (perfil strict).

## Quickstart

```bash
git clone https://github.com/Cucholambr3ta/x-dd.git
cd x-dd
./scripts/xdd-doctor.sh                 # diagnóstico del entorno
make init DEST=/ruta/a/tu/proyecto      # bootstrap de un proyecto X-DD
```

Verificar la suite completa localmente:

```bash
make install   # pytest + jsonschema + PyYAML (ver requirements-dev.txt)
make test      # lint + pytest + bats + AgentShield
```

## Scripts principales

| Script | Función |
|---|---|
| `xdd-doctor.sh` | Diagnóstico del entorno (`--json` para CI) |
| `xdd-init.sh` | Bootstrap de proyecto (`--profile`, `--list-profiles`) |
| `xdd-gate.py` | Gate keeper HMAC-SHA256 (init/validate/transition/approve/status) |
| `xdd-orchestrate.py` | Runtime multi-agente (sequential/parallel/parallel_then_sync) |
| `xdd-shield.py` | AgentShield: audit estático de seguridad del framework |
| `xdd-eval.py` | Eval-harness con 5 tipos de grader |
| `xdd-adapt.sh` | Genera config por IDE (7 adapters) |

## Gobernanza de ramas (Constitución Art. 7 v1.5)

Modelo **híbrido** ([ADR-0042](docs/adr/0042-gitflow-hybrid-trunk-based.md)): trunk-based por defecto, GitFlow opt-in. Invariantes en ambos modos:

- `main` y `develop` protegidas — integración solo vía PR con aprobación humana.
- **Tests verdes obligatorios** en CI antes de merge.
- Conventional Commits.

## Documentación

- [Constitución](docs/constitucion.md) — ley suprema, 9 artículos
- [Guía de Integración X-DD](docs/X-DD_Integration_Guide.md) — pipeline completo
- [INSTALL](INSTALL.md) — instalación detallada y perfiles
- [Guía de Retrofit](docs/RETROFIT_GUIDE.md) — capacidades extendidas
- [ADRs](docs/adr/) — 43 decisiones arquitectónicas
- [Guías por IDE](docs/) — `GUIA_*_AGENTES_SKILLS_WORKFLOWS.md` (7 IDEs)
- [LICENSE](LICENSE) — licencia del proyecto

---

<div align="center">

*X-DD — Excelencia Operativa*

</div>
