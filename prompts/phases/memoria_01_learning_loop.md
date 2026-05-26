# 🧠 Prompt MEM-01: Memoria Viva y Bucle de Aprendizaje MemPalace

*   **Agente:** `specialized-chief-of-staff` (de `./prompts/agents/specialized/specialized-chief-of-staff.md`)
*   **Workflow:** `/cierre-fase` (o `/x-dd-trace` retrospectivo)
*   **Artefacto Producido:** Actualización de `memoria.md` (Memoria Viva) + Inyección en los **Halls** de MemPalace.
*   **Palacio de Memoria Loci:** Registrado y guardado en la `Room: Retrospectiva y Aprendizaje` del proyecto actual.

---

## 📝 Instrucciones Operativas para la IA

Copia y pega el siguiente prompt en la sesión del agente al concluir un hito o fase de desarrollo para capitalizar el conocimiento:

```markdown
Eres specialized-chief-of-staff (de la agencia de especialidades) con las habilidades del ecosistema activas.

Proyecto: [PROJ-NombreProyecto]
Fase Completada: [pegar el nombre de la fase o hito cerrado]
Changelog Físico: [pegar el listado de archivos creados, modificados o eliminados]

Tu tarea consiste en realizar el cierre formal de la fase e inyectar el aprendizaje técnico extraído directamente en el Palacio de Memoria (MemPalace) para evitar que futuros agentes cometan los mismos errores o reescriban soluciones existentes.

Sigue rigurosamente estos pasos:

=========================================
🧠 PASO 1 — EXTRACCIÓN DE HECHOS (Halls de MemPalace):
=========================================
1. Identifica qué se construyó exactamente (Wing del proyecto).
2. Analiza los principales desafíos técnicos superados durante el desarrollo:
   - ¿Qué bugs o errores complejos se depuraron? (ej: "Error de tipos con Drizzle ORM al mapear campos JSON").
   - ¿Qué configuraciones o flags de dependencias fueron necesarios? (ej: "Añadir flag --add-host=host.docker.internal al levantar el Docker de Hermes").
3. Sintetiza las lecciones aprendidas en un formato de "Hechos Semánticos" claros y concisos, listos para la API de MemPalace.

=========================================
🧠 PASO 2 — ACTUALIZACIÓN DE MEMORIA.MD:
=========================================
Edita el archivo `memoria.md` en la raíz del proyecto para registrar el fin de la fase con el siguiente bloque Markdown inmutable:

```markdown
### 📅 [Fecha de Cierre] — Cierre de Fase: [Nombre de la Fase]
* **Estado:** ✅ Completado
* **Responsable:** `project-manager-senior`

#### 🔨 Artefactos Entregados:
- [ ] [NEW] [Ruta y enlace a archivos críticos creados]
- [ ] [MODIFY] [Ruta y enlace a archivos modificados]

#### 🎓 Lecciones y Hechos para MemPalace:
1. **[Categoría - ej. Tipado/Docker]:** [Hecho técnico resumido en 1 oración] — *Guardado en Hall: [Nombre del Hall, ej. Configuración]*
2. **[Categoría - ej. Dependencias]:** [Hecho técnico resumido en 1 oración] — *Guardado en Hall: [Nombre del Hall]*
```

=========================================
🧠 PASO 3 — LLAMADA AL CONECTOR MCP MEMPALACE:
=========================================
*(En la sesión agéntica con acceso a la CLI o al servidor MCP de MemPalace)*
1. Registra el Wing si es un proyecto nuevo.
2. Añade los hechos semánticos y lecciones aprendidas llamando a las herramientas del servidor MCP de MemPalace (`python3 -m mempalace.mcp_server` o similar CLI) para poblar el grafo SQLite local:
   - `wing`: [PROJ-NombreProyecto]
   - `room`: [Fase del Pipeline, ej: Fase 4 - TDD e Implementación]
   - `fact`: [Lección o hecho técnico preciso]

REPORTA: "🧠 BUCLE DE APRENDIZAJE COMPLETADO: Memoria Viva actualizada en memoria.md y hechos inyectados físicamente en el grafo SQLite de MemPalace".
```
