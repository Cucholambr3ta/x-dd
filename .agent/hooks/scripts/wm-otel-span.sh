#!/bin/bash
# wm:otel:span — emite span llm.call con input/output tokens y latencia.
# Sprint 18 ADR-0021. Invocado por wrap_model_call del runtime X-DD.
# Recibe JSON por stdin: {model, input_tokens, output_tokens, duration_ms, run_id}.
# No bloquea. No-op fuera de repos X-DD.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-otel.py" ] || exit 0

DATA=""
if ! [ -t 0 ]; then DATA=$(cat); fi

MODEL=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('model','llm'))" "$DATA" 2>/dev/null || echo "llm")
DUR=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('duration_ms', 0))" "$DATA" 2>/dev/null || echo "0")
IN_TOK=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('input_tokens', 0))" "$DATA" 2>/dev/null || echo "0")
OUT_TOK=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('output_tokens', 0))" "$DATA" 2>/dev/null || echo "0")

ATTRS=$(python3 -c "import json; print(json.dumps({'model': '$MODEL', 'input_tokens': $IN_TOK, 'output_tokens': $OUT_TOK}))" 2>/dev/null || echo '{}')

python3 "$SCRIPTS/xdd-otel.py" emit \
  --name "llm.call" --kind "llm.call" \
  --duration-ms "$DUR" --attrs "$ATTRS" >/dev/null 2>&1 || true

exit 0
