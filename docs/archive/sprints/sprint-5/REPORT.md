# Sprint 5 — Build Report (Registry tipado de agentes)

> Fase 4-Build (3/5). El registry es la base que alimenta tanto los
> workflows (composition_patterns) como el MCP server (Sprint 6).

## Tareas MEJORAS abordadas
- **3.1** — Registry machine-readable (`registry.json` + schema).
- **3.2** — Composición jerárquica (lead + specialists).
- **Sobre-mejora:** migrator automático que parsea los 180 agentes
  existentes y genera el registry inicial (vs escribir 180 entradas a mano).

## Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| Migrator | `scripts/migrate-agents-to-registry.py` | ✅ parser YAML mínimo, kebab-case ids, ide_compat default |
| Registry | `prompts/agents/registry.json` | ✅ 180 agentes / 15 categorías / 3 patrones / 3 rules |
| Schema | `prompts/agents/registry.schema.json` | ✅ JSON Schema 2020-12 |
| Validator | `scripts/validate-registry.py` | ✅ `--strict` para id-refs |
| Generator | `scripts/generate-equipo.sh` | ✅ regenera `docs/equipo.md` desde SSoT |

## Validaciones

```bash
python3 scripts/migrate-agents-to-registry.py
# → 180 agentes generados

python3 scripts/validate-registry.py --strict
# → 180 agents OK en 15 categorías (sin id-refs rotas)

bash scripts/generate-equipo.sh
# → docs/equipo.md actualizado (auto-generado)

bash scripts/lint-workflows.sh && bash scripts/xdd-doctor.sh
# → verdes
```

## Composition patterns iniciales

| Patrón | Lead | Specialists | Orquestación |
|--------|------|-------------|--------------|
| `security_review` | `engineering-code-reviewer` | `engineering-security-engineer`, `engineering-threat-detection-engineer` | sequential |
| `feature_squad` | `product-manager` | `engineering-backend-architect`, `design-ui-designer`, `testing-test-results-analyzer` | parallel_then_sync |
| `release_train` | `project-management-studio-producer` | `testing-contract-testing-engineer`, `engineering-devops-automator`, `support-end-user-docs-writer` | sequential |

## Sobre-mejoras incorporadas

- **Migrator automático** vs escribir manualmente — el script puede re-ejecutarse cuando se añadan agentes nuevos.
- **`--strict` en validator** — detecta id-refs rotas en composition_patterns y routing_rules.
- **`docs/equipo.md` ahora es SSoT-derived** — eliminado el riesgo de drift entre código y docs.

## Aprendizajes
Ver `lecciones.md` (entradas Sprint 5: validator strict descubre refs rotas; SSoT-derived docs eliminan drift).

## Próximo paso
**Sprint 6 — MCP Server propio de X-DD ⭐**. El server consumirá `registry.json` para exponer `xdd_list_agents`.
