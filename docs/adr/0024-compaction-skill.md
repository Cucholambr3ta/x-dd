# ADR-0024 — Compaction skill provider-agnostic (xdd-compact + xdd-fs-context + code-as-tool)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 19

## Context

Sprint 19 introduce budget metering (ADR-0023). Cuando warning trigger, hace falta **reducir tokens** sin perder semántica.

Patterns probados:
- LLMLingua-2 (MIT, Microsoft): compresión semantic-preserving 20x
- Claude Compaction API: server-side summarization
- Code Execution with MCP (ai-boost): 98.7% reducción wrapping N calls en 1 script
- Filesystem-paradigm (Mirage, OpenViking): lazy-load on-demand

X-DD necesita ofrecer las 3 estrategias provider-agnostic.

## Decision

3 skills + 1 workflow:

1. **`skills/xdd-compact/SKILL.md`** — wrapper provider-agnostic
   - 4 methods: `llmlingua` | `claude_api` | `truncate` | `auto`
   - `auto` decide por disponibilidad: LLMLingua local → Claude API → truncate fallback
   - Preserve markers default: ` ``` `, `// IMPORTANT`, `TODO`, `FIXME`
   - Pre-process: redact secrets gitleaks ANTES de compactar

2. **`skills/xdd-fs-context/SKILL.md`** — filesystem-paradigm
   - 3 modes: `local-fs` (zero-dep, .xdd/context/), `mcp-fs` (Mirage o similar), `code-as-tool` (script orquesta)
   - Workflows declarativos referencian `context_dir`, no contenido inline

3. **`.agent/workflows/code-as-tool.md`** — pattern Code Execution with MCP
   - Wrapper de N tool calls homogéneos en 1 Python/Bash
   - Output structured JSON, no prose
   - Reglas: stdlib first, idempotent, error handling, no leaks

4. **`prompts/skills/registry.json`** registra los 3 skills

## Alternatives considered

- **Bundlear LLMLingua dep:** rechazado. Heavy (modelo ML). Opt-in.
- **Solo Claude Compaction (vendor lock):** rechazado. Viola ADR-0005 multi-provider.
- **Hard truncate sin alternativas:** rechazado. Pierde semántica.
- **xdd-fs-context bundle MCP server:** rechazado. Mirage es external; declaramos compat.

## Consequences

### Positivas
- ✅ Cuando context warning, agent tiene paths claros para reducir
- ✅ Provider-agnostic: equipos eligen método según privacy/cost/quality tradeoff
- ✅ `code-as-tool` pattern reduce 98%+ tokens en batch workflows
- ✅ Default seguro: redact secrets pre-compact

### Negativas
- ⚠️ LLMLingua y Claude Compaction requieren setup adicional (no built-in)
- ⚠️ `truncate` fallback pierde middle context — workflows sensibles a orden deben evitar
- ⚠️ `xdd-fs-context` MCP mode depende de Mirage/equivalent (external dep no incluida)

## Implementation Sprint 19

```yaml
# xdd.config.yml
compaction:
  default_method: auto
  target_reduction: 0.50
  preserve_markers: ["```", "// IMPORTANT", "TODO"]

fs_context:
  mcp_provider: none   # local-fs default
```

```bash
# Workflow ejemplo invoca skills
# (real invocation depende del orchestrator)
```

## Related
- ADR-0023 Context budget policy (companion)
- ADR-0005 MCP integration preferida (xdd-fs-context mcp_provider mode)
- ADR-0015 AI pre-commit review (también pre-procesa secrets)
- Sprint 10 (eval-harness): grader `token_count_reduction` ya existe

## References
- LLMLingua: https://github.com/microsoft/LLMLingua (MIT)
- Mirage MCP: https://mirage.dev
- Code Execution with MCP: ai-boost/awesome-harness-engineering
- ByteRover: research paper on Active Context Compression
