# IDE Setup — X-DD universal adapter (Sprint 24)

**Install once → funciona en cualquier IDE.** `xdd-init` auto-detecta tus IDEs y genera config óptima por cada uno. Cero pasos manuales.

## Quick start

```bash
bash scripts/xdd-init.sh /tu/proyecto --profile=full
# → detecta IDEs presentes → genera .claude/commands/, .cursor/, .vscode/, etc.

# Manual (todos):
bash scripts/xdd-adapt.sh all --dest=/tu/proyecto

# Opt-out auto-adapt en init:
XDD_NO_ADAPT=1 bash scripts/xdd-init.sh /tu/proyecto
```

## Matriz IDE — qué obtienes

| IDE | Trigger | Mecanismo | Archivos generados |
|---|---|---|---|
| **Claude Code** | `/helios` slash ✅ | slash command real | `.claude/commands/*.md` + `.mcp.json` |
| **OpenCode** | `/helios` slash ✅ | command + workflows | `.opencode/command/*.md` + `AGENTS.md` |
| **VSCode + Copilot** | `/helios` slash ✅ | prompt files | `.github/prompts/*.prompt.md` + `.vscode/mcp.json` |
| **Cursor** | `@helios` + MCP ⚠️ | rules + MCP | `.cursor/rules/*.mdc` + `.cursor/mcp.json` |
| **Windsurf** | MCP tool ⚠️ | rules + MCP | `.windsurf/rules/*.md` + `.windsurf/mcp.json` |
| **Antigravity** | `/<trigger>` o MCP ✅ | MCP + local skills | `~/.gemini/config/mcp_config.json` (merge) + `.agents/skills/` |
| **Codex** | `/<trigger>` (description-based) ✅ | global skills | `~/.codex/skills/<trigger>-orchestrator/` (SKILL.md + agents-index.json) |

> ⚠️ **Verdad técnica:** La ejecución nativa de scripts de terminal mediante slash commands locales directos solo está soportada en Claude Code, OpenCode y VSCode Copilot. Cursor y Windsurf usan MCP tools u `@-mention`. Antigravity emula la experiencia de slash commands en el chat mediante el sistema de triggers conversacionales definidos en `.agents/skills/*.md`.

## Por IDE

### Claude Code
```bash
bash scripts/xdd-adapt.sh claude-code --dest=/proyecto
```
- `.claude/commands/helios.md` (copia real, NO symlink)
- `.mcp.json` apunta a xdd-mcp-server
- **Reinicia Claude Code** → `/helios` aparece en menú

### VSCode + Copilot
```bash
bash scripts/xdd-adapt.sh vscode-copilot --dest=/proyecto
```
- `.github/prompts/helios.prompt.md` → `/helios` en Copilot Chat
- `.vscode/mcp.json` (key `servers`, convención VSCode)
- Requiere Copilot con prompt files habilitados

### Cursor
```bash
bash scripts/xdd-adapt.sh cursor --dest=/proyecto
```
- `.cursor/rules/helios.mdc` → menciona `@helios`
- `.cursor/mcp.json` → tools MCP en Cursor Settings

### Antigravity (Google IDE)
```bash
bash scripts/xdd-adapt.sh antigravity --dest=/proyecto
```
- Configuración global de MCP mergeada en `~/.gemini/config/mcp_config.json`.
- Skills locales materializadas en `.agents/skills/`.
- **Triggers conversacionales:** Activa las skills en la CLI/chat de Cascade usando sus triggers (ej. escribiendo `/<trigger>` o `/compact`). También puedes invocar herramientas de contexto vía MCP (`xdd_invoke_workflow`).

## MCP server (denominador común)

Todos los IDEs MCP-capable consumen `xdd-mcp-server` (6 tools):
- `xdd_invoke_workflow` — arranca orquestador / workflow específico
- `xdd_list_workflows` — catálogo
- `xdd_list_agents` — 180 agentes
- `xdd_validate_phase` / `xdd_transition_phase` — gates HMAC
- `xdd_get_phase_artifacts` — contenido `.xdd/<fase>/`

Config MCP generada apunta a:
```json
{"command": "python3", "args": ["-m", "xdd-mcp-server"], "cwd": "/tu/proyecto"}
```

`cwd` = proyecto → MCP lee su `.xdd/` local. Para monorepo, cada package puede tener su MCP cwd.

## Troubleshooting

| Síntoma | Causa | Fix |
|---|---|---|
| `/helios` no aparece Claude Code | symlink (versión vieja) o no reiniciaste | re-run adapt (copia real) + reinicia |
| `/helios` no aparece en subproyecto | `.claude/` solo a nivel CWD, no hereda padre | `xdd-adapt claude-code --dest=subproyecto` |
| Antigravity no muestra `/helios` | Antigravity no tiene slash markdown | usa tools MCP, no slash |
| MCP server no responde | `xdd-mcp-server` no en PYTHONPATH | verifica `cwd` en mcp.json apunta a proyecto con dir `xdd-mcp-server/` |
| commands desactualizados | editaste workflow SSoT | re-run `xdd-adapt all` |

## Referencias
- [ADR-0034 Universal IDE adapter](adr/0034-universal-ide-adapter.md)
- [ADR-0007 Alcance inicial adapters](adr/0007-alcance-inicial-adaptadores.md)
- [docs/MCP_INTEGRATION.md](MCP_INTEGRATION.md)
- [docs/BRANDING.md](BRANDING.md) — trigger custom (Helios)
