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

# Heurística 3 (S11): analiza traces OTel de la sesión → patrones de tool calls
TRACES_DIR="${XDD_OTEL_DIR:-$ROOT/.xdd/traces/spans}"
if [ -d "$TRACES_DIR" ]; then
    TOOL_PATTERN=$(python3 - <<PYEOF 2>/dev/null
import json, sys, pathlib, collections
traces_dir = pathlib.Path("$TRACES_DIR")
tool_counts = collections.Counter()
for f in sorted(traces_dir.glob("*.json"))[-50:]:
    try:
        s = json.loads(f.read_text(encoding="utf-8"))
        if s.get("kind") == "tool.call":
            tool_counts[s.get("attributes", {}).get("tool_name", "unknown")] += 1
    except (json.JSONDecodeError, OSError, KeyError):
        continue
if tool_counts:
    top = tool_counts.most_common(3)
    print(",".join(f"{t}:{n}" for t,n in top))
PYEOF
)
    if [ -n "$TOOL_PATTERN" ]; then
        python3 "$STATE_SCRIPT" record-instinct \
          --pattern "frequent tools: $TOOL_PATTERN" \
          --category tool_use \
          --context "session=$SESSION_ID" \
          --session-id "$SESSION_ID" >>"$HOME/.xdd/learning.log" 2>&1 &
    fi
fi

exit 0
