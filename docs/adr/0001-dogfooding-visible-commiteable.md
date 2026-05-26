# ADR-0001: Dogfooding visible y commiteable

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

X-DD es un framework de proceso. Su mayor riesgo de adopción es el escepticismo razonable: "¿esto funciona realmente o son solo plantillas?". La forma más fuerte de prueba es **aplicarse a sí mismo en público**.

Pregunta abierta: ¿qué tan visibles deben ser los artefactos del propio X-DD aplicado a X-DD?

Tres opciones consideradas:
1. Todo commiteable y público (`.xdd/`, `memoria.md`, `lecciones.md`, `docs/adr/`, `PROJ-MASTER-PLAN.md`, `docs/CHANGELOG.md`, `RELEASES/`).
2. Parcial: ADRs y CHANGELOG públicos; `.xdd/` y memoria local-only (gitignored).
3. Mínimo: solo CHANGELOG y release notes públicos.

## Decisión

**Todo visible y commiteable.** El repo público debe demostrar el sistema en acción: fases con `.status=APROBADO` firmadas, ADRs Nygard, Gantt Mermaid, CHANGELOG estructurado, retro al final del release.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Parcial | Repo más limpio | Pierde el efecto demostrativo principal | El "mostrar el sistema" es el diferenciador |
| Mínimo | Mismo aspecto que otros repos OSS | Indistinguible de un repo que no usa X-DD | Anula la propuesta de valor |

## Consecuencias

- **Positivas:** un visitante del repo ve X-DD funcionando contra X-DD. Diferenciador real frente a otros frameworks.
- **Negativas / Trade-offs:** el repo carga más peso (artefactos de fase + ADRs). Aceptable: son archivos markdown, no binarios.
- **Neutras:** `.xdd/.gate-key` queda gitignored (ADR-0009).

## Plan de revisión

Revisitar si los artefactos crecen a >5 MB o si algún archivo expone PII del maintainer. Nada planeado para v0.1.0.
