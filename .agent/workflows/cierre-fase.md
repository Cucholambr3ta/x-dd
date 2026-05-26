---
description: Ejecución del cierre formal de una fase de desarrollo y actualización de la Memoria Viva de X-DD.
---
# /cierre-fase
**ID:** FLUJO-CIERRE | **Versión:** 1.1 | **Agente:** Architect & QA-Reviewer
**Misión:** Certificar el éxito de la fase y asegurar la persistencia del conocimiento (Learning Loop).

## 1. DESTILACIÓN DE LOGROS
- Resume los hitos alcanzados en la fase actual.
- Verifica contra el **Plan de Implementación** que todo esté marcado como `[x]`.

## 2. BUCLE DE APRENDIZAJE (POST-MORTEM)
- Identifica cualquier error, bloqueo o "gotcha" técnico que ocurrió durante el desarrollo.
- **Registro**: Si el error es nuevo, añádelo a `lecciones.md` con su síntoma, causa y solución.
- **Evolución**: Si la solución es reutilizable, propón al usuario crear una nueva skill en `.agent/skills/`.

## 3. ACTUALIZACIÓN DE MANIFIESTOS
- Actualiza `memoria.md` con el log de la sesión.
- Actualiza `CLAUDE.md` con el nuevo "Estado Actual" y "Próximo Hito".

## 4. CERTIFICACIÓN DE CALIDAD
- Genera un reporte rápido de QA:
  - ¿Drift detectado? (Sí/No)
  - ¿Tests pasando? (Sí/No)
  - ¿Estética premium validada? (Sí/No)

## 5. SELLO DE CIERRE
- Archiva los planes completados de `/docs/plans` a `/docs/plans/archive/` (opcional).
- Termina con el Timestamp y el estatus final del proyecto.

---
*Driven by X-DD Learning Loop*