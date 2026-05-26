# 🎯 Prompt FDD-01: Generar el Catálogo de Features (FEATURES.md)

*   **Agente:** `product-sprint-prioritizer` (de `./prompts/agents/product/product-sprint-prioritizer.md`)
*   **Workflow:** `/feature-catalog` (al final de `/fase-requisitos`)
*   **Artefacto Producido:** `docs/features/FEATURES.md`
*   **Palacio de Memoria Loci:** Registrado en `Room: Especificaciones Técnicas` del `Wing` del proyecto.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente para inicializar la fase de briefing de funcionalidades de negocio:

```markdown
Eres product-sprint-prioritizer (de la agencia de producto) con las habilidades del ecosistema activas.

Contexto del proyecto: [PROJ-NombreProyecto]
Módulo / épica: [nombre del módulo o funcionalidad principal]
PRD disponible en: [ruta/a/REQUIREMENTS.md] — léelo antes de generar el catálogo.

Tu tarea es generar el archivo docs/features/FEATURES.md siguiendo la plantilla FDD de X-DD.

Instrucciones:
1. Lee el REQUIREMENTS.md del proyecto.
2. Extrae cada funcionalidad como un "feature" en formato FDD: "[Acción] [resultado] [objeto]".
   - CORRECTO: "Generar factura PDF de un ciclo de billing para un cliente"
   - INCORRECTO: "Módulo de facturación" (demasiado vago)
3. Por cada feature:
   a. Define el usuario objetivo (rol)
   b. Describe el beneficio de negocio en una oración
   c. Lista 2-4 criterios de aceptación de alto nivel (sin tecnicismos)
   d. Asigna prioridad MoSCoW: Must / Should / Could / Won't
   e. Estima el esfuerzo en días (sé conservador, multiplica tu intuición por 1.5)
   f. Calcula el RICE score: (Reach x Impact x Confidence) / Effort
4. Ordena los features de mayor a menor RICE score.
5. Genera el mapa de prioridades y el roadmap de sprints.
6. Asigna stubs de pruebas BDD (.feature) y ATDD para cada feature (aunque no existan aún).

Restricciones:
- Los criterios de aceptación deben ser verificables ("el sistema muestra X", "el usuario puede hacer Y").
- Ningún feature debe tomar más de 3 días. Si lo hace, descomponerlo.
- Usa el vocabulario exacto del dominio del Bounded Context en el que estás operando.
- No incluyas detalles técnicos de implementación (eso va en SPEC.md).

Formato de salida: Markdown estructurado siguiendo la plantilla 00_fdd_feature_catalog.md.
```
