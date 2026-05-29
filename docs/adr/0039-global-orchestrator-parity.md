# ADR-0039 — Global orchestrator parity: `/<trigger>` invocable desde cualquier dir

- **Fecha:** 2026-05-28
- **Estado:** Accepted
- **Sprint:** 29
- **Decididores:** Maintainer (Alejandro Placencia)
- **Relacionado:** ADR-0034 (Universal IDE adapter), ADR-0035 (Global install architecture), ADR-0036 (Codex adapter global skills — pattern origen), ADR-0037 (Windsurf adapter parity), ADR-0038 (Workflow enforcement Sprint 28)

## Contexto

Post Sprint 28, el orquestador X-DD (`/xdd` o `/<trigger>` custom) tenía limitación crítica:

**Era exclusivamente project-local.** Vivía en `.claude/commands/`, `.opencode/command/`, `.windsurf/workflows/`, etc. — todos relativos al proyecto. Para invocar `/<trigger>`, el usuario debía:

1. Crear directorio del proyecto
2. Ejecutar `bash scripts/xdd-init.sh .`
3. Abrir el IDE en ese dir
4. **Recién entonces** `/<trigger>` aparecía como slash command

**Caso de uso bloqueado:** "Abro IDE en directorio vacío, digo `/anmax quiero armar un proyecto`, y el orquestador me guía desde cero."

### Excepción ya existente

Codex (ADR-0036, Sprint 24) **ya implementaba el patrón global**: `~/.codex/skills/<trigger>-orchestrator/SKILL.md`. Codex permite `/<trigger>` desde cualquier dir porque su skill orchestrator vive en path global del usuario.

### Lecciones del proyecto piloto multi-IDE

Durante dogfooding, el usuario explícitamente expresó:

> "entonces no puedo decir, '/anmax quiero armar un proyecto, utiliza xdd'?"

La respuesta era NO en 6 de los 7 IDEs soportados. Solo Codex respondía Sí.

## Decisión

**Replicar el patrón Codex (`~/.codex/skills/`) a los 6 IDEs restantes.** Crear un nuevo script `scripts/xdd-global-install.sh` que instale el orquestador en path global del usuario por IDE.

### Paths globales por IDE

| IDE | Path global del orquestador | Patrón de archivo |
|---|---|---|
| claude-code | `~/.claude/commands/<trigger>.md` | slash command markdown |
| opencode | `${XDG_CONFIG_HOME:-~/.config}/opencode/command/<trigger>.md` | slash command markdown |
| cursor | `~/.cursor/rules/<trigger>.mdc` | rule .mdc con `@mention` |
| windsurf | `~/.codeium/workflows/<trigger>.md` | workflow Cascade |
| vscode-copilot | `${XDG_CONFIG_HOME:-~/.config}/Code/User/prompts/<trigger>.prompt.md` | prompt file Copilot |
| codex | `~/.codex/skills/<trigger>-orchestrator/SKILL.md` | skill orchestrator (ya soportado) |

### Self-bootstrap behavior (nueva sección en orquestador global)

El orquestador global incluye **Sección 0: SELF-BOOTSTRAP CHECK** que ejecuta ANTES del PRE-FLIGHT BOOTSTRAP Sprint 28:

```
0. SELF-BOOTSTRAP CHECK (Sprint 29)
1. Verifica si xdd.profile.yml existe en dir actual.
2. Si NO existe:
   - Pregunta al usuario: "Bootstrap ahora? Perfil sugerido: developer. [SI/NO/perfil-custom]"
   - Si SI: ejecuta bash <XDD_ROOT>/scripts/xdd-init.sh . --profile=developer inline.
   - Si NO: ABORT con mensaje "Ejecuta xdd-init.sh manualmente".
3. Si EXISTE: continúa con PRE-FLIGHT BOOTSTRAP estándar Sprint 28.
```

Después del self-bootstrap, el comportamiento es **idéntico al PROJECT-LOCAL** del Sprint 28.

### Precedencia project-local vs global

Los IDEs soportados respetan precedencia natural:

- **Claude Code:** `.claude/commands/` (project) > `~/.claude/commands/` (global)
- **OpenCode:** `.opencode/command/` (project) > `~/.config/opencode/command/` (global)
- **Cursor:** `.cursor/rules/` (project) > `~/.cursor/rules/` (global)
- **Windsurf:** `.windsurf/workflows/` (project) > `~/.codeium/workflows/` (global)
- **VSCode:** `.github/prompts/` (project) > `~/.config/Code/User/prompts/` (global)
- **Codex:** sin precedencia (todo global por diseño ADR-0036)

**Beneficio:** una vez que el proyecto se bootstrapea, el orquestador project-local con **PRE-FLIGHT BOOTSTRAP Sprint 28 strict** toma precedencia. El global solo se usa pre-bootstrap.

## Alternativas consideradas

### A. Hacer `xdd-init.sh` ejecutable desde global PATH

Rechazada. No resuelve el problema — usuario seguía teniendo que ejecutar comando bash antes de poder usar slash IDE.

### B. Crear binario `xdd` en PATH con subcomandos (`xdd init`, `xdd start`)

Rechazada. Misma limitación que A. Slash IDE más natural que CLI.

### C. Hooks IDE que auto-ejecutan `xdd-init.sh` al abrir dir vacío

Rechazada. Demasiado intrusivo. Algunos dirs vacíos no son proyectos X-DD. Auto-init sin consentimiento viola principio least-surprise.

