# Sprint 6 — Build Report (MCP Server propio ⭐)

> Fase 4-Build (4/5). Cumple [ADR-0005](../../../docs/adr/0005-mcp-preferido-y-server-propio.md):
> X-DD habla MCP nativo, reduciendo el costo de soportar nuevos IDEs.

## Sobre-mejora estratégica

Esta sprint **NO estaba en MEJORAS-X-DD.md v1.1**. El plan original solo
consumía el MCP server de MemPalace. Tras el análisis del Sprint 0, ADR-0005
formalizó la necesidad de un server propio. Sin este Sprint, X-DD necesitaría
un adapter por cada IDE soportado (9+ adapters); con MCP, todos los IDEs
compatibles consumen el mismo server.

## Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| Server JSON-RPC stdio | `xdd-mcp-server/server.py` | ✅ initialize / tools/list / tools/call + error codes |
| 6 tools | `xdd-mcp-server/tools.py` | ✅ con reuse de `scripts/xdd-gate.py` |
| Entrypoint CLI | `xdd-mcp-server/__main__.py` | ✅ `--check` smoke test + `--version` |
| Package init | `xdd-mcp-server/__init__.py` | ✅ versión |
| Tests pytest | `tests/test_mcp_server.py` | ✅ **17/17 verdes** |
| Documentación | `docs/MCP_INTEGRATION.md` | ✅ setup por IDE (Claude Code, Cursor, Zed, Continue, Cline, Windsurf) |

## Tools v0.1.0

| Tool | Descripción |
|------|-------------|
| `xdd_validate_phase` | Validación de fase + firma HMAC |
| `xdd_transition_phase` | Transición secuencial |
| `xdd_list_workflows` | Catálogo desde `.agent/workflows/` |
| `xdd_invoke_workflow` | Devuelve contenido (NO ejecuta — T6.3) |
| `xdd_list_agents` | Registry (filtrable) |
| `xdd_get_phase_artifacts` | Whitelist `.xdd/` (T4.3) |

## Decisiones técnicas

- **Python stdlib pura** — sin `fastmcp` ni `mcp-sdk`. Cumple ADR-0003.
- **Reuso de `scripts/xdd-gate.py`** vía `importlib` — evita duplicación
  de lógica HMAC/checksums.
- **Sin transports SSE** — solo stdio para v0.1.0.
- **JSON-RPC manual** — implementación mínima (initialize / tools/list /
  tools/call / notifications/initialized) suficiente para todos los IDEs MCP-compat.

## Validaciones

```bash
# Smoke test
python3 -m "xdd-mcp-server" --check
# → 6 tools listadas

# JSON-RPC end-to-end (stdio)
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"xdd_list_workflows","arguments":{}}}' \
  | python3 -m "xdd-mcp-server"
# → initialize OK, 6 tools, 48 workflows

# Tests
python3 -m pytest tests/test_mcp_server.py tests/test_gate.py -q
# → 34 passed (17 mcp + 17 gate)

# Linters
bash scripts/lint-workflows.sh && bash scripts/xdd-doctor.sh
# → verdes
```

## Cobertura del modelo de amenazas

| Amenaza | Mitigación |
|---------|------------|
| **T4.3** (MCP expone artefactos sensibles) | `ALLOWED_ARTIFACT_PREFIXES = (".xdd/",)` |
| **T6.3** (Tool que ejecuta arbitrary code) | NO existe `xdd_exec` ni `xdd_shell`; `xdd_invoke_workflow` devuelve contenido para que el orquestador lo interprete |
| **T2.4** (Inputs mal validados) | Cada tool valida vía schema antes de ejecutar (`tools/call` con `arguments` typed) |

## Próximo paso
**Sprint 7 — Adapters IDE + tests E2E**. Sólo necesitamos adapters explícitos
para Claude Code y OpenCode (ADR-0007); el resto consume via este server MCP.
