# ADR-0044: Deprecar MCP — no es necesario para la orquestación X-DD

**Estado:** Aceptada
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

ADR-0005 estableció MCP (Model Context Protocol) como integración preferida, con un
`xdd-mcp-server` propio que expone tools a clientes MCP. ADR-0007 añadió una vía de
integración por MCP genérico. La hipótesis era que MCP sería el canal universal para que
cualquier IDE consumiera X-DD.

El piloto **agentix** (réplica de X-DD construida sin MCP, por decisión explícita del
owner) **demostró lo contrario**: la orquestación multi-agente y la integración con 7 IDEs
funcionan completamente por **copia real** de comandos/workflows a cada IDE (`xdd-adapt.sh`,
`xdd_adapters.py`). MCP añade un servidor, un proceso, y superficie de mantenimiento sin
cubrir un caso que la copia real no resuelva ya.

Evidencia: agentix orquesta pipelines (gate HMAC, runtime seq/parallel, 7 adapters) con 0
dependencia de MCP y 41 tests verdes.

## Decisión

**Deprecar MCP en v0.1.x; eliminarlo en v0.2.0.** No se borra ahora para no romper a
usuarios que ya lo configuraron.

Alcance de esta deprecación (v0.1.x):
- ADR-0005 → estado **Deprecado por ADR-0044**; ADR-0007 → parte MCP deprecada (adapters
  de copia real siguen vigentes).
- Avisos `⚠️ DEPRECADO v0.2.0` en `docs/MCP_INTEGRATION.md` y `scripts/xdd-mcp-install-global.sh`.
- `xdd-doctor.sh`: checks MCP pasan de informativos a marcados como deprecados (no fallan).
- **NO se toca** `xdd-mcp-server/`, ni los tests MCP, ni los manifests: siguen presentes y
  verdes en v0.1.x.

Alcance diferido (v0.2.0, ADR futuro):
- Borrado de `xdd-mcp-server/`, `scripts/xdd-mcp-install-global.sh`, tests MCP, refs en
  manifests y docs. Migración de cualquier usuario a la vía de copia real.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Borrar MCP ahora (v0.1.0) | Repo más limpio ya | Rompe a quien lo configuró; 116 archivos tocados justo en el release | Riesgo alto pre-release |
| Deprecar ahora, borrar v0.2.0 (elegida) | Señal clara, sin romper; release seguro | MCP vive un ciclo más como peso muerto declarado | — |
| Mantener MCP indefinidamente | Cero trabajo | Servidor + mantenimiento sin valor demostrado | Contradice la evidencia de agentix |

## Consecuencias

- **Positivas:** dirección clara (copia real es el canal), release v0.1.0 sin romper nada,
  menos superficie de mantenimiento a partir de v0.2.0.
- **Trade-offs:** coexistencia temporal de MCP deprecado en v0.1.x.
- **Neutras:** quien use MCP en v0.1.x sigue funcionando; tiene un ciclo para migrar.

## Relación

- **Deprecación de:** ADR-0005 (completa), ADR-0007 (parte MCP).
- **Refuerza:** ADR-0034 (universal IDE adapter por copia real), ADR-0046 (adapters en código).
- **Difiere a v0.2.0:** borrado físico de MCP (ADR futuro).
