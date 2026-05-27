# ADR-0030 — A2A (Google Agent-to-Agent) Protocol compat

**Date:** 2026-05-27
**Status:** Accepted (stub v0.1.0; full HTTP server v0.2.0)
**Sprint:** 23

## Context

Google A2A Protocol = JSON-RPC standard para agents que se descubren y invocan entre sí. Agent Card = descriptor JSON publicado en `/.well-known/agent`.

X-DD composition_patterns son naturalmente A2A agents (lead + specialists, orchestration declarada). Exponerlos via A2A permite que otros agents (Google ecosystem, Mastra, deepagents) consuman X-DD patterns transparentemente.

## Decision

Sprint 23 introduce `scripts/xdd-a2a.py`:

- `agent-card`: emite JSON Agent Card spec/0.1 con todos los composition_patterns como tools A2A
- `list-patterns`: lista patterns con metadata A2A
- `invoke`: client-side test JSON-RPC (stub, real exec via xdd-orchestrate)
- `serve`: stub mode v0.1.0 (HTTP server real diferido a v0.2.0)

Implementación HTTP server completa diferida a v0.2.0. v0.1.0 entrega: Agent Card emisor + protocol docs.

## Alternatives considered

- **Implementar HTTP server v0.1.0:** rechazado. Scope > 1d. Stub + docs cubren spec compat.
- **Solo MCP (Sprint 6) sin A2A:** rechazado. A2A es ecosystem Google complementario, no replaceable.
- **A2A vía proxy externo:** rechazado. Adopters externos deben tener path nativo.

## Consequences

### Positivas
- ✅ X-DD discoverable via A2A standard
- ✅ Composition_patterns expuestos sin reimplementar
- ✅ Agent Card serializable + reproducible
- ✅ Compat con Sprint 23 plan_and_act + adapt_orch patterns

### Negativas
- ⚠️ v0.1.0 = stub. HTTP server real es v0.2.0
- ⚠️ Spec A2A todavía evoluciona — drift de upstream esperado

## Implementation Sprint 23

```bash
python3 scripts/xdd-a2a.py agent-card --pretty
python3 scripts/xdd-a2a.py list-patterns --json
python3 scripts/xdd-a2a.py invoke --agent=feature_squad
python3 scripts/xdd-a2a.py serve --port=8500  # stub
```

## Related
- ADR-0005 MCP integration preferida
- ADR-0031 AG-UI streaming spec (companion: A2A = discovery, AG-UI = streaming)
- ADR-0032 Skills migration + plan_and_act + adapt_orch (patterns expuestos via A2A)
- Sprint 6 MCP server propio
- Sprint 11 orchestrate runtime

## References
- Google A2A: https://github.com/google-research/google-research/tree/master/a2a
- Agent Card spec: A2A Protocol docs
