# docs/dev — Material de desarrollo interno

> ⚠️ **No es parte del producto liberado.** Este directorio contiene guías de
> **desarrollo del propio framework X-DD** — cómo se crean agentes, skills y workflows
> para cada IDE soportado. Son referencia para contribuir a X-DD, no documentación de
> usuario final.

## Contenido

Guías por IDE (`GUIA_<IDE>_AGENTES_SKILLS_WORKFLOWS.md`) — cómo crear/estructurar
agentes, skills y workflows en cada entorno:

- `GUIA_CLAUDE_CODE_…`
- `GUIA_OPENCODE_…`
- `GUIA_CURSOR_…`
- `GUIA_WINDSURF_…`
- `GUIA_VSCODE_…`
- `GUIA_ANTIGRAVITY_…`
- `GUIA_CODEX_…`

## Por qué viven aquí

Comparten ~80% de estructura (son casi idénticas salvo detalles por IDE). Se reubicaron
desde `docs/` para separar **documentación de usuario** (en `docs/`) de **material de
desarrollo** (aquí). La consolidación de las 7 guías en una plantilla + SSoT queda como
mejora futura (v0.2.0).

Para documentación de usuario, ver [docs/](../) y el [README](../../README.md) del repo.
