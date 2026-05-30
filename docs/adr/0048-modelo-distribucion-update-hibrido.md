# ADR-0048: Modelo de distribución y actualización — híbrido (pip + xdd update)

**Estado:** Propuesto (objetivo v0.2.0)
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

> Numeración: asume que ADR-0043–0047 (branches de la cadena pip/MCP del Sprint 33) ya
> están en `develop`. Si se fusiona antes, renumerar.

---

## Contexto

Hoy `xdd-init.sh` **copia físicamente** el framework al proyecto del usuario
(`copy_if_absent` → `cp -r`, sin sobrescribir). El resultado es una **foto congelada**: una
vez inicializado un proyecto, las mejoras del framework (p. ej. los fixes de gate del Sprint
32/33) **no llegan**. Un re-init hace SKIP de lo existente, así que tampoco actualiza.

Tres canales hoy, con realidades de update muy distintas:

| Canal | Update hoy |
|-------|-----------|
| Repo X-DD (contribuidores) | `git pull` ✅ |
| `xdd-init` copia a proyecto | **nada** ❌ (congelado) |
| `xdd-global-install` (slash command) | re-correr el script ⚠️ manual |

El agujero es el canal de copia, que es el del usuario típico.

Lo que ya cambió a favor (Sprint 33): **ADR-0043** dejó X-DD pip-installable con
`XDD_SCRIPTS_DIR` para resolver scripts dinámicamente; **ADR-0045** expuso el comando `xdd`;
**ADR-0047** habilitó publish en PyPI. Eso pavimenta el camino: el tooling ya puede vivir
fuera del proyecto y actualizarse con `pip`.

No todo debe actualizarse igual. Hay que distinguir tres clases de archivo:

| Clase | Ejemplos | Quién lo cambia | Política de update |
|-------|----------|-----------------|--------------------|
| **Tooling** | `scripts/xdd-*.py/.sh` | Framework | actualizar automático (pip) |
| **Plantillas editables** | `prompts/agents/`, `.agent/workflows/`, `CLAUDE.md` | Framework, a veces user | opt-in, no destructivo |
| **Artefactos del proyecto** | `memoria.md`, `lecciones.md`, `xdd.profile.yml`, `.xdd/` | Usuario / pipeline | **nunca** tocar |

## Decisión

**Adoptar un modelo híbrido (Modelo C):**

1. **Tooling vía pip.** El motor (scripts) se distribuye e instala como paquete
   (`pip install -U x-dd` / `pipx upgrade x-dd`). El proyecto **resuelve** el tooling
   instalado vía entry-points + `XDD_SCRIPTS_DIR` (ADR-0043/0045) en vez de copiarlo.
   `xdd-init` deja de copiar tooling.

2. **Plantillas editables vía `xdd update` (opt-in, no destructivo).** Un comando nuevo
   re-sincroniza `prompts/agents/`, `.agent/workflows/`, gobernanza, comparando la versión
   del framework instalado contra la copia del proyecto. Reglas:
   - Archivos **no modificados** por el user (checksum coincide con el original de su versión)
     → se actualizan en sitio.
   - Archivos **modificados** por el user → NO se pisan; se reporta el diff y se ofrece
     `.new` al lado (estilo `dpkg`/`pacman`), nunca overwrite silencioso.
   - Artefactos del proyecto (`memoria.md`, `lecciones.md`, `xdd.profile.yml`, `.xdd/`) →
     intocables siempre.

3. **Versión + migración.** El proyecto registra contra qué versión de X-DD se inicializó
   (lee `VERSION`, ADR-0033/B7). `xdd update` muestra `de vX → vY` y aplica migraciones
   declarativas si el contrato de fases cambió (respetando append-only, ADR-0044/Art.9: las
   fases nuevas quedan PENDIENTE, nunca INVÁLIDO).

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| **A — pip puro (referencia, no copia)** | un solo `pip -U` actualiza todo | el user no puede customizar workflows/agents en su árbol sin perder el update | demasiado rígido para plantillas que el user toca |
| **B — solo `xdd update` (sigue copiando todo)** | proyecto autocontenido | reimplementa lo que pip ya hace para el tooling; merges para 30+ scripts que el user nunca edita | reinventa la distribución |
| **C — híbrido (elegida)** | tooling auto vía pip; plantillas opt-in no destructivo; artefactos intocables | dos mecanismos (pip + `xdd update`) | la complejidad se justifica por separar lo que cambia el framework de lo que cambia el user |

## Consecuencias

- **Positivas:** los fixes de tooling llegan con `pip install -U x-dd`; las plantillas se
  refrescan con control del user; los artefactos del proyecto nunca se pisan. Cierra el
  agujero del canal de copia.
- **Trade-offs:** el proyecto deja de ser 100% autocontenido para el tooling (necesita X-DD
  instalado) — aceptable, es el modelo de cualquier framework. `xdd update` requiere lógica
  de checksum + 3-way no destructivo.
- **Breaking:** `xdd-init` que deja de copiar tooling es incompatible con proyectos v0.1.x
  existentes → requiere paso de migración (`xdd update --migrate-from-copy`) y por eso esto
  es **objetivo v0.2.0**, no v0.1.0.

## Plan de implementación (v0.2.0)

1. `xdd-init` deja de copiar tooling; el proyecto resuelve scripts vía pip/`XDD_SCRIPTS_DIR`.
2. Nuevo `scripts/xdd-update.py` (+ entry-point `xdd update`): checksum manifest por versión,
   diff no destructivo, `.new` para archivos divergentes.
3. Sello de versión de init en el proyecto (`.xdd/.xdd-version` o en `xdd.profile.yml`).
4. Migración `--migrate-from-copy` para proyectos v0.1.x (de copia → referencia).
5. Documentar el ciclo de update en INSTALL.md + README.

## Relación

- **Construye sobre:** ADR-0043 (pip-installable), ADR-0045 (comando `xdd`), ADR-0047 (PyPI),
  B7 (VERSION única).
- **Respeta:** Art. 9 / ADR-0044 (append-only de fases; firmas no se invalidan retroactivo).
- **Objetivo:** v0.2.0 (breaking para el modelo de copia actual).
