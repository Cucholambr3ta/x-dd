# ADR-0014 — SDD parity: /clarify + /cross-validate + constitution.md template

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 16

## Context

Spec-Kit (github.com/github/spec-kit, 106k⭐, MIT) popularizó 3 mecanismos en Spec-Driven Development:
1. `/clarify` — workflow que detecta ambigüedad y bloquea gate
2. `/cross-validate` — workflow que verifica consistencia entre artefactos relacionados
3. `constitution.md` — plantilla per-project con principios no negociables + governance

X-DD ya tiene `docs/constitucion.md` propia (la del framework), pero **no provee plantilla para que proyectos consumidores definan la suya**. Y no tiene workflows equivalentes a `/clarify` ni `/cross-validate`.

Gap real: equipos adoptan Spec-Kit por estos 3 mecanismos. X-DD necesita paridad.

## Decision

Sprint 16 incorpora los 3 mecanismos como **first-class** en X-DD:

1. **`.agent/workflows/clarify.md`**
   - Detecta ambigüedad en SPEC/DOMAIN/PLAN
   - 4 niveles severidad: CRÍTICA / ALTA / MEDIA / BAJA
   - Bloquea gate si quedan CRÍTICAS pendientes
   - Respuestas registradas append-only en `CLARIFICATIONS.md`

2. **`.agent/workflows/cross-validate.md`**
   - Compara pares de artefactos: SPEC↔DOMAIN, PLAN↔FEATURES, DOMAIN↔openapi.yaml, etc.
   - Detecta 3 tipos de drift: MISSING / CONFLICT / ORPHAN
   - Genera REPORT.md + bloquea gate si MISSING o CONFLICT

3. **`templates/constitution.template.md`**
   - 10 artículos: misión, principios, pipeline, stack, calidad, trazabilidad, ambigüedad cero, adaptabilidad, portabilidad, governance
   - Adoptable per-project copiando + editando placeholders
   - Independiente de la constitución del framework X-DD (`docs/constitucion.md`)

## Alternatives considered

- **Importar Spec-Kit como dep:** rechazado. Heavy (106k⭐ con runtime CLI propio). X-DD prefiere workflows markdown puros.
- **Solo `/clarify` (skip cross-validate):** rechazado. Cross-validate aporta valor único (drift detection no cubierto por otro workflow).
- **Constitution como ADR sin template:** rechazado. Plantilla baja barrera de adopción dramaticamente.

## Consequences

### Positivas
- ✅ Paridad funcional con Spec-Kit en las 3 capacidades más valoradas
- ✅ `/clarify` cierra brecha del Art. 7 "Ambigüedad Cero" — ahora ejecutable, no aspiracional
- ✅ `/cross-validate` cierra brecha del Art. 6 "Trazabilidad bidireccional"
- ✅ Plantilla constitución habilita gobernanza formal para proyectos consumidores
- ✅ Workflows son markdown puros (sin runtime extra) — alineado con ADR-0007

### Negativas
- ⚠️ Workflows son guías, no scripts ejecutables — semántica depende del orquestador agéntico
- ⚠️ Constitution template añade fricción inicial — mitigado: opt-in, no obligatorio

## Related

- ADR-0007 Alcance inicial de adapters
- ADR-0011 White-labeling (constitution puede heredar branding)
- Sprint 9 + /evolve (Constitution puede mencionar policy de auto-promote)
- Spec-Kit: https://github.com/github/spec-kit

## References

- Spec-Kit constitution.md examples: https://github.com/github/spec-kit/tree/main/templates
- Constitución X-DD framework: `docs/constitucion.md` (referencia, no plantilla per-project)
