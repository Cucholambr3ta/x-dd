# 🥒 Prompt BDD-01: Convertir REQUIREMENTS.md en archivos .feature

*   **Agente:** `product-manager` (de `./prompts/agents/product/product-manager.md`)
*   **Workflow:** `/bdd-generate`
*   **Artefacto Producido:** `tests/features/feat-[ID]-[nombre-kebab].feature`
*   **Palacio de Memoria Loci:** Indexado como especificación de comportamiento en la `Room: Pruebas Funcionales`.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente para generar los escenarios de comportamiento del sistema:

```markdown
Eres product-manager (de la agencia de producto) con las habilidades del ecosistema activas.

Contexto del proyecto: [PROJ-NombreProyecto]
Feature a convertir: FEAT-[ID] — [nombre del feature]
Criterios de aceptación fuente: [pegar aquí los CAs de FEATURES.md]
Dominio de referencia: [pegar aquí la sección relevante del DOMAIN.md si existe]

Tu tarea es generar el archivo tests/features/feat-[ID]-[nombre-kebab].feature en formato Gherkin.

Instrucciones:
1. Por cada criterio de aceptación, escribe un Scenario completo con Given / When / Then (Dado / Cuando / Entonces).
2. Identifica el Happy Path como el Scenario principal.
3. Identifica al menos 1 escenario de error (validación o fallo esperado).
4. Identifica al menos 1 escenario de caso borde (valor límite, listas vacías, etc.).
5. Si el mismo flujo aplica a múltiples valores, usa Scenario Outline con Examples.
6. Si todos los escenarios comparten el mismo estado inicial, extráelo a un Background.
7. Agrega el comentario de trazabilidad en la cabecera: FEAT-ID, REQ-ID, SPEC §, DOMAIN aggregate.

Restricciones de vocabulario:
- Usa EXCLUSIVAMENTE los términos del lenguaje ubicuo del DOMAIN.md.
- Prohibido usar sinónimos de términos de dominio (ej. no "mes de cobro" si el dominio dice "ciclo de billing").
- Los nombres de entidades deben coincidir con los agregados del DOMAIN.md.
- El lenguaje de los escenarios debe ser de negocio, comprensible por usuarios no técnicos.

Restricciones de estructura:
- Máximo 8 escenarios por archivo .feature. Si necesitas más, el feature está mal acotado.
- Máximo 5 pasos por escenario. Si necesitas más, usar Background o refactorizar el comportamiento.
- Los datos de prueba en Examples deben ser representativos, no arbitrarios.

Verifica antes de entregar:
- [ ] ¿Cada criterio de aceptación de FEATURES.md tiene al menos un Scenario?
- [ ] ¿Los scenarios son ejecutables o hay pasos ambiguos que no se pueden automatizar?
- [ ] ¿Los nombres de entidades coinciden exactamente con el DOMAIN.md?

Formato de salida: Gherkin puro (.feature), seguido del esqueleto (skeleton) de step definitions en TypeScript.
```
