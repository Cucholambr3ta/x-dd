# ADR-0002: `xdd.profile.yml` y `xdd.config.yml` coexisten sin overlap

- **Fecha:** 2026-05-26
- **Estado:** Aceptado
- **Decidido por:** Alejandro Placencia, Claude

## Contexto

El retrofit anterior introdujo `xdd.profile.yml` (perfil del producto: saas/mobile/lib/internal + stacks). MEJORAS-X-DD.md v1.1 propone `xdd.config.yml` (MemPalace, pipeline, agents, ide_adapters).

Hay overlap potencial si ambos coexisten sin política clara.

## Decisión

**Coexisten con separación semántica estricta:**

- `xdd.profile.yml` = **declarativo, estable**. Responde "qué soy": perfil de producto, stacks declarados, capabilities activadas.
- `xdd.config.yml` = **operacional, puede cambiar**. Responde "cómo me ejecuto": versión de MemPalace, triggers, gates, paths de indexación, MCP, runtime.

Ningún campo se duplica entre ambos.

## Alternativas consideradas

| Opción | Pro | Contra | Por qué descartada |
|--------|-----|--------|---------------------|
| Fusionar todo en `xdd.config.yml` | Un solo archivo | Mezcla concerns muy distintos; profile cambia raramente y config cambia con cada bump de MemPalace | Difícil de versionar y migrar |
| Mantener solo `xdd.profile.yml` (postergar config) | Cero archivos nuevos | Pierde toda la centralización de comportamiento operacional | Bloquea Sprint 3 |
| Renombrar profile a config | Convención común OSS | Rompería proyectos existentes que ya tienen `xdd.profile.yml` | Plenamente evitable |

## Consecuencias

- **Positivas:** cada archivo tiene un único motivo para cambiar. Schemas independientes. Versionado independiente.
- **Negativas / Trade-offs:** dos archivos en raíz del proyecto consumidor. Aceptable: ambos tienen `# yaml-language-server` directive.
- **Neutras:** `xdd-doctor.sh` debe validar ambos.

## Plan de revisión

Revisitar para v0.2.0 si emerge un tercer archivo (`xdd.secrets.yml`?) — entonces formalizar `xdd.*.yml` como familia.
