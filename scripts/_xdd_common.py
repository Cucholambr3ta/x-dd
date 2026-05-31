"""_xdd_common.py — utilidades compartidas por los scripts X-DD.

Stdlib-first (ADR-0003). Pensado para importarse tanto en modo standalone
(`python scripts/xdd-*.py`) como empaquetado en el wheel (`xdd_cli/scripts/`,
ejecutado vía runpy). Cada script hace `sys.path.insert(0, str(Path(__file__).parent))`
antes de `from _xdd_common import ...` para que la importación resuelva en ambos modos.

Provee:
  - utcnow_iso()     timestamp UTC a precisión de segundo  (%Y-%m-%dT%H:%M:%SZ)
  - utcnow_iso_us()  timestamp UTC a precisión de microseg. (%Y-%m-%dT%H:%M:%S.%fZ)
  - read_version()   versión canónica (archivo VERSION → metadata del paquete → fallback)

IMPORTANTE: las dos variantes de timestamp NO son intercambiables. xdd-gate.py firma
`last_ts` con HMAC a precisión de segundo; cambiar su formato rompería firmas ya emitidas.
Observabilidad (agui/otel/replay) usa microsegundos. Mantener ambas.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

# Fallback embebido: única fuente literal de versión que el test de consistencia
# vigila. Debe coincidir con el archivo VERSION en la raíz del repo.
_VERSION_FALLBACK = "0.1.2"


def utcnow_iso() -> str:
    """UTC ISO-8601 a precisión de segundo. Usado por gate/state/eval/etc."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utcnow_iso_us() -> str:
    """UTC ISO-8601 a precisión de microsegundo. Usado por observabilidad."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def read_version() -> str:
    """Versión canónica, resuelta en orden:

    1. Archivo VERSION en la raíz del repo (modo editable/standalone).
    2. Metadata del paquete instalado `x-dd` (modo wheel, sin VERSION adjunto).
    3. Fallback literal embebido (último recurso).
    """
    # 1. VERSION en la raíz del repo: scripts/ → repo_root/VERSION (editable)
    #    o xdd_cli/scripts/ → no existe (wheel), cae al paso 2.
    version_file = Path(__file__).resolve().parent.parent / "VERSION"
    try:
        v = version_file.read_text(encoding="utf-8").strip()
        if v:
            return v
    except OSError:
        pass

    # 2. Metadata del paquete instalado.
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("x-dd")
    except (PackageNotFoundError, ImportError):
        pass

    # 3. Fallback.
    return _VERSION_FALLBACK


# Aliases retrocompatibles: varios scripts definían `utcnow()` a precisión de
# segundo. Mantener el nombre evita tocar sus call-sites.
utcnow = utcnow_iso
