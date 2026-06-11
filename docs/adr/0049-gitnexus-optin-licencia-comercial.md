# ADR-0049: GitNexus opt-in por licencia comercial (PolyForm-NC)

**Estado:** Aceptado (implementado v0.2.0)
**Fecha:** 2026-05-31
**Sprint:** v0.2 S4
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

GitNexus se integra como *code intelligence* opcional de X-DD (post-commit re-index +
`xdd-start` index + instrucciones en CLAUDE.md). Su licencia es **PolyForm Noncommercial**,
que **prohíbe el uso comercial**.

El usuario confirmó que los proyectos paralelos donde usa X-DD **son comerciales**. Hasta
v0.1.x, X-DD ejecutaba GitNexus **automáticamente** si el CLI estaba en PATH (post-commit,
xdd-start). Eso expone al usuario a un incumplimiento de licencia sin que medie una decisión
explícita.

X-DD **no depende de GitNexus en runtime**: los gates, workflows y el pipeline no lo
requieren. Es una capa de navegación/impacto sobre el grafo de código, no parte del flujo.

## Decisión

GitNexus pasa a ser **opt-in explícito** vía `XDD_GITNEXUS=1` (default OFF):

- `scripts/hooks/post-commit`: el bloque `gitnexus analyze` solo corre con `XDD_GITNEXUS=1`.
- `scripts/xdd-start.sh`: el `gitnexus index` solo corre con `XDD_GITNEXUS=1`; si no, imprime
  una línea recordando que es opt-in por licencia.
- `xdd-doctor`: reporta `gitnexus_enabled` (estado de la env var).
- CLAUDE.md: nota opt-in **fuera** del bloque auto-generado `<!-- gitnexus -->`.
- Doc dedicada: `docs/gitnexus-optin.md`.

MemPalace (MIT) sigue por defecto y cubre la continuidad de contexto.

## Consecuencias

- **Positivo:** elimina el riesgo legal por defecto. El uso comercial de X-DD ya no dispara
  GitNexus sin consentimiento. Cumple el principio de "seguro por defecto".
- **Negativo:** sin `XDD_GITNEXUS=1`, se pierde el grafo de código (impacto/navegación por
  símbolos). Mitigación: MemPalace cubre continuidad; para grafo en proyectos comerciales,
  usar una herramienta con licencia permisiva (no acoplada a X-DD).
- El bloque `<!-- gitnexus -->` en CLAUDE.md/AGENTS.md sigue generándose si el usuario corre
  GitNexus manualmente; describe el índice cuando está activo.

## Alternativas descartadas

- **Mantener auto-ejecución:** descartado — riesgo legal en uso comercial confirmado.
- **Eliminar GitNexus del todo:** descartado — útil en proyectos no-comerciales; opt-in
  preserva la opción sin imponerla.
