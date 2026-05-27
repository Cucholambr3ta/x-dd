# Research: awesome-harness-engineering (walkinglabs/awesome-harness-engineering)

**Fecha:** 2026-05-27
**Repo:** https://github.com/walkinglabs/awesome-harness-engineering
**Stars:** 2.7k · **License:** NOASSERT
**Sprint context:** post Sprint 14, antes de Sprint 15

## TL;DR

Lista curada de "harness engineering" — infraestructura wrapping LLMs (no los LLMs). 8 categorías: courses, foundations, context/memory, constraints/guardrails, specs/workflows, evals/observability, benchmarks, runtimes.

Validamos buena parte de la propuesta X-DD; identificamos 3 gaps reales a cerrar.

## Tools comparables a X-DD (orquestadores)

| Tool | Comentario X-DD |
|---|---|
| Claude Agent SDK | Multi-IDE → X-DD usa MCP, no SDK directo (decisión ADR-0005) |
| SWE-agent | Inspectable harness coding agent — relevante para v0.2.0 (replay) |
| deepagents | Middleware patterns — comparar con composition_patterns Sprint 11 |
| AgentKit (Inngest) | Durable workflows — X-DD orchestrate stdlib pure (no Inngest dep) |
| Harbor | Meta-framework eval+improve — comparable con Sprint 9 + /evolve |

**Conclusión:** X-DD ocupa nicho diferenciado (pipeline gated formal + firma HMAC). No hay overlap directo con runtimes anteriores.

## Tools complementarios (evals, observability)

| Tool | Gap o validación X-DD |
|---|---|
| SWE-bench, OSWorld, Terminal-Bench, WebArena | Benchmarks externos — futura suite de eval-harness |
| **Inspect AI** (UK AISI) | Validar enfoque xdd-eval (Sprint 10): solvers + scorers, MCP support — alineado |
| **AgentOps / agenttrace** | **GAP**: X-DD no tiene trace replay session-level |
| **OpenTelemetry Gen AI** | **GAP**: orchestrate.py emite tracing JSON propio, no OTel spans |

## Conceptos validados (no tools)

- **12 Factor Agents** — alineado con constitución X-DD (estado, prompts, pause-resume)
- **AGENTS.md / agent.md** — X-DD compatible vía xdd-adapt.sh
- **Context budget / backpressure** — **GAP**: X-DD asume tokens infinitos
- **Greenfield/Brownfield/Vibecode taxonomy** — útil para docs futuras

## Gaps reales identificados → roadmap

### Para v0.1.0 (Sprints 15-17 ya planeados)
- Ningún ítem nuevo de awesome-harness-engineering merita entrar a v0.1.0 (los Sprints 15-17 ya definidos cubren prioridades estratégicas: monorepo, SDD parity, multi-agent).

### Para v0.2.0 (post-release)
- **OTel Gen AI spans** en `xdd-orchestrate.py` y `xdd-eval.py` — interop con AgentOps/agenttrace
- **Context budget metering** — sección nueva `context_budget:` en xdd.profile.yml + hook que avisa al 80% del budget
- **Session replay** — trace persistente en `.xdd/traces/<session-id>.jsonl` con replay tool

## Conclusión

awesome-harness-engineering valida que X-DD está bien posicionado (no duplicamos categorías existentes) y aporta 3 gaps concretos para v0.2.0. No requiere re-planificación de Sprints 15-17.

## Referencias

- ADR-0005 MCP como integración preferida
- Sprint 10 (eval-harness) → comparar con Inspect AI
- Sprint 11 (orchestration runtime) → OTel pendiente
- Sprint 9 (continuous learning) → comparar con Harbor meta-framework
