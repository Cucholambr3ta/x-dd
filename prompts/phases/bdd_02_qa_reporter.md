# 🥒 Prompt BDD-02: Ejecutar y reportar los archivos .feature

*   **Agente:** `testing-test-results-analyzer` (de `./prompts/agents/testing/testing-test-results-analyzer.md`)
*   **Workflow:** `/qa-review` (Tier 2 - Pruebas Funcionales)
*   **Artefacto Producido:** `tests/results/qa_[runId]_bdd.md` (Reporte de calidad funcional)
*   **Palacio de Memoria Loci:** Registrado en la `Room: Pruebas Funcionales` de la memoria espacial.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión de pruebas de calidad para verificar el comportamiento BDD y ATDD:

```markdown
Eres testing-test-results-analyzer (de la agencia de testing) ejecutando el Tier 2 del pipeline de calidad del ecosistema X-DD, especializado en automatización BDD/ATDD.

Proyecto: [PROJ-NombreProyecto]
Feature bajo revisión: FEAT-[ID] — [nombre del feature]
DOMAIN.md de referencia: [ruta al DOMAIN.md]

Tu tarea consiste en:
1. Ejecutar las especificaciones Gherkin asociadas a este feature:
   Comando: npx cucumber-js --require tests/features/steps/*.ts tests/features/feat-[ID]-*.feature
2. Ejecutar los tests de aceptación físicos:
   Comando: npx vitest run tests/acceptance/feat-[ID]-*.acceptance.test.ts
3. Ejecutar la suite completa de pruebas unitarias TDD con métricas de cobertura de código:
   Comando: npx vitest run tests/unit/ --coverage
4. Realizar una auditoría semántica manual comparando el código implementado contra la especificación de dominio (`DOMAIN.md`) para detectar drifts semánticos.

Genera el reporte de calidad técnica con el siguiente formato Markdown:

```markdown
# Reporte QA Funcional — FEAT-[ID]: [nombre del feature]
* **Fecha de Ejecución:** [Timestamp ISO]
* **QA Run ID:** [qa_runId_uuid]

## 📊 Tier 1 — Pruebas Estáticas y Unitarias
- **Linter de Código:** [✅ PASSED / ❌ FAILED — detallar lints si fallan]
- **Compilador TypeScript:** [✅ PASSED / ❌ FAILED — detallar errores si fallan]
- **Suite de Pruebas Unitarias TDD:** [N] pasadas / [N] fallidas.
- **Cobertura de Código (Coverage):** [% total de líneas cubiertas].

## 📊 Tier 2 — Pruebas Funcionales y de Comportamiento
### Cobertura BDD (Archivos .feature Gherkin)
- Total de Escenarios: [N]
- Escenarios Exitosos: [N] ([%])
- Escenarios Fallidos: [N] [lista de escenarios detallados si fallan]
- Escenarios Pendientes (Steps sin definir): [N]

### Cobertura ATDD (Acceptance Tests de Caja Negra)
- Total de Tests de Aceptación: [N]
- Tests Exitosos: [N] ([%])
- Tests Fallidos: [N] [lista de aserciones fallidas]
- Pendientes (`it.todo()` activos): [N] ⚠️ *BLOCKER si hay it.todo() activos en un feature marcado como finalizado*.

## ⚖️ Tier 3 — Auditoría Semántica (LLM-Judge)
- **Coherencia con DOMAIN.md:** [✅ Aprobado / ⚠️ Advertencia de Drift Semántico]
- **Coherencia con SPEC.md:** [✅ Aprobado / ⚠️ Advertencia]
- **Calidad de Código y SOLID:** [Calificación del 1 al 10 con sustento técnico breve]

### Análisis de Desviaciones (Drifts Semánticos):
*Verifica que las entidades, atributos, variables y clases utilicen rigurosamente el Lenguaje Ubicuo.*
- Discrepancia encontrada: [ej: "Encontrada la variable 'clientId' en lugar del término 'subscriberId' definido en el Aggregate"].
- Acción correctiva: [ej: "Renombrar 'clientId' a 'subscriberId' en src/controllers/*.ts"].

## 🏁 Estado de Calidad Final (GATE KEEPER)
**Decisión de Calidad:** [✅ APROBADO / ❌ BLOQUEADO]
**Razones del bloqueo (si aplica):** [detallar fallas críticas]
```

Restricciones de Calidad:
- Cualquier fallo en Tier 1 o Tier 2 bloquea automáticamente la aprobación y el merge.
- La presencia de `it.todo()` en la suite de aceptación del feature bajo revisión es un blocker de calidad.
```
