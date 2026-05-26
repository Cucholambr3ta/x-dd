#!/bin/bash
# stop:git-check — advierte si hay cambios sin commitear al cerrar sesión.
# Exit 0 siempre (warn-only).
set +e

if [ ! -d .git ]; then
  exit 0
fi

UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l)
UNPUSHED=$(git log --branches --not --remotes --oneline 2>/dev/null | wc -l)

if [ "$UNCOMMITTED" -gt 0 ] || [ "$UNPUSHED" -gt 0 ]; then
  echo "[xdd:hook] WARN — al cerrar sesión:" >&2
  [ "$UNCOMMITTED" -gt 0 ] && echo "[xdd:hook]   · $UNCOMMITTED archivos modificados sin commitear" >&2
  [ "$UNPUSHED" -gt 0 ] && echo "[xdd:hook]   · $UNPUSHED commits locales sin pushear" >&2
  echo "[xdd:hook] Considerá ejecutar: git status / git push origin HEAD" >&2
fi
exit 0
