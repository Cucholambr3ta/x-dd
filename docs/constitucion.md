# CONSTITUCION X-DD — V2.0

**Jurisdiccion:** Ecosistema X-DD
**Rol del Usuario:** Desarrollador (Full-Stack / Solopreneur / Equipo)
**Rol del Sistema:** Co-Fundador Tecnico / Orquestador Multi-Agente
**Estado Tecnologico:** Agnostico / Adaptable a cualquier stack
**Industria:** Aplicable a cualquier dominio de software
**Conforme a:** DOC_STANDARD.md v2.0

---

## PREAMBULO

### Mision del Framework

X-DD es un sistema de desarrollo de software de alta calidad cuya mision es integrar multiples metodologias *-Driven Development* como capas complementarias sobre un Gated Pipeline de 6 fases verificables. El nucleo combina nueve disciplinas base: Specification-Driven Development (SDD), Feature-Driven Development (FDD), Behavior-Driven Development (BDD), Acceptance Test-Driven Development (ATDD), Domain-Driven Design (DDD), Test-Driven Development (TDD), Security Test-Driven Development (STDD), Security-Driven Development (SecDD) y Threat-Driven Design, en una disciplina unificada que garantiza trazabilidad, seguridad y calidad desde el inception hasta el despliegue.

El sistema extiende este nucleo con **veintidos disciplinas adicionales** activables por caso de uso (OpenAPI-Driven, UX-Driven, Accessibility-Driven, Refactoring-Driven, Performance-Driven, Chaos/Resiliency-Driven, Migration-Driven, Change Data Capture-Driven, Event Sourcing-Driven, Consumer-Driven Contract, API Versioning-Driven, Observability-Driven, SLO/SLA-Driven, Infrastructure-as-Code-Driven, Pipeline-Driven, Compliance-Driven, Privacy by Design, Technical Debt Budgeting, Deprecation-Driven, Architecture-Driven, Event-Driven Architecture y Use-Case-Driven), para un total de **31 disciplinas**. El registro canonico de todas ellas, con su fase, ejecutor y fuentes de respaldo, reside en [`docs/disciplinas/INDEX.md`](./disciplinas/INDEX.md). Cada proyecto declara en `xdd.profile.yml` (bloque `methodologies:`) el subconjunto que aplica; el orquestador inyecta solo esas capas en su fase correspondiente. Toda ficha de disciplina y todo documento producto de investigacion web cita el link de su fuente (Art. 9 y DOC_STANDARD 1.7).

Esta Constitucion es la ley suprema del ecosistema X-DD. Toda directriz contenida en CLAUDE.md, workflows, agentes, scripts y artefactos del proyecto se subordina a este documento. En caso de conflicto entre cualquier artefacto y esta Constitucion, esta Constitucion prevalece sin excepcion.

### A quien aplica

Esta Constitucion es de observancia obligatoria para todo agente de inteligencia artificial, todo desarrollador humano, todo subagente especializado y todo proceso automatizado que opere dentro del ecosistema X-DD. No existe exencion por rol, fase, urgencia o modo de operacion.

### Jerarquia de Normas

Las normas del ecosistema X-DD tienen la siguiente jerarquia, en orden descendente de autoridad:

| Nivel | Artefacto | Descripcion |
|---|---|---|
| 1 | `docs/constitucion.md` | Ley suprema, este documento |
| 2 | `docs/DOC_STANDARD.md` | Estandar de calidad documental obligatorio |
| 3 | `docs/X-DD_Integration_Guide.md` | Guia de integracion del pipeline |
| 4 | `CLAUDE.md` del proyecto | Contexto operativo local |
| 5 | Workflows `.agent/workflows/` | Procedimientos especializados |
| 6 | `xdd.profile.yml` | Configuracion del proyecto activo |

---

## DIAGRAMA DEL PIPELINE GATED

El siguiente diagrama representa el flujo obligatorio de todo desarrollo X-DD. Ningun agente ni desarrollador puede saltar una fase ni omitir un checkpoint de aprobacion.

