# ADR-0034 — Universal IDE adapter (copia real + 6 IDEs + MCP auto-config + auto-detect)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 24

## Context

ADR-0007 limitó adapters a claude-code + opencode; resto vía MCP "manual". Realidad de campo (dogfooding del maintainer): instalar X-DD/ANMAX en proyectos nuevos generó fricción:

1. **Symlinks rotos** — `xdd-adapt.sh` + `xdd-brand.sh` creaban `.claude/commands/*.md` como **symlinks**. Claude Code + VSCode Copilot **rechazan symlinks** → `/anmax` invisible ("No matching commands").
2. **Solo 2 IDEs** — Cursor/Windsurf/VSCode/Antigravity requerían config MCP manual no documentada → fricción para nuevo instalador.
3. **`.claude/commands/` no hereda del padre** — cada proyecto (CWD) necesita su propia config; workspace global no se propaga a subproyectos.
4. **MCP config manual** — usuario debía escribir `mcp.json` a mano en formato + ruta correcta por IDE.

Objetivo declarado del user: "install once → funciona en cualquier IDE, cero pasos extra".

## Decision

Sprint 24 reescribe adapter como **universal**:

### 1. Copia real, NO symlinks
`copy_real()` reemplaza `ln -sf`. Claude Code + Copilot leen archivos reales. Trade-off: pierde DRY (commands duplicados del SSoT), gana compatibilidad cross-IDE. SSoT sigue en `.agent/workflows/`; adapters son derivados materializados.

### 2. Seis IDEs soportados
| Target | Output | Slash nativo |
|---|---|---|
| `claude-code` | `.claude/commands/*.md` + `.mcp.json` | ✅ `/trigger` |
| `opencode` | `.opencode/command/*.md` + AGENTS.md + `.agent/workflows/` | ✅ |
| `cursor` | `.cursor/rules/*.mdc` + `.cursor/mcp.json` | ⚠️ `@trigger` + MCP |
| `windsurf` | `.windsurf/rules/*.md` + `.windsurf/mcp.json` | ⚠️ MCP |
| `vscode-copilot` | `.github/prompts/*.prompt.md` + `.vscode/mcp.json` | ✅ `/trigger` en Copilot Chat |
| `antigravity` | `.antigravity/mcp.json` + README | ❌ solo MCP tools |

### 3. MCP auto-config por IDE
`gen_mcp_json()` genera `mcp.json` en formato correcto:
- `mcpServers` key: Claude Code, Cursor, Windsurf, Antigravity
- `servers` key: VSCode (convención distinta)
- `cwd` apunta al proyecto → MCP server lee su `.xdd/` local

### 4. Trigger resolution
`resolve_trigger()`: `--trigger` flag > branding `xdd.profile.yml` > `"xdd"` default. Rebrand automático de cabecera del command copiado (`# /xdd` → `# /anmax`).

### 5. Auto-detect en xdd-init
Tras bootstrap, `xdd-init.sh` detecta IDEs presentes (CLI `command -v` o config dirs `.cursor/.vscode/.windsurf/.antigravity/.idx`) y corre `xdd-adapt` por cada uno. Opt-out: `XDD_NO_ADAPT=1`. Resultado: **un solo `xdd-init` configura todos los IDEs del dev sin pasos extra**.

## Alternatives considered

- **Mantener symlinks (status quo):** rechazado. Root cause de la fricción del maintainer.
- **Solo MCP universal (sin slash files):** rechazado. Claude Code/Copilot/OpenCode SÍ dan slash nativo — desperdiciarlo degrada UX.
- **Trigger `/` idéntico en todos los IDEs:** imposible técnicamente (Cursor/Antigravity no soportan slash markdown custom). Documentado honestamente en matriz.
- **Bundlear MCP server en cada IDE config global:** rechazado. Per-proyecto `cwd` necesario para `.xdd/` correcto.

## Consequences

### Positivas
- ✅ `xdd-init` → 6 IDEs configurados automáticamente, cero pasos manuales
- ✅ Symlink bug eliminado (copia real) → `/anmax` visible en Claude Code + Copilot
- ✅ MCP auto-config → Cursor/Windsurf/Antigravity listos sin escribir json a mano
- ✅ Trigger custom (ANMAX) propaga a todos los formatos
- ✅ Honestidad: matriz declara qué IDE da slash real vs MCP-only

### Negativas
- ⚠️ Commands duplicados (copia real) — re-correr adapter tras editar workflow SSoT. Mitigación: `xdd-adapt all` idempotente; futuro hook post-edit re-sync
- ⚠️ Antigravity/Cursor no tendrán `/trigger` slash (limitación IDE, no X-DD)
- ⚠️ `.github/prompts/` puede colisionar con prompts existentes del proyecto (cp sobreescribe; documentar)
- ⚠️ Auto-detect heurístico (config dirs) puede falsos-positivos (`.github` ⇒ vscode-copilot aunque no use Copilot). Aceptable: genera config inerte si IDE ausente

## Implementation Sprint 24

```bash
# Auto (en init):
bash scripts/xdd-init.sh /path --profile=full       # detecta + adapta todos

# Manual:
bash scripts/xdd-adapt.sh all --dest=/path --trigger=anmax
bash scripts/xdd-adapt.sh cursor --dest=/path
bash scripts/xdd-adapt.sh vscode-copilot --dest=/path

# Opt-out auto-adapt:
XDD_NO_ADAPT=1 bash scripts/xdd-init.sh /path
```

## Related
- ADR-0007 Alcance inicial adapters (superseded en alcance: 2 → 6 IDEs)
- ADR-0005 MCP integration preferida
- ADR-0011 White-labeling (trigger custom propaga a adapters)
- ADR-0033 GitNexus tier-1 (MCP companion, mismo patrón mcp.json)
- Lección [HERRAMIENTAS] symlinks en .claude/commands rechazados por Claude Code

## References
- VSCode prompt files: https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files
- Cursor rules: https://docs.cursor.com/context/rules
- MCP spec: https://spec.modelcontextprotocol.io
