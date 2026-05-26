#!/bin/bash
# X-DD Doctor — verifica el estado de las herramientas del ecosistema.
# No aborta al primer fallo: lista todo y reporta al final.
set -u

XDD_VERSION="0.1.0-dev"

case "${1:-}" in
  -h|--help)
    cat <<'EOF'
xdd-doctor — diagnóstico del entorno X-DD.

Uso:
  bash scripts/xdd-doctor.sh
  bash scripts/xdd-doctor.sh --help | --version

Comprueba núcleo, memoria, testing, seguridad y estructura del proyecto.
Reporta ✓ / ⚠ / ✗ y resumen final.

Salida:
  - exit 0 si no hay faltantes críticos.
  - exit 1 si falta alguna dep `required: yes`.

NOTA: Sprint 3 reescribe este script con SemVer real y --json.
EOF
    exit 0
    ;;
  -v|--version)
    echo "xdd-doctor v${XDD_VERSION}"
    exit 0
    ;;
esac

PASS=0; FAIL=0; WARN=0

check () {
  local name="$1"; local cmd="$2"; local required="$3"  # required: yes|no
  if command -v "$cmd" >/dev/null 2>&1; then
    local ver
    ver="$($cmd --version 2>&1 | head -1 || true)"
    printf "  ✓ %-14s %s\n" "$name" "$ver"
    PASS=$((PASS+1))
  else
    if [ "$required" = "yes" ]; then
      printf "  ✗ %-14s FALTA (requerido)\n" "$name"
      FAIL=$((FAIL+1))
    else
      printf "  ⚠ %-14s ausente (opcional)\n" "$name"
      WARN=$((WARN+1))
    fi
  fi
}

echo "=== X-DD Doctor ==="
echo
echo "[Núcleo]"
check "git"        git        yes
check "node"       node       yes
check "npm"        npm        yes
check "docker"     docker     no
check "claude/oc"  claude     no
command -v claude >/dev/null 2>&1 || check "opencode" opencode no

echo
echo "[Memoria]"
check "mempalace"  mempalace  no

echo
echo "[Testing]"
check "vitest"     vitest     no
check "playwright" playwright no

echo
echo "[Seguridad]"
check "semgrep"    semgrep    no
check "gitleaks"   gitleaks   no
check "trivy"      trivy      no
check "nuclei"     nuclei     no

echo
echo "[Estructura del proyecto actual]"
for f in CLAUDE.md memoria.md lecciones.md xdd.profile.yml .agent/workflows .claude/settings.json prompts templates; do
  if [ -e "$f" ]; then
    printf "  ✓ %s\n" "$f"
  else
    printf "  ⚠ %s ausente\n" "$f"
    WARN=$((WARN+1))
  fi
done

# Detección de perfil
if [ -f "xdd.profile.yml" ]; then
  PROFILE=$(grep -E '^profile:' xdd.profile.yml | awk '{print $2}' | tr -d '"' || true)
  printf "\n[Perfil del proyecto]\n  → %s\n" "${PROFILE:-no declarado}"
fi

echo
echo "Resumen: $PASS OK, $WARN warnings, $FAIL faltantes críticos."
[ $FAIL -eq 0 ] || exit 1
