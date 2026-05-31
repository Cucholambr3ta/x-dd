# CHANGELOG técnico — X-DD

> Historia técnica del repositorio. Mantenida por `/xdd-trace` (cierre de sprint) y `/release-cut` (release).
> Formato basado en [Keep a Changelog](https://keepachangelog.com).
>
> Para release notes user-facing ver [RELEASES/](../RELEASES/) (a partir de v0.1.0).

---

## [Unreleased] — main

## [0.1.2] — 2026-05-30

> Reconexión del flujo de auto-update (hooks) + endurecimiento de hooks.
> Notas user-facing en [RELEASES/v0.1.2.md](../RELEASES/v0.1.2.md).

### Added
- **Materializador de hooks** (`scripts/xdd-hooks-install.py`, `xdd hooks`): traduce
  `.agent/hooks/hooks.json` (SSoT) → `~/.claude/settings.json`. Cierra el gap donde
  los hooks estaban definidos y validados pero **nunca se ejecutaban** (Claude Code
  lee settings.json, no hooks.json). Merge no-destructivo, filtra por perfil, marca
  los propios con `_xdd_id`. Subcomandos install/sync/status + --dry-run + --project.
- **GitNexus auto-update** en `scripts/hooks/post-commit` (antes sólo MemPalace; no
  tenía automatización).
- `xdd-doctor`: sección **[Hooks / auto-update]** (post-commit activo + hooks materializados).

### Changed
- `xdd-init` instala el git post-commit (antes sólo `xdd-start`) y materializa hooks.
- Lock MemPalace: `flock -n` skip-if-running en hooks (palace global único) → elimina
  el error "palace held by PID" con mines concurrentes.

### Fixed
- **Seguridad — patrón anti fork-bomb roto**: `:(){.*}` no detectaba `:(){ :|:& };:`
  (en ERE `()` = grupo vacío, `{` = cuantificador inválido). Reemplazado por la firma
  real; `\s`→`[[:space:]]`. ~5 sprints de falsa protección.
- **Falso positivo `rm`**: el patrón bloqueaba cualquier ruta absoluta tras `rm -f`
  (p.ej. `rm -f /tmp/x`). Refinado a raíz + dirs de sistema + `~`.
- **Guarda repo-fuente**: `post:write:auto-organize` y `post:edit:mempalace-index`
  no-op fuera de un repo X-DD / en el repo-fuente (el settings global los activaba en
  todos los repos; auto-organize llegaba a gitignorear código versionado del fuente).

### Tests
- `test_hooks_install.py` (12) + `test_manifests.test_hooks_materializables` cierran el
  gap "schema-válido ≠ ejecutándose". `hooks.bats` 20 casos (positivos + negativos,
  payloads en base64). Total: 306 pytest.

## [0.1.1] — 2026-05-30

> Release de hardening. Notas user-facing en [RELEASES/v0.1.1.md](../RELEASES/v0.1.1.md).

### Fixed
- **xdd-orchestrate**: `main()` parseaba `argv` dos veces (`build_parser()` invocado 2×).
  Ahora parsea una sola vez y despacha al `func` resultante.
- **xdd-gate**: `_validate_phase()` lanzaba `ValueError` no capturado cuando la última
  línea de `.approvers` no contenía el separador ` | `. Ahora reporta el artefacto como
  malformado y devuelve `(False, errors)` sin crashear (camino de seguridad del gate).

### Changed
- **DRY versión + timestamp** (`scripts/_xdd_common.py`, nuevo): `read_version()` resuelve
  la versión en orden VERSION → metadata del paquete → fallback literal. Los 24 scripts y
  `src/xdd_cli/__init__.py` dejan de hardcodear `__version__`. `utcnow_iso()` (precisión de
  segundo) y `utcnow_iso_us()` (microsegundo) centralizan los 14 timestamps duplicados; se
  preserva la precisión por call-site (gate firma a segundo → HMAC intacto).
- **xdd-otel / xdd-frozen-transfer / xdd-authz**: `except Exception:` silenciosos
  reemplazados por capturas concretas (`json.JSONDecodeError`/`OSError`/`yaml.YAMLError`/
  `KeyError`) con comentario del porqué.

### Removed
- Import muerto `subprocess` en `scripts/xdd-orchestrate.py`.

### Tests
- `test_gate.py`: `.approvers` malformado no lanza excepción.
- `test_orchestrate.py`: `main()` construye el parser una sola vez (regresión).
- `test_version_consistency.py`: valida fallbacks literales contra VERSION (modelo nuevo).
- Total: 293 pytest (+7) verdes; 141 bats; AgentShield 0 findings ≥ high.

## [0.1.0] — 2026-05-30

> Primer release público. Notas user-facing en [RELEASES/v0.1.0.md](../RELEASES/v0.1.0.md).
> Incluye: gated pipeline 6 fases + gate HMAC, gate ejecutable de flujos (xdd-flow),
> MockProvider determinista (xdd-provider), pip-installable + comando `xdd` (pipx),
> adapters en código (módulo aditivo), deprecación de MCP (borrado v0.2.0), VERSION
> única, 7 IDEs, 180 agentes.

### Added — Codex adapter (2026-05-28) — 7° IDE — PR #40 + ADR-0036
- **`scripts/xdd-adapt.sh adapt_codex()`** — genera `~/.codex/skills/<trigger>-orchestrator/` (SKILL.md frontmatter MINIMAL name+description + references/agents-index.json 180 entries lowercase-normalized + workflows-index.md + constitution + invoke_workflow.sh helper).
- **6 X-DD skills copiadas** a `~/.codex/skills/` (compat directo: xdd-talk-compact + agent-eval + xdd-ai-review + xdd-compact + xdd-fs-context + xdd-sandbox).
- **Project-level `<DEST>/.codex/README-xdd.md`** referencia dónde vive realmente.
- **Auto-detect xdd-init:** `command -v codex` OR `~/.codex/` dir.
- **Override env:** `XDD_CODEX_HOME=/path`.
- **Pattern respetado per guía Codex:** 1 orchestrator + agents-index (NO N skills individuales). Frontmatter minimal.
- **`docs/adr/0036-codex-adapter-global-skills.md`**.

### Fixed — install manifests Sprints 13-25 (2026-05-28) — PR #39
- **`manifests/install-modules.json`** + **`install-profiles.json`** — 10 módulos nuevos (personas, skills-core, mcp-server-global, workspace-monorepo, observability, governance-runtime, ahe-evolve, protocols, router, pentest).
- **Bug raíz:** manifests no actualizados durante Sprints 13-25 → projects perdían 18 scripts + 6 skills + 4 personas + registry.
- **Stats install:** core 13→43 paths, full 25→70 paths, 0 gaps post-fix.

### Fixed — install docs-governance + AGENTS.md template (2026-05-28) — PR #38
- **Módulo docs-governance nuevo** (8 files): docs/constitucion.md + X-DD_Integration_Guide + RETROFIT_GUIDE + HOOKS + CONFIG + INSTALL_PROFILES + INSTALL + AGENTS.
- **core extendido** con docs/constitucion.md + AGENTS.md.
- **AGENTS.md template** (mirror CLAUDE.md rebrandeado OpenCode) — governance manifest.
- **`adapt_opencode` fix:** AGENTS.md SKIP si existe (preserva governance custom) + COPY desde X-DD root si no. Registry 180 agentes movido a `docs/equipo.md` (separación ley vs directorio).

### Added — VSCode tasks.json + settings.json (2026-05-27) — PR #37
- **`adapt_vscode_copilot`** amplía a 4 archivos (vs 2 antes): + `.vscode/tasks.json` (4 tasks: doctor/start/list/gate) + `.vscode/settings.json` (env vars terminal ANTHROPIC/OPENAI).
- **SKIP si existing** (no overwrite proyecto).
- **`docs/INSTALL_VSCODE.md`** reescrito limpio: corrige errors doc previo (mempalace = pip no npm, xdd-skill-invoke CLI inexistente).
- **`.gitignore`** añade `.claude/skills/` (gitnexus auto-config).

### Added — Sprint 25 Global install architecture (2026-05-27) — PR #36 + ADR-0035
- **`scripts/xdd-mcp-install-global.sh`** — genera `~/.local/bin/xdd-mcp-server` con PYTHONPATH baked al X-DD root. Comandos: install / `--check` / `--uninstall` / `--bin-dir=` / `--xdd-root=`.
- **`xdd-mcp-server/tools.py` refactor:** `get_workflows_dir(project_root)` + `get_registry_path()` local-first + global fallback. `get_xdd_dir()` STRICTAMENTE local (T4.3, sin fallback). 4 tools acept `project_root` opcional. Schemas inputSchema añade field. Backwards compat constants retained.
- **`adapt_antigravity` refactor:** detecta wrapper global → MCP config SIN cwd (dinámico al workspace IDE). Fallback legacy cwd-fixed si no wrapper. Popula `.agents/skills/` (convención Antigravity plural).
- **Tests:** test_mcp_local_first.py 11 verde + xdd-mcp-install-global.bats 8 verde + 17/17 backwards compat.

### Fixed — Antigravity path real + scrub branding privado (2026-05-27) — PR #35
- **Antigravity path real descubierto:** `~/.gemini/config/mcp_config.json` (no `~/.antigravity/`). `adapt_antigravity` mergea formato `$typeName CascadePluginCommandTemplate`.
- **Scrub branding privado del repo público:** ejemplos `helios` → `helios` (marca canónica X-DD). Rutas absolutas host → `<workspace>` placeholder (Portabilidad Absoluta Art.).
- **`.claude/settings.json`** untracked + gitignored (era leak PR #34 con paths secrets).
- **`.agent/workflows/xdd-trace.md`:** "Legacy-PM" legacy → "X-DD-PM".

### Added — Sprint 24 Universal IDE adapter (2026-05-27) — PR #34 + ADR-0034
- **Root cause fix:** symlinks rechazados Claude Code/Copilot. `copy_real()` reemplaza `ln -sf`.
- **6 IDEs soportados:** claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity. Cada uno con MCP auto-config formato propio (`mcpServers` vs `servers`).
- **Auto-detect en xdd-init:** detecta IDEs presentes (CLI `command -v` o config dirs) y corre `xdd-adapt` por cada uno. Opt-out: `XDD_NO_ADAPT=1`.
- **Trigger resolution:** `--trigger` > branding `xdd.profile.yml` > `"xdd"` default. Rebrand cabecera command copiado.
- **15/15 bats verde** + ADR-0034 + `docs/IDE_SETUP.md` matriz honesta (limitación slash idéntico cross-IDE).


### Added — GitNexus tier-1 integration (2026-05-27) — PR #32
- **`scripts/xdd-doctor.sh`** — detect `gitnexus` CLI en sección Núcleo recomendado (paralelo a `mempalace`).
- **`scripts/xdd-start.sh`** — bloque idéntico a MemPalace: indexa GitNexus si CLI disponible (log `~/.gitnexus/index.log`), warn + continúa si falta.
- **`DEPENDENCIES.md`** — entrada GitNexus en Núcleo recomendado + disclaimer PolyForm Noncommercial 1.0.0.
- **`templates/xdd.profile.template.yml`** — capability nueva `code_intelligence: true` default.
- **`docs/MCP_INTEGRATION.md`** — sección "Stack MCP completo recomendado X-DD (3 servers)": xdd-mcp + MemPalace + GitNexus.
- **`README.md`** — diagrama integraciones externas incluye GitNexus + disclaimer license.
- **`agent.yaml`** — `mcp.companions` declara MemPalace + GitNexus tier-1; `dependencies.recommended` añade GitNexus.
- **`docs/adr/0033-gitnexus-tier1-companion.md`** — política integración + license analysis + alternativas + consecuencias.

### Added — Sprint 23 (2026-05-27) — Protocols + Skills ecosystem (PR #29)
- **`scripts/xdd-a2a.py`** — Google A2A Protocol compat stub: agent-card emisor + list-patterns + invoke + serve stub.
- **`scripts/xdd-agui.py`** — AG-UI event-driven streaming spec (6 event types validados).
- **`scripts/xdd-bundle.py`** — Web bundles MVP (ADR-0017 impl): pack/verify/install/inspect + HMAC signature + license whitelist.
- **`bundles/security-bundle.xddbundle`** — demo bundle empaquetando xdd-sandbox + xdd-ai-review + security agents.
- 2 composition_patterns nuevos en registry: `plan_and_act` (sequential gated) + `adapt_orch` (parallel adaptive).
- **`docs/SKILLS_INTEROP.md`** — mapping X-DD ↔ Microsoft Skills Framework + agents-best-practices.
- **`docs/research/agents-best-practices-integration.md`** — notas adopción patterns provider-neutral.
- ADRs 0030 A2A, 0031 AG-UI, 0032 Skills migration policy.
- Tests: 20 nuevos verde (test_protocols_bundle.py).

### Added — Sprint 22 (2026-05-27) — AHE-style /evolve refactor (PR #28)
- **`scripts/xdd-trace-summarize.py`** — Experience layer: 3 depths (summary/detail/full), comprime traces N-million → layered markdown.
- **`scripts/xdd-frozen-transfer.py`** — Component layer: experiments transferring skills source → target.
- **Refactor `cmd_evolve` (xdd-state.py)**: autopopula `rationale_evidence` + `predicted_impact` + `falsification_metric`.
- **Schema migration idempotente**: `_migrate_evolutions()` ALTER TABLE +4 cols AHE.
- **`docs/AHE_EVOLVE.md`** — flujo end-to-end + política T6.1.
- ADR-0029 AHE-style evolve 3-layer observability.
- Tests: 10 nuevos verde (test_ahe.py).

### Added — Sprint 21 (2026-05-27) — Sandbox + Permissions hardening (PR #27)
- **`scripts/xdd-intent.py`** — nah-style intent taxonomy (8 intents + severity classifier).
- **`scripts/xdd-authz.py`** — OAP-style deterministic authz <100ms (4 actions: allow/require_approval/mask/deny).
- **`skills/xdd-sandbox/SKILL.md`** — provider-agnostic sandbox (E2B/Daytona/Microsandbox/docker/none).
- **`.agent/hooks/scripts/pre-tool-authz.sh`** — hook PreToolUse que bloquea si authz deny.
- **`templates/constitution.template.yml`** — machine-readable adapter del constitution.md humano (AutoHarness-style).
- ADRs 0027 Sandbox provider abstraction, 0028 Permission model (intent + 5-layer + OAP).
- AutoHarness 6-step governance integrado via combinación de scripts.
- Tests: 20 nuevos verde (test_intent.py + test_authz.py).

### Added — Sprint 20 (2026-05-27) — Eval benchmarks externos + meta-eval (PR #26)
- **Graders nuevos en xdd-eval.py**: `inspect_ai_compat` (match/includes/regex) + `pass_at_one_external` (universal).
- **4 suite scaffolds en `evals/external/`**: terminal-bench-2, swe-bench-verified, promptfoo-compat, longmemeval.
- **`scripts/xdd-meta-eval.py`** — compare/trend/baseline (detecta regresión ciclo a ciclo, NexAU-AHE pattern).
- **`docs/EXTERNAL_BENCHMARKS.md`** — política integración + workflow.
- ADRs 0025 Inspect AI compatibility, 0026 External benchmark integration.
- Tests: 13 nuevos verde (test_eval_external.py).

### Added — Sprint 19 (2026-05-27) — Context Engineering Stack (PR #25)
- **`scripts/xdd-context.py`** — budget metering (estimate/check/budget), thresholds warn 80% / block 95%.
- **`.agent/hooks/scripts/pre-llm-budget.sh`** — hook PreToolUse para budget check.
- **`skills/xdd-compact/SKILL.md`** — provider-agnostic compaction (LLMLingua/Claude API/truncate/auto).
- **`skills/xdd-fs-context/SKILL.md`** — filesystem-paradigm context curation (3 modes).
- **`.agent/workflows/code-as-tool.md`** — pattern Code Execution with MCP (98%+ reducción tokens).
- ADRs 0023 Context budget policy, 0024 Compaction skill provider-agnostic.
- **`docs/CONTEXT_ENGINEERING.md`** — guía completa.
- Tests: 10 nuevos verde (test_context.py).

### Added — Sprint 18 (2026-05-27) — Observability Triad (PR #24)
- **`scripts/xdd-otel.py`** — OpenTelemetry Gen AI spans (span-start/end/emit/list/export). Compat OpenLLMetry/OpenInference.
- **`scripts/xdd-replay.py`** — session reconstruction (record/list/show/replay --step/diff).
- **`scripts/xdd-cost.py`** — per-call LLM cost tracker SQLite + 11 models pricing default.
- **6 nuevos event types en hooks.json**: before_agent / before_model / wrap_model_call / wrap_tool_call / after_model / after_agent (deepagents-style middleware).
- ADRs 0021 Observability stack + OTel + replay, 0022 Per-call cost tracking.
- **`docs/OBSERVABILITY.md`** — guía 3 herramientas + 6-stage middleware.
- Tests: 20 nuevos verde (test_otel.py + test_replay.py + test_cost.py).

### Added — Sprint 17 (2026-05-27) — Party + Brainstorm + HITL + Router + retry/cond (PR #23)
- **Party Mode** en xdd-orchestrate.py (pattern sin lead, participantes paralelos).
- **`.agent/workflows/brainstorm.md`** — workflow exploratorio invoca party.
- **`scripts/xdd-router.py`** — multi-provider router (5 task types × 4 providers + fallback chain).
- **HITL checkpoints** en composition_patterns (hitl_after/hitl_prompt/hitl_required).
- **maybe_retry + evaluate_conditional** helpers en orchestrate.
- ADRs 0016 Party Mode, 0017 Web bundles spec, 0018 HITL checkpoints, 0019 Multi-provider router.
- Tests: 16 nuevos verde (test_orchestrate.py +9, test_router.py +7).

### Added — Sprint 16 (2026-05-27) — SDD parity + AI review + community skills + TF-IDF (PR #22)
- **`.agent/workflows/clarify.md`** + **`.agent/workflows/cross-validate.md`** — SDD parity inspired Spec-Kit MIT.
- **`templates/constitution.template.md`** — 10 artículos per-project (governance YAML).
- **`skills/xdd-ai-review/SKILL.md`** — AI pre-commit review provider-agnostic (4 providers).
- **TF-IDF clustering refactor** de cmd_evolve en xdd-state.py (stdlib pure, no sklearn dep).
- ADRs 0014 SDD parity, 0015 AI pre-commit review, 0020 Community skills voting policy (7-day window).
- Tests: 6 nuevos verde TF-IDF (test_state.py).

### Added — Sprint 15 (2026-05-27) — Monorepo 3 modos (PR #21)
- **`scripts/xdd-monorepo.sh`** — detect 9 tools (nx/turborepo/pnpm/yarn/lerna/rush/bazel/cargo/go) + suggest mode.
- **3 modos**: `isolated` (cada package independiente), `shared` (un gate raíz), `hybrid` (meta-fases raíz + build/qa per-package).
- **`docs/MONOREPO.md`** — guía completa + tabla decisión.
- **Schema xdd.profile.yml**: añade sección `monorepo:`.
- **`docs/research/awesome-harness-engineering-analysis.md`** — research note (3 gaps OTel/context/replay → Sprint 18-19).
- ADR-0013 Monorepo 3 modos.
- Tests: 12 nuevos verde (xdd-monorepo.bats).

### Added — Sprint 14 (2026-05-27) — Workspace mode + Wizard (PR #20)
- **`scripts/xdd-wizard.sh`** — 7-step interactive bootstrap wizard.
- **Schema xdd.profile.yml**: añade sección `workspace:` (enabled, root, projects, shared_memory, shared_gate_key).
- **`docs/WORKSPACE.md`** — guía + tabla decisión.
- ADR-0012 Workspace mode + Wizard.
- Tests: 5 nuevos verde (xdd-wizard.bats).


### Added — Sprint 13 (2026-05-26) — White-labeling (branding + 4 personas + rename trigger)
- **`scripts/xdd-brand.sh`** — aplica white-labeling al destino. Lee sección
  `branding` de `xdd.profile.yml`, genera `.claude/commands/<trigger>.md`
  symlink, copia persona, escribe `.claude/branding.json`. Idempotente.
- **`prompts/orchestrator/personas/{technical,friendly,casual,formal}.md`** —
  4 personas presets con ejemplos de cierre de sprint/error/decisión.
- **`schemas/xdd.profile.schema.json`** — schema actualizado con sección
  `branding` (ecosystem_name/slug, orchestrator_trigger, persona, output.compact,
  attribution_required, rename_subworkflows).
- **`templates/xdd.profile.with-branding.yml`** — template completo.
- **`docs/adr/0011-white-labeling-policy.md`** — política inmutable
  (framework upstream) vs customizable (instance).
- **`docs/BRANDING.md`** — guía operativa con 3 ejemplos (startup casual,
  fintech formal, consultora dev) + matriz combinable 4×4 con xdd-talk-compact.
- **`tests/bats/xdd-brand.bats`** — 10 tests verdes.
- **`.xdd/build/sprint-13/REPORT.md`** — sub-reporte.

### Added — Sprint 12 (2026-05-26) — AgentShield + Shannon dep + rename + ADR-0010
- **`scripts/xdd-shield.py`** — AgentShield: audit estático del propio framework.
  13 reglas v0.1.0 (hooks/workflows/registry/MCP/general). Severity crit/high/
  warning/info, `--ci` gate, `--json` output. Repo X-DD pasa con 0 crit/high.
- **`scripts/xdd-pentest.sh`** — wrapper híbrido. Si Shannon CLI (`shn`)
  instalado: delega capacidades dinámicas (fuzz/verify/sandbox). Sin Shannon:
  degrada elegantemente a STRIDE + source-review estático con aviso de skip.
- **Rename** `prompts/agents/security/shannon-secops-expert.md` →
  `security-pentest-operator.md`. Frontmatter actualizado con constraints
  declarados. Atribución a Shannon preservada en system prompt + NOTICE.
- **`docs/adr/0010-shannon-external-dep-pentest-operator-naming.md`** —
  Shannon como dep externa AGPL-3.0 opcional + rename para neutralidad.
- **`docs/PENTEST.md`** — guía operativa con división Shannon↔AgentShield.
- **`DEPENDENCIES.md`** — nueva sección Pentesting con disclaimer AGPL.
- **`tests/test_shield.py`** — 10 tests verdes (102 total).
- **`.xdd/build/sprint-12/REPORT.md`**.

### Added — Sprint 11 (2026-05-26) — Multi-agent orchestration runtime
- **`scripts/xdd-orchestrate.py`** — runtime stdlib pura (ThreadPoolExecutor,
  no PM2). 3 orchestration types: sequential / parallel / parallel_then_sync.
  Modo dry-run por default + `--exec` para validar prompts. NO ejecuta LLM
  calls directamente; delega al orquestador vía MCP server (Sprint 6).
- **`.agent/workflows/orchestrate.md`** — workflow `/orchestrate` catalogado
  sección 10. 51 workflows totales.
- **`tests/test_orchestrate.py`** — 13 tests verdes (92 total).
- **`.xdd/build/sprint-11/REPORT.md`**.

### Added — Sprint 10 (2026-05-26) — Skills + Eval-harness + xdd-talk-compact
- **`skills/xdd-talk-compact/SKILL.md`** — compresión output orquestador,
  3 niveles (lite/standard/ultra), inspirado en caveman (juliusbrussee/caveman,
  MIT, 65k stars) con atribución en NOTICE. Combinable con persona (Sprint 13)
  en matriz 4×3.
- **`skills/agent-eval/SKILL.md`** — eval-harness con 5 grader types
  (structural/behavioral/output_match/pass_at_k/token_count_reduction).
- **`scripts/xdd-eval.py`** — harness Python stdlib pura. `list`/`run`/`show`
  + `--ci` gate. Parser YAML mínimo. Token counter con `ignore_code_blocks`.
- **`evals/xdd-talk-compact/cases.jsonl + grader.yaml`** — suite real,
  5 cases, threshold 50% reduction. Validado: 5/5 pasan (~60% avg reduction).
- **`prompts/skills/registry.json` + `schemas/skills.schema.json`** — SSoT.
- **`tests/test_eval.py`** — 17 tests verdes (79 total).
- **Fix CI markdownlint** — 2 errores en `the-longform-guide.md` (link
  fragments + empty link).
- **`.xdd/build/sprint-10/REPORT.md`**.

### Added — Sprint 9 (2026-05-26) — Continuous Learning (instincts + /evolve + SQLite)

- **`scripts/xdd-state.py`** — state store SQLite con 5 subcomandos
  (init/record-instinct/list/evolve/prune/stats). DB default `~/.xdd/state.db`
  (override `XDD_STATE_DB`). Schema: instincts + instinct_sessions + evolutions.
- **`.agent/workflows/evolve.md`** — workflow `/evolve` que cluster instincts
  por categoría (MVP simple, TF-IDF en Sprint 11) y propone skills/agents/commands.
  Aprobación humana obligatoria (T6.1 mitigación) antes de promover.
- **`.agent/hooks/scripts/stop-pattern-extraction.sh`** — deja de ser stub.
  Extrae 2 heurísticas v0.1.0: commits recientes + cambios de `.status` de fases.
  Opt-out vía `XDD_LEARNING_DISABLED=1`.
- **Catalog actualizado** — sección 9 "Continuous Learning" añadida.
- **`tests/test_state.py`** — 12 tests pytest verdes (init, record, list filters,
  evolve clusters, evolve generate, prune, stats).
- **`.xdd/build/sprint-9/REPORT.md`** — Build extensión.

### Stats — Sprint 9
- **109 tests totales verdes** (97 anteriores + 12 nuevos).
- **50 workflows** (49 + /evolve).
- **+1 script** (`xdd-state.py`).
- **+1 hook real** (no stub).

### Changed — Sprint 9
- `memoria.md` — estado actualizado a Sprint 9.

### Added — Sprint 8 (2026-05-26) — Gobernanza OSS + 3-tier docs + commitlint + agent.yaml + research/

**Gobernanza OSS (Tarea 8.1):**
- `CONTRIBUTING.md` — guía completa con reglas duras X-DD
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `SECURITY.md` — policy de divulgación, hardening, threat model summary
- `NOTICE` — atribuciones a ECC, MemPalace, Anthropic, Nygard, Keep a Changelog, MCP
- `.github/ISSUE_TEMPLATE/{bug,feature,ide-adapter,agent}.md` (4 templates)
- `.github/PULL_REQUEST_TEMPLATE.md` con checklist X-DD obligatorio

**Devcontainer 1-click:**
- `.devcontainer/devcontainer.json` (Python 3.12 + Node 20 + gh + Docker-in-Docker)
- `.devcontainer/postCreate.sh` (bats + pytest + jsonschema + pre-commit + MemPalace opcional)

**3-tier docs (inspiración ECC):**
- `the-shortform-guide.md` — Quickstart visual ~15 min
- `the-longform-guide.md` — referencia exhaustiva por feature
- `the-security-guide.md` — modelo de amenazas + SecDD + hardening

**Manifesto plugin interop:**
- `agent.yaml` — descriptor X-DD para futuro plugin marketplace (workflows, agents,
  MCP, hooks, gate keeper, config, install, deps, dogfooding, testing, docs)

**Commitlint enforced (Tarea 9.1 parcial):**
- `commitlint.config.js` con conventional commits + scope sugerido
- `.github/workflows/lint-commits.yml` valida commits del PR

**Live state separado (inspiración ECC):**
- `WORKING-CONTEXT.md` (raíz) — estado live del sprint actual, sobreescribible
- `memoria.md` se mantiene como bitácora inmutable

**Research:**
- `docs/research/ECC-inspiration-analysis.md` — análisis comparativo X-DD vs ECC

**Release infrastructure (Tarea 9.1):**
- `.github/workflows/release.yml` — tag-triggered con validación de gates +
  extracción de notas del CHANGELOG

### Changed — Sprint 8
- `memoria.md` — estado actualizado a Sprint 8 / Fase 6-Retro init.

### Added — Sprint 7 (2026-05-26) — Adapters + Hooks + Manifests + E2E

**Adapter IDE (DRY pattern):**
- `scripts/xdd-adapt.sh` con targets `claude-code`, `opencode`, `all` + `--dry-run`/`--list` —
  genera config IDE-específica desde SSoT (.agent/workflows/) vía symlinks.
- Cobertura: 8 tests bats `tests/bats/xdd-adapt.bats`.

**Hook system event-driven (inspiración ECC):**
- `.agent/hooks/hooks.json` con 8 hooks bash cross-platform.
- Eventos: 3 PreToolUse (`dangerous-command`, `config-protection`, `doc-file-warning`)
  + 2 PostToolUse (`mempalace-index`, `pr-logger`) + 1 SessionStart (`context-load`)
  + 2 Stop (`git-check`, `pattern-extraction` stub Sprint 9).
- Profiles: minimal / standard / strict. Runtime control vía
  `XDD_HOOK_PROFILE`, `XDD_DISABLED_HOOKS`, `XDD_ALLOW_CONFIG_EDIT`.
- `schemas/hooks.schema.json` valida estructura.
- `.agent/hooks/README.md` + `docs/HOOKS.md` con recetas, threat model coverage,
  diferencias vs ECC.
- Cobertura: 12 tests bats `tests/bats/hooks.bats`.

**Manifest-driven install + profiles:**
- `manifests/install-modules.json` (13 módulos) + `install-profiles.json` (6 perfiles:
  minimal/core/developer/security/research/full) + `install-components.json` (componentes finos).
- 3 schemas JSON Schema draft 2020-12 en `schemas/install-*.schema.json`.
- `scripts/xdd-init.sh` extendido con `--profile=NAME`, `--modules=csv`, `--list-profiles`.
  Mantiene fallback legacy si Python no disponible.
- `docs/INSTALL_PROFILES.md` referencia completa.
- Módulos futuros (Sprints 9-12) declarados con `available_from` — instalador no se rompe.
- Cobertura: 9 tests bats `tests/bats/xdd-init.bats` + 13 tests pytest `tests/test_manifests.py`.

**install.ps1 cross-platform:**
- Paridad con `xdd-init.sh` para Windows (PowerShell 5.1+/7+).
- Soporta `-Profile`, `-Modules`, `-Dest`, `-ListProfiles`, `-Help`, `-Version`.
- Usa Python3 para resolver manifests.

**Tests E2E del Quickstart:**
- `tests/e2e/test_quickstart.bats`: 12 escenarios end-to-end.
- Doctor + lint + validate-registry + gate + MCP + init + adapt + dogfooding.

**Trazabilidad:**
- `.xdd/build/sprint-7/REPORT.md` + `.xdd/qa/QA_REPORT.md` (cierre Fase 5-QA).
- Re-aprobación legítima de fase `spec` post-cambio markdownlint (caso real Sprint 7).

### Changed — Sprint 7
- `scripts/xdd-init.sh` reescrito con resolver manifest-driven.
- `.agent/hooks/scripts/pre-write-doc-warning.sh` matchea paths sin prefijo `./`.
- `.xdd/spec/.signature` re-firmada (cambio legítimo de DOMAIN.md tras PR #6).

### Stats — Sprint 7
- **97 tests totales** verdes (35 bats + 50 pytest + 12 E2E).
- **26 archivos nuevos**, 3 modificados, ~2100 LOC añadidas.
- **8 hooks**, **6 profiles**, **13 modules**, **4 schemas JSON**.

### Added — Sprint 6 (2026-05-26) — MCP Server propio ⭐

- **`xdd-mcp-server/`** — Model Context Protocol server propio de X-DD.
  Python ≥3.9 stdlib pura (sin deps PyPI: ni `fastmcp` ni `mcp-sdk`).
  JSON-RPC 2.0 sobre stdio. Implementa subset necesario de MCP
  (`initialize`, `tools/list`, `tools/call`, `notifications/initialized`).
- **6 tools v0.1.0:**
  - `xdd_validate_phase` — validación + firma HMAC (reusa `scripts/xdd-gate.py`)
  - `xdd_transition_phase` — transición secuencial
  - `xdd_list_workflows` — catálogo desde `.agent/workflows/`
  - `xdd_invoke_workflow` — devuelve contenido (NO ejecuta — T6.3)
  - `xdd_list_agents` — registry tipado (filtrable por categoría)
  - `xdd_get_phase_artifacts` — whitelist `.xdd/` (T4.3)
- **`tests/test_mcp_server.py`** — **17/17 pytest verdes** (dispatcher,
  tools, error handling, security mitigations).
- **`docs/MCP_INTEGRATION.md`** — setup por IDE: Claude Code, Cursor, Zed,
  Continue, Cline, Windsurf. Cualquier IDE MCP-compat consume el mismo server
  sin adapter dedicado.
- **`.xdd/build/sprint-6/REPORT.md`** — Build (4/5).

### Changed — Sprint 6
- **`memoria.md`** — estado actualizado a Sprint 6 / Fase 4-Build (4/5).
- **README.md** (pendiente próximo sprint) — anuncio "X-DD habla MCP nativo".

### Added — Sprint 5 (2026-05-26) — Registry tipado de agentes

- **`prompts/agents/registry.json`** — catálogo machine-readable con
  **180 agentes / 15 categorías** + **3 composition_patterns**
  (security_review, feature_squad, release_train) + **3 routing_rules**.
- **`prompts/agents/registry.schema.json`** — JSON Schema 2020-12 que define
  la estructura: agent (id, name, category, prompt_file, ide_compat,
  constraints, triggers, fallback_agent), composition_pattern y routing_rule.
- **`scripts/migrate-agents-to-registry.py`** — migrador automático.
  Parser YAML mínimo (no requiere PyYAML), genera ids kebab-case y atributos
  desde frontmatter. Re-ejecutable cuando se añaden agentes nuevos.
- **`scripts/validate-registry.py`** — valida schema + existencia de
  `prompt_file`. Modo `--strict` detecta id-refs rotas en composition_patterns
  y routing_rules.
- **`scripts/generate-equipo.sh`** — regenera `docs/equipo.md` desde el
  registry. SSoT-derived: elimina drift entre código y docs.
- **`.xdd/build/sprint-5/REPORT.md`** — Build (3/5).

### Changed — Sprint 5
- **`docs/equipo.md`** — ahora auto-generado desde registry. Header explícito:
  "NO editar a mano". Tablas por categoría con emoji/nombre/descripción/path.
- **`memoria.md`** — estado actualizado a Sprint 5 / Fase 4-Build (3/5).

### Fixed — entre sprints (2026-05-26) — PR #6

- **`.markdownlint.yaml`** — reescrito con 22 reglas cosméticas desactivadas
  (line-length, single-h1, blanks-around-*, table-column-style, bare-urls,
  list-marker-space). Mantiene solo reglas que detectan errores reales
  (estructura, links rotos, fenced code, encoding).
- **`.xdd/spec/DOMAIN.md`**, **`docs/GATE.md`**, **`prompts/agents/product/product-manager.md`**,
  **`prompts/agents/specialized/specialized-developer-advocate.md`** — 7 errores
  reales corregidos (tablas con `|` literal, blockquotes mal unidos, heading
  parseado mal).
- **CI `lint-markdown`** — pasó de 6603 errores en 295 archivos a **0 errores**.

### Operational — entre sprints (2026-05-26)

- **Política del repo cambiada a `delete_branch_on_merge=false`** —
  preserva las branches de cada sprint en GitHub para trazabilidad pública del
  trabajo realizado.
- **5 branches restauradas** desde reflog local y pusheadas:
  `feat/sprint-1-mempalace-quickstart`, `feat/sprint-2-ci-base`,
  `feat/sprint-3-doctor-config`, `feat/sprint-4-gate-hmac`, `feat/sprint-5-registry`.

### Added — Sprint 4 (2026-05-26) — Gate keeper HMAC ⭐

- **`scripts/xdd-gate.py`** — gate keeper programático con 5 subcomandos
  (`init`, `validate`, `transition`, `approve`, `status`) + salida `--json`.
  Implementa firma **HMAC-SHA256** sobre `(phase, sorted_checksums, approver,
  timestamp_utc_iso)` por cada aprobación. Cualquier alteración manual de
  artefactos / status / approvers / clave invalida la firma y `validate` lo
  detecta. Python ≥3.9, stdlib pura (sin deps PyPI).
- **`tests/test_gate.py`** — 17 tests pytest, todos verdes:
  init idempotente, approve con/sin key/approver, validate detecta tampering
  de artefactos / firma corrupta / clave rotada, transition no-secuencial,
  status reporta todas las fases.
- **`docs/GATE.md`** — referencia completa: setup, comandos, flujo típico,
  artefactos por fase, integración en workflows, rotación de clave,
  cobertura de amenazas (T1-T3 + V4 del threat model).
- **`.gitignore`** — `.xdd/.gate-key` explícito como secreto + Python/Node/IDE
  caches y env files (ADR-0009).
- **`.xdd/build/sprint-4/REPORT.md`** — Build (2/5).

### Dogfooding — Sprint 4

Las 3 fases ya completadas de X-DD aplicado a sí mismo están **APROBADAS y FIRMADAS**:

```
✓ briefing  APROBADO  (firma cffaf210…)
✓ spec      APROBADO  (firma 4fc4d8e6…)
✓ plan      APROBADO  (firma 232d9368…)
```

Transiciones validadas: `briefing→spec`, `spec→plan`, `plan→build` ✓.

### Changed — Sprint 4

- **`memoria.md`** — estado actualizado a Sprint 4 / Fase 4-Build (2/5).

### Added — Sprint 3 (2026-05-26)
- **`scripts/xdd-doctor.sh` v2** — reescrito con comparación SemVer real
  (`semver_ge` + `sort -V`), salida `--json` opcional (sobre-mejora), checks
  separados en Núcleo obligatorio / recomendado / Orquestadores / Testing /
  Seguridad / Estructura / Configuración. Versiones mínimas declaradas:
  git ≥2.30, bash ≥4.0, python3 ≥3.9, node ≥20, mempalace ≥3.3, bats ≥1.10,
  gitleaks ≥8.18.
- **`xdd.config.yml`** — configuración operacional del propio repo X-DD
  (dogfooding); directiva `# yaml-language-server` para autocomplete.
- **`schemas/xdd.config.schema.json`** — JSON Schema draft 2020-12; cubre
  mempalace, pipeline (con `require_signature` para HMAC), agents (Sprint 5),
  ide_adapters (Sprint 7).
- **`docs/CONFIG.md`** — referencia completa de cada campo con defaults,
  enums, ejemplos de validación.
- **`.xdd/build/sprint-3/REPORT.md`** — sub-reporte de Build (1/5).

### Changed — Sprint 3
- **`xdd-doctor.sh`** ahora retorna `--json` machine-readable para CI/dashboards.
- **`memoria.md`** — estado actualizado a Sprint 3 / Fase 4-Build (1/5).

### Added — Sprint 2 (2026-05-26)
- **`.github/workflows/lint-shell.yml`** — ShellCheck en push/PR sobre `**.sh`.
- **`.github/workflows/lint-markdown.yml`** — markdownlint-cli2 sobre `**.md`.
- **`.github/workflows/gitleaks.yml`** — escaneo de secretos en cada PR y push a main.
- **`.github/workflows/validate-prompts.yml`** — 3 jobs: lint-workflows + smoke-doctor + verify --help/--version en scripts.
- **`.markdownlint.yaml`** — reglas alineadas al estilo del repo (línea ≤200, HTML inline, headings duplicados siblings-only).
- **`.pre-commit-config.yaml`** — hooks pre-commit: trailing whitespace, end-of-file, check-yaml/json, large files, mixed line ending, shellcheck, gitleaks, markdownlint, lint-xdd-workflows.
- **`.github/renovate.json`** — config Renovate con preset OSS, automerge minor/patch, MemPalace con review requerido, security alerts habilitados.
- **`.xdd/plan/PLAN.md`** — espejo formal del plan macro en el repo (Fase 3-Plan dogfooded).

### Changed — Sprint 2
- **`memoria.md`** — estado actualizado a Sprint 2 / Fase 3.

### Added — Sprint 1 (2026-05-26)
- **`DEPENDENCIES.md`** — matriz oficial de dependencias (núcleo, recomendado,
  orquestadores, testing, seguridad) con versión mínima, distribución, licencia
  y rol. Advertencia anti-impostores para MemPalace.
- **`.editorconfig`** — convenciones consistentes (LF, UTF-8, 2-space, max 100,
  4-space para py/sh, tab para Makefile).
- **`.gitattributes`** — normalización a LF + linguist overrides para que GitHub
  clasifique `templates/`, `docs/` y `prompts/agents/` como documentación.
- **`Makefile`** — UX unificada: `make doctor|start|init|lint|test|trace|cierre|version`.
- **`.xdd/spec/DOMAIN.md`** — modelo de dominio (DDD) con 5 bounded contexts,
  15+ entidades, value objects, agregados, ubiquitous language y 7 reglas
  invariantes. Diagrama Mermaid.
- **`.xdd/spec/THREATS.md`** — modelo de amenazas STRIDE: 23 amenazas tipificadas
  + 5 vectores específicos para sistemas IA-driven + plan de mitigación por
  sprint.
- **`--help` y `--version`** añadidos a `xdd-start.sh`, `xdd-init.sh`,
  `xdd-doctor.sh`, `lint-workflows.sh` (todos `v0.1.0-dev`).

### Changed — Sprint 1
- **`README.md`** — badges (license, last-commit, ADRs, workflows, MemPalace);
  framing corregido de MemPalace ("dependencia externa MIT" en lugar de "pieza
  del ecosistema"); descripción técnica corregida ("ChromaDB + SQLite" en lugar
  de "base de grafos"); nueva sección "Qué NO es X-DD"; principios de
  gobernanza incluyen firma HMAC del gate y dogfooding visible.
- **`memoria.md`** — estado actualizado a Sprint 1 / Fase 2.

### Added — Sprint 0 (2026-05-26)
- **Dogfooding inicial** — directorio `.xdd/briefing/` con `SPEC.md` y `FEATURES.md`
  del propio X-DD como producto.
- **10 ADRs** (`docs/adr/0000` a `0009`) cerrando las preguntas abiertas del
  plan MEJORAS-X-DD v1.1: mapeo a fases, dogfooding visible, profile vs
  config, Python como runtime, MemPalace externa, MCP server propio, gate
  HMAC, alcance de adapters, CLI diferido, política de `.xdd/`.
- **`docs/adr/README.md`** — índice cronológico de ADRs.
- **`PROJ-MASTER-PLAN.md`** — Gantt Mermaid de los 8 sprints + grafo de dependencias.
- **`docs/CHANGELOG.md`** — este archivo.
- **Anexo v1.2 de `MEJORAS-X-DD.md`** — consolida las decisiones meta y enlaza ADRs.

### Changed — Sprint 0
- **`memoria.md`** — actualizada con sección "Estado Actual" del Sprint 0 y log
  de las 10 decisiones arquitectónicas.

---

## Convenciones

- Cada sección de sprint usa subcategorías: `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed`, `Security`.
- Cada bullet enlaza al archivo o sección que cambió.
- Commits asociados siguen formato convencional: `feat(N.N): ...`, `fix(N.N): ...`,
  `docs(adr): NNNN ...`.
- `/release-cut` consolida `[Unreleased]` a `[v0.1.0] — YYYY-MM-DD`.
