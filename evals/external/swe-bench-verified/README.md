# SWE-bench-Verified — X-DD external eval adapter (Sprint 20)

Premier coding agent benchmark: real GitHub issues + verified test outcomes.

## Source
- Original: https://github.com/SWE-bench/SWE-bench (MIT)
- Princeton + paper "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
- NexAU-AHE: frozen harness transfer from Terminal-Bench-trained → SWE-bench passes

## Setup local

```bash
git clone https://github.com/SWE-bench/SWE-bench /tmp/swe-bench
cd /tmp/swe-bench
pip install -e .

# subset 50 tasks (instance IDs en subset.json)
python3 scripts/xdd-eval.py run --suite=external/swe-bench-verified --runs=1
```

## Files
- `cases.jsonl`: placeholder con instance_ids (populated by adapter)
- `grader.yaml`: `type: pass_at_one_external`
- `subset.json`: 50 instance_ids subset
- `README.md`
