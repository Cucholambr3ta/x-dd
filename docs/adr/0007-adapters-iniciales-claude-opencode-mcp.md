# ADR-0007: Adapters iniciales — Claude Code + OpenCode + MCP genérico

- **Fecha:** 2026-05-26
- **Estado:** Aceptado (parte MCP deprecada por [ADR-0044](0044-deprecar-mcp-no-necesario.md), 2026-05-30)
- **Decidido por:** Alejandro Placencia, Claude

> ⚠️ **Parte MCP DEPRECADA v0.2.0:** los adapters de copia real (Claude Code, OpenCode,
> +5 IDEs) siguen siendo el camino vigente. La integración vía **MCP genérico** queda
> deprecada y se eliminará en v0.2.0 (ver ADR-0044). El resto de este ADR sigue vigente.

## Contexto

MEJORAS-X-DD.md v1.1 (Tarea 1.4) propone adapters para 9 IDEs: Claude Code, OpenCode, Cursor, Windsurf, Copilot, Cline, Aider, Continue, Zed. Mantener 9 adapters es alta superficie sin demanda probada.

ADR-0005 introduce un MCP server propio que cubre nativamente Cursor, Continue, Zed, Cline, Windsurf (y futuros).

## Decisión

**v0.1.0 implementa solo dos adapters explícitos:**

1. `xdd-adapt.sh claude-code` → `.claude/commands/*.md` + `CLAUDE.md`
2. `xdd-adapt.sh opencode` → `AGENTS.md` + `.agent/workflows/`

Los demás IDEs se conectan vía el MCP server (Sprint 6). Adapters adicionales (Cursor `.mdc` rules nativas, Windsurf rules nativas, Copilot instructions, Aider conventions) entran por contribución externa post-v0.1.0.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| 9 adapters desde v0.1.0 | Cobertura completa | Insostenible para 1 maintainer; sintaxis cambia rápido | Alto riesgo de inconsistencia |
| Solo MCP, cero adapters | Mínima superficie | Claude Code y OpenCode usan slash commands que no son MCP nativos | Pierde 2 IDEs con tracción real |
| Adapters auto-generados desde un DSL | Elegante | El DSL es proyecto en sí mismo | Sobre-engineering |

## Consecuencias

- **Positivas:** maintainer focal en Claude Code + OpenCode (los más usados por el target inicial) + MCP universal.
- **Negativas / Trade-offs:** usuarios de Cursor/Windsurf que prefieren rules nativas sobre MCP deben esperar (o contribuir).
- **Neutras:** `docs/IDE_SUPPORT.md` documenta claramente qué IDE usa qué mecanismo.

## Plan de revisión

Revisitar cuando llegue el segundo issue/PR pidiendo adapter para un IDE específico — ahí se evalúa promover de "MCP genérico" a adapter dedicado.
