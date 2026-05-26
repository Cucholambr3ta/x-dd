#!/bin/bash
# X-DD Start — inicializa MemPalace y lanza el orquestador
set -e

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

echo "[X-DD] Inicializando MemPalace en $PROJECT_DIR..."

# Crear wing si no existe, luego re-indexar
mempalace init "$PROJECT_DIR" 2>/dev/null || true
mempalace mine "$PROJECT_DIR"

# Configurar git hook si hay repo git
if [ -d ".git" ]; then
  git config core.hooksPath ./scripts/hooks
  chmod +x ./scripts/hooks/post-commit
  echo "[X-DD] Git hook post-commit activado."
fi

echo "[X-DD] MemPalace listo. Iniciando orquestador..."

# Lanzar orquestador (Claude Code o OpenCode según lo que esté instalado)
if command -v claude &>/dev/null; then
  claude
elif command -v opencode &>/dev/null; then
  opencode
else
  echo "[X-DD] ERROR: No se encontró 'claude' ni 'opencode'. Instala uno de los dos (ver INSTALL.md)."
  exit 1
fi
