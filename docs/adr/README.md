# Architecture Decision Records — X-DD

Índice cronológico de decisiones arquitectónicas. Formato [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html). Generadas vía `/adr-new`.

## Convenciones

- **Numeración:** 4 dígitos, secuencial, sin huecos.
- **Estados:** `Propuesto` | `Aceptado` | `Reemplazado por ADR-XXXX` | `Deprecado`.
- **Nunca borrar** un ADR — si se reemplaza, actualizar su estado y enlazar al nuevo.

## Índice

| # | Título | Estado | Tema |
|---|--------|--------|------|
| [0000](./0000-mapeo-mejoras-pipeline-xdd.md) | Mapeo MEJORAS-X-DD ↔ pipeline X-DD | Aceptado | Proceso |
| [0001](./0001-dogfooding-visible-commiteable.md) | Dogfooding visible y commiteable | Aceptado | Filosofía |
| [0002](./0002-profile-vs-config-coexisten.md) | `xdd.profile.yml` y `xdd.config.yml` coexisten sin overlap | Aceptado | Configuración |
| [0003](./0003-python-runtime-gate-keeper.md) | Python como runtime del gate keeper | Aceptado | Runtime |
| [0004](./0004-mempalace-dep-externa-no-fork.md) | MemPalace como dependencia externa, no fork | Aceptado | Dependencias |
| [0005](./0005-mcp-preferido-y-server-propio.md) | MCP como integración preferida + MCP server propio | Aceptado | Integración |
| [0006](./0006-gate-keeper-firma-hmac.md) | Gate keeper con firma HMAC-SHA256 | Aceptado | Seguridad |
| [0007](./0007-adapters-iniciales-claude-opencode-mcp.md) | Adapters iniciales: Claude Code + OpenCode + MCP | Aceptado | Integración |
| [0008](./0008-consolidacion-xdd-cli-diferida.md) | Consolidación `xdd` CLI Python — diferida a post-v0.1.0 | Propuesto (diferido) | Roadmap |
| [0009](./0009-politica-versionado-xdd-directorio.md) | Política de versionado de `.xdd/` (qué se commitea) | Aceptado | Repo |

## Cómo añadir un ADR

```bash
# Ejecuta el workflow X-DD
/adr-new

# O manualmente:
NEXT=$(printf '%04d' $(($(ls docs/adr/*.md | grep -oE '/[0-9]{4}-' | grep -oE '[0-9]{4}' | sort -n | tail -1) + 1)))
cp templates/adr.template.md docs/adr/${NEXT}-mi-decision.md
```

Tras crear, añadir entrada en este índice y commitear con `docs(adr): NNNN <título>`.
