# ADR-0013 — Monorepo: 3 modos (isolated / shared / hybrid)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 15

## Context

Sprint 14 introdujo workspace mode (N proyectos en una carpeta, cada uno independiente). Workspaces ≠ monorepos.

**Monorepo verdadero** = N packages versionados/buildeados como una unidad, con dependencias inter-package gestionadas por una tool (nx/turborepo/pnpm-workspaces/lerna/bazel/cargo/go workspaces).

X-DD necesita soportar monorepos porque la mayoría de equipos modernos los usan. Pero no hay un único modelo correcto — depende de cómo el equipo opera.

## Decision

Soportar **3 modos explícitos** declarados en `xdd.profile.yml`:

### Modo 1: `isolated`
Cada package es proyecto X-DD independiente. Cada uno con su propio `.xdd/`, `xdd.profile.yml`, `.gate-key`.

```yaml
monorepo:
  mode: isolated
  tool: nx
  packages_dir: packages
  packages:
    - {name: api, path: packages/api, profile: developer}
    - {name: web, path: packages/web, profile: core}
```

**Cuándo usar:** packages con ciclos de vida muy distintos (api estable + web experimental). Máxima autonomía.

**Implicaciones:**
- Gate keeper per-package
- Fases independientes (api en QA, web en Build)
- No comparte memoria/state por default (override con `workspace.shared_memory=true` Sprint 14)

### Modo 2: `shared`
Un solo `.xdd/` en raíz del monorepo. Todos los packages comparten gate, fases, gate-key. Como si fuera 1 proyecto.

```yaml
monorepo:
  mode: shared
  tool: pnpm-workspaces
  packages:
    - {name: api, path: packages/api}
    - {name: web, path: packages/web}
```

**Cuándo usar:** packages tightly coupled (cliente + librería compartida). Release sincronizado.

**Implicaciones:**
- 1 SPEC.md, 1 PLAN.md, 1 QA_REPORT.md
- `qa-review` corre tests de TODOS los packages
- 1 gate firmado = release coordinado

### Modo 3: `hybrid`
Fases meta (briefing/spec/plan) en raíz, fases ejecución (build/qa/retro) per-package via `owns_phases`.

```yaml
monorepo:
  mode: hybrid
  tool: turborepo
  packages:
    - {name: api, path: packages/api, profile: developer, owns_phases: [build, qa, retro]}
    - {name: web, path: packages/web, profile: core, owns_phases: [build, qa, retro]}
```

**Cuándo usar:** un product team con N microservices. Decisiones de arquitectura compartidas; ejecución autónoma.

**Implicaciones:**
- Briefing/Spec/Plan firmados a nivel raíz (consenso)
- Build/QA/Retro firmados per-package (autonomía)
- `.xdd/` raíz + `.xdd/` per-package coexisten

## Alternatives considered

- **Single mode "auto-detect":** rechazado. La elección es estratégica, no técnica.
- **Modes implícitos por presencia de `nx.json` etc:** rechazado. Hace magia ambigua.
- **Solo `shared` mode + workspace mode para isolated:** rechazado. Hybrid es el caso real más común y merece primera clase.

## Consequences

### Positivas
- ✅ Cubre 3 patrones reales de uso de monorepos
- ✅ Schema explícito → adopters declaran intent, no se asume
- ✅ Backwards compatible con projects no-monorepo (sin sección `monorepo:`)
- ✅ Compatible con todas las tools monorepo (nx/turborepo/pnpm/yarn/lerna/bazel/cargo/go)
- ✅ Hybrid mode habilita el patrón "1 product, N microservices" sin custom tooling

### Negativas
- ⚠️ 3 modos = 3 paths de testing necesarios (cobertura tests bats)
- ⚠️ Hybrid añade complejidad: gate keeper debe entender ownership de fase
- ⚠️ `shared` y `isolated` ya cubren 80% de casos — riesgo de over-engineering
- ⚠️ Runtime de workflows asume ahora opcionalmente `--package=<name>` flag (TODO Sprint 16)

## Implementation in Sprint 15

- `schemas/xdd.profile.schema.json`: añade sección `monorepo:` con enum mode
- `scripts/xdd-monorepo.sh`: helper que detecta tool (lee nx.json/turbo.json/pnpm-workspace.yaml/etc) y sugiere mode
- `scripts/xdd-wizard.sh`: añade paso "monorepo?" si destino contiene package.json + nx.json/turbo.json/pnpm-workspace.yaml/lerna.json/Cargo.toml workspaces
- `docs/MONOREPO.md`: guía completa de los 3 modos + cuándo usar cuál
- `tests/bats/xdd-monorepo.bats`: tests por modo

## Related

- ADR-0012 Workspace mode + Wizard
- Sprint 16 (next): Workflow runtime `--package=<name>` routing
- ECC-research, awesome-harness-engineering (no abordan monorepo explícitamente)

## References

- Nx: https://nx.dev
- Turborepo: https://turbo.build
- pnpm workspaces: https://pnpm.io/workspaces
- Bazel: https://bazel.build
- Cargo workspaces: https://doc.rust-lang.org/cargo/reference/workspaces.html
