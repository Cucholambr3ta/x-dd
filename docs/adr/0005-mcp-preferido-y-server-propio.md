# ADR-0005: MCP como integración preferida + MCP server propio de X-DD

- **Fecha:** 2026-05-26
- **Estado:** Deprecado por [ADR-0044](0044-deprecar-mcp-no-necesario.md) (2026-05-30) — borrado en v0.2.0
- **Decidido por:** Alejandro Placencia, Claude

> ⚠️ **DEPRECADO v0.2.0:** el piloto agentix demostró que la orquestación X-DD no
> requiere MCP (copia real a IDEs cubre el caso). MCP queda deprecado: sigue presente
> y funcional en v0.1.x, pero se eliminará en v0.2.0. Ver ADR-0044.

## Contexto

MEJORAS-X-DD.md v1.1 declara "MCP es la vía preferida de integración" pero solo **consume** el MCP server de MemPalace. No expone nada de X-DD vía MCP.

Si X-DD quiere ser multi-IDE sin escribir un adapter por IDE (Claude Code, OpenCode, Cursor, Windsurf, Copilot, Cline, Aider, Continue, Zed = 9 adapters), exponerse como MCP server propio reduce drásticamente la superficie de mantenimiento. MCP es estándar abierto soportado nativamente por Claude Code, Cursor, Continue, Zed, Cline, Windsurf.

## Decisión

**MCP es la vía preferida de integración para X-DD.** En Sprint 6 implementamos `xdd-mcp-server/` (Python + FastMCP) que expone:

- `xdd_validate_phase(phase)` — wrapper de gate keeper.
- `xdd_transition_phase(from, to)` — transición con validación.
- `xdd_list_workflows()` — catálogo desde `.agent/workflows/`.
- `xdd_invoke_workflow(name, args)` — ejecuta workflow.
- `xdd_list_agents(category?)` — desde registry tipado (Sprint 5).
- `xdd_get_phase_artifacts(phase)` — contenido de `.xdd/<fase>/`.

Cualquier IDE compatible MCP usa X-DD sin adapter específico.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Solo adapters por IDE | Control fino por IDE | 9 adapters a mantener; sintaxis cambia rápido | Insostenible |
| Solo MCP server, sin adapters | Mínima superficie | Slash commands no funcionan nativamente sin algún hook | Combinamos ambos: ADR-0007 |
| MCP server pero en Node | Coherente si futuro xdd-cli es Node | ADR-0003 ya eligió Python; FastMCP es Python | Coherencia interna |
| Esperar a un estándar más maduro | Cero riesgo | MCP ya tiene tracción en >5 IDEs major | No esperar |

## Consecuencias

- **Positivas:** Cursor/Continue/Zed/Cline obtienen X-DD nativo. Reduce ADR-0007 a 2 adapters explícitos.
- **Negativas / Trade-offs:** el server es proceso adicional (stdio o sse). Aceptable: FastMCP arranca en <1s.
- **Neutras:** documentación dedicada (`docs/MCP_INTEGRATION.md`) por IDE compatible.

## Plan de revisión

Revisitar si MCP es deprecado o reemplazado por un estándar superior. Si el server agrega tools >20, considerar partirlo por capability.
