# ADR-0008: Consolidación en `xdd` CLI (Python + Click/Typer) — diferida a post-v0.1.0

- **Fecha:** 2026-05-26
- **Estado:** Reemplazado por [ADR-0043](0043-pip-installable-supersede-0008.md) (2026-05-30)
- **Decidido por:** Alejandro Placencia, Claude

> ⚠️ **SUPERSEDED:** la consolidación dejó de estar diferida. ADR-0043 resuelve el
> `pip install` por **empaquetado con entry-points sobre los scripts existentes**
> (sin reescritura a Click/Typer), evitando el costo que motivó este diferimiento.

## Contexto

Tras los sprints 3-8, X-DD tendrá ~6-8 scripts dispersos:
- `xdd-doctor.sh`
- `xdd-init.sh`
- `xdd-start.sh`
- `xdd-adapt.sh`
- `xdd-gate.py`
- `xdd-metrics.sh` (futuro)
- `lint-workflows.sh`
- `validate-registry.py`
- `generate-equipo.sh`
- `migrate-agents-to-registry.py`

Consolidarlos en un único `xdd` CLI Python (Click/Typer) ofrecería: instalación PyPI (`pip install xdd-cli`), UX uniforme (`xdd doctor`, `xdd init`, `xdd gate validate`), `--help` consistente, mejor testabilidad, mejor empaquetado.

## Decisión

**Diferir la consolidación a post-v0.1.0** (probablemente v0.2.0). Los Sprints 3-7 mantienen N scripts shell + Python sueltos.

Razones:
1. Reescribir todo en Click/Typer agrega ~2 días de trabajo al plan actual (17.5 días → ~20).
2. La UX shell actual es funcional (`bash scripts/xdd-doctor.sh`).
3. Empaquetar como `xdd-cli` requiere decisiones de naming PyPI, registro, semver coordinado con la versión del framework.
4. La oportunidad real aparece cuando hay usuarios externos pidiendo `pip install` — eso es señal de demanda.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Consolidar ahora en Sprint 0 | Coherencia desde el día 1 | Bloquea sprints 3-7; reescribe el plan completo | Riesgo alto para v0.1.0 |
| Consolidar al final, en Sprint 8 | Sin bloqueos | Sprint 8 ya está cargado con gobernanza OSS y release | No cabe |
| Nunca consolidar (vivir con N scripts) | Cero esfuerzo extra | UX inconsistente; difícil documentar `--help` global | Aceptable solo si X-DD se mantiene "infrastructure-as-text" |

## Consecuencias

- **Positivas:** v0.1.0 se entrega en tiempo; el experimento prueba si la demanda de `pip install` existe.
- **Negativas / Trade-offs:** N scripts con UX heterogénea durante v0.1.x. Mitigación: `Makefile` (`make doctor|start|gate|adapt`) unifica la invocación.
- **Neutras:** este ADR se reabre en la retro de v0.1.0 con datos reales de uso.

## Plan de revisión

Revisitar en retro v0.1.0 (Sprint 8) con criterio: si ≥3 issues/PRs externos piden CLI unificado, promover a P0 de v0.2.0.
