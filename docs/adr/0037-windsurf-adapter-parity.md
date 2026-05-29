# ADR-0037 — Windsurf adapter parity (workflows nativos + MCP merge global)

- **Fecha:** 2026-05-28
- **Estado:** Accepted
- **Sprint:** 26
- **Decididores:** Maintainer (Alejandro Placencia)
- **Relacionado:** ADR-0034 (Universal IDE adapter), ADR-0035 (Global install arch), ADR-0036 (Codex adapter)

## Contexto

Post-Sprint 24/25, el adapter Windsurf (`adapt_windsurf()` en `scripts/xdd-adapt.sh`) era el más delgado de los 7 IDEs soportados:

```bash
adapt_windsurf() {
  write_file "$DEST/.windsurf/rules/${TRIGGER}.md" ...
  gen_mcp_json "$DEST/.windsurf/mcp.json" "mcpServers"
}
```

**Dos gaps identificados** durante review de doc generado por Windsurf IA (`docs/GUIA_WINDSURF_AGENTES_SKILLS_WORKFLOWS.md`):

### Gap 1 — Workflows nativos no copiados

Windsurf soporta workflows nativos en `.windsurf/workflows/*.md` invocables como slash commands `/workflow-name` (doc oficial: https://docs.windsurf.com/plugins/cascade/workflows.md). El adapter NO los generaba, pese a que Claude Code (`.claude/commands/`) y OpenCode (`.opencode/command/`) usan el helper `copy_commands()` exactamente con esta finalidad.

**Impacto usuario:** En Windsurf, `/xdd`, `/fase-requisitos`, etc. no estaban disponibles como slash nativos. Únicas vías de invocación eran MCP `xdd_invoke_workflow` o `@mention` rule. Workflow oficial Windsurf desaprovechado.

### Gap 2 — MCP config en path equivocado

Adapter generaba `.windsurf/mcp.json` (project-local), pero Windsurf lee MCP config exclusivamente de `~/.codeium/mcp_config.json` (global, doc oficial: https://docs.windsurf.com/plugins/cascade/mcp.md). Resultado: usuario corría `xdd-adapt windsurf` y MCP no se registraba en IDE — silently broken.

**Impacto usuario:** Bug crítico — apariencia de adapter funcional, pero zero MCP tools disponibles en sesiones Windsurf.

## Decisión

Implementar **paridad completa** del adapter Windsurf con los dos patrones canónicos existentes:

1. **Paridad workflows (vs Claude Code/OpenCode):** invocar `copy_commands "$DEST/.windsurf/workflows" "md"`. Reusar mismo helper que claude-code y opencode — zero código duplicado.

2. **Paridad MCP merge global (vs Antigravity):** replicar lógica de `adapt_antigravity()` (líneas 342+) — Python merge en config global con env var override `XDD_WINDSURF_HOME`, no destructivo, ABORT si JSON corrupto.

**Diferencias intencionales vs Antigravity:**
- Key JSON: `mcpServers` estándar (NO `$typeName` Cascade que es Antigravity-specific)
- Path: `$HOME/.codeium` (NO `$HOME/.gemini/config`)
- Sin Cascade plugin descriptor — Windsurf usa MCP estándar

**Adicionales (calidad/UX):**
- WARN al stderr si algún workflow excede 12000 chars (límite Windsurf documentado, soft warning no fail)
- Stub `.windsurf/mcp.json` project-local con `_comment` apuntando a path global (avoid confusión)
- `.windsurf/README-xdd.md` con arquitectura 3-mecanismo (workflows / rule / MCP)
- Detección extendida en `xdd-init.sh`: `$HOME/.codeium` como trigger adicional (CLI no siempre en PATH)

## Alternativas consideradas

### A. Mantener `.windsurf/mcp.json` project-local

Rechazada. Windsurf no lo lee — contradice doc oficial. Hubiera requerido documentar workaround manual al usuario (copia/edita).

### B. Sobrescribir `~/.codeium/mcp_config.json` (NO merge)

Rechazada. Destructiva — borra otros MCP servers que el usuario haya configurado para integraciones distintas a X-DD. Violación principio least-surprise.

### C. Crear `~/.codeium/mcp_config.json` separado por proyecto

Rechazada. Windsurf usa exactamente ese path global, no soporta múltiples. Solución correcta = merge.

### D. Generar N rules `.md` (una por workflow) como hack para emular slash

Rechazada. Lección Cursor: satura rule picker, mala UX, no es slash nativo real.

### E. No fix — dejar adapter "minimal" porque Windsurf tiene Cascade Workflows alternativa

Rechazada. Cascade workflows ≠ Windsurf workflows nativos. Adapter `windsurf` debe producir output funcional out-of-the-box, no requiere docs leídas por usuario para entender por qué `/xdd` no aparece.

## Consecuencias

### Positivas

- **Paridad funcional:** Windsurf alcanza nivel Claude Code/OpenCode (workflows) + Antigravity (MCP global)
- **Cero código nuevo de infraestructura:** reusa `copy_commands()` + patrón merge de antigravity
- **Portabilidad:** `XDD_WINDSURF_HOME` env var permite tests CI con HOME mocked vía `mktemp`
- **No destructive:** merge preserva otros MCP servers del usuario
- **Idempotente:** ejecutar N veces produce mismo resultado
- **Safe fail:** JSON corrupto detiene adapter sin destruir el archivo
- **UX clara:** stub project-local + README local explican dónde vive config real

### Neutras

- Adapter Windsurf pasa de 16 líneas a ~110 (alineado con `adapt_antigravity` ~80 líneas)
- Suite tests bats crece de 18 a 29 casos (11 nuevos en `xdd-adapt-windsurf.bats`)

### Negativas (aceptadas)

- Adapter ahora escribe en `$HOME` (global) — usuarios con tooling restrictivo pueden necesitar `XDD_WINDSURF_HOME` override. Documentado en guía.
- Requiere `python3` instalado para merge (ya requirido por resto de adapters — sin regresión).

## Implementación

### Diff principal `scripts/xdd-adapt.sh`

```bash
adapt_windsurf() {
  local windsurf_cfg="${XDD_WINDSURF_HOME:-$HOME/.codeium}/mcp_config.json"
  # Wrapper global detection (Sprint 25)
  local wrapper="$HOME/.local/bin/xdd-mcp-server"
  local use_global=0
  [ -x "$wrapper" ] && use_global=1

  # 1. Workflows nativos (paridad claude-code/opencode)
  copy_commands "$DEST/.windsurf/workflows" "md"

  # 1.b WARN si workflow > 12000 chars (límite Windsurf)
  # ...

  # 2. Rule @-mention
  write_file "$DEST/.windsurf/rules/${TRIGGER}.md" ...

  # 3. MCP merge GLOBAL (paridad antigravity, sin $typeName)
  python3 - "$windsurf_cfg" "$TRIGGER" "$DEST" "$wrapper" "$use_global" <<'PY'
  # ABORT si JSON corrupto, merge no destructivo
  ...
PY

  # 4. Stub project-local informativo
  write_file "$DEST/.windsurf/mcp.json" '{"_comment": "Config real en ~/.codeium/mcp_config.json", ...}'

  # 5. README local
  write_file "$DEST/.windsurf/README-xdd.md" ...
}
```

### Tests añadidos `tests/bats/xdd-adapt-windsurf.bats` (11 casos)

1. Copia workflows SSoT a `.windsurf/workflows/`
2. Merge MCP en `$XDD_WINDSURF_HOME/mcp_config.json` (no project-local)
3. Preserva otros servers existentes en config global
4. Crea archivo si no existe
5. ABORT no destructivo si JSON corrupto
6. Idempotencia (ejecutar 2x = mismo resultado)
7. Genera rule + stub mcp.json + README local
8. `--dry-run` no escribe nada (ni project ni global)
9. Default trigger `xdd` sin rebrand
10. `XDD_WINDSURF_HOME` override funciona (portabilidad CI)
11. Integración en target `all` (los 7 IDEs)

### Detección xdd-init.sh

```bash
{ command -v windsurf >/dev/null 2>&1 || [ -d ".windsurf" ] || [ -d "$HOME/.codeium" ]; } \
  && DETECTED="$DETECTED windsurf"
```

Añadido `[ -d "$HOME/.codeium" ]` — instalación Windsurf típica no pone CLI en PATH.

### Doc actualizada

`docs/GUIA_WINDSURF_AGENTES_SKILLS_WORKFLOWS.md`:
- Header: estado adapter → "✅ Implementación completa (Sprint 26 / ADR-0037)"
- Sección 2: "Sprint 26 resuelve los gaps"
- Sección 4 matriz: actualiza workflows + MCP path
- Sección 5.3: reescribe "qué hace el adapter" con outputs reales
- Sección 5.5: anti-patterns actualizados (gap resuelto + nuevo: edit directo en `.windsurf/workflows/`)
- Sección 8.1-8.5: estado actualizado, override portabilidad documentado
- Sección 12: tabla comparativa actualizada — paridad alcanzada
- Sección 14: troubleshooting refleja nuevo flow
- Sección 17 TL;DR: 7 puntos refrescados

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Tests pasados accidentalmente contaminan `~/.codeium/` del developer | `XDD_WINDSURF_HOME` mock obligatorio en tests; test 17 ("all") actualizado para forzar override |
| Usuario tiene `~/.codeium/mcp_config.json` con servers JSON-no-estándar | Adapter ABORTA con mensaje claro, no destruye archivo |
| Workflow excede 12000 chars en SSoT | WARN al stderr durante adapt, no fail. Usuario decide split |
| `python3` no instalado en máquina | Adapter falla con mensaje claro. Requirement ya documentado en `xdd-doctor.sh` |

## Referencias

- Implementación: `scripts/xdd-adapt.sh:260-380` (función `adapt_windsurf`)
- Tests: `tests/bats/xdd-adapt-windsurf.bats` (11 casos)
- Guía técnica: `docs/GUIA_WINDSURF_AGENTES_SKILLS_WORKFLOWS.md`
- Doc oficial workflows: https://docs.windsurf.com/plugins/cascade/workflows.md
- Doc oficial MCP: https://docs.windsurf.com/plugins/cascade/mcp.md
- ADR-0034: Universal IDE adapter (decisión de soportar 6 IDEs + Codex)
- ADR-0035: Global install architecture (wrapper `xdd-mcp-server` sin `cwd` fijo)
- ADR-0036: Codex adapter (patrón orchestrator + skills globales)
