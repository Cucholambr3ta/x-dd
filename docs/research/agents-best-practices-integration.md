# Research — agents-best-practices integration

**Fecha:** 2026-05-27
**Repo:** https://github.com/DenisSergeevitch/agents-best-practices
**License:** MIT
**Sprint context:** S23

## TL;DR
Provider-neutral skill spec + concise prompt format + tool atomic+idempotent patterns. X-DD adopta en SKILL.md frontmatter + CONTRIBUTING.md.

## Adopciones concretas

1. **`origin:` field en SKILL.md frontmatter** — explicito x-dd | community | external
2. **`inspired_by:`** — cita upstream explícita (ya hecho desde Sprint 10)
3. **Triggers neutrales** — no Claude-specific, no Codex-specific
4. **Tool atomic+idempotent** — ya documentado en code-as-tool workflow (Sprint 19)

## CONTRIBUTING.md additions futuras (post-release)

- Sección "Provider-neutral skill checklist" basada en agents-best-practices
- Linter `scripts/xdd-skills-lint.py` que valida neutrality (no provider-specific strings)

## Referencias
- agents-best-practices: https://github.com/DenisSergeevitch/agents-best-practices
- [docs/SKILLS_INTEROP.md](../SKILLS_INTEROP.md)
- [ADR-0032](../adr/0032-skills-migration-plan-act-adapt-orch.md)
