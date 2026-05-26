# CHANGELOG técnico — X-DD

> Historia técnica del repositorio. Mantenida por `/xdd-trace` (cierre de sprint) y `/release-cut` (release).
> Formato basado en [Keep a Changelog](https://keepachangelog.com).
>
> Para release notes user-facing ver [RELEASES/](../RELEASES/) (a partir de v0.1.0).

---

## [Unreleased] — main

### Added — Sprint 0 (2026-05-26)
- **Dogfooding inicial** — directorio `.xdd/briefing/` con `SPEC.md` y `FEATURES.md`
  del propio X-DD como producto.
- **10 ADRs** (`docs/adr/0000` a `0009`) cerrando las preguntas abiertas del
  plan MEJORAS-X-DD v1.1: mapeo a fases, dogfooding visible, profile vs
  config, Python como runtime, MemPalace externa, MCP server propio, gate
  HMAC, alcance de adapters, CLI diferido, política de `.xdd/`.
- **`docs/adr/README.md`** — índice cronológico de ADRs.
- **`PROJ-MASTER-PLAN.md`** — Gantt Mermaid de los 8 sprints + grafo de dependencias.
- **`docs/CHANGELOG.md`** — este archivo.
- **Anexo v1.2 de `MEJORAS-X-DD.md`** — consolida las decisiones meta y enlaza ADRs.

### Changed — Sprint 0
- **`memoria.md`** — actualizada con sección "Estado Actual" del Sprint 0 y log
  de las 10 decisiones arquitectónicas.

---

## Convenciones

- Cada sección de sprint usa subcategorías: `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed`, `Security`.
- Cada bullet enlaza al archivo o sección que cambió.
- Commits asociados siguen formato convencional: `feat(N.N): ...`, `fix(N.N): ...`,
  `docs(adr): NNNN ...`.
- `/release-cut` consolida `[Unreleased]` a `[v0.1.0] — YYYY-MM-DD`.
