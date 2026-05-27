# ADR-0023 — Context budget policy (xdd-context.py + thresholds)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 19

## Context

Sesiones agénticas largas explotan context window sin warning. Costo: error 400 al exceder + degradación de respuesta antes de hard limit.

Research:
- LLMLingua: compresión semantic-preserving
- Mirage / Token Savior: filesystem-paradigm reduce loading
- ai-boost: "Context Engineering" is foundational discipline

Hoy X-DD asume tokens infinitos. Sin presupuesto declarado = sin alerts.

## Decision

Sprint 19 introduce:

1. **`scripts/xdd-context.py`**: estima tokens (heurística stdlib o tiktoken si disponible) + check vs budget. Exit codes: 0=ok, 1=warning, 2=block.
2. **Sección `context_budget:` en `xdd.config.yml`** opt-in:
   ```yaml
   context_budget:
     max_tokens: 200000          # Claude Opus/Sonnet 200k default
     warning_threshold: 0.80     # warn al 80%
     block_threshold: 0.95       # bloquea al 95%
   ```
3. **Hook `.agent/hooks/scripts/pre-llm-budget.sh`**: PreToolUse que invoca `xdd-context check` antes de cada LLM call. Si exit=2, bloquea call. Si exit=1, warn pero permite.

## Alternatives considered

- **No introducir budget (status quo):** rechazado. Sin alerts = bug en producción.
- **Hard limit only (no warning):** rechazado. Warning at 80% da time para compactar antes de block.
- **Budget como % del context window del provider:** considerado pero más complejo. Para v0.1.0, absolute number simple.
- **Bundlear tiktoken:** rechazado. Stdlib heurística suficiente baseline; tiktoken opcional.

## Consequences

### Positivas
- ✅ Alerts antes de OOM/400
- ✅ Hook activable per-profile (default no-op, `strict` activa)
- ✅ Compatible con compact skill (Sprint 19 companion) — warning trigger compact
- ✅ Opt-in: proyectos sin `context_budget:` mantienen comportamiento anterior

### Negativas
- ⚠️ Heurística stdlib subestima 5-15% vs tiktoken — aceptable para alert
- ⚠️ Hook depende de orchestrator pasar `XDD_TOKENS_ESTIMATE` env var (no auto-detecta)
- ⚠️ Budget único — no diferencia entre system prompt + history (deferred v0.2.0)

## Implementation Sprint 19

```bash
python3 scripts/xdd-context.py estimate --file=long-prompt.md --json
python3 scripts/xdd-context.py check --tokens=170000 --budget=200000
python3 scripts/xdd-context.py budget --show
```

## Related
- ADR-0024 Compaction skill (companion: cuando warning → compact)
- ADR-0019 Multi-provider router (provider determines max context window default)
- ADR-0022 Per-call cost tracking (cost depende de tokens)

## References
- Anthropic context windows: https://docs.anthropic.com (200k Claude Sonnet/Opus)
- OpenAI context windows: 128k GPT-4o
- tiktoken: https://github.com/openai/tiktoken
- LLMLingua: https://github.com/microsoft/LLMLingua
