# X-DD Hooks

Catálogo de hooks event-driven inspirado en ECC (Sprint 7).
Definidos en [`hooks.json`](hooks.json) y validados contra
[`schemas/hooks.schema.json`](../../schemas/hooks.schema.json).

## Eventos soportados

- **PreToolUse** — antes de ejecutar tool. Puede bloquear (`exit_on_match: 2`).
- **PostToolUse** — después. No bloquea; útil para indexar / loguear.
- **SessionStart** — al iniciar sesión del orquestador.
- **SessionEnd** — al cerrar sesión (cleanup).
- **Stop** — al finalizar respuesta del agente.
- **PreCompact** — antes de compactar contexto.

## Profiles

Cada hook declara en qué profiles aplica: `minimal | standard | strict`.
Configurable vía env:

```bash
export XDD_HOOK_PROFILE=standard   # default
```

## Catálogo v0.1.0

| ID | Evento | Profile | Comportamiento |
|----|--------|---------|----------------|
| `pre:bash:dangerous-command` | PreToolUse `Bash` | standard, strict | **Bloquea** `rm -rf /`, `git push --force`, `git reset --hard origin/...`, `chmod 777`, `curl \| sh`, fork bombs, `dd >/dev/sda` |
| `pre:edit:config-protection` | PreToolUse `Edit\|Write` | strict | **Bloquea** edición de configs sensibles (linters, schemas). Override: `XDD_ALLOW_CONFIG_EDIT=1` |
| `pre:write:doc-file-warning` | PreToolUse `Write` | standard, strict | Advierte sobre `.md` fuera de paths canónicos (no bloquea) |
| `post:edit:mempalace-index` | PostToolUse `Edit\|Write\|NotebookEdit` | minimal+ | Re-indexa MemPalace en background |
| `post:bash:pr-logger` | PostToolUse `Bash` | standard, strict | Loguea URL de PR tras `gh pr create` en `~/.xdd/pr-history.log` |
| `session-start:context-load` | SessionStart | standard, strict | Imprime `WORKING-CONTEXT.md` + última sesión de `memoria.md` |
| `stop:git-check` | Stop | standard, strict | Advierte si hay cambios sin commitear/pushear |
| `stop:pattern-extraction` | Stop | strict | Stub para Sprint 9 (Continuous Learning) |

## Instalación

```bash
# Manual (futuro: vía manifests, Sprint 7.3)
cp -r .agent/hooks/scripts ~/.claude/hooks/
# O via xdd-adapt.sh (próxima iteración)
```

Los hooks usan `bash` puro (sin Node) para portabilidad. Reciben JSON por
stdin con `{tool_name, tool_input, tool_output?}`. Salida:
- `exit 0` — permitir y continuar
- `exit 2` — **bloquear** la herramienta (solo PreToolUse)
- otro código — error logueado, no bloquea

## Variables de entorno

| Var | Default | Efecto |
|-----|---------|--------|
| `XDD_HOOK_PROFILE` | `standard` | `minimal\|standard\|strict` |
| `XDD_DISABLED_HOOKS` | (vacío) | CSV de IDs a desactivar, ej `pre:bash:dangerous-command,stop:git-check` |
| `XDD_ALLOW_CONFIG_EDIT` | `0` | `1` permite editar configs protegidos |
| `XDD_SESSION_START_MAX_CHARS` | `8000` | cap del contexto inicial cargado |

## Tests

```bash
# Manual quick-check
echo '{"tool_input":{"command":"rm -rf /"}}' | bash .agent/hooks/scripts/pre-bash-dangerous-command.sh
# → BLOCKED + exit 2

echo '{"tool_input":{"file_path":".markdownlint.yaml"}}' | bash .agent/hooks/scripts/pre-edit-config-protection.sh
# → BLOCKED + exit 2

# Suite bats (Sprint 7.5)
bats tests/hooks/
```

## Crear un hook propio

1. Escribir script bash/node en `.agent/hooks/scripts/`.
2. Registrar entry en `.agent/hooks/hooks.json` siguiendo el schema.
3. Validar: `python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('.agent/hooks/hooks.json')), json.load(open('schemas/hooks.schema.json')))"`.
4. Test manual con stdin.

## Threat model coverage

Los hooks mitigan amenazas listadas en [.xdd/spec/THREATS.md](../../.xdd/spec/THREATS.md):

- **T2.6** (hook ejecutando script malicioso) — `pre:edit:config-protection` defiende los configs de linters/CI
- **T6.2** (workflow ejecuta `sudo` o accede fuera de scope) — `pre:bash:dangerous-command` bloquea ataques destructivos típicos
- **V2** (Hook ejecutando script malicioso post-commit) — todos los hooks viven en `.agent/hooks/scripts/` versionado y auditable, no en `.git/hooks/`
