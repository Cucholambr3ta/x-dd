# AHE-style /evolve — X-DD (Sprint 22)

Continuous learning científico: **evidence + prediction + falsification**.

Inspirado en NexAU-AHE (china-qijizhifeng) — 3 capas de observability.

## Quick start

```bash
# Después de varias sesiones X-DD:
python3 scripts/xdd-state.py evolve --generate
# → Crea propuestas en tabla evolutions con AHE fields

# Trace summary (Experience layer)
python3 scripts/xdd-trace-summarize.py last --depth=detail

# Frozen transfer experiment (Component layer)
python3 scripts/xdd-frozen-transfer.py run \
  --source=. --target=/tmp/test-project --dry-run
```

## 3-layer observability

### Component layer
Cada skill/agent/command propuesto:
- Versionado en git
- Diff explícito antes de promote
- Revertible
- Tracked en `evolutions.cluster_id`

### Experience layer
Traces N-millones tokens → layered markdown report:
- `summary`: event counts + timestamps
- `detail`: + samples top 5 event types
- `full`: + all events excerpts

Output `xdd-trace-summarize.py` consumible por humano + propuestas /evolve.

### Decision layer
Cada propuesta en tabla `evolutions`:

| Campo | Significado |
|---|---|
| `rationale_evidence` | JSON: instinct IDs + trace excerpts + categoría dist |
| `predicted_impact` | "≥10% improvement en pass_rate workflows tocando X" |
| `falsification_metric` | "meta-eval compare next 3 runs delta ≥ +0.10" |
| `falsification_outcome` | null → passed/failed (next iter llena) |

## Frozen transfer experiments

Hipótesis NexAU-AHE: harness evolucionado en benchmark A debería transferir a benchmark B sin re-train.

```bash
# Source = donde aprendió. Target = donde validar transfer.
python3 scripts/xdd-frozen-transfer.py run \
  --source=/path/to/project-trained-on-tb2 \
  --target=/path/to/project-with-swe-bench

# Luego:
cd /path/to/project-with-swe-bench
python3 scripts/xdd-eval.py run --suite=external/swe-bench-verified
python3 scripts/xdd-meta-eval.py compare --last=2 --suite=external/swe-bench-verified
# Si delta ≥ +0.10 → transfer SUCCESS
```

## Flujo end-to-end

```
1. X-DD usa proyectos → hooks stop-pattern-extraction → instincts en SQLite
2. /evolve --generate → crea propuesta con rationale_evidence + predicted_impact + falsification_metric
3. Humano aprueba (T6.1 mitigation)
4. Skill/agent/command commited
5. Próxima iteración:
   - Eval-harness corre suite
   - xdd-meta-eval compare verifica delta vs baseline
   - UPDATE evolutions SET falsification_outcome = 'passed' o 'failed'
6. Patrón de "falsificación fail" → revertir promote, marcar instinct para re-clustering
```

## Política T6.1

Mantenida: `/evolve` NUNCA auto-promueve. Humano siempre firma.

## Schema migration

`_migrate_evolutions(conn)` añade 4 columnas idempotente. DBs Sprint 9-21 upgrade sin breaking.

## Referencias
- [ADR-0029 AHE-style evolve](adr/0029-ahe-evolve-3-layer-observability.md)
- NexAU-AHE: https://github.com/china-qijizhifeng/agentic-harness-engineering
- Sprint 9 base (continuous learning)
- Sprint 18 (trace replay → input Experience layer)
- Sprint 20 (meta-eval → verifica falsification)
