---
name: xdd-historias
trigger: /xdd historias
description: Genera historias de usuario completas post-doc-granular. Lee acuerdos/proyecto/ + acuerdos/wireframes/ e identifica todas las historias. Por cada una crea 4 artefactos (propuesta, requisitos-escenarios, escenario-tecnico, checklist-tareas) via pipeline worker-auditor. Genera acuerdos/sprints/ (1 doc por sprint) con plan de sprints atomico. Sin evaluacion — si es una historia identificable, se documenta completa.
phase: plan
category: planning
---

# /xdd historias — Historias de usuario + plan de sprints

> **Principio (cero deuda tecnica):** Sin evaluacion. Cada funcionalidad identificable
> en los documentos granulares y wireframes tiene su historia de usuario. No hay
> "esto es obvio" ni "el agente ya sabe". Si existe como unidad de valor entregable,
> tiene historia completa.
>
> **Pipeline worker → auditor:** quien escribe NO aprueba. El auditor verifica
> completitud, alineacion con briefing y granularidad del checklist (minimo 50 tareas).
> Toda deficiencia encontrada se registra en acuerdos/lecciones/sprint-NN.md.

## 0. Pre-flight

1. Verificar que `acuerdos/proyecto/INDEX.md` existe (doc-granular completo).
2. Verificar que `acuerdos/wireframes/` tiene al menos 1 HTML aprobado.
3. Leer `acuerdos/memoria/MEMORY.md` + journal mas reciente en `acuerdos/memoria/` (Art. 3).
4. Si falta doc-granular: detener y ejecutar `/xdd doc-granular` primero.

---

## 1. IDENTIFICACION DE HISTORIAS

El agente lee TODOS los artefactos de `acuerdos/proyecto/`:
- `INDEX.md` (mapa completo de documentos)
- Cada `NN-<DOMINIO>.md` (documentos granulares)

Y los wireframes de `acuerdos/wireframes/*.html`.

A partir de esa lectura identifica **todas** las historias de usuario del proyecto.

**Criterio de historia:** Una historia es una unidad de valor entregable que:
- Un usuario puede completar de forma independiente, O
- Es un componente tecnico necesario para que otras historias funcionen (historia tecnica), O
- Es una configuracion, setup o infraestructura que habilita el sistema

**No hay limite de historias.** Un proyecto simple genera 10-20.
Uno complejo genera 50-100+. El numero lo determina el proyecto, no el agente.

**Tipos de historia:**
- `HU` — Historia de usuario (funcionalidad para el usuario final)
- `HT` — Historia tecnica (infraestructura, setup, configuracion)
- `HS` — Historia de seguridad (controles STDD, amenazas STRIDE)

Producir: `acuerdos/sprint.md` borrador con el listado inicial de historias
(numeradas, tipo, titulo, estimacion preliminar en puntos de historia).

---

## 2. PIPELINE WORKER → AUDITOR POR HISTORIA

Por cada historia del listado, ejecutar (en paralelo via xdd-orchestrate parallel_then_sync):

### PASO 1 — ESCRIBE 4 ARTEFACTOS (worker: engineering-technical-writer + product-manager)

#### `acuerdos/historia-usuario-N/propuesta.md`

```markdown
# HU-N: <Titulo>

## Descripcion
Como <tipo de usuario>, quiero <accion> para <beneficio>.

## Valor de negocio
<Por que esta historia importa. Que pasa si no se implementa.>

## Criterio de exito
<Condicion medible y verificable que indica que la historia esta completa.>

## Alcance
- Incluye: <lista>
- Excluye: <lista>

## Dependencias
- Requiere: <HU-X, HT-Y, documento tecnico Z>
- Bloquea: <HU-A, HB>
```

#### `acuerdos/historia-usuario-N/requisitos-escenarios.md`

Gherkin completo. Minimo por historia:
- 1 escenario happy path
- 2+ escenarios de error (inputs invalidos, estados inconsistentes, timeouts)
- 1+ escenario borde (limites, casos extremos, concurrencia)
- Escenarios de seguridad si la historia toca auth, datos, o superficies de ataque

```gherkin
Feature: <nombre-historia>
  Como <usuario>
  Quiero <accion>
  Para <beneficio>

  Scenario: Happy path — <descripcion>
    Given <precondicion>
    When <accion>
    Then <resultado esperado>

  Scenario: Error — <descripcion>
    ...

  Scenario: Borde — <descripcion>
    ...
```

Todos los terminos del Gherkin deben existir en `acuerdos/proyecto/` (ubiquitous language).

