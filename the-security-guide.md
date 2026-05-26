# The Security Guide to X-DD

> Modelo de amenazas + best practices SecDD + hardening + cómo X-DD se defiende
> a sí mismo. Complementa `SECURITY.md` (policy) y `.xdd/spec/THREATS.md` (modelo
> STRIDE formal).

## Filosofía SecDD

**Security-Driven Development** está embebido en X-DD, no agregado al final:

1. **STRIDE en Fase 2** (Spec) — antes de escribir código, modelar amenazas.
2. **STDD en Fase 4** (Build) — tests de seguridad **antes** de la implementación.
3. **SAST + DAST + Secrets scan en Fase 5** (QA) — gates de release.
4. **AgentShield en Fase 5** (Sprint 12) — auditoría estática del propio framework agéntico.
5. **Gate keeper firmado HMAC** — "APROBADO" auditable, no string editable.

## Threat model — STRIDE

23 amenazas tipificadas + 5 vectores específicos de sistemas IA-driven. Documento
completo: [`.xdd/spec/THREATS.md`](.xdd/spec/THREATS.md).

### Top 5 amenazas críticas y cómo se mitigan

| # | Amenaza | Categoría | Mitigación en X-DD | Verificado |
|---|---------|-----------|---------------------|------------|
| T2.1 | Edición manual de `.status` para forjar aprobación | Tampering | Firma HMAC-SHA256 sobre (phase, checksums, approver, timestamp) | `tests/test_gate.py::test_validate_detects_invalid_signature` |
| T4.3 | MCP server expone artefactos fuera de scope | Information Disclosure | Whitelist explícita `.xdd/` en `xdd_get_phase_artifacts` | `tests/test_mcp_server.py::test_get_phase_artifacts` |
| T6.1 | Agente IA aprueba fase sin permiso humano | Elevation of Privilege | `--approver` o `XDD_APPROVER` env obligatorios | `tests/test_gate.py::test_approve_requires_approver` |
| T6.3 | Tool MCP ejecuta arbitrary code | Elevation of Privilege | NO existe `xdd_exec` / `xdd_shell` en el set v0.1.0 | review estático |
| V4 | Gate keeper sin firma criptográfica (anti-patrón ECC) | (vector) | HMAC obligatorio desde Sprint 4 / ADR-0006 | testing exhaustivo |

### 5 vectores IA-driven

1. **Prompt injection vía workflow externo** — un PR con instrucciones ocultas en
   frontmatter `description:`. Mitigación: code review obligatorio + `lint-workflows.sh`.
2. **Hook ejecutando script malicioso post-commit** — Mitigación: hooks viven
   versionados en `.agent/hooks/scripts/` (auditable) + shellcheck en CI.
3. **Agente filtrando secretos al MCP server** — Mitigación: tools MCP rechazan
   strings que matchean gitleaks patterns + logging.
4. **Gate sin firma criptográfica** — Resuelto por ADR-0006.
5. **`xdd.config.yml` apunta a versión vieja de MemPalace** — Doctor v2 con
   SemVer real avisa de constraints peligrosos.

## Hardening del usuario X-DD

### Setup mínimo seguro

```bash
# 1. Profile strict (activa todos los hooks defensivos)
export XDD_HOOK_PROFILE=strict

# 2. Gate keeper inicializado
python3 scripts/xdd-gate.py init

# 3. Pre-commit + gitleaks
pip install pre-commit && pre-commit install
```

### Variables de entorno relevantes

| Var | Default | Recomendado prod | Efecto |
|-----|---------|------------------|--------|
| `XDD_HOOK_PROFILE` | `standard` | `strict` | Activa todos los hooks defensivos |
| `XDD_APPROVER` | (vacío) | tu nombre | Para gate approvals (T6.1 compliance) |
| `XDD_DISABLED_HOOKS` | (vacío) | (vacío) | NO desactivar hooks de seguridad |
| `XDD_ALLOW_CONFIG_EDIT` | `0` | `0` | NUNCA `1` en CI o prod |

### Para colaboración multi-máquina

`.xdd/.gate-key` está gitignored. Para compartir el equipo:
- **Recomendado**: 1Password / Bitwarden / vault corporativo.
- **NUNCA** por email/Slack/repo público.

### Rotación de la clave