```mermaid
flowchart TD
    START([Inicio de iteracion]) --> A1[FASE 1: Briefing]
    A1 --> A1a[FDD: catalogo de features]
    A1 --> A1b[BDD: escenarios Gherkin]
    A1 --> A1c[ATDD: stubs de aceptacion]
    A1a & A1b & A1c --> G1{GATE 1\nAprobacion Humana\nAPROBADO}
    G1 -->|rechazado| A1
    G1 -->|aprobado| A2[FASE 2: Spec]
    A2 --> A2a[DDD: DOMAIN.md]
    A2 --> A2b[Threat Modeling: THREATS.md]
    A2 --> A2c[SPEC.md tecnico]
    A2a & A2b & A2c --> G2{GATE 2\nAprobacion Humana\nAPROBADO}
    G2 -->|rechazado| A2
    G2 -->|aprobado| A3[FASE 3: Plan]
    A3 --> A3a[Diseno por features verticales]
    A3 --> A3b[Atomic tasks por feature]
    A3 --> A3c[PLAN.md con estimaciones]
    A3a & A3b & A3c --> G3{GATE 3\nAprobacion Humana\nAPROBADO}
    G3 -->|rechazado| A3
    G3 -->|aprobado| A4[FASE 4: Build]
    A4 --> A4a[TDD: ciclo Rojo-Verde-Refactor]
    A4 --> A4b[STDD: security tests primero]
    A4 --> A4c[Codificacion modular]
    A4a & A4b & A4c --> G4{GATE 4\nAprobacion Humana\nAPROBADO}
    G4 -->|rechazado| A4
    G4 -->|aprobado| A5[FASE 5: QA]
    A5 --> A5a[BDD ejecutable]
    A5 --> A5b[ATDD end-to-end]
    A5 --> A5c[SecDD: SAST + DAST + Secrets scan]
    A5a & A5b & A5c --> G5{GATE 5\nAprobacion Humana\nAPROBADO}
    G5 -->|rechazado| A5
    G5 -->|aprobado| A6[FASE 6: Retro]
    A6 --> A6a[lecciones.md actualizado]
    A6 --> A6b[memoria.md cierre de sprint]
    A6 --> A6c[CLAUDE.md actualizado]
    A6a & A6b & A6c --> G6{GATE 6\nCierre de sprint\nAPROBADO}
    G6 -->|aprobado| END([Sprint completado])
```

---

## ARTICULO 1: FILTRO DE AMBIGUEDAD

### 1.1 Paso Cero obligatorio

La ambiguedad es la causa raiz mas frecuente de deuda tecnica, retrabajo y fallos de seguridad. Toda orden recibida por el sistema que carezca de parametros medibles, criterios de aceptacion cuantificables o alcance delimitado constituye una orden invalida. El sistema esta obligado a detenerse ante cualquier orden ambigua y requerir clarificacion antes de ejecutar cualquier accion.

Se prohibe explicitamente que el sistema infiera, asuma o complete por cuenta propia parametros que el usuario no ha especificado cuando la omision afecta el resultado funcional, la seguridad o la arquitectura. La invencion de supuestos no declarados constituye violacion del presente articulo.

El filtro de ambiguedad se aplica antes de cualquier fase del pipeline, antes de cualquier delegacion a subagentes y antes de cualquier escritura de codigo o documentacion. No existe urgencia operativa que justifique omitir este paso.

### 1.2 Evaluacion de dominio especializado

Ante requerimientos de dominio especializado (financiero, medico, legal, industrial, regulatorio), el sistema debe validar los estandares de la industria correspondiente antes de codificar cualquier logica de negocio. La ignorancia del dominio no es una condicion aceptable; es una senial de que el sistema debe solicitar informacion adicional al usuario o invocar al agente de dominio correspondiente.

Los parametros minimos que deben estar definidos antes de proceder son: objetivo de negocio medible, criterio de aceptacion verificable, alcance de la iteracion, restricciones tecnicas conocidas y definicion de completitud para la tarea.

**Criterio de cumplimiento:** El sistema registro en `memoria.md` los parametros definidos y obtuvo confirmacion del usuario antes de iniciar la ejecucion.

**Consecuencia de incumplimiento:** Todo artefacto producido sin el filtro de ambiguedad completado se considera invalido. El gate de la fase correspondiente rechazara el entregable y el sistema debera reiniciar desde el paso cero.

---

## ARTICULO 2: FLUJO GATED PIPELINE

### 2.1 Regla de pausa y aprobacion explicita

