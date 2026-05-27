# ADR-0011: White-labeling policy — framework name immutable, ecosystem instance customizable

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

Las organizaciones de desarrollo (clientes potenciales de X-DD) querrían:
1. Renombrar el ecosistema instalado a su marca interna (ej. "Helios", "ACME-Pipeline")
2. Custom slash command trigger principal (`/xdd` → `/helios`)
3. Tono del orquestador adaptable a su cultura (technical / friendly / casual / formal / custom)

Pero el framework upstream tiene identidad propia (X-DD, atribuciones, licencia, ADRs).
Hay que separar **lo customizable (instancia)** de **lo inmutable (framework)**.

## Decisión

**Policy de white-labeling con frontera clara:**

### Customizable (sección `branding` en `xdd.profile.yml`)

- `ecosystem_name` (str) — aparece en outputs, banners, prompts. Default: "X-DD"
- `ecosystem_slug` (str) — usado en prefixes técnicos. Default: "xdd"
- `orchestrator_trigger` (str) — slash command principal. Default: "xdd" → `/xdd`
- `rename_subworkflows` (bool) — si true, sub-workflows también (`/helios-build`). Default: false (recomendado mantener prefix `xdd-*` para discoverability)
- `orchestrator_persona.tone` — enum: `technical | friendly | casual | formal | custom`
- `orchestrator_persona.custom_prompt` — path a .md propio si tone=custom
- `output.compact` — del Sprint 10 (`off | lite | standard | ultra`)
- `attribution_required` (bool) — default true: README del proyecto consumidor menciona "powered by X-DD"

### Inmutable (no permitido cambiar)

- Nombre del repo X-DD upstream
- `name: x-dd` field en `agent.yaml` (necesario para discovery)
- Atribuciones en `NOTICE`
- Referencias en `docs/adr/`
- `MEJORAS-X-DD.md` (es del framework upstream)
- Estructura `.xdd/<phase>/` (convención canónica)
- Nombres en ADRs históricos

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Sin white-labeling (X-DD fijo) | Cero código nuevo | Bloquea adopción enterprise con guidelines de marca propia | No |
| Rename completo (todo customizable) | Máximo flex | Pierde atribución y discoverability del framework upstream | Anti-OSS |
| Solo branding visual (ecosystem_name) | Mínimo viable | No resuelve el caso del slash trigger (issue real de los amigos del user) | Insuficiente |
| Branding completo CON sub-workflows rename por default | Total flex | Pierde el hint `xdd-*` que ayuda a descubrir framework | `rename_subworkflows: false` por default + opt-in |

## Consecuencias

- **Positivas:**
  - Enterprise adopters pueden brandear su instancia (Helios/ACME-Pipeline) manteniendo upstream limpio.
  - 4 personas presets cubren 95% de casos de uso; custom para el 5% restante.
  - Sub-workflows por default mantienen prefix `xdd-*` → "powered by X-DD" sigue siendo descubrible incluso con rename.
  - Backward-compatible: sin sección `branding` = identity X-DD estándar (default).
- **Negativas / Trade-offs:**
  - 4 personas adicionales (200-400 palabras cada una) a mantener.
  - Confusión potencial: "mi instancia es Helios, ¿pero qué es el upstream?" — mitigado por `attribution_required: true`.
- **Neutras:**
  - Sprint 14 (workspace mode) puede componerse con branding sin conflicto.

## Combinación con persona (4×3 matriz)

|  | technical | friendly | casual | formal |
|---|---|---|---|---|
| `compact: off` | default | accesible | informal | corporativo |
| `compact: lite` | sin filler | + emojis ok | menos formal | profesional concentrado |
| `compact: standard` | concise | conversacional breve | shortcuts | ejecutivo |
| `compact: ultra` | telegraphic | shortcuts emoji | caveman | conciso ejecutivo |

Cada org elige su combinación operativa según su cultura.

## Plan de revisión

Revisitar cuando:
- ≥3 issues de usuarios externos pidan custom persona pero las 4 presets no calzan → ampliar set.
- Demanda de white-labeling visual (logos, colores) — actualmente n/a porque X-DD es CLI/text.
- v0.2.0 podría agregar i18n del orquestador (multi-language).
