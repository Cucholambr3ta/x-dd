# Monorepo en X-DD (Sprint 15 + ADR-0013)

X-DD soporta monorepos en **3 modos explícitos**: `isolated`, `shared`, `hybrid`.

## Quick detect

```bash
bash scripts/xdd-monorepo.sh detect /path/to/repo    # imprime tool detectado
bash scripts/xdd-monorepo.sh suggest /path/to/repo   # tool + modo recomendado + yaml sample
```

Tools detectados: `nx`, `turborepo`, `pnpm-workspaces`, `yarn-workspaces`, `lerna`, `rush`, `bazel`, `cargo-workspaces`, `go-workspaces`.

## Los 3 modos

### `isolated` — máxima autonomía per-package

Cada package es proyecto X-DD independiente con su propio `.xdd/`, `xdd.profile.yml`, `.gate-key`.

```yaml
monorepo:
  mode: isolated
  tool: lerna
  packages:
    - {name: api, path: packages/api, profile: developer}
    - {name: web, path: packages/web, profile: core}
```

**Cuándo:** packages con ciclos de vida muy distintos. Releases independientes.

### `shared` — un solo gate, release sincronizado

Un único `.xdd/` en raíz. Todos los packages comparten gate, fases, gate-key.

```yaml
monorepo:
  mode: shared
  tool: pnpm-workspaces
  packages:
    - {name: api, path: packages/api}
    - {name: web, path: packages/web}
```

**Cuándo:** packages tightly coupled. 1 SPEC.md = 1 release coordinado.

### `hybrid` — meta-fases compartidas, ejecución autónoma

Briefing/Spec/Plan en raíz (consenso). Build/QA/Retro per-package (autonomía).

```yaml
monorepo:
  mode: hybrid
  tool: nx
  packages:
    - {name: api, path: packages/api, profile: developer, owns_phases: [build, qa, retro]}
    - {name: web, path: packages/web, profile: core, owns_phases: [build, qa, retro]}
```

**Cuándo:** 1 product team con N microservices. Arquitectura compartida, dev autónomo.

## Tabla de decisión

| Pregunta | isolated | shared | hybrid |
|---|---|---|---|
| ¿Releases independientes? | ✅ | ❌ | ⚠️ por package |
| ¿Spec única raíz? | ❌ | ✅ | ✅ |
| ¿1 gate keeper? | ❌ N | ✅ 1 | ⚠️ 1+N |
| ¿Mejor para teams pequeños? | ❌ | ✅ | ⚠️ |
| ¿Mejor para teams grandes? | ⚠️ | ❌ | ✅ |

## Defaults por tool (suggest)

| Tool | Modo sugerido | Razón |
|---|---|---|
| nx, turborepo, bazel | hybrid | Build orchestration sofisticada → equipo grande |
| pnpm-workspaces, yarn-workspaces | shared | Tightly coupled JS packages |
| lerna, rush | isolated | Lerna histórico = packages publicados independientes |
| cargo-workspaces, go-workspaces | shared | Single binary o lib unified release típico |

Sobreescribir el suggest cuando tu equipo opere distinto.

## Limitaciones actuales (post-Sprint 15)

- Workflow runtime no enruta por `--package=<name>` todavía → Sprint 16
- `hybrid` mode requiere gate keeper consciente de `owns_phases` → Sprint 16
- Tests E2E por modo: solo unit-level tests, no integration

## Referencias

- [ADR-0013 Monorepo 3 modos](adr/0013-monorepo-three-modes.md)
- [ADR-0012 Workspace mode + Wizard](adr/0012-workspace-mode-wizard.md)
- [docs/WORKSPACE.md](WORKSPACE.md) (mode workspace = N proyectos sin monorepo tool)
