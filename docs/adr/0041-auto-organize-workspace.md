# ADR-0041 — Auto-organize workspace + auto-gitignore declarativo

- **Fecha:** 2026-05-29
- **Estado:** Accepted
- **Sprint:** 31
- **Decididores:** Maintainer (Alejandro Placencia)
- **Relacionado:** ADR-0035 (Global install architecture — wrapper), ADR-0038 (Sprint 28 workflow enforcement), ADR-0039 (Global orchestrator), ADR-0040 (VSCode global discovery)

## Contexto

Durante dogfooding del piloto multi-IDE (proyecto e-commerce 2026-05-29) se detectó **contaminación severa del workspace**:

- **35 MB** de archivos no-proyecto en root del proyecto
- `prompts/` 2.9 MB con 180 agentes (framework, accesible vía wrapper global ADR-0035)
- `scripts/`, `skills/`, `templates/` copiados (framework — wrapper global ya los sirve)
- `MEJORAS-X-DD.md`, `INSTALL.md`, `DEPENDENCIES.md` (framework docs, no proyecto)
- `DOMAIN.md`, `THREATS.md`, `DISCOVERY.md`, `SPEC.md` en root sin estructura `docs/`
- Sin `.gitignore` base — caches/secretos potencialmente commiteables

**Root causes:**

1. `xdd-init.sh` con perfil `developer`/`full` copia el framework completo al proyecto pese a que ADR-0035 ya permite wrapper global. Manifests no diferencian entre módulos copy-required vs wrapper-reference.
2. Workflow `/project-architecture-gsd` v2.3.0 (Sprint 28) requiere invocación explícita post-SPEC. No es automático tras bootstrap.
3. No existe automation para `.gitignore` base — el archivo se crea vacío y se llena (o no) según vaya conociendo cada dev.
4. Docs canónicos del proyecto (`SPEC.md`, `DOMAIN.md`, etc.) terminan en root porque LLM orquestador no los mueve a `docs/`.

**Verbalización del usuario** durante dogfooding:

> "el repo se ve muy contaminado con carpetas y además mucha documentación está fuera de alguna estructura de carpetas definidas y genera mucho ruido visual"

> "que al momento de crear cierto tipos de archivos se vayan agregando directamente al .gitignore y además que se vaya ordenando la documentacion para tener un espacio de trabajo lo más limpio"

## Decisión

**Sistema declarativo de auto-organize con 3 puntos de entrada:**

1. **Hook PostToolUse `post:write:auto-organize`** — real-time, async, tras cada `Write`/`Edit`/`NotebookEdit`
2. **Script `scripts/xdd-organize.sh`** — invocable manual con `check`/`apply`/`init`/`status`/`all`
3. **Workflow `/cierre-fase` v1.3** — invocación batch en sello de cierre de cada fase

Las reglas se declaran en `templates/auto-organize.template.yml` (default del framework) o `.agent/auto-organize.yml` (override por proyecto).

### Reglas implementadas (8)

| ID | Acción | Patrones | Modo |
|---|---|---|---|
| `move_to_docs` | `move` | `SPEC.md`, `DOMAIN.md`, `THREATS.md`, `DISCOVERY.md`, `PLAN.md`, `PRD.md`, `SAD.md`, `RFC-*.md`, `API.md`, `openapi.yaml` | root → `docs/` |
| `move_research_to_subdir` | `move` | `*-research-*.md`, `*-inspiration-*.md`, `*-analysis.md` | root → `docs/research/` |
| `move_adrs` | `move` | `ADR-*.md`, `[0-9][0-9][0-9][0-9]-*.md` | root → `docs/adr/` |
| `gitignore_framework_pollution` | `gitignore_and_delete` | `MEJORAS-X-DD.md`, `INSTALL.md`, `DEPENDENCIES.md` | con `--confirm-delete` |
| `gitignore_framework_copies` | `gitignore_only` | `prompts/`, `scripts/`, `skills/`, `templates/` | preservar |
| `gitignore_cache` | `gitignore_only` | `node_modules/`, `__pycache__/`, `.venv/`, `*.log`, `*.tmp`, `.DS_Store`, `dist/`, `build/`, etc. | preservar |
| `gitignore_secrets` | `gitignore_only` + WARN si tracked | `.env`, `*.pem`, `*.key`, `credentials.json`, `.gate-key` | SecDD enforcement |
| `ensure_canonical_dirs` | `mkdir_with_gitkeep` + README placeholder | `idea/`, `docs/`, `api/`, `design/`, `assets/`, `src/`, `tests/` | scaffolding canónico |