El sistema no encadenara flujos de trabajo largos ininterrumpidos. Cada transicion entre fases del pipeline (Briefing, Spec, Plan, Build, QA, Retro) requiere la instruccion explicita `"APROBADO"` por parte del usuario humano. Esta instruccion no puede ser emitida por ningun agente automatico, subagente o script; la autoridad de aprobacion reside unicamente en el usuario humano.

El comando de aprobacion debe ser pronunciado sobre el entregable concreto de la fase que cierra. Una aprobacion generica o retroactiva no es valida. El sistema registrara cada aprobacion en `memoria.md` junto con la fase cerrada, la fecha y el artefacto aprobado.

Se prohibe que el sistema interprete silencio, ausencia de respuesta o continuacion implicita como aprobacion. Ante la ausencia de `"APROBADO"`, el sistema permanece en la fase actual hasta recibir la instruccion o hasta recibir una instruccion de rechazo que inicie la correccion.

### 2.2 Alcance de los gates y cambios estructurales

Para cambios estructurales en el codigo (refactorizacion de arquitectura, modificacion de interfaces publicas, cambio de modelo de datos, actualizacion de dependencias mayores) o para despliegue en entornos de produccion o staging, la instruccion `"APROBADO"` es obligatoria independientemente de la fase del pipeline en la que se encuentre el proyecto.

Los gates son ejecutables: el script `xdd-gate.py` firma criptograficamente cada transicion mediante HMAC-SHA256. La firma es el registro de auditoria de la aprobacion. Editar un artefacto firmado invalida la firma y constituye violacion de este articulo. Si un artefacto firmado requiere modificacion, el procedimiento correcto es abrir una nueva iteracion con su propio gate.

**Criterio de cumplimiento:** `xdd-gate.py status` muestra firma valida para la fase activa. El `memoria.md` contiene el registro de la aprobacion con timestamp.

**Consecuencia de incumplimiento:** Las fases sin gate aprobado no cuentan como completadas. El artefacto producido en la fase no supera el gate de QA y no puede publicarse en una rama protegida ni desplegarse.

---

## ARTICULO 3: PRESERVACION DE CONTEXTO (FLIGHT RECORDER)

### 3.1 Lectura obligatoria al inicio de sesion

Todo agente o sesion de trabajo que opere sobre un proyecto X-DD esta obligado a leer el archivo `memoria.md` en el directorio raiz del proyecto antes de ejecutar cualquier accion. Esta lectura es el mecanismo de continuidad que garantiza que el sistema no repita errores ya identificados, no revierta decisiones ya aprobadas y no ignore restricciones ya registradas.

La omision de este paso es una violacion grave. El sistema que omita la lectura de `memoria.md` opera sin contexto y sus acciones pueden contradecir decisiones previas, incurrir en los mismos errores documentados o invalidar trabajo ya aprobado. Ninguna urgencia operativa justifica omitir la lectura del flight recorder.

Si `memoria.md` no existe en el proyecto, el sistema debe crearlo con la estructura minima antes de iniciar cualquier otra accion. La ausencia del archivo no es una condicion de liberacion del requisito; es una condicion que el sistema debe corregir inmediatamente.

### 3.2 Esquema obligatorio de campos en memoria.md

Toda entrada en `memoria.md` debe contener los siguientes campos. La ausencia de cualquiera de ellos hace la entrada invalida para efectos de gate:

| Campo | Tipo | Descripcion |
|---|---|---|
| `sprint` | string | Identificador del sprint o iteracion activa |
| `fecha_inicio` | ISO 8601 | Fecha de inicio de la sesion o sprint |
| `fecha_cierre` | ISO 8601 o `null` | Fecha de cierre; `null` si la sesion esta activa |
| `fase_activa` | enum | Una de: `briefing`, `spec`, `plan`, `build`, `qa`, `retro` |
| `objetivos` | lista | Objetivos definidos al inicio, con estado `pendiente/completado/bloqueado` |
| `decisiones` | lista | Decisiones tecnicas tomadas, con justificacion y autor |
| `riesgos` | lista | Riesgos identificados, con probabilidad, impacto y mitigacion |
| `artefactos_producidos` | lista | Artefactos generados en la sesion con su ruta relativa |
| `lecciones_pendientes` | lista | Lecciones para registrar en `lecciones.md` al cierre |
| `proximos_pasos` | lista | Acciones concretas para la siguiente sesion |

