# ADR-0029 — AHE-style /evolve: 3-layer observability + frozen transfer

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 22

## Context

Sprint 9 introdujo /evolve con clustering categórico. Sprint 16 lo upgraded a TF-IDF cosine. Aún así: propuestas /evolve son **opaco** — sin evidencia explícita, sin predicción de impacto, sin verificación posterior.

NexAU-AHE (china-qijizhifeng) demostró que continuous learning **científico** requiere 3 layers:
1. **Component**: cada propuesta versionada, diff explícito, revertible
2. **Experience**: traces N-millones tokens comprimidos → layered report con evidence sourced
3. **Decision**: cada propuesta con `rationale_evidence` + `predicted_impact` + `falsification_check` que la siguiente iteración valida

Frozen harness transfer: NexAU-AHE demostró que harness evolucionado en Terminal-Bench transfiere a SWE-bench → "evolved components encode general engineering experience, not benchmark-specific tuning".

X-DD gap: nada de esto implementado.

## Decision

Sprint 22:

### 1. Extender schema `evolutions` (xdd-state.py SQLite)
4 columnas nuevas:
- `rationale_evidence` (JSON): instinct IDs + trace excerpts + category distribution
- `predicted_impact` (text): qué métrica esperás mejorar y cuánto
- `falsification_metric` (text): cómo verificarás next iteration
- `falsification_outcome` (text): null / passed / failed (next iter lo llena)

Migración idempotente via `_migrate_evolutions(conn)`.

### 2. `scripts/xdd-trace-summarize.py` — Experience layer
- 3 depths: `summary` / `detail` / `full`
- Comprime N-million events → layered markdown report con evidence sourced (timestamps + samples)
- Compatible con `.xdd/traces/<session-id>.jsonl` (Sprint 18 output)

### 3. `scripts/xdd-frozen-transfer.py` — Component layer experiment
- Toma skills/agents del proyecto source
- Aplica frozen al target
- Genera experiment report con next steps (correr eval-harness target + comparar via xdd-meta-eval)
- Persistencia `.xdd/frozen-experiments/<exp-id>.json`

### 4. cmd_evolve refactor
Cada propuesta ahora incluye rationale_evidence + predicted_impact + falsification_metric autogenerados.

## Alternatives considered

- **Solo TF-IDF (Sprint 16 status quo):** rechazado. Sin evidencia/falsificación = pseudo-ciencia.
- **Importar NexAU-AHE como dep:** rechazado. Heavy. Implementar 3-layer abstracción es ~600 LOC X-DD propio.
- **Solo trace-summarize, skip frozen-transfer:** rechazado. Frozen transfer demuestra generalización (claim científico fuerte).

## Consequences

### Positivas
- ✅ Continuous learning científico: evidence + prediction + falsification
- ✅ Trace replay (Sprint 18) feeds Experience layer
- ✅ Frozen transfer experiments documentables/reproducibles
- ✅ Meta-eval (Sprint 20) consume falsification_outcome para guarded promotion
- ✅ Schema idempotent migration (proyectos existentes upgrade sin breaking)

### Negativas
- ⚠️ `predicted_impact` y `falsification_metric` autogenerados con templates — manual refinement recommended
- ⚠️ `falsification_outcome` requires manual flag o pipeline futuro (no auto-fill v0.1.0)
- ⚠️ Frozen transfer asume estructura skills/ + registry compatible source ↔ target

## Implementation Sprint 22

```bash
# Trace summary
python3 scripts/xdd-trace-summarize.py last --depth=detail
python3 scripts/xdd-trace-summarize.py session --id=sess1 --depth=full --json

# Frozen transfer
python3 scripts/xdd-frozen-transfer.py run \
  --source=/path/to/project-a --target=/path/to/project-b --dry-run

python3 scripts/xdd-frozen-transfer.py run \
  --source=/path/to/project-a --target=/path/to/project-b \
  --suite=external/terminal-bench-2

python3 scripts/xdd-frozen-transfer.py list
```

## Related
- Sprint 9 (continuous learning base — instincts + state.db)
- Sprint 16 (TF-IDF clustering — Sprint 22 extiende)
- Sprint 18 (trace replay — input para Experience layer)
- Sprint 20 (meta-eval — verifica falsification next iteration)
- Sprint 21 (authz — propuestas /evolve pasan por authz si auto-promote)

## References
- NexAU-AHE: https://github.com/china-qijizhifeng/agentic-harness-engineering
- 84.7% pass@1 Terminal-Bench 2 con harness evolucionado
- Frozen harness transfer comprobado en SWE-bench-Verified
