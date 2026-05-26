#!/bin/bash
# pre:bash:dangerous-command — bloquea comandos peligrosos.
# Recibe el comando como JSON por stdin (formato Claude Code) o $1.
# Exit 2 = bloquea ejecución; Exit 0 = permite.
set -eu

# Obtener el comando del input
CMD=""
if [ -t 0 ]; then
  CMD="${1:-}"
else
  RAW=$(cat || true)
  if command -v python3 >/dev/null 2>&1; then
    CMD=$(echo "$RAW" | python3 -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print((d.get('tool_input') or {}).get('command') or '')" 2>/dev/null || echo "")
  else
    CMD=$(echo "$RAW" | grep -oE '"command"\s*:\s*"[^"]*"' | head -1 | sed 's/.*"command"\s*:\s*"\(.*\)"/\1/' || echo "")
  fi
fi

[ -z "$CMD" ] && exit 0

# Patrones peligrosos
DANGEROUS_PATTERNS=(
  'rm[[:space:]]+-[rR][fF]?[[:space:]]+/'
  'rm[[:space:]]+-[fF][rR]?[[:space:]]+/'
  'git[[:space:]]+push[[:space:]]+.*--force'
  'git[[:space:]]+push[[:space:]]+.*-f([[:space:]]|$)'
  'git[[:space:]]+reset[[:space:]]+--hard[[:space:]]+(origin|HEAD~)'
  'git[[:space:]]+clean[[:space:]]+-[fdx]'
  'chmod[[:space:]]+-?R?[[:space:]]+777'
  'curl[[:space:]]+.*\|[[:space:]]*(bash|sh)([[:space:]]|$)'
  'wget[[:space:]]+.*\|[[:space:]]*(bash|sh)([[:space:]]|$)'
  'dd[[:space:]]+if=.*of=/dev/(sda|hda|nvme)'
  ':(){.*}'
  '>\s*/dev/(sda|hda|nvme)'
)

for pat in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$CMD" | grep -qE "$pat"; then
    echo "[xdd:hook] BLOCKED — comando peligroso detectado:" >&2
    echo "[xdd:hook]   patrón: $pat" >&2
    echo "[xdd:hook]   comando: $CMD" >&2
    echo "[xdd:hook] Si es intencional, ejecutalo manualmente fuera del agente." >&2
    exit 2
  fi
done

exit 0