### Principios de diseño

- **Idempotente:** ejecutar N veces produce mismo resultado (`.gitignore` no acumula duplicados; `move` skip si destino existe)
- **Non-destructive por default:** `apply` solo mueve + `gitignore_only`. Para `gitignore_and_delete` se requiere flag explícito `--confirm-delete`
- **Override por proyecto:** copia `templates/auto-organize.template.yml` a `.agent/auto-organize.yml` y modifica
- **Opt-out global:** `XDD_NO_ORGANIZE=1` desactiva todos los entry points
- **Preserva `.gitignore` del usuario:** solo añade patterns nuevos; no destruye contenido existente
- **SecDD enforcement:** secretos already-tracked en git → WARN (no auto-fix; requiere intervención humana con `git rm --cached`)

## Alternativas consideradas

### A. Borrar contaminación con script imperativo único `cleanup.sh`

Rechazada. Imperativo + hardcoded → no extensible. Cada nuevo patrón requiere edit del script. YAML declarativo permite override por proyecto sin tocar el motor.

### B. Hook PreToolUse que bloquee creación de archivos en paths "prohibidos"

Rechazada. Bloquear creación rompe flujo natural del LLM. Es mejor permitir y reorganizar después (PostToolUse). Menos fricción.

### C. Solo invocación manual via `bash scripts/xdd-organize.sh`

Rechazada. El usuario nunca lo va a recordar. Necesita ser automático para servir su propósito (auto-organize). Hook + workflow `/cierre-fase` aseguran ejecución en momentos canónicos.

### D. Reescribir `xdd-init.sh` para NO copiar framework files

Rechazada parcialmente — se aplicó **junto con** A41 (no en su lugar). Sprint 31 SÍ añade `xdd-organize init` post-bootstrap automático en `xdd-init.sh`. Pero auto-organize sigue siendo necesario para limpieza incremental durante sesiones.

### E. Crear sistema completo de "workspace lint" estilo eslint

Rechazada. Over-engineering. YAML declarativo + 8 reglas cubre 95% de los casos.

## Consecuencias

### Positivas

- **Cumple petición directa del usuario** (auto-gitignore + auto-organize docs)
- **Solo 8 reglas, fácil entender + override**
- **SecDD enforcement gratis** — secretos comunes auto-gitignoreados
- **`.gitignore` siempre presente y útil** post-bootstrap
- **Estructura canónica 7 dirs** automática desde día 1 del proyecto
- **3 entry points** (hook real-time, script manual, workflow cierre) cubren todos los flujos
- **Non-destructive defaults + opt-out env var** evitan sorpresas
- **Override por proyecto** sin modificar repo X-DD
- **Idempotente** — ejecutar al inicio de cada sesión vía hook no genera churn

### Neutras

- Suite tests bats crece con `xdd-organize.bats` (16 casos)
- 3 archivos nuevos en repo X-DD (script + template + ADR + hook script + workflow update + init update)
- Nuevo hook en `hooks.json` registrado para profiles `standard`/`strict`

### Negativas (aceptadas)

- Requiere `python3` + `PyYAML` instalados (consistente con resto de stack X-DD — ya documented)
- Hook PostToolUse async añade overhead mínimo tras cada Write/Edit (latencia < 100ms típico, fully async)
- `gitignore_and_delete` queda pendiente sin `--confirm-delete` por seguridad — usuario debe ejecutar explícitamente para limpiar framework pollution legacy

## Implementación

### Files nuevos

| Path | Propósito |
|---|---|
| `templates/auto-organize.template.yml` | Reglas declarativas (8 reglas, override por proyecto en `.agent/auto-organize.yml`) |
| `scripts/xdd-organize.sh` | Entry point principal (`check`/`apply`/`init`/`status`/`all`) |
| `.agent/hooks/scripts/post-write-auto-organize.sh` | Hook PostToolUse async, no destructive |
| `tests/bats/xdd-organize.bats` | 16 casos cubriendo todas las reglas + edge cases |
| `docs/adr/0041-auto-organize-workspace.md` | Este ADR |

### Files modificados

| Path | Cambio |
|---|---|
| `.agent/hooks/hooks.json` | + entry `post:write:auto-organize` (PostToolUse, async, standard/strict profiles) |
| `.agent/workflows/cierre-fase.md` | v1.2 → v1.3 — nueva Sección 5 AUTO-ORGANIZE antes del sello |
| `scripts/xdd-init.sh` | Auto-invoca `xdd-organize init` + `apply` post-bootstrap (opt-out `XDD_NO_ORGANIZE=1`) |
| `tests/bats/xdd-init-sprint28.bats` | Test workflow `/cierre-fase` ahora acepta v1.2+ (no exact match) |

