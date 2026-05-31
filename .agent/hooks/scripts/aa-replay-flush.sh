#!/bin/bash
# aa:replay:flush — cierra el span OTel y flushea eventos de la sesión.
# Sprint 18 ADR-0021. Invocado por after_agent del runtime X-DD.
# No bloquea. No-op si no es repo X-DD o falta xdd-otel.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || exit 0

SPAN_FILE="${HOME}/.xdd/traces/.current_agent_span"
if [ -f "$SPAN_FILE" ]; then
  SPAN_ID=$(python3 -c "import json; d=json.load(open('$SPAN_FILE')); print(d.get('span_id',''))" 2>/dev/null || echo "")
  if [ -n "$SPAN_ID" ]; then
    python3 "$SCRIPTS/xdd-otel.py" span-end --id "$SPAN_ID" --status ok >/dev/null 2>&1 || true
  fi
  rm -f "$SPAN_FILE"
fi
exit 0