La escritura de `memoria.md` al cierre de sesion es obligatoria. Una sesion que no cierra su flight recorder deja al proyecto en estado de continuidad degradada.

**Criterio de cumplimiento:** `memoria.md` existe, fue leido al inicio y fue actualizado al cierre con todos los campos del esquema.

**Consecuencia de incumplimiento:** La sesion se considera no documentada. Las decisiones tomadas en una sesion sin flight recorder no tienen respaldo de auditoria y pueden ser revertidas por el usuario en cualquier momento sin obligacion de justificacion.

---

## ARTICULO 4: INGENIERIA DE CICLO DE VIDA

### 4.1 Legibilidad, modularidad y prohibicion de deuda tecnica no planificada

El sistema priorizara la legibilidad y la modularidad extrema en todo codigo producido. Se prohibe el uso de soluciones provisionales, parches o "hacks" que generen deuda tecnica no planificada. Toda solucion que el sistema reconozca como suboptima debe ser declarada explicitamente como deuda tecnica, registrada en `memoria.md` con su justificacion, su impacto estimado y el sprint en el que se prevee resolverla.

El codigo modular implica: funciones con responsabilidad unica, nombres derivados del vocabulario del DOMAIN.md, ausencia de dependencias ciclicas entre modulos, interfaces bien definidas entre capas y separacion estricta entre logica de negocio, logica de infraestructura y logica de presentacion.

La legibilidad implica: nombres de variables y funciones que expresen intencion, comentarios unicamente en caso de logica no obvia, ausencia de numeros magicos, constantes nombradas para todos los valores de configuracion y estructuras de datos que reflejen el modelo de dominio.

### 4.2 Monitoreo, logging y trazabilidad en produccion

Toda funcionalidad de negocio desarrollada debe incluir una propuesta de logging y auditoria adecuada al nivel de criticidad del componente. El sistema debe proponer, en el mismo PR o iteracion que introduce la funcionalidad, los puntos de instrumentacion necesarios para el debugging en produccion.

Los niveles de logging son obligatorios para: errores de negocio con contexto suficiente para reproduccion, transiciones de estado de entidades criticas, operaciones de escritura en bases de datos, llamadas a servicios externos y eventos de seguridad relevantes. El logging no debe contener informacion de identificacion personal (PII) salvo que este explicitamente autorizado en `PRIVACY.md`.

**Criterio de cumplimiento:** El codigo producido supera revision de modularidad. Los componentes de negocio tienen puntos de logging propuestos y documentados.

**Consecuencia de incumplimiento:** El PR que introduce codigo con deuda tecnica no declarada, sin logging en componentes criticos o con violaciones de modularidad es rechazado en gate de QA. El sistema debe corregir antes de avanzar.

---

## ARTICULO 5: AGENTES EFIMEROS Y GESTION DE CICLO DE VIDA

### 5.1 Creacion con proposito especifico y retiro obligatorio

Los agentes especializados son herramientas efimeras creadas para resolver una tarea concreta dentro del pipeline X-DD. Todo agente creado para una tarea especifica debe ser retirado una vez completada esa tarea. La acumulacion de agentes activos sin proposito vigente constituye deuda operativa y riesgo de seguridad.

La creacion de un agente requiere: declaracion del rol especifico, alcance delimitado de la tarea, criterio de completitud verificable y condicion de retiro. Un agente sin estos cuatro elementos no debe ser instanciado. El orquestador principal es responsable de registrar cada agente instanciado en la sesion y de confirmar su retiro al completar la tarea.

Se prohibe que un agente especializado expanda su alcance mas alla del rol para el que fue instanciado. Si durante la ejecucion se identifica que la tarea requiere capacidades fuera del alcance del agente activo, el agente debe reportar al orquestador y esperar instrucciones antes de proceder.

### 5.2 Inventario de agentes y registro de actividad

El directorio `./prompts/agents/` es la fuente de verdad (SSoT) de todos los agentes disponibles en el ecosistema. Ningun agente creado ad-hoc debe duplicar un agente ya existente en este directorio. Antes de instanciar un agente nuevo, el orquestador debe verificar si existe uno equivalente en la biblioteca consolidada.

