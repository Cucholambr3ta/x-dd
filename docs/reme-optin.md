# ReMe — Memory Management Kit (opt-in)

ReMe es un toolkit de gestion de memoria conversacional para agentes IA.
Licencia: Apache-2.0 (compatible con uso comercial, sin restricciones).
Repo: https://github.com/agentscope-ai/ReMe

> ReMe es OPT-IN. X-DD no lo activa por defecto. Activar con `XDD_REME=1`.
> MemPalace (indexacion de codebase) sigue siendo el sistema de continuidad por defecto.
> ReMe y MemPalace son complementarios, no sustitutos.

---

## Diferencia entre ReMe y MemPalace

| Aspecto | MemPalace | ReMe |
|---------|-----------|------|
| Que indexa | Archivos del repo (codigo, docs, workflows) | Conversaciones del agente (dialogo, preferencias, decisiones) |
| Busqueda | RAG sobre codebase | Hibrida vector+BM25 sobre historial conversacional |
| Persistencia | Indice semantico del repo | MEMORY.md (long-term) + journal diario |
| Cuando usar | Continuidad de contexto sobre el proyecto | Memoria del agente entre sesiones largas |
| Licencia | MIT | Apache-2.0 |

Usar ambos en conjunto: MemPalace para "que hay en el repo", ReMe para "que hemos hablado y decidido".

---

## Instalacion

```bash
pip install "reme-ai[light]"
```

Variables de entorno requeridas:

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `LLM_API_KEY` | API key del LLM | `sk-xxx` (Anthropic, OpenAI, etc.) |
| `LLM_BASE_URL` | Base URL del LLM (OpenAI-compatible) | `https://api.anthropic.com/v1` |
| `EMBEDDING_API_KEY` | API key para embeddings (opcional) | `sk-xxx` |
| `EMBEDDING_BASE_URL` | Base URL embeddings (opcional) | (mismo endpoint) |

---

## Activacion

```bash
XDD_REME=1 bash scripts/xdd-start.sh
```

O setear permanentemente en el entorno del proyecto:

```bash
echo "export XDD_REME=1" >> ~/.profile
```

Con `XDD_REME=1`, X-DD:
1. En `session:start`: carga `MEMORY.md` + journal del dia anterior si existe.
2. En `stop`: ejecuta `summary_memory` async para persistir la sesion en `memory/YYYY-MM-DD.md`.

---

## Estructura de archivos generada por ReMe

```
<proyecto>/
├── MEMORY.md                   # Memoria long-term: preferencias, decisiones clave, patrones
├── memory/
│   └── YYYY-MM-DD.md           # Journal diario: resumen de cada sesion
├── dialog/
│   └── YYYY-MM-DD.jsonl        # Dialogo raw antes de compactacion (JSONL)
└── tool_result/
    └── <uuid>.txt              # Cache de outputs largos de herramientas (TTL auto)
```

`MEMORY.md` y `memory/` son versionables (commitear). `dialog/` y `tool_result/` son efimeros (gitignore).

---

## Capacidades que activa

| Capacidad | Como funciona |
|-----------|---------------|
| Compactacion de contexto | `check_context` + `compact_memory` antes de cada razonamiento. Reduce 99%+ de tokens sin perder informacion clave. |
| Journal diario | `summary_memory` escribe `memory/YYYY-MM-DD.md` al cerrar sesion (async). |
| Long-term memory | `MEMORY.md` acumula preferencias, patrones recurrentes, decisiones arquitectonicas. |
| Busqueda semantica | `memory_search` busca en el historial con hibrido vector+BM25. Util para recall de decisiones pasadas. |
| Compactacion de tool outputs | `compact_tool_result` evita que outputs largos saturen el contexto. |

---

## Integracion con X-DD

ReMe se integra via hooks event-driven (sistema de hooks X-DD, Sprint 7):

- **`session:start:reme-load`** (SessionStart, perfil minimal+): carga MEMORY.md + journal del dia anterior en el contexto inicial del agente.
- **`stop:reme-summary`** (Stop, perfil minimal+): llama `summary_memory` async al cerrar sesion, escribe journal del dia.

Ambos hooks son no-bloqueantes: si ReMe no esta instalado o `XDD_REME` no esta seteado, los hooks son no-op.

---

## Configuracion avanzada

Variables opcionales de X-DD para ReMe:

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `XDD_REME` | `0` | Activa ReMe (`1` para activar) |
| `XDD_REME_COMPACT_THRESHOLD` | `90000` | Tokens para disparar compactacion |
| `XDD_REME_COMPACT_RESERVE` | `10000` | Tokens a reservar de mensajes recientes |
| `XDD_REME_LANGUAGE` | `""` | Idioma del journal (ej: `es` para español, vacio = auto) |
| `XDD_REME_VECTOR` | `0` | Activa embeddings vectoriales (`1` requiere EMBEDDING_API_KEY) |
| `XDD_REME_FTS` | `1` | Full-text search BM25 (activo por defecto, sin costo) |

---

## Relacion con el modo operativo X-DD

| Modo | MemPalace | ReMe | Descripcion |
|------|-----------|------|-------------|
| Base | No | No | Pipeline funcional, sin continuidad automatica |
| Completo | Si | No | Codebase RAG activo |
| Completo + ReMe | Si | Si | Codebase RAG + memoria conversacional persistente |
| Solo ReMe | No | Si | Memoria conversacional sin indexacion de repo |

`xdd-doctor --json` reporta `reme_mode: "active" | "inactive"`.
`xdd-start` imprime el modo ReMe al arrancar si `XDD_REME=1`.
