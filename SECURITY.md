# Security Policy

## Versiones soportadas

X-DD está en pre-release (v0.1.0-dev). Soporte activo solo para `main`.

| Versión | Soportada |
|---------|-----------|
| `main` (latest) | ✅ |
| `< v0.1.0` | ❌ (no existe release oficial aún) |

Tras el release de v0.1.0, las versiones soportadas se actualizarán aquí.

## Reporte de vulnerabilidades

**NO abras un issue público para vulnerabilidades de seguridad.**

### Cómo reportar

1. **Email:** `placencia.menares+xdd-security@gmail.com` (o cualquier otro canal que
   indique el maintainer en su perfil GitHub).
2. **GitHub Security Advisory:** https://github.com/Cucholambr3ta/x-dd/security/advisories/new
   (preferido, queda privado con auditoría).

### Qué incluir

- Descripción de la vulnerabilidad
- Pasos para reproducir (PoC mínimo)
- Impacto estimado
- Versión / commit hash afectado
- Sugerencia de mitigación (opcional)

### Qué esperar

| Etapa | SLA |
|-------|-----|
| Acuse de recibo | < 72 horas |
| Triage inicial + assessment | < 1 semana |
| Fix + advisory público | varía según severidad (24h crítico, 30d bajo) |
| Credit en advisory | Sí (a menos que pidas anonimato) |

## Modelo de amenazas

X-DD mantiene un modelo STRIDE completo en
[`.xdd/spec/THREATS.md`](.xdd/spec/THREATS.md):

- **23 amenazas tipificadas** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- **5 vectores específicos de sistemas IA-driven** (prompt injection vía workflow externo, hook ejecutando script malicioso, agente filtrando secretos al MCP, gate keeper sin firma, version pinning peligroso).

Mitigaciones implementadas a v0.1.0 (11/11 críticas) — ver [`.xdd/qa/QA_REPORT.md`](.xdd/qa/QA_REPORT.md) sección Seguridad.

## Hardening recomendado para usuarios de X-DD

### 1. Activar gate keeper con HMAC

Desde Sprint 4, el gate keeper firma cada `APROBADO` con HMAC-SHA256. Activar:

```bash
python3 scripts/xdd-gate.py init  # genera .xdd/.gate-key (gitignored)
```

Nunca commitees `.xdd/.gate-key`. El `.gitignore` del repo ya lo excluye, pero
si por error lo commiteas: **rotar inmediatamente** (`SECURITY.md` documenta el
flujo en `docs/GATE.md`).

### 2. Activar hooks de seguridad

```bash
export XDD_HOOK_PROFILE=strict  # activa todos los hooks defensivos
```

Esto incluye `pre:bash:dangerous-command` (bloquea `rm -rf /`, force pushes,
fork bombs, etc.) y `pre:edit:config-protection` (bloquea modificar linters).

### 3. CI con gitleaks + shellcheck + secret scanning

Ya configurado en `.github/workflows/`. Branch protection rules deben requerir
estos checks antes de merge.

### 4. MCP server: no exponer a internet

El `xdd-mcp-server` está diseñado para stdio local. **No** corras en TCP/SSE
expuesto a internet sin autenticación. Si necesitás eso, abrí issue para
discutir.

### 5. Aprobaciones requieren humano explícito

Por diseño (T6.1), `xdd-gate.py approve` requiere `--approver NAME` o
`XDD_APPROVER` env. **Nunca delegues esto a un agente IA**. La firma vale solo
si el aprobador es real.

## Vulnerabilidades conocidas

Ninguna a la fecha (`2026-05-26`). Tras release v0.1.0, este apartado listará
CVEs históricos.

## Dependencias auditadas

Ver [`DEPENDENCIES.md`](DEPENDENCIES.md). Renovate (`.github/renovate.json`) tiene
`vulnerabilityAlerts: enabled` para actualizar automáticamente con etiqueta
`security`.

## Acknowledgments

Hall of Fame de reporters de vulnerabilidades (post-v0.1.0).

## Licencia

Esta política está bajo MIT (igual que el repo).
