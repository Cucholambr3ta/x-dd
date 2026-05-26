# X-DD — Cross-Driven Development System

**Pipeline de desarrollo de alta calidad** que integra múltiples metodologías *-Driven Development* como capas sobre un Gated Pipeline de 6 fases, orquestado por **Claude Code** u **OpenCode** y una agencia de 77+ subagentes especializados.

---

## ¿Qué es X-DD?

X-DD es un ecosistema de desarrollo de software que combina las mejores metodologías en un solo pipeline coherente, sin agregar fases nuevas — cada metodología se embebe en la fase donde más aporta:

```
FASE 1 (Briefing)  ──► + FDD (catálogo de features) + BDD (Gherkin) + ATDD (stubs)
FASE 2 (Spec)      ──► + DDD (modelo de dominio)    + Threat Modeling (THREATS.md)
FASE 3 (Plan)      ──► + FDD (plan por features verticales)
FASE 4 (Build)     ──► + TDD (Rojo→Verde→Refactor)  + STDD (security tests primero)
FASE 5 (QA)        ──► + BDD ejecutable + ATDD + SAST + DAST + Secrets scanning
FASE 6 (Retro)     ──► Learning Loop → lecciones.md
```

## Metodologías integradas

| Metodología | Qué aporta |
|-------------|------------|
| **SDD** — Spec-Driven | Eje central: ningún código sin especificación aprobada |
| **FDD** — Feature-Driven | Plan por features verticales de valor, no por capas técnicas |
| **BDD** — Behavior-Driven | Escenarios Gherkin `.feature` ejecutables desde Fase 1 |
| **ATDD** — Acceptance TDD | Tests de aceptación como contrato antes de codificar |
| **DDD** — Domain-Driven | Modelo de dominio explícito (`DOMAIN.md`) con ubiquitous language |
| **TDD** — Test-Driven | Ciclo Rojo→Verde→Refactor obligatorio para lógica de negocio |
| **STDD** — Security TDD | Security tests escritos *antes* del código para funciones críticas |
| **SecDD** — Security-Driven | SAST + DAST + Secrets scanning en el pipeline QA |
| **Threat-Driven** | Modelado STRIDE sobre el dominio antes de codificar |

## Estructura del repositorio

```
x-dd/
├── CLAUDE.md                    ← Manifiesto raíz (leer primero)
├── README.md                    ← Este archivo
├── INSTALL.md                   ← Guía de instalación de herramientas
│
├── docs/
│   ├── constitucion.md          ← Ley suprema del ecosistema (9 artículos)
│   ├── equipo.md                ← Directorio de 77+ agentes especializados
│   ├── SDD_GUIDE.md             ← Guía completa del Pipeline Elite SDD
│   └── X-DD_Integration_Guide.md ← Integración de todas las metodologías
│
├── .agent/
│   └── workflows/               ← 29 workflows slash commands (Claude Code / OpenCode)
│       ├── xdd.md               ← /xdd — Orquestador principal
│       ├── xdd-build.md         ← /xdd-build — Build con TDD/STDD
│       ├── qa-review.md         ← /qa-review — QA completo (3 Tiers)
│       ├── fase-requisitos.md   ← /fase-requisitos — Briefing
│       ├── security-audit.md    ← /security-audit
│       └── ...                  (25 workflows adicionales)
│
├── .claude/
│   └── settings.json            ← Hook PostToolUse: re-indexa MemPalace tras cada Write/Edit
│
├── scripts/
│   ├── xdd-start.sh             ← Arranque unificado: MemPalace + git hooks + orquestador
│   └── hooks/
│       └── post-commit          ← Git hook: re-indexa MemPalace tras cada commit
│
└── prompts/
    ├── agents/                  ← 77+ subagentes especializados (16 categorías)
    │   ├── engineering/         ← Senior dev, architect, devops, security...
    │   ├── design/              ← UX, UI, brand, accessibility...
    │   ├── security/            ← SecOps, threat detection, security engineer
    │   ├── product/             ← Product manager, researcher...
    │   ├── finance/             ← Financial analyst, FP&A, tax...
    │   └── ...                  (11 categorías más)
    ├── phases/                  ← Prompts por metodología (TDD, BDD, DDD, SecDD...)
    ├── skills/                  ← Catálogo de skills inyectables
    ├── templates/               ← Plantillas de artefactos (SPEC, DOMAIN, THREATS...)
    ├── workflows/               ← Catálogo de workflows
    └── ecosystem/               ← Estructura del ecosistema
```

## Inicio rápido

1. **Instalar herramientas** → ver [INSTALL.md](./INSTALL.md)
2. **Copiar la estructura** al nuevo proyecto (`.agent/`, `.claude/`, `prompts/`, `scripts/`, `CLAUDE.md`)
3. **Crear `memoria.md`** en la raíz del proyecto
4. **Arrancar X-DD** — un solo comando inicializa MemPalace, activa los git hooks y lanza el orquestador:
   ```bash
   bash ./scripts/xdd-start.sh
   ```
5. **Ejecutar `/xdd`** para arrancar el orquestador principal

## Automatización de MemPalace

MemPalace se re-indexa automáticamente en tres momentos para preservar el contexto entre sesiones — especialmente útil al agotar tokens:

| Momento | Mecanismo | Archivo |
|---------|-----------|---------|
| Arranque de sesión | `xdd-start.sh` ejecuta `mempalace mine` antes del orquestador | `scripts/xdd-start.sh` |
| Cada Write/Edit del agente | Hook `PostToolUse` dispara `mempalace mine` en background | `.claude/settings.json` |
| Cada `git commit` | Hook `post-commit` re-indexa en background | `scripts/hooks/post-commit` |

```
Agente edita archivo  →  PostToolUse hook  →  mempalace mine (background)
git commit            →  post-commit hook  →  mempalace mine (background)
Nueva sesión          →  xdd-start.sh      →  mempalace mine → orquestador
```

## Árbol de decisión — ¿qué metodologías usar?

| Escenario | Camino |
|-----------|--------|
| Módulo nuevo con lógica de negocio compleja | **COMPLETO**: FDD + DDD + SDD + BDD + ATDD + TDD + Threat + STDD + SecDD |
| Feature con usuario/cliente definido | **ESTÁNDAR**: FDD + SDD + ATDD + BDD + TDD + SecDD |
| Tool interna / script | **ÁGIL**: FDD + SDD + TDD |
| Bugfix > 20 líneas | **MÍNIMO**: SDD + TDD |
| Bugfix < 10 líneas | **DIRECTO**: sin pipeline (Art. 8) |

## Principios de gobernanza

- **Ambigüedad Cero** — El sistema se detiene si hay parámetros indefinidos
- **Gated Pipeline** — Se requiere `"APROBADO"` antes de pasar de fase
- **Spec First** — No existe `src/` sin `SPEC.md` previo aprobado
- **TDD First** — No existe función de negocio sin su test previo
- **Portabilidad Absoluta** — Sin rutas absolutas; todo relativo a `./`

---

*X-DD System — Pipeline de desarrollo con excelencia operativa*
