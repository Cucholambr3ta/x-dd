#!/bin/bash
# post:bash:pr-logger — log de PR URL tras gh pr create.
# No bloquea. Async OK.
set +e

CMD=""
OUTPUT=""
if [ ! -t 0 ]; then
  RAW=$(cat || true)
  if command -v python3 >/dev/null 2>&1; then
    CMD=$(echo "$RAW" | python3 -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print((d.get('tool_input') or {}).get('command') or '')" 2>/dev/null || echo "")
    OUTPUT=$(echo "$RAW" | python3 -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print((d.get('tool_output') or {}).get('output') or '')" 2>/dev/null || echo "")
  fi
fi

# Detectar gh pr create
if echo "$CMD" | grep -qE "gh\s+pr\s+create"; then
  PR_URL=$(echo "$OUTPUT" | grep -oE 'https://github\.com/[^/]+/[^/]+/pull/[0-9]+' | head -1)
  if [ -n "$PR_URL" ]; then
    mkdir -p ~/.xdd
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) PR opened: $PR_URL" >> ~/.xdd/pr-history.log
    echo "[xdd:hook] PR logged → $PR_URL"
  fi
fi
exit 0
