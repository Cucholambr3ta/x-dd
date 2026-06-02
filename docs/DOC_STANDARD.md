# Estandar de Documentacion X-DD

> Ley unica de formato y granularidad para todo artefacto de documentacion generado por
> cualquier agente o workflow de X-DD. Referenciada por la Constitucion (Art. 9). Si un
> workflow, agente o template entra en conflicto con este documento, este documento gana.

**Version:** 1.0.0
**Estado:** ACTIVO
**Aplica a:** todos los workflows y agentes que emiten artefactos `.md`, `.yaml`, `.feature`.

---

## 1. Principios inquebrantables

### 1.1 Cero iconografia

Prohibicion absoluta de emojis, iconos o simbolos no textuales en artefactos finales.
Densidad de emoji exigida: 0%. Solo se admiten simbolos ASCII con valor tecnico o
matematico (operadores, flechas en diagramas ASCII, notacion). Esta regla no admite
excepciones.

### 1.2 Diagramas Mermaid obligatorios

Todo artefacto que describa estructura, flujo, estado o relaciones DEBE incluir al menos
un diagrama. El formato por defecto es Mermaid. ASCII solo cuando Mermaid es imposible en
el contexto de consumo.

Tipos de diagrama por artefacto:

| Artefacto | Diagrama minimo obligatorio |
| --- | --- |
| ARQUITECTURA.md | C4 nivel Contexto + Contenedor (Mermaid `C4Context`, `C4Container`) |
| DOMAIN.md | Diagrama de clases/agregados (Mermaid `classDiagram`) + Context Map |
| THREATS.md | Diagrama de flujo de datos con fronteras de confianza (Mermaid `flowchart`) |
| Casos de uso | Diagrama de secuencia por caso (Mermaid `sequenceDiagram`) |
| Entidades con ciclo de vida | Diagrama de estado (Mermaid `stateDiagram-v2`) |
| Despliegue | Diagrama de despliegue (Mermaid `flowchart` o `C4Deployment`) |

### 1.3 Tablas para datos estructurados

Toda lista de datos con mas de un atributo se representa como tabla, no como lista de
bullets. Obligatorio para: requisitos, casos de prueba, matrices de trazabilidad,
controles de seguridad, inventarios PII, metricas, parametros de configuracion.

### 1.4 Gherkin completo

Cada criterio de aceptacion de cada historia de usuario tiene su bloque Gherkin:
`Feature` / `Scenario` (o `Scenario Outline` + `Examples`) / `Given` / `When` / `Then`.
Incluir siempre: 1 happy path, >=1 escenario de error, >=1 caso borde. Vocabulario
exclusivamente del DOMAIN.md (Ubiquitous Language).

### 1.5 Profundidad minima

Cada seccion principal contiene sub-secciones con contenido sustantivo. Prohibido entregar
una seccion como una sola lista de bullets de alto nivel sin desarrollo. Si una seccion no
aplica al proyecto, se declara explicitamente "No aplica" con justificacion de una linea.

### 1.6 Trazabilidad bidireccional

Cada requisito referencia sus casos de prueba. Cada caso de prueba referencia su requisito.
Cada feature referencia su entidad de dominio. Cada amenaza referencia el activo y el
control. Los identificadores siguen el formato: `REQ-NNN`, `NFR-NNN`, `FEAT-NNN`,
`THR-NNN`, `TC-NNN`, `SEC-REQ-NNN`.

---

## 2. Secciones minimas por artefacto

Cada artefacto del pipeline debe contener al menos estas secciones. Un artefacto con
menos secciones se considera incompleto y no pasa el gate de QA.

### 2.1 ARQUITECTURA.md

1. Vision general del sistema
2. Diagrama C4 Contexto (Mermaid)
3. Diagrama C4 Contenedor (Mermaid)
4. Diagrama C4 Componente (Mermaid) de los contenedores criticos
5. Decisiones arquitectonicas clave (referencia a ADRs)
6. Atributos de calidad y como se satisfacen
7. Riesgos arquitectonicos

### 2.2 DOMAIN.md