### Tests

- ✅ `xdd-organize.bats` — 16/16 verde
- ✅ Regresión: 67/67 verde (Sprints 26/28/29/30 sin tocar)
- ✅ Lint workflows: 0 errores

### Smoke test usuario

```bash
# Sin tocar nada — preview:
bash scripts/xdd-organize.sh check --dest=/path/al/proyecto-sucio

# Aplicar (non-destructive):
bash scripts/xdd-organize.sh apply --dest=/path/al/proyecto-sucio

# Limpieza completa con delete de framework pollution:
bash scripts/xdd-organize.sh apply --dest=/path --confirm-delete

# Generar estructura canónica en proyecto nuevo:
bash scripts/xdd-organize.sh init --dest=/path/proyecto-nuevo
```

## Lecciones registradas (driver de este ADR)

```
### [PROCESO] Bootstrap default copia framework completo al proyecto — 2026-05-29
Causa raíz: Manifests no aprovechan wrapper global ADR-0035. Profile developer trata módulos como copy mandatory.
Lección: Manifest install-profiles.json debe declarar copy vs wrapper-reference por módulo.
Aplica a: Cualquier proyecto X-DD que no necesite modificar framework localmente.

### [PROCESO] Docs proyecto en root sin estructura canónica — 2026-05-29
Causa raíz: Workflow /project-architecture-gsd scaffolding NO auto-ejecutado post-init.
Lección: xdd-init.sh debe generar 7 dirs canónicos directo. Workflows posteriores mueven artefactos.
Aplica a: Todo proyecto bootstrapped.

### [HERRAMIENTAS] Falta automation auto-gitignore + auto-organize en sesiones — 2026-05-29
Causa raíz: Cada LLM/dev tiene que recordar gitignorear caches/secretos. No hay enforcement.
Lección: Hook PostToolUse + workflow /cierre-fase + script standalone garantizan automation en 3 momentos canónicos.
Aplica a: Todo proyecto consumidor de X-DD.
```

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Auto-move rompe imports/refs que apuntan a `./SPEC.md` | `skip_if_exists: true` + idempotente. Solo mueve si `docs/SPEC.md` no existe. Usuario debe actualizar refs manualmente — documentado en workflow `/cierre-fase`. |
| `.gitignore` cache rule añade entries no deseadas (proyecto necesita `node_modules` por razón válida) | Override por proyecto en `.agent/auto-organize.yml` — borrar pattern o regla completa. |
| Hook PostToolUse genera latencia perceptible | `async: true` en hooks.json — ejecuta en background, no bloquea respuesta del LLM. |
| Auto-delete framework pollution borra docs que el usuario quería conservar | Acción `gitignore_and_delete` requiere flag explícito `--confirm-delete`. Default `apply` solo gitignorea sin destruir. |
| Concurrencia: 2 hooks PostToolUse simultáneos modifican `.gitignore` | Riesgo bajo (single-threaded por sesión LLM). Mitigación futura: file lock — backlog. |

## Verificación end-to-end

```bash
# Tests Sprint 31
bats tests/bats/xdd-organize.bats   # 16/16 verde

# Regresión cumulativa
bats tests/bats/                     # 83/83 verde (67 previo + 16 Sprint 31)

# Smoke en proyecto contaminado:
PROJ=/path/al/proyecto-sucio
bash scripts/xdd-organize.sh check --dest=$PROJ | head -20
# Output esperado: lista de MOVE + GITIGNORE planeados

bash scripts/xdd-organize.sh apply --dest=$PROJ
# Output esperado: SPEC.md → docs/, .gitignore actualizado con caches/secretos
```

## Referencias

- `templates/auto-organize.template.yml` — reglas declarativas
- `scripts/xdd-organize.sh` — implementación
- `.agent/hooks/scripts/post-write-auto-organize.sh` — hook real-time
- `.agent/workflows/cierre-fase.md` v1.3 — invocación batch en cierre
- `tests/bats/xdd-organize.bats` — 16 casos
- ADR-0035 — wrapper global (origen de "framework copies son redundantes")
- ADR-0038 — Sprint 28 workflow enforcement (scaffolding 7 dirs origen)
- ADR-0040 — Sprint 30 fix VSCode global discovery
- Driver: feedback dogfooding directo del usuario 2026-05-29 (proyecto e-commerce piloto)
