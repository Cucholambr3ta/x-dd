# ⚙️ Catálogo Maestro de Workflows: Ecosistema X-DD

Este documento describe los **29 workflows operativos** configurados en `.agent/workflows/`, explicando cómo guían el ciclo de vida del desarrollo agéntico e interactúan con la memoria local de **MemPalace**.

---

## 🚀 Listado General de Workflows Activos

Los workflows son guías ejecutables en formato Markdown que definen flujos paso a paso para resolver tareas de desarrollo específicas. Se invocan mediante comandos o llamadas directas en la sesión del agente:

### 1. Orquestación y Construcción Principal
*   **`/x-dd` (`x-dd.md`)**: El orquestador principal y Team Lead. Sincroniza el estado del proyecto actual, lee la memoria viva y prepara el plan del día.
*   **`/x-dd-build` (`x-dd-build.md`)**: Workflow maestro para la fase de construcción. Implementa código siguiendo estándares inmutables de desarrollo.
*   **`/x-dd-ingest` (`x-dd-ingest.md`)**: Ingesta universal de documentos técnicos para convertirlos a formato agnóstico legible por IA.
*   **`/x-dd-trace` (`x-dd-trace.md`)**: Sincroniza y traza el progreso en el diagrama de Gantt del proyecto y el Changelog oficial.
*   **`/cierre-fase` (`cierre-fase.md`)**: Ejecuta el cierre formal de una fase de desarrollo. Actualiza la memoria viva (`memoria.md`) y exporta las lecciones al palacio de memoria.

### 2. Planificación y Gestión de Requisitos
*   **`/fase-requisitos` (`fase-requisitos.md`)**: Auditoría y descomposición de requerimientos de negocio en features técnicas priorizadas.
*   **`/plan-fases` (`plan-fases.md`)**: Estructura el desarrollo en fases incrementales alineadas con RICE scores.
*   **`/analisis-impacto` (`analisis-impacto.md`)**: Evalúa los efectos secundarios de los cambios propuestos en los módulos existentes del sistema.
*   **`/mejorar-prompt` (`mejorar-prompt.md`)**: Refina las instrucciones operativas del agente para tareas altamente específicas.

### 3. Sincronización y Memoria (MemPalace Loci)
*   **`/mempalace-sync` (`mempalace-sync.md`)**: Sincroniza bidireccionalmente el código local del workspace con el Palacio de la Memoria de **MemPalace** (`mempalace mine`), actualizando el mapa de grafos de dependencias e indexando las lecciones del día en la base de datos de conocimiento de forma automatizada.

### 4. Aseguramiento de Calidad y Pruebas Estructuradas
*   **`/qa-review` (`qa-review.md`)**: Ejecución de revisiones por pares concurrentes y validación de código pre-release en tres niveles (estética, lógica y rendimiento).
*   **`/generate-unit-tests` (`generate-unit-tests.md`)**: Generación automatizada de pruebas unitarias con mocks para obtener coberturas mínimas del 80%.
*   **`/pruebas-humo` (`pruebas-humo.md`)**: Pruebas rápidas de humo para validar que el despliegue inicial compile y levante correctamente.
*   **`/refactor-area` (`refactor-area.md`)**: Refactorización de código legado para simplificar la lógica sin alterar el comportamiento.
*   **`/pruebas-fuzz` (`pruebas-fuzz.md`)**: Inyección destructiva de datos malformados para testear la estabilidad de las APIs.
*   **`/stress-test` (`stress-test.md`)**: Somete el sistema a condiciones extremas de carga para validar SLAs y cuellos de botella.

### 5. Seguridad y SecOps (Auditoría Ofensiva)
*   **`/security-audit` (`security-audit.md`)**: Auditoría de seguridad estática y dinámica (SAST/DAST) simulando vectores de ataque controlados en sandboxes.
*   **`/advanced-agentic-pentesting` (`advanced-agentic-pentesting.md`)**: Workflow de pentesting autónomo liderado por la skill de Shannon para encontrar vulnerabilidades complejas en tiempo de ejecución.
*   **`/secure-isolation-ops` (`secure-isolation-ops.md`)**: Configuración y despliegue de ejecuciones aisladas en contenedores efímeros de Docker para análisis dinámico seguro.
*   **`/dependency-update` (`dependency-update.md`)**: Auditoría proactiva de dependencias y parches de vulnerabilidades conocidas (CVEs).

### 6. Despliegue, Operaciones y Resiliencia
*   **`/deploy-prod` (`deploy-prod.md`)**: Workflow de despliegue seguro a entornos productivos con gates automáticos de sanidad.
*   **`/ci-cd-setup` (`ci-cd-setup.md`)**: Configuración de pipelines automatizados (GitHub Actions / GitLab CI).
*   **`/incidente-ID` (`incidente-ID.md`)**: Respuesta rápida a incidentes en producción (Hotfixes) y contención de daños.
*   **`/rollback` (`rollback.md`)**: Reversión segura y automatizada al último estado estable en producción ante fallos catastróficos.

### 7. Documentación y Utilería de Soporte
*   **`/technical-documentation` (`technical-documentation.md`)**: Generación de documentación técnica detallada en base a la arquitectura del código.
*   **`/skill-template-generator` (`skill-template-generator.md`)**: Plantillas y automatización para mantener la coherencia absoluta entre el código de las skills y su documentación (`SKILL.md`).
*   **`/design-system-builder` (`design-system-builder.md`)**: Generación automatizada de tokens de diseño CSS para mantener la consistencia estética.
*   **`/generar-flujo` (`generar-flujo.md`)**: Generador de archivos de flujos visuales `.canvas`.

---

## 🛠️ Ejecución y Orquestación de Workflows por Hermes Agent

Cuando **Hermes Agent** ejecuta un workflow, sigue un protocolo estricto:
1.  **Lectura del Workflow:** El agente carga la receta del workflow desde `.agent/workflows/[nombre].md`.
2.  **Preparación del Entorno Aislado:** Levanta el entorno en Docker (si el workflow requiere SecOps o ejecución).
3.  **Ejecución con Gates:** Cada paso importante (como `/qa-review`) valida los criterios de aceptación y requiere la confirmación explícita del desarrollador.
4.  **Sincronización:** Una vez completado el workflow, ejecuta `/mempalace-sync` para registrar el éxito y las lecciones aprendidas en los Halls de MemPalace, garantizando que el conocimiento quede permanentemente en tu sistema.
