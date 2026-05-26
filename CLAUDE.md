# X-DD Root Manifest

Este manifiesto define el contexto operativo y gobernanza para **Claude Code** y otros agentes cuando trabajan en un proyecto X-DD.

## ⚖️ Gobernanza
- La ley suprema local reside en la [Constitución X-DD](./docs/constitucion.md).
- **Lectura Obligatoria (Art. 3):** Antes de cualquier iteración, lee el archivo `memoria.md` del proyecto activo.
- **Directorio de Agentes:** Para delegar en subagentes especializados, consulta el [Directorio de Agentes](./docs/equipo.md).

## 🚀 Misión
Desarrollar software de alta calidad mediante el pipeline X-DD: la integración de múltiples metodologías *-Driven Development* (SDD, FDD, BDD, ATDD, DDD, TDD, STDD, SecDD, Threat-Driven) como capas sobre un Gated Pipeline de 6 fases.

## 🛠️ Guías de Desarrollo
- **Pipeline X-DD completo:** [docs/X-DD_Integration_Guide.md](./docs/X-DD_Integration_Guide.md)
- **Instalación de herramientas:** [INSTALL.md](./INSTALL.md)
- **Capacidades extendidas (retrofit):** [docs/RETROFIT_GUIDE.md](./docs/RETROFIT_GUIDE.md)

## 📦 Artefactos del proyecto (cuando aplican)

Los workflows producen artefactos versionables en la raíz del proyecto. Consulta el workflow correspondiente antes de modificarlos:

| Artefacto | Producido por | Propósito |
|-----------|---------------|-----------|
| `memoria.md` | `/xdd`, `/cierre-fase` | Flight recorder (Art. 3) |
| `lecciones.md` | `/cierre-fase` | Aprendizajes acumulados |
| `DISCOVERY.md` | `/ux-discovery` | Validación de problema |
| `SPEC.md` | `/project-architecture-gsd` | Especificación técnica |
| `DOMAIN.md` | `/project-architecture-gsd` | Modelo de dominio (DDD) |
| `THREATS.md` | `/project-architecture-gsd` | Modelo de amenazas (STRIDE) |
| `PRIVACY.md` | `/privacy-review` | PII y bases legales (GDPR) |
| `FEATURES.md` | `/fase-requisitos` | Catálogo FDD |
| `PLAN.md` | `/plan-fases` | Plan por features |
| `openapi.yaml` | `/api-contract` | Contrato API |
| `FLAGS.md` | `/feature-flag` | Inventario de feature flags |
| `events.schema.json` | `/analytics-instrument` | Schema de eventos |
| `BUDGET.md` | `/finops-baseline` | Presupuesto cloud |
| `DR_PLAN.md` | `/dr-drill` | Plan de DR |
| `ONBOARDING.md` | `/onboard-dev` | Guía de onboarding |
| `CHANGELOG.md` + `RELEASES/v*.md` | `/release-cut` | Trazabilidad de releases |
| `docs/adr/NNNN-*.md` | `/adr-new` | Decisiones arquitectónicas |
| `xdd.profile.yml` | `xdd-init.sh` | Perfil del proyecto |

## 💎 Directrices de Calidad
1. **Portabilidad Absoluta:** Prohibido generar rutas absolutas del host. Toda ruta debe ser estrictamente relativa (`./` o `../`).
2. **Cero Duplicados:** No clonar directorios de agencias externas. Se utiliza únicamente la biblioteca consolidada en `./prompts/agents/`.
3. **Flujo Gated Pipeline (Art. 2):** Solicita el comando `"APROBADO"` antes de realizar grandes refactorizaciones o pasar de fases en el plan.

---
*X-DD System — Excelencia Operativa*
