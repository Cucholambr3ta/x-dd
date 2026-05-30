# Sprint 3 — Build Report

> Fase 4-Build (1/5). Cierre del primer paso de la fase de construcción.

## Tareas MEJORAS abordadas
- **1.2** — `xdd.config.yml` centralizado con schema JSON.
- **1.3** — `xdd-doctor.sh` v2 con SemVer real + salida `--json` (sobre-mejora).

## Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| Doctor v2 | `scripts/xdd-doctor.sh` | ✅ SemVer real + `--json` |
| Schema | `schemas/xdd.config.schema.json` | ✅ JSON Schema draft 2020-12 |
| Config raíz | `xdd.config.yml` | ✅ con directiva `yaml-language-server` |
| Doc | `docs/CONFIG.md` | ✅ referencia completa |

## Validaciones

```bash
# Salida humana
bash scripts/xdd-doctor.sh
# → 17 OK, 9 warnings (opcionales), 0 críticos

# Salida JSON (parseable)
bash scripts/xdd-doctor.sh --json | python3 -m json.tool
# → JSON válido con tool/version/timestamp/summary/checks[]

# Config válido YAML
python3 -c "import yaml; yaml.safe_load(open('xdd.config.yml'))"
# → OK

# Lint workflows sigue verde
bash scripts/lint-workflows.sh
# → 0 errores, 0 warnings
```

## Sobre-mejoras incorporadas

- Salida `--json` del doctor (no estaba en plan original) — habilita integración futura con dashboards y CI gates.
- `bash` añadido a deps obligatorias (estaba implícito).
- `pytest` y `bats` añadidos a checks opcionales (necesarios para Sprint 4+ y 7).

## Aprendizajes
Ver entradas Sprint 3 en `../../../../lecciones.md`.

## Próximo paso
**Sprint 4 — Gate keeper HMAC-SHA256** (Fase 4-Build 2/5). Esta es la base para que todo el resto del sistema de aprobaciones sea genuinamente auditable.
