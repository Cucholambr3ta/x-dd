#!/bin/bash
# Hook: pre:commit:gitflow — Enforces GitFlow branch naming convention.
# Permite: main, develop, feature/*, fix/*, hotfix/*, release/*, chore/*, docs/*, refactor/*
# Bloquea commit si el branch no sigue la convencion (exit 2).
# Perfil: standard+.
set -eu

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Branches siempre permitidos
case "$BRANCH" in
  main|master|develop|HEAD) exit 0 ;;
esac

# Pattern GitFlow
if echo "$BRANCH" | grep -qE '^(feature|fix|hotfix|release|chore|docs|refactor|test|ci|build|perf|style)/[a-z0-9/_-]+$'; then
  exit 0
fi

# Branch no sigue convencion
echo "[xdd-hook] ERROR: branch '$BRANCH' no sigue GitFlow." >&2
echo "[xdd-hook] Convencion: feature/*, fix/*, hotfix/*, release/*, chore/*, docs/*, refactor/*" >&2
echo "[xdd-hook] Ejemplo: git checkout -b feature/mi-nueva-feature" >&2
exit 2
