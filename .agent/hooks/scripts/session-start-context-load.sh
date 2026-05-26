#!/bin/bash
# session-start:context-load — imprime el contexto vivo al iniciar sesión.
# Lee WORKING-CONTEXT.md + última entrada de memoria.md.
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

# Cap a ~8000 chars total (similar a ECC_SESSION_START_MAX_CHARS)
exit 0
