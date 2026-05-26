# ADR-0004: MemPalace como dependencia externa, no fork ni vendor

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

El README anterior presentaba MemPalace como "pieza del ecosistema X-DD", creando confusión de ownership. Hechos verificados:

- MemPalace es proyecto independiente: [github.com/MemPalace/mempalace](https://github.com/MemPalace/mempalace)
- Versión actual: v3.3.2 — maduro.
- Licencia: MIT.
- Distribución: PyPI (`pip install mempalace`).
- API: CLI + MCP server con 29 tools.
- Sitio oficial: mempalaceofficial.com (advertencia oficial sobre dominios impostores).

## Decisión

**MemPalace es dependencia externa MIT vía PyPI con constraint `>=3.3.0`.** X-DD nunca:
- Forkea MemPalace.
- Empaqueta su código.
- Implementa funcionalidad equivalente "por si MemPalace cambia".

El acoplamiento es **vía interfaces estables** (CLI `mempalace init|mine|search|wake-up` y MCP server).

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Fork bajo control de X-DD | Estabilidad de API garantizada | Duplica esfuerzo de mantenimiento, fragmenta ecosistema | Antitético al espíritu OSS |
| Vendor (copy/paste del código) | Sin red durante install | Imposible mantener actualizado, licencia se complica | No |
| Re-implementar memoria semántica en X-DD | Control total | Recrear ChromaDB + grafo + MCP es un proyecto en sí mismo | Out of scope para v0.1.0 |
| Hacer MemPalace opcional sin alternativa | Cero dep mínima | Pierde el diferenciador del framework (memoria persistente) | Es opcional pero recomendado |

## Consecuencias

- **Positivas:** ownership claro; usuarios reciben mejoras de MemPalace upstream sin esperar a X-DD; licencias compatibles.
- **Negativas / Trade-offs:** breaking changes en MemPalace pueden afectar X-DD. Mitigación: `version_constraint` en `xdd.config.yml`, Renovate config para alertas tempranas.
- **Neutras:** X-DD degrada elegantemente si MemPalace no está instalado (los hooks ya tienen guard `command -v mempalace`).

## Plan de revisión

Revisitar si MemPalace cambia licencia, abandono o si surge una alternativa MIT equivalente con mejor API.
