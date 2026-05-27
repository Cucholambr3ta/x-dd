# ADR-0017 — Web bundles para distribución de skills/agents/workflows

**Date:** 2026-05-27
**Status:** Accepted (spec only; impl v0.2.0)
**Sprint:** 17

## Context

BMAD distribuye "web bundles" — archivos auto-contenidos (zip/tarball) con skills + agents + workflows + manifest, instalables one-shot:

```
my-bundle.xddbundle
├── manifest.json
├── skills/
├── agents/
├── workflows/
└── docs/
```

X-DD hoy distribuye via clone repo + `xdd-init.sh`. No hay path para que un equipo empaquete su set de skills/agents/workflows y lo distribuya como unidad.

Caso de uso real: equipo de seguridad arma "security-bundle.xddbundle" con sus 12 skills + 8 agents custom + 3 workflows. Distribuye a otros equipos como zip.

## Decision

**v0.1.0:** spec del formato bundle + manifest schema. **No implementación runtime.**
**v0.2.0:** `xdd-bundle.py` con comandos `pack`, `verify`, `install`.

### Formato `.xddbundle` (v0.1.0 spec)

```
my-bundle.xddbundle (zip)
├── manifest.json           # required
├── skills/<name>/SKILL.md
├── agents/*.md
├── workflows/*.md
├── docs/
└── LICENSE                  # required
```

### manifest.json schema

```json
{
  "spec_version": "0.1.0",
  "name": "security-bundle",
  "version": "1.2.0",
  "author": "Security Team <sec@org.com>",
  "license": "MIT",
  "description": "Security skills + agents + workflows",
  "depends_on": {
    "xdd": ">=0.1.0",
    "mempalace": ">=3.3.0"
  },
  "contents": {
    "skills": ["xdd-ai-review", "advanced-pentest"],
    "agents": ["security-pentest-operator", "security-auditor"],
    "workflows": ["secure-isolation-ops"]
  },
  "signature": "sha256:abc123..."  // HMAC-SHA256 firmable
}
```

### CLI (v0.2.0)

```bash
xdd-bundle pack ./my-bundle/ -o my-bundle.xddbundle
xdd-bundle verify my-bundle.xddbundle   # checks signature + schema + license
xdd-bundle install my-bundle.xddbundle   # extract to skills/, agents/, workflows/
```

## Alternatives considered

- **OCI/Docker images:** rechazado. Demasiado pesado para markdown puro.
- **npm/pip packages:** rechazado. Crea acoplamiento a un ecosistema lenguaje.
- **Git submodules:** rechazado. Mala UX para usuarios no-git-fluent.
- **Implementar impl ya en v0.1.0:** rechazado. Spec primero, validar adopción antes de invertir.

## Consequences

### Positivas
- ✅ Path claro para que equipos distribuyan sus extensiones
- ✅ Manifest firmable (HMAC) + license obligatoria → seguridad supply-chain
- ✅ Compatible con community skills voting (ADR-0020): bundles externos pueden mergear al main X-DD via misma policy
- ✅ Future-proof: spec versionada, evolución compatible

### Negativas
- ⚠️ Spec sin runtime = adopción 0 hasta v0.2.0
- ⚠️ Riesgo de drift con install profiles (Sprint 7) si no se coordinan
- ⚠️ Signature validation no obligatoria todavía → para v0.2.0 será requisito

## Related
- ADR-0020 Community skills voting (bundles externos pueden contribuir upstream)
- Sprint 7 (install profiles + modules)
- ADR-0006 HMAC signature (mismo algoritmo)
- BMAD bundles: https://github.com/bmad-code-org/BMAD-METHOD
