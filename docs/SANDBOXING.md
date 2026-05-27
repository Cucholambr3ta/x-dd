# Sandboxing — X-DD (Sprint 21)

Provider-agnostic skill `xdd-sandbox` con 5 backends.

## Backends soportados

| Backend | License | Setup | Best for |
|---|---|---|---|
| `e2b` | Apache-2.0 | `pip install e2b` + API key | Cloud sandbox + browser/desktop |
| `daytona` | Apache-2.0 | Daytona instance | Dev environments AI-generated |
| `microsandbox` | MIT | rootless VM tool | Local privacy-first |
| `docker` | Apache-2.0 | docker daemon | Quick container isolation |
| `none` | - | - | Disable (NOT recommended prod) |

## Config (xdd.config.yml)

```yaml
sandbox:
  backend: docker
  default_image: "python:3.12-slim"
  network: deny            # deny | allow_localhost | full
  cpu_limit: "1.0"
  mem_limit: "512m"
  timeout_sec: 30
  auto_for_intents:
    - lang_exec
    - filesystem_delete
    - fork_subprocess
```

## Flow

1. Tool call → `xdd-intent classify` → severity ≥ threshold
2. Si match con `auto_for_intents` → wrap en sandbox backend
3. Backend ejecuta, captura output, retorna
4. Combinable: `xdd-authz require_approval` → humano confirma → sandbox ejecuta

## Boundaries

- ❌ Sandbox ≠ authz. Authz decide IF; sandbox decide HOW.
- ❌ `network: full` deshabilita beneficio principal.
- ✅ `network: deny` para code untrusted.
- ✅ Recomendable mínimo `docker` para prod.

## Implementación pendiente

v0.1.0 = spec + skill SKILL.md. Implementación per-backend → v0.2.0.

## Referencias
- [ADR-0027 Sandbox provider abstraction](adr/0027-sandbox-provider-abstraction.md)
- [skills/xdd-sandbox/SKILL.md](../skills/xdd-sandbox/SKILL.md)
- [docs/PERMISSIONS.md](PERMISSIONS.md)