1. Ubiquitous Language (tabla: termino, definicion, sinonimos prohibidos)
2. Bounded Contexts (diagrama Mermaid)
3. Context Map (relaciones upstream/downstream)
4. Agregados (root, invariantes, entidades, value objects, repositorio)
5. Domain Events (emisor, consumidores, efecto)
6. Diagrama de clases del dominio (Mermaid `classDiagram`)

### 2.3 THREATS.md

1. Activos y actores adversarios (tabla con criticalidad)
2. Diagrama de flujo de datos con fronteras de confianza (Mermaid)
3. Analisis STRIDE por componente (tabla: THR-NNN, categoria, vector, probabilidad, impacto, riesgo)
4. Controles y mitigaciones (libreria/tecnica exacta por amenaza)
5. Requisitos de seguridad derivados (SEC-REQ-NNN, copiados a SPEC.md)
6. Verificacion (cada agregado del DOMAIN.md tiene >=1 amenaza analizada)

### 2.4 FEATURES.md

1. Catalogo de features (tabla: FEAT-NNN, nombre `[accion][resultado][objeto]`, beneficio, prioridad RICE/MoSCoW, estimacion)
2. Criterios de aceptacion por feature (referencia a casos Gherkin)
3. Mapa feature -> entidad de dominio
4. Dependencias entre features

### 2.5 FUNCIONALES.md / NO_FUNCIONALES.md

- Funcionales: tabla (REQ-NNN, historia de usuario, criterio de aceptacion, prioridad, estado, casos de prueba)
- No funcionales: tabla (NFR-NNN, categoria, metrica, umbral, prioridad, metodo de verificacion)

### 2.6 Artefactos QA

- PLAN_QA.md: estrategia por capa + tabla de cobertura objetivo
- CASOS_GHERKIN.md: todos los Feature/Scenario organizados por feature
- MATRIZ_TRAZABILIDAD.md: tabla REQ -> TC -> tipo -> resultado -> cobertura
- CASOS_BORDE.md: tabla (TC-NNN, escenario, precondicion, entrada, resultado esperado, prioridad)
- CHECKLIST_RELEASE.md: Definition of Done con criterios de salida verificables

### 2.7 Artefactos de seguridad y privacidad

- PRIVACY.md: inventario PII (tabla), bases legales GDPR, retencion, transferencias, brechas
- SECURITY_CONTROLS.md: tabla (control, estado, evidencia, riesgo residual)

---

## 3. Definition of Done por documento

Un documento esta completo cuando:

1. Contiene todas las secciones minimas de la seccion 2 para su tipo.
2. Tiene cero emojis (verificable con grep de rango Unicode de emoji).
3. Incluye los diagramas Mermaid obligatorios para su tipo (seccion 1.2).
4. Usa tablas para todo dato estructurado (seccion 1.3).
5. Cada criterio de aceptacion tiene su bloque Gherkin (cuando aplica).
6. Cada identificador trazable resuelve en ambas direcciones (seccion 1.6).
7. Ninguna seccion es un bullet de alto nivel sin desarrollo (seccion 1.5).

---

## 4. Verificacion automatizada

Estos chequeos forman parte del gate de QA (Tier 1):

```bash
# Cero emojis en artefactos generados
grep -rlP '[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}]' docs/ && echo "FALLO: emojis detectados" || echo "OK: 0 emojis"

# Presencia de al menos un bloque Mermaid en artefactos estructurales
grep -L '```mermaid' docs/arquitectura/ARQUITECTURA.md docs/arquitectura/DOMAIN.md && echo "FALLO: falta diagrama"
```

---

## 5. Aplicabilidad

Este estandar es referenciado por:

- El agente `engineering-technical-writer` (reglas hard-coded en su prompt).
- Todos los workflows en `.agent/workflows/` que emiten artefactos.
- Todos los templates en `templates/`.
- El gate de QA (`/qa-review`) como criterio Tier 1.

Cualquier agente o workflow nuevo que emita documentacion debe declarar conformidad con
este estandar en su seccion de output.
