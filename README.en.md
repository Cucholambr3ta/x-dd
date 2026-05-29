<div align="center">

# 🚀 X-DD

<sub>🌐 **Languages:** [🇪🇸 Español](README.md) · [🇺🇸 English](README.en.md) · [🇧🇷 Português](README.pt-BR.md)</sub>

## AI-powered development with formal discipline — without sacrificing speed

**Gated pipeline · Cryptographic signing · Multi-IDE · Visible dogfooding**

For teams already using Claude Code, Cursor, or OpenCode who want **zero technical debt** + **cryptographic audit trail** + **agents that learn on their own**.

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT%20pure-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1.0--pre--release-orange?style=for-the-badge)](RELEASES/)
[![Tests](https://img.shields.io/badge/tests-330%2B%20✓-brightgreen?style=for-the-badge)](tests/)
[![Workflows](https://img.shields.io/badge/workflows-51-blue?style=for-the-badge)](.agent/workflows/)
[![Agents](https://img.shields.io/badge/agents-180-orange?style=for-the-badge)](docs/equipo.md)
[![ADRs](https://img.shields.io/badge/ADRs-36-purple?style=for-the-badge)](docs/adr/)

<br/>

### 🎯 [**Get started in 4 minutes →**](#-4-minutes-to-start)

<sub>Compatible with **7 IDEs auto-adapt + universal MCP**. No vendor lock-in. No hidden traps.</sub>

</div>

> ⚠️ **Pre-release (v0.1.0-rc).** Functional + dogfooded in maintainer's production. API/manifests/CLI may break until final signed tag `v0.1.0`. Early adopters: pin commit SHA. Issues: [github.com/Cucholambr3ta/x-dd/issues](https://github.com/Cucholambr3ta/x-dd/issues).

---

## 💔 The known problem

```text
❌ Pure vibe-coding                    ❌ Traditional heavy process

   ⚡ high initial velocity              🐌 anti-AI bureaucracy
   💸 tech debt explodes by month 3      🥱 doesn't leverage agent speed
   🔍 unauditable decisions              📋 friction without value
   🐛 production bugs                    ⏰ slow time-to-ship
```

**Result:** teams trapped between speed and quality.

---

## ✨ The X-DD solution

**6-phase gated pipeline with HMAC cryptographic signing.** Agentic speed + enterprise auditability.

> *"Big brain. Formal process. Concise output."*

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

Each arrow = **HMAC-SHA256 signed transition**. No signature = no progression. **Auditable. Non-editable.**

---

## 🎁 What you get

<table>
<tr>
<td width="33%" align="center" valign="top">

### 🔒 Cryptographic<br/>**audit trail**

Every gate HMAC-SHA256 signed.<br/>"APPROVED" auditable, non-editable.<br/>**Unique in the space.**

*No competitor has it.*

</td>
<td width="33%" align="center" valign="top">

### 🚀 Speed<br/>**without chaos**

180 specialized agents.<br/>51 production-ready workflows.<br/>**Discipline with agentic speed.**

*From idea to signed release.*

</td>
<td width="33%" align="center" valign="top">

### 🌍 Any<br/>**IDE/Assistant**

7 IDEs auto-config + more via MCP.<br/>No vendor lock-in.<br/>**1 framework, all agents.**

*Claude, Cursor, OpenCode, Continue, Zed, Windsurf, Antigravity, Codex, Gemini...*

</td>
</tr>
</table>

---

## 💎 Numbers that matter

<div align="center">

| 📊 Metric | Value |
|---|---|
| Green tests | **330+** (pytest + bats + E2E, S0-25) |
| Production workflows | **51** runnable as slash commands |
| Specialized agents | **180** in 15 categories |
| Nygard ADRs documented | **36** architectural decisions |
| Event-driven hooks | **8** (security + quality + learning) |
| Install profiles | **6** (minimal → full) |
| Supported IDEs | **7 auto-adapt + más vía MCP** (Claude Code, Cursor, OpenCode, VSCode+Copilot, Windsurf, Antigravity, Codex + Continue, Zed, Cline, Gemini... vía MCP) |
| Closed sprints | **26** (public visible dogfooding, S0-25) |
| AgentShield self-audit | **0 crit/high** with `--severity=high` ✅ |

</div>

---

## ⚡ 4 minutes to start

```mermaid
flowchart LR
    A["🔍 1. doctor (30s)"] --> B["📦 2. init (1 min)"]
    B --> C["🚀 3. start (30s)"]
    C --> D["💬 4. run /xdd command (kickoff)"]

    classDef step fill:#fff4e1,stroke:#cc8800,color:#000,stroke-width:2px
    class A,B,C,D step
```

```bash
# Linux / macOS / WSL
bash scripts/xdd-doctor.sh                              # 1) verify environment
bash scripts/xdd-init.sh /your/project --profile=core   # 2) bootstrap
cd /your/project && bash scripts/xdd-start.sh           # 3) start MemPalace + GitNexus + orchestrator
# 4) in your IDE/assistant: run the /xdd command        # 4) pipeline begins

# Windows
.\install.ps1 -Dest C:\projects\my-app -Profile core
```

**Stuck?** The doctor tells you exactly what's missing.

---

## 🎬 Real use cases (no slides)

<details open>
<summary><b>🚀 Case 1: Ship a checkout feature (3 days → 1 day with X-DD)</b></summary>

```mermaid
flowchart TD
    U["👤 PM: add checkout v2"] --> CMD["run /xdd command"]
    CMD --> F1["Phase 1: run /fase-requisitos<br/>📄 SPEC.md + FEATURES.md<br/>+ BDD .feature stubs"]
    F1 -->|"🔒"| F2["Phase 2: run /project-architecture-gsd<br/>📐 DOMAIN.md + 🛡️ THREATS.md STRIDE"]
    F2 -->|"🔒"| F3["Phase 3: run /plan-fases<br/>📊 PLAN.md vertical FDD"]
    F3 -->|"🔒"| F4["Phase 4: run /xdd-build<br/>🔴→🟢→🔵 TDD + STDD"]
    F4 -->|"🔒"| F5["Phase 5: run /qa-review<br/>SAST + DAST + executable BDD"]
    F5 -->|"🔒"| F6["Phase 6: run /cierre-fase<br/>📚 lecciones.md + run /release-cut"]

    F5 -.->|"if fails"| F4

    classDef phase fill:#e8f4f8,stroke:#2c6e91,color:#000,stroke-width:2px
    class F1,F2,F3,F4,F5,F6 phase
```

**Result:** code + tests 80%+ coverage + modeled THREATS + cryptographic audit trail + user-facing release notes. **Zero accumulated tech debt.**

</details>

<details>
<summary><b>🛡️ Case 2: Hybrid pentest — finds vulnerabilities traditional QA misses</b></summary>

```mermaid
flowchart TD
    U["👤 Sec Engineer<br/>run /advanced-agentic-pentesting"] --> CHK{"🔍 Shannon installed?"}

    CHK -->|"✅ Yes"| FULL["💥 Full pentest:<br/>STRIDE + source review +<br/>dynamic fuzz + sandboxed exploit verify"]
    CHK -->|"⚪ No"| DEG["🛡️ Degraded mode:<br/>STRIDE + static source review<br/>⚠️ skip: fuzz/verify warned"]

    FULL --> REP1["📊 Findings + PoC + proposed patch"]
    DEG --> REP2["📊 Partial report + how-to-enable"]

    REP1 --> AS["🔍 xdd-shield: AgentShield framework audit"]
    REP2 --> AS

    classDef ok fill:#d4edda,stroke:#28a745,color:#000,stroke-width:2px
    classDef warn fill:#fff3cd,stroke:#856404,color:#000,stroke-width:2px
    classDef report fill:#cce5ff,stroke:#004085,color:#000,stroke-width:2px
    class FULL ok
    class DEG warn
    class REP1,REP2 report
```

**Result:** apps with SAST + DAST + threat model + sandboxed exploits + verified patches. Shannon CLI is **optional** (AGPL-3.0 with user consent). Without Shannon, X-DD degrades gracefully.

</details>

<details>
<summary><b>🎨 Case 3: White-labeling — distribute X-DD as your internal product</b></summary>

```mermaid
flowchart LR
    YML["xdd.profile.yml<br/>branding:<br/>  ecosystem_name: Helios<br/>  orchestrator_trigger: helios<br/>  persona.tone: formal"] --> BRAND["bash scripts/xdd-brand.sh"]
    BRAND --> SYM[".claude/commands/helios.md<br/>symlink xdd.md"]
    BRAND --> PER[".claude/orchestrator-persona.md<br/>formal persona"]
    BRAND --> CFG[".claude/branding.json<br/>active config"]

    SYM --> USE["💬 Helios, ship this feature<br/>formal corporate tone"]

    classDef config fill:#f3e5f5,stroke:#6a1b9a,color:#000,stroke-width:2px
    classDef out fill:#e0f7fa,stroke:#006064,color:#000,stroke-width:2px
    class YML config
    class USE out
```

**Result:** your org has "Helios" (or whatever name you choose). Automatic X-DD upstream attribution. 4 persona presets: technical / friendly / casual / formal. **One organization = one identity.**

</details>

<details>
<summary><b>🧠 Case 4: Continuous Learning — the system improves itself</b></summary>

```mermaid
flowchart TD
    SES["💻 Active agentic session"] -->|"Stop hook"| EXT["stop-pattern-extraction"]
    EXT --> DB[("🗄️ ~/.xdd/state.db<br/>SQLite instincts")]
    DB -->|"after N sessions"| ACC["Instincts with<br/>confidence +0.1/occ"]

    ACC --> EVOL["run /evolve workflow"]
    EVOL --> CLUST["🧬 TF-IDF clustering<br/>cosine similarity"]
    CLUST --> PROP["💡 Proposals:<br/>new command/skill/agent"]

    PROP --> HUM{"👤 Human approval<br/>T6.1 mitigation"}
    HUM -->|"✅ Approved"| GEN["Generate artifact<br/>in .agent/workflows or skills/"]
    HUM -->|"❌ Rejected"| REJ["Mark rejected in SQLite"]

    GEN --> COMMIT["Commit + cierre-fase<br/>System grows"]

    classDef hook fill:#fff0e6,stroke:#cc6600,color:#000,stroke-width:2px
    classDef human fill:#ffe6e6,stroke:#cc0000,color:#000,stroke-width:2px
    class EXT,EVOL hook
    class HUM human
```

**Result:** after 50 sessions, X-DD learned your patterns and suggests new skills/agents. **NEVER auto-promotes. Human signs every decision.**

</details>

<details>
<summary><b>🏢 Case 5: Multi-agent orchestration — a complete virtual team</b></summary>

```mermaid
flowchart TD
    CMD["run /orchestrate --pattern=feature_squad"] --> LEAD["👔 Lead:<br/>product-manager"]
    LEAD -->|"parallel_then_sync"| P1["🏗️ engineering-backend-architect"]
    LEAD -->|"parallel_then_sync"| P2["🎨 design-ui-designer"]
    LEAD -->|"parallel_then_sync"| P3["🧪 testing-test-results-analyzer"]
    P1 --> SYNC{"🤝 sync_point:<br/>spec_approval"}
    P2 --> SYNC
    P3 --> SYNC
    SYNC --> DONE["✅ Consensus spec"]

    classDef lead fill:#e1bee7,stroke:#6a1b9a,color:#000,stroke-width:2px
    classDef spec fill:#bbdefb,stroke:#1565c0,color:#000,stroke-width:2px
    class LEAD lead
    class P1,P2,P3 spec
```

**Result:** PM + Backend + UI + QA collaborating in parallel. Formal sync. **Replaces a 30-min standup with an executable workflow.**

</details>

---

## 🏆 Why X-DD vs alternatives?

<div align="center">

**The space is crowded. But only X-DD combines formal discipline + cryptographic signing + visible dogfooding.**

</div>

| Capability | **X-DD** | Spec-Kit (106k⭐) | OpenSpec (51k⭐) | BMAD (48k⭐) | Mastra (24k⭐) |
|---|---|---|---|---|---|
| Formal 6-phase gated pipeline | ✅ | partial 4 phases | ❌ "fluid" | ❌ | ❌ |
| **🔒 HMAC-signed gates** | **✅ UNIQUE** | ❌ | ❌ | ❌ | ❌ |
| **🛡️ DOMAIN + THREATS in Phase 2** | **✅ mandatory** | ❌ | ❌ | ❌ | ❌ |
| **🔍 AgentShield self-audit** | **✅ UNIQUE** | ❌ | ❌ | ❌ | ❌ |
| **📖 Visible committed dogfooding** | **✅ UNIQUE** | ❌ | ❌ | ❌ | ❌ |
| 11 formal Nygard ADRs | ✅ | partial | ❌ | ❌ | ❌ |
| Own MCP server | ✅ 6 tools | ❌ | ❌ | ❌ | ✅ |
| Multi-IDE | ✅ 13+ | ✅ 30+ | ✅ 25+ | ✅ several | ✅ |
| Continuous Learning (instincts) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Eval-harness 5 grader types | ✅ | ❌ | ❌ | ❌ | ✅ |
| Multi-agent orchestration runtime | ✅ | ❌ | ❌ | Party Mode | ✅ |
| Per-org white-labeling | ✅ + personas | partial | ❌ | ❌ | ❌ |
| **License purity** | **MIT pure** | MIT | MIT | NOASSERT ⚠️ | NOASSERT ⚠️ |

<div align="center">

**Spec-Kit has 106k stars. X-DD just started. But X-DD is the only one with real cryptographic audit trail.**

</div>

---

## 🎨 Persona × Compression — adapt X-DD to your culture

White-labeling (Sprint 13) + xdd-talk-compact (Sprint 10) = combinable 4×4 matrix:

|  | `technical` | `friendly` | `casual` | `formal` |
|---|---|---|---|---|
| `compact: off` | default | accessible | informal | corporate |
| `compact: lite` | no filler | + emojis ok | less formal | concentrated professional |
| `compact: standard` | concise | brief conversational | shortcuts | executive |
| `compact: ultra` | telegraphic | shortcuts emoji | caveman | concise executive |

**Casual startup:** `casual + ultra`. **Regulated fintech:** `formal + standard`. **Dev consultancy:** `technical + lite`.

---

## 🔌 Compatible with any AI assistant

```mermaid
flowchart LR
    XDD["🧠 X-DD"] --> MCP["📡 xdd-mcp-server<br/>6 tools"]
    XDD --> A1["xdd-adapt claude-code"]
    XDD --> A2["xdd-adapt opencode"]

    A1 --> CC["💻 Claude Code"]
    A2 --> OC["💻 OpenCode"]

    MCP --> IDES["💎 Cursor / Continue / Zed /<br/>Cline / Roo Code / Windsurf /<br/>Antigravity / Codex / Gemini /<br/>Qwen / Hermes / VSCode /<br/>any MCP-compatible IDE"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef bridge fill:#90caf9,stroke:#1565c0,color:#000,stroke-width:2px
    classDef ide fill:#a5d6a7,stroke:#2e7d32,color:#000,stroke-width:2px
    class XDD core
    class MCP,A1,A2 bridge
    class CC,OC,IDES ide
```

**1 shared MCP server vs N per-IDE adapters.** Sustainable maintainability. No vendor lock-in.

---

## 📦 Choose your level — scale with need

<table>
<tr>
<th>Profile</th><th>For what</th><th>Command</th>
</tr>
<tr>
<td><b>🌱 minimal</b></td>
<td>Try X-DD without commitment</td>
<td><code>--profile=minimal</code></td>
</tr>
<tr>
<td><b>⭐ core</b></td>
<td><b>Recommended to start</b></td>
<td><code>--profile=core</code></td>
</tr>
<tr>
<td><b>🚀 developer</b></td>
<td>Active dev with AI</td>
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
<td>Full adoption</td>
<td><code>--profile=full</code></td>
</tr>
</table>

---

## 🌳 Which methodologies to use? — decision tree

```mermaid
flowchart TD
    START{"Type of change"} -->|"Bugfix less than 10 lines"| DIR["⚡ DIRECT<br/>no pipeline"]
    START -->|"Bugfix more than 20 lines"| MIN["📋 MINIMUM<br/>SDD + TDD"]
    START -->|"Internal tool / script"| AGI["🛠️ AGILE<br/>FDD + SDD + TDD"]
    START -->|"Customer-facing feature"| STD["📦 STANDARD<br/>FDD + SDD + ATDD + BDD + TDD + SecDD"]
    START -->|"Module with complex logic"| FULL["🏛️ COMPLETE<br/>FDD + DDD + SDD + BDD + ATDD<br/>+ TDD + Threat + STDD + SecDD"]

    classDef path fill:#fff9c4,stroke:#f57f17,color:#000,stroke-width:2px
    class DIR,MIN,AGI,STD,FULL path
```

**X-DD Constitution Art. 8:** not every task needs the full pipeline. **Adaptable, not rigid.**

---

## ⚠️ What X-DD is NOT (honesty)

- ❌ **Not an application framework.** Doesn't replace React/Express/Django.
- ❌ **Not a test runner.** It orchestrates Vitest/Playwright/pytest.
- ❌ **Not MemPalace.** Consumes it as an optional MIT external dep.
- ❌ **Doesn't require Claude Code.** Works with 13+ assistants via MCP.
- ❌ **Doesn't send data to the cloud.** Local-first. Code stays in the team.
- ❌ **Not monorepo-compatible without adaptation** (Sprint 15 roadmap).

---

## 🛡️ Governance principles

- 🎯 **Zero Ambiguity** — system halts if any parameter is undefined
- 🔒 **Gated Pipeline** — `"APROBADO"` HMAC-SHA256 signed ([ADR-0006](docs/adr/0006-gate-keeper-firma-hmac.md))
- 📐 **Spec First** — no `src/` exists without an approved `SPEC.md`
- 🧪 **TDD First** — no business function exists without its prior test
- 🌍 **Absolute Portability** — no absolute paths; everything relative to `./`
- 👁️ **Visible Dogfooding** — X-DD walks through its 6 phases in public ([ADR-0001](docs/adr/0001-dogfooding-visible-commiteable.md))

---

## 🔗 Optional external integrations

```mermaid
flowchart TB
    XDD["🧠 X-DD core<br/>MIT pure"]

    XDD -.->|"semantic memory"| MP["🏛️ MemPalace<br/>MIT · 52.8k ⭐<br/>96-99% recall benchmarks<br/>29 MCP tools"]
    XDD -.->|"code intelligence<br/>recommended"| GN["🧬 GitNexus<br/>PolyForm Noncomm ⚠️ · 40.5k ⭐<br/>AST graph 14 langs<br/>16 MCP tools"]
    XDD -.->|"dynamic pentest<br/>optional"| SH["🛡️ Shannon CLI<br/>AGPL-3.0 ⚠️ · 43k ⭐<br/>White-box sandboxed exploits"]

    classDef core fill:#ffd54f,stroke:#f57f17,color:#000,stroke-width:3px
    classDef ext fill:#e8f5e9,stroke:#388e3c,color:#000,stroke-width:2px
    classDef warn fill:#ffebee,stroke:#c62828,color:#000,stroke-width:2px
    class XDD core
    class MP ext
    class GN warn
    class SH warn
```

> ⚠️ **GitNexus is PolyForm Noncommercial 1.0.0.** Personal/research/non-profit use is free. Commercial use requires paid license. X-DD never bundles it. Disclaimer in [ADR-0033](docs/adr/0033-gitnexus-tier1-companion.md) + [DEPENDENCIES.md](DEPENDENCIES.md).
>
> ⚠️ **Shannon is AGPL-3.0.** Your X-DD project is **NOT contaminated** by using Shannon via the hybrid wrapper. X-DD never bundles it. The decision is yours. Full disclaimer in [docs/PENTEST.md](docs/PENTEST.md).

---

## 📚 Documentation by your role

<table>
<tr>
<th>If you are...</th>
<th>Start here</th>
</tr>
<tr>
<td>🆕 <b>New developer</b></td>
<td><a href="the-shortform-guide.md"><code>the-shortform-guide.md</code></a> · 15-min visual Quickstart</td>
</tr>
<tr>
<td>🔬 <b>Power user / Architect</b></td>
<td><a href="the-longform-guide.md"><code>the-longform-guide.md</code></a> · Exhaustive reference</td>
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
<td><a href="docs/MCP_INTEGRATION.md"><code>docs/MCP_INTEGRATION.md</code></a> · MCP setup per IDE</td>
</tr>
<tr>
<td>🏛️ <b>Decision maker</b></td>
<td><a href="docs/adr/"><code>docs/adr/</code></a> · 11 Nygard ADRs explain the "why"</td>
</tr>
<tr>
<td>📊 <b>PM / project lead</b></td>
<td><a href="PROJ-MASTER-PLAN.md"><code>PROJ-MASTER-PLAN.md</code></a> · Gantt + public sprints</td>
</tr>
<tr>
<td>🤝 <b>Contributor</b></td>
<td><a href="CONTRIBUTING.md"><code>CONTRIBUTING.md</code></a> · How to add workflow/agent/skill/hook</td>
</tr>
</table>

---

## 🚀 Get started now

```bash
# 1) Verify environment
make doctor

# 2) Bootstrap your first project
bash scripts/xdd-init.sh /path/my-project --profile=core

# 3) Start
cd /path/my-project && bash scripts/xdd-start.sh

# 4) In your IDE/AI assistant: run the /xdd command
```

**Want to see X-DD applied to itself?** Check [`.xdd/`](.xdd/) — 6 signed phases, public, auditable.

---

<div align="center">

### 🌟 X-DD is for you if...

✅ You want **agentic speed** + **formal discipline**
✅ You need **cryptographic audit trail** for compliance
✅ You work on a **multi-IDE team** (Claude Code + Cursor + ...)
✅ You care about **visible dogfooding** over marketing
✅ You prefer **pure MIT** over ambiguous licenses
✅ You want a framework **that improves itself** (instincts + /evolve)

<br/>

### 🚫 X-DD is NOT for you if...

❌ You want **vibe-coding without discipline** (use Claude Code directly)
❌ Your organization **rejects formal process discipline**
❌ You need a **web dashboard** today (v0.2.0 roadmap)
❌ You want **lock-in on a single IDE** (X-DD is multi-IDE by design)

<br/>

---

<sub>**X-DD** · *Cross-Driven Development System* · MIT · Build with discipline, ship with speed.</sub>

[⭐ Star on GitHub](https://github.com/Cucholambr3ta/x-dd) ·
[📖 15-min Quickstart](the-shortform-guide.md) ·
[🐛 Issues](https://github.com/Cucholambr3ta/x-dd/issues) ·
[🤝 Contribute](CONTRIBUTING.md) ·
[💬 Discussions](https://github.com/Cucholambr3ta/x-dd/discussions)

</div>
