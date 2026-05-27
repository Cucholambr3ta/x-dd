# ADR-0015 — AI pre-commit review (provider-agnostic, skill xdd-ai-review)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 16

## Context

Pre-commit hooks tradicionales corren linters estáticos (shellcheck, eslint, gitleaks). No detectan:
- Race conditions
- Lógica de auth bypass sutil
- Resource leaks
- Test gaps

LLMs sí pueden detectar esos patrones leyendo un diff. Inspiración: **gentleman-guardian-angel** (gga), un pre-commit hook que invoca un proveedor AI.

Gap X-DD: hooks `.agent/hooks/scripts/` no incluyen review AI todavía. Adopters tienen que reinventar la wheel.

## Decision

Sprint 16 introduce `skill xdd-ai-review` provider-agnostic:

- **Skill** `skills/xdd-ai-review/SKILL.md` define el patrón
- Soporta 4 providers: `claude` (Haiku default), `openai` (gpt-4o-mini), `local` (Ollama), `none` (skip)
- Configurado vía `xdd.config.yml` sección `ai_review:`
- Hook pre-commit puede invocar el skill; bloquea commit si findings ≥ `block_on_severity`
- Diff preprocesado: strings que matchean `.gitleaks.toml` se redactan ANTES de enviar al LLM (seguridad)

## Alternatives considered

- **Bundlear gentleman-guardian-angel:** rechazado. License gga = NOASSERT (ambigua). X-DD mantiene MIT pure.
- **Implementar review en Python interno:** rechazado por scope. Mejor delegar al LLM directamente vía MCP/SDK.
- **Solo Claude:** rechazado. Vendor lock-in viola filosofía multi-IDE / multi-provider del Art. 0.

## Consequences

### Positivas
- ✅ Pre-commit AI review como ciudadano de primera clase X-DD
- ✅ Provider-agnostic: equipos eligen su stack (privacy: local; velocidad: Haiku; calidad: gpt-4)
- ✅ Default seguro: redacta secrets antes de enviar al LLM
- ✅ Compatible con `--no-verify` de developer (override consciente, no bypass silencioso)
- ✅ Inspiración registrada (gga) sin contaminar licencia

### Negativas
- ⚠️ Costo per commit (~$0.001 con Haiku) — mitigado: opcional, default disabled
- ⚠️ Latencia ~2-5s por commit con cloud provider — mitigado: local Ollama option
- ⚠️ Skill no incluye runtime ejecutable propio — adopters implementan invocación específica de su provider

## Related

- ADR-0005 MCP como integración preferida
- ADR-0007 Adapters IDE (skill se invoca diferente per-IDE)
- skills/agent-eval/SKILL.md (Sprint 10)
- gga upstream: https://github.com/gentleman-tools/guardian-angel (referencia, no dep)

## References

- Anthropic API: https://docs.anthropic.com
- OpenAI API: https://platform.openai.com/docs
- Ollama: https://ollama.com
