# ADR-0033 — GitNexus como companion tier-1 (paralelo MemPalace)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** Pre-release v0.1.0 add-on

## Context

X-DD tiene 3 capas memory/context hasta ahora:
1. **MemPalace** (MIT, tier-1 recommended) — memoria semántica del agent (sesiones, decisiones, traces)
2. **xdd-fs-context** (X-DD Sprint 19) — filesystem-paradigm context curation baseline
3. **MCP server propio** (Sprint 6) — exposición gates/workflows/agents

**Gap real identificado** (research deep dive 2026-05-27):
X-DD asume orquestador IDE entiende el código. Pero "AI edita `UserService.validate()` ignorando 47 funciones que dependen de su return type → breaking changes ship". X-DD no resuelve esto.

**GitNexus** (abhigyanpatwari/GitNexus, 40.5k ⭐, TypeScript) llena exactamente ese hueco:
- Knowledge graph del codebase via Tree-sitter AST + LadybugDB
- 14 lenguajes (TS/Py/Java/Kotlin/Go/Rust/C#/PHP/Ruby/Swift/Dart/C/C++)
- 16 MCP tools: hybrid search (BM25 + semantic + RRF), impact analysis con confidence, Cypher queries, multi-file rename coordination
- Leiden clustering, execution flow tracing
- Hooks Claude Code PreToolUse/PostToolUse nativos

**Caveat license:** PolyForm Noncommercial 1.0.0. Uso personal/research/educational/non-profit gratis. Comercial = paid license (akonlabs.com).

## Decision

GitNexus se integra como **companion tier-1 paralelo a MemPalace** en v0.1.0:

1. **`scripts/xdd-doctor.sh`** → detect `gitnexus` CLI en sección "Núcleo recomendado" (paralelo a `mempalace`)
2. **`scripts/xdd-start.sh`** → bloque idéntico a MemPalace: si `gitnexus` instalado, indexa el proyecto en background; sin él, warning + continúa
3. **`DEPENDENCIES.md`** → entrada GitNexus en "Núcleo recomendado" + disclaimer license (estilo Shannon ADR-0010)
4. **`xdd.profile.yml`** capability nueva `code_intelligence: true` (default)
5. **`docs/MCP_INTEGRATION.md`** → tercera opción MCP (xdd-mcp-server + MemPalace + GitNexus)
6. **NO bundle**: X-DD repo no incluye binarios GitNexus. Decisión install/license del user

## Alternatives considered

- **Diferir a v0.2.0 con skill wrapper xdd-code-intel:** rechazado — user pidió integración tier-1 ahora paralelo MemPalace
- **Recomendar como "external opt-in" estilo Shannon AGPL:** rechazado — Shannon AGPL bloquea para SaaS comercial (más restrictivo), GitNexus PolyForm permite uso research/personal sin restricción. Justifica tier-1
- **Sustituir xdd-fs-context (Sprint 19):** rechazado — xdd-fs-context = baseline portable zero-dep (sigue siendo default); GitNexus = upgrade opt-in
- **Solo recomendar en docs sin activación automática:** rechazado — user pidió "que se active igual que MemPalace"

## Consequences

### Positivas
- ✅ Cierra gap real "AI ignora blast radius" (problema documentado en research)
- ✅ MCP nativo → consumible sin adapter X-DD-específico
- ✅ Compat con orquestadores existentes (Claude Code, Cursor, etc.) — GitNexus expone su propio MCP server
- ✅ `/analisis-impacto` workflow existente (X-DD) puede invocar GitNexus pre-condition para grafo de deps preciso
- ✅ Patrón consistente con MemPalace (mismo flujo doctor + start + DEPENDENCIES)
- ✅ Stack divergente (TS) no afecta X-DD (interop sólo vía MCP, no comparte libs)

### Negativas
- ⚠️ License PolyForm Noncomm requiere disclaimer + decision consciente del user comercial
- ⚠️ Dep adicional para mantener (Node + npm requeridos)
- ⚠️ Index inicial puede tomar segundos-minutos en codebases grandes (warning en log)
- ⚠️ Overlap parcial con xdd-fs-context (Sprint 19) — política: GitNexus = upgrade; xdd-fs-context = baseline zero-dep

## License analysis (PolyForm Noncommercial 1.0.0)

| Caso de uso | ¿Gratis? |
|---|---|
| Uso personal | ✅ Sí |
| Research / academic | ✅ Sí |
| Educational | ✅ Sí |
| Non-profit | ✅ Sí |
| Open source contributions | ✅ Sí |
| Commercial SaaS / product | ❌ Requiere paid license |
| Consultoría con cliente | ❌ Requiere paid license |
| Internal corporate tools | ❌ Requiere paid license |

X-DD MIT NO se contamina por **consumir** GitNexus MCP server. PolyForm Noncomm restringe **modificación + redistribución comercial**, no consumo client-side. Análogo a usar Slack en un proyecto MIT — no contamina.

Disclaimer en `DEPENDENCIES.md` + `INSTALL.md` informa al user comercial antes de adoptar.

## Implementation v0.1.0

```bash
# Verificar GitNexus instalado (junto a MemPalace)
bash scripts/xdd-doctor.sh
# → check "gitnexus" gitnexus no ""

# Arrancar X-DD (indexa MemPalace + GitNexus automáticamente)
bash scripts/xdd-start.sh
# → "[X-DD] Inicializando MemPalace..."
# → "[X-DD] Inicializando GitNexus..."

# Instalar GitNexus (opt-in)
npm i -g gitnexus
# o
npx gitnexus

# xdd.profile.yml — capability default true
capabilities:
  code_intelligence: true   # GitNexus MCP — impact analysis (opt-in, PolyForm Noncomm)
```

## Related

- ADR-0004 MemPalace dep externa no fork (mismo pattern aplicado a GitNexus)
- ADR-0005 MCP integration preferida
- ADR-0010 Shannon AGPL external opt-in (pattern license disclaimer)
- ADR-0024 Compaction skill provider-agnostic (xdd-fs-context complementa GitNexus)
- Workflow `/analisis-impacto` (X-DD) ← futura integración GitNexus impact analysis tool

## References

- GitNexus repo: https://github.com/abhigyanpatwari/GitNexus (40.5k⭐, PolyForm Noncomm)
- Akon Labs (commercial license): https://akonlabs.com
- PolyForm spec: https://polyformproject.org/licenses/noncommercial/1.0.0/
- Tree-sitter: https://tree-sitter.github.io
- LadybugDB: native + WASM graph DB
