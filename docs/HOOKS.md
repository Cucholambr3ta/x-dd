# Hooks — referencia X-DD

Hooks event-driven inspirados en ECC. Sprint 7 introduce un catálogo
inicial de 8 hooks bash cross-platform. Definidos en
[`.agent/hooks/hooks.json`](../.agent/hooks/hooks.json),
documentados en [`.agent/hooks/README.md`](../.agent/hooks/README.md).

> Para los detalles de cada hook + cómo crear hooks propios, leé
> [`.agent/hooks/README.md`](../.agent/hooks/README.md). Esta página
> resume las decisiones de arquitectura y diferencias vs ECC.

## Filosofía

Tres categorías de uso:
1. **Seguridad** — bloquear comandos peligrosos (`pre:bash:dangerous-command`),
   proteger configs de relajaciones silenciosas (`pre:edit:config-protection`).
2. **Higiene** — advertir sobre `.md` fuera de paths canónicos
   (`pre:write:doc-file-warning`), avisar de cambios sin commitear (`stop:git-check`).
3. **Continuidad** — re-indexar MemPalace (`post:edit:mempalace-index`),
   cargar contexto al iniciar (`session-start:context-load`),
   loguear PRs (`post:bash:pr-logger`), extraer instincts (`stop:pattern-extraction`, Sprint 9).

## Materialización: del SSoT a la ejecución (v0.1.1+)

`hooks.json` es la **fuente única (SSoT)**, pero Claude Code no lo lee: lee
`settings.json`. Hasta v0.1.1 faltaba el paso que traduce uno a otro, por lo que
los hooks estaban **definidos pero nunca se ejecutaban** (p.ej. `mempalace mine`
no se disparaba en Edit/Write). El flujo correcto:

```
.agent/hooks/hooks.json  (SSoT, 15 hooks)
        │
        │  scripts/xdd-hooks-install.py  (xdd hooks install)
        ▼
~/.claude/settings.json  ← sólo eventos Claude Code: Pre/PostToolUse, SessionStart, Stop
        │                   (los eventos runtime X-DD —before_model, wrap_tool_call…— se omiten)
        ▼
Claude Code dispara los hooks  →  Edit/Write → mempalace mine (async)
```

- **`xdd hooks install`** materializa el perfil activo (`XDD_HOOK_PROFILE`, default
  `standard`) en `~/.claude/settings.json`. Merge **no destructivo**: preserva hooks
  ajenos (p.ej. caveman) y marca los propios con `_xdd_id` para re-sincronizar
  (`xdd hooks sync`) sin duplicar. `xdd hooks status` lista los que faltan.
- **Destino global** → cada `command` lleva guarda `[ -f "$PWD/.agent/hooks/scripts/… ]`
  para ser **no-op fuera de un repo X-DD**.
- **git post-commit** (`scripts/hooks/post-commit`, vía `core.hooksPath`) re-indexa
  **MemPalace + GitNexus** tras cada commit. `xdd-init`/`xdd-start` lo instalan.
- **Lock MemPalace**: el palace es único global; los hooks usan `flock -n`
  (skip-if-running) para no colisionar con mines concurrentes de otros repos.
- `xdd-doctor` reporta si el post-commit está activo y si los hooks están materializados.

## Diferencias clave vs ECC

| Aspecto | ECC | X-DD v0.1.0 |
|---|---|---|
| Lenguaje | Node.js | Bash puro |
| Plugin discovery | `CLAUDE_PLUGIN_ROOT` lookup loops largos | Path relativo simple |
| Profiles | minimal / standard / strict | minimal / standard / strict (igual) |
| Hot disable | env `ECC_DISABLED_HOOKS` | env `XDD_DISABLED_HOOKS` (igual patrón) |
| Distribución | npm + plugin marketplace | gitignore + symlink desde adapter (Sprint 7.1) |
| Catálogo inicial | 15+ hooks | 8 hooks (subset cuidadoso) |

X-DD prioriza Bash sobre Node para:
- No agregar Node como dep obligatoria (ya es opcional en `DEPENDENCIES.md`).
- Cross-platform via `XDD_INSTALL.ps1` (Sprint 7.4) wrappea los hooks con `bash` (WSL/Git Bash).
- Threat model T6.2/V2 — más fácil auditar 100 líneas bash que un dispatcher Node.

## Roadmap (post-v0.1.0)

- **v0.1.1** — ✅ materializador `xdd hooks` (hooks.json → settings.json) + post-commit
  GitNexus + flock MemPalace. Cierra el gap "definido ≠ ejecutándose".
- **Sprint 9** — `stop:pattern-extraction` deja de ser stub y escribe instincts a SQLite.
- **Sprint 12** — `pre:bash:agent-shield` integrado: análisis estático de comandos.
- **v0.2.0** — hot reload de hooks tras edit del JSON (sin reiniciar sesión).

## Ver también

- [`.agent/hooks/README.md`](../.agent/hooks/README.md) — catálogo + recetas
- [`schemas/hooks.schema.json`](../schemas/hooks.schema.json) — validación
- [`.xdd/spec/THREATS.md`](../.xdd/spec/THREATS.md) — amenazas que mitigan los hooks
