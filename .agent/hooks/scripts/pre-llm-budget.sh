#!/bin/bash
# Sprint 19 ADR-0023: pre-LLM-call budget check.
# Lee tokens estimados desde stdin o XDD_TOKENS_ESTIMATE env var.
# Invoca xdd-context check con budget de xdd.config.yml.
set -eu

TOKENS="${XDD_TOKENS_ESTIMATE:-}"
if [ -z "$TOKENS" ]; then
  # Sin input → no-op (stub no bloquea)
  exit 0
fi

XDD_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$XDD_ROOT/scripts/xdd-context.py" check --tokens="$TOKENS"
RC=$?
# rc=0 ok, rc=1 warning (no bloquea), rc=2 block
if [ "$RC" -eq 2 ]; then
  echo "[hook] BLOCK: context budget exceeded" >&2
  exit 2
fi
exit 0
