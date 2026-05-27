<div align="center">

# 🚀 X-DD

<sub>🌐 **Idiomas:** [🇪🇸 Español](README.md) · [🇺🇸 English](README.en.md) · [🇧🇷 Português](README.pt-BR.md)</sub>

## Desarrollo AI-powered con disciplina formal — sin sacrificar velocidad

**Pipeline gated · Firma criptográfica · Multi-IDE · Dogfooding visible**

Para equipos que ya usan Claude Code, Cursor u OpenCode y buscan **cero deuda técnica** + **audit trail criptográfico** + **agentes que aprenden solos**.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT%20pure-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-160%2B%20✓-brightgreen?style=for-the-badge)](tests/)
[![Workflows](https://img.shields.io/badge/workflows-51-blue?style=for-the-badge)](.agent/workflows/)
[![Agents](https://img.shields.io/badge/agents-180-orange?style=for-the-badge)](docs/equipo.md)
[![ADRs](https://img.shields.io/badge/ADRs-11-purple?style=for-the-badge)](docs/adr/)

<br/>

### 🎯 [**Comienza en 4 minutos →**](#-4-minutos-para-comenzar)

<sub>Compatible con **13+ IDEs/asistentes IA**. Sin vendor lock-in. Sin trampas ocultas.</sub>

</div>

---

## 💔 El problema conocido

```text
❌ Vibe-coding puro                    ❌ Proceso pesado tradicional

   ⚡ velocidad inicial alta             🐌 burocracia anti-IA
   💸 deuda técnica explota mes 3        🥱 no aprovecha velocidad agentes
   🔍 decisiones inauditables             📋 friction sin valor
   🐛 bugs en producción                  ⏰ time-to-ship lento
```

**Resultado:** equipos atrapados entre velocidad y calidad.

---

## ✨ La solución X-DD

**Pipeline gated de 6 fases con firma criptográfica HMAC.** Velocidad agéntica + auditabilidad enterprise.

> *"Cerebro grande. Proceso formal. Salida concisa."*

```mermaid
flowchart LR
    B["📋 Briefing"] -->|"🔒 HMAC"| S["🎨 Spec"]
    S -->|"🔒 HMAC"| P["📊 Plan"]
    P -->|"🔒 HMAC"| BUILD["⚙️ Build"]
    BUILD -->|"🔒 HMAC"| Q["🛡️ QA"]
    Q -->|"🔒 HMAC"| R["📚 Retro"]
    R -.->|"🧠 Learning Loop"| B

    classDef fase fill:#e1f5ff,stroke:#0066cc,stroke-width:3px,color:#000
    class B,S,P,BUILD,Q,R fase
```

Cada flecha = **transición firmada HMAC-SHA256**. Sin firma = sin paso. **Auditable. No editable.**

---

## 🎁 Lo que obtienes

<table>
<tr>
<td width="33%" align="center" valign="top">

### 🔒 Audit trail<br/>**criptográfico**

Cada gate firmado HMAC-SHA256.<br/>"APROBADO" auditable, no editable.<br/>**Único en el espacio.**

*Ningún competidor lo tiene.*

</td>
<td width="33%" align="center" valign="top">

### 🚀 Velocidad<br/>**sin caos**

180 agentes especializados.<br/>51 workflows production-ready.<br/>**Disciplina con velocidad agéntica.**

*De idea a release con firma.*

</td>
<td width="33%" align="center" valign="top">

### 🌍 Cualquier<br/>**IDE/Asistente**

13+ soportados vía MCP.<br/>Sin vendor lock-in.<br/>**1 framework, todos los agentes.**

*Claude, Cursor, OpenCode, Continue, Zed, Windsurf, Antigravity, Codex, Gemini...*

</td>
</tr>
</table>

---

## 💎 Números que importan

<div align="center">

| 📊 Métrica | Valor |
|---|---|
| Tests verdes | **160+** (pytest + bats + E2E) |
| Workflows production | **51** ejecutables como slash commands |
| Agentes especializados | **180** en 15 categorías |
| ADRs Nygard documentados | **11** decisiones arquitectónicas |
| Hooks event-driven | **8** (security + quality + learning) |
| Install profiles | **6** (minimal → full) |
| IDEs soportados | **13+** (Claude Code, Cursor, OpenCode, Continue, Zed, Cline, Windsurf, Antigravity, Codex, Gemini, Qwen, Hermes, Copilot...) |
| Sprints cerrados | **15** (dogfooding visible público) |
| AgentShield audit propio | **0 crit/high** con `--severity=high` ✅ |

</div>

---

## ⚡ 4 minutos para comenzar

```mermaid
flowchart LR
    A["🔍 1. doctor (30s)"] --> B["📦 2. init (1 min)"]
    B --> C["🚀 3. start (30s)"]
    C --> D["💬 4. comando /xdd (arranca)"]

    classDef step fill:#fff4e1,stroke:#cc8800,color:#000,stroke-width:2px
    class A,B,C,D step
```

```bash
# Linux / macOS / WSL
bash scripts/xdd-doctor.sh                              # 1) verifica entorno
bash scripts/xdd-init.sh /tu/proyecto --profile=core    # 2) bootstrap
cd /tu/proyecto && bash scripts/xdd-start.sh            # 3) arranca MemPalace + GitNexus + orquestador
# 4) en tu IDE/asistente: escribir el comando /xdd      # 4) pipeline empieza

# Windows
.\install.ps1 -Dest C:\proyectos\mi-app -Profile core
```

**¿Bloqueado?** El doctor indica exactamente qué falta.

---

## 🎬 Casos de uso reales (no slides)

<details open>
<summary><b>🚀 Caso 1: Publicar una feature de checkout (3 días → 1 día con X-DD)</b></summary>

```mermaid
flowchart TD
    U["👤 PM: agregar checkout v2"] --> CMD["comando /xdd"]
    CMD --> F1["Fase 1: comando /fase-requisitos<br/>📄 SPEC.md + FEATURES.md<br/>+ .feature stubs BDD"]
    F1 -->|"🔒"| F2["Fase 2: comando /project-architecture-gsd<br/>📐 DOMAIN.md + 🛡️ THREATS.md STRIDE"]
    F2 -->|"🔒"| F3["Fase 3: comando /plan-fases<br/>📊 PLAN.md vertical FDD"]
    F3 -->|"🔒"| F4["Fase 4: comando /xdd-build<br/>🔴→🟢→🔵 TDD + STDD"]
    F4 -->|"🔒"| F5["Fase 5: comando /qa-review<br/>SAST + DAST + BDD ejecutable"]
    F5 -->|"🔒"| F6["Fase 6: comando /cierre-fase<br/>📚 lecciones.md + comando /release-cut"]

    F5 -.->|"si falla"| F4

    classDef phase fill:#e8f4f8,stroke:#2c6e91,color:#000,stroke-width:2px
    class F1,F2,F3,F4,F5,F6 phase
```

**Resultado:** código + tests 80%+ coverage + THREATS modelado + audit trail criptográfico + release notes user-facing. **Cero deuda técnica acumulada.**

</details>

<details>
<summary><b>🛡️ Caso 2: Pentest híbrido — encuentra vulnerabilidades que el QA tradicional no ve</b></summary>

```mermaid
flowchart TD
    U["👤 Sec Engineer<br/>comando /advanced-agentic-pentesting"] --> CHK{"🔍 ¿Shannon instalado?"}

    CHK -->|"✅ Sí"| FULL["💥 Full pentest:<br/>STRIDE + source review +<br/>dynamic fuzz + verify exploits sandboxed"]
    CHK -->|"⚪ No"| DEG["🛡️ Modo degradado:<br/>STRIDE + source review estático<br/>⚠️ skip: fuzz/verify avisado"]

    FULL --> REP1["📊 Findings + PoC + patch propuesto"]
    DEG --> REP2["📊 Report parcial + how-to-enable"]

    REP1 --> AS["🔍 xdd-shield: AgentShield audit framework"]
    REP2 --> AS

    classDef ok fill:#d4edda,stroke:#28a745,color:#000,stroke-width:2px
    classDef warn fill:#fff3cd,stroke:#856404,color:#000,stroke-width:2px
    classDef report fill:#cce5ff,stroke:#004085,color:#000,stroke-width:2px
    class FULL ok
    class DEG warn
    class REP1,REP2 report
```

**Resultado:** apps con SAST + DAST + threat model + exploits sandbox + parches verificados. Shannon CLI es **opcional** (AGPL-3.0 con consentimiento del usuario). Sin Shannon, X-DD degrada elegantemente.

</details>

<details>
<summary><b>🎨 Caso 3: White-labeling — distribuye X-DD como tu producto interno</b></summary>

```mermaid
flowchart LR
    YML["xdd.profile.yml<br/>branding:<br/>  ecosystem_name: Helios<br/>  orchestrator_trigger: helios<br/>  persona.tone: formal"] --> BRAND["bash scripts/xdd-brand.sh"]
    BRAND --> SYM[".claude/commands/helios.md<br/>symlink xdd.md"]
    BRAND --> PER[".claude/orchestrator-persona.md<br/>persona formal"]
    BRAND --> CFG[".claude/branding.json<br/>config activa"]

    SYM --> USE["💬 Helios, publica esta feature<br/>tono corporativo formal"]

    classDef config fill:#f3e5f5,stroke:#6a1b9a,color:#000,stroke-width:2px
    classDef out fill:#e0f7fa,stroke:#006064,color:#000,stroke-width:2px
    class YML config
    class USE out
```

**Resultado:** tu organización tiene "Helios" (o el nombre que elijas). Atribución X-DD upstream automática. 4 personas presets: technical / friendly / casual / formal. **Una organización = una identidad.**

</details>

<details>
<summary><b>🧠 Caso 4: Continuous Learning — el sistema mejora solo</b></summary>

```mermaid
flowchart TD
    SES["💻 Sesión agéntica activa"] -->|"hook Stop"| EXT["stop-pattern-extraction"]
    EXT --> DB[("🗄️ ~/.xdd/state.db<br/>SQLite instincts")]
    DB -->|"tras N sesiones"| ACC["Instincts con<br/>confidence +0.1/occ"]

    ACC --> EVOL["comando /evolve workflow"]
    EVOL --> CLUST["🧬 TF-IDF clustering<br/>cosine similarity"]
    CLUST --> PROP["💡 Propuestas:<br/>command/skill/agent nuevos"]

    PROP --> HUM{"👤 Aprobación humana<br/>T6.1 mitigación"}
    HUM -->|"✅ Aprobado"| GEN["Genera artefacto<br/>en .agent/workflows o skills/"]
    HUM -->|"❌ Rechazado"| REJ["Marca rejected en SQLite"]

    GEN --> COMMIT["Commit + cierre-fase<br/>Sistema crece"]

    classDef hook fill:#fff0e6,stroke:#cc6600,color:#000,stroke-width:2px
    classDef human fill:#ffe6e6,stroke:#cc0000,color:#000,stroke-width:2px
    class EXT,EVOL hook
    class HUM human
```

**Resultado:** después de 50 sesiones, X-DD aprendió tus patrones y sugiere skills/agents nuevos. **NUNCA auto-promueve. El humano firma cada decisión.**

</details>

<details>
<summary><b>🏢 Caso 5: Multi-agent orchestration — un equipo virtual completo</b></summary>

```mermaid
flowchart TD
    CMD["comando /orchestrate --pattern=feature_squad"] --> LEAD["👔 Lead:<br/>product-manager"]
    LEAD -->|"parallel_then_sync"| P1["🏗️ engineering-backend-architect"]
    LEAD -->|"parallel_then_sync"| P2["🎨 design-ui-designer"]
    LEAD -->|"parallel_then_sync"| P3["🧪 testing-test-results-analyzer"]
    P1 --> SYNC{"🤝 sync_point:<br/>spec_approval"}
    P2 --> SYNC
    P3 --> SYNC
    SYNC --> DONE["✅ Spec consensuado"]

    classDef lead fill:#e1bee7,stroke:#6a1b9a,color:#000,stroke-width:2px
    classDef spec fill:#bbdefb,stroke:#1565c0,color:#000,stroke-width:2px
    class LEAD lead
    class P1,P2,P3 spec
```

**Resultado:** PM + Backend + UI + QA colaborando en paralelo. Sync formal. **Reemplaza standup de 30 min por workflow ejecutable.**

</details>

---

## 🏆 ¿Por qué X-DD vs alternativas?

<div align="center">

**El espacio está poblado. Pero solo X-DD combina disciplina formal + firma criptográfica + dogfooding visible.**

</div>

| Capacidad | **X-DD** | Spec-Kit (106k⭐) | OpenSpec (51k⭐) | BMAD (48k⭐) | Mastra (24k⭐) |
|---|---|---|---|---|---|
| Pipeline gated formal 6 fases | ✅ | parcial 4 fases | ❌ "fluid" | ❌ | ❌ |
| **🔒 Gate firmado HMAC** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| **🛡️ DOMAIN + THREATS Fase 2** | **✅ obligatorio** | ❌ | ❌ | ❌ | ❌ |
| **🔍 AgentShield audit propio** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| **📖 Dogfooding visible commiteable** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| 11 ADRs Nygard formales | ✅ | parcial | ❌ | ❌ | ❌ |
| MCP server propio | ✅ 6 tools | ❌ | ❌ | ❌ | ✅ |
| Multi-IDE | ✅ 13+ | ✅ 30+ | ✅ 25+ | ✅ varios | ✅ |
| Continuous Learning (instincts) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Eval-harness 5 grader types | ✅ | ❌ | ❌ | ❌ | ✅ |
| Multi-agent orchestration runtime | ✅ | ❌ | ❌ | Party Mode | ✅ |
| White-labeling per-org | ✅ + personas | parcial | ❌ | ❌ | ❌ |
| **License purity** | **MIT pure** | MIT | MIT | NOASSERT ⚠️ | NOASSERT ⚠️ |

<div align="center">

**Spec-Kit tiene 106k stars. X-DD recién arranca. Pero X-DD es el único con audit trail criptográfico real.**

</div>

---

## 🎨 Persona × Compresión — adapta X-DD a tu cultura

White-labeling (Sprint 13) + xdd-talk-compact (Sprint 10) = matriz 4×4 combinable:

|  | `technical` | `friendly` | `casual` | `formal` |
|---|---|---|---|---|
| `compact: off` | default | accesible | informal | corporativo |
| `compact: lite` | sin filler | + emojis ok | menos formal | profesional concentrado |
| `compact: standard` | concise | conversacional breve | shortcuts | ejecutivo |
| `compact: ultra` | telegraphic | shortcuts emoji | caveman | conciso ejecutivo |

**Startup casual:** `casual + ultra`. **Fintech regulada:** `formal + standard`. **Consultora dev:** `technical + lite`.

---

## 🔌 Compatible con cualquier asistente IA

```mermaid
flowchart LR
    XDD["🧠 X-DD"] --> MCP["📡 xdd-mcp-server<br/>6 tools"]
    XDD --> A1["xdd-adapt claude-code"]
    XDD --> A2["xdd-adapt opencode"]

    A1 --> CC["💻 Claude Code"]
    A2 --> OC["💻 OpenCode"]

    MCP --> IDES["💎 Cursor / Continue / Zed /<br/>Cline / Roo Code / Windsurf /<br/>Antigravity / Codex / Gemini /<br/>Qwen / Hermes / VSCode /<br/>cualquier IDE MCP-compatible"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef bridge fill:#90caf9,stroke:#1565c0,color:#000,stroke-width:2px
    classDef ide fill:#a5d6a7,stroke:#2e7d32,color:#000,stroke-width:2px
    class XDD core
    class MCP,A1,A2 bridge
    class CC,OC,IDES ide
```

**1 MCP server compartido vs N adapters per-IDE.** Mantenibilidad sostenible. Sin vendor lock-in.

---

## 📦 Elige tu nivel — escala con la necesidad

<table>
<tr>
<th>Perfil</th><th>Para qué</th><th>Comando</th>
</tr>
<tr>
<td><b>🌱 minimal</b></td>
<td>Probar X-DD sin compromiso</td>
<td><code>--profile=minimal</code></td>
</tr>
<tr>
<td><b>⭐ core</b></td>
<td><b>Recomendado para comenzar</b></td>
<td><code>--profile=core</code></td>
</tr>
<tr>
<td><b>🚀 developer</b></td>
<td>Dev activo con IA</td>
<td><code>--profile=developer</code></td>
</tr>
<tr>
<td><b>🛡️ security</b></td>
<td>SecDD focus</td>
<td><code>--profile=security</code></td>
</tr>
<tr>
<td><b>🔬 research</b></td>
<td>Eval + continuous learning</td>
<td><code>--profile=research</code></td>
</tr>
<tr>
<td><b>💎 full</b></td>
<td>Adopción completa</td>
<td><code>--profile=full</code></td>
</tr>
</table>

---

## 🌳 ¿Qué metodologías usar? — árbol de decisión

```mermaid
flowchart TD
    START{"Tipo de cambio"} -->|"Bugfix menos de 10 líneas"| DIR["⚡ DIRECTO<br/>sin pipeline"]
    START -->|"Bugfix más de 20 líneas"| MIN["📋 MÍNIMO<br/>SDD + TDD"]
    START -->|"Tool interna / script"| AGI["🛠️ ÁGIL<br/>FDD + SDD + TDD"]
    START -->|"Feature con cliente"| STD["📦 ESTÁNDAR<br/>FDD + SDD + ATDD + BDD + TDD + SecDD"]
    START -->|"Módulo con lógica compleja"| FULL["🏛️ COMPLETO<br/>FDD + DDD + SDD + BDD + ATDD<br/>+ TDD + Threat + STDD + SecDD"]

    classDef path fill:#fff9c4,stroke:#f57f17,color:#000,stroke-width:2px
    class DIR,MIN,AGI,STD,FULL path
```

**Constitución X-DD Art. 8:** no toda tarea necesita el pipeline completo. **Adaptable, no rígido.**

---

## ⚠️ Lo que X-DD NO es (honestidad)

- ❌ **No es un framework de aplicación.** No reemplaza React/Express/Django.
- ❌ **No es un test runner.** Orquesta Vitest/Playwright/pytest.
- ❌ **No es MemPalace.** Lo consume como dep externa MIT opcional.
- ❌ **No requiere Claude Code.** Funciona con 13+ asistentes vía MCP.
- ❌ **No envía datos a la nube.** Local-first. El código no sale del equipo.
- ❌ **No es compatible con monorepos sin adaptación** (roadmap Sprint 15).

---

## 🛡️ Principios de gobernanza

- 🎯 **Ambigüedad Cero** — el sistema se detiene si hay parámetros indefinidos
- 🔒 **Gated Pipeline** — `"APROBADO"` firmado HMAC-SHA256 ([ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md))
- 📐 **Spec First** — no existe `src/` sin `SPEC.md` previo aprobado
- 🧪 **TDD First** — no existe función de negocio sin su test previo
- 🌍 **Portabilidad Absoluta** — sin rutas absolutas; todo relativo a `./`
- 👁️ **Dogfooding Visible** — X-DD pasa por sus 6 fases en público ([ADR-0001](docs/adr/0001-dogfooding-visible-commiteable.md))

---

## 🔗 Integraciones externas opcionales

```mermaid
flowchart TB
    XDD["🧠 X-DD core<br/>MIT pure"]

    XDD -.->|"memoria semántica"| MP["🏛️ MemPalace<br/>MIT · 52.8k ⭐<br/>96-99% recall benchmarks<br/>29 MCP tools"]
    XDD -.->|"code intelligence<br/>recomendado"| GN["🧬 GitNexus<br/>PolyForm Noncomm ⚠️ · 40.5k ⭐<br/>AST grafo 14 langs<br/>16 MCP tools"]
    XDD -.->|"pentest dinámico<br/>opcional"| SH["🛡️ Shannon CLI<br/>AGPL-3.0 ⚠️ · 43k ⭐<br/>White-box exploits sandboxed"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef ext fill:#e8f5e9,stroke:#388e3c,color:#000,stroke-width:2px
    classDef warn fill:#ffebee,stroke:#c62828,color:#000,stroke-width:2px
    class XDD core
    class MP ext
    class GN warn
    class SH warn
```

> ⚠️ **GitNexus es PolyForm Noncommercial 1.0.0.** Uso personal/research/non-profit gratis. Comercial requiere paid license. X-DD nunca lo bundle. Disclaimer en [ADR-0033](docs/adr/0033-gitnexus-tier1-companion.md) + [DEPENDENCIES.md](DEPENDENCIES.md).
>
> ⚠️ **Shannon es AGPL-3.0.** Tu proyecto X-DD **NO se contamina** por usar Shannon vía wrapper híbrido. X-DD nunca lo bundle. La decisión es tuya. Disclaimer completo en [docs/PENTEST.md](docs/PENTEST.md).

---

## 📚 Documentación según tu rol

<table>
<tr>
<th>Si eres...</th>
<th>Comienza aquí</th>
</tr>
<tr>
<td>🆕 <b>Developer nuevo</b></td>
<td><a href="the-shortform-guide.md"><code>the-shortform-guide.md</code></a> · 15 min Quickstart visual</td>
</tr>
<tr>
<td>🔬 <b>Power user / Architect</b></td>
<td><a href="the-longform-guide.md"><code>the-longform-guide.md</code></a> · Referencia exhaustiva</td>
</tr>
<tr>
<td>🛡️ <b>Security engineer</b></td>
<td><a href="the-security-guide.md"><code>the-security-guide.md</code></a> · Threat model + SecDD + hardening</td>
</tr>
<tr>
<td>🎨 <b>Org adopter / branding</b></td>
<td><a href="docs/BRANDING.md"><code>docs/BRANDING.md</code></a> · White-labeling + 4 personas</td>
</tr>
<tr>
<td>🔌 <b>IDE integrator</b></td>
<td><a href="docs/MCP_INTEGRATION.md"><code>docs/MCP_INTEGRATION.md</code></a> · Setup MCP por IDE</td>
</tr>
<tr>
<td>🏛️ <b>Decision maker</b></td>
<td><a href="docs/adr/"><code>docs/adr/</code></a> · 11 ADRs Nygard explican el "por qué"</td>
</tr>
<tr>
<td>📊 <b>PM / project lead</b></td>
<td><a href="PROJ-MASTER-PLAN.md"><code>PROJ-MASTER-PLAN.md</code></a> · Gantt + sprints públicos</td>
</tr>
<tr>
<td>🤝 <b>Contributor</b></td>
<td><a href="CONTRIBUTING.md"><code>CONTRIBUTING.md</code></a> · Cómo añadir workflow/agent/skill/hook</td>
</tr>
</table>

---

## 🚀 Comienza ahora

```bash
# 1) Verifica entorno
make doctor

# 2) Bootstrap tu primer proyecto
bash scripts/xdd-init.sh /ruta/mi-proyecto --profile=core

# 3) Arranca
cd /ruta/mi-proyecto && bash scripts/xdd-start.sh

# 4) En tu IDE/asistente IA: escribir el comando /xdd
```

**¿Quieres ver X-DD aplicado a sí mismo?** Revisa [`.xdd/`](.xdd/) — 6 fases firmadas, públicas, auditables.

---

<div align="center">

### 🌟 X-DD es para ti si...

✅ Quieres **velocidad agéntica** + **disciplina formal**
✅ Necesitas **audit trail criptográfico** para compliance
✅ Trabajas en **equipo multi-IDE** (Claude Code + Cursor + ...)
✅ Te importa **dogfooding visible** sobre marketing
✅ Prefieres **MIT puro** sobre licencias ambiguas
✅ Quieres un framework **que mejora solo** (instincts + /evolve)

<br/>

### 🚫 X-DD NO es para ti si...

❌ Quieres **vibe-coding sin disciplina** (usa Claude Code directo)
❌ Tu organización **rechaza disciplina formal** de proceso
❌ Necesitas **dashboard web** hoy (roadmap v0.2.0)
❌ Quieres **lock-in en un solo IDE** (X-DD es multi-IDE por diseño)

<br/>

---

<sub>**X-DD** · *Cross-Driven Development System* · MIT · Build with discipline, ship with speed.</sub>

[⭐ Star en GitHub](https://github.com/Cucholambr3ta/x-dd) ·
[📖 Quickstart 15min](the-shortform-guide.md) ·
[🐛 Issues](https://github.com/Cucholambr3ta/x-dd/issues) ·
[🤝 Contribuir](CONTRIBUTING.md) ·
[💬 Discussions](https://github.com/Cucholambr3ta/x-dd/discussions)

</div>
