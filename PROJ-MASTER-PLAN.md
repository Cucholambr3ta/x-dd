# PROJ-MASTER-PLAN — X-DD v0.1.0

> Carta Gantt del release v0.1.0. Mantenida por `/xdd-trace`.
> Cada cierre de sprint marca tareas como `done` y actualiza fechas reales.

## Resumen

- **Release:** v0.1.0
- **Sprints:** 8 + Sprint 0 (Reconciliación)
- **Esfuerzo estimado:** ~17.5 días de trabajo
- **Plan macro:** [MEJORAS-X-DD.md](MEJORAS-X-DD.md) + anexo v1.2
- **SPEC:** [.xdd/briefing/SPEC.md](.xdd/briefing/SPEC.md)
- **Features:** [.xdd/briefing/FEATURES.md](.xdd/briefing/FEATURES.md)
- **ADRs:** [docs/adr/](docs/adr/)

## Gantt

```mermaid
gantt
    title X-DD v0.1.0 — Roadmap por sprint y fase X-DD
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d
    excludes    weekends

    section F1-F3 Briefing/Spec/Plan
    Sprint 0 Reconciliación + 10 ADRs    :active, s0, 2026-05-26, 1d
    Sprint 1 MemPalace externo + Quickstart :s1, after s0, 2d
    Sprint 2 CI base + plan formal       :s2, after s1, 1d

    section F4 Build
    Sprint 3 xdd-doctor v2 + xdd.config  :s3, after s2, 2d
    Sprint 4 Gate keeper HMAC ⭐         :crit, s4, after s3, 3d
    Sprint 5 Registry agentes tipado     :s5, after s4, 2d
    Sprint 6 MCP server propio ⭐        :crit, s6, after s5, 3d
    Sprint 7 Adapters + tests E2E        :s7, after s6, 2d

    section F5-F6 QA + Retro
    Sprint 8 Gobernanza OSS + 3-tier     :s8, after s7, 2d
    Sprint 9 Continuous Learning         :s9, after s8, 4d
    Sprint 10 Skills + Eval-harness      :s10, after s9, 5d
    Sprint 11 Multi-agent orchestration  :s11, after s10, 4d
    Sprint 12 AgentShield + Shannon dep  :s12, after s11, 4d
    Sprint 13 White-labeling             :s13, after s12, 3d
    Sprint 14 Workspace + Wizard         :s14, after s13, 3d
    Sprint 15 Monorepo 3 modos           :s15, after s14, 4d
    Sprint 16 SDD parity + AI review + TFIDF :s16, after s15, 6d
    Sprint 17 Party + HITL + Router      :s17, after s16, 6d
    Sprint 18 Observability Triad        :s18, after s17, 5d
    Sprint 19 Context Engineering        :s19, after s18, 5d
    Sprint 20 Eval benchmarks externos   :s20, after s19, 6d
    Sprint 21 Sandbox + Permissions      :s21, after s20, 6d
    Sprint 22 AHE evolve refactor        :s22, after s21, 5d
    Sprint 23 Protocols + Skills ecosys  :s23, after s22, 6d
    GitNexus tier-1 companion            :gn, after s23, 1d

    section Release
    Release v0.1.0                       :crit, rel, after gn, 1d

    section Hitos
    Hito Gate firmado funcionando        :milestone, after s4, 0d
    Hito MCP server público              :milestone, after s6, 0d
    Hito 3 MCP stack completo            :milestone, after gn, 0d
    Hito Release v0.1.0                  :milestone, after rel, 0d
```

## Estado por sprint

