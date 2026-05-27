# ADR-0025 — Inspect AI compatibility en xdd-eval

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 20

## Context

Inspect AI (UK AISI, MIT) es el framework eval open-source más adoptado en 2025-2026. Solvers + scorers + MCP support. xdd-eval (Sprint 10) tiene 5 grader types propios pero no compat con Inspect AI.

Gap: equipos que ya usan Inspect AI no pueden traer sus suites a X-DD sin reescribir.

## Decision

Sprint 20 añade `grader_inspect_ai_compat` a `scripts/xdd-eval.py`:

- 3 scorers: `match` (exact), `includes` (case-insensitive substring), `regex`
- Multiple scorers per case (AND semantics: all must pass)
- Case schema compat: `{input, target, output, scorers}`

Suites Inspect AI pueden convertirse a X-DD format via adapter simple (JSONL line per case + grader.yaml `type: inspect_ai_compat`).

## Alternatives considered

- **Import inspect-ai package dep:** rechazado. Heavy + opinionado. Compat solo necesita 3 scorers.
- **Solo `match` scorer:** rechazado. Insuficiente para queries semánticas.
- **No compat, exhortar a usar Inspect AI directo:** rechazado. Equipos quieren single eval harness.

## Consequences

### Positivas
- ✅ Inspect AI suites portables a X-DD sin escribir Python
- ✅ Stdlib pure (regex + str ops)
- ✅ Compat directa con LongMemEval cases que usan `includes` scorer

### Negativas
- ⚠️ No cubre todos los Inspect AI scorers (faltan: F1, BLEU, etc.) — diferidos a v0.2.0
- ⚠️ Solvers de Inspect AI no se importan (solo scorers)

## Implementation Sprint 20

```yaml
# evals/external/longmemeval/grader.yaml
type: inspect_ai_compat
scorers:
  - includes
```

```bash
python3 scripts/xdd-eval.py run --suite=external/longmemeval --runs=1
```

## Related
- ADR-0026 External benchmark integration policy (companion)
- Sprint 10 grader registry
- Inspect AI: https://github.com/UKGovernmentBEIS/inspect_ai
