# lecciones.md — Aprendizajes Acumulados

> Lecciones aprendidas del proyecto. Indexado por MemPalace. Consultado por agentes antes de proponer soluciones para evitar repetir errores (Constitución Art. 9).
> Actualizado vía `/cierre-fase` al final de cada fase.

## Formato
Cada lección sigue la estructura:
```
### [CATEGORÍA] Título breve — YYYY-MM-DD
**Contexto:** Qué estábamos intentando hacer.
**Problema:** Qué falló o sorprendió.
**Causa raíz:** Por qué pasó.
**Lección:** Regla aplicable a futuras decisiones.
**Aplica a:** Ámbito (módulo X, todo el proyecto, stack Y…).
```

Categorías sugeridas: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`, `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.

---

## Lecciones

### [HERRAMIENTAS] Symlinks rechazados Claude Code + VSCode Copilot → SIEMPRE copia real en `.claude/commands/` y `.github/prompts/` — 2026-05-27
**Contexto:** Sprint 24 universal IDE adapter inicial generaba `.claude/commands/*.md` como symlinks → SSoT en `.agent/workflows/`. UX broken: trigger custom "No matching commands" en Claude Code + Copilot Chat. Antigravity diagnostico CWD correcto pero también symlink → no aparecía.
**Problema:** Claude Code + VSCode Copilot prompt files NO siguen/aceptan symlinks (security policy). Antigravity también.
**Causa raíz:** Asumí que symlinks = OK para DRY. Falso para IDEs modernos AI-agent.
**Lección:** Para `.claude/commands/`, `.github/prompts/`, `.opencode/command/`: SIEMPRE `cp` real, NUNCA `ln -sf`. Trade-off DRY vs compat: compat gana. SSoT permanece en `.agent/workflows/`; adapter materializa copias. Re-correr adapter tras editar SSoT.
**Aplica a:** Cualquier adapter futuro X-DD para IDEs AI-agent. Pattern `copy_real()` en xdd-adapt.sh.

### [ARQUITECTURA] Install-once-global > per-proyecto copy → escalable cross-workspace (Sprint 25 + ADR-0035) — 2026-05-27
**Contexto:** Sprint 24 cwd estático MCP + xdd-mcp-server/ duplicado per-proyecto. Update X-DD upstream → propagar a N proyectos manualmente. Workspace switching IDE bloqueado.
**Problema:** N proyectos = N copias = N updates. cwd fijo MCP = 1 proyecto único soportado.
**Causa raíz:** Pattern install per-proyecto (legado xdd-init full). MemPalace + GitNexus YA usaban install-once-global (modelo correcto, no copié pattern hasta dogfooding falló).
**Lección:** Para framework que sirve N proyectos: usar wrapper PATH (`~/.local/bin/`) + tools.py resolver dinámico (local-first + global fallback) + MCP config sin cwd (workspace dinámico IDE). Backwards compat: alias constants WORKFLOWS_DIR/REGISTRY_PATH preserva imports externos. Patrón MemPalace/GitNexus validated.
**Aplica a:** Frameworks multi-proyecto. Wrapper installer pattern reusable.

### [PROCESO] Install manifests deben actualizarse CADA sprint que añade scripts/modules/skills (PR #39) — 2026-05-28
**Contexto:** Sprints 13-25 añadieron 18 scripts + 6 skills + 4 personas + registry. `manifests/install-modules.json` NUNCA se actualizó. `xdd-init full` instalaba ~25 paths cuando debía 70+. Bug salió en dogfooding agent_helios (faltaban xdd-state.py, xdd-orchestrate.py, etc.).
**Problema:** Manifests = SSoT install pero no en checklist sprint closure.
**Causa raíz:** `/cierre-fase` workflow cubre memoria/lecciones/CHANGELOG/PROJ-MASTER-PLAN pero NO `manifests/install-*.json`.
**Lección:** Añadir item a `/cierre-fase` checklist: "Si sprint añadió scripts/skills/files, actualizar `manifests/install-modules.json` (file en módulo apropiado o nuevo módulo) + verificar perfiles relevantes incluyen el módulo. Audit post-fix: `git ls-files` vs install_files cobertura debe ser 100% paths críticos (scripts/, skills/, prompts/orchestrator/)."
**Aplica a:** Todos los sprints que tocan source paths versionables. Workflow auto-check pendiente para v0.2.0.

