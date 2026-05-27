# ADR-0032 — Skills migration policy + plan_and_act + adapt_orch patterns

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 23

## Context

Sprint 10 introdujo skills (SKILL.md). Sprint 16 política community voting. Sprint 23 cierra ecosystem con:

1. **Migration policy** explicita: cuándo workflow → skill
2. **2 nuevos composition_patterns** del research: plan_and_act + adapt_orch
3. **Web bundles MVP impl** (ADR-0017 spec)

ai-boost research enumeró deepagents patterns + Plan-and-Execute + AdaptOrch. X-DD necesita representar formalmente.

## Decision

### 1. Skills migration policy (cuándo workflow → skill)

Migra workflow a skill cuando:
- Es atomic (1 single capability)
- Tiene < 100 LOC equivalente
- Es reusable across múltiples workflows
- No requiere phase gate

Mantiene como workflow cuando:
- Multi-step con phase transitions
- Requiere gate keeper signing
- Domain-specific (no reusable)

Compat: workflow legacy puede llamar skill nuevo via tool invocation.

### 2. Composition patterns nuevos

**`plan_and_act`** (Plan-and-Execute):
```yaml
name: plan_and_act
lead: product-manager
specialists: [engineering-backend-architect, engineering-frontend-developer]
orchestration: sequential
gate_between: plan_approval
```
Planner crea plan → gate humano → executors ejecutan. Útil para tareas multi-step donde plan necesita aprobación antes de ejecución.

**`adapt_orch`** (Task-Adaptive Topology):
```yaml
name: adapt_orch
lead: product-manager
specialists: [backend-architect, ui-designer, security-engineer, test-analyzer]
orchestration: parallel_then_sync
sync_point: topology_decision
```
Specialists corren en paralelo. Lead recibe N outputs, decide topology de combinación (consensus, weighted, best-of-N). Útil para tasks complejas donde la mejor estructura no es conocida upfront.

### 3. Web bundles MVP (`scripts/xdd-bundle.py`)

Implementa ADR-0017 spec:
- `pack`: source dir → .xddbundle (zip) + manifest.json + HMAC signature
- `verify`: validate manifest required fields + license whitelist (rechaza AGPL/proprietary) + signature
- `install`: extract a target project
- `inspect`: muestra manifest sin extraer

`bundles/security-bundle.xddbundle` empaqueta xdd-sandbox + xdd-ai-review + security agents + secure-isolation-ops workflow → demo distribución.

## Alternatives considered

- **Migrar TODOS los workflows a skills:** rechazado. Workflows multi-step con gates necesitan permanecer como tales.
- **Solo 1 pattern nuevo:** rechazado. plan_and_act + adapt_orch cubren cases distintos (sequential gated vs parallel adaptive).
- **Web bundles deferred a v0.2.0:** rechazado. Spec sin impl = adopción 0. MVP entrega path completo.

## Consequences

### Positivas
- ✅ Política explicita migra skill ↔ workflow
- ✅ 2 nuevos patterns cubren cases research-validated
- ✅ Bundle ecosystem funciona: pack/verify/install/inspect
- ✅ security-bundle demo distributable
- ✅ License whitelist rechaza AGPL/proprietary (mantiene MIT pure)
- ✅ HMAC signature en manifest = audit trail

### Negativas
- ⚠️ Bundles no GUI install yet (solo CLI)
- ⚠️ Migration policy es guía, no scripted (manual judgment per case)
- ⚠️ HMAC key default público — production should override (Sprint 4 gate-key pattern)

## Implementation Sprint 23

```bash
# A2A
python3 scripts/xdd-a2a.py agent-card --pretty

# AG-UI
python3 scripts/xdd-agui.py schema

# Bundle
python3 scripts/xdd-bundle.py pack ./skills/xdd-sandbox/ \
    -o bundles/sandbox-skill.xddbundle \
    --name=sandbox-skill --author=acme --license=MIT
python3 scripts/xdd-bundle.py verify bundles/sandbox-skill.xddbundle
python3 scripts/xdd-bundle.py install bundles/sandbox-skill.xddbundle --to=/tmp/test-install

# Compositions nuevos en registry
python3 scripts/xdd-orchestrate.py run --pattern=plan_and_act
python3 scripts/xdd-orchestrate.py run --pattern=adapt_orch
```

## Related
- ADR-0017 Web bundles distribution spec (Sprint 17, este sprint impl)
- ADR-0020 Community skills voting policy (bundles también vía 7-day window)
- ADR-0030 A2A (patterns nuevos discoverable via Agent Card)
- ADR-0011 White-labeling (bundles per-org)
- Sprint 11 orchestrate runtime
- Sprint 10 skills system

## References
- deepagents Plan-and-Execute: https://github.com/langchain-ai/deepagents
- AdaptOrch research: ai-boost/awesome-harness-engineering
- BMAD bundles inspiration: https://github.com/bmad-code-org/BMAD-METHOD
- Microsoft Skills Framework: docs.microsoft.com (spec)
