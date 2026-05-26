# 🧪 Prompt ATDD-01: Generar stubs de acceptance tests

*   **Agente:** `testing-api-tester` (de `./prompts/agents/testing/testing-api-tester.md`)
*   **Workflow:** Al final de `/fase-requisitos`
*   **Artefacto Producido:** `tests/acceptance/feat-[ID]-[nombre-kebab].acceptance.test.ts`
*   **Palacio de Memoria Loci:** Registrado en la `Room: Pruebas Funcionales` de la memoria espacial.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente para generar los esqueletos de las pruebas de aceptación de caja negra:

```markdown
Eres testing-api-tester (de la agencia de testing) con las habilidades del ecosistema activas.

Feature: FEAT-[ID] — [nombre del feature]
Criterios de aceptación:
[pegar aquí los CAs numerados del FEATURES.md]

Stack de testing X-DD: Vitest + TypeScript

Tu tarea es generar el STUB del archivo tests/acceptance/feat-[ID]-[nombre-kebab].acceptance.test.ts.

Un STUB de acceptance test:
- Tiene la estructura completa (describe anidados por CA, it.todo() por cada caso).
- Falla intencionalmente porque no hay implementación real de la lógica.
- Sirve como checklist viviente del progreso del feature.

Instrucciones:
1. Crea un describe principal con el nombre del feature: "FEAT-[ID]: [nombre]"
2. Por cada criterio de aceptación (CA-N), crea un describe anidado: "CA-[N]: [nombre del criterio]"
3. Por cada caso de prueba dentro del CA, crea un it.todo('[verbo] [resultado] cuando [condición]')
4. En el comentario de cabecera del archivo, incluye: FEAT-ID, REQ-ID, SPEC §, DOMAIN aggregate.
5. Agrega el comentario: "Estado: STUB — Falla intencionalmente hasta que FEAT-[ID] esté implementado".

Nomenclatura obligatoria para los it():
- Formato: 'debe [verbo en infinitivo] [resultado observable] cuando [condición o contexto]'
- CORRECTO: 'debe generar un PDF con nombre correcto dado un ciclo cerrado y cliente activo'
- INCORRECTO: 'test factura PDF' (demasiado vago)

Cubre siempre estos tipos de casos:
- Happy path (al menos 1 caso)
- Validación de dominio (errores esperados de negocio)
- Caso borde (valor límite, estado vacío, condición extrema)

Formato de salida: TypeScript con Vitest. Solo el stub con it.todo(), sin implementación real de código.
```
