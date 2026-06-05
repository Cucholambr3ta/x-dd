---
description: Ejecución de revisión por pares concurrente y validación estratificada (Tiers 1-3) para garantizar la excelencia técnica y estética antes de la entrega.
---

# /qa-review

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-010 | **Versión:** 2.3.0 | **Nivel:** Táctico
**Mission:** Ejecución de revisión por pares concurrente y validación estratificada (Tiers 1-3) para garantizar la excelencia técnica y estética antes de la entrega.

**Agentes Asignados:** Swarm de QA (04) (3 clones: Seguridad, Calidad, Documentación)
**Skills Requeridas:** `skill-security-auditor.md`, `skill-code-audit.md`, `skill-technical-documentation.md`, `skill-qa-review-details.md`, `skill-workflow-asset-protocol.md`, `skill-advanced-evaluation.md`, `skill-visual-diff.md`
**Cultura:** Peer Review Concurrente · Calidad Colectiva · Zero Defect Policy · Tiered Validation


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
## 1. MISIÓN DEL FLUJO

Este workflow ejecuta una **revisión por pares concurrente** con un sistema de validación estratificado por costo y velocidad. El principio fundamental es capturar el 95% de los errores gratis mediante automatización (Tiers 1-2) y reservar el LLM (Tier 3) para juicios de calidad semántica.

## 2. TEST TIERS (QA REVIEW)

| Tier | Qué | Costo | Velocidad |
| :--- | :--- | :--- | :--- |
| **Tier 1 — Estático** | Linters, análisis de tipos, tests unitarios. | Gratis | <30s |
| **Tier 2 — QA Funcional** | Tests E2E, integración, verificación visual. | ~0-1 USD | ~5-20min |
| **Tier 3 — LLM-as-judge** | Calidad de código, coherencia SAD, docs. | ~$0.15-0.5 | ~1-2min |

## 3. FLUJO OPERATIVO (SINOPSIS)

El detalle técnico y las fases operativas se encuentran en `skill-qa-review-details.md`.

### 3.1 Invocación y Roles (Orchestrator)

Carga del Swarm de QA (04) con roles específicos de Seguridad, Calidad y Documentación.

### 3.2 Tier 1: Validación Estática (Paralelo)

Ejecución de SAST, linters y validación de frescura de documentación. Hallazgos críticos bloquean el PR inmediatamente.

### 3.3 Tier 2: QA Funcional (Sandbox)

Pruebas DAST y E2E en entorno sandbox Docker contra los criterios de aceptación de la fase. **Validación de Interoperabilidad:** Verificar que los contratos establecidos en `FLUJO_001` y `FLUJO_061` se cumplen visual y funcionalmente.

### 3.4 Tier 3: LLM-as-Judge y Consolidación

Evaluación semántica, generación de reportes NDJSON y actualización del README. Scores bajos generan deuda técnica documentada.

## 4. PROTOCOLO DE ACTIVOS

La persistencia de hallazgos y reportes debe seguir el estándar en `skill-workflow-asset-protocol.md`. La evidencia atómica completa se almacena en `tests/results/qa_${runId}.ndjson`.

## 5. RESULTADOS ESPERADOS — atomico por tier (ADR-0050)

El reporte consolidado se atomiza en 1 doc por tier. La evidencia NDJSON ya es atomica
(1 finding por linea) y queda intacta.

```
tests/results/
  qa_${runId}.ndjson           UNCHANGED (evidencia atomica — 1 finding/linea)
  qa_${runId}/
    INDEX.md / INDEX.json      (resumen + links a los 3 tiers)
    tier1-estatico.md          (SAST, linters, type checks)
    tier2-funcional.md         (E2E, integration, visual)
    tier3-llm-judge.md         (calidad semantica, consistencia)
  qa_${runId}_latest.md        → agregado generado (compat, concat de los 3 tiers)
```

| Artefacto | Destino | Formato | Atomicidad |
| :--- | :--- | :--- | :--- |
| Tier 1 estatico | `tests/results/qa_${runId}/tier1-estatico.md` | Markdown | atomo |
| Tier 2 funcional | `tests/results/qa_${runId}/tier2-funcional.md` | Markdown | atomo |
| Tier 3 LLM-judge | `tests/results/qa_${runId}/tier3-llm-judge.md` | Markdown | atomo |
| Indice del run | `tests/results/qa_${runId}/INDEX.md` + `.json` | Markdown+JSON | indice |
| Reporte consolidado | `tests/results/qa_${runId}_latest.md` | Markdown | agregado generado |
| Evidencia atomica | `tests/results/qa_${runId}.ndjson` | NDJSON | atomo (1 finding/linea) |
| Estado del Proyecto | `README.md` | Markdown | — |

> La copia gate `.xdd/qa/QA_REPORT.md` queda UNCHANGED (agregado valido para check_secdd
> + HMAC). Solo se atomiza el rich tree en `tests/results/`. Verificar:
> `python3 scripts/xdd-discipline-check.py folder --kind qa --path tests/results/qa_${runId}`

## 6. CONEXIONES DE INTEROPERABILIDAD (ART. 6)

- **Predecesores:** `FLUJO_056` (Quality Validation), `FLUJO_009` (Fase Inicio).
- **Sucesores:** `FLUJO_011` (Fase Término), `FLUJO_018` (Deploy Prod).
- **Skills Vinculadas:** `skill-qa-review-details`, `skill-advanced-evaluation`, `skill-visual-diff`.

---

**Versión:** 2.3.0 (Art. 6 Compliant)
**Fecha:** 2026-03-20

```text
X-DD System
```


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.