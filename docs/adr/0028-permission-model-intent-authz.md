# ADR-0028 — Permission model: intent taxonomy + 5-layer eval + OAP authz

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 21

## Context

Sin permission model formal, X-DD asume cualquier tool call es legítima. Casos de explotación posible:
- LLM-generated `rm -rf /`
- Lectura de `.env` con secrets
- Curl a endpoint externo malicioso
- `eval()` arbitrario

Research mostró 3 patterns probados:
- **nah** (intent taxonomy): clasificar tool calls por categoría de riesgo
- **OAP — Open Agent Passport**: pre-action authz deterministic <100ms, 0% attack success
- **Claude Code Auto Mode**: two-stage classifier (fast gate + chain-of-thought)
- **Claude Agent SDK 5-layer eval**: hooks → deny → mode → allow → canUseTool
- **AutoHarness 6-step governance**: parse → risk_classify → permission → execute → sanitize → audit_log

## Decision

Sprint 21 introduce 2 herramientas:

### 1. `scripts/xdd-intent.py` — intent taxonomy classifier
8 intents categorized:
- `filesystem_delete` (critical)
- `secret_access` (critical)
- `lang_exec` (high)
- `fork_subprocess` (high)
- `network_outbound` (medium)
- `filesystem_write` (medium)
- `mcp_external` (medium)
- `read_only` (low)

Regex patterns clasifican tool+args. Sin patrón → default per-tool (Read = read_only, Bash = lang_exec, etc.).

### 2. `scripts/xdd-authz.py` — OAP-style pre-action authz
Deterministic, target <100ms. Lee policy desde:
- `.xdd/.policy.yml` (dedicated)
- `xdd.config.yml` sección `permissions:` (inline)

Policy schema:
```yaml
permissions:
  default_action: allow
  auto_mode_threshold: high   # severity ≥ high → require_approval
  intent_rules:
    - {intent: filesystem_delete, action: require_approval}
    - {intent: secret_access, action: deny}
    - {intent: lang_exec, action: require_approval}
    # ...
```

4 actions: `allow`, `require_approval`, `mask`, `deny`. Exit codes: 0/1/1/2.

### 3. Hook `.agent/hooks/scripts/pre-tool-authz.sh`
PreToolUse hook que lee `XDD_TOOL_NAME` + `XDD_TOOL_ARGS` env vars → invoca `xdd-authz check` → bloquea si exit=2.

### 4. `templates/constitution.template.yml`
Machine-readable adapter del constitution.md humano. Espeja permissions + sandbox + observability. Inspirado en AutoHarness constitution YAML.

## Alternatives considered

- **OPA (Open Policy Agent) embedded:** rechazado. Heavy + Rego DSL barrier.
- **Solo allow/deny binary:** rechazado. `require_approval` y `mask` son intermedios útiles.
- **Hardcoded policy en script:** rechazado. Per-proyecto must override.
- **5 layers idéntico Claude SDK:** simplificado a 3 (intent → rule → default). 5 layers añadía complejidad sin claro beneficio.

## Consequences

### Positivas
- ✅ Enterprise-ready: tool calls pasan por authz determinístico
- ✅ <100ms target verificado en tests
- ✅ Policy machine-readable + auditable
- ✅ Hook activable per-profile (default no-op; strict activa)
- ✅ Compat con xdd-sandbox: authz decide IF, sandbox decide HOW
- ✅ AutoHarness 6-step governance integrado (parse→classify→permission→execute→sanitize→audit) via combinación de xdd-intent + xdd-authz + xdd-shield + xdd-otel + hooks

### Negativas
- ⚠️ Patterns regex no cubren todos los casos edge (false negatives posibles)
- ⚠️ `require_approval` requiere orchestrator que sepa prompt humano (X-DD declara metadata, no fuerza UX)
- ⚠️ Sin auditing trail SQL todavía (solo exit codes + JSON). Diferido a Sprint 22 evidence layer

## Implementation Sprint 21

```bash
# Classify
python3 scripts/xdd-intent.py classify --tool=Bash --args='{"command":"rm -rf /"}' --json

# Authz check
python3 scripts/xdd-authz.py check --tool=Read --args='{"path":"/home/x/.env"}' --json
# → action: deny, exit 2

# Policy validate
python3 scripts/xdd-authz.py policy --validate

# Hook activation in xdd.config.yml
hooks:
  profile: strict
```

## Related
- ADR-0027 Sandbox provider (companion)
- ADR-0021 Observability stack (audit log via OTel)
- ADR-0011 White-labeling (constitution puede heredar org branding)
- Sprint 12 AgentShield (audit estático complementa runtime authz)

## References
- nah intent taxonomy: ai-boost/awesome-harness-engineering
- OAP — Open Agent Passport: 53ms median, 0% attack success (research)
- Claude Code Auto Mode: walkinglabs
- Claude Agent SDK 5-layer: walkinglabs
- AutoHarness 6-step: https://github.com/aiming-lab/AutoHarness
