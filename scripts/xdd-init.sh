#!/bin/bash
# X-DD Init — bootstrap portable de un proyecto nuevo
# Uso: bash ./scripts/xdd-init.sh [/ruta/al/proyecto/nuevo]
#      Sin argumento, inicializa en $PWD.
set -eu

# Directorio del repo X-DD (donde vive este script)
XDD_ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"
DEST="${1:-$PWD}"

if [ "$XDD_ROOT" = "$DEST" ]; then
  echo "[xdd-init] ERROR: el destino no puede ser el propio repo X-DD."
  exit 1
fi

mkdir -p "$DEST"
cd "$DEST"

echo "[xdd-init] Origen: $XDD_ROOT"
echo "[xdd-init] Destino: $DEST"

copy_if_absent () {
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    echo "[xdd-init] SKIP existente: $dst"
  else
    cp -r "$src" "$dst"
    echo "[xdd-init] Copiado: $dst"
  fi
}

copy_if_absent "$XDD_ROOT/.agent"    "./.agent"
copy_if_absent "$XDD_ROOT/.claude"   "./.claude"
copy_if_absent "$XDD_ROOT/prompts"   "./prompts"
copy_if_absent "$XDD_ROOT/scripts"   "./scripts"
copy_if_absent "$XDD_ROOT/templates" "./templates"
copy_if_absent "$XDD_ROOT/CLAUDE.md" "./CLAUDE.md"

# Templates de memoria (instanciados, no solo plantillas)
if [ ! -f "./memoria.md" ]; then
  cp "$XDD_ROOT/templates/memoria.template.md" "./memoria.md"
  echo "[xdd-init] memoria.md creado desde template."
fi
if [ ! -f "./lecciones.md" ]; then
  cp "$XDD_ROOT/templates/lecciones.template.md" "./lecciones.md"
  echo "[xdd-init] lecciones.md creado desde template."
fi

# Perfil del proyecto (xdd.profile.yml)
if [ ! -f "./xdd.profile.yml" ]; then
  cp "$XDD_ROOT/templates/xdd.profile.template.yml" "./xdd.profile.yml"
  echo "[xdd-init] xdd.profile.yml creado desde template. Editalo para declarar tu tipo de producto y stacks."
fi

# Git init si no es repo
if [ ! -d ".git" ]; then
  git init -q
  echo "[xdd-init] Repositorio git inicializado."
fi

chmod +x ./scripts/*.sh ./scripts/hooks/* 2>/dev/null || true

cat <<EOF

[xdd-init] ✓ Bootstrap completado en: $DEST

Siguientes pasos:
  1. cd "$DEST"
  2. Edita memoria.md con la identidad del proyecto.
  3. Edita xdd.profile.yml: declara tipo de producto y stacks (flags, analytics, cloud...).
  4. Verifica el entorno:   bash ./scripts/xdd-doctor.sh
  5. Arranca X-DD:          bash ./scripts/xdd-start.sh
EOF
