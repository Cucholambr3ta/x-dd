# X-DD — Guía de Integración X-DD
**Versión:** 2.0 | **Fecha:** 2026-05-17 | **Complementa:** SDD_GUIDE.md

---

## Índice

1. [Diagnóstico: qué ya tienes y qué falta](#1-diagnóstico)
2. [Filosofía de integración](#2-filosofía-de-integración)
3. [El pipeline X-DD ampliado](#3-el-pipeline-x-dd-ampliado)
4. [Integración fase a fase](#4-integración-fase-a-fase)
5. [Capa de seguridad: SecDD, STDD y Threat-Driven Development](#5-capa-de-seguridad)
6. [Árbol de decisión: ¿qué camino tomar?](#6-árbol-de-decisión)
7. [Cambios en la estructura de carpetas](#7-cambios-en-la-estructura-de-carpetas)
8. [Nuevas skills y workflows propuestos](#8-nuevas-skills-y-workflows)
9. [Guía de transición](#9-guía-de-transición)
10. [Agente Residente Local — NousResearch Hermes + MemPalace](#10-agente-residente-local--nousresearch-hermes--mempalace)
11. [La Agencia Externa de Subagentes Especializados (agency-agents)](#11-la-agencia-externa-de-subagentes-especializados-agency-agents)

---

## 1. Diagnóstico de Madurez y Capacidades (Ecosistema Elite v2.0)

Tras la exitosa integración masiva de **77 subagentes especializados** (procedentes de `agency-agents`) y el acoplamiento del **Agente Residente Local** (Hermes + MemPalace), la matriz de capacidades de la suite X-DD ha completado su transición de infraestructura. Los "gaps de capacidades" anteriores han sido plenamente mitigados a nivel del ecosistema, pasando a un estado de **Listo para Activación en Producción** por cada proyecto.

### Matriz de Estado de Metodologías X-DD

| Metodología | ¿Dónde vive en el Pipeline? | Estado de Infraestructura | Soporte Agéntico Dedicado |
|-------------|----------------------------|---------------------------|---------------------------|
| **SDD** | Fases 1–6 (Pipeline completo) | ✅ Completo | `Orchestrator` + `Product-Manager` |
| **BDD** | Fase 1 (Requisitos) + Fase 5 (QA) | 🔄 Listo para Activación | `agency-rapid-prototyper` + `Anmax-Automation` |
| **ATDD** | Fase 1 (Requisitos) + Fase 5 (QA) | 🔄 Listo para Activación | `agency-qa-review` + `agency-acceptance-orchestrator` |
| **FDD** | Fase 1 (Briefing) + Fase 3 (Plan) | 🔄 Listo para Activación | `agency-product-manager` + `agency-project-manager` |
| **TDD** | Fase 4 (Build - Test First) | 🔄 Listo para Activación | `agency-agency-senior-developer` + `agency-code-reviewer` |
| **DDD** | Fase 2 (Spec - Modelo de Dominio) | 🔄 Listo para Activación | `agency-senior-architect` + `agency-backend-architect` |
| **SecDD/STDD** | Fase 4 (Build - Pruebas Preventivas) | 🔄 Listo para Activación | `agency-security-engineer` + `skill-shannon-secops` |
| **Threat-Driven Dev.** | Fase 2 (Spec - Modelado Preventivo) | 🔄 Listo para Activación | `agency-threat-detection-engineer` + `SecOps` |

### Mitigación de Gaps de Infraestructura

* **Gap 1 (TDD) — Mitigado:** La Fase 4 (Build) ahora cuenta con la infraestructura para escribir stubs de pruebas unitarias (`tests/unit/**/*.test.ts`) *antes* del código de producción mediante `agency-agency-senior-developer`, rompiendo el hábito heredado de escribir pruebas de forma puramente reactiva en la Fase 5.
* **Gap 2 (DDD) — Mitigado:** Contamos con plantillas y directrices en `prompts/phases/03_spec_ddd.md` para que el arquitecto (`agency-senior-architect`) diseñe un modelo de dominio explícito (`DOMAIN.md`) en la Fase 2, definiendo bounded contexts, aggregates y domain events para controlar la complejidad en el ERP/CRM/WMS.
* **Gap 3 (BDD) — Mitigado:** Los escenarios Gherkin ya no son texto libre. La infraestructura soporta la generación de archivos ejecutables `.feature` (`tests/features/`) y stubs correspondientes en la Fase 1, procesados por `agency-rapid-prototyper` y listos para su automatización en Playwright.
* **Gap 4 (ATDD) — Mitigado:** Introducido el flujo para definir criterios de aceptación automatizados que bloquean el pipeline de CI/CD, garantizando que `agency-qa-review` valide la completitud funcional en la Fase 5.
* **Gap 5 (FDD) — Mitigado:** Establecida la creación de un catálogo formal de características (`docs/features/FEATURES.md`) en la Fase 1 estructurado por valor de negocio y priorizado dinámicamente usando RICE/MoSCoW por `agency-product-manager`.
* **Gap 6 (Threat Modeling) — Mitigado:** Creado el framework de modelado preventivo de amenazas (`docs/specs/THREATS.md`) en la Fase 2 para que `agency-threat-detection-engineer` y `SecOps` analicen brechas y riesgos antes del desarrollo físico de las features.
* **Gap 7 (STDD) — Mitigado:** Las pruebas de seguridad ya no son reactivas. La Fase 4 integra el ciclo de Security TDD (STDD), donde `agency-security-engineer` genera casos de prueba de inyección y fallos de RBAC que deben fallar de inicio y ser mitigados por diseño.

---

## 2. Filosofía de integración

> **Principio maestro: las nuevas metodologías son capas, no fases nuevas.**

El pipeline de 6 fases NO cambia. No se agrega una "Fase 7 — DDD" ni se rompe el Gated Pipeline. En su lugar, cada metodología se embebe en la fase donde más aporta:

```
FASE 1 (Briefing)   ──► + BDD formalizado + ATDD + FDD catálogo
FASE 2 (Spec)       ──► + DDD modelo de dominio + Threat Modeling (THREATS.md)
FASE 3 (Plan)       ──► + FDD reorganización por valor
FASE 4 (Build)      ──► + TDD ciclo Rojo-Verde-Refactor + STDD security tests
FASE 5 (QA)         ──► + BDD ejecutable + ATDD + SAST + DAST + Secrets scanning
FASE 6 (Retro)      ──► Sin cambios (ya es excelente)
```

**Regla de composición:** Cada proyecto define su "nivel X-DD" según la complejidad. No todos los proyectos necesitan las 6 metodologías. El árbol de decisión (Sección 5) determina qué camino tomar.

---

## 3. El pipeline X-DD ampliado

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE X-DD X-DD (v2.0)                               │
│                                                                                  │
│  FASE 1          FASE 2             FASE 3       FASE 4      FASE 5    FASE 6   │
│  Briefing    ──► Spec           ──► Plan     ──► Build   ──► QA    ──► Retro   │
│                                                                                  │
│  + FDD           + DDD              + FDD        + TDD       + BDD              │
│  (catálogo)      (dominio)          (por valor)  (first)     (exec)             │
│  + BDD           + Threat Model     │            + STDD 🛡️   + ATDD             │
│  (features)      (THREATS.md) 🛡️   │            (sec tests) + SAST 🛡️          │
│  + ATDD          │                  │            │           + DAST 🛡️          │
│  (criterios)     │                  │            │           + Secrets 🛡️       │
│                                                                                  │
│              [APROBADO]         [APROBADO]   [APROBADO]                         │
│         (SPEC+DOMAIN+THREATS)                                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Mapa completo: metodología → agente → artefacto

| Metodología | Fase X-DD | Agente líder | Nuevo artefacto |
|------------|------------|--------------|-----------------|
| **FDD** | Fase 1 + 3 | `project-manager-senior` | `docs/features/FEATURES.md` |
| **BDD** | Fase 1 + 5 | `project-manager-senior` + `code-reviewer` | `tests/features/*.feature` |
| **ATDD** | Fase 1 + 5 | `architect-review` + `code-reviewer` | `tests/acceptance/*.test.ts` |
| **DDD** | Fase 2 | `architect-review` | `docs/specs/DOMAIN.md` |
| **Threat-Driven** 🛡️ | Fase 2 | `shannon-secops-expert` + `architect-review` | `docs/specs/THREATS.md` |
| **TDD** | Fase 4 | `senior-developer-agent` | `tests/unit/*.test.ts` (antes de `src/`) |
| **STDD** 🛡️ | Fase 4 | `senior-developer-agent` + `shannon-secops-expert` | `tests/security/**/*.security.test.ts` |
| **SecDD** 🛡️ | Fase 5 | `code-reviewer` + `shannon-secops-expert` | SAST + DAST + Secrets reports |
| **SDD** | Todas | `specialized-chief-of-staff` | `SPEC.md` (sin cambios) |

---

## 4. Integración fase a fase

### FASE 1 — Briefing: agregar FDD, BDD y ATDD

**Qué cambia:** El cuestionario GSD ahora produce tres artefactos adicionales además del REQUIREMENTS.md.

**Nuevo artefacto 1 — Catálogo de Features (FDD):**
Antes de escribir requisitos técnicos, listar los features en formato FDD:

```
[acción] [resultado] [objeto]
```

Ejemplo: *"Generar factura PDF de un ciclo de billing para un cliente Telco"*

Cada feature tiene: nombre, beneficio al usuario, prioridad (MoSCoW/RICE), estimación, criterios de aceptación de alto nivel.

Archivo: `docs/features/FEATURES.md` (ver plantilla `templates/00_fdd_feature_catalog.md`)

**Nuevo artefacto 2 — Archivos .feature (BDD):**
Formalizar los escenarios Gherkin que hoy viven como texto libre en REQUIREMENTS.md y convertirlos en archivos `.feature` ejecutables por Cucumber/Playwright-BDD.

Directorio: `tests/features/<nombre-feature>.feature`

Convención de nombres: `feature-[id]-[nombre-kebab].feature`

**Nuevo artefacto 3 — Tests de aceptación stub (ATDD):**
Por cada criterio de aceptación del REQUIREMENTS.md, crear el stub del test de aceptación (archivo vacío con el `describe` y el `it` definidos). El test falla por diseño hasta que la implementación lo satisfaga.

Directorio: `tests/acceptance/<nombre-feature>.acceptance.test.ts`

**Agentes involucrados:**
- `Orchestrator` — Facilita el cuestionario y extrae los features
- `Domain-Expert` — Valida criterios de dominio (ciclos de billing, protocolos, etc.)
- `Product-Manager` — Prioriza el catálogo con RICE/MoSCoW

**Gate de salida ampliado:** Además del REQUIREMENTS.md, el `FEATURES.md` y al menos un `.feature` por épica deben existir antes de avanzar.

---

### FASE 2 — Spec: agregar DDD

**Qué cambia:** El SPEC.md ahora tiene una sección obligatoria de **Modelo de Dominio** que precede a los diagramas C4.

**Por qué DDD aquí:** El modelo de dominio es el contrato conceptual que hace que los diagramas C4 sean coherentes. Sin un vocabulario compartido (ubiquitous language), los componentes del C4 reflejan intuiciones del desarrollador, no la realidad del negocio.

**Nuevo sub-artefacto: `docs/specs/DOMAIN.md`** (ver plantilla `templates/01_ddd_domain_model.md`)

Estructura obligatoria:

```markdown
## Ubiquitous Language
Glosario de términos del dominio con definiciones precisas.
(Ejemplo: "Ciclo de Billing" ≠ "Período de Factura" — definir la diferencia)

## Bounded Contexts
Mapa de los subdominios y sus fronteras. Cada contexto tiene su propio modelo.

## Context Map
Cómo se relacionan los bounded contexts (Upstream/Downstream, ACL, Shared Kernel).

## Core Aggregates
Por cada bounded context: aggregates, entities, value objects, domain events.

## Domain Events
Eventos que cruzan bounded contexts y disparan flujos de trabajo.
```

**Regla crítica:** El ubiquitous language del DOMAIN.md se convierte en **vocabulario obligatorio** para nombrar variables, funciones, clases y endpoints. Code drift semántico es también Code Drift.

**Agentes involucrados:**
- `Architect` — Lidera el modelado C4 y la arquitectura
- `Domain-Expert` — Aporta el vocabulario preciso del dominio Telco
- `Orchestrator` — Verifica coherencia con otros bounded contexts en el ecosistema

**Gate de salida ampliado:** El `DOMAIN.md` debe estar aprobado junto con el SPEC.md. Los nombres en el DOMAIN.md son inmutables para las fases siguientes.

---

### FASE 3 — Plan: reforzar FDD

**Qué cambia:** El PLAN.md se reorganiza para priorizar **features completos y verticales** (FDD) en lugar de capas técnicas horizontales.

**Antes (orientado a capas):**
```
Tarea 1: Modelo de datos (todas las tablas del módulo)
Tarea 2: CRUD API (todos los endpoints)
Tarea 3: UI (todas las pantallas)
Tarea 4: Tests
```

**Después (orientado a features — FDD):**
```
Feature 1: Generar factura PDF [alta prioridad, 1 día]
  - Subtarea 1.1: Tabla `invoices` + modelo Drizzle
  - Subtarea 1.2: Endpoint POST /invoices
  - Subtarea 1.3: Componente <InvoiceGenerator />
  - Subtarea 1.4: Test unitario del cálculo de totales (TDD)
  - Subtarea 1.5: Test de aceptación E2E
  DoD: El archivo .feature del feature pasa al 100%

Feature 2: Enviar factura por email [prioridad media, 0.5 días]
  ...
```

**Por qué importa para el solo dev:** Entrega valor usable antes. Si el tiempo se acorta, cancelas features de baja prioridad, no dejás módulos a medio terminar.

**Gate de salida ampliado:** El `PLAN.md` debe listar los features en orden de prioridad RICE. Cada feature tiene su DoD atado al archivo `.feature` correspondiente.

---

### FASE 4 — Build: integrar TDD (el cambio más importante)

**Qué cambia:** El ciclo de construcción de Builder se invierte. Antes de escribir cualquier función de lógica de negocio, se escribe el test que la valida.

**El ciclo TDD dentro de `/xdd-build`** (ver plantilla `templates/04_tdd_cycle.md`)**:**

```
Por cada subtarea de tipo "lógica de negocio":

  1. 🔴 ROJO    — Escribir el test (describe lo que la función DEBE hacer)
                  El test falla porque la función no existe
                  Archivo: tests/unit/<nombre>.test.ts

  2. 🟢 VERDE   — Escribir el mínimo código para que el test pase
                  Sin sobre-ingeniería. Solo lo necesario.
                  Archivo: src/<nombre>.ts

  3. 🔵 REFACTOR — Mejorar el código sin romper el test
                  Aplicar SOLID, DRY, Clean Code
                  El test debe seguir en verde
```

**¿Qué va a TDD y qué no?**

| Aplica TDD | No aplica TDD |
|------------|---------------|
| Lógica de negocio (cálculos, reglas) | Scaffolding (rutas básicas, modelos Drizzle) |
| Transformaciones de datos | Configuración (env, docker-compose) |
| Algoritmos (billing, provisioning) | UI puramente visual (sin lógica) |
| Validaciones de dominio | Integraciones externas (mockear, no TDD) |
| Reglas de seguridad | |

**Nuevo estándar de código en Builder:**
- Ninguna función de lógica de negocio existe sin su test correspondiente en `tests/unit/`
- El test se crea ANTES del archivo `.ts`. Si no existe el test, no existe la función.
- Builder debe reportar el status TDD por subtarea: `🔴→🟢→🔵`

**Gate de salida ampliado:** El build de un feature solo está completo cuando:
1. Los tests unitarios TDD están en verde
2. El archivo `.feature` BDD asociado pasa al 100%
3. El test de aceptación ATDD está en verde

---

### FASE 5 — QA: conectar BDD y ATDD a los Tiers

**Qué cambia:** El Tier 2 ahora ejecuta los archivos `.feature` y los tests de aceptación como parte del pipeline automático.

**Tier actualizado:**

| Tier | Tipo | Qué valida | Nueva adición |
|------|------|-----------|---------------|
| **Tier 1** | Estático | Linters, tipos, tests unitarios TDD | Sin cambios |
| **Tier 2** | Funcional | Tests E2E + **archivos .feature (BDD)** + **tests de aceptación (ATDD)** | ✅ Nuevo |
| **Tier 3** | LLM-Judge | Calidad semántica, coherencia con SAD y **coherencia con DOMAIN.md** | ✅ Ampliado |

**En Tier 3:** El LLM-Judge ahora también verifica que el código usa el vocabulario del DOMAIN.md (ubiquitous language). Un método llamado `calculateBillingPeriod` cuando el dominio define `computeCycleTotals` es un drift semántico reportable.

**Artefactos QA actualizados:**
- `tests/results/qa_${runId}_latest.md` — Agrega sección de cobertura BDD (% de scenarios pasados)
- `tests/results/qa_${runId}_bdd.html` — Reporte visual de Cucumber (opcional)

---

## 5. Capa de seguridad: SecDD, STDD y Threat-Driven Development

> La seguridad no es una fase nueva en el pipeline — es una **capa transversal** que se añade a las fases existentes sin modificar la estructura del Gated Pipeline.

### Las tres metodologías de seguridad

**Threat-Driven Development** opera en Fase 2 (Spec). Toma el `DOMAIN.md` recién creado y aplica el framework STRIDE sobre cada aggregate, endpoint y domain event para identificar amenazas antes de codificar. El resultado es el `THREATS.md` — un contrato de seguridad que lista amenazas, su riesgo y los controles obligatorios que deben implementarse. Las amenazas CRÍTICAS bloquean el avance de Fase 4 si no tienen control documentado.

**STDD (Security Test-Driven Development)** opera en Fase 4 (Build). Extiende el ciclo TDD con una capa de security tests que se escriben *antes* del código, igual que los tests funcionales. Un security test valida que la función rechaza inputs adversariales, hace cumplir permisos y no filtra información. El ciclo queda: 🔴 test funcional falla → 🔴🛡️ security test falla → 🟢 implementación con controles → 🔵 refactor + hardening. Los controles de seguridad nacen integrados en el diseño, no como parche posterior.

**SecDD (Security-Driven Development)** opera en Fase 5 (QA). Es la capa de herramientas automatizadas que escanea el código y la aplicación en ejecución. Amplía el Tier 1 con SAST (Semgrep) y detección de secretos (Gitleaks), y el Tier 2 con DAST (OWASP ZAP / Nuclei) y análisis de dependencias (Trivy). Shannon SecOps mantiene su rol de Red Team ofensivo bajo demanda con `/advanced-agentic-pentesting`.

### La relación entre las tres capas

```
Threat-Driven (Fase 2)    →  Define QUÉ amenazas existen y qué controles son obligatorios
       ↓
STDD (Fase 4)             →  Implementa los controles como código + los valida con tests
       ↓
SecDD / QA (Fase 5)       →  Verifica automáticamente que los controles funcionan en runtime
       ↓
Shannon SecOps (demanda)  →  Ataca el sistema como un adversario real — Red Team ofensivo
```

### FASE 2 (Spec) — Threat Modeling

**Nuevo artefacto: `docs/specs/THREATS.md`** (ver plantilla `templates/05_secdd_threat_model.md`)

**Proceso:**
1. Architect entrega el `DOMAIN.md` aprobado
2. Shannon SecOps (SecOps) lidera el threat modeling con `/threat-model`
3. Por cada aggregate, endpoint y domain event del `DOMAIN.md`, se aplica STRIDE
4. Se identifican activos, actores adversariales y superficies de ataque
5. Para cada amenaza: probabilidad, impacto, riesgo y control propuesto
6. Las amenazas CRÍTICAS generan `SEC-REQ-*` que se copian obligatoriamente al `SPEC.md`
7. Cada amenaza genera un stub de security test en `tests/security/`

**Gate de Fase 2 ampliado:** `THREATS.md` + `DOMAIN.md` + `SPEC.md` — los tres deben aprobarse juntos. Ninguna amenaza CRÍTICA sin control documentado.

**Específico para X-DD (Telco):** El threat model cubre amenazas de protocolos Telco: TR-069 hijacking, RADIUS dictionary attacks, SIP toll fraud, ISPcube API key compromise. Domain-Expert participa como asesor de dominio.

---

### FASE 4 (Build) — Ciclo STDD

**Nuevo directorio:** `tests/security/` con subdirectorios por categoría (ver plantilla `templates/06_stdd_security_cycle.md`)

**El ciclo STDD por función crítica:**

```
Para cada función listada en el THREATS.md como "security test requerido":

  1. 🔴        TDD test funcional          → falla (función no existe)
  2. 🔴🛡️      STDD security test          → falla (función no existe)
  3. 🟢        Implementación mínima        → ambos tests pasan
  4. 🔵        Refactor + hardening         → ambos tests siguen en verde
```

**¿Qué funciones/endpoints requieren STDD?**

| Requiere STDD | No requiere STDD |
|--------------|-----------------|
| Autenticación y manejo de tokens | Scaffolding y CRUD básico sin lógica |
| Endpoints que reciben input del exterior | Configuración y scripts de migración |
| Lógica de autorización (RBAC, IDOR) | UI puramente visual sin lógica de negocio |
| Funciones que acceden a datos PII | Utilidades internas sin superficie de ataque |
| Cálculos financieros (billing, pagos) | Tests de otros tests |
| Integraciones con sistemas externos | |

**Categorías de security tests:**

```
tests/security/
├── injection/       ← SQL, XSS, path traversal, command injection
├── auth/            ← JWT spoofing, brute force, token expiry, session fixation
├── authz/           ← RBAC, IDOR, privilege escalation, resource ownership
├── disclosure/      ← Error handling, PII exposure, data dumps sin paginación
├── availability/    ← Rate limiting, payload size, query timeouts
├── audit/           ← Audit log integridad, tamper detection
└── transport/       ← TLS enforcement, security headers, CORS
```

---

### FASE 5 (QA) — Tier de seguridad ampliado

| Tier | Tipo | Herramienta | Qué detecta | Bloquea merge si falla |
|------|------|-------------|------------|----------------------|
| **Tier 1** | SAST | **Semgrep** | SQLi, XSS, hardcoded secrets, patrones inseguros en TS/Python/PHP/Rust | ✅ Sí |
| **Tier 1** | Secrets | **Gitleaks** | API keys, tokens, contraseñas en código o historial git | ✅ Sí |
| **Tier 1** | SCA | **`npm audit` / Trivy** | Dependencias con CVEs conocidos (crítico o alto) | ✅ Sí |
| **Tier 2** | DAST | **OWASP ZAP** | OWASP Top 10 en la aplicación en ejecución | ✅ Para producción |
| **Tier 2** | DAST | **Nuclei** | Vulnerabilidades conocidas con templates actualizados | ✅ Para producción |
| **Tier 2** | Security tests | **Vitest** (STDD) | Controles a nivel de código (injection, authz, rate limiting) | ✅ Sí |
| **Tier 3** | Red Team | **Shannon SecOps** | Pentesting ofensivo completo bajo demanda | Manual |

**Comando unificado de seguridad para `/qa-review`:**
```bash
# Tier 1 — Estático
npx semgrep --config=auto src/
gitleaks detect --source=. --verbose
npm audit --audit-level=high

# Tier 2 — Security tests STDD
npx vitest run tests/security/

# Tier 2 — DAST (en entorno de staging)
docker run -t owasp/zap2docker-stable zap-baseline.py -t $STAGING_URL
nuclei -u $STAGING_URL -t cves/ -t vulnerabilities/
```

---

### Árbol de decisión de seguridad

```
¿El proyecto maneja datos de clientes, pagos o infraestructura Telco?
│
├─► SÍ (ERP, WekiCRM, provisioning, billing)
│       ↓
│   Camino COMPLETO: Threat Model + STDD + SecDD (SAST+DAST+Secrets)
│   + Shannon Red Team antes de cada release a producción
│
└─► NO (herramienta interna, script, utilidad sin datos sensibles)
        ↓
    Camino MÍNIMO: SAST (Semgrep) + Secrets (Gitleaks)
    Sin STDD ni DAST requeridos
```

**Skills de seguridad disponibles (AgentSecOps/SecOpsAgentKit):**
Copiar directamente a `.agent/skills/` para ampliar las capacidades de Shannon SecOps:

| Skill kit | Herramienta | Propósito |
|-----------|------------|-----------|
| `appsec/semgrep` | Semgrep | SAST multilenguaje |
| `devsecops/gitleaks` | Gitleaks | Detección de secretos |
| `devsecops/container-grype` | Trivy/Grype | Vulnerabilidades en imágenes Docker |
| `devsecops/checkov` | Checkov | Seguridad en IaC (docker-compose, GitHub Actions) |
| `secsdlc/reviewdog` | Reviewdog | Code review de seguridad en PRs |
| `incident-response/ir-velociraptor` | Velociraptor | Forensics e incident response |

---

## 6. Árbol de decisión

Usa este árbol al iniciar cada proyecto o feature para decidir qué combinación de metodologías aplicar:

```
¿Es un proyecto greenfield o feature nueva?
│
├─► SÍ ─► ¿La lógica de negocio es compleja?
│              (reglas de billing, provisioning, scoring, etc.)
│         │
│         ├─► SÍ ─► Camino COMPLETO: FDD + DDD + SDD + ATDD + BDD + TDD
│         │         (Proyectos: xdd-erp, PROJ-WekiCRM módulos complejos)
│         │
│         └─► NO ─► ¿El cliente/usuario define criterios de aceptación?
│                   │
│                   ├─► SÍ ─► Camino ESTÁNDAR: FDD + SDD + ATDD + BDD + TDD
│                   │         (Proyectos con cliente o product owner definido)
│                   │
│                   └─► NO ─► Camino ÁGIL: FDD + SDD + TDD
│                             (Features internas, scripts, herramientas)
│
└─► NO (mantenimiento/bugfix)
        │
        ├─► < 10 líneas afectadas ─► Directo (Art. 2 bypassed, como antes)
        │
        └─► > 20 líneas afectadas ─► Camino MÍNIMO: SDD + TDD
                                      (Spec del fix + test que reproduce el bug)
```

### Tabla de selección rápida

| Escenario | FDD | DDD | SDD | ATDD | BDD | TDD | Threat | STDD | SecDD |
|-----------|:---:|:---:|:---:|:----:|:---:|:---:|:------:|:----:|:-----:|
| ERP módulo nuevo (billing, inventory) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Feature con usuario definido | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| Tool interna / script | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| Bugfix > 20 líneas | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ⚠️ | ❌ |
| Refactoring de dominio | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| Integración de tercero (ISPcube, RADIUS) | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Infra / provisioning Telco | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

> ⚠️ = Opcional, según complejidad del dominio externo

---

## 7. Cambios en la estructura de carpetas

### Workspace Raíz — sin cambios

### Proyecto `PROJ-*` — adiciones

```
PROJ-NombreProyecto/
├── CLAUDE.md
├── README.md
├── memoria.md
├── prompts/                  ← NUEVO (Carpeta de recursos agénticos consolidados)
│   ├── agents/               ← CONSOLIDADO LOCAL (Agencia de 77 subagentes especializados)
│   │   ├── academic/         ← Personas académicas y de investigación
│   │   ├── design/           ← Especialistas visuales, HSL, UX/UI, accesibilidad
│   │   ├── engineering/      ← Devs backend, frontend, devops, firmware, smart contracts
│   │   ├── finance/          ← Controladores, contadores, FP&A, impuestos
│   │   ├── game-development/ ← Game design, level design, Unity, Unreal, Godot
│   │   └── ...               (marketing, sales, support, strategy, testing, etc.)
│   └── ...
│
├── idea/
│   └── briefing.md
│
├── docs/
│   ├── features/
│   │   └── FEATURES.md          ← NUEVO (FDD: catálogo de features)
│   ├── specs/
│   │   ├── SPEC.md              ← Sin cambios (DDD se embebe aquí)
│   │   ├── DOMAIN.md            ← NUEVO (DDD: modelo de dominio)
│   │   └── THREATS.md           ← NUEVO 🛡️ (Threat-Driven: modelo de amenazas)
│   ├── plans/
│   │   ├── PLAN.md              ← Reorganizado por features (FDD)
│   │   └── archive/
│   ├── analisis/
│   └── auditorias/
│
├── src/
│
├── tests/
│   ├── unit/                    ← NUEVO (TDD: tests unitarios primero)
│   │   └── *.test.ts
│   ├── features/                ← NUEVO (BDD: archivos Cucumber .feature)
│   │   └── *.feature
│   ├── acceptance/              ← NUEVO (ATDD: tests de aceptación)
│   │   └── *.acceptance.test.ts
│   ├── security/                ← NUEVO 🛡️ (STDD: security tests primero)
│   │   ├── injection/
│   │   ├── auth/
│   │   ├── authz/
│   │   ├── disclosure/
│   │   ├── availability/
│   │   ├── audit/
│   │   └── transport/
│   ├── e2e/                     ← Existente (Playwright)
│   └── results/
│
├── api/
├── interop/
└── design/
```

### Reglas nuevas (Art. X — pendientes de ratificación en Constitución):
> No existe `tests/features/*.feature` sin su correspondiente entrada en `docs/features/FEATURES.md`. No existe `src/*.ts` con lógica de negocio sin su `tests/unit/*.test.ts` previo.
> No existe `docs/specs/SPEC.md` aprobado sin su `docs/specs/THREATS.md` aprobado (en proyectos con datos sensibles). No existe función en el THREATS.md marcada con "security test requerido" sin su archivo en `tests/security/`.

---

## 8. Nuevas skills y workflows

### Skills nuevas propuestas

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `skill-tdd-coach` | Builder | Guía el ciclo Rojo-Verde-Refactor, detecta lógica sin test, propone test cases |
| `skill-ddd-modeler` | Architect | Modelado de bounded contexts, aggregates, ubiquitous language, context maps |
| `skill-bdd-writer` | Architect | Conversión de requisitos en `.feature` files Gherkin ejecutables |
| `skill-atdd-generator` | QA-Reviewer | Generación de stubs de acceptance tests desde criterios de aceptación |
| `skill-threat-modeler` 🛡️ | SecOps | Modelado STRIDE sobre el DOMAIN.md, clasificación de riesgo, generación de THREATS.md |
| `skill-stdd-coach` 🛡️ | Builder + SecOps | Guía el ciclo STDD, identifica funciones que requieren security tests, propone payloads adversariales |
| `skill-devsecops-pipeline` 🛡️ | SecOps | Integración de Semgrep, Gitleaks, Trivy, ZAP y Nuclei en el pipeline QA |

**Skills del AgentSecOps/SecOpsAgentKit** (copiar a `.agent/skills/` directamente):

| Skill kit | Herramienta | Agente en X-DD |
|-----------|------------|-----------------|
| `appsec/semgrep` | Semgrep SAST | QA-Reviewer (Tier 1) |
| `devsecops/gitleaks` | Gitleaks | QA-Reviewer (Tier 1) |
| `devsecops/container-grype` | Trivy/Grype | QA-Reviewer (Tier 1) |
| `devsecops/checkov` | Checkov IaC | SecOps |
| `secsdlc/reviewdog` | Reviewdog | QA-Reviewer (PRs) |
| `incident-response/ir-velociraptor` | Velociraptor | SecOps |

### Workflows nuevos propuestos

| Comando | Fase | Propósito |
|---------|------|-----------|
| `/domain-model` | Fase 2 | Genera el `DOMAIN.md` con Architect + TelcoExpert |
| `/threat-model` 🛡️ | Fase 2 | Genera el `THREATS.md` con Shannon SecOps + Architect |
| `/feature-catalog` | Fase 1 | Genera `FEATURES.md` con priorización RICE/MoSCoW |
| `/bdd-generate` | Fase 1 | Convierte REQUIREMENTS.md en archivos `.feature` |
| `/tdd-cycle` | Fase 4 | Guía el ciclo Rojo-Verde-Refactor para una función específica |
| `/stdd-cycle` 🛡️ | Fase 4 | Guía el ciclo STDD para una función/endpoint crítico |
| `/atdd-verify` | Fase 5 | Ejecuta los acceptance tests y genera reporte de cobertura |
| `/security-scan` 🛡️ | Fase 5 | Ejecuta SAST+Secrets+SCA y genera reporte consolidado |

### Modificaciones a workflows existentes

| Workflow | Cambio |
|----------|--------|
| `/fase-requisitos` | Agregar paso: "Generar FEATURES.md y archivos .feature skeleton" |
| `/xdd-build` | Agregar ciclo TDD antes de cada función de negocio |
| `/qa-review` | Tier 2 incluye ejecución de `.feature` files y acceptance tests |

---

## 9. Guía de transición

### Proyectos existentes (no greenfield)

**Para PROJ-ZeroAura (Fase 2 completada):**
1. Crear `docs/specs/DOMAIN.md` — retroalimentar el dominio del asistente androide (States, Commands, Events)
2. Crear `tests/unit/` — añadir TDD a nueva lógica en Rust/TS. No retro-testear todo (es deuda, no emergencia)
3. Los nuevos features siguen el camino completo

**Para xdd-erp (en desarrollo):**
1. Crear `docs/features/FEATURES.md` — convertir el PLAN.md actual en catálogo FDD
2. Crear `docs/specs/DOMAIN.md` — crítico para el ERP: billing, clients, provisioning son bounded contexts separados
3. A partir de hoy, cada nueva función de negocio requiere su test TDD previo

**Para PROJ-WekiCRM (producción):**
1. Solo nuevos features siguen X-DD
2. Bugs: `SDD + TDD` mínimo (el test que reproduce el bug antes del fix)

### Regla de adopción progresiva

```
Semana 1-2:  Adoptar TDD en Build (el gap más impactante, el más fácil de implementar)
Semana 1-2:  Agregar Semgrep + Gitleaks al pipeline (integración en < 30 min)
Semana 3-4:  Crear DOMAIN.md para xdd-erp y ZeroAura
Semana 3-4:  Crear THREATS.md para xdd-erp (dominio Telco con datos sensibles)
Mes 2:       Formalizar BDD con archivos .feature en proyectos activos
Mes 2:       Implementar STDD para funciones críticas de billing y auth
Mes 3:       Automatizar ATDD + DAST (ZAP/Nuclei) en el Tier 2 del pipeline QA
Mes 3:       Instalar skills del AgentSecOps/SecOpsAgentKit en Shannon SecOps
En curso:    FDD se adopta naturalmente al crear FEATURES.md en cada nuevo proyecto
En curso:    Shannon SecOps ejecuta /advanced-agentic-pentesting antes de cada release
```

### Checklist de proyecto X-DD listo (completo)

```
─── Funcional ───────────────────────────────────────────────────────────
[ ] docs/features/FEATURES.md creado con priorización RICE
[ ] docs/specs/DOMAIN.md creado y aprobado (si aplica DDD)
[ ] Al menos 1 archivo .feature por épica en tests/features/
[ ] Stubs de acceptance tests en tests/acceptance/
[ ] PLAN.md organizado por features verticales (no por capas)
[ ] Builder en modo TDD-first para lógica de negocio
[ ] Tier 2 ejecuta .feature files en /qa-review
[ ] REQUIREMENTS.md referencia los archivos .feature correspondientes

─── Seguridad 🛡️ ────────────────────────────────────────────────────────
[ ] docs/specs/THREATS.md creado y aprobado (proyectos con datos sensibles)
[ ] Ninguna amenaza CRÍTICA sin control documentado en THREATS.md
[ ] SEC-REQ-* del THREATS.md copiados al SPEC.md como requisitos no funcionales
[ ] Stubs de security tests en tests/security/ para cada función del THREATS.md
[ ] Semgrep y Gitleaks integrados en el Tier 1 del pipeline QA
[ ] Builder en modo STDD para funciones/endpoints críticos
[ ] npm audit / Trivy ejecutan en CI/CD sin vulnerabilidades críticas o altas
[ ] OWASP ZAP / Nuclei configurados para staging (antes de producción)
[ ] Skills del AgentSecOps/SecOpsAgentKit instaladas en Shannon SecOps
[ ] Shannon SecOps ejecuta /advanced-agentic-pentesting antes de cada release

─── Memoria y Agente Residente 🧠 ──────────────────────────────────────
[ ] Wing de MemPalace creado para el proyecto (mempalace_init_wing)
[ ] Rooms y Halls configurados (billing, auth, api, security, domain, testing...)
[ ] Hermes Agent instalado y apuntando a Ollama local
[ ] .hermes/skills/xdd-mempalace-rag.md configurado en el PROJ-*
[ ] Al menos 1 snippet AAAK escrito en MemPalace al cerrar la Fase 6
[ ] scripts/export_aaak_to_jsonl.py presente en el proyecto
[ ] training/axolotl_hermes_local.yaml configurado con el wing correcto
[ ] Primer fine-tuning ejecutado cuando MemPalace tiene ≥ 20 snippets
[ ] hermes-local disponible como modelo en Ollama
```

---

## 10. Agente Residente Local — NousResearch Hermes + MemPalace

Esta capa cierra el loop de aprendizaje del ecosistema X-DD: el conocimiento generado durante el desarrollo con Claude se convierte en entrenamiento para un agente local que vive dentro del proyecto.

### Arquitectura del loop

```
Claude Code (desarrollo)
        │
        │ genera conocimiento en cada Fase 6 (Retro)
        ↓
MemPalace AAAK Snippets
[LESSON] [DECISION] [DOMAIN] [SECURITY] [PROMPT] [WORKFLOW]
        │
        │ export_aaak_to_jsonl.py (threshold: 50 snippets nuevos)
        ↓
Dataset JSONL (formato ChatML / ShareGPT)
        │
        │ axolotl train + LoRA merge + GGUF
        ↓
Hermes-X-DD (modelo fine-tuned, local)
        │
        │ Ollama serve → OpenAI-compatible API
        ↓
Agente Residente en PROJ-*
        │ RAG → MemPalace en cada consulta
        │ Responde en español, conoce el dominio Telco y el codebase
        ↓
Claude consulta al residente para contexto histórico
```

### Modelo base recomendado

| Hardware | Modelo | VRAM | Velocidad |
|----------|--------|------|-----------|
| RTX 3080 / 4070 (12 GB) | `Hermes-4-14B Q4_K_M` | 10 GB | ~40 tok/s |
| RTX 3090 / 4090 (24 GB) | `Hermes-4-35B-A3B Q4_K_M` | 22 GB | ~35 tok/s |
| CPU (sin GPU) | `Hermes-4-14B Q4_K_M` | 16 GB RAM | ~8 tok/s |

> **Hermes-4-35B-A3B es MoE** — tiene 35B parámetros totales pero solo activa 3B en cada inferencia.
> Consume VRAM de modelo pequeño con capacidad de modelo grande. Ideal para hardware limitado.

### Nuevo agente: MLOps-Agent

```
MLOps-Agent
  Rol: MLOps del agente residente
  Activa: /train-hermes o al superar umbral de snippets en MemPalace
  Responsabilidades:
    - Monitorear threshold de snippets nuevos (50 por defecto)
    - Ejecutar pipeline: export → validate → train → merge → deploy
    - Versionar modelos: hermes-local-v1, v2, ...
    - Reportar métricas en memoria.md y como snippet [WORKFLOW]
```

### Nuevas skills

| Skill | Propósito |
|-------|-----------|
| `skill-hermes-resident` | Setup, consulta RAG, export dataset, fine-tuning, status |

### Nuevos workflows

| Comando | Propósito |
|---------|-----------|
| `/ask-hermes <query>` | Consulta al agente residente con RAG de MemPalace |
| `/ask-hermes domain <término>` | Consulta de ubiquitous language |
| `/ask-hermes lessons <área>` | Lecciones aprendidas sobre una tecnología |
| `/ask-hermes security <componente>` | Amenazas y controles del componente |
| `/train-hermes` | Pipeline completo de re-entrenamiento de Hermes-X-DD |

### Documentación completa

Ver `NOUS_AGENT_INTEGRATION.md` para la arquitectura completa, y los templates:
- `templates/08_mempalace_export_dataset.md` — script de exportación AAAK → JSONL
- `templates/09_hermes_resident_prompts.md` — system prompts y skills del agente residente

### Regla de adopción

```
Fase 0 (inmediato): Setup Hermes Agent + Ollama + RAG desde MemPalace
Fase 1 (semana 2-3): Acumular 20+ snippets AAAK durante desarrollo normal
Fase 2 (mes 1): Primer fine-tuning con Axolotl cuando se alcanza el threshold
Fase continua: Re-entrenamiento automático cada 50 snippets nuevos
```

---

## 11. La Agencia Local de Subagentes Especializados (prompts/agents)

La integración y consolidación de la biblioteca de agentes dota al ecosistema X-DD de un ejército modular y local de **77 subagentes hiper-especializados** organizados directamente dentro de `./prompts/agents/`. Esto garantiza que los agentes viajen físicamente con el proyecto y no dependan de instalaciones globales en el sistema operativo host.

### Consolidación Local y Portabilidad Absoluta
1. **Sin dependencias globales**: Al estar alojados dentro de `./prompts/agents/`, los perfiles agénticos no requieren de procesos de instalación externa ni compilación de scripts en la máquina host. Esto elimina la deuda técnica y asegura portabilidad absoluta en la migración a nuevos entornos (ej. Linux Mint).
2. **Rutas Relativizadas**: Cualquier referencia, carga o lectura de perfiles de agente se realiza de forma estrictamente relativa al workspace actual (`./prompts/agents/...`), garantizando que sea 100% independiente del sistema operativo y de la ruta absoluta del proyecto.
3. **Depreciación del Pipeline Global**: Los scripts de compilación heredados (`convert.sh`, `install.sh`) y la necesidad de prefijar globalmente con `agency-` quedan **depreciados / obsoletos** para el ecosistema local de X-DD, simplificando la arquitectura y reduciendo la sobrecarga de archivos en el repositorio.

### Directrices de Delegación en el Flujo Diario

Cuando el Orquestador Principal (`/xdd`) o el usuario se enfrentan a un desafío altamente especializado (ej. optimización fina de un pipeline de render, auditorías de accesibilidad WCAG 2.2, modelado financiero FP&A o firmware IoT), se delega la tarea instanciando al agente específico desde `./prompts/agents/`:
- **Para optimización visual:** Invocar `whimsy-injector` o `inclusive-visuals-specialist` (en `./prompts/agents/design/`).
- **Para tuning de rendimiento:** Invocar `database-optimizer` o `filament-optimization-specialist` (en `./prompts/agents/engineering/`).
- **Para lógica DeFi/Web3:** Invocar `solidity-smart-contract-engineer` (en `./prompts/agents/engineering/`).
- **Para refinamiento ágil y micro-cambios:** Invocar `minimal-change-engineer` (en `./prompts/agents/engineering/`).

---

> **Mantenido por:** Architect + Orchestrator
> **Gobernado por:** Constitución X-DD v2.0 (con ampliaciones y Agencia Externa ratificadas)
> **Ley suprema:** constitucion.md
