# Architecture Decision Records — X-DD

Índice cronológico de decisiones arquitectónicas. Formato [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html). Generadas vía `/adr-new`.

## Convenciones

- **Numeración:** 4 dígitos, secuencial, sin huecos.
- **Estados:** `Propuesto` | `Aceptado` | `Reemplazado por ADR-XXXX` | `Deprecado`.
- **Nunca borrar** un ADR — si se reemplaza, actualizar su estado y enlazar al nuevo.

## Índice

| # | Título | Estado | Tema |
|---|--------|--------|------|
| [0000](./0000-mapeo-mejoras-pipeline-xdd.md) | Mapeo MEJORAS-X-DD ↔ pipeline X-DD | Aceptado | Proceso |
| [0001](./0001-dogfooding-visible-commiteable.md) | Dogfooding visible y commiteable | Aceptado | Filosofía |
| [0002](./0002-profile-vs-config-coexisten.md) | `xdd.profile.yml` y `xdd.config.yml` coexisten sin overlap | Aceptado | Configuración |
| [0003](./0003-python-runtime-gate-keeper.md) | Python como runtime del gate keeper | Aceptado | Runtime |
| [0004](./0004-mempalace-dep-externa-no-fork.md) | MemPalace como dependencia externa, no fork | Aceptado | Dependencias |
| [0005](./0005-mcp-preferido-y-server-propio.md) | MCP como integración preferida + MCP server propio | Aceptado | Integración |
| [0006](./0006-gate-keeper-firma-hmac.md) | Gate keeper con firma HMAC-SHA256 | Aceptado | Seguridad |
| [0007](./0007-adapters-iniciales-claude-opencode-mcp.md) | Adapters iniciales: Claude Code + OpenCode + MCP | Aceptado | Integración |
| [0008](./0008-consolidacion-xdd-cli-diferida.md) | Consolidación `xdd` CLI Python — diferida a post-v0.1.0 | Propuesto (diferido) | Roadmap |
| [0009](./0009-politica-versionado-xdd-directorio.md) | Política de versionado de `.xdd/` (qué se commitea) | Aceptado | Repo |
| [0010](./0010-shannon-external-dep-pentest-operator-naming.md) | Shannon como dep externa AGPL + rename a security-pentest-operator | Aceptado | Seguridad + naming |
| [0011](./0011-white-labeling-policy.md) | White-labeling: nombre del framework inmutable, instancia customizable | Aceptado | Customización |
| [0012](./0012-workspace-mode-wizard.md) | Workspace mode + wizard interactivo | Aceptado | IDE Setup |
| [0013](./0013-monorepo-three-modes.md) | Monorepo: 3 modos (isolated / shared / hybrid) | Aceptado | Arquitectura |
| [0014](./0014-sdd-parity-clarify-cross-validate-constitution.md) | SDD parity: /clarify + /cross-validate + constitución template | Aceptado | Gobernanza |
| [0015](./0015-ai-pre-commit-review.md) | AI pre-commit review (provider-agnostic) | Aceptado | Calidad |
| [0016](./0016-party-mode-orchestration.md) | Party Mode orchestration (N agentes sin lead) | Aceptado | Multi-agente |
| [0017](./0017-web-bundles-distribution.md) | Web bundles para distribución de skills/agents/workflows | Aceptado | Release |
| [0018](./0018-hitl-checkpoints-orchestration.md) | HITL checkpoints en orchestration runtime | Aceptado | Orquestación |
| [0019](./0019-multi-provider-router.md) | Multi-provider LLM router (xdd-router.py) | Aceptado | Interop |
| [0020](./0020-community-skills-voting-policy.md) | Community skills voting policy (ventana 7 días) | Aceptado | Comunidad |
| [0021](./0021-observability-stack-otel-replay.md) | Observability: OTel Gen AI spans + session replay + middleware | Aceptado | Observabilidad |
| [0022](./0022-per-call-cost-tracking.md) | Per-call LLM cost tracking (xdd-cost.py + SQLite) | Aceptado | FinOps |
| [0023](./0023-context-budget-policy.md) | Context budget policy (xdd-context.py + thresholds) | Aceptado | Rendimiento |
| [0024](./0024-compaction-skill.md) | Compaction skill provider-agnostic | Aceptado | Skills |
| [0025](./0025-inspect-ai-compatibility.md) | Inspect AI compatibility en xdd-eval | Aceptado | Integración |
| [0026](./0026-external-benchmark-integration.md) | External benchmark integration policy | Aceptado | Calidad |
| [0027](./0027-sandbox-provider-abstraction.md) | Sandbox provider abstraction (skill xdd-sandbox) | Aceptado | Seguridad |
| [0028](./0028-permission-model-intent-authz.md) | Permission model: intent taxonomy + 5-layer eval + OAP authz | Aceptado | Seguridad |
| [0029](./0029-ahe-evolve-3-layer-observability.md) | AHE-style /evolve: 3-layer observability + frozen transfer | Aceptado | Arquitectura |
| [0030](./0030-a2a-protocol-compat.md) | A2A (Google Agent-to-Agent) Protocol compat | Aceptado | Integración |
| [0031](./0031-agui-streaming-spec.md) | AG-UI event-driven streaming spec | Aceptado | UI |
| [0032](./0032-skills-migration-plan-act-adapt-orch.md) | Skills migration policy + plan_and_act + adapt_orch | Aceptado | Evolución |
| [0033](./0033-gitnexus-tier1-companion.md) | GitNexus como companion tier-1 (paralelo MemPalace) | Aceptado | Integración |
| [0034](./0034-universal-ide-adapter.md) | Universal IDE adapter (copia real + 6 IDEs + auto-detect) | Aceptado | Integración |
| [0035](./0035-global-install-architecture.md) | Global install architecture + dynamic path resolution | Aceptado | Despliegue |
| [0036](./0036-codex-adapter-global-skills.md) | Codex adapter (skills global, orchestrator pattern) | Aceptado | Integración |
| [0037](./0037-windsurf-adapter-parity.md) | Windsurf adapter parity (workflows nativos) | Aceptado | Integración |
| [0038](./0038-workflow-enforcement-pilot-lessons.md) | Workflow enforcement: retroaplicación de lecciones del piloto | Aceptado | Lecciones |
| [0039](./0039-global-orchestrator-parity.md) | Global orchestrator parity: `/<trigger>` desde cualquier dir | Aceptado | Arquitectura |
| [0040](./0040-vscode-global-prompts-discovery.md) | VSCode + Copilot global prompts discovery | Aceptado | Integración |
| [0041](./0041-auto-organize-workspace.md) | Auto-organize workspace + auto-gitignore declarativo | Aceptado | Automatización |
| [0042](./0042-gitflow-hybrid-trunk-based.md) | Reconciliación GitFlow — híbrido trunk-based por defecto | Aceptada | Versionado |

> Nota: ADR-0043 a 0047 (pip-installable, comando global, adapters en código,
> deprecación MCP, PyPI publish) se integran al fusionar sus branches a `develop`.

## Cómo añadir un ADR

```bash
# Ejecuta el workflow X-DD
/adr-new

# O manualmente:
NEXT=$(printf '%04d' $(($(ls docs/adr/*.md | grep -oE '/[0-9]{4}-' | grep -oE '[0-9]{4}' | sort -n | tail -1) + 1)))
cp templates/adr.template.md docs/adr/${NEXT}-mi-decision.md
```

Tras crear, añadir entrada en este índice y commitear con `docs(adr): NNNN <título>`.
