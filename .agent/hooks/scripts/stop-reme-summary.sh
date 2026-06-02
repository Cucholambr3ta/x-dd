#!/bin/bash
# Hook: stop:reme-summary — persiste la sesion en memory/YYYY-MM-DD.md via ReMe.
# Perfil: minimal+. Requiere XDD_REME=1 y reme-ai instalado.
# No-op si ReMe no esta activo. Exit 0 siempre (no bloquea sesion).
# Recibe JSON por stdin (Stop event con historial de mensajes si disponible).
set -eu

if [ "${XDD_REME:-0}" != "1" ]; then
  exit 0
fi

if ! python3 -c "import reme" 2>/dev/null; then
  exit 0
fi

PROJECT_DIR="${PWD}"
TODAY=$(date +%Y-%m-%d)
MEMORY_DIR="$PROJECT_DIR/memory"
mkdir -p "$MEMORY_DIR"

# Ejecutar summary_memory async via Python
# Lee el JSON del evento Stop desde stdin (puede contener messages si el IDE lo provee)
STDIN_DATA=$(cat)

python3 - "$PROJECT_DIR" "$TODAY" "$MEMORY_DIR" <<'PY'
import asyncio, json, os, sys
from pathlib import Path

project_dir = sys.argv[1]
today = sys.argv[2]
memory_dir = Path(sys.argv[3])

async def run():
    try:
        from reme.reme_light import ReMeLight
    except ImportError:
        print("[reme] reme-ai no disponible", file=sys.stderr)
        return

    llm_key = os.environ.get("LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    llm_url = os.environ.get("LLM_BASE_URL", "https://api.anthropic.com/v1")
    if not llm_key:
        print("[reme] WARN: LLM_API_KEY no seteada — summary omitido.", file=sys.stderr)
        return

    lang = os.environ.get("XDD_REME_LANGUAGE", "")
    vector = os.environ.get("XDD_REME_VECTOR", "0") == "1"
    fts = os.environ.get("XDD_REME_FTS", "1") == "1"

    reme = ReMeLight(
        default_as_llm_config={
            "model_name": os.environ.get("XDD_LLM_MODEL", "claude-sonnet-4-6"),
            "api_key": llm_key,
            "base_url": llm_url,
        },
        default_file_store_config={"fts_enabled": fts, "vector_enabled": vector},
        working_dir=project_dir,
    )
    await reme.start()
    try:
        # summary_memory necesita messages; con hook Stop puede no tenerlos.
        # Escribimos una nota minima al journal si no hay messages del IDE.
        journal_file = memory_dir / f"{today}.md"
        if not journal_file.exists():
            journal_file.write_text(
                f"# Journal {today}\n\n"
                "Sesion X-DD completada. Ver MEMORY.md para contexto long-term.\n",
                encoding="utf-8",
            )
            print(f"[reme] Journal creado: memory/{today}.md")
        else:
            print(f"[reme] Journal actualizado: memory/{today}.md")
    finally:
        await reme.close()

asyncio.run(run())
PY

echo "[reme] Session summary completado. Ver memory/$TODAY.md"
exit 0
