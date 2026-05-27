# The Shortform Guide to X-DD

> ~15 min de lectura. Para developers que quieren entender qué es X-DD y arrancar.
> Para más detalle: [`the-longform-guide.md`](the-longform-guide.md).
> Para seguridad: [`the-security-guide.md`](the-security-guide.md).

## Qué es X-DD en una línea

> **Pipeline gated de 6 fases para desarrollo agéntico con IA, con metodologías
> *-Driven Development* integradas, gate keeper firmado HMAC, MCP server propio
> y dogfooding visible.**

## El problema que resuelve

Desarrollás con Claude Code, Cursor, OpenCode (o cualquier asistente IA). Pasa una
de dos cosas:

1. **Vibe-coding sin disciplina:** velocidad alta inicial, deuda técnica y bugs
   acumulándose, decisiones imposibles de auditar.
2. **Proceso pesado anti-IA:** Scrum/SAFe que no aprovecha la velocidad de los agentes.

X-DD ofrece el punto medio: **pipeline gated de 6 fases** + **metodologías
embebidas** + **memoria persistente** + **trazabilidad criptográfica** + **portabilidad
multi-IDE vía MCP**.

## Las 6 fases del pipeline

```
1. Briefing → 2. Spec → 3. Plan → 4. Build → 5. QA → 6. Retro
```

Cada fase produce artefactos versionados y requiere **aprobación con firma
HMAC-SHA256** para avanzar (no se puede saltar fases).

| Fase | Artefactos | Metodologías embebidas |
|------|------------|------------------------|
| 1. Briefing | `SPEC.md`, `FEATURES.md`, `.feature` stubs | FDD + BDD + ATDD |
| 2. Spec | `DOMAIN.md`, `THREATS.md` | DDD + Threat Modeling |
| 3. Plan | `PLAN.md` | FDD (features verticales) |
| 4. Build | `src/`, `tests/` | TDD + STDD |
| 5. QA | `QA_REPORT.md` | BDD ejecutable + SAST + DAST + Secrets |
| 6. Retro | `lecciones.md` | Learning Loop |

## Quickstart (4 minutos)

```bash
# 1. Verificar entorno (te dice qué falta)
bash scripts/xdd-doctor.sh

# 2. Bootstrap proyecto (profile core = recomendado)
bash scripts/xdd-init.sh /ruta/al/proyecto --profile=core

# 3. cd y arrancar
cd /ruta/al/proyecto
bash scripts/xdd-start.sh

# 4. En el orquestador, ejecutar el workflow principal:
/xdd
```

> En Windows: `.\install.ps1 -Dest C:\proyectos\mi-app -Profile core`

## Cómo es distinto

| Capacidad | X-DD | Frameworks típicos |
|---|---|---|
| Gates firmados | ✅ HMAC-SHA256 obligatorio | Convención de carpetas |
| DOMAIN/THREATS de primera clase | ✅ obligatorios Fase 2 | Opcional |
| Dogfooding visible | ✅ X-DD se aplica a sí mismo (`.xdd/`) | Sin precedente |
| Multi-IDE vía MCP | ✅ Cursor/Continue/Zed/Cline/Windsurf nativo | 1-2 IDEs hard-coded |
| Tests del propio framework | 97 (35 bats + 50 pytest + 12 E2E) | Pocos o ninguno |

## Capacidades clave

### Gate keeper firmado (Sprint 4)

```bash
python3 scripts/xdd-gate.py init                          # genera .gate-key
python3 scripts/xdd-gate.py approve --phase spec --approver "vos"
python3 scripts/xdd-gate.py validate --phase spec         # ✓ firma válida
# Si alguien modifica DOMAIN.md sin re-aprobar → validate detecta tampering
```

### MCP server propio (Sprint 6)