```bash
# Backup defensivo
cp .xdd/.gate-key ~/safe/xdd-gate-key.bak.$(date +%s)

# Rotar
rm .xdd/.gate-key && python3 scripts/xdd-gate.py init

# Re-aprobar TODAS las fases (firmas viejas son inválidas)
export XDD_APPROVER="vos"
for p in briefing spec plan build qa retro; do
  test -d .xdd/$p && python3 scripts/xdd-gate.py approve --phase $p
done

# Documentar en docs/CHANGELOG.md → sección Security
```

## CI pipeline de seguridad

`.github/workflows/`:

| Workflow | Qué chequea | En cada |
|----------|-------------|---------|
| `gitleaks.yml` | Secretos en código | PR + push main |
| `lint-shell.yml` | Shellcheck sobre `**.sh` | PR + push |
| `lint-markdown.yml` | markdownlint | PR + push |
| `validate-prompts.yml` | Workflows + `--help`/`--version` en scripts | PR + push |
| `lint-commits.yml` | commitlint sobre commits del PR | PR |
| `agent-shield.yml` | Sprint 12 (futuro) — audit estático del framework | PR + push |

## Hooks defensivos críticos

Ver [`docs/HOOKS.md`](docs/HOOKS.md). Los más importantes:

### `pre:bash:dangerous-command` (PreToolUse, blocking)

Bloquea **antes de ejecutar**:
- `rm -rf /` y variantes
- `git push --force` a cualquier rama
- `git reset --hard origin/...`
- `chmod 777` recursivo
- `curl | bash` y `wget | bash`
- Fork bombs `:(){...}`
- `dd if=... of=/dev/sda`

Si necesitás uno de estos legítimamente (no debería pasar en agentes), ejecutalo
manualmente fuera del agente.

### `pre:edit:config-protection` (PreToolUse, blocking, profile strict)

Bloquea editar configs sensibles (`.markdownlint.yaml`, `.editorconfig`,
`.eslintrc*`, `pyproject.toml`, `schemas/`, etc.) sin override explícito.

**Por qué:** evita que un agente "debilite la config para que el código pase
el lint" en lugar de arreglar el código real.

Override solo en emergencias:
```bash
export XDD_ALLOW_CONFIG_EDIT=1
# ... edit ...
unset XDD_ALLOW_CONFIG_EDIT
```

## Auditoría del propio framework

X-DD se audita a sí mismo:

| Capacidad | Sprint | Estado |
|-----------|--------|--------|
| 10 ADRs Nygard | 0 | ✅ |
| THREATS.md con 23 amenazas | 1 | ✅ |
| Gate keeper firmado | 4 | ✅ |
| 97 tests verdes | 7 | ✅ |
| QA_REPORT con 11/11 mitigaciones | 7 | ✅ |
| AgentShield (audit estático del agente) | 12 | ⏳ próximo |
| SAST en CI sobre el repo | (Renovate + gitleaks) | ✅ parcial |

## Cómo reportar vulnerabilidades

Ver [`SECURITY.md`](SECURITY.md). Resumen:

- **NO** abrir issue público.
- GitHub Security Advisory (preferido): https://github.com/Cucholambr3ta/x-dd/security/advisories/new
- Email: ver `SECURITY.md`.
- SLA: acuse en 72h, fix según severidad.

## Para developers que añaden capacidades

Cualquier PR debe:

1. Pasar `gitleaks` (sin secretos).
2. No introducir rutas absolutas del host (Portabilidad Absoluta).
3. Si añade workflow/agente nuevo: pasar `lint-workflows.sh` + `validate-registry.py --strict`.
4. Si añade hook: validar contra `schemas/hooks.schema.json` + test bats.
5. Si modifica el threat model: actualizar `THREATS.md` + ADR si es decisión nueva.

## Referencias

- [`SECURITY.md`](SECURITY.md) — Policy de divulgación
- [`.xdd/spec/THREATS.md`](.xdd/spec/THREATS.md) — STRIDE completo
- [`docs/GATE.md`](docs/GATE.md) — Gate keeper detalles
- [`docs/HOOKS.md`](docs/HOOKS.md) — Hooks system
- [ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md) — Firma HMAC
- [ADR-0009](docs/adr/0009-politica-versionado-xdd-directorio.md) — Qué se commitea de `.xdd/`
