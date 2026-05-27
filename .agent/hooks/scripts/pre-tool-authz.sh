#!/bin/bash
# Sprint 21 ADR-0028: hook PreToolUse que invoca xdd-authz.
# Si exit 2 = deny → bloquea tool call.
# Si exit 1 = require_approval → orchestrator debería prompt humano.
set -eu

TOOL="${XDD_TOOL_NAME:-}"
ARGS_JSON="${XDD_TOOL_ARGS:-{}}"
if [ -z "$TOOL" ]; then
  exit 0  # no info, no-op
fi

XDD_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$XDD_ROOT/scripts/xdd-authz.py" check --tool="$TOOL" --args="$ARGS_JSON"
RC=$?
case "$RC" in
  0) exit 0 ;;
  1) echo "[hook] require_approval: $TOOL" >&2; exit 1 ;;
  2) echo "[hook] DENY: $TOOL blocked by authz policy" >&2; exit 2 ;;
  *) exit 0 ;;
esac
