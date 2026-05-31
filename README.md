<div align="center">

# X-DD

**El sistema operativo para desarrollo de software asistido por IA**

**Agentes de IA que colaboran bajo reglas estrictas y firmadas — para que "lo hizo la IA" deje de significar "nadie revisó".**

[![beta](https://img.shields.io/badge/status-beta-blue)](https://github.com/Cucholambr3ta/x-dd/releases)
[![pip install](https://img.shields.io/badge/pip-install%20x--dd-blue)](#instala-en-30-segundos)
[![Constitución](https://img.shields.io/badge/Constituci%C3%B3n-v1.5-blue)](docs/constitucion.md)
[![Tests](https://img.shields.io/badge/tests-verdes%20como%20gate%20de%20CI-brightgreen)](tests/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

</div>

---

## El problema

La IA escribe código rápido. Pero "build verde" no es "producto verde": tests que no existen,
documentación inventada, fases marcadas como completas que nunca corrieron. Cuando un agente
escribe **y** aprueba su propio trabajo, nadie revisó nada.

## La solución

X-DD pone a los agentes a trabajar dentro de un **pipeline con candados criptográficos**. Cada
fase del desarrollo se valida por contenido real y se firma con HMAC. No hay "APROBADO" verbal:
hay una firma que el gate verifica, y un aprobador que no puede ser el mismo que hizo el trabajo.

```
Briefing → Spec → Plan → Build → QA → Retro
   └─ cada flecha es un gate firmado que bloquea el avance sin aprobación válida ─┘
```

## Lo que hace a X-DD distinto: 9 disciplinas, una sola corriente

X-DD no inventa una metodología nueva: **integra nueve** *-Driven Development* como capas sobre
el pipeline gated, cada una entrando en la fase donde aporta.

| Disciplina | Qué aporta | Dónde entra |
|---|---|---|
| **SDD** Spec-Driven | la spec es el contrato, no un borrador | Briefing → Spec |
| **FDD** Feature-Driven | catálogo de features trazable | Spec → Plan |
| **DDD** Domain-Driven | modelo de dominio + bounded contexts | Spec |
| **BDD / ATDD** Behavior/Acceptance | criterios ejecutables antes de codear | Plan → Build |
| **TDD** Test-Driven | tests primero, código después | Build |
| **STDD** Security-Test-Driven | tests de seguridad como ciudadanos de primera | Build → QA |
| **SecDD + Threat-Driven** | modelo de amenazas STRIDE guía el diseño | Spec + QA |

No eliges una; X-DD las **orquesta en la fase correcta**.

## Harness engineering: el agente es el 10%, el entorno es el 90%

Un buen prompt no basta. Lo que hace confiable a un agente es el **harness** que lo rodea: los
gates, los hooks, el presupuesto de contexto, la memoria y las pruebas. X-DD trata ese entorno
como ingeniería de primera clase:

- **Eval-harness** (`xdd-eval`) — 5 tipos de grader deterministas para medir agentes sin azar.
- **MockProvider** (`xdd-provider`) — corre flujos completos **sin red ni tokens**, reproducibles.
- **Hooks + context budget + observabilidad** — OTel spans, session replay, cost tracker.
- **AgentShield** (`xdd-shield`) — audita el propio framework con 13 reglas estáticas.

## Memoria y pruebas: MemPalace + Shannon

Dos integraciones externas (opcionales, nunca bundled) cubren lo que un agente solo no puede:

- **🧠 MemPalace** *(memoria semántica, MIT)* — el flight recorder del proyecto. ChromaDB + SQLite
  + 29 MCP tools para que los agentes recuerden decisiones y lecciones **entre sesiones**, no solo
  dentro de una conversación. Sin él, X-DD degrada a memoria de archivos (`memoria.md`/`lecciones.md`).

- **🎯 Shannon** *(pentest dinámico, AGPL)* — pruebas de seguridad reales: white-box, exploits en
  sandbox, *verify findings* contra el código corriendo. Integrado vía `xdd-pentest.sh`. Sin él,
  X-DD degrada elegantemente a STRIDE + revisión estática de fuente.

> Ambas son **dependencias externas declaradas** ([DEPENDENCIES.md](DEPENDENCIES.md)), nunca
> incrustadas: tu proyecto MIT no se contamina con sus licencias. Instalarlas es decisión tuya.

## Por qué importa

| En vez de… | X-DD te da… |
|---|---|
| "confía en que la IA lo hizo bien" | un gate que **parsea el artefacto** (tests N>0, evidencia de ejecución, placeholders resueltos) |
| el agente que escribe también aprueba | **aprobador ≠ autor**, firmado criptográficamente |
| "el .md existe, listo" | validación de **flujos ejecutados** end-to-end (`xdd-flow`), no solo de archivos |
| copiar prompts entre IDEs a mano | **7 IDEs** desde una sola fuente (Claude Code, Cursor, opencode, Windsurf, Copilot, Antigravity, Codex) |
| 180 prompts sueltos | un **registry tipado** de 180 agentes especializados |
| probar agentes gastando tokens | **MockProvider determinista** — testea flujos sin red ni costo |

## ¿Por qué X-DD y no otro framework?

| | X-DD | wshobson/agents | catlog22/Claude-Code-Workflow | prompt-repo genérico |
|---|---|---|---|---|
| **Gobernanza de fases** | ✅ 6 fases + gate HMAC | ❌ | ❌ | ❌ |
| **Aprobador ≠ autor** | ✅ firmado criptográfico | ❌ | ❌ | ❌ |
| **9 metodologías integradas** | ✅ SDD+FDD+BDD+TDD+… | parcial | parcial | ❌ |
| **Validación de ejecución real** | ✅ `xdd-flow` | ❌ | ❌ | ❌ |
| **Dogfooding real** | ✅ X-DD se desarrolla con X-DD | ❌ | ❌ | ❌ |
| **7 IDEs desde una fuente** | ✅ | parcial | ❌ | ❌ |
| **Modo degradado documentado** | ✅ Base / Completo | ❌ | ❌ | ❌ |

La diferencia real: los otros frameworks son *colecciones de prompts*. X-DD es un **pipeline gated**
donde "APROBADO" tiene firma criptográfica, el aprobador no puede ser el autor, y cada check
valida ejecución real, no archivos.

## Historial de validación

X-DD se desarrolla **con su propio pipeline** — cada sprint pasa por las 6 fases (Briefing→Spec→Plan→Build→QA→Retro) antes de llegar a `main`. Las lecciones aprendidas se acumulan en [`lecciones.md`](lecciones.md), que el agente consulta antes de proponer soluciones para no repetir errores. Hoy: **50+ lecciones acumuladas**, **4+ proyectos paralelos validados**.

## Instala en 30 segundos

### Modo Base (< 2 minutos) — pipeline completo, sin dependencias extra

```bash
pip install x-dd             # o: pipx install x-dd
xdd init /ruta/a/tu/proyecto
xdd doctor                   # diagnóstico: [MODO: BASE]
```

El pipeline completo funciona: workflows, agentes, gate HMAC, 7 IDEs.
Lo que se pierde: continuidad semántica automática entre sesiones (ver [docs/modos.md](docs/modos.md)).

### Modo Completo (~10 minutos) — + MemPalace (memoria semántica)

```bash
pip install x-dd mempalace
mempalace init /ruta/a/tu/proyecto
xdd init /ruta/a/tu/proyecto
xdd doctor                   # diagnóstico: [MODO: COMPLETO]
```

Con MemPalace el agente recuerda el proyecto entre sesiones.

## Qué hay dentro

- **🔐 Gate keeper HMAC-SHA256** — cada transición de fase se firma; el gate detecta manipulación.
- **▶️ Gate ejecutable** — `xdd-flow` corre flujos de agentes y valida su salida real, no su existencia.
- **🧪 CI como ley** — pytest + bats + AgentShield corren como gate en cada PR (Constitución Art. 7).
- **🛡️ AgentShield** — audit estático de seguridad del propio framework: 13 reglas.
- **🎨 White-labeling** — renombra el orquestador y su persona por proyecto.
- **📊 Observabilidad** — spans OTel, session replay, cost tracker, context budget.

## Filosofía

X-DD se construye a sí mismo con su propio pipeline (*dogfooding*). Cada decisión vive en un
[ADR](docs/adr/) (47 y contando). La [Constitución](docs/constitucion.md) es la ley; el gate la
hace cumplir. No prometemos calidad: la bloqueamos cuando falta.

## Empieza

- 📖 [Constitución](docs/constitucion.md) — la ley, 9 artículos
- 🚀 [INSTALL](INSTALL.md) — instalación, perfiles, pip
- 🧭 [Guía de Integración](docs/X-DD_Integration_Guide.md) — el pipeline completo
- 🏛️ [ADRs](docs/adr/) — por qué X-DD es como es
- 🛠️ [Guías de desarrollo](docs/dev/) — cómo crear agentes/skills/workflows (material interno)

> **v0.2:** el MCP server propio se elimina en esta versión ([ADR-0044](docs/adr/0044-deprecar-mcp-no-necesario.md)); la copia real a 7 IDEs lo reemplaza sin pérdida de funcionalidad.

---

<div align="center">

**X-DD — la IA escribe, el pipeline responde.**

[Empezar](#instala-en-30-segundos) · [Documentación](docs/) · [Licencia MIT](LICENSE)

</div>