### D. Symlinks globales al `.agent/workflows/` del repo X-DD

Rechazada. Los IDEs rechazan symlinks en paths config (lección ADR-0034 root cause de Claude Code).

### E. NO implementar — usuarios deben hacer bootstrap manual

Rechazada. Es exactamente el punto de fricción que se quería eliminar. El usuario lo verbalizó directamente.

## Consecuencias

### Positivas

- **`/<trigger>` invocable desde cualquier dir** en 6 IDEs (paridad Codex)
- **Self-bootstrap automático:** dir vacío → user confirma → `xdd-init.sh` ejecuta inline
- **One-time global install** por máquina (no per-proyecto)
- **Coexistencia con Sprint 28:** PRE-FLIGHT enforcement strict sigue activo post-bootstrap (project-local override)
- **Portabilidad CI:** `XDG_CONFIG_HOME` y `XDD_CODEX_HOME` env vars soportadas para tests bats con HOME mock
- **Uninstall limpio:** flag `--uninstall` remueve archivos previos
- **Check mode:** flag `--check` reporta qué está instalado sin escribir

### Neutras

- Suite tests bats crece con `xdd-global-install.bats` (14 casos)
- Script nuevo `scripts/xdd-global-install.sh` (~220 líneas)

### Negativas (aceptadas)

- Usuario debe ejecutar `bash scripts/xdd-global-install.sh` una vez por máquina (no auto)
- Trigger custom global requiere `--trigger=<NAME>` flag — sin parse automático de `xdd.profile.yml` (porque el script vive global, no project-local)
- Codex se reinstala vía `xdd-adapt codex` cada vez (no destructive — idempotente)

## Implementación

### Files nuevos

| Path | Propósito |
|---|---|
| `scripts/xdd-global-install.sh` | Script principal (instala/uninstala/check/dry-run) |
| `tests/bats/xdd-global-install.bats` | Suite tests (14 casos, HOME mock) |
| `docs/adr/0039-global-orchestrator-parity.md` | Este ADR |

### Files modificados

Ninguno. Sprint 29 es aditivo — no toca workflows ni scripts existentes. Coexiste con Sprint 28 enforcement project-local.

### Tests

```bash
bats tests/bats/xdd-global-install.bats   # 14/14 verde
```

### Smoke test usuario

```bash
# Install global (una vez)
bash scripts/xdd-global-install.sh

# Verificar
bash scripts/xdd-global-install.sh --check

# Resultado esperado:
#  ✓ claude-code: ~/.claude/commands/xdd.md
#  ✓ opencode: ~/.config/opencode/command/xdd.md
#  ✓ cursor: ~/.cursor/rules/xdd.mdc
#  ✓ windsurf: ~/.codeium/workflows/xdd.md
#  ✓ vscode-copilot: ~/.config/Code/User/prompts/xdd.prompt.md
#  ✓ codex: ~/.codex/skills/xdd-orchestrator/SKILL.md

# Flujo nuevo (post Sprint 29):
mkdir mi-proyecto && cd $_
# Abre IDE
# /xdd quiero armar un proyecto X-DD
# → orquestador detecta dir vacío
# → pregunta perfil
# → ejecuta xdd-init.sh inline
# → continúa con PRE-FLIGHT BOOTSTRAP strict Sprint 28
```

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Global install desactualizado tras update X-DD | Re-ejecutar `xdd-global-install.sh` (idempotente). Considerar futuro `--update` flag. |
| Conflicto con orquestadores de otros frameworks que usen `~/.claude/commands/<name>.md` | Flag `--trigger=<NAME>` permite naming distinto. Check pre-install si archivo existe (NO implementado aún — backlog). |
| Tests contaminan `~/.claude/` real del developer | Suite usa `mktemp -d` para HOME mock. Verificado 0 pollution. |
| Usuario quiere desinstalar selectivamente | Flag `--ides=<list>` + `--uninstall` permite remover IDEs específicos. |
| Cambio en path config de algún IDE (rebranding/version) | Documentado en script + ADR. Update único en `install_<ide>()` función. |

## Verificación end-to-end

```bash
# Tests Sprint 29
bats tests/bats/xdd-global-install.bats   # 14/14 verde

# Regresión Sprint 26 + 27 + 28
bats tests/bats/xdd-adapt.bats             # 18/18
bats tests/bats/xdd-adapt-windsurf.bats    # 11/11
bats tests/bats/xdd-init.bats              # 9/9
bats tests/bats/xdd-init-sprint28.bats     # 10/10

# Total cumulativo: 62/62 verde

# Lint
bash scripts/lint-workflows.sh             # 0 errores
```

## Referencias

- `scripts/xdd-global-install.sh` — implementación
- `tests/bats/xdd-global-install.bats` — 14 casos
- ADR-0036 — patrón Codex origen (skills global)
- ADR-0034 — universal IDE adapter (paths por IDE)
- ADR-0035 — global install architecture (precedente conceptual)
- ADR-0038 — Sprint 28 workflow enforcement (PRE-FLIGHT BOOTSTRAP heredado en orquestador global)
- Issue conversacional con usuario: "no puedo decir /anmax quiero armar un proyecto?" — driver directo del sprint
- VSCode prompt files spec: https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files
- Cursor rules spec: https://docs.cursor.com/context/rules
- Windsurf workflows spec: https://docs.windsurf.com/plugins/cascade/workflows.md
