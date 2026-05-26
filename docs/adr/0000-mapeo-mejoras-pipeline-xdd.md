# ADR-0000: Mapeo MEJORAS-X-DD ↔ pipeline X-DD

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia (maintainer), Claude (asesor de arquitectura)

## Contexto

El plan `MEJORAS-X-DD.md` v1.1 organiza el trabajo en 13 capítulos / ~70 tareas. La pregunta abierta era cómo mapear ese plan al pipeline X-DD de 6 fases (Constitución Art. 9 prohíbe agregar fases nuevas) sin caer en burocracia ni perder dogfooding.

Tres opciones consideradas:
1. Tratar MEJORAS como un único feature macro: una sola pasada por las 6 fases.
2. Cada sprint = su propio ciclo X-DD completo (6 fases × 8 sprints = 48 mini-ciclos).
3. Híbrido: briefing/spec/plan macro; build iterativo; QA y retro al final.

## Decisión

**Una pasada completa por las 6 fases para todo MEJORAS.** Sprints 0-2 = Fase 1-3 (Briefing/Spec/Plan). Sprints 3-7 = Fase 4-Build (iterativa). Sprint 8 = Fase 5-QA + Fase 6-Retro + release v0.1.0.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Mini-ciclos por sprint | Máximo dogfooding | 48 SPEC/PLAN/QA duplicados; burocracia masiva | Sobrepasa esfuerzo razonable |
| Híbrido | Punto medio | Mismo resultado final que opción 1, pero más complejo de explicar | La opción 1 ya tiene QA continuo por sprint vía `/cierre-fase` |

## Consecuencias

- **Positivas:** un solo `.xdd/briefing/SPEC.md` macro; `.xdd/plan/PLAN.md` único; coherencia con Constitución.
- **Negativas / Trade-offs:** la Fase 4-Build dura 5 sprints (riesgo de scope creep). Mitigación: cada sprint cierra con `/cierre-fase` y entrada en `CHANGELOG.md`.
- **Neutras:** los 5 sprints de Build se trazan en `.xdd/build/sprint-N/` con sub-reportes.

## Plan de revisión

Revisitar si para v0.2.0 el scope crece a >10 sprints (ahí conviene partir en releases incrementales y aplicar X-DD por release).
