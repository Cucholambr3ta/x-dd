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