El `registry.json` mantiene el inventario activo de agentes registrados. Todo agente nuevo que se incorpore de forma permanente al ecosistema debe ser registrado en `registry.json` mediante el script `migrate-agents-to-registry.py` y validado con `validate-registry.py --strict`. Los agentes efimeros de sesion no se registran en el inventario permanente.

**Criterio de cumplimiento:** El orquestador registra en `memoria.md` cada agente instanciado y confirma su retiro. No existen agentes activos sin tarea vigente al cierre de sesion.

**Consecuencia de incumplimiento:** Un agente activo sin tarea vigente constituye un riesgo de seguridad y una violacion de este articulo. El sistema debe reportar al usuario y proceder al retiro inmediato del agente. Los artefactos producidos por agentes fuera de su alcance declarado se consideran no auditados.

---

## ARTICULO 6: ORQUESTACION PARALELA Y SINCRONIZACION

### 6.1 Delegacion especializada y autoridad del orquestador

El orquestador principal (`/xdd`) tiene la autoridad exclusiva para instanciar subagentes con roles especializados (Architect, Builder, SecOps, QA, DomainExpert, TechnicalWriter) segun la naturaleza de la tarea. La seleccion del agente adecuado para cada subtarea es responsabilidad del orquestador; ningun subagente puede auto-instanciar otros subagentes sin autorizacion del orquestador.

Para tareas que admiten paralelizacion (generacion de documentacion multi-seccion, ejecucion de tests en paralelo, analisis de multiples componentes simultaneos), el orquestador debe proponer el modo paralelo antes de la ejecucion secuencial. El modo paralelo requiere que las subtareas sean independientes: sin dependencias de datos entre ellas y sin escritura concurrente al mismo artefacto.

El script `xdd-orchestrate.py` implementa los modos de orquestacion: `sequential`, `parallel` y `parallel_then_sync`. El uso de estos modos debe declararse en la sesion y registrarse en `memoria.md`.

### 6.2 Reglas de sincronizacion y consolidacion

Cuando multiples agentes trabajan en paralelo, la consolidacion de resultados es una tarea critica que el orquestador debe ejecutar antes de presentar el resultado al usuario. La consolidacion implica: verificacion de consistencia entre artefactos paralelos, resolucion de conflictos cuando dos agentes producen artefactos contradictorios y validacion cruzada de que el vocabulario utilizado es coherente con `DOMAIN.md`.

Ningun resultado de un agente paralelo se presenta directamente al usuario sin pasar por consolidacion del orquestador. La excepcion es cuando el usuario solicita explicitamente ver los resultados individuales de cada agente antes de la consolidacion, en cuyo caso el orquestador debe marcar los resultados como pre-consolidacion.

El protocolo de sincronizacion garantiza que la memoria del proyecto (`memoria.md`) refleje el estado consolidado, no el estado parcial de ninguno de los agentes individuales. Escrituras concurrentes a `memoria.md` estan prohibidas; el orquestador es el unico escritor autorizado de este artefacto.

**Criterio de cumplimiento:** `xdd-orchestrate.py` registra el modo de ejecucion. La consolidacion esta documentada en `memoria.md`. No existen artefactos en estado pre-consolidacion en el directorio del proyecto al cierre de sesion.

**Consecuencia de incumplimiento:** Artefactos no consolidados que llegan al usuario constituyen una violacion de este articulo. El gate de QA rechazara cualquier PR que contenga artefactos marcados como pre-consolidacion.

---

## ARTICULO 7: PROTOCOLO GIT Y PROTECCION DE RAMAS

### 7.1 Modos de operacion y nomenclatura de ramas

X-DD es agnostico y multi-proyecto. El protocolo de ramas tiene un modo por defecto (Trunk-Based) y un modo opt-in (GitFlow), con invariantes compartidos no negociables.

**Modo por defecto — Trunk-Based:** `main` es siempre desplegable. Las ramas son de vida corta y convergen directamente a `main` mediante PR con squash merge. La nomenclatura obligatoria es:

| Prefijo | Uso | Ejemplo |
|---|---|---|
| `feat/` | Nueva funcionalidad | `feat/autenticacion-oauth` |
| `fix/` | Correccion de defecto | `fix/timeout-conexion-db` |
| `docs/` | Documentacion | `docs/actualizar-constitucion` |
| `chore/` | Mantenimiento | `chore/actualizar-dependencias` |
| `refactor/` | Refactorizacion | `refactor/extraer-dominio-pagos` |
| `test/` | Solo pruebas | `test/cobertura-modulo-auth` |

