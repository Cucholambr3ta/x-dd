#!/bin/bash
# ba:otel:trace-start — abre span OTel agent.invocation al inicio del loop del agente.
# Sprint 18 ADR-0021. Invocado por before_agent del runtime X-DD.
# No bloquea. No-op si xdd-otel no disponible o no es repo X-DD.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || exit 0

# Leer session_id del stdin (JSON del runtime) o generar UUID simple
SESSION_ID=""
if ! [ -t 0 ]; then
  SESSION_ID=$(python3 -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print(d.get('session_id') or d.get('run_id') or '')" 2>/dev/null || echo "")
fi
SESSION_ID="${SESSION_ID:-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:16])' 2>/dev/null || echo 'agent0')}"

SPAN_FILE="${HOME}/.xdd/traces/.current_agent_span"
mkdir -p "$(dirname "$SPAN_FILE")"

SPAN=$(python3 "$SCRIPTS/xdd-otel.py" span-start \
  --name "agent.invocation" --kind "agent.invocation" \
  --attrs "{\"session_id\": \"$SESSION_ID\"}" --json 2>/dev/null)

if [ -n "$SPAN" ]; then
  printf '%s' "$SPAN" > "$SPAN_FILE"
fi
exit 0
