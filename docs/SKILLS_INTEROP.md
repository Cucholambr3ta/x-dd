# Skills Interop — X-DD ↔ Microsoft Skills Framework + agents-best-practices

## X-DD SKILL.md format

```yaml
---
name: <name>
description: <one-line>
origin: x-dd | community | external
inspired_by: <upstream reference>
category: context-engineering | quality-gate | security | etc
when_to_use:
  - <trigger condition 1>
triggers:
  - <slash command or string>
evals: <path to evals/> | null
---

# <Name> — <Title>

## Propósito
...

## Configuración
...

## Boundaries
...

## Referencias
- [ADR-NNNN](../../docs/adr/NNNN-...)
```

## Mapping a Microsoft Skills Framework

| X-DD field | Microsoft SKM field |
|---|---|
| `name` | `skill.name` |
| `description` | `skill.description` |
| `category` | `skill.category` (taxonomía similar) |
| `triggers` | `skill.invocation.triggers` |
| `when_to_use` | `skill.when_appropriate` |
| `inspired_by` | (metadata) |
| `evals` | `skill.validation.eval_suite` |

Conversion bidireccional 1:1 via JSON mapping. Conversor: `scripts/xdd-skills-export.py --to=microsoft <skill>` (futuro v0.2.0).

## Mapping a agents-best-practices (DenisSergeevitch)

agents-best-practices enfatiza:
- Provider-neutral patterns (Codex/Claude/etc)
- Concise prompt format
- Tool use atomic + idempotent

X-DD adopta en SKILL.md frontmatter:
- `origin: external` para skills importados
- `inspired_by:` cita explícita
- Triggers neutrales (no Claude-specific)

## Skills X-DD post-Sprint 23

| Skill | Category | Sprint |
|---|---|---|
| `xdd-talk-compact` | output-optimization | 10 |
| `agent-eval` | quality-gate | 10 |
| `xdd-ai-review` | quality-gate | 16 |
| `xdd-compact` | context-engineering | 19 |
| `xdd-fs-context` | context-engineering | 19 |
| `xdd-sandbox` | security | 21 |

Todos provider-agnostic. Triggers documentados.

## Referencias
- Microsoft Skills Framework: https://docs.microsoft.com
- agents-best-practices: https://github.com/DenisSergeevitch/agents-best-practices
- [ADR-0032 Skills migration policy](adr/0032-skills-migration-plan-act-adapt-orch.md)
- [ADR-0020 Community skills voting](adr/0020-community-skills-voting-policy.md)