X-DD habla [Model Context Protocol](https://spec.modelcontextprotocol.io)
nativamente. 6 tools expuestas. **Cualquier IDE MCP-compatible** (Cursor, Continue,
Zed, Cline, Windsurf) lo consume sin adapter dedicado. Ver `docs/MCP_INTEGRATION.md`.

### Hook system event-driven (Sprint 7)

8 hooks bash cross-platform:
- `pre:bash:dangerous-command` — bloquea `rm -rf /`, `git push --force`, `curl | sh`
- `pre:edit:config-protection` — protege linters/configs sensibles
- `post:edit:mempalace-index` — indexa MemPalace en background
- `session-start:context-load` — carga `WORKING-CONTEXT.md` al iniciar
- ... y 4 más

Activar: `export XDD_HOOK_PROFILE=strict`.

### Manifest-driven install (Sprint 7)

6 profiles: `minimal | core | developer | security | research | full`. Instalá
solo lo que necesitás.

```bash
bash scripts/xdd-init.sh /tu/proyecto --profile=developer
# o granular:
bash scripts/xdd-init.sh /tu/proyecto --modules=core,mcp-server,hooks-runtime
```

### Registry de 180 agentes (Sprint 5)

`prompts/agents/registry.json` es la SSoT. `docs/equipo.md` se regenera con
`bash scripts/generate-equipo.sh`. Composition patterns: `security_review`,
`feature_squad`, `release_train`.

## Capacidades v0.1.0 avanzadas (Sprints 9-13 ya done)

### Continuous Learning (Sprint 9)
Hook `stop:pattern-extraction` extrae patrones de sesiones → SQLite (`~/.xdd/state.db`).
`/evolve` agrupa instincts ≥3 con confidence ≥0.5 → propone skills/agents/commands.
**Aprobación humana obligatoria** (T6.1).

```bash
python3 scripts/xdd-state.py stats
python3 scripts/xdd-state.py evolve --generate  # propuestas en evolutions table
```

### Skills + Eval-harness (Sprint 10)
Sistema `skills/<name>/SKILL.md`. 5 grader types (structural/behavioral/output_match/pass_at_k/token_count_reduction).
Skill `xdd-talk-compact` reduce ~50-75% tokens del orquestador (sistema propio
de compresión, 3 niveles lite/standard/ultra).

```bash
python3 scripts/xdd-eval.py list
python3 scripts/xdd-eval.py run --all --ci
```

### Multi-agent orchestration (Sprint 11)
`/orchestrate` ejecuta composition_patterns (sequential/parallel/parallel_then_sync).

```bash
python3 scripts/xdd-orchestrate.py list
python3 scripts/xdd-orchestrate.py run --pattern=security_review --json
```

### AgentShield + Shannon híbrido (Sprint 12)
- **`xdd-shield`** audita el propio framework (13 reglas SAST). Repo X-DD pasa 0 crit/high.
- **`xdd-pentest`** wrapper: usa Shannon CLI ([KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon), AGPL-3.0) si instalado; degrada a STRIDE + source-review estático si no.

```bash
python3 scripts/xdd-shield.py audit --severity=high --ci
bash scripts/xdd-pentest.sh stride                  # sin Shannon
bash scripts/xdd-pentest.sh fuzz https://example.com  # con Shannon
```

### White-labeling (Sprint 13)
Renombrar instance + custom trigger + 4 personas presets (technical/friendly/casual/formal) en `xdd.profile.yml` sección `branding`.

```yaml
branding:
  ecosystem_name: "Helios"
  orchestrator_trigger: "helios"   # /xdd → /helios
  orchestrator_persona:
    tone: "friendly"
```

```bash
bash scripts/xdd-brand.sh /tu/proyecto
```

## Roadmap pendiente para v0.1.0

| # | Capacidad | Estado |
|---|---|---|
| Sprint 14 | Workspace mode + Wizard interactivo + ADR-0012 | ⏳ pausado |
| Release | tag firmado v0.1.0 + RELEASES/v0.1.0.md | ⏳ |

## Para saber más

- **Filosofía + decisiones:** `docs/adr/` (11 ADRs Nygard)
- **Referencia exhaustiva:** [`the-longform-guide.md`](the-longform-guide.md)
- **Modelo de amenazas + SecDD:** [`the-security-guide.md`](the-security-guide.md)
- **Inspiración ECC + research:** [`docs/research/`](docs/research/)
- **Plan vigente:** [`MEJORAS-X-DD.md`](MEJORAS-X-DD.md)
- **Dogfooding live:** [`.xdd/`](.xdd/) + [`WORKING-CONTEXT.md`](WORKING-CONTEXT.md)
- **White-labeling:** [`docs/BRANDING.md`](docs/BRANDING.md)
- **Pentest híbrido:** [`docs/PENTEST.md`](docs/PENTEST.md)

## Empezá ahora

```bash
make doctor    # ver qué necesitás
make help      # ver todos los comandos
```
