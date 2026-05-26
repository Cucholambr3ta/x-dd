---
name: 🔌 IDE Adapter request
about: Solicitar soporte nativo para un IDE específico
title: 'feat(adapter): '
labels: enhancement, ide-adapter
---

> **Antes de abrir:** Cursor, Continue, Zed, Cline y Windsurf ya están
> soportados vía el MCP server propio de X-DD (`docs/MCP_INTEGRATION.md`).
> ¿Probaste esa vía? Si funciona, no necesitás adapter dedicado.

## IDE

- Nombre: (Cursor / Windsurf / Continue / etc.)
- Versión:
- URL oficial:

## ¿Por qué un adapter dedicado y no MCP?

(MCP cubre la mayoría de casos. Justificá por qué este IDE necesita más.)

## Convención de config del IDE

(¿Dónde lee el IDE los slash commands / agentes / rules? Linkeá docs oficiales.)

## Demanda

[ADR-0007](https://github.com/Cucholambr3ta/x-dd/blob/main/docs/adr/0007-adapters-iniciales-claude-opencode-mcp.md)
limita adapters dedicados a 2 (Claude Code + OpenCode). Para añadir uno
nuevo, requerimos:

- [ ] ≥3 +1 reactions en este issue
- [ ] PoC mínimo o referencia a integración existente
- [ ] Compromiso de mantenimiento del adapter (issue es buen indicador)
