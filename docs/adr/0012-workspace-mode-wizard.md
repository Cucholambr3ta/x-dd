# ADR-0012 — Workspace mode + Wizard interactivo

**Date:** 2026-05-27
**Status:** Accepted
**Sprint:** 14

## Context

X-DD inicialmente asume 1 proyecto = 1 directorio. Realidad: equipos modernos trabajan en **workspaces** (VSCode workspaces, JetBrains modules, Nx/Turborepo) con N proyectos relacionados pero independientes.

Además, `xdd-init.sh` requiere conocer perfiles, profile.yml schema y branding upfront. Barrera para adopters nuevos.

Dos problemas distintos pero compartiendo solución: **superficie de adopción**.

## Decision

Se introducen dos features acopladas en Sprint 14:

### 1. Workspace mode (opt-in via xdd.profile.yml)

```yaml
workspace:
  enabled: true
  root: "/abs/path"
  shared_memory: true       # ~/.xdd/state.db compartido
  shared_gate_key: false    # cada proyecto su propia .gate-key (default)
  projects:
    - name: "api"
      path: "./api"
      profile: "developer"
    - name: "web"
      path: "./web"
      profile: "core"
```

**Semántica:**
- `workspace.enabled=false` (default) → comportamiento legacy (1 proyecto)
- `workspace.enabled=true` → X-DD reconoce N proyectos. Workflows pueden invocarse en cualquiera vía `--project=<name>`
- `shared_memory=true` → `~/.xdd/state.db` global → instincts atraviesan proyectos
- `shared_gate_key=false` → cada proyecto tiene su `.gate-key` independiente (default seguro)

### 2. Wizard interactivo (`xdd-wizard.sh`)

Script bash que guía al usuario por 7 pasos:
1. Destination path
2. Profile (minimal/core/developer/security/research/full)
3. Workspace mode (single vs multi-project)
4. Branding (default X-DD vs custom)
5. Persona si custom (technical/friendly/casual/formal)
6. Compact level si custom (off/lite/standard/ultra)
7. Confirmación → invoca `xdd-init.sh` + opcionalmente `xdd-brand.sh`

**Flag `--non-interactive`:** acepta defaults silenciosamente (útil para CI/tests).

## Alternatives considered

- **Workspace = nuevo CLI separado (`xdd-workspace`):** rechazado. Acopla mal con xdd-init + duplica config parsing.
- **Wizard solo via TUI (curses/dialog):** rechazado. Dependencia extra (`dialog`/`whiptail` no garantizado). Bash puro = portable Linux/macOS/WSL.
- **Workspace con `~/.xdd/workspaces/` registry global:** rechazado. Viola portabilidad (Art. 9). Workspace vive en su propio profile.yml.

## Consequences

### Positivas
- ✅ Barrera de entrada baja: `bash scripts/xdd-wizard.sh` reemplaza necesidad de leer 3 archivos de docs
- ✅ Workspace soporta monorepos parcialmente (Sprint 15 lo completará con 3 modos)
- ✅ Schema extensible: `workspace:` aditivo, no rompe profile.yml existentes
- ✅ Default seguro: `shared_gate_key=false` evita compartir secretos entre proyectos

### Negativas
- ⚠️ Wizard sin TUI rica = UX text-mode (aceptable tradeoff por portabilidad)
- ⚠️ Workspace mode no implementa todavía routing de workflows por proyecto — workflow runtime asume proyecto único (deferred a Sprint 15)
- ⚠️ `shared_memory=true` puede generar cross-talk de instincts entre proyectos diferentes (mitigado por TF-IDF clustering Sprint 16)

## Related

- ADR-0011 White-labeling policy (branding heredado por wizard)
- ADR-0013 Monorepo 3 modos (Sprint 15, extiende workspace mode)
- T6.1 Aprobación humana obligatoria (wizard NO hace cambios destructivos sin confirm)

## References

- VSCode workspaces: https://code.visualstudio.com/docs/editor/workspaces
- Nx monorepo: https://nx.dev
