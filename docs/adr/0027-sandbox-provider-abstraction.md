# ADR-0027 — Sandbox provider abstraction (skill xdd-sandbox)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 21

## Context

Hoy un agente con X-DD puede ejecutar `bash` directamente en host. Sin sandbox = exposición total a side effects de código LLM-generated.

Research identificó ecosistema rico:
- E2B (Apache-2.0): cloud sandbox + browser + desktop
- Daytona (Apache-2.0): dev environments AI-generated
- Microsandbox (MIT): rootless local VM
- docker (Apache-2.0): container isolation universal
- Picrew enumera 25+ sandbox-related projects

X-DD necesita capa abstracta provider-agnostic.

## Decision

Sprint 21 introduce `skills/xdd-sandbox/SKILL.md`:

- 5 backends declarados: `e2b`, `daytona`, `microsandbox`, `docker`, `none`
- Configurado vía `xdd.config.yml` sección `sandbox:`
- `auto_for_intents: [lang_exec, filesystem_delete, fork_subprocess]` — sandbox triggered automático cuando intent matches
- X-DD NO bundle ninguno: cada backend requiere setup opt-in del usuario

## Alternatives considered

- **Bundlear docker dep:** rechazado. Docker daemon no siempre disponible (CI containers, ARM, etc.).
- **Solo E2B (cloud):** rechazado. Vendor lock + costo.
- **Implementar sandbox propio X-DD:** rechazado. Reimplementar 5 sandbox runtimes = scope creep masivo.

## Consequences

### Positivas
- ✅ Code untrusted (LLM-generated, eval, etc.) ejecuta aislado
- ✅ Provider-agnostic: equipos eligen tradeoff cost/privacy/perf
- ✅ Auto-trigger por intent classification (xdd-intent + auto_for_intents)
- ✅ Compat con authz: `xdd-authz` decide IF, `xdd-sandbox` decide HOW

### Negativas
- ⚠️ Skill es spec, no runtime. Implementación per-backend pendiente para v0.2.0
- ⚠️ `none` default es inseguro — recomendar `docker` mínimo en docs
- ⚠️ Network deny estricto puede romper workflows legítimos (curl APIs)

## Related
- ADR-0028 Permission model (xdd-intent + xdd-authz, companion)
- Sprint 12 AgentShield (audit estático complementa runtime sandbox)
- Sprint 9/22 continuous learning (sandbox refuerza confianza de skills auto-generadas)

## References
- E2B: https://e2b.dev
- Daytona: https://daytona.io
- Microsandbox: https://github.com/microsandbox/microsandbox
- Picrew sandbox section: 25 sandbox tools enumerados
