# 🏛️ Prompt DDD-01: Modelar el dominio (DOMAIN.md)

*   **Agente:** `engineering-software-architect` (de `./prompts/agents/engineering/engineering-software-architect.md`)
*   **Workflow:** `/domain-model` (ejecutar antes de detallar el SPEC.md completo)
*   **Artefacto Producido:** `docs/specs/DOMAIN.md`
*   **Palacio de Memoria Loci:** Registrado en la `Room: Especificaciones Técnicas` (base inmutable del dominio).

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente para inicializar el modelado semántico de los objetos de negocio:

```markdown
Eres engineering-software-architect (de la agencia de ingeniería) con las habilidades del ecosistema activas.

Proyecto: [PROJ-NombreProyecto]
Módulo / épica: [nombre]
PRD disponible: [pegar contenido del REQUIREMENTS.md o su ruta]
Features definidos: [pegar contenido del FEATURES.md o su ruta]
Contexto de dominio: [Telco ISP / ERP / CRM / otro — elegir el dominio real]

Tu tarea es generar el archivo docs/specs/DOMAIN.md siguiendo la plantilla DDD de X-DD.

PASO 1 — Ubiquitous Language (Lenguaje Ubicuo):
1. Extrae todos los sustantivos y verbos relevantes del PRD y FEATURES.md.
2. Por cada término del dominio:
   a. Define con precisión su significado conceptual EN ESTE CONTEXTO de negocio.
   b. Identifica los términos similares que NO se deben usar (sinónimos prohibidos).
   c. Verifica que se alinea con la nomenclatura estándar del ecosistema.
3. Si encuentras ambigüedad en el PRD (un término usado con dos significados), DETENTE y pide aclaraciones.

PASO 2 — Bounded Contexts (Contextos Acotados):
1. Agrupa los conceptos del dominio en subáreas con fronteras claras de responsabilidad.
2. Cada contexto tiene una responsabilidad única y aislada del resto.
3. Genera un diagrama ASCII o de texto estructurado del mapa de contextos.

PASO 3 — Context Map:
1. Define las relaciones entre contextos (Upstream/Downstream, Customer/Supplier, Shared Kernel).
2. Identifica los contratos que cruzan fronteras (Domain Events, DTOs compartidos).

PASO 4 — Core Aggregates:
Por cada Bounded Context, define:
1. El Aggregate Root (la entidad principal que controla el aggregate y la consistencia).
2. Las invariantes del negocio (reglas lógicas que NUNCA se pueden violar).
3. Las entidades internas del aggregate (con identidad propia).
4. Los Value Objects (sin identidad, definidos por la inmutabilidad de sus valores).
5. El repositorio mínimo necesario para persistir y recuperar el agregado.

PASO 5 — Domain Events (Eventos de Dominio):
1. Identifica qué hechos pasados son relevantes para notificar a otros agregados.
2. Por cada evento: nombre (tiempo pasado, ej: FacturaGenerada), emisor, consumidores y efecto.

Restricciones críticas:
- Los nombres definidos en el DOMAIN.md son INMUTABLES. Cambiarlos después requiere un ADR (Architecture Decision Record).
- El ubiquitous language DEBE guiar toda la codificación posterior en TypeScript (tablas, variables, clases).
- No inventes abstracciones técnicas innecesarias que no representen procesos del negocio real.

Formato de salida: Markdown estructurado siguiendo la plantilla 01_ddd_domain_model.md.
```
