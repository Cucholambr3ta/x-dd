#!/bin/bash
# pre:tool:temporal-awareness — inyecta contexto temporal del sprint en cada tool call.
# S13, v0.2. Opt-out: XDD_TEMPORAL_AWARENESS=0.
# Exit 0 siempre (no bloquea). Las anotaciones van a stdout para que Claude Code
# las incluya como contexto adicional (non-blocking hint).
set +e

[ "${XDD_TEMPORAL_AWARENESS:-1}" = "0" ] && exit 0
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-state.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-state.py" ] || exit 0

# Obtener sprint activo (best-effort)
ACTIVE_SPRINT=$(python3 "$SCRIPTS/xdd-state.py" sprint-status --json 2>/dev/null \
  | python3 -c "
import json, sys
try:
    rows = json.load(sys.stdin)
    active = [r for r in rows if r.get('status') == 'active']
    if active:
        r = active[0]
        started = r.get('started_at','')[:10]
        print(f\"{r['id']} (desde {started}): {r.get('goal','sin objetivo definido')}\")
except Exception:
    pass
" 2>/dev/null || echo "")

if [ -n "$ACTIVE_SPRINT" ]; then
  DATE_NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
  echo "[xdd:temporal] Sprint activo: $ACTIVE_SPRINT | Ahora: $DATE_NOW" >&2
fi

exit 0
