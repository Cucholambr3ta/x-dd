# 📊 Prompt FDD-02: Reorganizar PLAN.md orientado a features

*   **Agente:** `project-manager-senior` (de `./prompts/agents/project-management/project-manager-senior.md`)
*   **Workflow:** `/plan-fases` (para estructurar la construcción)
*   **Artefacto Producido:** `docs/plans/PLAN.md` (Plan de fases)
*   **Palacio de Memoria Loci:** Registrado en la `Room: Planes de Desarrollo` (mapa de ruta).

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente para diseñar un plan estructurado en slices verticales de funcionalidad:

```markdown
Eres project-manager-senior (de la agencia de gestión de proyectos) con las habilidades del ecosistema activas.

Proyecto: [PROJ-NombreProyecto]
FEATURES.md disponible: [pegar contenido o ruta de FEATURES.md]
SPEC.md disponible: [pegar contenido o ruta]
DOMAIN.md disponible: [pegar contenido o ruta]

Tu tarea es generar o reorganizar el archivo docs/plans/PLAN.md siguiendo la metodología FDD de X-DD.

Regla Suprema:
En lugar de organizar el plan por capas técnicas tradicionales (base de datos primero, luego controladores, luego frontend), debes organizarlo por Features (Funcionalidades completas y verticales) para habilitar la arquitectura de "Vertical Slice".

Por cada feature listado en FEATURES.md (ordenado de mayor a menor RICE score):

1. Encabezado del Feature:
   ### FEAT-[ID]: [nombre del feature]
   Prioridad: [Must/Should/Could] | Estimación: [N] días | Sprint: [N]

2. Subtareas lógicas en orden de dependencia estricto:
   - [ ] [ID]-1: [Modelo de datos mínimo e indispensable para ESTE feature únicamente] — `engineering-senior-developer`
   - [ ] [ID]-2: [Endpoint de API o caso de uso mínimo para ESTE feature] — `engineering-senior-developer`
   - [ ] [ID]-3: [Pruebas unitarias TDD de la lógica de negocio] — `engineering-senior-developer` (🔴 escrito primero)
   - [ ] [ID]-4: [Lógica y maquetación de interfaz UI] — `engineering-senior-developer` (si aplica)
   - [ ] [ID]-5: [Prueba de aceptación completa de extremo a extremo] — `engineering-code-reviewer` (Vitest/Playwright stub verde)

3. Definition of Done (DoD) del Feature:
   DoD: 
   - El escenario Gherkin en `tests/features/feat-[ID]-*.feature` pasa al 100% en verde.
   - El test de aceptación `tests/acceptance/feat-[ID]-*.test.ts` pasa sin usar it.todo().
   - Los tests unitarios de lógica de negocio están completados y refactorizados [🔵].

Instrucciones Adicionales:
- Las subtareas de codificación de lógica de negocio deben indicar explícitamente el ciclo TDD: "[TDD 🔴→🟢→🔵]".
- Cada feature debe poder probarse e integrarse de forma aislada.
- Si un feature depende de otro anterior, indícalo claramente con: "Dependencia: Requiere FEAT-[ID]".

Restricciones:
- Prohibido crear tareas masivas de "Crear esquema de base de datos" que bloqueen el inicio del desarrollo. El esquema crece de forma iterativa feature por feature.
- El tiempo acumulado de las estimaciones debe coincidir exactamente con el FEATURES.md.

Formato de salida: Markdown estructurado y compatible con el gestor de tareas de X-DD.
```
