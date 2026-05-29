<div align="center">

# 🚀 X-DD

<sub>🌐 **Idiomas:** [🇪🇸 Español](README.md) · [🇺🇸 English](README.en.md) · [🇧🇷 Português](README.pt-BR.md)</sub>

## Desenvolvimento AI-powered com disciplina formal — sem sacrificar velocidade

**Pipeline gated · Assinatura criptográfica · Multi-IDE · Dogfooding visível**

Para times que já usam Claude Code, Cursor ou OpenCode e buscam **zero dívida técnica** + **trilha de auditoria criptográfica** + **agentes que aprendem sozinhos**.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT%20pure-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1.0--pre--release-orange?style=for-the-badge)](RELEASES/)
[![Tests](https://img.shields.io/badge/tests-330%2B%20✓-brightgreen?style=for-the-badge)](tests/)
[![Workflows](https://img.shields.io/badge/workflows-51-blue?style=for-the-badge)](.agent/workflows/)
[![Agents](https://img.shields.io/badge/agents-180-orange?style=for-the-badge)](docs/equipo.md)
[![ADRs](https://img.shields.io/badge/ADRs-36-purple?style=for-the-badge)](docs/adr/)

<br/>

### 🎯 [**Comece em 4 minutos →**](#-4-minutos-para-começar)

<sub>Compatível com **7 IDEs auto-adapt + MCP universal**. Sem vendor lock-in. Sem armadilhas ocultas.</sub>

</div>

> ⚠️ **Pre-release (v0.1.0-rc).** Funcional + dogfooded em produção do maintainer. API/manifests/CLI podem quebrar até tag final assinada `v0.1.0`. Early adopters: pin commit SHA. Issues: [github.com/Cucholambr3ta/x-dd/issues](https://github.com/Cucholambr3ta/x-dd/issues).

---

## 💔 O problema conhecido

```text
❌ Vibe-coding puro                    ❌ Processo pesado tradicional

   ⚡ alta velocidade inicial            🐌 burocracia anti-IA
   💸 dívida técnica explode no mês 3    🥱 não aproveita velocidade dos agentes
   🔍 decisões inauditáveis              📋 fricção sem valor
   🐛 bugs em produção                   ⏰ time-to-ship lento
```

**Resultado:** times presos entre velocidade e qualidade.

---

## ✨ A solução X-DD

**Pipeline gated de 6 fases com assinatura criptográfica HMAC.** Velocidade agêntica + auditabilidade enterprise.

> *"Cérebro grande. Processo formal. Saída concisa."*

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

Cada seta = **transição assinada HMAC-SHA256**. Sem assinatura = sem avanço. **Auditável. Não editável.**

---

## 🎁 O que você ganha

<table>
<tr>
<td width="33%" align="center" valign="top">

### 🔒 Trilha de auditoria<br/>**criptográfica**

Cada gate assinado HMAC-SHA256.<br/>"APROVADO" auditável, não editável.<br/>**Único no espaço.**

*Nenhum concorrente tem.*

</td>
<td width="33%" align="center" valign="top">

### 🚀 Velocidade<br/>**sem caos**

180 agentes especializados.<br/>51 workflows production-ready.<br/>**Disciplina com velocidade agêntica.**

*De ideia a release assinado.*

</td>
<td width="33%" align="center" valign="top">

### 🌍 Qualquer<br/>**IDE/Assistente**

7 IDEs auto-config + mais via MCP.<br/>Sem vendor lock-in.<br/>**1 framework, todos os agentes.**

*Claude, Cursor, OpenCode, Continue, Zed, Windsurf, Antigravity, Codex, Gemini...*

</td>
</tr>
</table>

---

## 💎 Números que importam

<div align="center">

| 📊 Métrica | Valor |
|---|---|
| Testes verdes | **330+** (pytest + bats + E2E, S0-25) |
| Workflows produção | **51** executáveis como slash commands |
| Agentes especializados | **180** em 15 categorias |
| ADRs Nygard documentados | **36** decisões arquiteturais |
| Hooks event-driven | **8** (security + quality + learning) |
| Install profiles | **6** (minimal → full) |
| IDEs suportados | **7 auto-adapt + más vía MCP** (Claude Code, Cursor, OpenCode, VSCode+Copilot, Windsurf, Antigravity, Codex + Continue, Zed, Cline, Gemini... vía MCP) |
| Sprints fechados | **26** (dogfooding visível público, S0-25) |
| AgentShield audit próprio | **0 crit/high** com `--severity=high` ✅ |

</div>

---

## ⚡ 4 minutos para começar

```mermaid
flowchart LR
    A["🔍 1. doctor (30s)"] --> B["📦 2. init (1 min)"]
    B --> C["🚀 3. start (30s)"]
    C --> D["💬 4. comando /xdd (inicia)"]

    classDef step fill:#fff4e1,stroke:#cc8800,color:#000,stroke-width:2px
    class A,B,C,D step
```

```bash
# Linux / macOS / WSL
bash scripts/xdd-doctor.sh                              # 1) verifica ambiente
bash scripts/xdd-init.sh /seu/projeto --profile=core    # 2) bootstrap
cd /seu/projeto && bash scripts/xdd-start.sh            # 3) inicia MemPalace + GitNexus + orquestrador
# 4) no seu IDE/assistente: executar o comando /xdd     # 4) pipeline começa

# Windows
.\install.ps1 -Dest C:\projetos\meu-app -Profile core
```

**Travado?** O doctor indica exatamente o que falta.

---

## 🎬 Casos de uso reais (sem slides)

<details open>
<summary><b>🚀 Caso 1: Publicar uma feature de checkout (3 dias → 1 dia com X-DD)</b></summary>

```mermaid
flowchart TD
    U["👤 PM: adicionar checkout v2"] --> CMD["comando /xdd"]
    CMD --> F1["Fase 1: comando /fase-requisitos<br/>📄 SPEC.md + FEATURES.md<br/>+ .feature stubs BDD"]
    F1 -->|"🔒"| F2["Fase 2: comando /project-architecture-gsd<br/>📐 DOMAIN.md + 🛡️ THREATS.md STRIDE"]
    F2 -->|"🔒"| F3["Fase 3: comando /plan-fases<br/>📊 PLAN.md vertical FDD"]
    F3 -->|"🔒"| F4["Fase 4: comando /xdd-build<br/>🔴→🟢→🔵 TDD + STDD"]
    F4 -->|"🔒"| F5["Fase 5: comando /qa-review<br/>SAST + DAST + BDD executável"]
    F5 -->|"🔒"| F6["Fase 6: comando /cierre-fase<br/>📚 lecciones.md + comando /release-cut"]

    F5 -.->|"se falhar"| F4

    classDef phase fill:#e8f4f8,stroke:#2c6e91,color:#000,stroke-width:2px
    class F1,F2,F3,F4,F5,F6 phase
```

**Resultado:** código + testes 80%+ coverage + THREATS modelado + trilha de auditoria criptográfica + release notes user-facing. **Zero dívida técnica acumulada.**

</details>

<details>
<summary><b>🛡️ Caso 2: Pentest híbrido — encontra vulnerabilidades que o QA tradicional não vê</b></summary>

```mermaid
flowchart TD
    U["👤 Sec Engineer<br/>comando /advanced-agentic-pentesting"] --> CHK{"🔍 Shannon instalado?"}

    CHK -->|"✅ Sim"| FULL["💥 Full pentest:<br/>STRIDE + source review +<br/>dynamic fuzz + verify exploits sandboxed"]
    CHK -->|"⚪ Não"| DEG["🛡️ Modo degradado:<br/>STRIDE + source review estático<br/>⚠️ skip: fuzz/verify avisado"]

    FULL --> REP1["📊 Findings + PoC + patch proposto"]
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

**Resultado:** apps com SAST + DAST + threat model + exploits sandbox + patches verificados. Shannon CLI é **opcional** (AGPL-3.0 com consentimento do usuário). Sem Shannon, X-DD degrada elegantemente.

</details>

<details>
<summary><b>🎨 Caso 3: White-labeling — distribua X-DD como seu produto interno</b></summary>

```mermaid
flowchart LR
    YML["xdd.profile.yml<br/>branding:<br/>  ecosystem_name: Helios<br/>  orchestrator_trigger: helios<br/>  persona.tone: formal"] --> BRAND["bash scripts/xdd-brand.sh"]
    BRAND --> SYM[".claude/commands/helios.md<br/>symlink xdd.md"]
    BRAND --> PER[".claude/orchestrator-persona.md<br/>persona formal"]
    BRAND --> CFG[".claude/branding.json<br/>config ativa"]

    SYM --> USE["💬 Helios, publica esta feature<br/>tom corporativo formal"]

    classDef config fill:#f3e5f5,stroke:#6a1b9a,color:#000,stroke-width:2px
    classDef out fill:#e0f7fa,stroke:#006064,color:#000,stroke-width:2px
    class YML config
    class USE out
```

**Resultado:** sua organização tem "Helios" (ou o nome que escolher). Atribuição X-DD upstream automática. 4 personas presets: technical / friendly / casual / formal. **Uma organização = uma identidade.**

</details>

<details>
<summary><b>🧠 Caso 4: Continuous Learning — o sistema melhora sozinho</b></summary>

```mermaid
flowchart TD
    SES["💻 Sessão agêntica ativa"] -->|"hook Stop"| EXT["stop-pattern-extraction"]
    EXT --> DB[("🗄️ ~/.xdd/state.db<br/>SQLite instincts")]
    DB -->|"após N sessões"| ACC["Instincts com<br/>confidence +0.1/occ"]

    ACC --> EVOL["comando /evolve workflow"]
    EVOL --> CLUST["🧬 TF-IDF clustering<br/>cosine similarity"]
    CLUST --> PROP["💡 Propostas:<br/>command/skill/agent novos"]

    PROP --> HUM{"👤 Aprovação humana<br/>T6.1 mitigação"}
    HUM -->|"✅ Aprovado"| GEN["Gera artefato<br/>em .agent/workflows ou skills/"]
    HUM -->|"❌ Rejeitado"| REJ["Marca rejected no SQLite"]

    GEN --> COMMIT["Commit + cierre-fase<br/>Sistema cresce"]

    classDef hook fill:#fff0e6,stroke:#cc6600,color:#000,stroke-width:2px
    classDef human fill:#ffe6e6,stroke:#cc0000,color:#000,stroke-width:2px
    class EXT,EVOL hook
    class HUM human
```

**Resultado:** após 50 sessões, X-DD aprendeu seus padrões e sugere skills/agents novos. **NUNCA promove automaticamente. O humano assina cada decisão.**

</details>

<details>
<summary><b>🏢 Caso 5: Multi-agent orchestration — um time virtual completo</b></summary>

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

**Resultado:** PM + Backend + UI + QA colaborando em paralelo. Sync formal. **Substitui standup de 30 min por workflow executável.**

</details>

---

## 🏆 Por que X-DD vs alternativas?

<div align="center">

**O espaço está povoado. Mas só X-DD combina disciplina formal + assinatura criptográfica + dogfooding visível.**

</div>

| Capacidade | **X-DD** | Spec-Kit (106k⭐) | OpenSpec (51k⭐) | BMAD (48k⭐) | Mastra (24k⭐) |
|---|---|---|---|---|---|
| Pipeline gated formal 6 fases | ✅ | parcial 4 fases | ❌ "fluid" | ❌ | ❌ |
| **🔒 Gate assinado HMAC** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| **🛡️ DOMAIN + THREATS Fase 2** | **✅ obrigatório** | ❌ | ❌ | ❌ | ❌ |
| **🔍 AgentShield audit próprio** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| **📖 Dogfooding visível commitado** | **✅ ÚNICO** | ❌ | ❌ | ❌ | ❌ |
| 11 ADRs Nygard formais | ✅ | parcial | ❌ | ❌ | ❌ |
| MCP server próprio | ✅ 6 tools | ❌ | ❌ | ❌ | ✅ |
| Multi-IDE | ✅ 13+ | ✅ 30+ | ✅ 25+ | ✅ vários | ✅ |
| Continuous Learning (instincts) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Eval-harness 5 grader types | ✅ | ❌ | ❌ | ❌ | ✅ |
| Multi-agent orchestration runtime | ✅ | ❌ | ❌ | Party Mode | ✅ |
| White-labeling per-org | ✅ + personas | parcial | ❌ | ❌ | ❌ |
| **License purity** | **MIT pure** | MIT | MIT | NOASSERT ⚠️ | NOASSERT ⚠️ |

<div align="center">

**Spec-Kit tem 106k stars. X-DD recém começou. Mas X-DD é o único com trilha de auditoria criptográfica real.**

</div>

---

## 🎨 Persona × Compressão — adapta X-DD à sua cultura

White-labeling (Sprint 13) + xdd-talk-compact (Sprint 10) = matriz 4×4 combinável:

|  | `technical` | `friendly` | `casual` | `formal` |
|---|---|---|---|---|
| `compact: off` | default | acessível | informal | corporativo |
| `compact: lite` | sem filler | + emojis ok | menos formal | profissional concentrado |
| `compact: standard` | concise | conversacional breve | shortcuts | executivo |
| `compact: ultra` | telegraphic | shortcuts emoji | caveman | conciso executivo |

**Startup casual:** `casual + ultra`. **Fintech regulada:** `formal + standard`. **Consultoria dev:** `technical + lite`.

---

## 🔌 Compatível com qualquer assistente IA

```mermaid
flowchart LR
    XDD["🧠 X-DD"] --> MCP["📡 xdd-mcp-server<br/>6 tools"]
    XDD --> A1["xdd-adapt claude-code"]
    XDD --> A2["xdd-adapt opencode"]

    A1 --> CC["💻 Claude Code"]
    A2 --> OC["💻 OpenCode"]

    MCP --> IDES["💎 Cursor / Continue / Zed /<br/>Cline / Roo Code / Windsurf /<br/>Antigravity / Codex / Gemini /<br/>Qwen / Hermes / VSCode /<br/>qualquer IDE MCP-compatível"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef bridge fill:#90caf9,stroke:#1565c0,color:#000,stroke-width:2px
    classDef ide fill:#a5d6a7,stroke:#2e7d32,color:#000,stroke-width:2px
    class XDD core
    class MCP,A1,A2 bridge
    class CC,OC,IDES ide
```

**1 MCP server compartilhado vs N adapters per-IDE.** Manutenibilidade sustentável. Sem vendor lock-in.

---

## 📦 Escolha seu nível — escala com a necessidade

<table>
<tr>
<th>Perfil</th><th>Para que</th><th>Comando</th>
</tr>
<tr>
<td><b>🌱 minimal</b></td>
<td>Testar X-DD sem compromisso</td>
<td><code>--profile=minimal</code></td>
</tr>
<tr>
<td><b>⭐ core</b></td>
<td><b>Recomendado para começar</b></td>
<td><code>--profile=core</code></td>
</tr>
<tr>
<td><b>🚀 developer</b></td>
<td>Dev ativo com IA</td>
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
<td>Adoção completa</td>
<td><code>--profile=full</code></td>
</tr>
</table>

---

## 🌳 Quais metodologias usar? — árvore de decisão

```mermaid
flowchart TD
    START{"Tipo de mudança"} -->|"Bugfix menos de 10 linhas"| DIR["⚡ DIRETO<br/>sem pipeline"]
    START -->|"Bugfix mais de 20 linhas"| MIN["📋 MÍNIMO<br/>SDD + TDD"]
    START -->|"Tool interna / script"| AGI["🛠️ ÁGIL<br/>FDD + SDD + TDD"]
    START -->|"Feature com cliente"| STD["📦 PADRÃO<br/>FDD + SDD + ATDD + BDD + TDD + SecDD"]
    START -->|"Módulo com lógica complexa"| FULL["🏛️ COMPLETO<br/>FDD + DDD + SDD + BDD + ATDD<br/>+ TDD + Threat + STDD + SecDD"]

    classDef path fill:#fff9c4,stroke:#f57f17,color:#000,stroke-width:2px
    class DIR,MIN,AGI,STD,FULL path
```

**Constituição X-DD Art. 8:** nem toda tarefa precisa do pipeline completo. **Adaptável, não rígido.**

---

## ⚠️ O que X-DD NÃO é (honestidade)

- ❌ **Não é um framework de aplicação.** Não substitui React/Express/Django.
- ❌ **Não é um test runner.** Orquestra Vitest/Playwright/pytest.
- ❌ **Não é MemPalace.** Consome como dep externa MIT opcional.
- ❌ **Não requer Claude Code.** Funciona com 13+ assistentes via MCP.
- ❌ **Não envia dados para a nuvem.** Local-first. O código não sai do time.
- ❌ **Não é compatível com monorepos sem adaptação** (roadmap Sprint 15).

---

## 🛡️ Princípios de governança

- 🎯 **Ambiguidade Zero** — o sistema para se há parâmetros indefinidos
- 🔒 **Gated Pipeline** — `"APROBADO"` assinado HMAC-SHA256 ([ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md))
- 📐 **Spec First** — não existe `src/` sem `SPEC.md` prévio aprovado
- 🧪 **TDD First** — não existe função de negócio sem seu teste prévio
- 🌍 **Portabilidade Absoluta** — sem rotas absolutas; tudo relativo a `./`
- 👁️ **Dogfooding Visível** — X-DD passa pelas suas 6 fases em público ([ADR-0001](docs/adr/0001-dogfooding-visible-commiteable.md))

---

## 🔗 Integrações externas opcionais

```mermaid
flowchart TB
    XDD["🧠 X-DD core<br/>MIT pure"]

    XDD -.->|"memória semântica"| MP["🏛️ MemPalace<br/>MIT · 52.8k ⭐<br/>96-99% recall benchmarks<br/>29 MCP tools"]
    XDD -.->|"code intelligence<br/>recomendado"| GN["🧬 GitNexus<br/>PolyForm Noncomm ⚠️ · 40.5k ⭐<br/>AST grafo 14 langs<br/>16 MCP tools"]
    XDD -.->|"pentest dinâmico<br/>opcional"| SH["🛡️ Shannon CLI<br/>AGPL-3.0 ⚠️ · 43k ⭐<br/>White-box exploits sandboxed"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef ext fill:#e8f5e9,stroke:#388e3c,color:#000,stroke-width:2px
    classDef warn fill:#ffebee,stroke:#c62828,color:#000,stroke-width:2px
    class XDD core
    class MP ext
    class GN warn
    class SH warn
```

> ⚠️ **GitNexus é PolyForm Noncommercial 1.0.0.** Uso pessoal/research/non-profit grátis. Comercial requer paid license. X-DD nunca o bundle. Disclaimer em [ADR-0033](docs/adr/0033-gitnexus-tier1-companion.md) + [DEPENDENCIES.md](DEPENDENCIES.md).
>
> ⚠️ **Shannon é AGPL-3.0.** Seu projeto X-DD **NÃO se contamina** por usar Shannon via wrapper híbrido. X-DD nunca o bundle. A decisão é sua. Disclaimer completo em [docs/PENTEST.md](docs/PENTEST.md).

---

## 📚 Documentação conforme seu papel

<table>
<tr>
<th>Se você é...</th>
<th>Comece aqui</th>
</tr>
<tr>
<td>🆕 <b>Developer novo</b></td>
<td><a href="the-shortform-guide.md"><code>the-shortform-guide.md</code></a> · 15 min Quickstart visual</td>
</tr>
<tr>
<td>🔬 <b>Power user / Architect</b></td>
<td><a href="the-longform-guide.md"><code>the-longform-guide.md</code></a> · Referência exaustiva</td>
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
<td><a href="docs/adr/"><code>docs/adr/</code></a> · 11 ADRs Nygard explicam o "por quê"</td>
</tr>
<tr>
<td>📊 <b>PM / project lead</b></td>
<td><a href="PROJ-MASTER-PLAN.md"><code>PROJ-MASTER-PLAN.md</code></a> · Gantt + sprints públicos</td>
</tr>
<tr>
<td>🤝 <b>Contributor</b></td>
<td><a href="CONTRIBUTING.md"><code>CONTRIBUTING.md</code></a> · Como adicionar workflow/agent/skill/hook</td>
</tr>
</table>

---

## 🚀 Comece agora

```bash
# 1) Verifica ambiente
make doctor

# 2) Bootstrap seu primeiro projeto
bash scripts/xdd-init.sh /rota/meu-projeto --profile=core

# 3) Inicia
cd /rota/meu-projeto && bash scripts/xdd-start.sh

# 4) No seu IDE/assistente IA: executar o comando /xdd
```

**Quer ver X-DD aplicado a si mesmo?** Veja [`.xdd/`](.xdd/) — 6 fases assinadas, públicas, auditáveis.

---

<div align="center">

### 🌟 X-DD é para você se...

✅ Quer **velocidade agêntica** + **disciplina formal**
✅ Precisa de **trilha de auditoria criptográfica** para compliance
✅ Trabalha em **time multi-IDE** (Claude Code + Cursor + ...)
✅ Te importa **dogfooding visível** sobre marketing
✅ Prefere **MIT puro** sobre licenças ambíguas
✅ Quer um framework **que melhora sozinho** (instincts + /evolve)

<br/>

### 🚫 X-DD NÃO é para você se...

❌ Quer **vibe-coding sem disciplina** (use Claude Code direto)
❌ Sua organização **rejeita disciplina formal** de processo
❌ Precisa de **dashboard web** hoje (roadmap v0.2.0)
❌ Quer **lock-in num único IDE** (X-DD é multi-IDE por design)

<br/>

---

<sub>**X-DD** · *Cross-Driven Development System* · MIT · Build with discipline, ship with speed.</sub>

[⭐ Star no GitHub](https://github.com/Cucholambr3ta/x-dd) ·
[📖 Quickstart 15min](the-shortform-guide.md) ·
[🐛 Issues](https://github.com/Cucholambr3ta/x-dd/issues) ·
[🤝 Contribuir](CONTRIBUTING.md) ·
[💬 Discussions](https://github.com/Cucholambr3ta/x-dd/discussions)

</div>
