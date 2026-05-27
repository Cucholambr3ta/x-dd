# ADR-0020 — Community skills voting policy (7-day window)

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 16

## Context

Sprint 9 (continuous learning) + `/evolve` propone nuevas skills/agents desde instincts del usuario. Sprint 16 (TF-IDF clustering) mejora la calidad de propuestas.

Pero adopters de X-DD (proyectos consumidores) pueden contribuir skills upstream al repo X-DD. Sin política, riesgos:
- Skills duplicadas o de baja calidad
- Skills sin licencia clara
- Skills con dependencias pesadas no declaradas
- Skills que rompen invariantes del framework

Inspiración: Gentleman-Skills voting policy (7-day community window).

## Decision

X-DD adopta política de **voto comunitario 7 días** para skills contribuidas externamente:

### Proceso de contribución de skill

1. Contributor abre PR con:
   - `skills/<name>/SKILL.md` (frontmatter completo con `origin`, `inspired_by`, `category`, `triggers`)
   - Entry nueva en `prompts/skills/registry.json`
   - Tests si aplica (`evals/<name>/cases.jsonl + grader.yaml`)
   - Sección "Justificación" en cuerpo del PR

2. **Ventana de 7 días naturales** (168h) para review comunitario.
   - Anuncio automático en GitHub Discussions (`community-skills` category)
   - Anuncio en Slack/Discord opcional (`#xdd-skills-voting`)

3. **Votos requeridos para merge:**
   - Mínimo **3 approvals** de maintainers core (CODEOWNERS)
   - Cualquier veto explícito de maintainer core = block
   - 0 vetos = puede mergear pasadas las 168h

4. **Criterios de evaluación:**
   - ✅ Licencia compatible (MIT, Apache-2.0, ISC; rechazo: GPL, AGPL salvo wrapper externo aprobado)
   - ✅ Sin dependencias nuevas no declaradas
   - ✅ Frontmatter completo + descripción clara
   - ✅ No duplica skill existente (revisión cruzada de `triggers` y `category`)
   - ✅ Pasa lint (`scripts/lint-workflows.sh` extendido a skills)
   - ✅ Si tiene `evals/`, los grader tests pasan

### Proceso de skill auto-generada por /evolve

1. `/evolve --generate` crea propuesta en tabla `evolutions` (status=`proposed`)
2. Humano del proyecto consumidor aprueba localmente → status=`approved` en su SQLite local
3. **Si el proyecto consumidor decide contribuir upstream:**
   - Exporta skill via `xdd-state.py export-skill <evolution-id> > skills/<name>/SKILL.md`
   - Abre PR siguiendo proceso de contribución (igual que externos)
   - Ventana 7 días + 3 approvals

### Skills tipo `core` (no community)

Skills marcadas con `origin: "x-dd"` en registry NO pasan por voting comunitario — son del framework. Cambios a ellas requieren ADR formal + voto unánime de maintainers.

## Alternatives considered

- **0 política:** rechazado. Frameworks con skills marketplace sin curación degradan (caso ECC: 246 skills, calidad heterogénea).
- **Curación exclusivamente maintainer:** rechazado. Cierra demasiado a contribuciones externas.
- **Ventana 14 días:** considerada pero rechazada por demasiado lenta para el ciclo agéntico.
- **2 approvals en vez de 3:** rechazado. 3 reduce sesgo individual.

## Consequences

### Positivas
- ✅ Calidad de skill base community = predecible
- ✅ Contributors externos tienen path claro a merge
- ✅ Maintainer overhead acotado (3 approvals, no review exhaustivo unilateral)
- ✅ Compatible con `/evolve` outputs (mismo proceso para skills generadas)

### Negativas
- ⚠️ 7 días puede sentir slow para contributors. Mitigación: maintainers pueden fast-track críticos
- ⚠️ Skills que dependen de provider específico (OpenAI, etc.) requieren disclaimer explícito
- ⚠️ CODEOWNERS debe mantenerse activo (3 maintainers core min para que voting funcione)

## Implementation

- `.github/CODEOWNERS` declara owners de `skills/` y `prompts/skills/registry.json`
- `.github/ISSUE_TEMPLATE/community-skill.md`: template para proponer skill nueva
- `.github/PULL_REQUEST_TEMPLATE/skill.md`: PR template con checklist
- `docs/CONTRIBUTING.md`: sección "Contributing skills" linkea a este ADR

## Related

- ADR-0014 SDD parity (constitution.md template menciona governance)
- Sprint 10 (skills system + eval-harness)
- Sprint 9 + /evolve (origen de skills auto-generadas)
- Gentleman-Skills: https://github.com/gentleman-org/gentleman-skills

## References

- Apache Software Foundation voting: https://www.apache.org/foundation/voting.html
- CODEOWNERS spec: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
