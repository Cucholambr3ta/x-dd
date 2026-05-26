#!/bin/bash
# pre:write:doc-file-warning — advierte sobre archivos .md fuera de paths estándar.
# Exit 0 siempre (solo warn).
set -eu

FILE_PATH=""
if [ -t 0 ]; then
  FILE_PATH="${1:-}"
else
  RAW=$(cat || true)
  if command -v python3 >/dev/null 2>&1; then
    FILE_PATH=$(echo "$RAW" | python3 -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print((d.get('tool_input') or {}).get('file_path') or '')" 2>/dev/null || echo "")
  fi
fi

[ -z "$FILE_PATH" ] && exit 0

# Solo aplica a .md
case "$FILE_PATH" in
  *.md|*.MD|*.Md) ;;
  *) exit 0 ;;
esac

# Paths estándar permitidos sin warn
case "$FILE_PATH" in
  *README.md|*CHANGELOG.md|*CONTRIBUTING.md|*CODE_OF_CONDUCT.md|*SECURITY.md|*LICENSE.md|*NOTICE.md|*CLAUDE.md|*AGENTS.md|*SOUL.md|*RULES.md|*MEMORY.md|*memoria.md|*lecciones.md|*MEJORAS-X-DD.md|*DEPENDENCIES.md|*PROJ-MASTER-PLAN.md|*WORKING-CONTEXT.md|*EVALUATION.md|*the-*-guide.md)
    exit 0 ;;
  docs/*|.xdd/*|.agent/*|prompts/*|templates/*|schemas/*|RELEASES/*|skills/*)
    exit 0 ;;
  */docs/*|*/.xdd/*|*/.agent/*|*/prompts/*|*/templates/*|*/schemas/*|*/RELEASES/*|*/skills/*|*SKILL.md|*ADR-*.md|*adr/*.md)
    exit 0 ;;
esac

echo "[xdd:hook] WARN — creando archivo .md fuera de paths estándar: $FILE_PATH" >&2
echo "[xdd:hook] Considerá: docs/, .xdd/, prompts/, templates/, skills/, o uno de los archivos raíz canónicos." >&2
exit 0
