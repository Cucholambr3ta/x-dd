# Promptfoo compat — X-DD external eval adapter (Sprint 20)

Bridge para correr configs Promptfoo desde xdd-eval.

## Source
- Original: https://github.com/promptfoo/promptfoo (MIT)
- Config-driven testing + red-team evaluation

## Use
```bash
# Si promptfoo CLI instalado:
promptfoo eval -c promptfooconfig.yaml --output=promptfoo-results.json

# Bridge convierte → xdd-eval cases format
python3 scripts/xdd-eval.py run --suite=external/promptfoo-compat --runs=1
```

## Files
- `cases.jsonl`: convertido desde promptfoo output
- `grader.yaml`: usa `inspect_ai_compat` (similar scorers a Promptfoo)
- `promptfooconfig.yaml.example`: ejemplo config Promptfoo
