# PLAN — X-DD v0.1.0 (Fase 3-Plan)

> Plan formalizado en el repo. Espejo ejecutable del archivo en
> `.claude/plans/indicame-que-mejoras-implementarias-happy-sunbeam.md`
> y del anexo v1.2 de [MEJORAS-X-DD.md](../../MEJORAS-X-DD.md).
> Versión 1.0 — Generado al cerrar Sprint 2.

## Estrategia

Una pasada completa por las 6 fases X-DD ([ADR-0000](../../docs/adr/0000-mapeo-mejoras-pipeline-xdd.md)),
ejecutada en 8 sprints. Dogfooding visible ([ADR-0001](../../docs/adr/0001-dogfooding-visible-commiteable.md)).

## Sprints

| # | Sprint | Fase | Branch | Estado | Tareas MEJORAS | PR |
|---|--------|------|--------|--------|----------------|-----|
| 0 | Reconciliación | F1 Briefing | feat/sprint-0-reconciliation | ✅ | meta (ADRs 0000-0009) | [#1](https://github.com/Cucholambr3ta/x-dd/pull/1) |
| 1 | MemPalace externo + Quickstart | F2 Spec | feat/sprint-1-mempalace-quickstart | ✅ | 1.1, 7.1, 12.2, 12.4 | [#2](https://github.com/Cucholambr3ta/x-dd/pull/2) |
| 2 | CI base + plan formal | F3 Plan | feat/sprint-2-ci-base | 🔄 | 5.1 (parcial), 12.3 | _en curso_ |
| 3 | xdd-doctor v2 + xdd.config.yml | F4 Build 1/5 | feat/sprint-3-doctor-config | ⏳ | 1.2, 1.3 | — |
| 4 | Gate keeper HMAC ⭐ | F4 Build 2/5 | feat/sprint-4-gate-hmac | ⏳ | 2.1, 2.2, 2.3 + ADR-0006 | — |
| 5 | Registry tipado de agentes | F4 Build 3/5 | feat/sprint-5-registry | ⏳ | 3.1, 3.2 | — |
| 6 | MCP server propio ⭐ | F4 Build 4/5 | feat/sprint-6-mcp-server | ⏳ | ADR-0005 (sobre-mejora) | — |
| 7 | Adapters IDE + tests E2E | F4-5 | feat/sprint-7-adapters-tests | ⏳ | 1.4, 4.1-4.4 | — |
| 8 | Gobernanza OSS + release v0.1.0 | F6 Retro | feat/sprint-8-governance-release | ⏳ | 8.1, 9.1 | — |

## Reglas duras (vigentes desde Sprint 0)

1. **Branch por sprint:** `feat/sprint-N-<slug>`.
2. **Commits convencionales con tarea MEJORAS** (`feat(N.N): ...`) o **categoría** (`docs(adr): ...`, `chore(trace): ...`).
3. **ADR antes de implementar** decisiones arquitectónicas.
4. **`lecciones.md` durante el sprint**, no al final.
5. **`/cierre-fase` + `/xdd-trace`** obligatorios antes del merge.
6. **Squash merge** del PR a `main` (configurado en repo).
7. **CI verde obligatorio** (a partir de Sprint 2).
8. **Sin skip de tests/lints** — investigar root cause.

## Artefactos por fase

| Fase | Path | Producido por |
|------|------|---------------|
| F1 Briefing | `.xdd/briefing/SPEC.md` + `FEATURES.md` | Sprint 0 |
| F2 Spec | `.xdd/spec/DOMAIN.md` + `THREATS.md` | Sprint 1 |
| F3 Plan | `.xdd/plan/PLAN.md` (este archivo) | Sprint 2 |
| F4 Build | `.xdd/build/sprint-N/REPORT.md` | Sprints 3-7 |
| F5 QA | `.xdd/qa/QA_REPORT.md` | Sprint 7-8 |
| F6 Retro | `.xdd/retro/lecciones.md` + tag v0.1.0 | Sprint 8 |

## Verificación al cerrar el plan (post-Sprint 8)

```bash
# Salud del entorno
make doctor

# Linters y CI local
make lint
pre-commit run --all-files

# Tests del propio framework (Sprint 3+)
bats tests/
pytest tests/
bash tests/e2e/test_quickstart.bats

# Estado del pipeline X-DD aplicado a X-DD (Sprint 4+)
for phase in briefing spec plan build qa retro; do
  python3 scripts/xdd-gate.py validate --phase $phase
done

# MCP server responde (Sprint 6+)
python3 -m xdd_mcp_server --check

# Release v0.1.0 publicado (Sprint 8)
git tag --verify v0.1.0
test -f RELEASES/v0.1.0.md
```

## Aprobación

- **Estado:** Aceptado — al cerrar Sprint 2.
- **Aprobador:** Alejandro Placencia.
- **Próximo gate:** transición a Fase 4-Build (Sprint 3).
