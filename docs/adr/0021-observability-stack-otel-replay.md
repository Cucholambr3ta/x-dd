# ADR-0021 — Observability stack: OTel Gen AI spans + session replay + 6-stage middleware

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 18

## Context

X-DD orchestrate runtime (Sprint 11) imprime JSON propio. xdd-eval (Sprint 10) loggea grader outputs aislados. No hay capa unificada para inspect/debug session.

Research deep-dive (post-Sprint 17) identificó 3 gaps:
1. **OpenTelemetry Gen AI spans** — standard semántico que OpenLLMetry, OpenInference, AgentOps SDK, Langfuse, Helicone consumen
2. **Session trace replay** — reconstruir qué hizo el agent en una sesión (NexAU-AHE Agent Debugger pattern)
3. **6-stage middleware pipeline** — pattern deepagents (LangChain) que da hooks pre/post agent + pre/post model + wrap tool/model

Sin estos, X-DD vive en silo de telemetría custom.

## Decision

Sprint 18 introduce 3 herramientas + 6 nuevos event types en hooks.json:

### Herramientas
1. **`scripts/xdd-otel.py`**: emisor de spans con semantic conventions Gen AI. Sub-commands: `span-start`, `span-end`, `emit` (one-shot), `list`, `export` (jsonl/otlp). Stdlib pure: no requiere opentelemetry-sdk para baseline. Spans persistidos en `.xdd/traces/spans/<span-id>.json`.
2. **`scripts/xdd-replay.py`**: session reconstruction. Sub-commands: `record` (helper para instrumentar), `list`, `show`, `replay` (linear playback con --step), `diff` (comparar 2 sessions). Sessions persisten en `.xdd/traces/<session-id>.jsonl`.

### 6 nuevos event types en `.agent/hooks/hooks.json`
- `before_agent`: ba:otel:trace-start
- `before_model`: bm:cost:budget-check
- `wrap_model_call`: wm:otel:span
- `wrap_tool_call`: wt:otel:span
- `after_model`: am:cost:record
- `after_agent`: aa:replay:flush

Cada uno con stub script en `.agent/hooks/scripts/`. Profile `strict` activa todos.

### Compat externa
- OpenLLMetry / OpenInference: spans con kind `llm.call`, `tool.call`, `agent.invocation`
- Export OTLP JSON format en `xdd-otel export --format=otlp` → ingestable por AgentOps, Langfuse
- Persistencia local-first siempre (`.xdd/traces/`)

## Alternatives considered

- **opentelemetry-sdk como dep:** rechazado. Heavy + opinionado. Stdlib pure baseline, OTLP export opcional cubre el caso.
- **AgentOps SDK como dep:** rechazado. Proprietary backend lock-in.
- **Solo JSON propio sin OTel:** rechazado. Sin estándar = sin interop. Justifica el sprint.
- **Bundlear agenttrace:** rechazado. Distinct philosophy (X-DD = pipeline; agenttrace = post-hoc audit).

## Consequences

### Positivas
- SI Interop con AgentOps, Langfuse, OpenLLMetry, OpenInference sin parsers custom
- SI Replay sesiones para debug regresiones (NexAU-AHE pattern)
- SI 6-stage middleware da control fine-grained sin acoplar a un orchestrator específico
- SI Local-first: trace data nunca sale del proyecto sin export explícito
- SI Stdlib pure baseline → cero deps nuevas

### Negativas
- WARN Stubs hooks 6-stage no auto-activos hasta orchestrators los soporten (Claude Code, OpenCode, Cursor adapt)
- WARN Pricing tabla en `xdd-cost.py` requiere mantenimiento manual (no auto-fetch de provider APIs)
- WARN `.xdd/traces/` puede crecer fast en sesiones largas → Sprint 22 añade trace-summarize compactador

## Implementation Sprint 18

```bash
# OTel
python3 scripts/xdd-otel.py span-start --name=feature-x --kind=agent.invocation
python3 scripts/xdd-otel.py span-end --id=<id> --status=ok
python3 scripts/xdd-otel.py export --format=otlp > spans.otlp.json

# Replay
python3 scripts/xdd-replay.py record --session=sess1 --event=turn_start --role=user --content="hello"
python3 scripts/xdd-replay.py list
python3 scripts/xdd-replay.py show --id=sess1
python3 scripts/xdd-replay.py replay --id=sess1 --step
python3 scripts/xdd-replay.py diff --a=sess1 --b=sess2
```

## Related
- ADR-0022 Per-call cost tracking (companion del Sprint 18)
- ADR-0029 AHE-style /evolve (Sprint 22 usa replay para evidence-backed rationale)
- Sprint 11 (orchestrate runtime — receptor de instrumentación OTel)
- Sprint 10 (eval-harness — receptor de spans skill.execution)

## References
- OpenTelemetry Gen AI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenLLMetry: https://github.com/traceloop/openllmetry
- OpenInference: https://github.com/Arize-ai/openinference
- AgentOps: https://agentops.ai
- NexAU-AHE Agent Debugger: https://github.com/china-qijizhifeng/agentic-harness-engineering
