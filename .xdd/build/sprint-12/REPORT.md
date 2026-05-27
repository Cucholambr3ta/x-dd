# Sprint 12 — Build Report (AgentShield + Shannon dep externa + rename + ADR-0010)

> F4 ext (4/5 bloque ECC-inspired). Simplificado de 4d a ~2d por decisión:
> Shannon como dep externa AGPL (no reimpl clean-room).

## Entregables
| Artefacto | Path | Estado |
|---|---|---|
| AgentShield (audit del framework) | `scripts/xdd-shield.py` | ✅ 13 reglas, severity-based, --ci gate |
| Wrapper híbrido | `scripts/xdd-pentest.sh` | ✅ stride/audit-source/fuzz/verify/status/full |
| Agente renombrado | `prompts/agents/security/security-pentest-operator.md` | ✅ (era shannon-secops-expert) + constraints frontmatter |
| ADR | `docs/adr/0010-shannon-external-dep-pentest-operator-naming.md` | ✅ |
| Doc operativa | `docs/PENTEST.md` | ✅ guía híbrida con AGPL disclaimer |
| DEPENDENCIES.md | Updated | ✅ sección Pentesting con AGPL warning |
| ADR README index | Updated | ✅ entrada 0010 |
| Registry | Regenerado | ✅ 180 agentes (mismo count, ID cambiado) |
| Tests pytest | `tests/test_shield.py` | ✅ **10 tests verdes (102 total)** |

## AgentShield: 13 reglas v0.1.0

| Categoría | Reglas |
|---|---|
| Hooks | no_eval_exec, no_absolute_paths |
| Workflows | have_description, gate_integration |
| Registry | consistent, security_agents_have_constraints |
| MCP | no_exec, get_artifacts_whitelist |
| General | gate_key_gitignored, no_curl_pipe_bash, hooks_json_schema, dependencies_md, threats_md |

Severidad: crit / high / warning / info. `--ci` exit 1 si crit+high (o warning con `--severity=warning`).

**Audit del propio repo:** 0 crit, 0 high, 0 warning con `--severity=high` ✓

## Wrapper xdd-pentest.sh (política híbrida ADR-0010)

| Capacidad | Sin Shannon | Con Shannon |
|---|---|---|
| stride | ✓ ejecuta | ✓ |
| audit-source | ✓ ejecuta | ✓ |
| fuzz | ⚠ skip + aviso (exit 0) | ✓ delega a `shn start` |
| verify | ⚠ skip + aviso (exit 0) | ✓ delega a `shn verify` |
| status | (info) | ✓ delega a `shn status` |
| full | parcial (stride+source) | completo |

## Rename agente

- `shannon-secops-expert` → `security-pentest-operator`
- Frontmatter: nombre nuevo, description menciona delega a `shn` cuando disponible, constraints declarados (never_auto_approve_security_patches, exploit_only_in_sandboxed, delegate_dynamic_to_shn)
- Section "Naming history" en system prompt preserva atribución

## Atribución
Shannon (KeygraphHQ/shannon, AGPL-3.0) declarada en `NOTICE`, `DEPENDENCIES.md` y system prompt del agente. NO se copió código verbatim.

## Stats
- **102/102 pytest verdes** (92 + 10)
- **51 workflows** (sin cambio en S12)
- **180 agentes** (mismo count, 1 renombrado)
- **+2 scripts** propios (xdd-shield.py, xdd-pentest.sh)
- **+1 ADR** (0010)
- **AgentShield audit del repo: 0 crit/high/warning con --severity=high**

## Próximo
Sprint 13 — White-labeling (branding + 4 personas + rename trigger principal + ADR-0011).
