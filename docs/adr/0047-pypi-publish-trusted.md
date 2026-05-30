# ADR-0047: Publicación en PyPI vía Trusted Publishing (OIDC)

**Estado:** Aceptada
**Fecha:** 2026-05-30
**Sprint:** 33
**Decisores:** Alejandro Placencia + Orquestador X-DD

---

## Contexto

ADR-0043 dejó X-DD empaquetable (`python -m build` produce sdist + wheel válidos,
`twine check` PASSED). Falta automatizar la **publicación** para que `pip install x-dd`
funcione sin clonar el repo. La pregunta es cómo autenticar el publish de forma segura.

## Decisión

**Publicar vía un workflow de GitHub Actions usando Trusted Publishing (OIDC), sin tokens
de PyPI en secrets.**

- `.github/workflows/pypi-publish.yml` se dispara con tags `v*.*.*`.
- **Tag pre-release** (`-dev`/`-rc`/`-alpha`/`-beta`) → **TestPyPI**.
- **Tag estable** (`vX.Y.Z` sin sufijo) → **PyPI**.
- Job `build` produce sdist+wheel y corre `twine check`; los jobs de publish usan
  `pypa/gh-action-pypi-publish` con `id-token: write` (OIDC).
- Requisito de configuración una vez: registrar el *trusted publisher* en (Test)PyPI
  apuntando a este repo + workflow + environment (`testpypi` / `pypi`).

OIDC > token: no hay secreto de larga vida que rotar ni que se pueda filtrar; el permiso
se acota al workflow y environment concretos.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Trusted Publishing OIDC (elegida) | Sin secretos; permiso acotado | Setup inicial en PyPI | — |
| API token en GitHub secrets | Simple | Secreto de larga vida; superficie de fuga | Peor postura de seguridad |
| Publish manual con `twine upload` | Cero CI | Manual, propenso a error, requiere token local | No reproducible |

## Consecuencias

- **Positivas:** `pip install x-dd` desde PyPI tras un tag estable; pre-releases probables
  en TestPyPI; cero secretos de PyPI en el repo.
- **Trade-offs:** el primer publish requiere configurar el trusted publisher (paso manual
  único en la web de PyPI). El publish real ocurre en el tag del release, no en esta PR.
- **Neutras:** el workflow no corre hasta que exista un tag `v*.*.*`.

## Relación

- **Construye sobre:** ADR-0043 (pip-installable), ADR-0045 (comando global).
- **Coordina con:** `release.yml` (GitHub Release) — ambos se disparan por el mismo tag.
