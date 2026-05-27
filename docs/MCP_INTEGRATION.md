# MCP Integration — `xdd-mcp-server`

> X-DD habla **Model Context Protocol** nativamente desde v0.1.0 (Sprint 6, [ADR-0005](adr/0005-mcp-preferido-y-server-propio.md)).
> Cualquier cliente MCP (Claude Code, Cursor, Continue, Zed, Cline, Windsurf, etc.) puede conectar al server propio de X-DD y consumir 6 tools sin adapter específico.

## Por qué importa

Sin un MCP server propio, X-DD necesitaría un adapter dedicado por cada IDE (9+ adapters). Con MCP, ese ecosistema completo accede a las mismas capacidades sin escribir código adicional. Implementa la promesa del plan v1.1: "MCP es la vía preferida de integración".

## Características

- **Python ≥3.9 stdlib pura** — sin deps PyPI obligatorias (sin `fastmcp`, sin `mcp-sdk`).
- **JSON-RPC 2.0 sobre stdio** — protocolo MCP estándar.
- **6 tools de v0.1.0** (ver tabla abajo).
- **Whitelist de paths** — `xdd_get_phase_artifacts` solo lee dentro de `.xdd/` (T4.3 mitigación del threat model).
- **No `exec` ni `shell`** — el server jamás ejecuta workflows; los devuelve para que el orquestador los interprete (T6.3 mitigación).
- **Reusa `scripts/xdd-gate.py`** como módulo para evitar duplicación.

## Tools v0.1.0

| Tool | Descripción | Schema input |
|------|-------------|---------------|
| `xdd_validate_phase` | Valida fase (status + checksums + firma HMAC) | `{phase}` |
| `xdd_transition_phase` | Valida transición secuencial | `{from_phase, to_phase}` |
| `xdd_list_workflows` | Lista workflows con `description:` del frontmatter | `{}` |
| `xdd_invoke_workflow` | Devuelve contenido del workflow (no lo ejecuta) | `{name}` |
| `xdd_list_agents` | Lista agentes del registry (filtrable por categoría) | `{category?}` |
| `xdd_get_phase_artifacts` | Lista artefactos en `.xdd/<fase>/` | `{phase}` |

## Smoke test

```bash
# Listar tools en JSON (no inicia el server stdio)
python3 -m "xdd-mcp-server" --check
# → 6 tools

# Versión
python3 -m "xdd-mcp-server" --version
# → xdd-mcp-server v0.1.0-dev

# Test end-to-end por stdio (3 mensajes JSON-RPC)
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"xdd_list_workflows","arguments":{}}}' \
  | python3 -m "xdd-mcp-server"
```

## Setup por IDE

### Claude Code

Añadir a `~/.claude/mcp_servers.json` (o usando `claude mcp add`):
```json
{
  "mcpServers": {
    "xdd": {
      "command": "python3",
      "args": ["-m", "xdd-mcp-server"],
      "cwd": "/ruta/a/tu/proyecto-x-dd"
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "xdd": {
      "command": "python3",
      "args": ["-m", "xdd-mcp-server"],
      "cwd": "/ruta/a/tu/proyecto-x-dd"
    }
  }
}
```

### Zed

En `~/.config/zed/settings.json`:
```json
{
  "context_servers": {
    "xdd": {
      "command": {
        "path": "python3",
        "args": ["-m", "xdd-mcp-server"]
      }
    }
  }
}
```

### Continue.dev

`~/.continue/config.json`:
```json
{
  "mcpServers": [{
    "name": "xdd",
    "command": "python3",
    "args": ["-m", "xdd-mcp-server"]
  }]
}
```

### Cline / Roo Code

Settings → MCP Servers → Add:
```json
{
  "xdd": {
    "command": "python3",
    "args": ["-m", "xdd-mcp-server"]
  }
}
```

### Windsurf (Codeium)

Settings → MCP → Add server:
```json
{
  "name": "xdd",
  "command": "python3",
  "args": ["-m", "xdd-mcp-server"]
}
```

> ⚠️ Las sintaxis exactas de cada IDE pueden cambiar entre versiones. Verificá la
> documentación oficial de tu IDE para MCP server config. Si encontrás diferencias,
> abrí un issue.

## Limitaciones v0.1.0

- **Sin SSE transport** — solo stdio. Suficiente para todos los IDEs actuales.
- **Sin Resources ni Prompts** — solo Tools. Suficiente para invocación.
- **Sin autenticación** — el server escucha local; no expuesto a red.
- **Sin streaming** — respuestas en single message.

Estas limitaciones se evaluarán en v0.2.0 si la comunidad las solicita.

## Modelo de amenazas

Mitigaciones implementadas (de [.xdd/spec/THREATS.md](../.xdd/spec/THREATS.md)):

| ID | Mitigación implementada |
|----|-------------------------|
| T4.3 | `xdd_get_phase_artifacts` whitelist `.xdd/` |
| T6.3 | Sin `xdd_exec` ni `xdd_shell` en el tool set; `xdd_invoke_workflow` devuelve contenido, no ejecuta |
| T2.4 | Inputs validados contra schema antes de invocar |

## Tests

Suite completa en [tests/test_mcp_server.py](../tests/test_mcp_server.py) — 17 casos cubriendo
JSON-RPC dispatcher, tools individuales, error handling y smoke test.

```bash
python3 -m pytest tests/test_mcp_server.py -v
```

## Arquitectura

```
xdd-mcp-server/
├── __init__.py        # versión
├── __main__.py        # entrypoint CLI (--check, --version)
├── server.py          # JSON-RPC 2.0 dispatcher
└── tools.py           # 6 tools + reuse de scripts/xdd-gate.py
```

El server NO necesita un proceso permanente; el orquestador lo arranca en stdio cuando lo necesita y lo cierra al terminar.

## Stack MCP completo recomendado X-DD (3 servers complementarios)

X-DD recomienda 3 MCP servers paralelos según necesidad:

| MCP Server | Origen | License | Tools | Función |
|---|---|---|---|---|
| **xdd-mcp-server** | X-DD propio (Sprint 6) | MIT | 6 | Gates HMAC + workflows + agents + phase artifacts |
| **MemPalace** | dep externa (ADR-0004) | MIT | 29 | Memoria semántica (ChromaDB + SQLite) + wings/rooms/drawers |
| **GitNexus** | dep externa (ADR-0033) | PolyForm Noncomm ⚠️ | 16 | Code intelligence (AST grafo, impact analysis, hybrid search BM25+semantic+RRF, 14 langs) |

**3 sirven en paralelo sin conflicto**: cada uno tiene namespace propio + responsabilidad distinta.
- xdd-mcp-server = pipeline/process intelligence
- MemPalace = semantic memory across sessions
- GitNexus = structural code knowledge

`xdd-start.sh` activa automáticamente MemPalace + GitNexus si CLI instalados. Sin ellos, X-DD degrada (xdd-fs-context Sprint 19 sirve como baseline portable zero-dep para code context).

⚠️ **GitNexus license**: PolyForm Noncommercial 1.0.0. Uso personal/research/non-profit = gratis. Comercial = paid license. Ver [ADR-0033](adr/0033-gitnexus-tier1-companion.md) + [DEPENDENCIES.md](../DEPENDENCIES.md).
