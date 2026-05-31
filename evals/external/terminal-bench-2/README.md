# Terminal-Bench 2 — X-DD external eval adapter (Sprint 20)

Benchmark Terminal-Bench 2.0 para coding agents: tareas terminal-native long-horizon.

## Source
- Original: https://github.com/laude-institute/terminal-bench (Apache-2.0)
- NexAU-AHE reports: 84.7% pass@1 con GPT-5.5 + harness evolucionado

## Setup local

```bash
# 1) Clone Terminal-Bench (en directorio adjacent al X-DD project)
git clone https://github.com/laude-institute/terminal-bench /tmp/terminal-bench
cd /tmp/terminal-bench
pip install -e .

# 2) Subset 20 tasks initial (avoiding heavy compute):
# Edit subset.json para los IDs a correr

# 3) Run via xdd-eval (adapter Python convierte resultados → grader pass_at_one_external)
python3 scripts/xdd-eval.py run --suite=external/terminal-bench-2 --runs=1
```

## Architecture

X-DD no bundle Terminal-Bench. Adapter consume su output JSON y normaliza:

```
Terminal-Bench output: {"task_id": "X", "passed": true, "stdout": "...", "duration": 42}
                  ↓ adapter
xdd-eval case: {"task_id": "X", "actual_pass": true, "expected_outcome": "pass"}
                  ↓ grader pass_at_one_external
Result: pass / fail
```

## subset.json

Lista de task_ids a correr (default: primeros 20 alfabético).

## Files

- `cases.jsonl`: lista de casos a evaluar (1 line = 1 task)
- `grader.json`: config grader (`type: pass_at_one_external`)
- `subset.json`: subset selection
- `README.md`: este archivo
