# ADR-0026 — External benchmark integration policy

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 20

## Context

Sin benchmarks externos, claims de X-DD ("mejora coding agents") son discurso. Research deep dive identificó 5 benchmarks clave:

1. **Terminal-Bench 2** (Apache-2.0) — coding agents terminal-native, NexAU-AHE reporta 84.7% pass@1
2. **SWE-bench-Verified** (MIT) — real GitHub issues, frozen-harness transfer comprobado
3. **Promptfoo** (MIT) — config-driven testing + red-team
4. **LongMemEval** — memoria de largo plazo (MemPalace 96.6% R@5)
5. **Inspect AI** suite (MIT, UK AISI) — meta framework

## Decision

Sprint 20 introduce:

1. **`grader_pass_at_one_external`** en `scripts/xdd-eval.py` — universal grader para benchmarks externos que producen JSON `{task_id, passed}`.
2. **Suites adapter en `evals/external/<name>/`** — 4 suites scaffolds (terminal-bench-2, swe-bench-verified, promptfoo-compat, longmemeval). Cada uno: `README.md` con setup + `cases.jsonl` placeholder + `grader.yaml`.
3. **`scripts/xdd-meta-eval.py`** — meta-evaluator que compara runs ciclo a ciclo. Comandos: `compare --last=N`, `trend`, `baseline --set/--show`.
4. **Política**: benchmarks externos NO se bundlean. Cada uno tiene setup instructions en su `README.md`. Adapter normaliza output → cases.jsonl X-DD format.

## Alternatives considered

- **Bundlear los 4 benchmarks como deps:** rechazado. Heavy (Terminal-Bench solo trae 500+ MB). License variety (Apache, MIT).
- **Solo 1 benchmark (SWE-bench):** rechazado. Múltiples cubren dimensiones distintas (terminal vs code-fix vs prompt vs memoria).
- **Implementar runners completos en X-DD:** rechazado. Reimplementar = drift de upstream.

## Consequences

### Positivas
- ✅ X-DD reproducible vs claims competidores
- ✅ Meta-eval mide mejora ciclo a ciclo (alineado con AHE iterative loop)
- ✅ Adapters thin: no duplica lógica upstream
- ✅ Suites scaffolds permiten quick-start sin setup completo

### Negativas
- ⚠️ User debe setup external benchmark separadamente (clone repo + install deps)
- ⚠️ Subsets iniciales acotados (20/50 tasks) por costo compute
- ⚠️ Sin running de subsets en CI por default (cost prohibitive)

## Implementation Sprint 20

```bash
# Setup (one-time)
git clone https://github.com/laude-institute/terminal-bench /tmp/tb2
pip install -e /tmp/tb2

# Run benchmark via X-DD
python3 scripts/xdd-eval.py run --suite=external/terminal-bench-2 --runs=1

# Meta-eval
python3 scripts/xdd-meta-eval.py baseline --set --suite=external/terminal-bench-2
# ... corre eval semanal ...
python3 scripts/xdd-meta-eval.py compare --last=5 --suite=external/terminal-bench-2
python3 scripts/xdd-meta-eval.py trend --suite=external/terminal-bench-2
```

## Related
- ADR-0025 Inspect AI compatibility (companion)
- ADR-0029 AHE-style /evolve (Sprint 22 usa meta-eval para falsification check)
- Sprint 10 (eval-harness base)

## References
- Terminal-Bench 2: https://github.com/laude-institute/terminal-bench
- SWE-bench: https://github.com/SWE-bench/SWE-bench
- Promptfoo: https://github.com/promptfoo/promptfoo
- LongMemEval: research paper 2024
- Harbor: https://github.com/anthropics/harbor (generalized harness eval)
