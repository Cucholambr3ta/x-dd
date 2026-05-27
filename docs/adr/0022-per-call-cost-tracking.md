# ADR-0022 — Per-call LLM cost tracking (xdd-cost.py + SQLite)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 18

## Context

Proyectos consumidores de X-DD ejecutan workflows que invocan LLMs vía MCP/skills. Hoy no hay forma de medir cuánto se gasta. En enterprise, ausencia de cost tracking es bloqueante.

Research identificó patterns probados:
- AutoHarness: per-call cost attribution con pricing table model-aware
- AgentOps SDK: cost + token tracking + benchmarking
- Helicone: lightweight proxy con cost dashboard
- ECC: cost tracker stub

## Decision

Sprint 18 introduce `scripts/xdd-cost.py` + SQLite store en `~/.xdd/cost.db`:

- Tabla `calls(id, ts, provider, model, input_tokens, output_tokens, cost_usd, session_id, task)`
- Tabla `pricing_overrides(model, input_per_1m, output_per_1m)` para override locales
- Pricing default 2026-Q1 hardcoded para 11+ models populares
- Comandos: `record`, `report` (by model/provider/day, since=N[h|d|w]), `pricing list/update`, `total`

Integración futura:
- Hook `after_model:am:cost:record` (Sprint 18 stub) llama `xdd-cost record` post LLM call
- Router (Sprint 17) puede consultar pricing para sugerir cheaper model
- Eval-harness (Sprint 10) puede agregar cost por run para meta-comparación

## Alternatives considered

- **Solo log JSON sin SQLite:** rechazado. Sin queries agregadas no hay reporting useful.
- **Usar AgentOps SDK directo:** rechazado. Lock-in proprietary backend.
- **Pricing auto-fetch desde provider APIs:** rechazado para v0.1.0. Mantenimiento manual aceptable inicialmente.
- **Compartir DB con xdd-state.py:** rechazado. Separation of concerns (instincts vs cost) → 2 DBs.

## Consequences

### Positivas
- ✅ Enterprise-ready: cost por session/task/model auditable
- ✅ Local-first: no envía data a SaaS
- ✅ Pricing override por proyecto (model custom, enterprise rates)
- ✅ Compat con xdd-router.py (Sprint 17) para tradeoffs cost/calidad
- ✅ Reports `--by=day` permiten trends

### Negativas
- ⚠️ Pricing table requiere actualización manual (cuando Anthropic/OpenAI suben precios)
- ⚠️ Token counts deben suministrarse desde orchestrator (X-DD no cuenta tokens por sí mismo)
- ⚠️ Sin alerting (threshold breach) en v0.1.0 — diferido a Sprint 19 context_budget

## Implementation Sprint 18

```bash
python3 scripts/xdd-cost.py record --provider=claude --model=claude-haiku-4-5 \
                                   --input-tokens=1500 --output-tokens=800 \
                                   --session-id=sess1 --task=code_review

python3 scripts/xdd-cost.py report --since=7d --by=model

python3 scripts/xdd-cost.py pricing --list
python3 scripts/xdd-cost.py pricing --update --model=custom-foo --input=2.0 --output=8.0

python3 scripts/xdd-cost.py total
```

## Related
- ADR-0019 Multi-provider router (Sprint 17) — consulta pricing para sugerir cheaper
- ADR-0021 Observability stack (Sprint 18 companion)
- Sprint 19 (next) context_budget — usa cost data para warn pre-call

## References
- AutoHarness: https://github.com/aiming-lab/AutoHarness
- AgentOps SDK: https://agentops.ai
- Helicone: https://helicone.ai
- Pricing data Q1 2026: Anthropic / OpenAI / Google official docs
