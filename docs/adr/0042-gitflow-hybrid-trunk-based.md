# ADR-0042: Reconciliación del Protocolo GitFlow — híbrido trunk-based por defecto

**Estado:** Aceptada
**Fecha:** 2026-05-29
**Sprint:** 32
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

El Artículo 7 de la Constitución (v1.4) prescribía **GitFlow clásico**: rama `develop`
de integración + nomenclatura `feature/*`, `bugfix/*`, `hotfix/*`, `release/v*`.

La práctica real durante los 31 sprints que el sistema se autoconstruyó **divergió** de esa
ley:

- **No existe** rama `develop`. Nunca se creó.
- Flujo real: `feat/sprint-N-tema` → PR → **squash merge directo a `main`**.
- Cada commit en `main` corresponde a 1 PR cerrado (`#40`–`#48`).
- Nomenclatura real: `feat/`, `fix/`, `docs/` (no `feature/`, `bugfix/`).
- Conventional Commits en los mensajes: `feat(scope):`, `fix(scope):`, `docs(scope):`.

Esto es **Trunk-Based Development**, recomendado por el propio agente
`engineering-git-workflow-master` "para la mayoría de equipos" y coherente con un
contexto solopreneur: rama corta → `main`, sin capa `develop` intermedia.

La contradicción Ley↔práctica debilitaba la auditoría de gobernanza: el sistema se
declaraba GitFlow mientras operaba trunk-based, y `xdd-shield` / la suite de tests no lo
detectaban.

## Decisión

Reescribir el Artículo 7 a **modelo híbrido honesto** (Constitución v1.5):

1. **Modo por defecto: Trunk-Based.** `main` siempre desplegable. Ramas de vida corta
   `feat/*`, `fix/*`, `docs/*`, `chore/*` → PR → squash merge a `main`.
2. **Modo opt-in: GitFlow.** Proyectos con releases versionados pueden adoptar `develop`
   + `release/v*` + `hotfix/*`. La Constitución describe ambos; el default es trunk.
3. **Invariantes en ambos modos** (no negociables):
   - `main` protegida: prohibido push directo; integración solo vía PR con aprobación humana.
   - **Tests verdes obligatorios** antes de merge (Art. 7 §4) — ahora gate real en CI
     (`.github/workflows/tests.yml`: pytest + bats + AgentShield), no verbal.
   - Conventional Commits.

Justificación: el framework es **agnóstico y multi-proyecto**. Forzar `develop` a todos
los proyectos contradice la realidad solopreneur probada; prohibir GitFlow limita
proyectos con cadencia de release. El híbrido refleja lo que sostuvo el sistema y escala.

## Consecuencias

### Positivas
- Ley alineada con práctica probada → auditoría de gobernanza coherente.
- "Tests verdes" deja de ser declaración verbal y pasa a ser gate ejecutable en CI.
- Flexibilidad: trunk por defecto, GitFlow disponible cuando aporta.

### Negativas / riesgos
- Proyectos existentes que asumían `develop` deben migrar conscientemente (opt-in).
- Dos modos = más superficie a documentar.

## Alternativas consideradas

1. **Adoptar GitFlow literal** (crear `develop`): doblar la práctica a la ley. Descartado:
   añade ceremonia que el sistema nunca necesitó en 31 sprints.
2. **Enmendar Art.7 solo a trunk-based**: alinear ley a práctica, sin GitFlow. Descartado:
   un framework agnóstico no debe cerrar la puerta a releases versionados.
3. **Híbrido honesto** (elegida): describe ambos, default trunk, invariantes compartidos.

---

*Relacionado: ADR-0006 (gate HMAC), ADR-0038 (workflow enforcement). Constitución v1.5 Art. 7.*
