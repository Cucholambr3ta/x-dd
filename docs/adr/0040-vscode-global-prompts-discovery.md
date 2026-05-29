# ADR-0040 — VSCode + Copilot global prompts discovery (merge `chat.promptFilesLocations`)

- **Fecha:** 2026-05-29
- **Estado:** Accepted
- **Sprint:** 30
- **Decididores:** Maintainer (Alejandro Placencia)
- **Relacionado:** ADR-0039 (Global orchestrator parity), ADR-0034 (Universal IDE adapter)

## Contexto

Sprint 29 implementó `scripts/xdd-global-install.sh` para registrar el orquestador `/<trigger>` global en los 6 IDEs soportados. La implementación inicial para VSCode + Copilot Chat escribía el prompt file en `~/.config/Code/User/prompts/<trigger>.prompt.md`.

**Bug detectado durante dogfooding 2026-05-29:**

El usuario ejecutó:
```bash
bash scripts/xdd-global-install.sh --trigger=anmax --check
# ✓ vscode-copilot: ~/.config/Code/User/prompts/anmax.prompt.md
```

Pero al abrir VSCode y escribir `/anmax`, **el autocomplete NO mostraba el slash command**, mientras que `/xdd` (project-local `.github/prompts/xdd.prompt.md`) sí aparecía.

### Root cause

VSCode + Copilot Chat por default **solo descubre prompts en workspace `.github/prompts/`**. La descubrir prompts globales (`~/.config/Code/User/prompts/`) requiere configuración explícita en `settings.json` del User:

```json
{
  "chat.promptFiles": true,
  "chat.promptFilesLocations": {
    "<path-al-dir-de-prompts>": true
  }
}
```

Sprint 29 escribía el prompt file pero NO configuraba la setting. Resultado: archivo presente, slash invisible.

### Diferencia vs otros IDEs

| IDE | Prompts global path | Auto-discover por default |
|---|---|---|
| Claude Code | `~/.claude/commands/` | ✅ Sí |
| OpenCode | `~/.config/opencode/command/` | ✅ Sí |
| Cursor | `~/.cursor/rules/` | ✅ Sí (rules picker) |
| Windsurf | `~/.codeium/workflows/` | ✅ Sí |
| **VSCode + Copilot** | `~/.config/Code/User/prompts/` | ❌ **NO — requiere setting** |
| Codex | `~/.codex/skills/` | ✅ Sí (descripción matching) |

VSCode es el único que requiere registro explícito del path en settings.

## Decisión

**Extender `install_vscode_copilot()` en `scripts/xdd-global-install.sh` para mergear `chat.promptFiles` y `chat.promptFilesLocations` en `~/.config/Code/User/settings.json` automáticamente.**

### Implementación del merge

```python
def install_vscode_copilot_settings():
    cfg = load_user_settings()  # parsea JSONC (comentarios + trailing commas)
    cfg["chat.promptFiles"] = True
    locs = cfg.get("chat.promptFilesLocations", {})
    if isinstance(locs, list):
        # Legacy schema: convertir lista a dict
        locs = {p: True for p in locs}
    locs[prompts_dir] = True
    cfg["chat.promptFilesLocations"] = locs
    save_user_settings(cfg)
```

### Reglas del merge (no destructivo)

1. **Preserva settings existentes:** `editor.fontSize`, `workbench.colorTheme`, etc. NO se tocan
2. **Preserva paths existentes en `chat.promptFilesLocations`:** otros paths registrados por el usuario o por otras herramientas se mantienen
3. **Tolera JSONC:** strip de comentarios `//` y `/* */` + trailing commas antes de parsear (VSCode usa JSONC, no JSON puro)
4. **Convierte legacy list schema:** algunas versiones tempranas usaban lista en vez de dict — auto-conversion
5. **ABORT si JSON corrupto:** error legible al stderr, archivo NO modificado
6. **Idempotente:** ejecutar N veces produce mismo resultado

### Path resolución

Sigue convenciones XDG:
```bash
local user_dir="${XDG_CONFIG_HOME:-$HOME/.config}/Code/User"
local prompts_dir="$user_dir/prompts"
local settings="$user_dir/settings.json"
```

Override portabilidad CI: `XDG_CONFIG_HOME` env var.

## Alternativas consideradas

### A. Documentar el setting en README sin tocar settings.json

Rechazada. Sprint 29 promete "install global = listo para usar". Requerir edición manual de `settings.json` rompe la promesa y hace que el usuario tenga que entender prompt files config interno de VSCode. Mala UX.

### B. Crear un script separado `xdd-vscode-configure.sh`

Rechazada. Añade un paso manual extra. La razón de `xdd-global-install.sh` es single-command install. No tiene sentido fragmentar.

