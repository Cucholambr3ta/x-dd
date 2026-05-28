# ADR-0036 — Codex adapter (skills global, orchestrator pattern)

**Date:** 2026-05-28
**Status:** Accepted
**Sprint:** Post-Sprint 25 follow-up

## Context

User aportó guía oficial de Codex (OpenAI CLI) — convención propia distinta a Claude Code/OpenCode/Cursor/etc.:
- Skills viven **GLOBAL** en `~/.codex/skills/<name>/`
- `SKILL.md` con frontmatter **minimal**: solo `name` (lowercase + dashes) + `description`
- Pattern recomendado: **NO** crear N skills individuales para N agentes. Mejor **1 orchestrator skill** + `agents-index.json` en `references/`
- Codex carga skill leyendo solo `name` + `description` del frontmatter
- Convención trigger: declarar en description (ej. `"Use when the user starts with /trigger..."`) — Codex no tiene slash registry

X-DD gap: adapter no soportaba Codex. 6 IDEs hasta ahora, todos project-local.

## Decision

Sprint follow-up añade `target codex` a `xdd-adapt.sh`:

### 1. Orchestrator skill global
`~/.codex/skills/<trigger>-orchestrator/`:
- `SKILL.md`: frontmatter MINIMAL (name + description), body describe X-DD pipeline 6 fases
- `references/agents-index.json`: 180 agentes con id/name/category/description (desde registry)
- `references/workflows-index.md`: 54 workflows extraídos auto
- `references/x-dd-constitution.md`: copia constitucion local
- `scripts/invoke_workflow.sh`: helper para leer workflow desde project root

### 2. 6 X-DD skills propias copiadas
`skills/{xdd-talk-compact, agent-eval, xdd-ai-review, xdd-compact, xdd-fs-context, xdd-sandbox}/` → `~/.codex/skills/<name>/` (compat directo — frontmatter X-DD tiene name+description, campos extra Codex ignora).

### 3. Project-level README
`<DEST>/.codex/README-xdd.md` documenta dónde vive realmente la skill (global) + uso `/trigger objetivo`.

### 4. Auto-detect en xdd-init
`xdd-init.sh` detecta `command -v codex` OR `~/.codex` dir → corre adapter codex auto.

### 5. Override env
`XDD_CODEX_HOME=/path` para tests + setups custom.

## Alternatives considered

- **N skills individuales (1 por agente):** rechazado per guía Codex ("No instales todos los agentes como skills al inicio") — satura entorno.
- **Skill por workflow individual:** rechazado. 54 skills = ruido. Mejor 1 orchestrator + index.
- **Frontmatter rico (origin, inspired_by, etc.):** rechazado per guía Codex ("No uses campos extra").
- **Project-local `.codex/skills/`:** Codex convención = GLOBAL únicamente. Project README solo para referencia.

## Consequences

### Positivas
- ✅ Codex = 7° IDE soportado (X-DD pipeline accesible desde OpenAI Codex)
- ✅ Pattern orchestrator + index = escalable (180 agentes sin saturar)
- ✅ 6 X-DD skills propias compat directo (frontmatter X-DD name+description = subset Codex)
- ✅ Auto-detect → cero pasos manuales si user tiene Codex instalado
- ✅ Override env var = testeable + setup custom

### Negativas
- ⚠️ Skills GLOBAL → todas las skills X-DD se ven en TODOS los proyectos Codex del user (aceptable, son governance/devops)
- ⚠️ `agents-index.json` deviene de registry — si user actualiza X-DD upstream, re-correr `xdd-adapt codex` necesario
- ⚠️ Codex helper script asume project root tiene `.agent/workflows/` — global install (Sprint 25) ya cubre esto

## Implementation

```bash
# Auto (xdd-init detecta codex):
bash scripts/xdd-init.sh /proj --profile=full

# Manual:
bash scripts/xdd-adapt.sh codex --dest=/proj                    # global ~/.codex/skills/
bash scripts/xdd-adapt.sh codex --dest=/proj --trigger=helios   # custom trigger

# Test/override:
XDD_CODEX_HOME=/tmp/test-codex bash scripts/xdd-adapt.sh codex --dest=/proj

# Uso en Codex:
# /xdd <objetivo>            → orchestrator activado
# /xdd list agents security  → filtra desde agents-index.json
# /xdd validate spec         → gate validation
```

## Related
- ADR-0034 Universal IDE adapter (6 IDEs base; este sprint añade 7°)
- ADR-0035 Global install architecture (Codex skills global = mismo pattern)
- ADR-0007 Alcance inicial adapters (superseded en alcance: 6 → 7)
- ADR-0011 White-labeling (trigger propaga a orchestrator name)

## References
- Guía Codex usuario (input dogfooding) → `GUIA_CODEX_AGENTES_SKILLS_WORKFLOWS.md` (no committed, ref local)
- Codex CLI docs (OpenAI): https://github.com/openai/codex
