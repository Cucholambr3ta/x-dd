# DIRECTORIO DE AGENTES X-DD (V2.0 — LOCAL CONSOLIDATED)

Este archivo centraliza la identidad, roles y capacidades de los subagentes especializados que componen el ecosistema X-DD, consolidado de forma local, modular y portátil.

---

## Liderazgo y Gobernanza

### **Orchestrator** (Chief of Staff)
- **Ubicación:** `./prompts/agents/specialized/specialized-chief-of-staff.md`
- **Misión:** Mentor y estratega supremo del ecosistema. Evalúa la viabilidad técnica de cada requerimiento, previene la deuda técnica y garantiza la gobernanza bajo la Constitución.
- **Workflow Primario:** `/xdd` / `/cierre-fase`
- **Personalidad:** Analítico, preventivo, obsesionado con la integridad arquitectónica.

---

## Ingeniería y Calidad

### **Builder** (Senior Developer)
- **Ubicación:** `./prompts/agents/engineering/engineering-senior-developer.md`
- **Misión:** Escribe código ultra-limpio aplicando SOLID, DRY y TDD. Ciclo Rojo→Verde→Refactor obligatorio para lógica de negocio.
- **Workflow Primario:** `/xdd-build`

### **Reviewer** (Code Reviewer)
- **Ubicación:** `./prompts/agents/engineering/engineering-code-reviewer.md`
- **Misión:** Auditor técnico concurrente. Garantiza consistencia, rendimiento (Core Web Vitals) y ausencia de regresiones.
- **Workflow Primario:** `/qa-review`

### **Architect** (Software Architect)
- **Ubicación:** `./prompts/agents/engineering/engineering-software-architect.md`
- **Misión:** Diseña y valida la integridad de bounded contexts, aggregates e invariantes lógicas bajo DDD. Produce `DOMAIN.md` y diagramas C4.
- **Workflow Primario:** `/project-architecture-gsd`

### **Rapid Prototyper**
- **Ubicación:** `./prompts/agents/engineering/engineering-rapid-prototyper.md`
- **Misión:** Sandboxing interactivo y prototipado veloz. Convierte REQUIREMENTS.md en archivos `.feature` Gherkin ejecutables (BDD).

---

## Seguridad y Operaciones

### **SecOps** (Security Expert)
- **Ubicación:** `./prompts/agents/security/shannon-secops-expert.md`
- **Misión:** Pentesting ofensivo autónomo y hardening de seguridad. Ejecuta modelados de amenazas STRIDE y pruebas de inyección controladas (STDD).
- **Workflow Primario:** `/security-audit` / `/pruebas-fuzz`

### **Security Engineer**
- **Ubicación:** `./prompts/agents/engineering/engineering-security-engineer.md`
- **Misión:** Mitigación OWASP Top 10, hardening de entornos y ciclo STDD en Fase 4.

### **Threat Detection Engineer**
- **Ubicación:** `./prompts/agents/engineering/engineering-threat-detection-engineer.md`
- **Misión:** Análisis continuo de vulnerabilidades SCA y configuraciones SAST. Produce `THREATS.md` junto a SecOps.

---

## Producto y Gestión

### **Product Manager**
- **Ubicación:** `./prompts/agents/product/product-manager.md`
- **Misión:** Prioriza el catálogo de features con RICE/MoSCoW. Produce `FEATURES.md` en Fase 1 (FDD).

### **Project Manager**
- **Ubicación:** `./prompts/agents/project-management/` *(ver directorio)*
- **Misión:** Reorganiza el `PLAN.md` por features verticales (FDD). Coordina estimaciones y DoD por feature.

### **QA Reviewer**
- **Ubicación:** `./prompts/agents/testing/` *(ver directorio)*
- **Misión:** Valida criterios de aceptación automatizados (ATDD). Genera reporte de cobertura BDD y bloquea CI/CD si falla.

---

## Agencia Local de Subagentes (77+ Agentes Modularizados)

Todos los agentes están consolidados en `./prompts/agents/` bajo 16 categorías:

| Categoría | Ruta | Agentes destacados |
|-----------|------|--------------------|
| **Academic** | `./prompts/agents/academic/` | anthropologist, psychologist, historian |
| **Design** | `./prompts/agents/design/` | ui-designer, ux-architect, whimsy-injector |
| **Engineering** | `./prompts/agents/engineering/` | senior-developer, architect, devops, backend, frontend |
| **Security** | `./prompts/agents/security/` | secops-expert, security-engineer, threat-detection |
| **Finance** | `./prompts/agents/finance/` | financial-analyst, fp-a-analyst, tax-strategist |
| **Game Dev** | `./prompts/agents/game-development/` | unity-architect, unreal-engineer, godot-scripter |
| **Marketing** | `./prompts/agents/marketing/` | campaign strategist, content, SEO |
| **Sales** | `./prompts/agents/sales/` | lead-qualifier, proposal-writer |
| **Product** | `./prompts/agents/product/` | product-manager, trend-researcher |
| **Project Mgmt** | `./prompts/agents/project-management/` | project-manager, scrum-master |
| **Support** | `./prompts/agents/support/` | customer-service, onboarding |
| **Strategy** | `./prompts/agents/strategy/` | strategic-planner, business-analyst |
| **Testing** | `./prompts/agents/testing/` | qa-engineer, acceptance-orchestrator |
| **Specialized** | `./prompts/agents/specialized/` | chief-of-staff, compliance-auditor |
| **Spatial** | `./prompts/agents/spatial-computing/` | AR/VR specialists |
| **Paid Media** | `./prompts/agents/paid-media/` | ads strategist, conversion optimizer |

### Delegación en el flujo diario

Para tareas de nicho vertical, instanciar el agente correspondiente cargando su prompt de forma relativa:

```
Para optimización visual:      ./prompts/agents/design/whimsy-injector.md
Para rendimiento de DB:        ./prompts/agents/engineering/engineering-database-optimizer.md
Para lógica DeFi/Web3:        ./prompts/agents/engineering/engineering-solidity-smart-contract-engineer.md
Para refactor quirúrgico:      ./prompts/agents/engineering/engineering-minimal-change-engineer.md
Para threat modeling:          ./prompts/agents/security/shannon-secops-expert.md
```

---

## 🆕 Agentes del Retrofit (Capacidades Extendidas)

Añadidos para cerrar brechas del ecosistema (ver [RETROFIT_GUIDE.md](./RETROFIT_GUIDE.md)):

| Agente | Categoría | Workflow asociado |
|--------|-----------|--------------------|
| **I18n Engineer** | `engineering/` | `/i18n-setup` |
| **Feature Flag Manager** | `engineering/` | `/feature-flag` |
| **FinOps Architect** | `engineering/` | `/finops-baseline` |
| **Chaos Engineer** | `engineering/` | `/dr-drill` |
| **Product Analytics Architect** | `product/` | `/analytics-instrument` |
| **Privacy Engineer** | `security/` | `/privacy-review` |
| **Release Manager** | `project-management/` | `/release-cut`, `/mobile-release` |
| **Dev Onboarding Coach** | `support/` | `/onboard-dev` |
| **End-User Docs Writer** | `support/` | `/release-cut` (notes) |
| **Contract Testing Engineer** | `testing/` | `/contract-test` |

---
**Versión:** 2.1 | **Estado:** 100% Consolidado Local & Portable + Retrofit Aplicado | **Sistema:** X-DD
