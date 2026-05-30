# ADR-0046: Módulo Python de adapters IDE (SSoT) — aditivo, no reemplaza xdd-adapt.sh

**Estado:** Aceptada
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

La generación de config IDE vive en `scripts/xdd-adapt.sh` (712 líneas, 29 tests bats):
copia comandos, MCP config, branding, symlinks DRY, 7 layouts. El piloto agentix demostró
un patrón más limpio: un **SSoT en código** (`adapters.py`, ~78 líneas) que emite a los 7
targets con layouts declarativos y copia real.

La tentación era reescribir `xdd-adapt.sh` a wrapper fino sobre un módulo Python. Pero esa
cirugía arriesga: (a) romper 29 tests bats, (b) regresión en branding/MCP/symlinks, (c)
perder el fix de CLAUDE.md heredoc branded aplicado recientemente. Alto riesgo justo antes
de un release.

## Decisión

**Portar el patrón SSoT como módulo Python NUEVO y ADITIVO (`scripts/xdd_adapters.py`),
sin tocar `xdd-adapt.sh`.**

- `xdd_adapters.py`: `Workflow` (SSoT), `_LAYOUT` (7 targets), `emit`/`emit_all` (copia
  real, nunca symlink, sin MCP), `load_ssot_from_dir`/`parse_workflow` (lee workflows
  markdown con frontmatter). CLI `emit`/`emit-all` + `--self-test`.
- `xdd-adapt.sh` permanece como el camino probado y por defecto.
- El módulo queda empaquetado en el paquete pip (ADR-0043) como base para la consolidación
  futura.

La consolidación real (xdd-adapt.sh → wrapper sobre el módulo) se difiere a v0.2.0, cuando
se pueda hacer con tiempo de pruebas y migración de los 29 bats.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Reescribir shell → wrapper fino | Una sola fuente | Riesgo de romper 29 bats + branding/MCP + fix heredoc reciente | Demasiado riesgo pre-release |
| Módulo aditivo (elegida) | Cero regresión; base empaquetable | Dos rutas temporales (shell + módulo) | — |
| No portar | Cero trabajo | Pierde el patrón consolidado demostrado | Desaprovecha el aprendizaje de agentix |

## Consecuencias

- **Positivas:** patrón SSoT disponible en Python, testeado (15 tests), empaquetado. Sin
  riesgo para el release. Base lista para consolidar en v0.2.0.
- **Trade-offs:** coexisten `xdd-adapt.sh` (producción) y `xdd_adapters.py` (módulo nuevo)
  hasta la consolidación.
- **Neutras:** el módulo no se invoca aún desde el flujo de init; es tooling/base.

## Relación

- **Reusa el patrón de:** agentix `adapters.py`.
- **Construye sobre:** ADR-0007 (adapters iniciales), ADR-0034 (universal IDE adapter),
  ADR-0043 (empaquetado pip).
- **Difiere a v0.2.0:** consolidación de `xdd-adapt.sh` sobre este módulo.
