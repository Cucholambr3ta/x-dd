# X-DD — Guía Maestra: Workflows, Skills, Agentes y Estructura

**Versión:** 1.0 | **Fecha:** 2026-05-17 | **Gobernanza:** Constitución X-DD v1.4

---

## Índice

1. [Filosofía del Sistema](#1-filosofía-del-sistema)
2. [El Pipeline Elite SDD](#2-el-pipeline-elite-sdd)
3. [Equipo de Agentes](#3-equipo-de-agentes)
4. [Catálogo de Skills](#4-catálogo-de-skills)
5. [Catálogo de Workflows](#5-catálogo-de-workflows)
6. [Estructura de Carpetas](#6-estructura-de-carpetas)
7. [Ciclo Completo: Ejemplo Práctico](#7-ciclo-completo-ejemplo-práctico)
8. [Reglas Críticas de Gobernanza](#8-reglas-críticas-de-gobernanza)

---

## 1. Filosofía del Sistema

X-DD opera bajo el principio de **Spec-Driven Development (SDD)**: ninguna línea de código existe sin una especificación técnica aprobada que la respalde. Esto elimina el "code drift" y asegura que cada decisión técnica es trazable hasta un requisito de negocio.

El ecosistema se comporta como un **equipo de IA especializado** coordinado por un orquestador principal, asumiendo la máxima carga cognitiva para que el desarrollador humano opere como **decisor estratégico**, no como ejecutor.

### Principios Fundamentales

| Principio | Descripción |
|-----------|-------------|
| **Ambigüedad Cero** | Ningún flujo arranca si hay parámetros indefinidos (Art. 1) |
| **Gated Pipeline** | Cada fase requiere aprobación humana explícita: `"APROBADO"` (Art. 2) |
| **Flight Recorder** | Toda sesión se persiste en `memoria.md` y errores en `lecciones.md` (Art. 3) |
| **Spec First** | No existe `src/` sin un `SPEC.md` previo en `docs/specs/` (Art. 9) |
| **Learning Loop** | Cada cierre de fase alimenta el repositorio de sabiduría (Art. 9, Fase 6) |

---

## 2. El Pipeline Elite SDD

El flujo de trabajo central definido en el **Artículo 9 de la Constitución**. Consta de 6 fases secuenciales con checkpoints de aprobación humana.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE ELITE SDD (Art. 9)                      │
│                                                                     │
│  FASE 1       FASE 2       FASE 3       FASE 4    FASE 5   FASE 6  │
│  Briefing  ──► Spec     ──► Plan     ──► Build  ──► QA  ──► Retro  │
│                                                                     │
│             [APROBADO]  [APROBADO]  [APROBADO]                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Fase 1 — Briefing (Elicitación de Requisitos)

**Workflow:** `/fase-requisitos`  
**Agente líder:** Orchestrator + Architect  
**Duración estimada:** 20–40 min

**Objetivo:** Transformar la visión del usuario en un PRD sin ambigüedad. El cuestionario GSD itera hasta que el nivel de ambigüedad es < 5%.

**Entregables:**
- `idea/` — Notas iniciales y briefing crudo
- `Memoria/gsd/REQUIREMENTS.md` — PRD oficial con criterios Gherkin
- `docs/specs/SPEC.md` — Borrador inicial de especificación

**Directrices:**
- Preguntas obligatorias cubren: Frontend, Backend, Seguridad e Infraestructura
- Cada requisito funcional incluye escenarios `Given / When / Then`
- Auditoría de interoperabilidad: cada requisito se valida contra los workflows existentes

**Gate de salida:** PRD aprobado por el usuario antes de continuar.

---

### Fase 2 — Spec (Especificación Técnica DRIFT-ZERO)

**Workflow:** Delegado a `Architect`  
**Agente líder:** Architect  
**Skills activas:** `skill-backend-architect`, `skill-fractional-cto`

**Objetivo:** Convertir el PRD en contratos técnicos formales que gobiernan la implementación.

**Entregables:**
- `docs/specs/SPEC.md` — Especificación técnica completa
- `Arquitectura/SAD.md` — Software Architecture Document (C4)
- Esquemas de base de datos y contratos de API (OpenAPI si aplica)

**Directrices:**
- "Contract First": los contratos de interfaz se definen antes que la lógica
- El SAD debe incluir diagramas C4 (Contexto, Contenedor, Componente)
- Prohibido continuar si hay incertidumbre en la capa de seguridad

**Gate de salida:** `"APROBADO"` humano requerido. El `SPEC.md` se sella como referencia inmutable para las fases siguientes.

---

### Fase 3 — Plan (Descomposición Atómica)

**Workflow:** `/plan-fases`  
**Agente líder:** Orchestrator + Architect  
**Duración estimada:** 30–50 min

**Objetivo:** Transformar el SPEC en un grafo de tareas ejecutables (DAG) ordenadas por dependencias y optimizadas para paralelismo.

**Entregables:**
- `docs/plans/PLAN.md` — Plan de implementación con tareas atómicas y DoD
- `Memoria/gsd/ROADMAP.md` — Hitos, riesgos y dependencias
- `Memoria/gsd/STATE.md` — Estado inicial en tiempo real del proyecto

**Directrices:**
- Cada tarea tiene un "Definition of Done" (DoD) técnico y medible
- El DAG es validado contra ciclos antes de ser entregado
- Las tareas se etiquetan con el agente responsable

**Gate de salida:** `"APROBADO"` humano requerido. El `PLAN.md` se convierte en el contrato de ejecución.

---

### Fase 4 — Implementación (Build)

**Workflow:** `/xdd-build`  
**Agente líder:** Builder  
**Skills activas:** `skill-web-design-architect`, `skill-clean-code-architect`, `skill-design-system-atomic`, `skill-perf-auditor`

**Objetivo:** Transformar el `PLAN.md` en código de producción de alta fidelidad, bloque a bloque, sin desviarse del `SPEC.md`.

**Proceso interno:**
1. Verificar existencia de `SPEC.md` y `PLAN.md` — si faltan, el build se detiene
2. Scaffolding del proyecto si es nuevo: `/idea`, `/docs`, `/src`, `/tests`, `/interop`
3. Implementar el primer bloque de tareas del `PLAN.md`
4. Prueba de humo básica por cada componente construido
5. Verificar "Code Drift" vs Spec después de cada bloque
6. Actualizar `claude.md` del proyecto al completar un bloque

**Estándares de código obligatorios:**
- Estética Premium: paleta HSL/OKLCH, sistema 60-30-10
- Clean Code: SOLID, DRY, sin hacks de deuda técnica no planificada
- Logging proactivo en toda funcionalidad del ERP
- Módulos independientes y testeables

**Gate de salida:** Al terminar, Builder invoca automáticamente a `QA-Reviewer`.

---

### Fase 5 — Validación QA

**Workflow:** `/qa-review`  
**Agente líder:** QA-Reviewer (Swarm de 3 roles: Seguridad, Calidad, Documentación)  
**Skills activas:** `skill-code-reviewer`, `skill-perf-auditor`, `skill-shannon-secops`

**Objetivo:** Certificar que el código es correcto, rápido y seguro antes de sellar la fase.

**Sistema de validación por Tiers:**

| Tier | Tipo | Qué valida | Costo | Velocidad |
|------|------|-----------|-------|-----------|
| **Tier 1** | Estático | Linters, tipos, tests unitarios | Gratis | < 30s |
| **Tier 2** | Funcional | Tests E2E, integración, verificación visual | ~0 USD | 5–20 min |
| **Tier 3** | LLM-Judge | Calidad semántica, coherencia con SAD, docs | ~0.15–0.5 USD | 1–2 min |

Un hallazgo crítico en Tier 1 bloquea el PR inmediatamente.

**Artefactos generados:**
- `tests/results/qa_${runId}_latest.md` — Reporte QA consolidado
- `tests/results/qa_${runId}.ndjson` — Evidencia atómica
- `README.md` actualizado con estado del proyecto

**Gate de salida:** Score QA aprobatorio + `"APROBADO"` humano para merge.

---

### Fase 6 — Retrospectiva (Learning Loop)

**Workflow:** `/cierre-fase`  
**Agente líder:** Architect + QA-Reviewer

**Objetivo:** Sellar la fase, persistir el conocimiento y alimentar la inteligencia colectiva del ecosistema.

**Pasos:**
1. **Destilación de logros** — Verificar que todo el `PLAN.md` tiene `[x]`
2. **Post-mortem** — Identificar errores, bloqueos o "gotchas" técnicos
3. **Registro en `lecciones.md`** — Si el error es nuevo, se documenta con síntoma, causa y solución
4. **Actualización de manifiestos** — `memoria.md`, `CLAUDE.md` (estado + próximo hito)
5. **Certificación QA** — Reporte rápido: Drift / Tests / Estética
6. **Sello de cierre** — Timestamp + estatus final (`SELLADO`)

**Regla de oro:** Si la solución encontrada es reutilizable, se propone crear una nueva skill en `.agent/skills/`.

---

## 3. Equipo de Agentes

El ecosistema X-DD opera como un equipo de IA multi-agente. Cada agente tiene un rol, personalidad y conjunto de skills predefinidos.

### Jerarquía del Equipo

```
                    ┌─────────────────────┐
                    │   Orchestrator (PM)   │ ← Orquestador /xdd
                    │   00_Anmax_Core     │
                    │  skill-fractional-  │
                    │       cto           │
                    └──────────┬──────────┘
                               │ Delega
         ┌─────────────────────┼──────────────────────┐
         │                     │                      │
┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
│ Architect │   │  Builder  │   │   QA-Reviewer      │
│ backend-        │   │  web-design-    │   │  code-reviewer  │
│ architect       │   │  architect +    │   │  perf-auditor   │
│                 │   │  clean-code +   │   │                 │
│                 │   │  design-system  │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │
┌────────▼────────┐   ┌─────────────────┐   ┌─────────────────┐
│ SecOps    │   │ Maintainer│   │ Domain-Expert│
│ shannon-secops  │   │ librarian-      │   │ (Consultor de   │
│                 │   │ indexer         │   │  Dominio Telco) │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Ficha por Agente

#### Orchestrator — Project Manager & Fractional CTO
- **ID:** `00_Anmax_Core`
- **Skill principal:** `skill-fractional-cto`
- **Workflow:** `/xdd`
- **Misión:** Orquestar el equipo, evaluar viabilidad técnica, detectar riesgos y gestionar el Gated Pipeline
- **Activa cuando:** Inicio de sesión, definición de meta del día, delegación de tareas
- **Personalidad:** Estratégico, analítico, preventivo. Nunca escribe código directamente

#### Architect — Diseñador de Sistemas
- **ID:** `architect`
- **Skill principal:** `skill-backend-architect`
- **Workflows:** `/fase-requisitos`, `/plan-fases`
- **Misión:** Diseñar arquitecturas C4, contratos de API, modelos de datos y el SAD
- **Activa cuando:** Fase 2 (Spec) y Fase 3 (Plan)

#### Builder — UI/UX Architect & Feature Engineer
- **ID:** `builder-creative`
- **Skills:** `skill-web-design-architect`, `skill-design-system-atomic`, `skill-clean-code-architect`
- **Workflow:** `/xdd-build`
- **Misión:** Transformar specs en código de producción con estética premium y arquitectura SOLID
- **Activa cuando:** Fase 4 (Implementación)
- **Personalidad:** Creativo, constructivo, obsesionado con la perfección visual y el performance

#### QA-Reviewer — Auditor de Calidad y Performance
- **ID:** `qa-mentor`
- **Skills:** `skill-code-reviewer`, `skill-perf-auditor`
- **Workflow:** `/qa-review`
- **Misión:** Revisión estratificada Tier 1-3, auditoría de performance (Core Web Vitals), zero-defect policy
- **Activa cuando:** Fase 5 (Validación), invocado automáticamente por Builder

#### SecOps — Red Team (Shannon)
- **ID:** `shannon-secops`
- **Skill principal:** `skill-shannon-secops`
- **Workflow:** `/advanced-agentic-pentesting`, `/security-audit`
- **Misión:** Pentesting autónomo, análisis SAST/DAST, protección de infraestructura Telco
- **Arsenal:** Docker con Nmap, SQLMap, Nuclei, HexStrike AI (70+ herramientas), Telco payloads

#### Maintainer — Guardián de la Estabilidad
- **ID:** `maintainer-guardian`
- **Skill principal:** `skill-librarian-indexer`
- **Workflows:** `/dependency-update`, `/rollback`
- **Misión:** Gestión de deuda técnica, indexación semántica de código, actualizaciones de dependencias

#### Domain-Expert — Consultor de Dominio
- **ID:** `telco-consultant`
- **Misión:** Contexto profundo sobre protocolos Telco (TR-069, RADIUS, SIP), ISPcube, modelos de facturación y provisioning
- **Activa cuando:** Cualquier decisión técnica con impacto en el dominio Telco

#### Product-Manager — Estratega de Producto
- **ID:** `product-strategist`
- **Skill principal:** `skill-product-prioritizer`
- **Misión:** Priorización de features, análisis de valor de negocio, roadmap estratégico
- **Activa cuando:** Definición del backlog y priorización de sprints

---

## 4. Catálogo de Skills

Las skills son módulos de conocimiento y comportamiento inyectados en los agentes. Viven en `.agent/skills/<nombre>/SKILL.md`.

### Skills de Liderazgo y Estrategia

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-fractional-cto` | Orchestrator | Evaluación de viabilidad técnica, gestión de riesgos y deuda |
| `skill-product-prioritizer` | Product-Manager | Priorización RICE/MoSCoW, análisis de valor de negocio |
| `skill-xdd-pm` | Orchestrator | Gestión de proyecto, trazabilidad de fases |

### Skills de Arquitectura e Ingeniería

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-backend-architect` | Architect | Diseño de sistemas C4, contratos OpenAPI, modelos de datos |
| `skill-web-design-architect` | Builder | Arquitectura visual, sistemas de grids, jerarquía tipográfica |
| `skill-design-system-atomic` | Builder | Atomic Design (Átomos→Moléculas→Organismos→Templates→Páginas) |
| `skill-clean-code-architect` | Builder | SOLID, DRY, patrones de refactoring, deuda técnica zero |
| `skill-perf-auditor` | QA-Reviewer | Core Web Vitals, Lighthouse, optimización de bundle |
| `skill-code-reviewer` | QA-Reviewer | Revisión por pares, detección de anti-patrones, coherencia con SAD |

### Skills de Seguridad

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-shannon-secops` | SecOps | Pentesting autónomo, SAST/DAST, payloads Telco |

### Skills de Gestión del Conocimiento

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-librarian-indexer` | Maintainer | Indexación semántica de código, metadatos, búsqueda |
| `skill-mempalace-manager` | Orchestrator | Gestión de grafos semánticos locales con MemPalace |
| `skill-mempalace-loci` | Orchestrator | Formato de anotación espacial y notas semánticas Loci para RAG |
| `skill-gsd-sync` | Orchestrator | Sincronización del estado del proyecto con GSD |
| `skill-xdd-learning-loop` | Orchestrator | Automatización del registro en `lecciones.md` |
| `skill-markitdown` | Orchestrator | Ingesta de documentos Office/PDF a Markdown |

### Skills de Infraestructura y Operaciones

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-project-architect` | Architect | Estándares de estructura PROJ-*, scaffolding de proyectos |
| `skill-xdd-workflow-bridge` | Orchestrator | Ejecución de flujos `.md` desde Claude Code |

### Skills de UX y Frontend

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-color-theory` | Builder | HSL/OKLCH, escalas de color 9-pasos, WCAG AA, regla 60-30-10 |

### Skills de Utilidad General

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `ai-context-optimizer` | Orchestrator | Optimización de tokens y contexto por RBAC |
| `systematic-debugging` | Cualquiera | Protocolo estructurado de debugging (síntoma→causa→solución) |
| `smart-file-search` | Cualquiera | Búsqueda inteligente en el sistema de archivos |
| `skill-identity-context` | Orchestrator | Gestión de identidad, idioma y protocolos de comunicación |

---

## 5. Catálogo de Workflows

Los workflows viven en `.agent/workflows/<nombre>.md` y son invocados con `/nombre`.

### Workflows Core del Pipeline SDD

| Comando | ID | Fase SDD | Agentes | Propósito |
|---------|----|----------|---------|-----------|
| `/xdd` | FLUJO-X-DD | Pre-flight | Orchestrator | Orquestador principal. Lectura de memoria, meta del día, delegación |
| `/fase-requisitos` | FLUJO-003 | Fase 1 | Core + Architect | Elicitación PRD, cuestionario GSD, generación de REQUIREMENTS.md |
| `/plan-fases` | FLUJO-005 | Fase 3 | Core + Architect | Roadmapping GSD, DAG de tareas, ROADMAP.md + STATE.md |
| `/xdd-build` | FLUJO-BUILD | Fase 4 | Builder | Construcción atómica basada en PLAN.md |
| `/qa-review` | FLUJO-010 | Fase 5 | QA Swarm | Revisión Tier 1-3, reportes NDJSON |
| `/cierre-fase` | FLUJO-CIERRE | Fase 6 | Architect + QA | Post-mortem, lecciones, sello de cierre |

### Workflows de Seguridad

| Comando | Propósito |
|---------|-----------|
| `/advanced-agentic-pentesting` | Pentesting autónomo con Shannon (Nmap, SQLMap, Nuclei, HexStrike) |
| `/security-audit` | Auditoría de seguridad estática y dinámica del código |
| `/secure-isolation-ops` | Operaciones en entornos de aislamiento seguro |

### Workflows de Mantenimiento e Infraestructura

| Comando | Propósito |
|---------|-----------|
| `/dependency-update` | Actualización controlada de dependencias con auditoría |
| `/rollback` | Procedimiento de reversión segura de cambios |
| `/ci-cd-setup` | Configuración de pipelines de CI/CD |
| `/deploy-prod` | Despliegue a producción con checklist de seguridad |
| `/refactor-area` | Refactoring estructural de una zona del código |

### Workflows de Diagnóstico y Análisis

| Comando | Propósito |
|---------|-----------|
| `/analisis-impacto` | Análisis del blast radius de un cambio propuesto |
| `/xdd-trace` | Trazabilidad de decisiones técnicas en el ecosistema |
| `/incidente-ID` | Protocolo de gestión de incidentes de producción |
| `/generate-unit-tests` | Generación automatizada de tests unitarios |
| `/stress-test` | Pruebas de estrés e inyección de carga |
| `/pruebas-humo` | Smoke tests rápidos post-deploy |
| `/pruebas-fuzz` | Fuzzing de inputs y APIs |

### Workflows de Documentación y Conocimiento

| Comando | Propósito |
|---------|-----------|
| `/technical-documentation` | Generación de documentación técnica estandarizada |
| `/generar-flujo` | Creación de nuevos workflows desde plantilla |
| `/design-system-builder` | Construcción de sistema de diseño desde cero |
| `/mempalace-sync` | Sincronización del Palacio de la Memoria (MemPalace) |
| `/xdd-ingest` | Ingesta masiva de documentos (Office, PDF) vía MarkItDown |
| `/mejorar-prompt` | Optimización de prompts de agentes |
| `/project-architecture-gsd` | Generación de arquitectura de proyecto bajo estándar GSD |

---

## 6. Estructura de Carpetas

### Workspace Raíz: `./`

```
Desarrollos/
├── CLAUDE.md                    ← Gobernanza para Claude Code (lectura obligatoria)
├── constitucion.md        ← Ley suprema del ecosistema
├── memoria.md                   ← Memoria operativa (sesiones y hitos)
├── lecciones.md                 ← Repositorio de sabiduría técnica
├── equipo.md              ← Directorio de agentes y roles
│
├── .agent/                      ← Núcleo del ecosistema de agentes
│   ├── skills/                  ← Skills (módulos de conocimiento)
│   │   └── <nombre-skill>/
│   │       └── SKILL.md
│   ├── workflows/               ← Workflows (flujos de trabajo invocables)
│   │   └── <nombre>.md
│   └── scripts/
│       ├── audit_context.ps1    ← Auditoría de salud del ecosistema
│       └── silent_launcher.vbs ← Launcher silencioso de startup
│
├── Arquitectura/
│   ├── SAD.md                   ← Software Architecture Document (workspace)
│   └── SAD_ZeroAura.md          ← SAD específico de PROJ-ZeroAura
│
├── Memoria/
│   └── gsd/
│       ├── PROJECT.md           ← Meta-proyecto GSD
│       ├── REQUIREMENTS.md      ← PRD activo
│       ├── ROADMAP.md           ← Hitos y milestones
│       └── STATE.md             ← Estado en tiempo real
│
├── docs/
│   ├── specs/                   ← SPEC.md de cada feature (DRIFT-ZERO)
│   └── plans/
│       ├── PLAN.md              ← Plan de implementación activo
│       └── archive/             ← Planes sellados
│
├── wiki/
│   └── procesos/
│       └── ventas/              ← Procedimientos granulares click-por-click
│
├── documents/
│   └── markdown/                ← Documentos ingeridos vía MarkItDown
│
├── Decision_Records/            ← ADRs (Architecture Decision Records)
├── Evidencias/                  ← Capturas y artefactos de auditorías
│
└── Proyectos/                   ← Proyectos PROJ-* individuales
    └── PROJ-<Nombre>/           ← Ver estructura interna abajo
```

### Estructura Interna de un Proyecto `PROJ-*`

Cada proyecto sigue el estándar definido en `skill-project-architect` y el Art. 5 de la Constitución:

```
PROJ-NombreProyecto/
├── CLAUDE.md                    ← Contexto específico del proyecto para Claude Code
├── README.md                    ← Estado actual y descripción del proyecto
├── memoria.md                   ← Memoria operativa del proyecto
│
├── idea/                        ← Fase 1: Briefing y notas crudas
│   └── briefing.md
│
├── docs/
│   ├── specs/
│   │   └── SPEC.md              ← Especificación técnica DRIFT-ZERO (Fase 2)
│   ├── plans/
│   │   ├── PLAN.md              ← Plan de implementación atómica (Fase 3)
│   │   └── archive/
│   ├── analisis/                ← Análisis técnico del sistema
│   └── auditorias/              ← Reportes de auditoría y deuda técnica
│
├── src/                         ← Código fuente (solo existe si hay SPEC.md)
├── api/                         ← Endpoints y contratos de backend
├── tests/
│   └── results/                 ← Reportes QA NDJSON y Markdown
├── interop/                     ← Contratos de interoperabilidad con otros PROJ-*
└── design/                      ← Assets de diseño y sistema de componentes
```

### Proyectos Activos en el Ecosistema

| Proyecto | Descripción | Estado |
|----------|-------------|--------|
| `xdd-erp` | ERP multi-módulo (GitHub: xdd-dev/xdd-erp) | En desarrollo |
| `PROJ-ZeroAura` | Asistente androide personal (Tauri 2.0 + Rust + React) | FASE 2 completada |
| `PROJ-Ominicontacto` | Integración con plataforma de contact center | Auditado |
| `xdd-crm | CRM activo | Producción + Mantenimiento |
| `otro-proyecto.ejemplo.com` | Sistema GIS/FTTH logístico (Vanilla PHP) | Legacy documentado |

---

## 7. Ciclo Completo: Ejemplo Práctico

**Escenario:** Implementar el módulo de Facturación del ERP

### Paso 1 — Arranque de Sesión
```
Usuario: /xdd
```
Orchestrator lee `memoria.md`, `lecciones.md`, `CLAUDE.md`. Resume el estado anterior y pregunta la meta del día.

### Paso 2 — Briefing
```
Usuario: /fase-requisitos
Meta: Módulo de Facturación para el ERP X-DD
```
Orchestrator + Domain-Expert lanzan el cuestionario GSD. Preguntas sobre ciclos de facturación, integración con ISPcube, tipos de pago Telco, etc. El resultado es `Memoria/gsd/REQUIREMENTS.md`.

### Paso 3 — Spec
Architect genera `docs/specs/SPEC.md` con:
- Diagrama C4 del módulo de Facturación
- Esquema de base de datos (Drizzle/Postgres)
- Contrato de API (OpenAPI)

```
Usuario: APROBADO
```

### Paso 4 — Plan
```
Usuario: /plan-fases
```
Architect descompone en tareas atómicas: Modelo de datos → CRUD API → Integración ISPcube → UI Dashboard → Tests. Se genera `docs/plans/PLAN.md` y `Memoria/gsd/ROADMAP.md`.

```
Usuario: APROBADO
```

### Paso 5 — Build
```
Usuario: /xdd-build
```
Builder ejecuta tarea por tarea del PLAN.md. Verifica Code Drift después de cada bloque. Genera el código en `src/` y `api/`.

### Paso 6 — QA
Invocado automáticamente por Builder. QA-Reviewer ejecuta Tier 1 (linters), Tier 2 (tests E2E en Docker), Tier 3 (LLM review). Genera `tests/results/qa_billing_001.md`.

```
Usuario: APROBADO
```

### Paso 7 — Cierre
```
Usuario: /cierre-fase
```
Orchestrator registra los hitos en `memoria.md`. Si se encontró algún "gotcha" técnico (ej: problema con timezone en cálculo de ciclos de billing), se registra en `lecciones.md`. El plan se archiva en `docs/plans/archive/`. La fase queda `SELLADA`.

---

## 8. Reglas Críticas de Gobernanza

### Reglas Absolutas (nunca se rompen)

1. **No existe `src/` sin `SPEC.md`** — Si no hay especificación técnica aprobada, el build no arranca.
2. **Palabra clave `"APROBADO"`** — Requerida antes de cualquier cambio estructural. Sin ella, el agente espera.
3. **Lectura de memoria obligatoria** — Cada sesión arranca leyendo `memoria.md` y `lecciones.md`.
4. **Registro de cierre obligatorio** — Ninguna sesión termina sin actualizar `memoria.md` vía `/cierre-fase`.
5. **Errores nuevos van a `lecciones.md`** — Siempre, sin excepción.

### Umbrales de Complejidad (Art. 8)

| Tipo de cambio | Líneas afectadas | Protocolo requerido |
|----------------|-----------------|---------------------|
| Mantenimiento simple (typos, UI menor) | < 10 | Directo (Art. 2 bypassed) |
| Feature o refactoring significativo | > 20 | Pipeline SDD completo obligatorio |
| Cualquier cambio en producción | Cualquiera | `"APROBADO"` + PR desde `feature/*` |

### Nomenclatura Estándar

```
Proyectos:   PROJ-PascalCase
Ramas git:   feature/[id]-descripcion
             bugfix/[id]-descripcion
             hotfix/[id]-descripcion
             release/v[version]
Skills:      skill-kebab-case
Workflows:   kebab-case
IDs sesión:  FASE-NOMBRE-VERSION
```

### Stack Tecnológico por Defecto

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML/JS/CSS Vanilla (por defecto), React/TypeScript para proyectos complejos |
| Backend | PHP (legacy), Python FastAPI (nuevo ERP), Rust (PROJ-ZeroAura) |
| Base de datos | PostgreSQL + pgvector, Drizzle ORM |
| Grafo de conocimiento | Neo4j |
| Infraestructura | Docker Compose, GitHub Actions |
| Estilos de color | HSL/OKLCH (nunca HEX plano) |
| Documentación | MemPalace Loci + Markdown |

---

> **Última actualización:** 2026-05-17
> **Mantenido por:** Orchestrator (00_Anmax_Core)
> **Ley suprema:** [constitucion.md](../constitucion.md)