| Sprint | Estado | Fase X-DD | Inicio plan | Cierre plan | Inicio real | Cierre real | PR |
|--------|--------|-----------|-------------|-------------|-------------|-------------|-----|
| 0 Reconciliación | ✅ done | F1 Briefing | 2026-05-26 | 2026-05-26 | 2026-05-26 | 2026-05-26 | [#1](https://github.com/Cucholambr3ta/x-dd/pull/1) |
| 1 MemPalace externo + Quickstart | ✅ done | F2 Spec | 2026-05-27 | 2026-05-28 | 2026-05-26 | 2026-05-26 | [#2](https://github.com/Cucholambr3ta/x-dd/pull/2) |
| 2 CI base + plan formal | ✅ done | F3 Plan | 2026-05-29 | 2026-05-29 | 2026-05-26 | 2026-05-26 | [#3](https://github.com/Cucholambr3ta/x-dd/pull/3) |
| 3 xdd-doctor v2 + xdd.config | ✅ done | F4 Build (1/5) | 2026-06-01 | 2026-06-02 | 2026-05-26 | 2026-05-26 | [#4](https://github.com/Cucholambr3ta/x-dd/pull/4) |
| 4 Gate keeper HMAC ⭐ | ✅ done | F4 Build (2/5) | 2026-06-03 | 2026-06-05 | 2026-05-26 | 2026-05-26 | [#5](https://github.com/Cucholambr3ta/x-dd/pull/5) |
| 5 Registry agentes tipado | ✅ done | F4 Build (3/5) | 2026-06-08 | 2026-06-09 | 2026-05-26 | 2026-05-26 | [#7](https://github.com/Cucholambr3ta/x-dd/pull/7) |
| 6 MCP server propio ⭐ | ✅ done | F4 Build (4/5) | 2026-06-10 | 2026-06-12 | 2026-05-26 | 2026-05-26 | [#8](https://github.com/Cucholambr3ta/x-dd/pull/8) |
| 7 Adapters + Hooks + Manifests + E2E ⭐ | ✅ done | F4 Build (5/5) + F5 QA | 2026-06-15 | 2026-06-17 | 2026-05-26 | 2026-05-26 | [#9](https://github.com/Cucholambr3ta/9) |
| 8 Gobernanza OSS + 3-tier docs + agent.yaml ⭐ | ✅ done | F6 Retro init | 2026-06-17 | 2026-06-19 | 2026-05-26 | 2026-05-26 | [#10](https://github.com/Cucholambr3ta/x-dd/pull/10) |
| 9 Continuous Learning (instincts + /evolve + SQLite) | ✅ done | F4 ext | 2026-06-20 | 2026-06-23 | 2026-05-26 | 2026-05-26 | [#11](https://github.com/Cucholambr3ta/x-dd/pull/11) |
| 10 Skills + Eval-harness + xdd-talk-compact | ✅ done | F4 ext | 2026-06-24 | 2026-06-29 | 2026-05-26 | 2026-05-26 | [#12](https://github.com/Cucholambr3ta/x-dd/pull/12) |
| 11 Multi-agent orchestration runtime | ✅ done | F4 ext | 2026-06-30 | 2026-07-03 | 2026-05-26 | 2026-05-26 | [#13](https://github.com/Cucholambr3ta/x-dd/pull/13) |
| 12 AgentShield + Shannon dep + rename | ✅ done | F4 ext + F5 audit | 2026-07-04 | 2026-07-05 | 2026-05-26 | 2026-05-26 | [#14](https://github.com/Cucholambr3ta/x-dd/pull/14) |
| 13 White-labeling (branding + 4 personas) | ✅ done | F6 ext | 2026-07-06 | 2026-07-08 | 2026-05-26 | 2026-05-26 | [#15](https://github.com/Cucholambr3ta/x-dd/pull/15) |
| 14 Workspace mode + Wizard interactivo | ✅ done | F6 ext | 2026-07-09 | 2026-07-11 | 2026-05-27 | 2026-05-27 | [#20](https://github.com/Cucholambr3ta/x-dd/pull/20) |
| 15 Monorepo 3 modos (isolated/shared/hybrid) | ✅ done | F6 ext | 2026-07-12 | 2026-07-15 | 2026-05-27 | 2026-05-27 | [#21](https://github.com/Cucholambr3ta/x-dd/pull/21) |
| 16 SDD parity + AI review + TF-IDF | ✅ done | F6 ext | 2026-07-16 | 2026-07-21 | 2026-05-27 | 2026-05-27 | [#22](https://github.com/Cucholambr3ta/x-dd/pull/22) |
| 17 Party + Brainstorm + HITL + Router | ✅ done | F6 ext | 2026-07-22 | 2026-07-27 | 2026-05-27 | 2026-05-27 | [#23](https://github.com/Cucholambr3ta/x-dd/pull/23) |
| 18 Observability Triad (OTel+replay+cost+6-stage) | ✅ done | F6 ext | 2026-07-28 | 2026-08-01 | 2026-05-27 | 2026-05-27 | [#24](https://github.com/Cucholambr3ta/x-dd/pull/24) |
| 19 Context Engineering (budget+compact+fs+code-as-tool) | ✅ done | F6 ext | 2026-08-02 | 2026-08-06 | 2026-05-27 | 2026-05-27 | [#25](https://github.com/Cucholambr3ta/x-dd/pull/25) |
| 20 Eval benchmarks externos (Inspect AI+TB2+SWE-bench) | ✅ done | F6 ext | 2026-08-07 | 2026-08-12 | 2026-05-27 | 2026-05-27 | [#26](https://github.com/Cucholambr3ta/x-dd/pull/26) |
| 21 Sandbox + Permissions (intent+authz+6-step gov) | ✅ done | F6 ext | 2026-08-13 | 2026-08-18 | 2026-05-27 | 2026-05-27 | [#27](https://github.com/Cucholambr3ta/x-dd/pull/27) |
| 22 AHE /evolve (3-layer obs + frozen transfer) | ✅ done | F6 ext | 2026-08-19 | 2026-08-23 | 2026-05-27 | 2026-05-27 | [#28](https://github.com/Cucholambr3ta/x-dd/pull/28) |
| 23 Protocols + Skills (A2A+AG-UI+bundle+plan_and_act) | ✅ done | F6 ext | 2026-08-24 | 2026-08-29 | 2026-05-27 | 2026-05-27 | [#29](https://github.com/Cucholambr3ta/x-dd/pull/29) |
| Add GitNexus tier-1 companion | ✅ done | F6 ext | 2026-08-30 | 2026-08-30 | 2026-05-27 | 2026-05-27 | [#32](https://github.com/Cucholambr3ta/x-dd/pull/32) |
| **Release** v0.1.0 tag firmado + RELEASES/v0.1.0.md + Template Repo | ⏳ pendiente | Release | 2026-08-31 | 2026-08-31 | — | — | — |

Leyenda: 🔄 en curso · ✅ done · ⏳ pendiente · ❌ blocked

## Tareas detalladas por sprint

Ver [.xdd/briefing/FEATURES.md](.xdd/briefing/FEATURES.md) y secciones por sprint en
[el plan macro](MEJORAS-X-DD.md).

## Dependencias críticas

```mermaid
graph LR
    S0[Sprint 0<br/>Reconciliación] --> S1[Sprint 1<br/>MemPalace]
    S0 --> S2[Sprint 2<br/>CI]
    S1 --> S3[Sprint 3<br/>doctor+config]
    S2 --> S3
    S3 --> S4[Sprint 4<br/>Gate HMAC ⭐]
    S4 --> S6[Sprint 6<br/>MCP server ⭐]
    S4 --> S7[Sprint 7<br/>Adapters+E2E]
    S5[Sprint 5<br/>Registry] --> S6
    S6 --> S7
    S7 --> S8[Sprint 8<br/>Release v0.1.0]

    classDef crit fill:#fce8e6,stroke:#c5221f
    class S4,S6,S8 crit
```

## Historial de actualizaciones

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-05-26 | Creación inicial al cerrar Sprint 0 | aplacencia |
| 2026-05-26 | Sprint 0 mergeado (PR #1); Sprint 1 en curso | aplacencia |
| 2026-05-26 | Sprint 1 mergeado (PR #2, squash c5be687); Sprint 2 en curso | aplacencia |
| 2026-05-26 | Sprint 2 mergeado (PR #3, squash ed9eed7); Sprint 3 en curso | aplacencia |
| 2026-05-26 | Sprint 3 mergeado (PR #4, squash 3310f8b); Sprint 4 en curso (gate ⭐) | aplacencia |
| 2026-05-26 | Sprint 4 mergeado (PR #5, squash 5c4d26c); Sprint 5 en curso | aplacencia |
| 2026-05-26 | Fix PR #6 (CI markdownlint relax) mergeado; política cambiada a `delete_branch_on_merge=false` para preservar trazabilidad por sprint | aplacencia |
| 2026-05-26 | Sprint 5 mergeado (PR #7, squash b24582a); Sprint 6 en curso (MCP server ⭐) | aplacencia |
| 2026-05-26 | Sprint 6 mergeado (PR #8, squash 572326f); Sprint 7 ampliado en curso (adapters+hooks+manifests, inspiración ECC) | aplacencia |
| 2026-05-26 | Plan actualizado a estrategia MAXIMALISTA (Sprints 7-12 todos para v0.1.0, ~23 días extra) | aplacencia |
| 2026-05-26 | Sprint 7 ampliado mergeado (PR #9, squash b6669a4); Sprint 8 en curso (gobernanza + 3-tier docs) | aplacencia |
| 2026-05-26 | Sprint 8 ampliado mergeado (PR #10, squash adede3b); Sprint 9 en curso (continuous learning) | aplacencia |
| 2026-05-26 | Sprints 13 (White-labeling) y 14 (Workspace+Wizard) nuevos agregados al plan v0.1.0; total ~36d | aplacencia |
| 2026-05-26 | Sprint 9 mergeado (PR #11, 88d87ce); Sprint 10 en curso (Skills + Eval + caveman MIT) | aplacencia |
| 2026-05-26 | Sprint 10 mergeado (PR #12); Sprint 11 en curso (orchestration runtime) | aplacencia |
| 2026-05-26 | Sprint 11 mergeado (PR #13, 16c856c); Sprint 12 en curso (AgentShield + Shannon dep) | aplacencia |
| 2026-05-26 | Sprint 12 mergeado (PR #14, 4f9a165); Sprint 13 en curso (white-labeling) | aplacencia |
| 2026-05-26 | Sprint 13 mergeado (PR #15, 4abfb58). Pendiente S14 + release v0.1.0 | aplacencia |
| 2026-05-27 | fix/docs-sync-s9-s13 — sync doc drift detectado en 9 files post-S13 | aplacencia |
| 2026-05-27 | Sprints 14-23 ejecutados autónomos (PRs #20-29). 10 sprints, 33 ADRs total, ~95 tests nuevos | aplacencia |
| 2026-05-27 | fix CI lint workflows description (PR #30) | aplacencia |
| 2026-05-27 | Workspace global Desarrollos/ instalado X-DD core post-purga ANMAX. Backup tar.gz preservado | aplacencia |
| 2026-05-27 | GitNexus tier-1 companion mergeado (PR #32) paralelo MemPalace + ADR-0033 | aplacencia |
| 2026-05-27 | docs/sync-post-gitnexus — sync 12 files post-S14-23 + GitNexus | aplacencia |
