# LongMemEval — X-DD external eval adapter (Sprint 20)

Benchmark de memoria de largo plazo para LLMs.

## Source
- Original LongMemEval: paper 2024
- MemPalace reports: 96.6% R@5

## Use con MemPalace integration

```bash
# Setup MemPalace (X-DD dep externa recomendada)
pip install mempalace

# Inject test data + query
python3 scripts/xdd-eval.py run --suite=external/longmemeval --runs=1
```

## Files
- `cases.jsonl`: queries + expected recalled items
- `grader.yaml`: usa `inspect_ai_compat` con scorer `includes` (recall-style)
