#!/bin/bash
# post:write:auto-organize — Sprint 31 / ADR-0041
# Hook PostToolUse que invoca xdd-organize en modo apply (non-destructive) tras
# Write/Edit/NotebookEdit. Real-time auto-organize sin destruir.
#
# Comportamiento:
#   - NO bloquea (exit 0 siempre)
#   - Async (no demora respuesta del orquestador)
#   - Solo gitignore_only + move (NO gitignore_and_delete sin --confirm-delete)
#   - Opt-out: XDD_NO_ORGANIZE=1 env var (mismo opt-out que xdd-organize)
#
# Output: log line por acción al stderr. Captura en .xdd/organize.log si dir existe.
set +e

# Skip si opt-out activo
[ "${XDD_NO_ORGANIZE:-0}" = "1" ] && exit 0

# Resolver path del repo X-DD source (script xdd-organize vive ahí)
XDD_ORGANIZE=""
if [ -x ./scripts/xdd-organize.sh ]; then
  XDD_ORGANIZE="./scripts/xdd-organize.sh"
elif [ -x "$HOME/Documentos/Desarrollos/scripts/xdd-organize.sh" ]; then
  XDD_ORGANIZE="$HOME/Documentos/Desarrollos/scripts/xdd-organize.sh"
elif command -v xdd-organize >/dev/null 2>&1; then
  XDD_ORGANIZE="$(command -v xdd-organize)"
else
  # No disponible — skip silencioso
  exit 0
fi

# Ejecutar apply (non-destructive). Log a .xdd/organize.log si dir existe.
LOG=""
[ -d .xdd ] && LOG=".xdd/organize.log"

if [ -n "$LOG" ]; then
  echo "=== $(date -Iseconds) post:write:auto-organize ===" >> "$LOG"
  bash "$XDD_ORGANIZE" apply --dest=. 2>&1 | tee -a "$LOG" >&2
else
  bash "$XDD_ORGANIZE" apply --dest=. 2>&1 >&2
fi

exit 0
