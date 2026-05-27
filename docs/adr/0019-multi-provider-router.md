# ADR-0019 — Multi-provider LLM router (xdd-router.py)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 17

## Context

X-DD soporta cualquier asistente IA vía MCP (ADR-0005). Pero a nivel de skill/workflow execution, no hay capa que rute **qué modelo concreto** invocar para qué task.

Casos reales:
- `xdd-ai-review` corre 100 veces/día → Haiku (barato + rápido)
- `/architect-deep-review` corre 1 vez/semana → Opus (capacidad max)
- Embedding de docs → local Ollama (privacy + free)

Sin router, cada skill hardcodea provider/model. Resultado: lock-in implícito + costos no controlados.

Inspiración: Mastra router (NOASSERT, 24k⭐).

## Decision

Sprint 17 introduce `scripts/xdd-router.py`:

- 5 task types declarados: `fast_classify`, `code_review`, `deep_reasoning`, `embedding`, `bulk_extraction`
- 4 providers: `claude`, `openai`, `local`, `none`
- Defaults documentados por task (Haiku para classify, Sonnet para review, Opus para reasoning, Ollama para embedding, Ollama para bulk)
- Override per-proyecto vía `xdd.config.yml` sección `router:`
- Fallback chain automática si provider no disponible (`ANTHROPIC_API_KEY` etc. falta)

Comandos:
- `xdd-router list` — lista providers + cuáles están disponibles via env vars
- `xdd-router route --task=TYPE` — sugiere provider+model + rationale

## Alternatives considered

- **LiteLLM (Python dep):** rechazado. Heavy dep + abstracción opinada que oculta diferencias provider.
- **Routing en MCP server X-DD:** rechazado. MCP server expone tools, no debe decidir provider — eso es del orchestrator.
- **Solo Claude tracks (vendor lock):** rechazado. Viola ADR-0005 multi-provider.

## Consequences

### Positivas
- ✅ Costo controlado: defaults basados en cost/quality tradeoff óptimo
- ✅ Privacy by design: `embedding` y `bulk_extraction` default a `local`
- ✅ Skills agnóstic: pueden invocar router en vez de hardcodear provider
- ✅ Stdlib pure (yaml opcional): sin dep nuevas
- ✅ Fallback chain automática → resiliencia

### Negativas
- ⚠️ No mide latencia/costo real — sugerencias basadas en static defaults
- ⚠️ Local provider requiere Ollama configurado (out-of-band setup)
- ⚠️ No incluye load balancing entre providers (round-robin futuro)
- ⚠️ Skills que ya hardcodean provider no migran automáticamente (manual update)

## Implementation Sprint 17

```yaml
# xdd.config.yml
router:
  default_provider: claude
  fallback: [openai, local, none]
  task_routes:
    fast_classify: {provider: local, model: llama3.1-8b}
    code_review: {provider: claude, model: claude-sonnet-4-6}
    deep_reasoning: {provider: claude, model: claude-opus-4-7}
    embedding: {provider: local, model: nomic-embed-text}
```

```bash
$ xdd-router route --task code_review
[router] task=code_review
  → provider: claude
  → model: claude-sonnet-4-6
  → rationale: Best price/quality for code review
```

## Related
- ADR-0005 MCP como integración preferida
- ADR-0015 AI pre-commit review (skill usa router para elegir provider)
- ADR-0007 Adapters IDE (router complementa, no reemplaza)
- Mastra router: https://mastra.ai/docs