#### `acuerdos/historia-usuario-N/escenario-tecnico.md`

```markdown
# Escenario Tecnico — HU-N

## Stack involucrado
<Frontend/Backend/DB/Infra segun aplique para esta historia>

## Componentes
<Lista de componentes, modulos, servicios que se crean o modifican>

## Diagrama de flujo

\`\`\`mermaid
sequenceDiagram / flowchart / stateDiagram (segun aplique)
\`\`\`

## Esquemas de datos
<Si aplica: tablas, tipos, contratos API para esta historia>

## Patrones y decisiones tecnicas
<Patrones arquitectonicos, librerias, approach tecnico elegido y por que>

## Integraciones afectadas
<Otros servicios, APIs externas, eventos que esta historia genera o consume>

## Consideraciones de seguridad
<Amenazas STRIDE relevantes de THREATS.md. Controles especificos.>
```

#### `acuerdos/historia-usuario-N/checklist-tareas.md`

Lista de tareas atomicas ejecutables. **Minimo 50 tareas por historia.**
Cada tarea es una accion concreta, verificable, no ambigua.

Estructura obligatoria del checklist:

```markdown
# Checklist — HU-N: <Titulo>

## Setup y preparacion
- [ ] <tarea atomica>
...

## Backend
- [ ] <tarea atomica>
...

## Frontend / UI
- [ ] <tarea atomica (si aplica)>
...

## Tests unitarios (TDD — tests primero)
- [ ] Escribir test que falla para <componente>
- [ ] Implementar minimo codigo para pasar test
- [ ] Refactor manteniendo tests verdes
...

## Tests de integracion / BDD
- [ ] Implementar escenario Gherkin: <scenario name>
- [ ] Verificar happy path en entorno local
...

## Tests de seguridad (STDD)
- [ ] Escribir test de seguridad para amenaza <STRIDE-REF>
- [ ] Verificar que el test falla antes de implementar control
- [ ] Implementar control y verificar test verde
...

## Observabilidad
- [ ] Añadir log estructurado en <punto critico>
- [ ] Definir metrica para <evento de negocio>
...

## Documentacion
- [ ] Actualizar acuerdos/proyecto/<dominio>.md con cambios
- [ ] Actualizar openapi.yaml si hay cambios de API
...

## Revision y cierre
- [ ] Code review por engineering-code-reviewer
- [ ] Shield audit 0 CRITICAL
- [ ] Todos los escenarios Gherkin verdes
- [ ] PR lista para merge
```

### PASO 2 — AUDITA (auditor: engineering-code-reviewer + product-manager)

El auditor NO es quien escribio (segregacion de roles).

El auditor verifica:

1. **Completitud propuesta:** AS, valor, criterio de exito, alcance, dependencias presentes.
2. **Cobertura Gherkin:** happy path + errores + bordes. Terminos en ubiquitous language.
3. **Granularidad tecnica:** diagrama Mermaid, esquemas de datos si aplican, patrones documentados.
4. **Checklist minimo 50 tareas:** si < 50, rechaza — writer amplia. Sin excepcion.
5. **Cobertura de seguridad en checklist:** si la historia toca auth/datos/API y no hay
   tareas STDD, rechaza.
6. **Alineacion con briefing:** propuesta refleja exactamente lo acordado en `acuerdos/idea/`.
7. **Consistencia cross-historia:** no contradice ni duplica otra historia aprobada.

Si hay deficiencias: auditor lista → writer corrige → auditor re-verifica. Max 3 iteraciones.
Si no cierra en 3: escalar al usuario con lista de gaps.

**Cada gap encontrado** → registrar en `acuerdos/lecciones/sprint-00.md` (sprint de planificacion):

```bash
python3 scripts/xdd-memory.py sprint-close --sprint=00 --project=.
# Append al archivo generado: gap encontrado, historia afectada, correccion aplicada
```

Gate de historia aprobada:

```bash
xdd-gate.py set-author --phase plan --author "engineering-technical-writer"
xdd-gate.py approve --phase plan --approver "engineering-code-reviewer"
```

---

## 3. PLAN DE SPRINTS — `acuerdos/sprints/` (atomico — ADR-0050)

Una vez que TODAS las historias estan aprobadas. **1 carpeta = plan, 1 doc = 1 sprint.**

### Estructura

```
acuerdos/sprints/
  INDEX.md / INDEX.json    (roadmap Mermaid + tabla: sprint, titulo, historias, pts, estado)
  sprint-01.md / .json     (objetivo, historias, DoD, dependencias)
  sprint-NN.md / .json
acuerdos/sprint.md         → puntero delgado a sprints/INDEX.md (compat)
```

