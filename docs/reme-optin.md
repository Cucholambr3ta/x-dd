# Sistema de Memoria Conversacional — X-DD

Sistema nativo de gestion de memoria conversacional persistente para agentes X-DD.
Implementado en `scripts/xdd-memory.py` — stdlib Python, sin dependencias externas.

Arquitectura inspirada en ReMe (agentscope-ai/ReMe, Apache-2.0) pero completamente nativa:
misma estructura de archivos, mismos prompts de compactacion/summarizacion, sin pip install.

Activar con `XDD_MEMORY=1`.

---

## Estructura de archivos

```
<proyecto>/
├── MEMORY.md                   # long-term: hechos, preferencias, decisiones clave (versionable)
├── memory/
│   └── YYYY-MM-DD.md           # journal diario: resumen estructurado por sesion (versionable)
├── dialog/
│   └── YYYY-MM-DD.jsonl        # dialogo raw antes de compactacion (gitignored)
└── tool_result/
    └── <uuid>.txt              # cache de outputs largos de herramientas, TTL 3 dias (gitignored)
```

Agregar al `.gitignore` del proyecto:
```
dialog/
tool_result/
```

---

## Diferencia con MemPalace

| Aspecto | MemPalace | Memoria conversacional (este sistema) |
|---------|-----------|---------------------------------------|
| Que indexa | Archivos del repo (codigo, docs) | Conversaciones del agente (dialogo, decisiones) |
| Busqueda | RAG sobre codebase | BM25 sobre historial conversacional |
| Persistencia | Indice semantico del repo | MEMORY.md + journal diario |
| Cuando usar | Continuidad sobre el proyecto | Memoria del agente entre sesiones |

Usar ambos en conjunto: MemPalace para "que hay en el repo", este sistema para "que hemos decidido y aprendido".

---

## Capacidades

| Capacidad | Comando | Descripcion |
|-----------|---------|-------------|
| Carga de sesion | `xdd-memory load` | Carga MEMORY.md + journal del dia anterior (hook SessionStart) |
| Journal diario | `xdd-memory summarize` | Escribe/actualiza memory/YYYY-MM-DD.md (hook Stop) |
| Compactacion | `xdd-memory compact --messages FILE` | Reduce historial largo a summary estructurado |
| Busqueda | `xdd-memory search QUERY` | BM25 sobre MEMORY.md + journals |
| GC | `xdd-memory gc [--days N]` | Purga tool_result/ con TTL vencido |
| Stats | `xdd-memory stats` | Estado del sistema |

---

## Activacion

```bash
export XDD_MEMORY=1
bash scripts/xdd-start.sh
```

Para summarizacion real (vs mock sin red):

```bash
export XDD_MEMORY=1
export XDD_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-...
bash scripts/xdd-start.sh
```

Sin `ANTHROPIC_API_KEY`, el sistema funciona en modo mock: crea el journal con una nota
stub. Los hooks, la estructura de archivos, la busqueda BM25 y el GC funcionan siempre.

---

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `XDD_MEMORY` | `0` | Activa el sistema (`1` para activar) |
| `XDD_PROVIDER` | `mock` | Provider LLM para summarizacion (`mock` o `anthropic`) |
| `XDD_MEMORY_COMPACT_THRESHOLD` | `90000` | Tokens para disparar compactacion |
| `XDD_MEMORY_COMPACT_RESERVE` | `10000` | Tokens a reservar de mensajes recientes |
| `XDD_MEMORY_LANGUAGE` | `""` | Idioma del journal (ej: `es`, vacio = auto) |
| `XDD_MEMORY_TOOL_TTL_DAYS` | `3` | TTL de archivos tool_result/ en dias |

---

## Modo operativo

| Modo | MemPalace | Memoria conv. | Descripcion |
|------|-----------|--------------|-------------|
| Base | No | No | Pipeline funcional, memoria manual |
| Completo | Si | No | Codebase RAG activo |
| Completo + Memoria | Si | Si | Codebase RAG + memoria conversacional |
| Solo Memoria | No | Si | Memoria conversacional sin indexacion de repo |

`xdd-doctor` reporta `memory_mode: "active" | "inactive"`.
`xdd-start` imprime el modo al arrancar si `XDD_MEMORY=1`.

---

## Formato del journal (memory/YYYY-MM-DD.md)

Cada sesion escribe una seccion con este formato:

```markdown
# Journal YYYY-MM-DD

## Sesion YYYY-MM-DDTHH:MM:SS

## Factual Memory
[Hechos objetivos, estados del proyecto, eventos importantes]

## Reflections & Logic
[Estrategias reutilizables, errores a evitar, insights para futuras sesiones]
```

Si hay multiples sesiones en el mismo dia, cada una se añade como seccion nueva.

---

## Formato de compactacion (summary estructurado)

El comando `compact` produce un summary con este formato (compatible con el formato
de contexto de X-DD, reutilizable como system prompt de la siguiente sesion):

```markdown
## Goal
[Que estaba haciendo el usuario]

## Progress
### Done
- [x] [Tarea completada]
### In Progress
- [ ] [Trabajo actual]

## Key Decisions
- **[Decision]**: [Razon]

## Next Steps
1. [Siguiente paso]

## Critical Context
- [Datos o referencias necesarias para continuar]
```

---

## Integracion con hooks

Los hooks se registran automaticamente con el modulo `continuous-memory`:

- **`session:start:reme-load`** (SessionStart): llama `xdd-memory load` — no-op si `XDD_MEMORY != 1`.
- **`stop:reme-summary`** (Stop): llama `xdd-memory summarize` + `xdd-memory gc` en background — no-op si `XDD_MEMORY != 1`.

Ambos hooks son seguros: si `xdd-memory.py` no existe o `XDD_MEMORY` no esta seteado, exit 0 silencioso.
