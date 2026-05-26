# ADR-0009: Política de versionado del directorio `.xdd/`

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

`.xdd/` contiene mezcla de artefactos:

- **Documentos:** `SPEC.md`, `DOMAIN.md`, `THREATS.md`, `PLAN.md`, `QA_REPORT.md`, `lecciones.md`.
- **Metadata de gate:** `.status`, `.checksums`, `.approvers`, `.signature` (uno por fase).
- **Secretos:** `.gate-key` (uno solo, raíz de `.xdd/`).

ADR-0001 establece "todo visible y commiteable" como principio general — pero `.gate-key` es secreto. Necesitamos política granular.

## Decisión

| Path | Commiteable | Motivo |
|------|-------------|--------|
| `.xdd/<fase>/*.md` | ✅ Sí | Dogfooding visible (ADR-0001). |
| `.xdd/<fase>/.status` | ✅ Sí | Auditoría pública del estado del pipeline. |
| `.xdd/<fase>/.checksums` | ✅ Sí | Permite verificar integridad sin la key (solo prueba que el contenido no cambió post-aprobación). |
| `.xdd/<fase>/.approvers` | ✅ Sí | Trazabilidad de quién aprobó y cuándo. |
| `.xdd/<fase>/.signature` | ✅ Sí | Sin la `.gate-key` la firma es opaca pero verificable por quien la tenga. |
| `.xdd/.gate-key` | ❌ **No (gitignored)** | Secreto. Compromiso permitiría reescribir firmas. |
| `.xdd/build/sprint-N/` | ✅ Sí | Sub-reportes por sprint de la Fase 4-Build. |

`.gitignore` añade explícitamente:
```
# X-DD gate keeper secret
.xdd/.gate-key
```

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Todo `.xdd/` gitignored | Máxima protección | Contradice ADR-0001; pierde dogfooding | No |
| Encriptar `.gate-key` y commitearla con passphrase | Permite recovery | UX pesada; passphrase termina en otro secret manager | Sobre-engineering |
| Usar git-crypt o age sobre `.gate-key` | Standard | Dependencia adicional | Diferir hasta v0.2.0 si hay demanda |

## Consecuencias

- **Positivas:** clara distinción público/secreto; auditoría completa sin exponer la key.
- **Negativas / Trade-offs:** equipos que comparten X-DD entre ≥2 máquinas deben compartir `.gate-key` por canal seguro (1Password, vault, etc.). Documentar en `SECURITY.md`.
- **Neutras:** `xdd-init.sh` debe escribir el patrón a `.gitignore` automáticamente.

## Plan de revisión

Revisitar si MEJORAS pide colaboración multi-máquina automatizada (compartir key sin canal externo).
