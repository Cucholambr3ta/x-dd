#!/bin/bash
# pre:edit:config-protection — bloquea modificación de configs sensibles.
# Profile: strict. Steers al agente a arreglar el código, no a debilitar la config.
set -eu

# Lista de paths protegidos (configs que NO deben relajarse silenciosamente)
PROTECTED=(
  ".markdownlint.yaml"
  ".markdownlint.json"
  ".editorconfig"
  ".gitignore"
  ".pre-commit-config.yaml"
  ".eslintrc"
  ".eslintrc.js"
  ".eslintrc.json"
  ".prettierrc"
  ".prettierrc.json"
  "eslint.config.js"
  "ruff.toml"
  "pyproject.toml"
  "tsconfig.json"
  ".github/renovate.json"
  ".github/dependabot.yml"
  "schemas/"
)

# Obtener path del input
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

# Verificar contra paths protegidos
for prot in "${PROTECTED[@]}"; do
  if [[ "$FILE_PATH" == *"$prot"* ]]; then
    if [ "${XDD_ALLOW_CONFIG_EDIT:-}" = "1" ]; then
      echo "[xdd:hook] WARN — editando config protegido: $FILE_PATH (XDD_ALLOW_CONFIG_EDIT=1)" >&2
      exit 0
    fi
    echo "[xdd:hook] BLOCKED — modificación a config protegido: $FILE_PATH" >&2
    echo "[xdd:hook] Steers: ¿podés arreglar el código en lugar de debilitar la config?" >&2
    echo "[xdd:hook] Si es realmente necesario: export XDD_ALLOW_CONFIG_EDIT=1" >&2
    exit 2
  fi
done

exit 0