### C. Pedir al usuario que escriba `chat.promptFilesLocations` manualmente

Rechazada. Misma razón que A. La cadena `${XDG_CONFIG_HOME:-$HOME/.config}/Code/User/prompts/` no es trivial de escribir correctamente.

### D. Generar un archivo `.vscode-prompts.config` separado fuera de `settings.json`

Rechazada. VSCode no consume tal config — solo lee `settings.json`. Inventar archivo paralelo no aporta.

### E. Solo escribir el prompt file, dejar al usuario configurar VSCode

Rechazada. Es exactamente la situación pre-Sprint 30. El bug que motivó este sprint.

## Consecuencias

### Positivas

- **`/<trigger>` global funciona en VSCode out-of-the-box** tras Sprint 30
- **No destructive:** otros settings del usuario + otros paths registrados preservados
- **Tolerant parsing:** maneja JSONC (formato real de settings.json VSCode) y legacy list schema
- **ABORT safety:** archivo corrupto detiene sin destruir
- **Tests cubren edge cases:** preservación, JSONC, ABORT, legacy schema → 5 casos nuevos en bats suite

### Neutras

- Suite tests bats crece de 14 a 19 casos en `xdd-global-install.bats`
- `install_vscode_copilot()` crece de 8 a ~55 líneas (Python merge inline)

### Negativas (aceptadas)

- Requiere `python3` instalado (consistente con resto del adapter — ya documented requirement)
- Si VSCode cambia el nombre de la setting en versión futura (`chat.promptFiles*`), Sprint 30 requerirá update
- Paths absolutos del usuario en `settings.json` — son del usuario host, no del repo. Aceptable.

## Implementación

### Files modificados

- `scripts/xdd-global-install.sh`: `install_vscode_copilot()` extendido (~47 líneas nuevas)
- `tests/bats/xdd-global-install.bats`: +5 casos (merge, preservación, JSONC, ABORT, legacy)

### Files nuevos

- `docs/adr/0040-vscode-global-prompts-discovery.md`: este ADR

### Tests

- 19/19 verde en `tests/bats/xdd-global-install.bats`
- Regresión Sprint 26 + 28: 39/39 verde
- Total cumulativo: **67/67 tests bats verde**

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Settings.json del usuario contiene formato JSONC complejo no cubierto por strip simple | Parser strip cubre `// line` + `/* block */` + trailing commas. Si parsing falla → ABORT (no destructive). Edge cases reales escalable. |
| VSCode renombra `chat.promptFiles*` en versión futura | ADR documentado. Update único en función. Cambio detectable por bats tests si setting key cambia. |
| Usuario quiere desinstalar — settings sigue apuntando a path borrado | VSCode ignora paths inexistentes silenciosamente. No rompe. `--uninstall` futuro flag podría limpiar también. |
| Conflicto con extensiones VSCode que también escriban `chat.promptFilesLocations` | Schema permite múltiples paths concurrentes. Merge aditivo no destructivo. |

## Verificación end-to-end

```bash
# Tests Sprint 30
bats tests/bats/xdd-global-install.bats   # 19/19 verde

# Smoke test usuario
bash scripts/xdd-global-install.sh --trigger=anmax
cat ~/.config/Code/User/settings.json | grep -A 5 "chat.promptFiles"
# Esperado:
#   "chat.promptFiles": true,
#   "chat.promptFilesLocations": {
#     "/home/<user>/.config/Code/User/prompts": true
#   }

# Reiniciar VSCode → abrir chat → escribir "/anmax" → autocomplete DEBE listar /anmax
```

## Lecciones registradas

Esta ADR retroaplica una lección detectada durante dogfooding:

```
### [HERRAMIENTAS] VSCode Copilot prompts globales requieren chat.promptFilesLocations explícito — 2026-05-29
**Contexto:** Sprint 29 xdd-global-install.sh para VSCode + Copilot.
**Problema:** /<trigger> global no aparece en autocomplete VSCode aunque archivo existe.
**Causa raíz:** VSCode Copilot default solo lee .github/prompts/ workspace. Path global User/prompts/ ignorado salvo configuración explícita.
**Lección:** Instalación global VSCode debe mergear chat.promptFilesLocations en settings.json User.
**Aplica a:** Cualquier global install VSCode + Copilot.
```

## Referencias

- `scripts/xdd-global-install.sh:232+` — implementación `install_vscode_copilot` post-Sprint 30
- `tests/bats/xdd-global-install.bats` — 5 casos nuevos
- ADR-0039 — Global orchestrator parity (Sprint 29 origen del bug)
- ADR-0034 — Universal IDE adapter
- VSCode prompt files docs: https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files
- Driver: feedback usuario durante dogfooding piloto multi-IDE (imagen autocomplete VSCode mostrando `/xdd` pero no `/anmax`)
