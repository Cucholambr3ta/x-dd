# ADR-0003: Python como runtime del gate keeper

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

El gate keeper (`xdd-gate.py`, Sprint 4) necesita:
- Parsear/validar JSON y JSON Schema.
- Calcular SHA-256 y HMAC-SHA256 (ADR-0006).
- Manejar fechas ISO 8601 con timezone.
- Tests unitarios robustos.

Hoy todo el tooling es Bash. Introducir Python añade dependencia, pero MemPalace (ADR-0004) ya requiere Python ≥3.9 — es dep transitiva inevitable.

## Decisión

**Python ≥3.9 como runtime del gate keeper.** Sin nuevas deps de PyPI (stdlib: `argparse`, `hashlib`, `hmac`, `json`, `pathlib`, `datetime`, `enum`).

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Bash puro | Cero deps nuevas | HMAC, JSON Schema y datetime son dolorosos en bash; tests con bats son frágiles para lógica compleja | Costo de desarrollo y mantenimiento alto |
| Node.js | Ya está como dep para tests (Vitest/Playwright) | Añade otra runtime obligatoria para usuarios que no testean en Node | Innecesario |
| Go | Binarios estáticos portables | Nueva dep no transitiva | Sobre-engineering para v0.1.0 |
| Rust | Performance + seguridad | Toolchain pesado | Misma razón que Go |

## Consecuencias

- **Positivas:** tests robustos vía pytest; manipulación JSON/HMAC directa; ya está disponible vía MemPalace.
- **Negativas / Trade-offs:** Python aparece explícito en `xdd-doctor.sh` (chequeo de versión). Mitigación: ya estaba ahí implícito por MemPalace.
- **Neutras:** habilita ADR-0008 (consolidación futura en `xdd` CLI Python).

## Plan de revisión

Revisitar si Python se vuelve barrera de adopción (poco probable: está en macOS por defecto y en toda distro Linux moderna).
