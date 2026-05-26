#!/bin/bash
# postCreate.sh — setup automático del Codespace / devcontainer.
set -eu

echo "[devcontainer] X-DD postCreate setup..."

# Python deps mínimas
pip install --quiet pytest jsonschema pyyaml || true

# Node deps mínimas (markdownlint para CI local)
sudo npm install -g markdownlint-cli2@latest commitlint @commitlint/cli @commitlint/config-conventional 2>/dev/null || true

# bats-core
if ! command -v bats >/dev/null 2>&1; then
  echo "[devcontainer] Installing bats-core..."
  sudo apt-get update -qq && sudo apt-get install -y -qq bats || true
fi

# Pre-commit
pip install --quiet pre-commit || true
pre-commit install 2>/dev/null || true

# MemPalace (opcional pero recomendado)
if ! command -v mempalace >/dev/null 2>&1; then
  echo "[devcontainer] Instalando MemPalace (opcional)..."
  pip install --quiet mempalace || echo "[devcontainer] MemPalace install falló (no crítico)."
fi

# Mostrar estado
echo
echo "[devcontainer] X-DD doctor:"
bash scripts/xdd-doctor.sh 2>&1 | tail -10 || true

echo
echo "[devcontainer] ✓ Setup completado."
echo "  - bats:      $(bats --version 2>&1 | head -1)"
echo "  - python3:   $(python3 --version)"
echo "  - node:      $(node --version 2>&1)"
echo "  - gh:        $(gh --version 2>&1 | head -1)"
echo "  - mempalace: $(mempalace --version 2>&1 | head -1 || echo 'no instalado (opcional)')"
echo
echo "Empezá con:  make help"
echo "O probá:     make test"
