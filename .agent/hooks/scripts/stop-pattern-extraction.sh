#!/bin/bash
# stop:pattern-extraction — Sprint 9 real impl.
# Lee evento Stop de Claude Code (JSON stdin), extrae patrones de la sesión
# y los persiste en SQLite via xdd-state.py. Best-effort, no bloquea jamás.
set +e

# Si xdd-state.py no existe (perfil sin continuous-learning), no-op.
ROOT="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"
STATE_SCRIPT="$ROOT/scripts/xdd-state.py"
[ -f "$STATE_SCRIPT" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Si XDD_LEARNING_DISABLED=1, no-op (opt-out por sesión).
[ "${XDD_LEARNING_DISABLED:-}" = "1" ] && exit 0

# Leer JSON stdin
RAW=$(cat 2>/dev/null || true)
[ -z "$RAW" ] && exit 0

SESSION_ID=$(echo "$RAW" | python3 -c "
import json, sys, os
try:
    d = json.loads(sys.stdin.read() or '{}')
    print(d.get('session_id') or os.environ.get('XDD_SESSION_ID', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null)

# Patrones heurísticos: chequear si hay archivos .md tocados, commits hechos,
# tests corridos, gates aprobados, etc. Para v0.1.0 hacemos lo mínimo.
# Sprint 11 (orchestration) puede enriquecer esto con análisis profundo.

# Heurística 1: si hubo commits en esta sesión, registra instinct
if git -C "$ROOT" log --since="1 hour ago" --oneline 2>/dev/null | head -1 | grep -q .; then
    python3 "$STATE_SCRIPT" record-instinct \
      --pattern "session ended with new commits" \
      --category user_action \
      --context "$(git -C "$ROOT" log -1 --pretty=format:'%s' 2>/dev/null)" \
      --session-id "$SESSION_ID" >>"$HOME/.xdd/learning.log" 2>&1 &
fi

# Heurística 2: si gate keeper validó/aprobó fases
if [ -d "$ROOT/.xdd" ]; then
    APPROVED=$(find "$ROOT/.xdd" -name ".status" -newer "$HOME/.xdd/state.db" 2>/dev/null | wc -l)
    if [ "${APPROVED:-0}" -gt 0 ]; then
        python3 "$STATE_SCRIPT" record-instinct \
          --pattern "phase status changed during session" \
          --category multi_step \
          --context "approved_count=$APPROVED" \
          --session-id "$SESSION_ID" >>"$HOME/.xdd/learning.log" 2>&1 &
    fi
fi

exit 0
