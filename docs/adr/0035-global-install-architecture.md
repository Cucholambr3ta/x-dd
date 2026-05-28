# ADR-0035 — Global install architecture + dynamic path resolution

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 25

## Context

Sprint 24 estableció per-IDE adapters con copia real + MCP auto-config. Pero arquitectura tiene 3 problemas reales descubiertos en dogfooding:

1. **`cwd` estático en MCP config:** `xdd-adapt antigravity` (y cursor/windsurf/vscode) escriben entrada MCP con `cwd` absoluto al proyecto. **Limita a UN proyecto** — workspace switching en IDE no re-arranca MCP en nuevo proyecto.
2. **Duplicación per-proyecto:** `xdd-init.sh --profile=full` copia `xdd-mcp-server/`, `.agent/workflows/`, `prompts/agents/registry.json`, scripts/, etc. **N proyectos = N copias** del framework. Update X-DD requiere re-propagar manualmente.
3. **Resolución estática de paths:** `tools.py` constants `WORKFLOWS_DIR = ROOT/.agent/workflows` apuntan al ROOT del paquete instalado (donde está `xdd-mcp-server/`). Server MCP global no puede servir workflows per-proyecto.
4. **Antigravity skills convention:** Antigravity lee skills desde `.agents/` (plural, no `.agent/` singular convención OpenCode). Adapter no poblaba `.agents/skills/`.

Inspiración: propuesta IDE Antigravity (`plan_detallado_antigravity.md`) — modelo MemPalace/GitNexus (install once global, sirve a N proyectos).

## Decision

Sprint 25 adopta **arquitectura install-once-global**:

### 1. Wrapper PATH global
`scripts/xdd-mcp-install-global.sh` genera `~/.local/bin/xdd-mcp-server`:
```bash
#!/bin/bash
export PYTHONPATH="$XDD_ROOT:$PYTHONPATH"
exec python3 -m xdd-mcp-server "$@"
```
- `XDD_ROOT` baked al instalar (del repo X-DD del usuario)
- Sin `cwd` fijo — cwd del proceso = workspace IDE activo
- Comandos: `--check`, `--uninstall`, `--bin-dir=`, `--xdd-root=`

### 2. tools.py: resolver local-first + global fallback
3 helpers nuevos:
```python
def get_workflows_dir(project_root):  # local .agent/workflows/ → global ROOT
def get_registry_path(project_root):  # local registry.json → global
def get_xdd_dir(project_root):        # STRICTAMENTE local (phase artifacts aislados)
```
- 4 tools acept arg opcional `project_root` (default: `os.getcwd()`)
- Schemas inputSchema añaden `project_root: {type: string}`
- `xdd_get_phase_artifacts`: SIN fallback global — artifacts per-project obligatorio
- Backwards compat: `WORKFLOWS_DIR`/`REGISTRY_PATH`/`XDD_DIR` constants retenidas como alias

### 3. adapt_antigravity refactor
- Detecta `~/.local/bin/xdd-mcp-server` → modo **wrapper global** (sin `cwd`)
- Fallback modo legacy si no instalado (cwd fijo)
- Merge en `~/.gemini/config/mcp_config.json` (ADR-0033 path confirmado)
- **Popula `.agents/skills/`** (convención Antigravity plural — NO `.agent/` singular OpenCode) con 6 skills X-DD

### 4. Antigravity skills directory
`.agents/skills/<name>/SKILL.md` = convención Antigravity (descubierto en dogfooding mesalink: `.agents/skills/supabase/SKILL.md`). Adapter copia `skills/*/` SSoT del repo X-DD a `.agents/skills/` del proyecto.

## Alternatives considered

- **Mantener cwd estático (status quo Sprint 24):** rechazado. Bloquea workspace switching.
- **`pip install xdd-mcp-server`:** rechazado v0.1.0 (require packaging Python + PyPI publish). Diferido a v0.2.0.
- **Solo wrapper, sin local-first en tools.py:** rechazado. Sin local-first, proyectos con skills custom no se ven.
- **Solo local-first sin wrapper:** rechazado. Mantiene cwd estático en MCP config.
- **Symlinks .agents → .agent:** rechazado. Symlinks rechazados por Antigravity (lección Sprint 24).

## Consequences

### Positivas
- ✅ **Install once → sirve a N proyectos** (modelo MemPalace/GitNexus)
- ✅ Workspace switching en IDE → MCP arranca en proyecto activo automático
- ✅ Update X-DD upstream → todos los proyectos del user al instante (un `git pull` en X-DD repo)
- ✅ Cero pollution per-proyecto (no copia xdd-mcp-server/ + .agent/ a cada uno)
- ✅ Local-first: proyectos con workflows/agents custom toman prioridad
- ✅ `.agents/skills/` resuelve convención Antigravity sin breaking OpenCode
- ✅ Backwards compat 100% (constants viejos + cwd legacy mode disponibles)
- ✅ Phase artifacts aislados estrictamente per-proyecto (security: T4.3)

### Negativas
- ⚠️ Wrapper requiere `~/.local/bin` en PATH (warning instalador si falta)
- ⚠️ XDD_ROOT baked en wrapper — si user mueve X-DD repo, re-correr installer
- ⚠️ `.agents/skills/` duplica contenido de `skills/` source (acceptable: convención IDE-específica)
- ⚠️ `pip install` packaging diferido a v0.2.0

## Implementation Sprint 25

```bash
# Instalar wrapper global (una vez)
bash scripts/xdd-mcp-install-global.sh
bash scripts/xdd-mcp-install-global.sh --check

# Configurar IDE Antigravity (cualquier proyecto)
bash scripts/xdd-adapt.sh antigravity --dest=/path/proyecto
# → mergea ~/.gemini/config/mcp_config.json sin cwd + popula .agents/skills/

# Verificar local-first
python3 -c "
import sys; sys.path.insert(0, 'xdd-mcp-server')
import tools
print(tools.get_workflows_dir('/path/proyecto'))  # local si existe, global sino
"
```

## Related
- ADR-0033 GitNexus tier-1 (mismo patrón global install)
- ADR-0034 Universal IDE adapter (Sprint 24, base que este sprint mejora)
- ADR-0007 Alcance inicial adapters (now superseded por arquitectura global)
- T4.3 Phase artifacts read-only (mantenido + reforzado: estricto cwd)
- ADR-0011 White-labeling (trigger custom propaga via wrapper sin cwd)

## References
- Propuesta IDE Antigravity → `plan_detallado_antigravity.md` (leído, eliminado post-implementación)
- MemPalace/GitNexus install pattern (modelo de referencia)
- Antigravity `.agents/skills/<name>/SKILL.md` convención (descubierto en mesalink)
