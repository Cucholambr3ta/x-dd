# Branding & White-labeling — X-DD

> Sprint 13. Permite a orgs renombrar la instancia X-DD instalada en su proyecto
> sin tocar el framework upstream. Implementa [ADR-0011](adr/0011-white-labeling-policy.md).

## Quick start

Agregá sección `branding` a tu `xdd.profile.yml`:

```yaml
profile: saas

branding:
  ecosystem_name: "Helios"
  ecosystem_slug: "helios"
  orchestrator_trigger: "helios"
  orchestrator_persona:
    tone: "friendly"
  output:
    compact: "standard"
```

Aplicalo:

```bash
bash scripts/xdd-brand.sh /ruta/a/tu/proyecto
```

Resultado:
- Slash command `/helios` disponible (symlink a workflow xdd.md original)
- Persona "friendly" cargada en `.claude/orchestrator-persona.md`
- `.claude/branding.json` con la config aplicada
- Sub-workflows siguen siendo `/xdd-build`, `/xdd-trace`, etc. (por discoverability)

## Configuración completa

Ver [`templates/xdd.profile.with-branding.yml`](../templates/xdd.profile.with-branding.yml) con todas las opciones.

| Campo | Tipo | Default | Efecto |
|---|---|---|---|
| `ecosystem_name` | string | "X-DD" | Aparece en banners, outputs, prompts |
| `ecosystem_slug` | string | "xdd" | Prefijos técnicos (paths internos) |
| `orchestrator_trigger` | string | "xdd" | Slash command principal (`/xdd` → `/<trigger>`) |
| `rename_subworkflows` | bool | false | Si true: `/helios-build`, `/helios-trace`, etc. |
| `orchestrator_persona.tone` | enum | "technical" | technical / friendly / casual / formal / custom |
| `orchestrator_persona.custom_prompt` | path | null | Si tone=custom, path al .md propio |
| `output.compact` | enum | "off" | off / lite / standard / ultra (Sprint 10 xdd-talk-compact) |
| `attribution_required` | bool | true | README menciona "powered by X-DD" |

## 4 Personas presets

| Persona | Ejemplo cierre de sprint |
|---|---|
| `technical` | "Sprint 4 cerrado. 17/17 tests passed. Gate firmado HMAC. Continúa con Sprint 5." |
| `friendly` | "✨ ¡Cerramos Sprint 4! Los 17 tests pasaron y el gate quedó firmado con HMAC. ¿Arrancamos Sprint 5?" |
| `casual` | "Listo el sprint 4 ✅. Tests verdes, gate firmado, branch ok. ¿Vamos al 5?" |
| `formal` | "Se ha completado la fase 4. La suite de pruebas (17 casos) ha sido ejecutada satisfactoriamente. Procédase a la fase 5." |
| `custom` | Tu prompt — path en `orchestrator_persona.custom_prompt` |

## 3 ejemplos de organización

### Startup casual

```yaml
branding:
  ecosystem_name: "RocketShip"
  ecosystem_slug: "rocket"
  orchestrator_trigger: "rocket"
  orchestrator_persona:
    tone: "casual"
  output:
    compact: "ultra"
```

→ `/rocket` + ultra-compressed casual responses.

### Fintech regulada

```yaml
branding:
  ecosystem_name: "Helios-Compliance"
  orchestrator_trigger: "helios"
  orchestrator_persona:
    tone: "formal"
  output:
    compact: "standard"
  attribution_required: true
```

→ `/helios` + responses corporativas estándar + atribución X-DD upstream.

### Consultora dev

```yaml
branding:
  ecosystem_name: "DevOps-Engine"
  orchestrator_trigger: "deveng"
  orchestrator_persona:
    tone: "technical"
  output:
    compact: "lite"
```

→ `/deveng` + technical + lite (sin filler pero gramática completa).

## Lo que SÍ y NO se puede rebrandear

| Permitido (instance Helios) | NO permitido (X-DD upstream) |
|---|---|
| Slash commands en `.claude/commands/` | El nombre del repo X-DD |
| Outputs de scripts custom | El field `name: x-dd` en `agent.yaml` |
| Persona del orquestador | Atribuciones en `NOTICE` |
| Banners en docs del proyecto | Referencias en `docs/adr/` |
| README del proyecto consumidor | `MEJORAS-X-DD.md` (es del framework) |

## Atribución default

`attribution_required: true` por default agrega al README del proyecto consumidor:

```markdown
*Powered by [X-DD framework](https://github.com/Cucholambr3ta/x-dd) (MIT). Instance: Helios.*
```

Si tu org decide `attribution_required: false`, lo permitimos por compatibilidad pero
ADR-0011 declara la atribución como "fuertemente recomendada" para repos OSS derivados.

## Combinación con Sprint 14 (workspace mode)

Cuando Sprint 14 esté listo, podés combinar:

```yaml
# en xdd.config.yml de tu workspace
workspace:
  enabled: true
  central_path: "~/.xdd-central"

# en xdd.profile.yml del workspace
branding:
  ecosystem_name: "Helios"
  orchestrator_trigger: "helios"
```

→ Workspace `helios` symlinkado a `~/.xdd-central` con `/helios` trigger y persona propia.

## Diferencias vs ECC

ECC tiene white-labeling parcial. X-DD lo formaliza con:
- Schema validable
- Política inmutable explícita (ADR-0011)
- 4 personas presets + custom
- Combinable con `xdd-talk-compact` en matriz 4×4
- Atribución por default a upstream

## Roadmap

- v0.1.0 (Sprint 13, este): branding + 4 personas + rename solo trigger principal.
- v0.2.0 candidatos: i18n del orquestador (multi-language), branding visual (logos para web UI futura), GPG-signed persona declarations (auditable).