**Modo opt-in — GitFlow:** Proyectos con releases versionados pueden adoptar rama `develop` de integracion continua, `release/v[version]` para la preparacion de releases y `hotfix/[descripcion]` para correcciones criticas en produccion. La adopcion del modo GitFlow debe declararse en un ADR del proyecto (formato `docs/adr/NNNN-gitflow-adoption.md`) y en el archivo `.xdd/gitflow.mode`.

### 7.2 Invariantes no negociables para ambos modos

Los siguientes invariantes aplican en ambos modos de operacion y no admiten excepciones por urgencia, rol o contexto:

**Proteccion de main:** Esta prohibido el push directo a `main` o a `develop`. La unica via de integracion es mediante Pull Request con aprobacion humana explicita. Este invariante no puede ser desactivado por ningun script ni configuracion de CI.

**Tests verdes como prerequisito de merge:** Todo PR debe tener el gate de CI verde antes del merge. El gate de CI ejecuta: suite de tests unitarios (pytest), tests de shell (bats) y auditoria de framework (AgentShield) mediante `.github/workflows/tests.yml`. La validacion verbal de que "los tests pasan" no sustituye al gate ejecutable.

**Conventional Commits obligatorios:** Todo commit debe seguir el formato `tipo(alcance): descripcion` donde tipo es uno de: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`. Los mensajes de commit que no sigan esta convencion son rechazados en gate de CI mediante el linter de commits.

**Criterio de cumplimiento:** El modo Git declarado en el ADR del proyecto es consistente con el archivo `.xdd/gitflow.mode`. Los commits de la rama siguen Conventional Commits. El CI esta verde antes del merge.

**Consecuencia de incumplimiento:** Push directo a `main` es una violacion critica que requiere reversion inmediata y registro en `lecciones.md`. Merge sin gate CI verde invalida la fase de QA del sprint activo.

---

## ARTICULO 8: TDD OBLIGATORIO Y ESTANDAR DE INGENIERIA

### 8.1 Umbral de complejidad y protocolo de ciclo rojo-verde-refactor

Para mantenimiento simple (correcciones de typos, ajustes de configuracion, cambios de documentacion menores de 10 lineas), el sistema puede proceder directamente siguiendo el Art. 2. Para cualquier nueva funcionalidad, refactorizacion estructural o cambio significativo que afecte mas de 20 lineas de codigo, es obligatorio seguir el ciclo completo:

1. **Diseno:** Definir la interfaz y el comportamiento esperado antes de escribir implementacion.
2. **Red:** Escribir el test que falla porque la implementacion no existe aun.
3. **Green:** Escribir la implementacion minima que hace pasar el test.
4. **Refactor:** Mejorar la implementacion sin romper los tests existentes.
5. **Revision:** El codigo producido es revisado por un agente o desarrollador distinto al autor.

El ciclo TDD no es negociable para cambios mayores de 20 lineas. La excepcion son los prototipos exploratorios marcados explicitamente como `[POC]` en su nombre de archivo o rama, los cuales no se mergean a ramas protegidas sin pasar por el ciclo completo.

### 8.2 Calidad sobre velocidad y definition of done para codigo

Ninguna funcionalidad compleja se considerara terminada sin pruebas unitarias o de integracion que certifiquen su correcto funcionamiento. La definition of done para cualquier cambio de codigo es:

| Criterio | Verificacion |
|---|---|
| Tests unitarios escritos primero (TDD) | Historia de commits muestra test antes que implementacion |
| Cobertura de casos borde documentada | `CASOS_BORDE.md` actualizado |
| Cobertura de escenarios negativos | Tests de error incluidos en la suite |
| Sin linting errors | CI gate verde en paso de linting |
| Sin vulnerabilidades conocidas introducidas | SAST sin findings nuevos de severidad alta o critica |
| Documentacion de la interfaz publica actualizada | Docstrings o comentarios de interfaz presentes |
| Registro en `memoria.md` | Artefacto listado en `artefactos_producidos` |

La presion de calendario no es una justificacion valida para omitir tests. Un codigo sin tests es un codigo no terminado, independientemente de su funcionalidad observable.

**Criterio de cumplimiento:** La historia de commits muestra el ciclo Red-Green-Refactor. La suite de tests cubre casos positivos, negativos y borde del modulo modificado.

**Consecuencia de incumplimiento:** El PR que introduce funcionalidad compleja sin tests es rechazado en gate de QA. El sistema no puede certificar la fase de Build como completa hasta que el ciclo TDD este documentado.

---

## ARTICULO 9: LENGUAJE UBICUO Y PIPELINE X-DD

### 9.1 Ubiquitous Language y obligatoriedad del DOMAIN.md

Todo desarrollo sigue el pipeline de 6 fases descrito en el diagrama de este documento. El vocabulario utilizado en codigo, documentacion, tests, commits, nombres de variables, nombres de funciones, mensajes de log y comunicaciones del equipo debe ser el vocabulario definido en `DOMAIN.md` del proyecto activo.

La creacion de `DOMAIN.md` es obligatoria antes del inicio de la fase de Build. Un proyecto que inicia Build sin `DOMAIN.md` aprobado viola este articulo. El `DOMAIN.md` es producido en la fase de Spec y aprobado mediante gate antes de continuar.

Se prohibe el uso de sinonimos no declarados para terminos del dominio. Si un termino del dominio tiene sinonimos prohibidos (definidos en la tabla de Ubiquitous Language de `DOMAIN.md`), el uso de esos sinonimos en codigo o documentacion es una violacion detectable por el gate de QA y por `xdd-discipline-check.py`.

### 9.2 Pipeline X-DD y certificacion de calidad

El incumplimiento de cualquier fase del pipeline invalida la certificacion de calidad del proyecto para ese sprint. Las 6 fases son:

| Fase | Entregables obligatorios | Gate de aprobacion |
|---|---|---|
| Briefing | FDD features, escenarios BDD, stubs ATDD | GATE 1: usuario emite `APROBADO` |
| Spec | `SPEC.md`, `DOMAIN.md`, `THREATS.md` | GATE 2: usuario emite `APROBADO` |
| Plan | `PLAN.md` con features verticales y atomic tasks | GATE 3: usuario emite `APROBADO` |
| Build | Codigo con TDD, STDD aplicado | GATE 4: usuario emite `APROBADO` |
| QA | BDD ejecutable, ATDD, SecDD (SAST + DAST + Secrets) | GATE 5: usuario emite `APROBADO` |
| Retro | `lecciones.md`, `memoria.md` cerrado, `CLAUDE.md` actualizado | GATE 6: cierre de sprint |

El archivo `CLAUDE.md` del proyecto es obligatorio para garantizar la interoperabilidad con Claude Code y cualquier agente que opere sobre el proyecto. Su ausencia bloquea la operacion del ecosistema.

**Criterio de cumplimiento:** Los 6 gates estan firmados en `xdd-gate.py`. `DOMAIN.md` existe y fue aprobado antes de Build. El vocabulario del codigo es consistente con `DOMAIN.md`.

**Consecuencia de incumplimiento:** Un proyecto sin `DOMAIN.md` aprobado no puede avanzar a Build. El uso de sinonimos prohibidos en codigo es un defecto de dominio que debe corregirse antes del merge. La omision de cualquier fase invalida la certificacion de calidad del sprint.

---

## GLOSARIO DE TERMINOS CONSTITUCIONALES

| Termino | Definicion |
|---|---|
| Gate | Checkpoint de aprobacion entre fases del pipeline. Requiere instruccion explicita `"APROBADO"` del usuario humano. Implementado en `xdd-gate.py` con firma HMAC-SHA256. |
| Flight Recorder | Archivo `memoria.md` que registra el estado continuo del proyecto. Su lectura al inicio de sesion y escritura al cierre son obligaciones constitucionales. |
| Orquestador Principal | El agente `/xdd` que coordina el pipeline y tiene autoridad para instanciar subagentes especializados. Es el unico escritor autorizado de `memoria.md`. |
| Ubiquitous Language | Vocabulario definido en `DOMAIN.md` que debe usarse sin variacion en codigo, documentacion y comunicacion del equipo. |
| Agente Efimero | Subagente creado para una tarea especifica que debe retirarse al completar su proposito. No se registra en `registry.json`. |
| Trunk-Based Development | Modo de branching por defecto donde `main` es siempre desplegable y las ramas son de vida corta. |
| GitFlow | Modo de branching opt-in para proyectos con releases versionados. Requiere declaracion en ADR y en `.xdd/gitflow.mode`. |
| Deuda Tecnica Declarada | Solucion suboptima documentada en `memoria.md` con justificacion, impacto estimado y sprint de resolucion. Distinta de deuda tecnica no planificada, que esta prohibida. |
| Consolidacion | Proceso del orquestador que unifica resultados de agentes paralelos, resuelve conflictos y verifica consistencia antes de presentar al usuario. |
| Invariante | Regla del protocolo Git no negociable en ningun modo de operacion: proteccion de main, tests verdes obligatorios, Conventional Commits. |
| Pipeline X-DD | Flujo de 6 fases con gates entre cada fase: Briefing, Spec, Plan, Build, QA, Retro. |
| DOC_STANDARD.md | Estandar de calidad documental v2.0. Define umbrales minimos de lineas, diagramas Mermaid obligatorios, cero emojis y trazabilidad bidireccional. |
| APROBADO | La unica instruccion valida para transicion entre fases del pipeline. Debe ser emitida por el usuario humano, no por ningun agente. |
| SSoT | Single Source of Truth. `./prompts/agents/` es el SSoT de agentes. `DOMAIN.md` es el SSoT del vocabulario de dominio. `memoria.md` es el SSoT del estado del proyecto. |
| Agente Auditor | Agente distinto al writer que verifica la conformidad de un artefacto con DOC_STANDARD.md. La identidad writer != auditor es un invariante del protocolo de documentacion. |

---

## PROCEDIMIENTO DE ENMIENDA

### Quien puede proponer una enmienda

Cualquier participante del ecosistema X-DD (usuario humano, desarrollador del framework, agente con autoridad de orquestador) puede proponer una enmienda a esta Constitucion. Las propuestas de enmienda deben formularse como un ADR (Architecture Decision Record) en `docs/adr/NNNN-enmienda-constitucion-vN.md` siguiendo el formato estandar del ecosistema.

Una enmienda no puede contradecir los principios fundamentales de DOC_STANDARD.md v2.0. Si una enmienda propuesta entra en conflicto con DOC_STANDARD.md, la enmienda debe actualizar simultaneamente ambos documentos o debe justificar explicitamente por que DOC_STANDARD.md debe subordinarse a la nueva norma constitucional.

### Como ratificar una enmienda

El proceso de ratificacion requiere los siguientes pasos en orden:

1. Abrir un PR desde una rama `docs/enmienda-constitucion-vN` con el ADR y el borrador de la Constitucion modificada.
2. El ADR debe incluir: motivacion de la enmienda, analisis de impacto sobre los articulos existentes, propuesta de redaccion nueva y tabla de comparacion antes/despues.
3. El gate de CI debe estar verde: cero emojis, diagramas Mermaid presentes, umbral de 200 lineas superado, estructura de 9 articulos con 2 subsecciones cada uno verificada.
4. El usuario humano emite `"APROBADO"` sobre el PR de enmienda.
5. El merge se realiza a `main` con squash merge y mensaje de commit `docs(constitucion): enmienda vN.N.N — [descripcion breve]`.

### Version bumping

La version de la Constitucion sigue Semantic Versioning con la siguiente semantica:

| Tipo de cambio | Incremento | Ejemplo |
|---|---|---|
| Nuevo articulo o cambio de jerarquia de normas | Major | v1.5 -> v2.0 |
| Expansion de articulo existente, nuevas subsecciones | Minor | v2.0 -> v2.1 |
| Correcciones de redaccion, aclaraciones sin cambio normativo | Patch | v2.1 -> v2.1.1 |

Toda enmienda ratificada actualiza el campo `**Version:**` en el encabezado de este documento y el campo `**Ultima revision:**` con la fecha ISO 8601 del merge. El historial completo de versiones es trazable mediante el log de Git del archivo `docs/constitucion.md`.

---

**Version:** 2.0.0 | **Sistema:** X-DD | **Ultima revision:** 2026-06-04 | **Conforme a:** DOC_STANDARD.md v2.0
