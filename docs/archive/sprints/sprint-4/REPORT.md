# Sprint 4 — Build Report (Gate keeper HMAC ⭐)

> Fase 4-Build (2/5). **El diferenciador real del framework**: gates auditables.

## Tareas MEJORAS abordadas
- **2.1** — `.xdd/<fase>/` con estados.
- **2.2** — `xdd-gate.py` con `validate|transition|approve`.
- **2.3** — Patrón de integración en workflows (`docs/GATE.md`).
- **Sobre-mejora ADR-0006** — Firma **HMAC-SHA256** sobre tuple canónico (`phase, sorted_checksums, approver, timestamp`).

## Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| Gate keeper | `scripts/xdd-gate.py` | ✅ 5 subcomandos + `--json` + Python ≥3.9 |
| Tests pytest | `tests/test_gate.py` | ✅ **17/17 verdes** |
| .gitignore | `.gitignore` | ✅ `.xdd/.gate-key` gitignored |
| Documentación | `docs/GATE.md` | ✅ uso, rotación, amenazas mitigadas |
| Sub-reporte | `.xdd/build/sprint-4/REPORT.md` | ✅ este archivo |

## Dogfooding visible

Las 3 fases ya completadas de X-DD aplicado a sí mismo están **APROBADAS y FIRMADAS**:

```
✓ briefing  APROBADO  (firma cffaf210...)
✓ spec      APROBADO  (firma 4fc4d8e6...)
✓ plan      APROBADO  (firma 232d9368...)
```

Transiciones validadas:
```
briefing → spec  ✓
spec → plan      ✓
plan → build     ✓
```

## Validaciones

```bash
# Tests del gate
python3 -m pytest tests/test_gate.py -v
# → 17 passed in 0.09s

# Status del propio X-DD
python3 scripts/xdd-gate.py status
# → briefing APROBADO, spec APROBADO, plan APROBADO, build MISSING (en curso)

# Lint y doctor verdes
bash scripts/lint-workflows.sh
bash scripts/xdd-doctor.sh
```

## Cobertura del modelo de amenazas

Mitiga las siguientes amenazas de [.xdd/spec/THREATS.md](../../spec/THREATS.md):

- **T1.1** (Spoofing de approver) — firma incluye approver
- **T2.1** (Edición manual de `.status`) — firma incluye phase+status implícitamente
- **T2.2** (Modificación post-aprobación de artefactos) — checksums recalculados detectan
- **T3.1** (Repudiation) — `.approvers` append-only + firma
- **V4** (Gate sin firma criptográfica) — **resuelto completamente**

## Próximo paso
**Sprint 5 — Registry tipado de agentes**. El registry alimentará tanto a workflows como al MCP server (Sprint 6).
