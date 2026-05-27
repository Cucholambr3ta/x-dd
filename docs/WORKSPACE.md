# Workspace mode + Wizard (Sprint 14)

## Wizard interactivo

```bash
bash scripts/xdd-wizard.sh
# o con defaults silenciosos:
bash scripts/xdd-wizard.sh --dest=/path --non-interactive
```

7 pasos: destination → profile → workspace mode → branding → persona → compact → confirm → invoca `xdd-init.sh` + `xdd-brand.sh` si custom.

## Workspace mode

Opt-in via `xdd.profile.yml`:

```yaml
workspace:
  enabled: true
  root: "/abs/path/to/workspace"
  shared_memory: true       # ~/.xdd/state.db compartido
  shared_gate_key: false    # cada proyecto su .gate-key (default seguro)
  projects:
    - name: "api"
      path: "./api"
      profile: "developer"
    - name: "web"
      path: "./web"
      profile: "core"
    - name: "worker"
      path: "./worker"
      profile: "minimal"
```

## Comportamiento

| Setting | Default | Effect |
|---|---|---|
| `enabled` | false | Comportamiento legacy 1-proyecto |
| `shared_memory` | true | Instincts atraviesan proyectos (cross-pollination) |
| `shared_gate_key` | false | Cada proyecto firma con su propia key (recomendado) |

## Cuándo usar workspace mode

- ✅ Monorepo light: api + web + worker en un repo
- ✅ Multi-app projects: 3 microservices en 3 carpetas
- ✅ Mobile + backend: app/ + backend/ + admin/
- ❌ Monorepo grande con miles de packages → ver [docs/MONOREPO.md](MONOREPO.md) (Sprint 15)

## Limitaciones actuales

- Workflow runtime asume proyecto único — Sprint 15 añade `--project=<name>` routing
- `shared_memory=true` puede generar cross-talk → mitigado en Sprint 16 con TF-IDF clustering

## Referencias

- [ADR-0012 Workspace mode + Wizard](adr/0012-workspace-mode-wizard.md)
- [ADR-0011 White-labeling policy](adr/0011-white-labeling-policy.md)
