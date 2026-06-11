# CASOS_GHERKIN.md — Casos de Aceptacion (BDD)

> Producido por `/fase-requisitos` o `/qa-review`. Cumple `docs/DOC_STANDARD.md`.
> Vocabulario exclusivamente del DOMAIN.md (Ubiquitous Language).
> Cada feature: 1 happy path, >=1 escenario de error, >=1 caso borde.

## Feature: <FEAT-001 nombre>

Trazabilidad: FEAT-001, REQ-001, SPEC seccion 3, DOMAIN agregado <Nombre>.

```gherkin
Feature: <nombre de la feature en lenguaje de negocio>

  Background:
    Dado que el usuario esta autenticado en el rol "<rol>"

  Scenario: <happy path>
    Dado <precondicion>
    Cuando <accion>
    Entonces <resultado esperado>

  Scenario: <escenario de error>
    Dado <precondicion invalida>
    Cuando <accion>
    Entonces <error esperado>

  Scenario Outline: <caso borde multi-valor>
    Dado <precondicion con "<entrada>">
    Cuando <accion>
    Entonces <resultado "<salida>">

    Examples:
      | entrada | salida |
      | <v1>    | <r1>   |
      | <v2>    | <r2>   |
```

## Definition of Done

- [ ] Cada criterio de aceptacion de FEATURES.md tiene su escenario
- [ ] Maximo 8 escenarios por feature, maximo 5 pasos por escenario
- [ ] Cada escenario trazable a REQ y FEAT
- [ ] Cero emojis (ver `docs/DOC_STANDARD.md` seccion 1.4)
