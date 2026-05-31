# Guía [IDE_NAME] — Agentes, Skills y Workflows compatibles con X-DD

> Plantilla SSoT v0.2 (S19). Cada guía IDE sigue esta estructura; las secciones
> marcadas `[IDE_SPECIFIC]` varían por IDE. Las demás son ~80% comunes.
> Ver `docs/dev/README.md` para instrucciones de uso.

**Proyecto:** `personal/x-dd/` — sistema multi-IDE install-once
**IDE:** [IDE_NAME]
**Versión doc:** [VERSION]
**Fecha:** [FECHA]
**Estado adapter:** [STATUS] en `scripts/xdd-adapt.sh` (`adapt_[ide]`)

---

## 1. Propósito [COMMON]
[Descripción del objetivo de integración]

## 2. Verdad técnica — capacidades del IDE [IDE_SPECIFIC]

| Capacidad | Claude Code (ref) | [IDE_NAME] |
|---|---|---|
| Slash commands locales | ✅ | [IDE_VALUE] |
| Triggers de Chat | ✅ | [IDE_VALUE] |
| Rules de archivos | ✅ | [IDE_VALUE] |
| Skills locales | manual | [IDE_VALUE] |
| MCP | ✅ | [IDE_VALUE] |

## 3. Arquitectura X-DD → [IDE_NAME] [IDE_SPECIFIC]
[Diagrama flowchart o descripción del flujo SSoT → runtime]

## 4. Matriz comparativa multi-IDE [COMMON]
[Tabla con todos los IDEs; actualizar GUIA_CLAUDE_CODE como ref]

## 5. Workflows — SSoT y consumo [IDE_SPECIFIC]
[Cómo se activan los workflows en este IDE]

## 6. Agentes — SSoT y consumo [IDE_SPECIFIC]
[Cómo se usan los agentes]

## 7. Skills [IDE_SPECIFIC]
[Convención de skills para este IDE]

## 8. Capa adapter — output [IDE_SPECIFIC]
[Qué genera xdd-adapt.sh para este IDE]

## 9. Instalación end-to-end [COMMON]
```bash
bash scripts/xdd-adapt.sh [ide] --dest=/ruta/proyecto
```

## 10. Troubleshooting [IDE_SPECIFIC]
[Tabla de síntomas / causas / soluciones]

## 11. Checklist para el Agente [COMMON]
- [ ] Workflows definidos en `.agent/workflows/*.md` con frontmatter `description`.
- [ ] Rutas relativas en prompts (no absolutas del host).
- [ ] `ide_compat` correcto en `registry.json` para este IDE.
- [ ] Skills con `name` + `description` en frontmatter mínimo.

## 12. Referencias [COMMON]
- [ADR-0034](../adr/0034-universal-ide-adapter.md) — Universal IDE Adapter
- [docs/IDE_SETUP.md](../IDE_SETUP.md) — matriz de adapters
