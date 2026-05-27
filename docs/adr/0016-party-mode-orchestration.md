# ADR-0016 — Party Mode orchestration (N agents sin lead)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 17

## Context

Composition patterns existentes (Sprint 11): `sequential`, `parallel`, `parallel_then_sync`. Todos requieren `lead`.

BMAD (NOASSERT, 48k⭐) popularizó "Party Mode": N agents sin lead, contribuciones libres, mejor para exploración/brainstorm. Caso de uso real: explorar el problem space sin un PM que filtre.

Gap X-DD: ningún pattern admite N agents sin lead.

## Decision

Añadir 4to pattern: `party`.

- Sin `lead`, sin `specialists` con jerarquía
- Campo `participants: [agent-id, ...]` (alias también `specialists` para compatibilidad)
- Opcional `consensus_required: bool` — si true, post-party se requiere consenso (workflow separado)
- Opcional `moderator: agent-id` — agente que sintetiza al final sin imponer

Implementación: `scripts/xdd-orchestrate.py:run_party()`.

## Alternatives considered

- **Modelar party como `parallel` sin lead:** rechazado. `parallel` siempre tiene lead; cambiar semántica rompería patterns existentes.
- **Solo en BMAD-compat mode:** rechazado. Party es genuinamente útil más allá de BMAD.
- **Implementar consensus_required como gate:** diferido a Sprint 18+.

## Consequences

### Positivas
- ✅ Brainstorm + exploración tienen runtime nativo
- ✅ Compatible con composition_patterns existentes (`party` es solo otro `orchestration`)
- ✅ Moderator opcional permite síntesis sin imponer

### Negativas
- ⚠️ Sin lead = sin handoff explícito → resultados pueden contradecirse
- ⚠️ N agents = costo lineal en cloud providers
- ⚠️ Consensus_required no implementa nada todavía (placeholder schema)

## Related
- ADR-0017 Web bundles (BMAD también)
- ADR-0011 White-labeling (party mode renombrable per-org)
- Sprint 11 (composition_patterns base)
