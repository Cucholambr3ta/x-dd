# ADR-0031 — AG-UI event-driven streaming spec

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 23

## Context

AG-UI = protocolo event-driven entre agent runtime y UI client (web/desktop). Reemplaza polling + ad-hoc JSON con stream JSONL de eventos tipados.

X-DD orchestrate (Sprint 11) imprime JSON al final. AG-UI permite streaming en tiempo real: tool_call, content_chunk, hitl_request, etc.

## Decision

Sprint 23 introduce `scripts/xdd-agui.py`:

- 6 event types con schemas validados: `turn_start`, `tool_call`, `tool_result`, `hitl_request`, `content_chunk`, `turn_end`
- Cada event: `{spec: "agui/0.1", ts, event, ...payload}`
- `emit` command: emite 1 event validado
- `stream --from-orchestrate`: lee stdin de xdd-orchestrate, convierte a AG-UI events
- `schema`: lista schemas validadas

## Alternatives considered

- **OTel streaming:** rechazado. OTel = post-hoc spans, no live streaming UX.
- **SSE (Server-Sent Events) propio:** rechazado. Reinventar wheel.
- **WebSocket:** considerado pero JSONL stdout simpler para v0.1.0.

## Consequences

### Positivas
- ✅ Frontends pueden consumir X-DD events nativamente
- ✅ hitl_request event integra con ADR-0018 HITL checkpoints
- ✅ Compatible con tool_call → xdd-intent → xdd-authz pipeline
- ✅ Stream JSONL = simple parse, no needs WebSocket libs

### Negativas
- ⚠️ stdout streaming limita a 1 cliente concurrente per orchestrate run
- ⚠️ Real-time UI needs adapter (futuro xdd-agui-server v0.2.0)
- ⚠️ Backwards compat: orchestrate stdout cambia con `stream` mode (opt-in)

## Implementation Sprint 23

```bash
python3 scripts/xdd-agui.py schema --json
python3 scripts/xdd-agui.py emit --event=turn_start --turn-id=1
python3 scripts/xdd-agui.py emit --event=hitl_request --turn-id=2 \
    --data='{"prompt":"approve deploy?","required":true}'

python3 scripts/xdd-orchestrate.py run --pattern=feature_squad --json \
    | python3 scripts/xdd-agui.py stream --from-orchestrate
```

## Related
- ADR-0018 HITL checkpoints (hitl_request event)
- ADR-0021 OTel observability (complementary, not replacement)
- ADR-0030 A2A (companion)
- Sprint 11 orchestrate runtime

## References
- AG-UI: ai-boost/awesome-harness-engineering enumera protocol
