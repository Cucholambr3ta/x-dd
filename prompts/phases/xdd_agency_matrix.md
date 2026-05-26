# 🗺️ Matriz de Orquestación y Gobernanza de Agentes X-DD

Esta matriz define formalmente la asignación de los agentes consolidados locales (`./prompts/agents/`) para la ejecución sistemática de cualquier ciclo de desarrollo guiado por metodologías del ecosistema X-DD (X-DD).

---

## 🏛️ Gobernanza y Asignación de Roles

A continuación se detalla el mapeo exacto de metodologías, fases, roles y los archivos de prompts que inyectan su comportamiento:

| Metodología / Fase | Rol Agéntico Primario | Ruta del Prompt Local | Habilidades Clave del Ecosistema |
| :--- | :--- | :--- | :--- |
| **Gobernanza General** | `specialized-chief-of-staff` | `./prompts/agents/specialized/specialized-chief-of-staff.md` | Orquestación general, alineación con la constitución, coordinación multi-agente. |
| **DDD (Domain-Driven Design)** | `engineering-software-architect` | `./prompts/agents/engineering/engineering-software-architect.md` | Modelado de dominio (`DOMAIN.md`), agregados, bounded contexts, arquitectura limpia. |
| **BDD (Behavior-Driven Development)** | `project-manager-senior` | `./prompts/agents/project-management/project-manager-senior.md` | Generación de escenarios Gherkin (`FEATURES.md`), análisis de casos de negocio. |
| **FDD (Feature-Driven Development)** | `project-manager-senior` | `./prompts/agents/project-management/project-manager-senior.md` | Clasificación de catálogos y priorización en slices verticales (`PLAN.md`). |
| **TDD (Test-Driven Development)** | `engineering-senior-developer` | `./prompts/agents/engineering/engineering-senior-developer.md` | Ciclos estrictos Rojo-Verde-Refactor, Vitest/Jest, mock de datos, SOLID/DRY. |
| **ATDD (Acceptance TDD)** | `engineering-code-reviewer` | `./prompts/agents/engineering/engineering-code-reviewer.md` | Verificación de criterios de aceptación, pruebas de extremo a extremo (E2E), QA. |
| **Security Development (STDD)** | `shannon-secops-expert` | `./prompts/agents/security/shannon-secops-expert.md` | Modelado de amenazas STRIDE (`THREATS.md`), inyección de payloads ofensivos, hardening. |
| **DevSecOps (Pipeline Scan)** | `shannon-secops-expert` | `./prompts/agents/security/shannon-secops-expert.md` | Escaneos de dependencias (SCA), análisis estático (SAST), fugas de secretos. |
| **Bucle de Aprendizaje (Memoria)** | `specialized-chief-of-staff` | `./prompts/agents/specialized/specialized-chief-of-staff.md` | Minado semántico de lecciones aprendidas, inyección en los Halls de MemPalace. |

---

## 🎯 Protocolo de Invocación Portable

Al trabajar en cualquier entorno de desarrollo compatible con X-DD (incluyendo la futura migración a Linux Mint):

1. **Sin Rutas Absolutas:** Toda invocación de agente o herramienta debe cargarse utilizando rutas relativas al directorio raíz del proyecto (`./prompts/agents/...`).
2. **Carga en Sesión:** Antes de delegar una subtarea a un subagente, el orquestador principal debe leer o inyectar el prompt correspondiente de esta matriz para inicializar su personalidad y contexto técnico inmutable.
3. **Validación Cruzada:** Ningún cambio de código de un agente de desarrollo (`senior-developer-agent`) se fusionará sin la revisión de un agente de control de calidad (`code-reviewer`) o de seguridad (`shannon-secops-expert`).
