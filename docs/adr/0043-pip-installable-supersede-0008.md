# ADR-0043: SDK pip-installable con entry-points sobre scripts existentes — supersede ADR-0008

**Estado:** Aceptada
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

ADR-0008 difirió la consolidación CLI a post-v0.1.0, con criterio de reapertura:
"si aparece demanda real de `pip install`". Esa señal llegó por una vía distinta a la
esperada: el piloto **agentix** (réplica de X-DD construida como SDK Python puro)
**demostró que el núcleo de X-DD cabe en un paquete `pip install -e .` instalable** sin
reescribir la lógica, y que hacerlo desbloquea distribución (PyPI) y un comando estable.

El temor central de ADR-0008 era el costo de **reescribir todo en Click/Typer**. Ese
costo se evita: no reescribimos los scripts.

## Decisión

**Empaquetar X-DD como paquete pip (`x-dd`) con entry-points que son dispatchers finos
sobre los scripts existentes.** NO se reescribe ningún script a Click/Typer.

- `pyproject.toml` (hatchling) en la raíz. Stdlib-first (`dependencies = []`), extras
  opcionales `[anthropic]` y `[dev]`.
- Paquete `src/xdd_cli/` con funciones dispatcher (`gate`, `eval_`, `flow`, `provider`,
  `shield`, `orchestrate`) que ejecutan `scripts/xdd-*.py` vía `runpy`, preservando argv.
- `[project.scripts]` expone `xdd-gate`, `xdd-eval`, `xdd-flow`, `xdd-provider`,
  `xdd-shield`, `xdd-orchestrate`.
- Los scripts se empaquetan como data del wheel (`force-include`); resolución en
  instalación editable (repo `scripts/`) o wheel (`xdd_cli/scripts/`), override con
  `XDD_SCRIPTS_DIR`.

Esto **supersede ADR-0008**: la consolidación ya no está diferida; se resuelve por
empaquetado, no por reescritura.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Reescribir a Click/Typer (lo que 0008 temía) | UX unificada `xdd gate ...` | ~2 días, riesgo de regresión en lógica probada | Costo que 0008 ya rechazó |
| Dispatcher fino + entry-points (elegida) | Cero reescritura; pip install; scripts intactos | Doble nombre (`xdd-gate` script y entry-point) | — |
| Seguir solo con Makefile | Cero esfuerzo | No instalable; no distribuible en PyPI | No cubre la demanda demostrada |

## Consecuencias

- **Positivas:** `pip install -e .` + `xdd-gate --help` funciona; base para PyPI (ADR-0047)
  y comando global `xdd` vía pipx (ADR-0045). Scripts existentes y sus tests intactos.
- **Trade-offs:** un dispatcher extra por script; el wheel duplica scripts como data.
- **Neutras:** la UX `xdd <subcomando>` unificada (un solo binario) queda como mejora
  futura opcional sobre esta base, no como prerequisito.

## Relación

- **Supersede:** ADR-0008.
- **Habilita:** ADR-0045 (comando global pipx), ADR-0047 (publish PyPI).
- **Reusa:** ADR-0003 (stdlib-first runtime).
