# Memoria Sprint 28 — 2026-06-04

> MEGASPRINT: Atomizacion total del pipeline X-DD + sistema JSON/MD de ahorro de tokens.
> Plan aprobado por el usuario. Esta es la fuente de verdad de trazabilidad.

## Plan aprobado

Atomizar el 15% restante del pipeline (briefing/spec/retro ya atomicos) + introducir
par JSON/MD para ahorro de tokens. Estado inicial: 85% atomico, 6 monoliticos accidentales
+ 1 monolitico-por-formato (openapi).

### Incrementos

| Inc | Objetivo |
|-----|----------|
| 0 | Sistema JSON/MD — xdd-doc-sync.py (genera .json compacto desde .md fuente de verdad) |
| 1 | Infraestructura atomicidad — check_atomic_folder + check_json_sidecar + xdd-init skeleton + ADR-0050 |
| 2 | acuerdos/sprint.md → acuerdos/sprints/ (carpeta + INDEX + puntero compat) |
| 3 | acuerdos/memoria/MEMORY.md → 3 atomos (decisiones/convenciones/riesgos) + aggregate |
| 4 | docs/FEATURES.md → docs/features/ (gate copy .xdd unchanged) |
| 5 | docs/DOMAIN.md → docs/domain/ + UBIQUITOUS_LANGUAGE.md |
| 6 | openapi.yaml → api/openapi/fragments/ + raiz generada (ADR-0051) |
| 7 | PRIVACY.md → docs/privacy/ por categoria PII |
| 8 | qa_runId_latest.md → 3 tier files + INDEX (NDJSON intacto) |
| 9 | HERENCIA COMPLETA A EVOL-DD (E0-E9, namespace evol-, bump PyPI) |

### Decisiones tomadas

| ID | Decision |
|----|----------|
| D1 | sprint.md coexiste como puntero a sprints/INDEX.md |
| D2 | MEMORY.md → 3 atomos: decisiones/convenciones/riesgos |
| D3 | QA: NDJSON intacto + 3 MD por tier + INDEX |
| D4 | ADR-0050 (atomicidad) + ADR-0051 (openapi fragments) |
| D5 | NO modificar PHASE_ARTIFACTS — mantiene HMAC verde |
| D6 | Plural para contables (sprints/, features/), singular para masa (domain/) |
| D7 | Editamos comportamiento del framework, no contenido de ejemplo |
| JSON-1 | JSON = estructura maxima de ahorro de tokens. MD = fuente de verdad, calidad completa |
| JSON-2 | xdd-doc-sync.py genera JSON desde MD auto post-escritura |
| JSON-3 | Alcance: todo el plan Inc 0-9 |

### Keystone arquitectonico

X-DD tiene 2 arboles: GATE TREE (.xdd/<phase>/, firmado HMAC, NO se toca) y RICH TREE
(acuerdos/ + docs/, atomico). Todos los monoliticos viven en RICH TREE. Dividirlos NO
rompe el gate. Enforcement de atomicidad via xdd-discipline-check.py, no via PHASE_ARTIFACTS.

### Ahorro de tokens esperado

Antes: cargar 80 docs MD = ~200k tokens. Despues: INDEX.json maestro (~3-5k) + solo los
2-3 MD del subdominio en curso (~8k) = ahorro ~95% en navegacion.

## Hitos

- (en progreso — se completa al cerrar la sesion)

## Bloqueos

- (ninguno aun)

## Proxima sesion

- Continuar incrementos pendientes si no se completan todos
- Verificar herencia Evol-DD v0.2.9 en PyPI
