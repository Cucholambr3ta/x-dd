#!/bin/bash
# X-DD Workflow Linter — valida los archivos .agent/workflows/*.md
# - Comprueba frontmatter con campo `description:`
# - Comprueba que no haya rutas absolutas del host (viola CLAUDE.md)
# - Reporta workflows sin documentar en prompts/workflows/03_workflows_catalog.md
set -u

ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"
WF_DIR="$ROOT/.agent/workflows"
CATALOG="$ROOT/prompts/workflows/03_workflows_catalog.md"

ERR=0; WARN=0

if [ ! -d "$WF_DIR" ]; then
  echo "[lint] ERROR: $WF_DIR no existe."
  exit 1
fi

echo "=== Lint .agent/workflows/ ==="

for f in "$WF_DIR"/*.md; do
  base="$(basename "$f" .md)"
  # Saltar READMEs (documentación, no workflow ejecutable)
  case "$base" in README|readme) continue ;; esac
  # 1. Frontmatter description
  if ! head -10 "$f" | grep -qE '^description:'; then
    echo "  ✗ $base — falta 'description:' en frontmatter"
    ERR=$((ERR+1))
  fi
  # 2. Rutas absolutas del host (acepta /usr, /etc, /var, /tmp, /opt, /home como ejemplos genéricos solo en bloques de código)
  if grep -nE '(^|[^./])/(home|Users|mnt|media)/[A-Za-z0-9_-]+/' "$f" >/dev/null 2>&1; then
    echo "  ⚠ $base — posibles rutas absolutas del host (revisar)"
    WARN=$((WARN+1))
  fi
  # 3. Documentación en catálogo
  if [ -f "$CATALOG" ] && ! grep -qF "$base" "$CATALOG"; then
    echo "  ⚠ $base — no aparece en prompts/workflows/03_workflows_catalog.md"
    WARN=$((WARN+1))
  fi
done

echo
echo "Resumen: $ERR errores, $WARN warnings."
[ $ERR -eq 0 ] || exit 1