### [DOMINIO] Cada IDE AI-agent tiene CONVENCIÓN propia — NO asumir cross-IDE compat sin leer docs (Codex case PR #40) — 2026-05-28
**Contexto:** Codex (OpenAI CLI) usa convención muy distinta a Claude Code/Cursor/etc.: Skills SOLO global (`~/.codex/skills/`), frontmatter MINIMAL (solo name+description), pattern 1 orchestrator + agents-index.json (NO N skills individuales — guía explícita "satura entorno"), trigger declarado en `description` (no slash registry). X-DD skills/* frontmatter incluye campos extra (origin, inspired_by, when_to_use, triggers, evals) → Codex ignora pero no rompe. AGENTS.md format X-DD ≠ Codex.
**Problema:** Asumí "skill = skill cross-IDE". Falso. Cada IDE tiene reglas.
**Causa raíz:** Skill spec ≠ universal. MCP es lo único universal cross-IDE.
**Lección:** ANTES de añadir adapter para IDE nuevo: (1) leer guía oficial del IDE, (2) identificar convenciones (paths, frontmatter mandatorio, patterns recommended/anti-patterns), (3) detectar override env var para tests. Pattern adapter consistente: detect → adapt → README local explicando dónde vive realmente. Frontmatter X-DD subset CON name+description sirve para IDEs minimalistas (Codex); IDEs ricos (Claude/Cursor) ignoran campos extra.
**Aplica a:** Futuros adapters IDE (Continue, Zed, Aider, Kiro, Trae, etc.). Mantener docs/IDE_SETUP.md actualizado con convención + override env var cada uno.

### [PROCESO] Workspace global = purga selectiva framework legacy + preserve hijos infra — 2026-05-27
**Contexto:** Workspace raíz `<workspace>/` tenía setup de framework legacy (predecessor X-DD). User pidió instalar X-DD global. El legacy es subset funcional inferior (15 categorías agents vs 180 X-DD; workflows legacy vs `xdd-*` renombrados; sin registry tipado; sin gate keeper HMAC). NO git repo → backup tar.gz crítico antes de tocar.
**Problema:** Colisiones directas (CLAUDE.md, .agent/, prompts/, scripts/, templates/, .claude/) requieren DELETE. Pero workspace también contiene non-legacy (Docker/MemPalace yaml, .hermes/, hermes-companion/, openwhispr/, personal/) que NO debe tocarse.
**Causa raíz:** Workspace mixed = product hijos + legacy bootstrap. Purga ciega corrompería productos.
**Lección:** Para install X-DD en workspace existente con framework legacy:
1. SIEMPRE backup tar.gz (workspace puede NO ser git repo).
2. Enumerar archivos colision-vs-preserve antes de tocar.
3. `tar -czf ~/workspace-backup-$(date).tar.gz CLAUDE.md docs/ .agent/ prompts/ scripts/ templates/ .claude/ setup_skills.sh` (solo lo a purgar, no toda la carpeta de 2.7GB).
4. `rm -rf` selectivo de paths X-DD-colliding.
5. `xdd-init.sh /path --profile=core` sobre workspace limpio.
6. Re-validar con `xdd-doctor.sh`.
**Aplica a:** Cualquier adopción X-DD sobre workspaces con frameworks legacy preinstalados. Patrón reusable para futuras migraciones ECC/Spec-Kit/BMAD adopters.

### [ARQUITECTURA] License tier-1 vs tier-2 según permisividad — GitNexus PolyForm Noncomm = tier-1 — 2026-05-27
**Contexto:** User pidió integrar GitNexus paralelo a MemPalace (tier-1 companion). GitNexus license = PolyForm Noncommercial 1.0.0. Decisión: ¿tratar igual que MemPalace (MIT, sin disclaimer pesado) o como Shannon (AGPL-3.0, external opt-in con disclaimer prominente)?
**Problema:** Default reflexivo era "GitNexus PolyForm = igual de restrictivo que Shannon AGPL → tier-2 external opt-in".
**Causa raíz:** Confundir restricción de **redistribución/modificación** (AGPL) con restricción de **uso comercial** (PolyForm). PolyForm permite uso research/personal/non-profit/educational sin restricción — más permisivo que AGPL para escenarios non-commercial.
**Lección:** Clasificar deps externas por licencia con matrix:
- MIT/Apache/BSD → tier-1 (sin disclaimer pesado)
- PolyForm Noncomm / similar source-available → tier-1 con disclaimer focalizado en "uso comercial requiere paid"
- AGPL → tier-2 external opt-in con disclaimer prominente (contamina si modificas + redistribuyes/SaaS)
- Proprietary → no recomendar
X-DD MIT NO se contamina por consumir client-side (MCP, CLI, API) cualquiera de las anteriores. Contaminación solo por bundlear código o redistribuir modificado.
**Aplica a:** Decisiones futuras de integración deps externas. Documentar matrix license en CONTRIBUTING.md (post-release).

### [PROCESO] ⚠️ Doc drift entre sprints rápidos — auditar README/CLAUDE/WORKING-CONTEXT/agent.yaml cada N sprints — 2026-05-27
**Contexto:** Tras correr Sprints 9-13 en secuencia rápida (4 sprints consecutivos sin pausa), el user preguntó "¿toda la documentación está actualizada?". Audit reveló drift significativo en 9 files macro: README sin badges/capacidades nuevas, CLAUDE.md sin scripts nuevos, WORKING-CONTEXT decía "Sprint 8 en curso", PROJ-MASTER-PLAN con S10 "🔄 En curso" (ya done), CHANGELOG sin entries S10/11/12/13, agent.yaml con workflows count viejo, INSTALL.md sin nuevos scripts/disclaimer Shannon, 3-tier guides sin secciones nuevas.
**Problema:** `/cierre-fase` + `/xdd-trace` se aplicaron por sprint pero **solo tocan** memoria.md + lecciones.md + PROJ-MASTER-PLAN + CHANGELOG. Files macro (README/CLAUDE/WORKING-CONTEXT/agent.yaml/INSTALL/guides) **NO están en el flujo automático** y solo se actualizan ad-hoc.
**Causa raíz:** Falta de checklist explícito de "files macro a tocar cada N sprints". El protocolo de cierre por sprint cubre trazabilidad granular pero no la doc estructural high-level que ve el visitante del repo OSS.
**Lección:** Cualquier framework OSS con dogfooding visible necesita 2 niveles de trazabilidad:
1. **Por-sprint** (granular): memoria/lecciones/CHANGELOG/PROJ-MASTER-PLAN (ya cubierto por /cierre-fase + /xdd-trace).
2. **Por-bloque** (estructural): README/CLAUDE/WORKING-CONTEXT/agent.yaml/INSTALL/guides — auditar **cada 3-5 sprints** o al cierre de cada fase X-DD.
Hacer un workflow `/docs-sync` (post-v0.1.0) que detecte drift automáticamente comparando contra git log + manifests. Patrón: SSoT-derived docs (como `docs/equipo.md` auto-generado desde registry) reducen drift; aplicar a más files si posible.
**Aplica a:** Cualquier framework OSS publicable que evolucione rápido. Refleja en `docs/research/` patrones de mantenimiento de docs. Considerar agregar a Sprint 14 o release v0.1.0 un workflow `/docs-sync` futuro.

### [TESTING] `capsys.readouterr()` necesita limpieza previa cuando hay output mezclado — 2026-05-26
**Contexto:** Sprint 9. Tests pytest de xdd-state.py invocaban init() + record() (con print "[state] ✓") + cmd_list(json=True). `capsys.readouterr().out` capturaba TODO acumulado, y `json.loads()` fallaba con "Extra data".
**Causa:** capsys es FIFO acumulativo. Sin limpieza, retorna todo desde el último readouterr().
**Lección:** Antes de capturar output del comando bajo prueba, llamar `capsys.readouterr()` sin asignar para limpiar buffer. O usar subprocess separado.
**Aplica a:** todos los tests pytest que parsean JSON de funciones que también imprimen logs humanos.

### [ARQUITECTURA] Heurística confidence +0.1/occ con cap 1.0 es MVP suficiente — 2026-05-26
**Contexto:** Sprint 9 xdd-state.py. Cómo asignar confidence a instincts.
**Decisión:** +0.1 por occurrence, cap 1.0. Simple, predecible.
**Lección:** Para v0.1.0 de feature nueva, heurística simple > algoritmo sofisticado. Sofisticación cuando hay datos para tunear. Sprint 11 puede agregar TF-IDF clustering; cluster-by-category basta como MVP.
**Aplica a:** cualquier feature nueva con espacio amplio de algoritmos. Simple > clever.

### [PROCESO] 3-tier docs (shortform/longform/security) cubren audiencias distintas sin canibalizar — 2026-05-26
**Contexto:** Sprint 8 ampliado, inspiración ECC. Producir 3 guías separadas de longitudes y propósitos distintos.
**Problema:** Tentación inicial: hacer un README grande y "completo". Resultado típico: nadie lo lee entero, los avanzados pierden tiempo en lo básico y los principiantes se asustan con detalles.
**Causa raíz:** Cada audiencia (developer nuevo / power user / security auditor) tiene tolerancia distinta de longitud y nivel de detalle.
**Lección:** Para repos OSS de framework, dividir docs por audiencia desde el día 1: (a) shortform 15 min visual con quickstart, (b) longform referencia por feature, (c) security-guide específico. README como índice + linkea a las 3. Patrón ECC reusable.
**Aplica a:** Cualquier framework OSS publicable. Pequeño costo extra (3 archivos vs 1), gran ganancia de adopción.

### [INTEROP] `agent.yaml` como manifesto plugin = "tarjeta de presentación" del framework — 2026-05-26
**Contexto:** Sprint 8, agregar manifesto plugin interop estilo ECC.
**Problema:** Cualquier orquestador o plugin marketplace que quiera descubrir las capacidades de X-DD tiene que parsear el repo entero (workflows, agentes, MCP, hooks, schemas, etc.). Caro y frágil.
**Causa raíz:** Falta de un manifesto único que declare "esto es X-DD, esto ofrece, esto requiere".
**Lección:** Para cualquier framework distribuible, mantener un `agent.yaml` (o `plugin.yaml` o `manifest.yaml`) en raíz que declare: workflows, agents, MCP server, hooks, gate, config, install, dependencies, supported_orchestrators. Es la "tarjeta de presentación" leíble por máquinas. Es a `agent systems` lo que `package.json` es a npm.
**Aplica a:** Frameworks que aspiran a ser instalables como plugins de orquestadores agénticos (Claude Code, OpenCode, Cursor, etc.).

### [DEVOPS] `set -eu` + `[ cond ] && cmd` al final = exit code 1 sorpresa — 2026-05-26
**Contexto:** Sprint 7.1, `xdd-adapt.sh` terminaba con `[ $DRY_RUN -eq 1 ] && echo "..."` como última línea.
**Problema:** Cuando `DRY_RUN=0`, el comando `[ 0 -eq 1 ]` retorna exit 1. Si es la última línea del script, el script entero termina con exit 1 — pero los tests bats detectaron esto, no la ejecución manual (porque manualmente el output parecía correcto y `$?` no se chequeaba).
**Causa raíz:** El idioma `[ cond ] && cmd` es atajo común en bash pero peligroso al final de scripts con `set -e`. La construcción equivalente `if [ cond ]; then cmd; fi` no tiene el side effect.
**Lección:** En scripts shell production-quality, NUNCA usar `[ ] && ...` como última línea ejecutable. Usar `if; then; fi` siempre, o terminar con `exit 0` explícito. Los tests bats (que sí chequean `$?`) son críticos para atrapar esto — la inspección manual no.
**Aplica a:** Todo script bash con `set -eu`. Patrón reutilizable.

### [TESTING] Tampering detection valida con cambios legítimos también — 2026-05-26
**Contexto:** Sprint 7.6, test E2E "fases briefing/spec/plan APROBADAS" falló con `Checksum mismatch en .xdd/spec/DOMAIN.md`.
**Problema:** El PR #6 (fix markdownlint) modificó legítimamente DOMAIN.md (reemplazó `|` literal en tabla por `/`). El gate keeper detectó el cambio post-aprobación e invalidó la firma — exactamente lo que debe hacer. Pero el test E2E asumía aprobación permanente.
**Causa raíz:** El gate distingue cambios autorizados de no autorizados solo si hay re-aprobación explícita. El test inicial no contemplaba el ciclo "cambio legítimo → re-aprobación → re-firma".
**Lección:** El modelo "approve & lock" debe documentar que cualquier cambio legítimo (incluyendo lint fixes, refactors menores) requiere `xdd-gate.py approve` nuevamente. Esto es feature, no bug — proporciona auditoría completa. Los tests E2E deben re-aprobar antes de validar O excluir validate de fases viejas.
**Aplica a:** Cualquier uso del gate keeper en CI. Workflow: PR modifica artefacto → desarrollador re-aprueba → gate firma → CI valida. Documentar en `docs/GATE.md`.

### [ARQUITECTURA] MCP stdlib pura > FastMCP cuando el subset es chico — 2026-05-26
**Contexto:** Sprint 6. Necesitaba implementar MCP server propio (ADR-0005).
**Problema:** La tentación inicial era usar `fastmcp` o `mcp-sdk` de PyPI — librerías oficiales/populares para MCP servers.
**Causa raíz:** Asumir que "librería oficial = mejor" sin medir el alcance real.
**Lección:** Para el subset MCP de X-DD (4 métodos JSON-RPC: initialize, tools/list, tools/call, notifications/initialized) la implementación stdlib pura cabe en ~80 líneas. Añadir una dep PyPI obligatoria habría violado ADR-0003 (Python stdlib pura) y bloqueado usuarios con políticas restrictivas de deps. Regla: medir alcance antes de añadir deps; si el subset cabe en <100 líneas y no se necesitan features avanzadas, stdlib gana.
**Aplica a:** Cualquier integración con un protocolo abierto donde solo se usa un subset pequeño (MCP, JSON-RPC, OpenAPI cliente mínimo, OAuth2 client minimal, etc.).

### [SEGURIDAD] Whitelist explícita de paths antes de exponer FS via API — 2026-05-26
**Contexto:** Sprint 6, tool `xdd_get_phase_artifacts` del MCP server.
**Problema:** Primera versión devolvía cualquier archivo que `Path.rglob` encontrara bajo el directorio de fase. Una corrupción de `.xdd/` o un symlink hostil podría haber filtrado contenido fuera del scope esperado.
**Causa raíz:** Pensar en términos de "feliz" (Path bajo `.xdd/<phase>/`) sin considerar el ataque (symlink, traversal, .xdd corrupto apuntando fuera).
**Lección:** Cualquier tool que devuelve contenido del filesystem via API debe tener **whitelist explícita de prefijos** en código (`ALLOWED_ARTIFACT_PREFIXES`), no inferida del path raíz. Defense in depth: validar dos veces (path está bajo dir esperado AND path matches whitelist).
**Aplica a:** Tools MCP futuras, cualquier endpoint REST que sirva archivos, integraciones MemPalace, plugins que leen FS del usuario.

### [PROCESO] Cambios de policy silenciosos rompen la trazabilidad del propio framework — 2026-05-26 ⚠️
**Contexto:** Sprint 1. Al hacer el primer `gh pr merge --squash`, el repo tenía squash merges deshabilitados. Solucioné activándolos y de paso activé `delete_branch_on_merge=true` "para limpieza". No consulté.
**Problema:** Durante 4 sprints las branches `feat/sprint-1-...` a `feat/sprint-4-...` se borraron en cada merge. El user lo descubrió al ver solo 2 branches en GitHub (main + sprint-0). Para un proyecto que vende "dogfooding visible" como diferenciador, eso destruyó exactamente la evidencia que debía mostrar.
**Causa raíz:** Cambié configuración del repo sin tratarla como decisión arquitectónica. La activación silenciosa de `delete_branch_on_merge` afectó la propuesta de valor del proyecto (trazabilidad histórica del trabajo), no solo la UX.
**Lección:** **Cualquier cambio a `repo settings`, `branch protection`, o cualquier policy que afecte cómo se preserva la historia debe tratarse como ADR.** Lo restauré gracias al reflog local (las 4 branches recuperables al commit pre-merge), pero la prevención hubiera sido proponer el ADR antes de tocar API. Patrón rojo: "lo cambio para que funcione esta vez" → afecta política del repo a futuro.
**Aplica a:** Cualquier `gh api -X PATCH repos/...`, `git config`, `core.hooksPath`, `branch protection rules`. Si modifica comportamiento más allá del comando actual, requiere ADR antes.

### [HERRAMIENTAS] Validator strict descubre id-refs rotas que el schema solo no detecta — 2026-05-26
**Contexto:** Sprint 5. Tras migrar 180 agentes a registry.json, `composition_patterns` y `routing_rules` referenciaban agent.ids aspiracionales pero no existentes (ej. `engineering-senior-software-engineer` cuando el real es `engineering-code-reviewer`).
**Problema:** JSON Schema valida tipos y forma, pero no relaciones cruzadas entre estructuras del mismo documento. Sin verificación de id-refs, los patrones quedan rotos hasta que alguien los invoca.
**Causa raíz:** Asumir nombres "obvios" sin verificar contra el catálogo real.
**Lección:** Cualquier registry con relaciones internas necesita validador `--strict` que verifique foreign-key-like constraints. Mejor: añadir esto al CI de Sprint 7 (workflow `validate-registry.yml`).
**Aplica a:** Cualquier JSON/YAML con relaciones internas (registries, workflows con referencias, configs con secciones cruzadas).

### [DEVOPS] SSoT-derived docs eliminan drift entre código y referencia humana — 2026-05-26
**Contexto:** Sprint 5. `docs/equipo.md` tenía contenido escrito a mano que se desactualizaba cada vez que se añadía un agente.
**Problema:** Drift entre el código (los .md de agentes), el registry y la doc humana es inevitable cuando ambos se editan a mano.
**Causa raíz:** Falta de SSoT — había dos fuentes de verdad y ninguna automatización entre ellas.
**Lección:** Para cualquier catálogo/inventory en proyectos de cualquier tamaño: declarar la SSoT explícita, derivar todo lo demás vía script (`generate-equipo.sh`), y poner el header "NO editar a mano" en el archivo derivado. El script va al CI para detectar drift.
**Aplica a:** `equipo.md` desde `registry.json`, `INSTALL.md` desde `DEPENDENCIES.md`, futuros catálogos.

### [SEGURIDAD] HMAC sobre payload canónico evita ambigüedades de serialización — 2026-05-26
**Contexto:** Implementando `xdd-gate.py` con firma HMAC-SHA256 (ADR-0006).
**Problema:** Inicialmente firmé sobre un dict serializado con `json.dumps(d)` sin opciones — `validate` fallaba intermitentemente porque el orden de las claves cambiaba entre runs.
**Causa raíz:** `json.dumps()` no garantiza orden estable de keys; en Python 3.7+ es por orden de inserción, pero la fuente del dict puede variar (lectura de archivo vs construcción in-memory).
**Lección:** Para HMAC sobre estructuras, siempre serializar con `json.dumps(d, sort_keys=True, separators=(',', ':'))`. Sin esto, dos representaciones equivalentes producen firmas diferentes y validación falsamente falla. Patrón llamado "canonical JSON" o "JCS" (RFC 8785).
**Aplica a:** Cualquier firma criptográfica sobre datos estructurados. Reutilizable más allá de X-DD.

### [TESTING] Tests del gate deben atacar el gate, no validarlo cortésmente — 2026-05-26
**Contexto:** Suite pytest del `xdd-gate.py` (Sprint 4).
**Problema:** Mi primer borrador tenía 6 tests "felices" (init OK, approve OK, validate OK). Insuficiente — el valor del gate no es que funcione cuando todo va bien, sino que **falle cuando algo se altera**.
**Causa raíz:** Sesgo a probar el camino feliz.
**Lección:** Los tests de seguridad/integridad deben atacar primero: alterar el artefacto, corromper la firma, rotar la clave, intentar transición no-secuencial, omitir el approver. Solo después validar el camino feliz. Resultado: 17 tests con cobertura real (no decorativa).
**Aplica a:** Cualquier test de mecanismos de control (gates, locks, ACLs, signatures, JWTs). Patrón "fuzzing dirigido en tests unitarios".

### [HERRAMIENTAS] `sort -V` es el comparador SemVer portable más simple — 2026-05-26
**Contexto:** Sprint 3 reescribe `xdd-doctor.sh` con comparación de versiones real (no solo `command -v`).
**Problema:** Comparar versiones en bash con `[ "$a" -gt "$b" ]` no funciona (strings); usar herramientas externas (vergleicher, sver) añade deps.
**Causa raíz:** Bash no tiene SemVer nativo; cada solución artesanal con `awk`/regex es propensa a errores con sufijos (`-dev`, `-rc1`, `.post1`).
**Lección:** `sort -V` (`--version-sort`) de coreutils está en todo Linux y macOS modernos. La función `semver_ge() { [ "$(printf '%s\n%s\n' "$min" "$ver" | sort -V | head -n1)" = "$min" ]; }` resuelve el 95% de los casos. Acepta `1.2.3`, `1.2`, sufijos pre-release. Sin deps.
**Aplica a:** Cualquier comparación SemVer en scripts shell. Reutilizable.

### [DEVOPS] `--json` desde el día 1 vale más que UI elegante — 2026-05-26
**Contexto:** Decisión de añadir `--json` a `xdd-doctor.sh` (no estaba en plan v1.1).
**Problema:** Salida solo humana ata el script a uso interactivo; integración con CI/dashboards requiere parseo frágil.
**Causa raíz:** Subestimar futuros consumidores de la herramienta.
**Lección:** Cualquier script de diagnóstico/estado debe ofrecer `--json` (o `--format=json`) desde el primer release. El esfuerzo extra es pequeño y abre integraciones que de otra forma requieren reescritura. Patrón: separar render humano vs JSON con flag temprano.
**Aplica a:** `xdd-gate.py` (Sprint 4), futuras tools del MCP server (Sprint 6), métricas (Sprint 10+).

### [DEVOPS] Branch protection con squash merges deshabilitado bloquea el flujo — 2026-05-26
**Contexto:** Tras pushear Sprint 1, `gh pr merge 2 --squash` falló con "Squash merges are not allowed on this repository".
**Problema:** El repo se creó con configuración default que no permite squash merges; bloquea la convención que el user pidió ("commits + PR + --squash").
**Causa raíz:** GitHub repos heredan `allow_squash_merge` según preferencias del owner, no necesariamente del workflow elegido.
**Lección:** Al crear repo nuevo para X-DD, configurar de inmediato vía API: `allow_squash_merge=true`, `allow_merge_commit=true`, `allow_rebase_merge=false`, `delete_branch_on_merge=true`. Documentar en `INSTALL.md` o `CONTRIBUTING.md` (Sprint 8).
**Aplica a:** Todo repo X-DD nuevo. Considerar añadir a `xdd-init.sh` un paso opcional si hay `gh` + remote configurado.

### [PROCESO] CI primero, refactor después — 2026-05-26
**Contexto:** Sprint 2 añade 4 GitHub Actions antes de implementar el gate keeper (Sprint 4) o el MCP server (Sprint 6).
**Problema:** Tentación de "primero hago el feature, después le pongo CI". Resultado típico: features llegan rotas o sin cobertura.
**Causa raíz:** El CI cuesta poco y atrapa regresiones desde el commit 1. Diferirlo invierte la ecuación.
**Lección:** En todo release público nuevo, los 4 linters básicos (shell + markdown + secrets + custom) van en el sprint 2-3 máximo. Antes de cualquier feature compleja. Las features se construyen sobre CI verde, no al revés.
**Aplica a:** Cualquier proyecto OSS / framework. Reutilizable.

### [HERRAMIENTAS] Edit en scripts requiere Read previo en la misma sesión — 2026-05-26
**Contexto:** Auditando los 4 scripts shell para añadirles `--help` y `--version` (Sprint 1).
**Problema:** El primer Edit sobre `xdd-init.sh` y `xdd-doctor.sh` falló con "File has not been read yet" pese a que ya estaban leídos en mensajes anteriores de la conversación.
**Causa raíz:** El tracker de archivos del agente vincula Read↔Edit por sesión/contexto activo; tras compresión o turnos largos puede perder la asociación.
**Lección:** Si un Edit falla con ese error, hacer un Read corto (10 líneas) del archivo target inmediatamente antes del Edit. Coste mínimo, evita el error y mantiene velocidad.
**Aplica a:** Cualquier edición a archivos previamente vistos pero no editados en la sesión activa.

### [DOMINIO] DOMAIN.md y THREATS.md del framework prueban su propia coherencia — 2026-05-26
**Contexto:** Producción de `.xdd/spec/{DOMAIN,THREATS}.md` del propio X-DD aplicado a sí mismo.
**Problema:** Al escribir DOMAIN.md emergieron entidades que el plan no había nombrado explícitamente: `Capability`, `CompositionPattern`, `MCPTool`, `Approval` como entidad separada de `Gate`. THREATS.md hizo visible que el `xdd-mcp-server` (Sprint 6) requiere whitelist explícita de paths — algo que el plan no detallaba.
**Causa raíz:** Documentar el dominio formalmente fuerza completitud que la planificación táctica omite.
**Lección:** Hacer DOMAIN + THREATS de cualquier proyecto antes de Build no es opcional: descubre entidades y mitigaciones que después serían costosas de retrofitear.
**Aplica a:** Cualquier proyecto X-DD en Fase 2-Spec. Confirma valor de Constitución Art. 4.

### [DEVOPS] Makefile como capa de UX uniforme antes de un CLI completo — 2026-05-26
**Contexto:** Decisión de no consolidar scripts en `xdd` CLI Python aún ([ADR-0008](docs/adr/0008-consolidacion-xdd-cli-diferida.md)).
**Problema:** Sin consolidación, 4+ scripts shell ofrecen UX heterogénea — el usuario necesita recordar nombres distintos.
**Causa raíz:** Diferir refactor no implica aceptar mala UX.
**Lección:** Un Makefile con targets bien nombrados (`make doctor|start|init|lint|test`) ofrece la UX uniforme que un CLI daría, sin el coste de reescribir. Ganamos tiempo manteniendo la calidad de uso.
**Aplica a:** Cualquier conjunto de scripts shell antes de consolidación en CLI. Patrón reutilizable.

### [PROCESO] El gate "APROBADO" como string es seguridad de teatro — 2026-05-26
**Contexto:** Diseñando el gate keeper del Sprint 4 según Tarea 2.2 de MEJORAS-X-DD.md v1.1.
**Problema:** El plan original proponía escribir literal `"APROBADO"` en `.xdd/<fase>/.status`. Ese archivo es trivialmente editable; cualquiera (humano o agente) puede aprobar fases sin enforcement real.
**Causa raíz:** Confundir "convención" con "control". Una vez que el gate keeper existe como código, los stakeholders asumen integridad — pero un string plano no la ofrece.
**Lección:** Cualquier "gate" o "approval" en un sistema agéntico requiere mecanismo criptográfico de integridad (HMAC mínimo). Si la decisión vive en un archivo de texto, debe firmarse contra una clave fuera del control del agente.
**Aplica a:** Cualquier mecanismo de aprobación en X-DD, en proyectos generados por X-DD y en general en frameworks de proceso para sistemas IA. Materializado en [ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md).

### [ARQUITECTURA] "MCP preferido" sin server propio es solo discurso — 2026-05-26
**Contexto:** Revisión de la sección 0.1 del plan v1.1 ("MCP es la vía preferida de integración").
**Problema:** El plan declaraba MCP como preferido pero solo consumía el server de MemPalace; no exponía X-DD vía MCP. Sin server propio, cada IDE nuevo necesitaba su adapter dedicado (9 adapters).
**Causa raíz:** Hueco entre intención declarada y mecanismo implementado.
**Lección:** Si un sistema declara un protocolo como preferido, debe ofrecerlo, no solo consumirlo. Auditar siempre la coherencia entre declaraciones de arquitectura y el código que las implementa.
**Aplica a:** Toda decisión de protocolo/estándar en X-DD. Materializado en [ADR-0005](docs/adr/0005-mcp-preferido-y-server-propio.md).

### [PROCESO] Mini-ciclos X-DD por sprint generan más burocracia que valor — 2026-05-26
**Contexto:** Decidiendo cómo aplicar X-DD a la implementación de MEJORAS.
**Problema:** La opción de "cada sprint = ciclo X-DD completo" (8 sprints × 6 fases = 48 SPEC/PLAN/QA) habría producido decenas de artefactos duplicados sin valor incremental.
**Causa raíz:** Confundir "más X-DD" con "mejor X-DD". La Constitución Art. 9 prohíbe agregar fases, pero no exige multiplicarlas innecesariamente.
**Lección:** Para releases de tamaño medio (≤8 sprints), una sola pasada por las 6 fases es coherente y suficiente. El dogfooding gana por calidad de artefactos, no por cantidad.
**Aplica a:** Cualquier planificación con X-DD sobre un release. Materializado en [ADR-0000](docs/adr/0000-mapeo-mejoras-pipeline-xdd.md).

### [DOMINIO] Confusión de ownership cuando una dep externa se presenta como interna — 2026-05-26
**Contexto:** README anterior describía MemPalace como "pieza del ecosistema X-DD".
**Problema:** Lectores asumían que MemPalace era parte de X-DD; expectativa errónea de soporte, ownership y roadmap unificado.
**Causa raíz:** Lenguaje impreciso sobre límites de sistema. Falta de `DEPENDENCIES.md` explícito.
**Lección:** Cualquier dependencia externa relevante debe declararse en `DEPENDENCIES.md` con versión, licencia, repo y rol. La descripción en README debe usar "integra" o "consume", no "incluye".
**Aplica a:** Todas las deps externas de X-DD y proyectos generados. Materializado en [ADR-0004](docs/adr/0004-mempalace-dep-externa-no-fork.md). Acción en Sprint 1.

### [HERRAMIENTAS] El número de scripts dispersos es señal pero no urgencia — 2026-05-26
**Contexto:** Discusión sobre consolidar 6-8 scripts en `xdd` CLI Python único.
**Problema:** Tentación de "limpiar todo de una vez" reescribiendo todo en Click/Typer ahora.
**Causa raíz:** Sesgo de orden — la dispersión es visible, la consolidación es satisfactoria, pero no agrega valor demostrable a usuarios v0.1.0.
**Lección:** Diferir consolidaciones puramente estéticas hasta tener señal de demanda real (issues de usuarios externos). Un `Makefile` es suficiente para uniformar UX sin reescribir.
**Aplica a:** Decisiones de refactor en X-DD. Materializado en [ADR-0008](docs/adr/0008-consolidacion-xdd-cli-diferida.md).

### [PROCESO] Una autoevaluación de release que dice "0 issues" es una señal de alarma, no de calidad — 2026-05-30
**Contexto:** v0.1.0 ya tag-eada. Revisión crítica externa post-release de release-state + calidad de código.
**Problema:** La QA previa marcó "0 issues / clean bill of health". La revisión encontró 2 bugs reales: `xdd-gate._validate_phase` crasheaba con `ValueError` ante un `.approvers` malformado, y `xdd-orchestrate.main()` parseaba argv dos veces. Además, el claim "VERSION = fuente única" eran 25 literales sincronizados por un test.
**Causa raíz:** La autoevaluación validó *presencia* de gates/tests/docs (que existían y eran buenos) pero no *ejecutó las rutas de error* ni desafió sus propios claims. Sesgo de confirmación: revisar el propio trabajo buscando confirmarlo.
**Lección:** (1) Ninguna release está "impecable"; un informe sin hallazgos indica revisión superficial, no código perfecto. (2) Un framework de gates que crashea parseando su propio artefacto contradice su tesis — los caminos de error del núcleo deben tener tests negativos explícitos, no solo happy-path. (3) Los claims de arquitectura ("single source of truth") deben verificarse contra el mecanismo real, no contra la intención. (4) La revisión crítica vale más cuando la hace un agente distinto al que produjo el trabajo (separación autor/aprobador, ya consagrada en el gate HMAC — extenderla al QA).
**Aplica a:** Todo `/cierre-fase` y QA de release en X-DD y proyectos generados. Antes de declarar release: ejecutar rutas de error del núcleo, desafiar cada claim de arquitectura, y preferir revisor ≠ autor. Materializado en v0.1.1 (release de hardening).

### [SEGURIDAD] Un regex de seguridad sin test negativo puede no detectar nada — 2026-05-30
**Contexto:** Al conectar el flujo de hooks (post-v0.1.1), se materializó por primera vez `pre:bash:dangerous-command` en Claude Code. Recién entonces se ejecutó de verdad.
**Problema:** El patrón anti fork-bomb `:(){.*}` **no detectaba la fork bomb canónica** `:(){ :|:& };:`. En ERE, `()` es un grupo de captura vacío y `{` inicia un cuantificador inválido → el patrón nunca matcheaba la amenaza que decía cubrir. (Bug gemelo: `>\s*/dev/...` usaba `\s`, no portable en ERE POSIX.) El hook llevaba ~5 sprints dando falsa sensación de protección.
**Causa raíz:** El test del hook (`hooks.bats`) sólo cubría casos que SÍ debían bloquear y que SÍ matcheaban (rm -rf, curl|sh). No había caso para la fork bomb ni un caso negativo (función bash benigna que NO debe bloquear). Regla de seguridad nunca ejercida = regla que no existe. Además el hook estaba definido pero no materializado ([[xdd-hooks-ssot-disconnect]]), así que jamás corría.
**Lección:** (1) Toda regla de detección de seguridad necesita **dos** tests: un positivo (la amenaza real se bloquea) y un negativo (un caso parecido benigno NO se bloquea). (2) Desconfiar de regex con metacaracteres sin escapar (`()`, `{}`, `\s`) en ERE — verificarlos contra el payload real, no asumir. (3) Un control de seguridad que nunca se ejecutó (porque el SSoT no se materializaba) es indistinguible de uno ausente. Mismo patrón frágil que [[xdd-content-checks-fragile]].
**Aplica a:** Todos los patrones de `pre-bash-dangerous-command.sh` y cualquier regla de detección (AgentShield, gates de contenido). Fix + tests de regresión (base64 para no exponer el payload) en branch `fix/forkbomb-regex`.

### [HERRAMIENTAS] Hooks globales necesitan guarda "repo-fuente vs proyecto consumidor" — 2026-05-30
**Contexto:** Tras materializar los hooks en `~/.claude/settings.json` (global), corrieron sobre el propio repo-fuente X-DD al editar archivos.
**Problema:** Dos hooks asumían "proyecto consumidor" y dañaban el repo-fuente: (1) `post:write:auto-organize` añadió `prompts/ scripts/ templates/ INSTALL.md` a `.gitignore` — esos dirs SON el código versionado del fuente, no copias; de commitearse, git dejaría de trackear el código. (2) `post:edit:mempalace-index` habría minado cualquier repo (ya tenía guarda añadida). Además, el patrón `rm -[fF] /` bloqueaba `rm -f /tmp/x` (cualquier ruta absoluta), falso positivo.
**Causa raíz:** Hooks escritos para el caso "X-DD instalado en proyecto destino" sin considerar que el settings GLOBAL los activa también en el repo-fuente (y en todos los demás repos). Reglas declarativas (`gitignore_framework_copies`) correctas para consumidor, destructivas para fuente.
**Lección:** (1) Todo hook global debe tener una guarda de contexto: detectar si `$PWD` es repo X-DD / repo-fuente / proyecto ajeno, y no-op donde no aplica. Marcador del fuente: `agent.yaml` con `name: x-dd` + `templates/`. (2) Patrones de path peligroso deben distinguir raíz/dirs-de-sistema de rutas profundas legítimas (`rm -rf /` y `/etc` sí; `/tmp/x` no). (3) Un hook destructivo sobre `.gitignore` es especialmente peligroso porque su daño es silencioso (deja de trackear, no borra).
**Aplica a:** Todos los hooks PostToolUse materializados globalmente. Guardas + tests en `hooks.bats`. Relacionado [[xdd-hooks-ssot-disconnect]].

### [DEVOPS] Empaquetar solo scripts/ en el wheel pipx dejó manifests/VERSION fuera → version stale y perfiles rotos — 2026-06-02
**Contexto:** X-DD v0.2.0 distribuido vía pipx. El comando `xdd` reportaba `0.1.0-dev` y `xdd init --list-profiles` imprimía "manifest no disponible" aunque pipx decía `x-dd 0.2.0`.
**Problema:** `pyproject.toml` solo empaquetaba `scripts/` en el wheel (`force-include`). Los scripts bash calculan `XDD_ROOT` como `dirname(BASH_SOURCE)/../`, que en pipx apunta a `xdd_cli/` (directorio del paquete instalado), donde `../VERSION` y `../manifests/` no existen. Resultado: fallback `"0.1.0-dev"` en VERSION y "manifest no disponible" en list-profiles.
**Causa raíz:** El pattern "empaquetar solo el código ejecutable" funciona para proyectos Python puros. X-DD es un framework data-heavy: sus scripts bash consumen manifests/, templates/, .agent/hooks/, skills/ y VERSION como "source of truth". Si esos dirs no están en el wheel, la instalación pip es funcionalmente incompleta aunque el metadata diga la versión correcta.
**Lección:** (1) Cualquier framework con data dirs versionados (manifests, templates, prompts, skills) DEBE incluirlos explícitamente en `pyproject.toml` (`force-include` en hatchling o `package_data` en setuptools). (2) Añadir `_data_dir()` en el entry-point Python con la misma lógica de 3 niveles (env var > editable > bundled) e inyectarla como `XDD_DATA_DIR` al env de scripts bash invocados. (3) Verificar tras cada nueva versión: `xdd --version` debe coincidir con `VERSION`, y `xdd init --list-profiles` debe listar perfiles reales. (4) Criterio de DoD para pyproject.toml: `python -c "from xdd_cli import _data_dir; assert (_data_dir()/'manifests').is_dir()"` verde en instalación pip.
**Aplica a:** pyproject.toml, src/xdd_cli/__init__.py, todos los scripts bash con `XDD_ROOT`. Patrón reusable para Evol-DD y cualquier framework similar.

### [HERRAMIENTAS] Deps externas opt-in deben seguir patrón GitNexus: env var + guard + doctor — 2026-06-03
**Contexto:** Al integrar `agent-browser` (CLI Rust de vercel-labs) como skill nativa de X-DD, la primera versión del workflow asumía que el CLI estaba instalado y fallaba sin mensaje claro si no lo estaba.
**Problema:** Dep externa requerida sin opt-in explícito = fricción silenciosa. Usuarios sin `agent-browser` instalado recibían error críptico del shell, no un mensaje accionable. Además, X-DD ya tenía un patrón establecido (GitNexus: `XDD_GITNEXUS=1`) que no se aplicó por defecto.
**Causa raíz:** Se creó la skill documentando "instalar si no disponible" en Prerrequisitos, pero sin guard de runtime ni detección en `xdd-doctor.sh`. El patrón GitNexus existía pero no se buscó activamente antes de diseñar el workflow.
**Lección:** Toda dep externa opt-in en X-DD sigue este protocolo: (1) env var `XDD_<TOOL>=1` para activar; (2) guard al inicio del workflow (abort limpio si OFF, error accionable si CLI faltante); (3) detección en `xdd-doctor.sh` con status en texto y JSON; (4) documentar en SKILL.md como "opt-in igual que GitNexus". Antes de integrar cualquier dep nueva, buscar si ya hay patrón establecido en el framework.
**Aplica a:** Cualquier integración de herramienta externa en X-DD (IDEs, CLIs, servidores MCP). Patrón: `XDD_<TOOL>=1` → guard → doctor → SKILL.md documenta opt-in.

### [ARQUITECTURA] Skills nativas NO son wrappers — lógica completa en SKILL.md, integración en workflows existentes — 2026-06-03
**Contexto:** Al integrar 5 skills externas (grill-me, fact-check, idea-refine, prompt-master, agent-browser), la primera pregunta fue si invocarlas vía API/CLI externos o hacerlas nativas.
**Problema:** Wrappers que llaman al original crean dependencia de red, versionado externo y posibles incompatibilidades de schema. Además, el valor de X-DD es integrar al pipeline gated, no delegar a terceros.
**Causa raíz:** Tentación de reusar código externo directamente en lugar de abstraer el concepto y reimplementar en el idioma del framework.
**Lección:** Al ingestar una skill/herramienta externa en X-DD: (1) leer el original completo, extraer el concepto/protocolo; (2) reimplementar en SKILL.md con lógica X-DD nativa (integración con gates, agents, memoria, DOC_STANDARD); (3) documentar atribución en NOTICE + frontmatter `inspired_by`; (4) conectar a workflows existentes (desde y hacia). El resultado debe ser indistinguible de una skill creada internamente. El usuario no necesita conocer el original para usar la skill.
**Aplica a:** Cualquier ingesta de skill/workflow/herramienta externa al ecosystem X-DD. Ver skills xdd-grill-me, xdd-fact-check, xdd-idea-refine, xdd-prompt-master, xdd-agent-browser como referencia.

### [PROCESO] El estándar de docs no se propaga solo — materializar en SSoT + puntos de generación + gate de QA — 2026-06-02
**Contexto:** X-DD tenía política "0% emoji" en el workflow `/technical-documentation` y prompts fuertes de DDD/STRIDE/Gherkin, pero el nivel de detalle variaba por workflow y el agente technical-writer tenía emojis en su propio frontmatter.
**Problema:** El estándar vivía en comentarios de workflows individuales, no en un documento único. Cada workflow especificaba su propio nivel de detalle (algunos altamente prescriptivos, otros vagos). Faltaban templates para SPEC/DOMAIN/THREATS/FEATURES. El agente `engineering-technical-writer` no tenía las reglas hard-coded en su prompt.
**Causa raíz:** "Política implícita" vs. "ley explícita". Un estándar que no está en un documento referenciable por todos los actores (agentes, workflows, gate) no existe operativamente; cada actor lo interpreta diferente.
**Lección:** (1) Todo estándar de calidad necesita una SSoT (en este caso `docs/DOC_STANDARD.md`) referenciada explícitamente desde TODOS los puntos de generación: agente, workflows, templates, gate QA. (2) Las reglas deben estar hard-coded en el prompt del agente que las ejecuta, no solo en el workflow que lo invoca. (3) El gate QA (Tier 1) debe tener un chequeo automatizado verificable (grep de emojis, presencia de bloque Mermaid). (4) Los templates con secciones mínimas y Definition of Done por artefacto son el mecanismo más efectivo de enforcement: el agente no puede "olvidar" una sección si el template la requiere.
**Aplica a:** Cualquier estándar de calidad en X-DD y proyectos generados. Patrón: SSoT → propagación masiva → gate automático → template con DoD.

### [SEGURIDAD] Gate bloqueante real = guards FSM (cadena + segregacion), no solo firma — 2026-06-04
**Contexto:** Replicar el flujo estrictamente bloqueante del sistema de un tercero (FSM formal con guards): ninguna fase se salta, autor no aprueba su propio trabajo
**Problema:** El gate X-DD firmaba HMAC y validaba artefactos, pero approve de una fase funcionaba aunque las previas nunca se aprobaran. El orden adyacente solo se chequeaba en transition, no en approve. Separacion autor/aprobador estaba sugerida pero no enforced
**Causa raiz:** Gate disenado como validador por-fase aislado, no como maquina de estados con cadena. Faltaba registrar el autor del artefacto para poder comparar contra el aprobador
**Leccion:** Un pipeline estrictamente bloqueante necesita 2 guards en approve, no solo firma: (1) CADENA — verificar que todas las fases previas esten APROBADO+validas (reusar el validador existente); (2) SEGREGACION — registrar autor (set-author escribe .author) y bloquear si approver==author. Ambos con escape hatch env var documentado (XDD_SKIP_CHAIN, XDD_SKIP_SEGREGATION) para dev-solo. Es el patron worker->auditor a nivel de fase: quien produce no aprueba
**Aplica a:** xdd-gate.py cmd_approve. Heredar a evol-gate.py (Inc 2). Patron reusable para cualquier gate de pipeline multi-fase
**Fix aplicado:** _enforce_phase_chain + _enforce_segregation + cmd_set_author en xdd-gate.py. status muestra autor/aprobador/cadena. 9 tests en test_gate_fsm.py

### [HERRAMIENTAS] argparse global args deben ir ANTES del subcomando — CLI confusa si no — 2026-06-04
**Contexto:** Inc 5 — nuevo subcomando `sprint-close` en xdd-memory.py. Argumentos globales definidos antes del subparser (--project, --json).
**Problema:** `xdd-memory.py sprint-close --sprint=01 --project=.` falla con "unrecognized arguments: --project=.". El arg global debe ir ANTES del subcomando: `xdd-memory.py --project=. sprint-close --sprint=01`.
**Causa raiz:** argparse procesa subcomandos secuencialmente — args definidos en el parser principal no se heredan al namespace del subparser si se pasan despues del subcomando.
**Leccion:** En CLIs con subcomandos argparse: documentar en help que args globales van ANTES del subcomando. Considerar add_help_on_each_subparser o parents=[common_parser] para propagar. Tests que usan la funcion directamente no detectan este bug — necesitan tambien probar via subprocess o argv.
**Aplica a:** xdd-memory.py, xdd-gate.py, cualquier CLI con argparse + subparsers en X-DD. Fix: añadir nota en --help y considerar add_subparsers(parser_class) con parents comunes.

### [PROCESO] Memoria/lecciones monoliticas escalan mal — separar por sprint desde inicio — 2026-06-04
**Contexto:** Inc 5 — el usuario noto que memoria.md y lecciones.md eran archivos monoliticos que crecian sin estructura temporal. El sistema xdd-memory.py ya tenia el patron MEMORY.md + memory/YYYY-MM-DD.md pero no se aplicaba a lecciones del proyecto.
**Problema:** Un solo archivo lecciones.md con 300+ lineas hace imposible buscar por sprint, correlacionar con errores especificos, o comparar velocidad de aprendizaje entre sprints. Mismo problema con memoria.md.
**Causa raiz:** Patron de journal diario existia para memoria conversacional (xdd-memory.py) pero no se extrapoló a los artefactos de proyecto hasta que el relato del sistema externo lo hizo explicito.
**Leccion:** Desde el inicio de un proyecto: lecciones y memoria separadas por sprint (acuerdos/lecciones/sprint-NN.md, acuerdos/memoria/sprint-NN.md). MEMORY.md para hechos persistentes. INDEX.md como indice navegable. El mismo patron del journal diario aplicado a granularidad de sprint. Backward compat: mantener root lecciones.md/memoria.md hasta migracion completa.
**Aplica a:** Todos los proyectos generados por X-DD via xdd-init.sh. xdd-memory.py sprint-close es el comando de cierre. cierre-fase v1.4 lo integra.

### [DOMINIO] Briefing como arbol bloqueante 16D — wireframes viven DENTRO del briefing, no en fase separada — 2026-06-04
**Contexto:** Inc 3 — modelar el briefing inspirado en sistema externo donde 43 docs granulares emergen de un briefing exhaustivo. El diseño inicial de X-DD tenia wireframes como etapa post-briefing.
**Problema:** Separar wireframes del briefing crea un gap temporal: el agente de build puede arrancar sin tener claro el diseno visual, generando componentes que luego rompen al aprobar los wireframes.
**Causa raiz:** Wireframes vistos como "documentacion de diseno" separada de la "definicion del producto". En realidad son el acuerdo mas tangible del briefing — sin ellos el briefing no esta cerrado.
**Leccion:** Wireframes son Dimension 16 del briefing (no etapa posterior). El briefing cierra SOLO cuando todas las 16 dimensiones tienen respuesta Y cada pantalla tiene HTML aprobado con tokens reales de D15. El HTML aprobado es la regla de diseno inmutable para el agente de build. Secuencia correcta: D15 (Design System → tokens) → D16 (wireframes con esos tokens) → gate cierre → doc-granular.
**Aplica a:** .agent/workflows/briefing.md y cualquier proyecto generado con X-DD. El artefacto acuerdos/wireframes/<pantalla>.html es prerequisito de build (validado por _validate_phase).

### [ARQUITECTURA] Gate checksum no debe incluir sus propios metarchivos — circular y no semantico — 2026-06-04
**Contexto:** Al ejecutar cierre-fase post-Inc 3+4, el gate validate reporto checksum mismatch en build aunque la fase estaba APROBADO. Investigacion revelo que el checksum de .xdd/build/ incluia .approvers, .checksums, .signature — archivos que el propio gate modifica al aprobar.
**Problema:** Cada `approve` modifica .approvers (append) y recalcula .checksums y .signature → el checksum almacenado queda invalido en la proxima validacion. Mismatch permanente e irreparable sin re-aprobar.
**Causa raiz:** La funcion `checksum(path)` para directorios usaba `rglob("*")` sin filtrar metarchivos del gate. Diseno correcto: el checksum debe cubrir el CONTENIDO semantico (artefactos del proyecto), no los metadatos del gate mismo.
**Leccion:** La funcion checksum de directorio debe excluir explicitamente los metarchivos del gate: .status, .checksums, .signature, .approvers, .author. Son metadatos de gobernanza, no artefactos verificables. Fix: `_GATE_META = {".status", ".checksums", ".signature", ".approvers", ".author"}` y filtrar en `rglob`.
**Aplica a:** scripts/xdd-gate.py funcion `checksum()`. Heredar fix a evol-gate.py si usa mismo patron. Verificar en test: approve multiple veces sobre misma fase no debe invalidar checksum.

### [PROCESO] doc-granular worker→auditor — N docs decididos por proyecto, no por plantilla — 2026-06-04
**Contexto:** Inc 4 — implementar el patron de documentacion granular inspirado en sistema externo (43 docs en proyecto mediano, 93 en complejo). Primera propuesta fue una lista fija de dominios.
**Problema:** Lista fija subrepresenta proyectos complejos y sobredocumenta proyectos simples. El sistema de referencia tenia el agente decidiendo el numero y granularidad de docs segun complejidad real del proyecto, no segun una plantilla.
**Causa raiz:** Tentacion de dar estructura predecible vs. dejar al agente razonar sobre la complejidad real. La plantilla fija es mas controlable pero introduce evaluacion implicita ("esto no necesita doc propio") que X-DD rechaza.
**Leccion:** Principio cero deuda tecnica aplicado a docs: "si es un dominio tecnico del proyecto, tiene doc". Sin evaluacion, sin "esto es obvio", sin limite de numero. El agente analiza TODOS los artefactos del briefing e identifica dominios con criterio: ¿hay suficiente complejidad para que un sub-agente necesite este doc como referencia independiente? El numero emerge del proyecto. Proyectos simples: 15-20 docs. Complejos: 50-100+.
**Aplica a:** .agent/workflows/doc-granular.md y cualquier instancia del patron. El INDEX.md lo genera el agente tras analizar el briefing completo — no viene de una lista predefinida.

### [HERRAMIENTAS] sed no maneja emojis Unicode multibyte — usar Python — 2026-06-04
**Contexto:** Purga masiva emojis en 52 docs/ de X-DD.
**Problema:** sed falla con "expresion sin terminar" para emojis ZWJ (✅, ⚠️). Caracter FE0F rompe el parser.
**Causa raiz:** sed procesa bytes, no codepoints. Emojis con variacion FE0F son multibyte; sed interpreta FE0F como delimitador regex.
**Leccion:** Para operaciones masivas Unicode: Python con `re.compile(pattern, re.UNICODE)`. sed solo para ASCII puro.
**Aplica a:** Cualquier purga de caracteres Unicode en X-DD y proyectos generados.

### [ARQUITECTURA] Atomicidad != granularidad — dimensiones ortogonales de calidad documental — 2026-06-04
**Contexto:** Discusion sobre nivel de detalle en docs generados por X-DD.
**Problema:** X-DD usaba "granularidad" como criterio pero la metrica correcta es "atomicidad": 1 doc = 1 unidad semantica indivisible.
**Causa raiz:** Granularidad = profundidad dentro del doc. Atomicidad = cohesion del scope. X-DD_Integration_Guide.md viola atomicidad al mezclar 9 disciplinas en 1 doc.
**Leccion:** 1 doc = 1 dominio tecnico, sin mezclar responsabilidades. X-DD_Integration_Guide.md debe dividirse en 9 docs (SDD.md, FDD.md, DDD.md...). Tambien aplica a workflows: 1 workflow = 1 operacion.
**Aplica a:** doc-granular workflow, DOC_STANDARD.md, discipline-check.

### [PROCESO] Docs del framework vs docs del proyecto — scope distinto — 2026-06-04
**Contexto:** Audit buscando FUNCIONALES.md en X-DD.
**Problema:** FUNCIONALES.md es artefacto generado POR X-DD para proyectos, no del framework mismo.
**Causa raiz:** X-DD tiene dos niveles: (1) docs del framework (constitucion, GATE, ARQUITECTURA) y (2) artefactos generados (SPEC.md, DOMAIN.md, FUNCIONALES.md).
**Leccion:** Distinguir nivel framework (docs/) vs nivel proyecto (acuerdos/proyecto/). Checklist de auditoria debe especificar el nivel objetivo.
**Aplica a:** Futuras auditorias de X-DD y evol-dd.
