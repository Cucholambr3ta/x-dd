#!/bin/bash
# am:cost:record — registra el costo de la llamada al modelo en SQLite cost.db.
# Sprint 18 ADR-0022. Invocado por after_model del runtime X-DD.
# Recibe JSON por stdin: {model, input_tokens, output_tokens, run_id}.
# No bloquea. No-op fuera de repos X-DD.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-cost.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-cost.py" ] || exit 0

DATA=""
if ! [ -t 0 ]; then DATA=$(cat); fi

MODEL=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('model','unknown'))" "$DATA" 2>/dev/null || echo "unknown")
IN_TOK=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('input_tokens', 0))" "$DATA" 2>/dev/null || echo "0")
OUT_TOK=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('output_tokens', 0))" "$DATA" 2>/dev/null || echo "0")
RUN_ID=$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('run_id',''))" "$DATA" 2>/dev/null || echo "")

python3 "$SCRIPTS/xdd-cost.py" record \
  --model "$MODEL" \
  --input-tokens "$IN_TOK" \
  --output-tokens "$OUT_TOK" \
  ${RUN_ID:+--run-id "$RUN_ID"} >/dev/null 2>&1 || true

exit 0
