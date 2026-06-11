# Memoria Sprint 27 — 2026-06-04

## Hitos

- DOC_STANDARD.md v2.0: criterios cuantitativos (umbrales lineas por tipo, criterios de rechazo, FSM worker-auditor, verificacion bash)
- docs/constitucion.md: 69→388 lineas — 9 articulos, Mermaid pipeline, schema memoria.md, glosario, enmiendas
- docs/GATE.md: 188→555 lineas — FSM stateDiagram-v2, HMAC protocol, threat model completo, recovery procedures
- docs/arquitectura/ARQUITECTURA.md: nuevo — 309 lineas, C4 Context + Container + Component, ADR table, riesgos
- Purga emojis: 0 en 52 docs/ (excl. archive) — Python unicode-safe (sed falla con multibyte)
- 409 tests verdes, shield 0 CRITICAL

## Bloqueos

- sed no maneja emojis ZWJ (Unicode multibyte) correctamente — python3 obligatorio para purga
- FUNCIONALES.md / NO_FUNCIONALES.md no existen en X-DD (son artefactos de proyectos, no del framework)

## Proxima sesion

- Refactorizar X-DD_Integration_Guide.md: atomicidad (1 disciplina = 1 doc)
- Heredar docs mejorados a evol-dd
- Implementar atomicidad como criterio en discipline-check
