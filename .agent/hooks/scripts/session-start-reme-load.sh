#!/bin/bash
# Hook: session:start:reme-load — carga MEMORY.md + journal ReMe al iniciar sesion.
# Perfil: minimal+. Requiere XDD_REME=1 y reme-ai instalado.
# No-op si ReMe no esta activo o no instalado.
# Recibe JSON por stdin (SessionStart event). Exit 0 siempre (no bloquea).
set -eu

# No-op rapido si ReMe no esta activado
if [ "${XDD_REME:-0}" != "1" ]; then
  exit 0
fi

# No-op si reme-ai no esta instalado
if ! python3 -c "import reme" 2>/dev/null; then
  echo "[reme] WARN: XDD_REME=1 pero reme-ai no instalado. Ejecuta: pip install 'reme-ai[light]'" >&2
  exit 0
fi

PROJECT_DIR="${PWD}"
MEMORY_FILE="$PROJECT_DIR/MEMORY.md"
MEMORY_DIR="$PROJECT_DIR/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")

echo "[reme] Cargando memoria conversacional..."

# Cargar MEMORY.md (long-term)
if [ -f "$MEMORY_FILE" ]; then
  echo "[reme] MEMORY.md encontrado ($(wc -l < "$MEMORY_FILE") lineas)."
  echo "[reme] Contexto long-term disponible para el agente."
else
  echo "[reme] MEMORY.md no existe. Se creara al cerrar la primera sesion."
fi

# Cargar journal del dia anterior si existe
if [ -n "$YESTERDAY" ] && [ -f "$MEMORY_DIR/$YESTERDAY.md" ]; then
  echo "[reme] Journal del dia anterior ($YESTERDAY) encontrado."
  echo "[reme] Resumen de ayer disponible en: memory/$YESTERDAY.md"
fi

# Journal del dia actual
if [ -f "$MEMORY_DIR/$TODAY.md" ]; then
  echo "[reme] Journal de hoy ($TODAY) ya existe — sesion continuada."
fi

echo "[reme] ReMe activo. Modo: Completo+ReMe (memoria conversacional + codebase RAG)."
echo "[reme] Al cerrar sesion, hook stop:reme-summary escribira el journal de hoy."
exit 0
