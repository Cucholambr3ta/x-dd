# External Benchmarks — X-DD (Sprint 20)

X-DD soporta 4 benchmarks externos via adapters thin + grader universal `pass_at_one_external` + meta-eval.

## Benchmarks soportados

| Benchmark | License | Cubre | Subset inicial |
|---|---|---|---|
| [Terminal-Bench 2](https://github.com/laude-institute/terminal-bench) | Apache-2.0 | Coding agents terminal-native | 20 tasks |
| [SWE-bench-Verified](https://github.com/SWE-bench/SWE-bench) | MIT | Real GitHub issues | 50 instances |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | MIT | Config-driven testing | configurable |
| [LongMemEval](https://example.com) | MIT | Long-term memory | configurable |

## Workflow típico

```bash
# 1) Setup external benchmark (one-time)
git clone https://github.com/laude-institute/terminal-bench /tmp/tb2
pip install -e /tmp/tb2

# 2) Run via xdd-eval (adapter convierte output)
python3 scripts/xdd-eval.py run --suite=external/terminal-bench-2 --runs=1

# 3) Set baseline (after first known-good run)
python3 scripts/xdd-meta-eval.py baseline --set --suite=external/terminal-bench-2

# 4) Run weekly + compare trend
python3 scripts/xdd-meta-eval.py compare --last=5 --suite=external/terminal-bench-2
python3 scripts/xdd-meta-eval.py trend --suite=external/terminal-bench-2
```

## Meta-eval (xdd-meta-eval.py)

Compara últimas N runs:
- `improving`: latest > previous + 0.01
- `stable`: |delta| ≤ 0.01
- `regressing`: latest < previous - 0.01 (exit code 1)

Useful para CI guard: si tu evolve introduce regresión vs baseline, CI falla.

## Inspect AI compatibility

`grader_inspect_ai_compat` con 3 scorers: `match`, `includes`, `regex`. Suites Inspect AI portables sin reescribir Python.

## Política

- ❌ X-DD NUNCA bundlea benchmarks externos
- ✅ Adapters thin (cases.jsonl + grader.yaml + README.md setup)
- ✅ Subsets acotados por default (cost compute)
- ✅ Meta-eval compara ciclo a ciclo (alineado AHE iterative loop)

## Referencias
- [ADR-0025 Inspect AI compatibility](adr/0025-inspect-ai-compatibility.md)
- [ADR-0026 External benchmark integration](adr/0026-external-benchmark-integration.md)
