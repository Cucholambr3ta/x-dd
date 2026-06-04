# Memoria Sprint 26 — 2026-06-04

## Hitos

- Inc 5: xdd-memory.py + subcomando sprint-close (11 tests verdes)
  - Crea acuerdos/memoria/sprint-NN.md + acuerdos/lecciones/sprint-NN.md
  - INDEX.md idempotente (no duplica entradas)
  - MEMORY.md inicializado en primer sprint-close
- Inc 5: xdd-init.sh genera MEMORY.md + INDEX.md en acuerdos/ al bootstrap
- Inc 5: cierre-fase.md v1.4 usa sprint-close en lugar de append monolitico
- Inc 6: workflow /xdd historias completo (xdd-historias.md)
  - 4 artefactos por historia: propuesta, requisitos-escenarios, escenario-tecnico, checklist
  - checklist minimo 50 tareas atomicas (TDD + STDD + observabilidad + docs)
  - pipeline worker-auditor: auditor verifica checklist y cobertura STDD
  - acuerdos/sprint.md generado al final
- 384 tests verdes, shield 0 CRITICAL, lint 0 errores

## Bloqueos

- Bug CLI argparse: --project debe ir ANTES del subcomando (no despues)
  Detectado al usar el comando manualmente; tests directos no lo capturan

## Proxima sesion

- Inc 7: xdd-gitflow.sh (setup dev/collab, sprint-start, sprint-close, pre-push hook)
- Inc 8: xdd-sprint.md (equipos dinamicos + eval pre-push + ciclo completo)
- Inc 9: xdd-discipline-check.py (gate valida contenido por disciplina)
