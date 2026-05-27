# Permission Model — X-DD (Sprint 21)

`xdd-intent` (clasifica) + `xdd-authz` (decide) + hook PreToolUse (enforce).

## Quick start

```bash
# Classify una tool call
python3 scripts/xdd-intent.py classify --tool=Bash --args='{"command":"rm -rf /"}' --json

# Authz check (lee policy desde xdd.config.yml o .xdd/.policy.yml)
python3 scripts/xdd-authz.py check --tool=Read --args='{"path":"/home/x/.env"}' --json

# Show effective policy
python3 scripts/xdd-authz.py policy --show
```

## Intent taxonomy (8 intents)

| Intent | Severity | Default action | Ejemplos |
|---|---|---|---|
| `filesystem_delete` | critical | require_approval | rm -rf, drop table |
| `secret_access` | critical | **deny** | .env, ~/.aws/credentials |
| `lang_exec` | high | require_approval | eval, exec, subprocess |
| `fork_subprocess` | high | allow | spawn, nohup, & |
| `network_outbound` | medium | allow | curl, wget (no localhost) |
| `filesystem_write` | medium | allow | > file, >> file |
| `mcp_external` | medium | require_approval | non-trusted MCP server |
| `read_only` | low | allow | Read, Glob, Grep |

## Policy declarativa

`xdd.config.yml`:
```yaml
permissions:
  default_action: allow
  auto_mode_threshold: high
  intent_rules:
    - {intent: filesystem_delete, action: require_approval}
    - {intent: secret_access, action: deny}
    - {intent: lang_exec, action: require_approval}
```

Override más granular: `.xdd/.policy.yml` dedicado.

## 4 actions posibles

| Action | Exit code | Significado |
|---|---|---|
| `allow` | 0 | Tool call procede normalmente |
| `require_approval` | 1 | Orchestrator debe prompt humano antes |
| `mask` | 1 | Permitir pero ocultar output sensible |
| `deny` | 2 | Bloquear tool call completamente |

## Hook integration (.agent/hooks/scripts/pre-tool-authz.sh)

Activación: profile `strict` en `xdd.config.yml`.

Orchestrator setea `XDD_TOOL_NAME` + `XDD_TOOL_ARGS` antes del tool call. Hook invoca `xdd-authz check`. Exit 2 → bloquea.

## Performance

OAP target: <100ms. Verificado en tests (test_authz.py:test_cmd_check_elapsed_under_100ms).

## Constitution YAML

`templates/constitution.template.yml`: adapter machine-readable que espeja sección permissions + otros (sandbox, observability, quality). Adoptarlo en proyectos para policy formal versionable.

## Referencias

- [ADR-0027 Sandbox provider](adr/0027-sandbox-provider-abstraction.md)
- [ADR-0028 Permission model](adr/0028-permission-model-intent-authz.md)
- [docs/SANDBOXING.md](SANDBOXING.md) (companion)
