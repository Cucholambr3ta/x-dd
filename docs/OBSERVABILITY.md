# Observability Stack — X-DD (Sprint 18)

X-DD provee 3 herramientas + 6 nuevos event types para observability completo.

## Quick start

```bash
# OTel spans
python3 scripts/xdd-otel.py span-start --name=feature-x --kind=agent.invocation --json
python3 scripts/xdd-otel.py span-end --id=<span_id> --status=ok
python3 scripts/xdd-otel.py export --format=otlp > spans.otlp.json

# Session replay
python3 scripts/xdd-replay.py record --session=sess1 --event=turn_start --role=user --content="hi"
python3 scripts/xdd-replay.py show --id=sess1

# Cost tracking
python3 scripts/xdd-cost.py record --provider=claude --model=claude-haiku-4-5 \
                                   --input-tokens=1500 --output-tokens=800
python3 scripts/xdd-cost.py report --since=7d --by=model
```

## OTel Gen AI spans (xdd-otel.py)

Compat con OpenLLMetry / OpenInference semantic conventions.

**Span kinds:** `llm.call`, `tool.call`, `agent.invocation`, `skill.execution`, `workflow.step`, `gate.transition`, `phase.validation`.

**Persistencia:** `.xdd/traces/spans/<span-id>.json` (override con `XDD_OTEL_DIR`).

**Export:** `jsonl` (raw) o `otlp` (JSON OTLP format) → ingesta por AgentOps, Langfuse, etc.

## Session replay (xdd-replay.py)

Trace events linealmente. Útil para debug regresiones, root-cause de bugs.

**Schema event (JSONL):**
```json
{"ts": "2026-05-27T10:00:00Z", "event": "turn_start", "session_id": "s1",
 "role": "user", "content": "...", "attributes": {...}}
```

**Persistencia:** `.xdd/traces/<session-id>.jsonl` (override con `XDD_TRACES_DIR`).

## Cost tracking (xdd-cost.py)

Per-call cost con pricing table model-aware (USD/1M tokens). SQLite `~/.xdd/cost.db`.

**Pricing default Q1 2026** incluye Claude (Haiku/Sonnet/Opus), GPT (4o-mini/4o, o1), Gemini (Flash/Pro), local (llama, embed).

**Override per-proyecto:**
```bash
python3 scripts/xdd-cost.py pricing --update --model=my-model --input=2.0 --output=8.0
```

**Reports agrupados:** `--by=model | provider | day`.

## 6-stage middleware (.agent/hooks/hooks.json)

Inspirado en deepagents (LangChain). Cada stage tiene 1+ hook script:

| Stage | Hook ID | Purpose |
|---|---|---|
| before_agent | ba:otel:trace-start | Abre span agent.invocation |
| before_model | bm:cost:budget-check | Pre-call budget check |
| wrap_model_call | wm:otel:span | Span llm.call con tokens/cost |
| wrap_tool_call | wt:otel:span | Span tool.call con duration |
| after_model | am:cost:record | Persiste cost a SQLite |
| after_agent | aa:replay:flush | Flush session events |

**Activación:** profile `strict` en `xdd.config.yml`:
```yaml
hooks:
  profile: strict
```

Profile `minimal` / `standard` no activa las 6-stage por default (solo profile `strict`).

## Integración con otros sprints

- **Sprint 11** (orchestrate): emite spans `agent.invocation`, `tool.call`, `workflow.step`
- **Sprint 10** (eval-harness): emite spans `skill.execution`
- **Sprint 17** (router): consulta `xdd-cost pricing` para optimizar tradeoffs
- **Sprint 22 (futuro)** (AHE /evolve): consume traces de replay para evidence-backed rationale

## Referencias
- [ADR-0021 Observability stack](adr/0021-observability-stack-otel-replay.md)
- [ADR-0022 Per-call cost tracking](adr/0022-per-call-cost-tracking.md)
- OpenTelemetry Gen AI: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenLLMetry: https://github.com/traceloop/openllmetry
