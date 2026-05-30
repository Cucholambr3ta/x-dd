# ADR-0045: Comando de terminal `xdd` unificado vía pipx

**Estado:** Aceptada
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

ADR-0043 dejó X-DD pip-installable con entry-points por script (`xdd-gate`, `xdd-flow`…).
Falta un **único comando de terminal** que dé acceso a todo el tooling sin recordar N
binarios ni invocar scripts por ruta absoluta.

Hay que distinguir dos planos que se confundían:
- **Slash command `/xdd`** (Sprint 29 / ADR-0039): registrado en los IDEs por
  `xdd-global-install.sh`. Vive DENTRO del IDE (orquestador conversacional).
- **Comando de terminal `xdd`**: binario en PATH para correr el tooling (gate, flow,
  doctor, init…) desde cualquier shell. **No existía.**

## Decisión

**Exponer un entry-point `xdd` que es un dispatcher de subcomandos** sobre los scripts
existentes, instalable con `pipx install x-dd`.

- `xdd_cli.main()` mapea `xdd <sub>` → script (`gate/eval/flow/provider/shield/
  orchestrate` vía runpy; `doctor/init/start/adapt/global-install` vía bash). NO reescribe.
- `[project.scripts]` añade `xdd = "xdd_cli:main"` junto a los entry-points por script.
- `xdd-global-install.sh` documenta (no fuerza) `pipx install x-dd` como vía de terminal,
  manteniéndose enfocado en registrar el slash command en IDEs.

pipx (no pip global) es la recomendación: aísla el binario en su propio venv y lo deja en
PATH, sin contaminar el entorno del usuario.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Solo entry-points por script (ADR-0043) | Simple | El usuario recuerda N binarios | Insuficiente como UX de terminal |
| `xdd` dispatcher (elegida) | Un solo comando; descubrible (`xdd --help`) | Doble vía (también `xdd-gate`) | — |
| Reescribir a Click con grupos | UX idiomática | Reintroduce el costo que ADR-0043 evitó | Contradice ADR-0008/0043 |

## Consecuencias

- **Positivas:** `pipx install x-dd` + `xdd doctor`/`xdd gate status`/`xdd flow` desde
  cualquier shell. Subcomandos descubribles. Slash command IDE y comando terminal quedan
  como planos separados y claros.
- **Trade-offs:** dos formas de invocar lo mismo (`xdd gate` y `xdd-gate`); aceptable.
- **Neutras:** el orquestador conversacional sigue siendo el slash command del IDE; `xdd`
  de terminal NO lo reemplaza, da acceso al tooling.

## Relación

- **Construye sobre:** ADR-0043 (pip-installable), ADR-0035 (global install), ADR-0039
  (orquestador global / slash command).
- **Habilita:** distribución PyPI (ADR-0047) hace `pipx install x-dd` funcionar sin clon.
