# Context Engineering — X-DD (Sprint 19)

Tres herramientas + 2 skills + 1 workflow para gestionar context budget.

## Quick start

```bash
# 1) Estimate tokens of a file
python3 scripts/xdd-context.py estimate --file=long-prompt.md

# 2) Check vs budget
python3 scripts/xdd-context.py check --tokens=170000 --budget=200000
# exit 0=ok, 1=warning (≥80%), 2=block (≥95%)

# 3) Show current budget config
python3 scripts/xdd-context.py budget --show
```

## Configuración

`xdd.config.yml` (opt-in):

```yaml
context_budget:
  max_tokens: 200000          # default (Claude Opus/Sonnet)
  warning_threshold: 0.80     # warn at 80%
  block_threshold: 0.95       # block at 95%

compaction:
  default_method: auto        # auto | llmlingua | claude_api | truncate | none
  target_reduction: 0.50
  preserve_markers: ["```", "TODO", "FIXME"]

fs_context:
  mcp_provider: none          # none | mirage | custom
```

## 3 estrategias de reducción de tokens

### 1. Compaction (xdd-compact skill)
LLMLingua / Claude API / truncate. Reducción 40-90%.

### 2. Filesystem paradigm (xdd-fs-context skill)
Treat data as mounted filesystem. Agent lazy-loads files.

### 3. Code-as-tool (code-as-tool workflow)
N tool calls → 1 script execution. **98%+ reducción** en batch.

## 6-stage middleware integration

Hook `before_model` (Sprint 18) puede invocar `xdd-context check`:
```bash
# .agent/hooks/scripts/pre-llm-budget.sh
XDD_TOKENS_ESTIMATE=<N>
bash .agent/hooks/scripts/pre-llm-budget.sh
# exit 2 = block call
```

Activación: profile `strict` en `xdd.config.yml`.

## Referencias

- [ADR-0023 Context budget policy](adr/0023-context-budget-policy.md)
- [ADR-0024 Compaction skill provider-agnostic](adr/0024-compaction-skill.md)
- [skills/xdd-compact](../skills/xdd-compact/SKILL.md)
- [skills/xdd-fs-context](../skills/xdd-fs-context/SKILL.md)
- [.agent/workflows/code-as-tool.md](../.agent/workflows/code-as-tool.md)
