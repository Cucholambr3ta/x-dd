# ADR-0006: Gate keeper con firma HMAC-SHA256

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

El plan base de MEJORAS-X-DD.md (Tarea 2.2) propone que `xdd-gate.py approve` escriba el string `"APROBADO"` en `.xdd/<fase>/.status`. **Problema crítico:** ese string es trivialmente editable por cualquiera con acceso al repo (o por el propio agente que pasa el gate). El "gate" sería convención, no enforcement.

Sin un mecanismo de integridad, X-DD no se distingue de "carpetas con nombres convencionales".

## Decisión

**Cada `approve` calcula HMAC-SHA256 sobre el tuple `(phase, sorted_checksums, approver, timestamp_utc_iso)` usando una clave secreta local en `.xdd/.gate-key` (gitignored, generada al primer `xdd-gate.py init`).** La firma se escribe en `.xdd/<fase>/.signature`.

Cada `validate` recalcula y compara. Cualquier alteración manual de `.status`, `.checksums`, `.approvers` o de los artefactos de fase invalida la firma.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Sin firma (solo `.status`) | Simplísimo | Cero enforcement | Anula el valor del gate |
| Firma GPG con clave del aprobador | Standard de la industria | Setup pesado para usuarios casuales; requiere keyring | Sobre-engineering para v0.1.0 |
| Sigstore / cosign | Cadena de confianza pública | Requiere infraestructura externa | Out of scope |
| Hash sin clave (solo SHA-256) | Sin secreto a gestionar | Cualquiera puede recalcular y reescribir | Inseguro |
| Firma en commit git (signed tag por fase) | Aprovecha git native | Requiere tag por fase; ruidoso en historia | Posible para v0.2.0 |

## Consecuencias

- **Positivas:** "APROBADO" es auditable. Diferenciador real vs frameworks de proceso "convencional".
- **Negativas / Trade-offs:** la `.gate-key` debe ser respaldada por el equipo (perderla invalida todas las firmas existentes). Mitigación: documentar en `SECURITY.md` cómo rotar.
- **Neutras:** `.gate-key` se genera con `secrets.token_bytes(32)`.

## Plan de revisión

Revisitar para v0.2.0 si la comunidad pide firma GPG / Sigstore (caso enterprise/compliance).
