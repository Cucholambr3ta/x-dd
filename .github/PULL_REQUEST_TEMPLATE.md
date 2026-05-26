# Pull Request

## Summary

(Una frase. Qué cambia y por qué.)

## Cambios

- ...
- ...

## Tipo

- [ ] feat (nueva capacidad)
- [ ] fix (bug fix)
- [ ] docs (solo documentación)
- [ ] refactor (sin cambio funcional)
- [ ] test (solo tests)
- [ ] chore (CI, build, deps, trazabilidad)

## Sprint / tarea MEJORAS

- Sprint N.M / Tarea X.Y (si aplica): ...

## Checklist (X-DD)

- [ ] **Tests verdes:** `bats tests/bats/` + `pytest tests/` + `bats tests/e2e/`
- [ ] **Lint limpio:** `bash scripts/lint-workflows.sh` + `bash scripts/xdd-doctor.sh`
- [ ] **Conventional commit:** `feat(scope): ...` enforced por commitlint
- [ ] **ADR creado** si introduce decisión arquitectónica
- [ ] **Lección registrada** en `lecciones.md` si hubo gotcha
- [ ] **/cierre-fase ejecutado** (memoria.md + lecciones.md actualizados)
- [ ] **/xdd-trace ejecutado** (PROJ-MASTER-PLAN.md + docs/CHANGELOG.md actualizados)
- [ ] **Sin secretos** (gitleaks verifica en CI)
- [ ] **Sin rutas absolutas del host** (Portabilidad Absoluta)
- [ ] **CI verde:** 5 workflows (shell, markdown, gitleaks, validate-prompts, lint-commits)
- [ ] **Gate keeper:** si modifiqué artefactos de fase aprobada, re-aprobé con `xdd-gate.py approve --phase X`

## Test plan

```bash
# Comandos que el reviewer puede correr para verificar
make doctor
make lint
bats tests/bats/
python3 -m pytest tests/ -q
```

## Screenshots / output

(Si aplica.)

## Related issues / ADRs

(Linkeá issues, ADRs, PRs relacionados.)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
