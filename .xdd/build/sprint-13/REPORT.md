# Sprint 13 — Build Report (White-labeling)

> F4 ext. Permite a orgs renombrar la instancia X-DD sin tocar el framework upstream.

## Entregables
| Artefacto | Path | Estado |
|---|---|---|
| 4 personas presets | `prompts/orchestrator/personas/{technical,friendly,casual,formal}.md` | ✅ |
| Profile schema actualizado | `schemas/xdd.profile.schema.json` | ✅ con sección branding |
| Template con branding | `templates/xdd.profile.with-branding.yml` | ✅ todas opciones |
| Script de aplicación | `scripts/xdd-brand.sh` | ✅ + --show + idempotente |
| ADR | `docs/adr/0011-white-labeling-policy.md` | ✅ + entry en ADR README |
| Doc operativa | `docs/BRANDING.md` | ✅ con 3 ejemplos de org |
| Tests | `tests/bats/xdd-brand.bats` | ✅ **10/10 verdes** |

## Capacidades white-labeling

| Customizable (instance) | Inmutable (framework upstream) |
|---|---|
| `ecosystem_name`, `ecosystem_slug` | Repo X-DD upstream |
| `orchestrator_trigger` (/xdd → /helios) | `name: x-dd` en agent.yaml |
| `rename_subworkflows` (opt-in, default false) | NOTICE atribuciones |
| `orchestrator_persona.tone` (4 presets + custom) | ADRs históricos |
| `output.compact` (combinable con xdd-talk-compact) | MEJORAS-X-DD.md |
| `attribution_required` | Estructura .xdd/ |

## Matriz combinable (persona × compact = 4×4)

|  | technical | friendly | casual | formal |
|---|---|---|---|---|
| off | default | accesible | informal | corporativo |
| lite | sin filler | + emojis ok | menos formal | profesional concentrado |
| standard | concise | conversacional breve | shortcuts | ejecutivo |
| ultra | telegraphic | shortcuts emoji | caveman | conciso ejecutivo |

Cada org elige según cultura. Ejemplos en `docs/BRANDING.md`.

## Decisión técnica clave: rename solo trigger principal

`rename_subworkflows: false` por default → sub-workflows mantienen `xdd-*` prefix.
Esto preserva discoverability del framework upstream incluso con rename de la instancia.
Opt-in si la org realmente quiere `/helios-build` en lugar de `/xdd-build`.

## Validaciones
```bash
bash tests/bats/xdd-brand.bats           # 10/10 verde
python3 -m pytest tests/ -q              # 102/102 (sin cambio)
python3 scripts/xdd-shield.py audit --severity=high --ci  # 0 findings
bash scripts/lint-workflows.sh           # 0 errores
```

## Próximo
Sprint 14 (PAUSADO) — Workspace mode + Wizard interactivo. Luego release v0.1.0.
