# Sprint 9 — Build Report (Continuous Learning)

> Fase 4-Build extensión. Primer sprint del bloque ECC-inspired.
> Habilita auto-extracción de patterns + `/evolve` para promover a artefactos.

## Tareas abordadas
- **Sobre-mejora ECC** — instincts + `/evolve` + SQLite state-store.

## Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| State store | `scripts/xdd-state.py` | ✅ 5 subcomandos + JSON |
| Hook real (no stub) | `.agent/hooks/scripts/stop-pattern-extraction.sh` | ✅ extrae 2 heurísticas |
| Workflow | `.agent/workflows/evolve.md` | ✅ con T6.1 mitigación |
| Catalog | `prompts/workflows/03_workflows_catalog.md` | ✅ sección 9 agregada |
| Tests | `tests/test_state.py` | ✅ **12/12 verdes** |

## Schema instinct

```python
{
  "id": "inst_<sha16>",
  "category": "user_action | auto_trigger | multi_step | tool_use | error_pattern | preference",
  "pattern": "texto descriptivo",
  "context": "opcional",
  "confidence": 0.0-1.0,  # +0.1 cada occurrence, cap 1.0
  "occurrences": int,
  "first_seen": ISO8601,
  "last_seen": ISO8601,
  "promoted": bool,
  "promoted_to": path,
  "source_sessions": [str]
}
```

## Subcomandos xdd-state

| Cmd | Función |
|-----|---------|
| `init` | Crea schema en `~/.xdd/state.db` (override via `XDD_STATE_DB` env) |
| `record-instinct` | Añade/incrementa instinct. Heurística confidence: +0.1/occurrence |
| `list` | Lista filtrable (category, min-confidence, promoted) |
| `evolve` | Cluster simple por categoría → propone tipo (command/skill/agent). `--generate` guarda en tabla evolutions |
| `prune` | Borra instincts viejos low-confidence not-promoted |
| `stats` | Métricas (total, high-conf, promoted, by category, evolutions) |

## /evolve workflow

1. Pre-cond: xdd-state.py existe (perfil con `continuous-learning` module)
2. Detecta clusters ≥3 instincts, conf ≥0.5
3. **Aprobación humana obligatoria** por propuesta (T6.1 — no auto-promote)
4. Generación según `proposed_type`:
   - command → `.agent/workflows/<name>.md`
   - skill → `skills/<name>/SKILL.md` (Sprint 10)
   - agent → `prompts/agents/<cat>/<cat>-<name>.md` + re-migrate + validate + generate-equipo
5. Marcar instincts promoted
6. `/cierre-fase` + commit

## Hook stop:pattern-extraction (no más stub)

Heurísticas v0.1.0:
- Si hubo commits en última hora → registra `user_action: session ended with new commits`
- Si `.status` de fases cambió → registra `multi_step: phase status changed during session`

Más heurísticas en Sprint 10 (skills/) y Sprint 11 (orchestration).

## Opt-out

```bash
export XDD_LEARNING_DISABLED=1  # hook stop:pattern-extraction no escribe
```

## Validaciones

```bash
python3 -m pytest tests/test_state.py -q     # 12/12 verde
python3 -m pytest tests/ -q                  # 62/62 verde total
bats tests/bats/                             # 35/35 verde
bash scripts/lint-workflows.sh               # 0 errores
```

## Cobertura threat model

- **T6.1** (Agente IA aprueba sin permiso humano) — `/evolve` exige aprobación humana **antes** de promover artefacto. Sin esto el sistema podría auto-generar skills sin control.
- **T4.4** (MemPalace indexa secretos) — instincts almacenan solo patrones abstractos, no contenido sensible. Schema fuerza category enum.

## Stats post-implementación

- Tests totales: **109** (97 anteriores + 12 nuevos)
- Workflows totales: **50** (49 + /evolve)
- Scripts nuevos: 1 (`xdd-state.py`)
- Hooks modificados: 1 (de stub a real)

## Próximo paso

**Sprint 10** — Skills (SKILL.md) + Eval-harness + **xdd-talk-compact** (caveman-inspired).
