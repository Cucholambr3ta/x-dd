# X-DD Root Manifest

Este manifiesto define el contexto operativo y gobernanza para **Claude Code** y otros agentes cuando trabajan en un proyecto X-DD.

## ⚖️ Gobernanza
- La ley suprema local reside en la [Constitución X-DD](./docs/constitucion.md).
- **Lectura Obligatoria (Art. 3):** Antes de cualquier iteración, lee el archivo `memoria.md` del proyecto activo.
- **Directorio de Agentes:** Para delegar en subagentes especializados, consulta el [Directorio de Agentes](./docs/equipo.md).

## 🚀 Misión
Desarrollar software de alta calidad mediante el pipeline X-DD: la integración de múltiples metodologías *-Driven Development* (SDD, FDD, BDD, ATDD, DDD, TDD, STDD, SecDD, Threat-Driven) como capas sobre un Gated Pipeline de 6 fases.

## 🛠️ Guías de Desarrollo
- **Guía SDD (Pipeline Elite):** [docs/SDD_GUIDE.md](./docs/SDD_GUIDE.md)
- **Integración X-DD completa:** [docs/X-DD_Integration_Guide.md](./docs/X-DD_Integration_Guide.md)
- **Instalación de herramientas:** [INSTALL.md](./INSTALL.md)

## 💎 Directrices de Calidad
1. **Portabilidad Absoluta:** Prohibido generar rutas absolutas del host. Toda ruta debe ser estrictamente relativa (`./` o `../`).
2. **Cero Duplicados:** No clonar directorios de agencias externas. Se utiliza únicamente la biblioteca consolidada en `./prompts/agents/`.
3. **Flujo Gated Pipeline (Art. 2):** Solicita el comando `"APROBADO"` antes de realizar grandes refactorizaciones o pasar de fases en el plan.

---
*X-DD System — Excelencia Operativa*
