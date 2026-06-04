---
description: Define el contrato API (OpenAPI/AsyncAPI/GraphQL SDL) en Fase 2. Genera openapi.yaml + stubs Pact.
---
# /api-contract

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-API | **Versión:** 1.0 | **Agente:** Backend-Architect + API-Tester
**Misión:** Convertir requisitos en un contrato API formal y versionado, antes de codificar.

## 0. Pre-flight
- Requiere `SPEC.md` y `DOMAIN.md` ya aprobados.
- Verifica si existe `openapi.yaml` previo → modo diff/migración.

## 1. Estilo de API
Pregunta y registra como ADR:
- **REST** (default para CRUD) | **GraphQL** (queries complejas / clientes diversos) | **gRPC** (servicios internos high-throughput) | **AsyncAPI** (eventos / colas).

## 2. Convenciones
- Versionado: URL (`/v1/`), header (`Accept-Version`), o ambos. Documenta deprecación.
- Errores: RFC 7807 (Problem Details) o esquema propio documentado.
- Auth: OAuth2 / API Key / mTLS (referencia `THREATS.md`).
- Paginación: cursor (default) o offset.
- Idempotencia: header `Idempotency-Key` en POST con efectos.

## 3. Generación atómica — fragments + raíz mergeada (ADR-0051)

OpenAPI es el unico caso monolitico-por-formato (el tooling necesita 1 raiz valida).
Por eso los recursos se editan de forma atomica y la raiz se GENERA.

```
api/openapi/fragments/
  _root.yaml           (metadata: openapi, info, servers)
  INDEX.md / INDEX.json
  <recurso>.yaml       (paths + components de UN recurso: users.yaml, orders.yaml...)
openapi.yaml           → RAIZ GENERADA (no editar a mano)
```

Pasos:
1. Escribe un fragmento por recurso en `api/openapi/fragments/<recurso>.yaml`
   (solo sus `paths` y `components.schemas`).
2. Mergea a la raiz:
   ```bash
   python3 scripts/xdd-openapi-merge.py merge --fragments api/openapi/fragments --out openapi.yaml
   ```
3. Sincroniza el INDEX:
   ```bash
   python3 scripts/xdd-doc-sync.py sync-folder api/openapi/fragments
   ```
4. Genera stubs de contract tests (Pact / Dredd) en `tests/contracts/` por recurso.
5. Genera servidor mock (Prism / json-server) desde la raiz mergeada.

Para GraphQL/gRPC (que ya son spec unica): escribe `schema.graphql` / `service.proto`
en raiz directamente (no aplica fragmentacion).

<!-- CONFIGURAR: Generador. Opciones: openapi-generator, swagger-codegen, orval, kubb, stainless. -->

## 4. Linting
Corre linter sobre la RAIZ mergeada (no sobre fragmentos sueltos):
- Validacion de estructura: `python3 scripts/xdd-openapi-merge.py validate --root openapi.yaml`
- Spectral para OpenAPI con ruleset team-defined sobre `openapi.yaml`.
- GraphQL Inspector para SDL.
Falla la fase si hay errores `error` (warnings se documentan).

## 5. Trazabilidad
- Cada endpoint → una feature de `FEATURES.md` (FDD).
- Cada modelo → una entidad de `DOMAIN.md` (DDD).
- Cada amenaza relevante → mitigación documentada (Threat-Driven).

## 6. Gated (Art. 2)
Solicita `"APROBADO"` antes de:
- Cambios breaking (mayor de versión).
- Eliminación de endpoints o campos.

## 7. Cierre
- Versiona `openapi.yaml` en git.
- Registra ADR si hubo decisión arquitectónica.
- Encola `/contract-test` para Fase 5.
