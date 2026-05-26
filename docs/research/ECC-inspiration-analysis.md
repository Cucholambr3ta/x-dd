# Research — ECC inspiration analysis

> Análisis comparativo X-DD vs [affaan-m/ECC](https://github.com/affaan-m/ECC)
> realizado durante Sprint 8 ampliado (2026-05-26). Documenta qué se tomó de
> ECC como inspiración, qué se descartó deliberadamente, y por qué.

## Objetivo

Identificar capacidades de ECC ("Everything Claude Code", MIT, ~12k LOC) que
mejoren X-DD sin contradecir su filosofía base (pipeline gated formal, dogfooding
visible, threat model riguroso).

## ECC en una línea

> "The agent harness performance optimization system. Skills, instincts, memory,
> security, and research-first development for Claude Code, Codex, Opencode,
> Cursor and beyond."

- **246 skills** (`skills/<name>/SKILL.md`)
- **61 agents** especializados
- **75 commands** (legacy slash-entry)
- **15+ hooks** event-driven (PreToolUse, PostToolUse, SessionStart, Stop, PreCompact)
- **Manifest-driven install** con 6 profiles (minimal/core/developer/security/research/full) + ~25 modules
- **AgentShield** — 102 reglas SAST específicas del agente
- **Continuous learning con instincts + /evolve** (SQLite state-store)
- **Cross-harness adapter DRY** (Cursor reusa hooks de Claude Code via adapter.js)
- **3-tier docs** (longform / shortform / security)
- **commitlint enforced**
- **install.sh + install.ps1** cross-platform

## Lo que X-DD tomó como inspiración (e implementó)

### Sprint 7 ampliado

| Capacidad ECC | Implementación X-DD | Diferencia clave |
|---|---|---|
| Hook system event-driven (15+ hooks Node) | 8 hooks **bash** cross-platform | X-DD usa bash por auditabilidad + ADR-0003 |
| Profiles: minimal/core/dev/security/research/full | Mismos 6 profiles | X-DD: 13 modules vs ECC ~25 (subset cuidadoso) |
| `install.sh` + `install.ps1` | Paridad cross-platform | X-DD usa Python3 para resolver manifests (no Node) |
| Cross-harness adapter (DRY) | `xdd-adapt.sh` con symlinks | X-DD prioriza MCP server para 5+ IDEs sin adapter dedicado |
| Schemas para hooks/install | 4 schemas JSON Schema 2020-12 | (mismo enfoque) |

### Sprint 8 ampliado (en curso)

| Capacidad ECC | Implementación X-DD |
|---|---|
| 3-tier docs | `the-{shortform,longform,security}-guide.md` |
| `commitlint.config.js` | Sí, + workflow CI `lint-commits.yml` |
| `WORKING-CONTEXT.md` separado de memoria | Sí — live state vs bitácora |
| `agent.yaml` manifesto plugin | Sí — interop para futuro plugin marketplace |
| Templates de issues/PR | 5 templates (bug, feature, ide-adapter, agent, PR) |
| `devcontainer.json` | Sí, con postCreate.sh y extensiones VSCode |

### Sprints 9-12 (próximos, en plan)

| Capacidad ECC | Sprint X-DD |
|---|---|
| Continuous learning (instincts + `/evolve` + SQLite) | Sprint 9 |
| Sistema de Skills (SKILL.md) + Eval-harness con grader types | Sprint 10 |
| Multi-agent orchestration runtime (`/pm2`, `/multi-*`) | Sprint 11 |
| AgentShield (102 reglas) | Sprint 12 (50 reglas iniciales) |

## Lo que X-DD descartó deliberadamente

### 1. Volumen masivo (246 skills + 61 agents + 75 commands)

X-DD ya tiene 49 workflows + 180 agentes. Sumar más sin criterio dilluye el
sistema. La filosofía es **menos cantidad, más calidad** + composition_patterns
en lugar de comandos duplicados.

### 2. `CLAUDE_PLUGIN_ROOT` lookup loops largos en hooks

ECC tiene scripts de hook que empiezan con 30+ líneas de búsqueda del plugin
root. X-DD usa path relativo simple (`.agent/hooks/scripts/`) que funciona en
WSL, Git Bash, Linux nativo y macOS sin gimnasia.

### 3. PM2 como dependencia para orchestration

ECC usa PM2 para multi-agent runtime. X-DD evita agregar Node como dep
obligatoria nueva — Sprint 11 implementará orchestration con Python `asyncio`
+ `subprocess` (stdlib pura, ADR-0003).

### 4. 194k stars de marketing inflado

ECC tiene visibilidad masiva (probable error de API o fork inflado). X-DD se
vende por **dogfooding visible** y **disciplina formal**, no por catálogo o
métricas vanity.

### 5. SOUL.md como manifesto separado

ECC tiene `SOUL.md` ("Core Identity"). X-DD lo cubre en `agent.yaml` +
`CLAUDE.md` + `the-shortform-guide.md` sin necesidad de otro archivo.

## Lo que X-DD tiene que ECC no

| Capacidad | X-DD | ECC |
|---|---|---|
| Pipeline gated formal de 6 fases | ✅ | ❌ (ad-hoc) |
| Firma HMAC-SHA256 en gates | ✅ (Sprint 4) | ❌ |
| `DOMAIN.md` + `THREATS.md` como artefactos de Fase 2 | ✅ | ❌ |
| 10 ADRs Nygard | ✅ | parcial |
| Dogfooding visible (`.xdd/`) | ✅ | ❌ |
| MCP server propio con whitelist de paths | ✅ (Sprint 6) | parcial |
| Constitución explícita del framework | ✅ | ❌ |
| Threat model STRIDE de 23 amenazas | ✅ | implícito |

## Métricas comparativas

| Métrica | X-DD v0.1.0-dev | ECC |
|---|---|---|
| LOC totales | ~5k (estimado) | ~35MB / mucho más |
| Workflows / commands | 49 workflows | 75 commands |
| Skills | 0 (Sprint 10) | 246 |
| Agentes | 180 | 61 |
| Hooks | 8 (Sprint 7) | 15+ |
| Profiles install | 6 | 6 |
| Tests del framework | 97 | "58 test files" (sin count claro) |
| ADRs Nygard | 10 | parcial |
| Dependencias runtime | Bash + Python3 stdlib + (opcional) Node | Node + Python + extras |

## Filosofías comparadas

| Tema | X-DD | ECC |
|---|---|---|
| Pipeline | Gated formal de 6 fases (Constitución) | Workflow flexible |
| Approval | HMAC-SHA256 firmado | "Plan Before Execute" (principio) |
| Audit trail | `.xdd/<phase>/.approvers` append-only + signature | Git commits |
| Cross-IDE | MCP-first (1 server, 5+ IDEs) | Plugin-per-IDE |
| Hooks | Bash, profile-gated | Node, profile-gated |
| Identity | `agent.yaml` + ADRs + CLAUDE.md | `SOUL.md` + `RULES.md` |
| Distribution | Manifest-driven install + dogfooding visible | Plugin marketplace (npm) |

## Conclusiones

ECC es un sistema **maduro y ambicioso** del que X-DD puede aprender mucho —
especialmente en hooks, manifests, install profiles, continuous learning y
multi-agent orchestration. El plan maximalista (Sprints 7-12 todos para v0.1.0)
incorpora estas capacidades **sin copiar verbatim** y manteniendo la filosofía
única de X-DD: **pipeline gated formal + dogfooding visible + threat model
riguroso + MCP-first multi-IDE**.

ECC y X-DD pueden coexistir en el mismo proyecto: ECC para amplitud
(246 skills), X-DD para disciplina de proceso (gates firmados, DOMAIN/THREATS).
No son competidores directos.

## Referencias

- ECC repo: https://github.com/affaan-m/ECC
- Plan X-DD: [MEJORAS-X-DD.md](../../MEJORAS-X-DD.md)
- ADRs relacionados: ADR-0001 (dogfooding visible), ADR-0005 (MCP preferido),
  ADR-0006 (HMAC firma), ADR-0007 (alcance de adapters)
- Análisis live en: [WORKING-CONTEXT.md](../../WORKING-CONTEXT.md)

## Atribución

Conceptos arquitectónicos inspirados en ECC (MIT, copyright affaan-m). No se
copió código verbatim. Implementaciones X-DD son independientes y mantienen
ADR-0003 (Python stdlib pura) y ADR-0004 (sin deps PyPI obligatorias).
