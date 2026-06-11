#!/bin/bash
# wt:otel:span — emite span tool.call con nombre de tool, args y duración.
# Sprint 18 ADR-0021. Invocado por wrap_tool_call del runtime X-DD.
# Recibe JSON por stdin: {tool_name, duration_ms, run_id}.
# No bloquea. No-op fuera de repos X-DD.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || exit 0

DATA=""
if ! [ -t 0 ]; then DATA=$(cat); fi

TOOL=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('tool_name','tool'))" "$DATA" 2>/dev/null || echo "tool")
DUR=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('duration_ms', 0))" "$DATA" 2>/dev/null || echo "0")

ATTRS=$(python3 -c "import json; print(json.dumps({'tool_name': '$TOOL'}))" 2>/dev/null || echo '{}')

python3 "$SCRIPTS/xdd-otel.py" emit \
  --name "tool.call" --kind "tool.call" \
  --duration-ms "$DUR" --attrs "$ATTRS" >/dev/null 2>&1 || true

exit 0
