# Sprint 10 — Build Report (Skills + Eval-harness + xdd-talk-compact)

> Fase 4-Build extensión (2/5 del bloque ECC-inspired).

## Entregables
| Artefacto | Path | Estado |
|---|---|---|
| Skill compresión | `skills/xdd-talk-compact/SKILL.md` | ✅ 3 niveles (lite/standard/ultra) |
| Skill eval | `skills/agent-eval/SKILL.md` | ✅ 5 grader types |
| Eval harness | `scripts/xdd-eval.py` | ✅ list/run/show + --ci |
| Registry skills | `prompts/skills/registry.json` + schema | ✅ |
| Eval suite | `evals/xdd-talk-compact/cases.jsonl + grader.yaml` | ✅ 5/5 cases, ≥50% reduction |
| Tests pytest | `tests/test_eval.py` | ✅ **17 tests verdes (79 total)** |

## Grader types implementados
1. `structural` — regex match
2. `behavioral` — required_keywords presentes
3. `output_match` — exact equality
4. `pass_at_k` — k runs, threshold % pasa
5. `token_count_reduction` — reducción vs baseline (con ignore_code_blocks)

## Validaciones
```bash
python3 scripts/xdd-eval.py run --all --ci    # 1/1 suite all OK
python3 -m pytest tests/ -q                    # 79/79 verde
bats tests/bats/                               # 35/35 verde
```

## Atribución
- xdd-talk-compact inspirado en caveman (juliusbrussee/caveman, MIT, 65k stars). NO copia verbatim.
- agent-eval inspirado en ECC `agent-eval` skill (MIT).

## Próximo
Sprint 11 — Multi-agent orchestration runtime.