### Por cada sprint, `acuerdos/sprints/sprint-NN.md`

```markdown
# Sprint NN — <titulo>

> Cubre el sprint NN. Objetivo y alcance especifico. NO mezcla otros sprints.

## Objetivo
<Que capacidad queda disponible al cerrar este sprint>

## Historias asignadas

| ID | Tipo | Titulo | Puntos |
|----|------|--------|--------|
| HT-01 | tecnica | Setup inicial | N |
| HU-02 | usuario | <titulo> | N |

## Dependencias
- Requiere: sprint-NN-1 mergeado a develop
- Habilita: sprint-NN+1

## Definition of Done
- Todos los tests verdes (unit + integration + security)
- Shield 0 CRITICAL
- PR mergeada a develop
```

### INDEX maestro `acuerdos/sprints/INDEX.md`

```markdown
# INDEX — Plan de Sprints

> Roadmap completo. 1 doc = 1 sprint. Trazabilidad sprint -> historias.

## Roadmap

\`\`\`mermaid
flowchart LR
  S1[sprint-01] --> S2[sprint-02] --> S3[sprint-03]
\`\`\`

| Sprint | Titulo | Historias | Puntos | Estado |
|--------|--------|-----------|--------|--------|
| sprint-01 | Setup | HT-01, HU-02 | N | Pendiente |
```

### Puntero de compat `acuerdos/sprint.md`

```markdown
# Plan de Sprints

> Movido a acuerdos/sprints/ (ADR-0050 atomicidad).
> Ver acuerdos/sprints/INDEX.md (humano) o INDEX.json (agentes, ahorro de tokens).
```

**Criterios para organizar sprints:**
- Historias tecnicas (HT) van primero (habilitan las funcionales)
- Historias de seguridad (HS) se distribuyen — nunca al final
- Dependencias respetadas (HU-X que requiere HU-Y: Y va antes)
- No mas de N SP por sprint (N = velocidad estimada del equipo)
- Ultimo sprint siempre incluye hardening final + observabilidad + docs

**Tras escribir cada sprint-NN.md, sincronizar el JSON:**
```bash
python3 scripts/xdd-doc-sync.py sync-folder acuerdos/sprints
```

---

## 4. GATE DE CIERRE

El workflow de historias cierra cuando:

```
[ ] acuerdos/sprints/ existe con INDEX.md + INDEX.json + un sprint-NN.md por sprint
[ ] acuerdos/sprint.md es puntero a sprints/INDEX.md (compat)
[ ] Cada sprint-NN.md tiene su .json sidecar (xdd-doc-sync)
[ ] Cada acuerdos/historia-usuario-N/ tiene los 4 artefactos completos
[ ] Cada historia tiene firma de aprobacion (auditor != writer)
[ ] checklist-tareas.md >= 50 tareas en cada historia
[ ] 0 gaps abiertos en ninguna historia
```

Verificar atomicidad de sprints:
```bash
python3 scripts/xdd-discipline-check.py folder --kind sprints --path acuerdos/sprints
```

Verificacion:

```bash
ls acuerdos/historia-usuario-*/propuesta.md | wc -l    # N historias
for h in acuerdos/historia-usuario-*/checklist-tareas.md; do
  count=$(grep -c "^\- \[" "$h" 2>/dev/null || echo 0)
  echo "$h: $count tareas"
done
xdd-gate.py status   # phase plan: APROBADO
```

Al cerrar: registrar en `acuerdos/memoria/sprint-00.md` el numero de historias generadas
y el plan de sprints. El siguiente paso es `/xdd sprint` (Inc 8).

---

## 5. POST-FLIGHT — INICIO DE SPRINTS

Con las historias completas y el plan definido:

```
/xdd sprint --sprint=01
```

El agente lee la historia asignada al sprint 1, crea el equipo de subagentes dinamico
segun los componentes tecnicos involucrados, y ejecuta el ciclo completo de desarrollo.

---

## Agentes delegados

| Agente | Rol |
|--------|-----|
| `product-manager` | Identifica historias, escribe propuesta.md, valida valor de negocio |
| `engineering-technical-writer` | Escribe requisitos-escenarios.md, escenario-tecnico.md, checklist-tareas.md |
| `engineering-code-reviewer` | Audita cada historia (NUNCA el mismo que escribio) |
| `project-manager-senior` | Organiza sprints en sprint.md, estima velocidad |
