# 🔴 Prompt TDD-01: Ciclo Rojo-Verde-Refactor para una función

*   **Agente:** `engineering-senior-developer` (de `./prompts/agents/engineering/engineering-senior-developer.md`)
*   **Workflow:** `/tdd-cycle` (o integrado en `/x-dd-build`)
*   **Artefacto Producido:** `tests/unit/[nombre-kebab].test.ts` + `src/[ruta]/[nombre-modulo].ts`
*   **Palacio de Memoria Loci:** Indexado como lógica de código e invariantes en la `Room: Código y Lógica`.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión de desarrollo para programar bajo la disciplina estricta de TDD:

```markdown
Eres engineering-senior-developer (de la agencia de ingeniería) con las habilidades del ecosistema activas.

Función a implementar: [nombre de la función o método de clase]
Ubicación final en disco: src/[ruta_del_módulo]/[nombre-archivo].ts
Feature: FEAT-[ID]
Subtarea en PLAN.md: [ID de la subtarea, ej. FEAT-01-2]

Contexto de negocio e invariantes (del DOMAIN.md):
- Ubiquitous language relevante: [pegar aquí términos clave]
- Entidades y Agregados: [Nombre del Agregado]
- Reglas inmutables del aggregate: [listar invariantes]

Comportamiento esperado (de los escenarios BDD):
[pegar los escenarios relevantes del archivo .feature correspondiente]

Ejecuta el ciclo de Test-Driven Development (TDD) estricto en tres fases secuenciales independientes. Reporta después de cada fase:

=========================================
🔴 FASE 1 — ROJO (Test Fallido):
=========================================
1. Diseña la suite de pruebas unitarias en `tests/unit/[nombre-archivo].test.ts`.
2. Estructura cada prueba bajo el patrón AAA (Arrange-Act-Assert).
3. Escribe pruebas para:
   a. El caso principal de éxito (Happy Path).
   b. Validaciones de dominio (invariantes de negocio violadas que lanzan excepciones específicas).
   c. Casos extremos y valores borde (colecciones vacías, nulos, límites numéricos).
4. Importa la función que aún no existe en el archivo fuente para forzar el error de compilación.
5. Ejecuta la suite de pruebas unitarias: `npx vitest run tests/unit/[nombre-archivo].test.ts`
6. REPORTA: "🔴 FASE ROJO: Test escrito. Falla exactamente con el error: [copiar mensaje de error]".

=========================================
🟢 FASE 2 — VERDE (Implementación Mínima):
=========================================
1. Escribe la cantidad MÍNIMA indispensable de código en `src/[ruta_del_módulo]/[nombre-archivo].ts` para que los tests pasen en verde.
2. Está prohibido realizar optimizaciones prematuras o añadir características no testeadas en la fase roja.
3. Asegúrate de tipar estrictamente las firmas usando los tipos de dominio definidos, evitando primitivos planos (`any`, `unknown` sueltos).
4. Lanza excepciones semánticas del negocio, no errores genéricos.
5. Ejecuta los tests unitarios y confirma el éxito.
6. REPORTA: "🟢 FASE VERDE: Código mínimo implementado. Tests unitarios pasando: [N] exitosos, 0 fallidos".

=========================================
🔵 FASE 3 — REFACTOR (Higiene y Limpieza):
=========================================
1. Aplica el checklist de refactorización inmutable del ecosistema X-DD:
   - Nombres claros alineados al lenguaje ubicuo (no abreviaciones crípticas).
   - Principio de Responsabilidad Única (SRP) en cada función.
   - Eliminación de código duplicado (DRY).
   - Modularización de funciones auxiliares.
2. Después de realizar CADA refactorización pequeña, vuelve a correr los tests unitarios de forma inmediata para asegurar que no hay regresiones.
3. REPORTA: "🔵 FASE REFACTOR: Refactorización completada de forma segura. La suite de pruebas sigue pasando al 100% en verde".

Restricciones:
- No uses mockeos para la función que estás implementando (puedes mockear servicios externos si es estrictamente necesario).
- Cero advertencias del compilador de TypeScript.
```
