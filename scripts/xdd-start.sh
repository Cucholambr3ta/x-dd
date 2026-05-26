#!/bin/bash
# X-DD Start — inicializa MemPalace (si está disponible) y lanza el orquestador
set -eu

PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR"

LOG_DIR="${HOME}/.mempalace"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/mine.log"

echo "[X-DD] Proyecto: $PROJECT_DIR"

# MemPalace: opcional, no debe abortar el arranque si falta
if command -v mempalace >/dev/null 2>&1; then
  echo "[X-DD] Inicializando MemPalace..."
  mempalace init "$PROJECT_DIR" >>"$LOG_FILE" 2>&1 || true
  if mempalace mine "$PROJECT_DIR" >>"$LOG_FILE" 2>&1; then
    echo "[X-DD] MemPalace indexado. Log: $LOG_FILE"
  else
    echo "[X-DD] WARN: mempalace mine falló (ver $LOG_FILE). Continuando sin indexar."
  fi
else
  echo "[X-DD] WARN: 'mempalace' no encontrado. Omitiendo indexación semántica."
  echo "[X-DD]       Instalación: ver INSTALL.md sección MemPalace."
fi

# Git hook post-commit (idempotente)
if [ -d ".git" ] && [ -f "./scripts/hooks/post-commit" ]; then
  git config core.hooksPath ./scripts/hooks
  chmod +x ./scripts/hooks/post-commit
  echo "[X-DD] Git hook post-commit activado."
fi

echo "[X-DD] Iniciando orquestador..."

if command -v claude >/dev/null 2>&1; then
  exec claude
elif command -v opencode >/dev/null 2>&1; then
  exec opencode
else
  echo "[X-DD] ERROR: No se encontró 'claude' ni 'opencode'. Instala uno (ver INSTALL.md)."
  exit 1
fi
