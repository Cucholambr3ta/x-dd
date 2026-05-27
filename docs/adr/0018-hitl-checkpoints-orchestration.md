# ADR-0018 — HITL checkpoints en orchestration runtime

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 17

## Context

Mastra (NOASSERT, 24k⭐) popularizó **HITL checkpoints**: puntos en un workflow multi-agent donde el runtime se pausa esperando aprobación humana antes de continuar.

X-DD ya tiene aprobación humana en gates (Art. 2 + Sprint 4 HMAC) pero **no a nivel de workflow paso-a-paso** dentro de un `composition_pattern`. Si un pattern tiene `sequential: [lead, specialist_A, specialist_B]`, no hay forma de bloquear entre lead y specialist_A esperando humano.

Caso de uso real: workflow "deploy-prod" debe pausar después de `qa-review` esperando que un humano apruebe "go for prod".

## Decision

Sprint 17 añade campos opcionales a composition_patterns:
- `hitl_after: "lead" | "specialist" | "sync_point"` — pausar después de este role
- `hitl_prompt: "string"` — texto que el orquestador presenta al humano
- `hitl_required: bool` — si true, pause es obligatoria; si false, advisory

Runtime: `scripts/xdd-orchestrate.py:has_hitl_checkpoint()` devuelve dict checkpoint cuando aplica. El runtime inserta el checkpoint en `results` con role `hitl_checkpoint`. **El orquestador real** (Claude Code, OpenCode, etc.) interpreta este dict y prompts al humano vía su UI.

X-DD no fuerza una UX específica de prompt (queda al orchestrator). Solo declara que el checkpoint existe.

## Alternatives considered

- **HITL como gate firmado:** rechazado. Gates son por fase, no por step dentro de pattern.
- **Hardcoded UX (CLI input):** rechazado. Acopla a un orquestador específico.
- **Skip HITL en X-DD, delegar 100% al orchestrator:** rechazado. Sin metadata declarativa el orchestrator no sabe DÓNDE pausar.

## Consequences

### Positivas
- ✅ Workflows complejos (deploy, release, migration) pueden pausar paso a paso
- ✅ Declarativo en composition_patterns → versionable, auditable
- ✅ Compatible con orquestadores existentes (cada uno implementa la UX del prompt)
- ✅ Backwards compatible: patterns sin `hitl_after` siguen funcionando igual

### Negativas
- ⚠️ Cumplimiento real depende del orquestador (X-DD no puede forzar pausa si el orchestrator lo ignora)
- ⚠️ Sin timeout especificado → checkpoint puede bloquear indefinidamente
- ⚠️ No incluye persistencia de la respuesta humana (qué se aprobó, por quién) → deferred a workflow superior

## Implementation Sprint 17

```python
# pattern example
{
  "name": "deploy_with_hitl",
  "orchestration": "sequential",
  "lead": "engineering-deploy-engineer",
  "specialists": ["testing-qa-validator", "ops-prod-deployer"],
  "hitl_after": "lead",
  "hitl_prompt": "Lead aprobó deploy plan. ¿Continuar con QA validator + prod deployer?",
  "hitl_required": true
}
```

## Related
- ADR-0006 HMAC gates (HITL es complementario, no reemplaza)
- ADR-0016 Party Mode (party no usa HITL por design)
- Sprint 11 (orchestration base)
- Mastra HITL inspiración: https://mastra.ai
