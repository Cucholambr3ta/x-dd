#!/bin/bash
# session-start:context-load — imprime el contexto vivo al iniciar sesión.
# Sprint 28 / ADR-0038: enforce lectura memoria + lecciones + WORKING-CONTEXT + doctor + gate.
# Lección retroactiva: en proyecto piloto multi-IDE el orquestador omitía leer lecciones,
# repitiendo errores conocidos. Ahora carga forzada y visible al inicio.
# Exit 0 siempre. El orquestador captura stdout como contexto del prompt.
set +e

if [ -f WORKING-CONTEXT.md ]; then
  echo "=== Working Context (live) ==="
  head -30 WORKING-CONTEXT.md
  echo
fi

if [ -f memoria.md ]; then
  echo "=== Memoria — última sesión ==="
  awk '/^### Sesión/{p=1} p' memoria.md | head -25
  echo
fi

# Sprint 28: carga lecciones recientes (last 5 entries) — previene repetición de errores
if [ -f lecciones.md ]; then
  echo "=== Lecciones — últimas 5 entries (consultar ANTES de proponer arquitectura) ==="
  awk '/^### \[/{count++; if (count>5) exit} count>=1' lecciones.md | head -80
  echo
fi

# Sprint 28: micro-doctor — verifica salud crítica del entorno (NO bloquea, solo reporta)
if [ -x ./scripts/xdd-doctor.sh ]; then
  echo "=== Doctor (resumen) ==="
  bash ./scripts/xdd-doctor.sh 2>/dev/null | tail -5
  echo
fi

# Sprint 28: gate status — fase actual + estado
if [ -f ./scripts/xdd-gate.py ] && command -v python3 >/dev/null 2>&1; then
  echo "=== Gate keeper (fase actual) ==="
  python3 ./scripts/xdd-gate.py status 2>/dev/null | head -10
  echo
fi

# Cap a ~8000 chars total (similar a ECC_SESSION_START_MAX_CHARS)
exit 0
