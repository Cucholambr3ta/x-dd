# Lecciones Sprint 26 — 2026-06-04

> Formato: CATEGORIA / Contexto / Problema / Causa raiz / Leccion / Aplica a.

### [HERRAMIENTAS] argparse global args deben ir ANTES del subcomando
**Contexto:** Nuevo subcomando sprint-close en xdd-memory.py con arg global --project.
**Problema:** `xdd-memory.py sprint-close --sprint=01 --project=.` falla. Debe ser `xdd-memory.py --project=. sprint-close --sprint=01`.
**Causa raiz:** argparse no hereda args globales al subparser si se pasan despues del subcomando.
**Leccion:** Documentar en --help que args globales van ANTES del subcomando. Tests directos no detectan esto — añadir test via argv.
**Aplica a:** Toda CLI con argparse + subparsers en X-DD.

### [PROCESO] Separar lecciones/memoria por sprint desde inicio del proyecto
**Contexto:** Inc 5 implementa sprint-close para reemplazar archivos monoliticos.
**Problema:** Un solo lecciones.md de 350+ lineas sin estructura temporal.
**Causa raiz:** El patron journal diario de xdd-memory.py no se extrapoló a lecciones de proyecto.
**Leccion:** Usar acuerdos/lecciones/sprint-NN.md desde el primer sprint. MEMORY.md para hechos persistentes. Backward compat mantiene root lecciones.md.
**Aplica a:** Todos los proyectos generados con X-DD.

### [DOMINIO] Historias de usuario necesitan minimo 50 tareas atomicas para evitar gaps de implementacion
**Contexto:** Inc 6 define checklist minimo de 50 tareas por historia.
**Problema:** Checklists cortos (5-10 tareas) generan implementaciones incompletas porque el agente "asume" pasos intermedios.
**Causa raiz:** Sin granularidad atomica, el agente puede marcar una historia como completa habiendo omitido tests, observabilidad, o controles de seguridad.
**Leccion:** Minimo 50 tareas por historia — TDD (tests primero), STDD (security tests), observabilidad, docs, code review. El auditor rechaza checklists por debajo del umbral. Sin excepcion.
**Aplica a:** /xdd historias workflow y cualquier checklist de historia en proyectos X-DD.
