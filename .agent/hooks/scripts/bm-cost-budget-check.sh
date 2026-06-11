#!/bin/bash
# bm:cost:budget-check — verifica el presupuesto de costo antes de llamar al modelo.
# Sprint 18 ADR-0022. Invocado por before_model del runtime X-DD.
# Exit 0 = dentro del presupuesto (continúa). Exit 1 = advertencia (no bloquea).
# No-op fuera de repos X-DD.
set +e
[ -f "$PWD/.agent/hooks/hooks.json" ] || [ -f "$PWD/xdd.profile.yml" ] || exit 0

SCRIPTS="$PWD/scripts"
[ -f "$SCRIPTS/xdd-cost.py" ] || SCRIPTS="$(dirname "$0")/../../scripts"
[ -f "$SCRIPTS/xdd-cost.py" ] || exit 0

# Chequeo: costo acumulado del día vs budget declarado en xdd.config.yml (default $5)
BUDGET_USD="${XDD_COST_BUDGET_USD:-5.0}"

TOTAL=$(python3 "$SCRIPTS/xdd-cost.py" report --since 1d --json 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(r.get('total_usd',0) for r in d.get('rows',[])))" 2>/dev/null || echo "0")
OVER=$(python3 -c "
try:
    t=float('$TOTAL'); b=float('$BUDGET_USD')
    print('1' if t >= b else '0')
except:
    print('0')
" 2>/dev/null)

if [ "$OVER" = "1" ]; then
  echo "[xdd:cost] WARN: costo acumulado ($TOTAL USD) ≥ presupuesto ($BUDGET_USD USD). Revisa xdd-cost report." >&2
fi
exit 0  # nunca bloquea; solo advierte
