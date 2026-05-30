#!/usr/bin/env python3
"""xdd-gate.py — Gate keeper programático del pipeline X-DD.

Cumple ADR-0006: cada `approve` firma con HMAC-SHA256 sobre
(phase, sorted_checksums, approver, timestamp_utc_iso) usando
una clave secreta local en .xdd/.gate-key (gitignored).

Comandos:
  init       — Genera .xdd/.gate-key si no existe (idempotente).
  validate   — Valida una fase: status APROBADO + artefactos presentes
               + checksums coinciden + firma HMAC válida.
  transition — Comprueba que from→to es secuencial y que `from` está APROBADO.
  approve    — Marca una fase como APROBADO, captura checksums y firma.
  status     — Resumen JSON del estado de todas las fases.

Salida: humano-legible por defecto; --json para machine-readable.
Exit 0 si OK; 1 si gate falla; 2 si error de uso.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable

__version__ = "0.1.0-dev"


class Status(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVIEW = "EN_REVIEW"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


# Orden inmutable de fases (Constitución Art. 9).
PHASES: list[tuple[str, list[str]]] = [
    ("briefing", [".xdd/briefing/SPEC.md", ".xdd/briefing/FEATURES.md"]),
    ("spec",     [".xdd/spec/DOMAIN.md", ".xdd/spec/THREATS.md"]),
    ("plan",     [".xdd/plan/PLAN.md"]),
    ("build",    [".xdd/build/"]),
    ("qa",       [".xdd/qa/QA_REPORT.md"]),
    ("retro",    [".xdd/retro/lecciones.md"]),
    # Fase aditiva (append-only). NO insertar antes de retro: cambiar el set de
    # artefactos de una fase ya firmada rompe su firma HMAC. Append al final es
    # seguro — proyectos viejos dejan `docs` en PENDIENTE, nunca en INVÁLIDO.
    # Producida por xdd-readme.py vía /cierre-fase.
    ("docs",     [".xdd/docs/README.md"]),
]
PHASE_IDS = [p[0] for p in PHASES]
PHASE_ARTIFACTS = dict(PHASES)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def checksum(path: Path) -> str:
    """SHA-256 truncado a 16 hex chars (suficiente para detectar manipulación
    en archivos versionados; no es defensa contra colisión deliberada — la firma
    HMAC sí lo es)."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    if path.is_file():
        h.update(path.read_bytes())
    else:
        for f in sorted(path.rglob("*")):
            if f.is_file():
                try:
                    h.update(f.relative_to(path).as_posix().encode())
                    h.update(f.read_bytes())
                except OSError:
                    continue
    return h.hexdigest()[:16]


def gate_key_path(root: Path) -> Path:
    return root / ".xdd" / ".gate-key"


def load_gate_key(root: Path) -> bytes:
    p = gate_key_path(root)
    if not p.exists():
        raise FileNotFoundError(
            f"{p} no existe — corré `xdd-gate.py init` primero."
        )
    return p.read_bytes()


def sign_payload(key: bytes, phase: str, checksums: dict, approver: str,
                 timestamp: str) -> str:
    """HMAC-SHA256 sobre payload canónico determinista (sorted keys)."""
    payload = json.dumps(
        {
            "phase": phase,
            "checksums": dict(sorted(checksums.items())),
            "approver": approver,
            "timestamp": timestamp,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def cmd_init(root: Path, _args) -> int:
    p = gate_key_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        print(f"[gate] {p} ya existe (no se sobrescribe).")
        return 0
    p.write_bytes(secrets.token_bytes(32))
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    print(f"[gate] {p} creado (256-bit). NO commitearlo (debe estar en .gitignore).")
    return 0


import re

# Placeholders del template que DEBEN estar resueltos en el artefacto final.
_PLACEHOLDER_RE = re.compile(r"\{\{AUTO:[^}]+\}\}|<CONFIGURAR[^>]*>")


def _check_unresolved_placeholders(path: Path, rel: str) -> list[str]:
    """Falla el gate si el README aún contiene {{AUTO:...}} o <CONFIGURAR>.
    Cierra el bug que dejaba pasar docs con datos inventados o sin rellenar."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [f"No se pudo leer {rel}: {e}"]
    hits = _PLACEHOLDER_RE.findall(text)
    if hits:
        sample = ", ".join(sorted(set(hits))[:3])
        return [f"{rel} tiene {len(hits)} placeholder(s) sin resolver: {sample}…"]
    return []


def _run_git(root: Path, args: list[str]) -> str:
    import subprocess
    try:
        out = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10
        )
        return out.stdout
    except (subprocess.SubprocessError, OSError):
        return ""


def _warn_phase_compression(root: Path, phase: str) -> None:
    """M6: avisa si la fase huele a 'pipeline teatro' (sin esfuerzo real)."""
    log = _run_git(root, ["log", "--since=24 hours ago", "--format=%H"])
    commits_24h = len([l for l in log.splitlines() if l.strip()])
    total = _run_git(root, ["rev-list", "--count", "HEAD"]).strip()
    if commits_24h and total.isdigit() and commits_24h == int(total) and int(total) <= len(PHASE_IDS):
        print(
            f"[gate] ⚠ {phase}: todo el historial ({total} commits) cabe en 24h "
            f"con ≤{len(PHASE_IDS)} commits totales. Posible compresión de "
            f"iteraciones (pipeline teatro). Verifica esfuerzo real por fase.",
            file=sys.stderr,
        )


def _load_profile(root: Path) -> dict:
    """Lee xdd.profile.yml sin dependencia dura de PyYAML (parser mínimo de las
    pocas claves que el gate necesita). Si no existe, devuelve {} (defaults)."""
    pf = root / "xdd.profile.yml"
    if not pf.exists():
        return {}
    caps: dict = {}
    in_caps = False
    coverage_min = None
    for raw in pf.read_text(errors="ignore").splitlines():
        line = raw.rstrip()
        if line.startswith("capabilities:"):
            in_caps = True
            continue
        if in_caps:
            if line and not line.startswith((" ", "\t")):
                in_caps = False
            else:
                m = re.match(r"\s+([a-z_]+):\s*(true|false)", line)
                if m:
                    caps[m.group(1)] = m.group(2) == "true"
        m2 = re.match(r"\s*coverage_min:\s*([0-9.]+)", line)
        if m2:
            coverage_min = float(m2.group(1))
    return {"capabilities": caps, "coverage_min": coverage_min}


# Marcadores que delatan un QA_REPORT sin tests reales (el bug Agent Anmax).
_NO_TEST_HINTS = re.compile(r"0\s+tests|sin\s+tests|no\s+tests|0\s+test\b", re.I)
_TEST_EVIDENCE = re.compile(
    r"\btests?\b.*\b(pass|passed|passing|verde|ok|✅|\d+\s*/\s*\d+)\b", re.I
)


def _check_qa_report(path: Path, rel: str, coverage_min: float | None) -> list[str]:
    """M2: QA exige evidencia de tests reales, no solo que el reporte exista."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [f"No se pudo leer {rel}: {e}"]
    errs = []
    if _NO_TEST_HINTS.search(text) or not _TEST_EVIDENCE.search(text):
        errs.append(
            f"{rel}: sin evidencia de tests reales (suite con N>0 y resultados). "
            "QA verde requiere tests, no solo build verde."
        )
    if coverage_min is not None:
        m = re.search(r"cobertura[^0-9]*([0-9]{1,3})\s*%", text, re.I) or re.search(
            r"coverage[^0-9]*([0-9]{1,3})\s*%", text, re.I
        )
        cov = float(m.group(1)) if m else None
        if cov is None:
            errs.append(f"{rel}: no declara cobertura (umbral perfil: {coverage_min}%).")
        elif cov < coverage_min:
            errs.append(
                f"{rel}: cobertura {cov}% < umbral {coverage_min}% del perfil."
            )
    return errs


def _check_build_evidence(root: Path, rel: str) -> list[str]:
    """M3: build exige evidencia de ejecución real, no solo dir existente."""
    ev = root / rel / "run-evidence.txt"
    if not ev.exists() or not ev.read_text(errors="ignore").strip():
        return [
            f"{rel}: falta run-evidence.txt con log de ejecución end-to-end real. "
            "Compilar no es ejecutar."
        ]
    return []


def _validate_phase(root: Path, phase: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if phase not in PHASE_IDS:
        return False, [f"Fase desconocida: {phase}"]
    pdir = root / ".xdd" / phase
    if not pdir.exists():
        return False, [f".xdd/{phase}/ no existe"]

    status_file = pdir / ".status"
    sig_file = pdir / ".signature"
    cks_file = pdir / ".checksums"
    apr_file = pdir / ".approvers"

    if not status_file.exists():
        errors.append(f".xdd/{phase}/.status no existe")
        return False, errors
    status = status_file.read_text().strip()
    if status != Status.APROBADO.value:
        errors.append(f"Fase {phase!r} status={status} (esperado APROBADO)")

    profile = _load_profile(root)
    caps = profile.get("capabilities", {})

    # M8: la fase `docs` solo es obligatoria si el perfil declara end_user_docs.
    # Si la capability está explícitamente en false, `docs` se considera N/A.
    if phase == "docs" and caps.get("end_user_docs") is False:
        return True, []

    for art_rel in PHASE_ARTIFACTS[phase]:
        art_path = root / art_rel
        if not art_path.exists():
            errors.append(f"Artefacto faltante: {art_rel}")
            continue
        # M5: gates verifican CONTENIDO, no solo existencia.
        if phase == "docs" and art_rel.endswith(".md"):
            errors.extend(_check_unresolved_placeholders(art_path, art_rel))
        elif phase == "qa" and art_rel.endswith("QA_REPORT.md"):
            errors.extend(
                _check_qa_report(art_path, art_rel, profile.get("coverage_min"))
            )
        elif phase == "build" and art_rel.endswith("/"):
            errors.extend(_check_build_evidence(root, art_rel))

    if not sig_file.exists() or not cks_file.exists() or not apr_file.exists():
        if status == Status.APROBADO.value:
            errors.append(
                f".signature / .checksums / .approvers faltantes en .xdd/{phase}/"
            )
        return len(errors) == 0, errors

    try:
        stored_cks = json.loads(cks_file.read_text())
    except json.JSONDecodeError:
        errors.append(f".xdd/{phase}/.checksums no es JSON válido")
        return False, errors

    for art_rel, old_hash in stored_cks.items():
        cur = checksum(root / art_rel)
        if cur != old_hash:
            errors.append(
                f"Checksum mismatch en {art_rel}: "
                f"stored={old_hash[:8]}… current={cur[:8]}…"
            )

    apr_lines = [l for l in apr_file.read_text().splitlines() if l.strip()]
    if not apr_lines:
        errors.append(f".xdd/{phase}/.approvers vacío")
        return False, errors
    last_approver, last_ts = apr_lines[-1].split(" | ", 1)

    try:
        key = load_gate_key(root)
    except FileNotFoundError as e:
        errors.append(str(e))
        return False, errors

    expected_sig = sign_payload(key, phase, stored_cks, last_approver, last_ts)
    actual_sig = sig_file.read_text().strip()
    if not hmac.compare_digest(expected_sig, actual_sig):
        errors.append(
            f"Firma HMAC inválida en {phase}. "
            "El gate ha sido alterado o la .gate-key cambió."
        )

    return len(errors) == 0, errors


def cmd_validate(root: Path, args) -> int:
    ok, errs = _validate_phase(root, args.phase)
    if args.json:
        print(json.dumps({"phase": args.phase, "ok": ok, "errors": errs}, indent=2))
    else:
        if ok:
            print(f"[gate] ✓ {args.phase}: APROBADO y firma válida.")
        else:
            print(f"[gate] ✗ {args.phase}: FALLA")
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
    return 0 if ok else 1


def cmd_transition(root: Path, args) -> int:
    src, dst = args.phase, args.to
    if src not in PHASE_IDS or dst not in PHASE_IDS:
        print(f"[gate] Fase desconocida ({src} → {dst})", file=sys.stderr)
        return 2
    if PHASE_IDS.index(dst) != PHASE_IDS.index(src) + 1:
        msg = f"Transición no secuencial: {src} → {dst}"
        if args.json:
            print(json.dumps({"ok": False, "error": msg}))
        else:
            print(f"[gate] ✗ {msg}", file=sys.stderr)
        return 1
    ok, errs = _validate_phase(root, src)
    if args.json:
        print(json.dumps({"from": src, "to": dst, "ok": ok, "errors": errs}, indent=2))
    else:
        if ok:
            print(f"[gate] ✓ {src} → {dst}: transición permitida.")
        else:
            print(f"[gate] ✗ {src} → {dst}: BLOQUEADA")
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
    return 0 if ok else 1


def cmd_approve(root: Path, args) -> int:
    phase = args.phase
    if phase not in PHASE_IDS:
        print(f"[gate] Fase desconocida: {phase}", file=sys.stderr)
        return 2

    pdir = root / ".xdd" / phase
    pdir.mkdir(parents=True, exist_ok=True)

    missing = [a for a in PHASE_ARTIFACTS[phase] if not (root / a).exists()]
    if missing:
        print(f"[gate] ✗ {phase}: no se puede aprobar — artefactos faltantes:",
              file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    approver = args.approver or os.environ.get("XDD_APPROVER", "")
    if not approver:
        print("[gate] ✗ falta aprobador. Pasá --approver NAME o exportá "
              "XDD_APPROVER=...", file=sys.stderr)
        return 2

    # M4: validador externo ≠ generador. El que aprueba no debe ser el mismo que
    # escribió el código de la fase (rompe la auto-aprobación que dejó pasar
    # pipelines teatro). Override explícito sólo para flujos solo-dev.
    allow_self = getattr(args, "allow_self_approve", False) or os.environ.get(
        "XDD_ALLOW_SELF_APPROVE"
    )
    last_author = _run_git(root, ["log", "-1", "--format=%an"])
    if last_author and last_author.strip().lower() == approver.strip().lower():
        if not allow_self:
            print(
                f"[gate] ✗ {phase}: el aprobador ('{approver}') es el mismo autor "
                f"del último commit. Requiere revisor externo. Para flujo solo-dev: "
                f"--allow-self-approve o XDD_ALLOW_SELF_APPROVE=1.",
                file=sys.stderr,
            )
            return 1
        print(f"[gate] ⚠ {phase}: auto-aprobación permitida (override solo-dev).")

    # M6: anti-compresión de iteraciones. Una fase con 0-1 commits o aprobada el
    # mismo instante que la anterior es señal de "pipeline teatro" — warning, no
    # bloqueo (puede ser legítimo en proyectos triviales).
    _warn_phase_compression(root, phase)

    try:
        key = load_gate_key(root)
    except FileNotFoundError as e:
        print(f"[gate] ✗ {e}", file=sys.stderr)
        return 2

    cks = {a: checksum(root / a) for a in PHASE_ARTIFACTS[phase]}
    ts = utcnow_iso()
    sig = sign_payload(key, phase, cks, approver, ts)

    (pdir / ".status").write_text(Status.APROBADO.value + "\n")
    (pdir / ".checksums").write_text(json.dumps(cks, sort_keys=True, indent=2) + "\n")
    (pdir / ".signature").write_text(sig + "\n")
    with (pdir / ".approvers").open("a", encoding="utf-8") as f:
        f.write(f"{approver} | {ts}\n")

    if args.json:
        print(json.dumps({
            "ok": True, "phase": phase, "approver": approver,
            "timestamp": ts, "signature_prefix": sig[:16],
        }, indent=2))
    else:
        print(f"[gate] ✓ {phase}: APROBADO por {approver} ({ts}).")
        print(f"       firma HMAC-SHA256 prefix: {sig[:16]}…")
    return 0


def cmd_status(root: Path, args) -> int:
    result = []
    for phase in PHASE_IDS:
        pdir = root / ".xdd" / phase
        entry = {"phase": phase, "exists": pdir.exists()}
        if pdir.exists():
            sf = pdir / ".status"
            entry["status"] = sf.read_text().strip() if sf.exists() else "MISSING"
            ok, errs = _validate_phase(root, phase)
            entry["valid"] = ok
            if errs:
                entry["errors"] = errs
        result.append(entry)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for e in result:
            mark = "✓" if e.get("valid") else ("⚠" if e.get("exists") else "·")
            print(f"  {mark} {e['phase']:9} {e.get('status', 'NO INICIADA')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xdd-gate",
        description="Gate keeper programático del pipeline X-DD (con firma HMAC-SHA256).",
    )
    p.add_argument("-v", "--version", action="version", version=f"xdd-gate v{__version__}")
    p.add_argument("--project-root", default=".", help="Raíz del proyecto (default: .)")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Genera .xdd/.gate-key si no existe")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help="Valida una fase")
    p_val.add_argument("--phase", required=True, choices=PHASE_IDS)
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    p_tr = sub.add_parser("transition", help="Valida transición entre fases")
    p_tr.add_argument("--phase", required=True, choices=PHASE_IDS, help="Fase actual")
    p_tr.add_argument("--to", required=True, choices=PHASE_IDS, help="Fase destino")
    p_tr.add_argument("--json", action="store_true")
    p_tr.set_defaults(func=cmd_transition)

    p_ap = sub.add_parser("approve", help="Aprueba una fase (firma HMAC)")
    p_ap.add_argument("--phase", required=True, choices=PHASE_IDS)
    p_ap.add_argument("--approver", help="Nombre o XDD_APPROVER env")
    p_ap.add_argument("--allow-self-approve", action="store_true",
                      help="Permite que autor==aprobador (flujo solo-dev)")
    p_ap.add_argument("--json", action="store_true")
    p_ap.set_defaults(func=cmd_approve)

    p_st = sub.add_parser("status", help="Resumen de estado de todas las fases")
    p_st.add_argument("--json", action="store_true")
    p_st.set_defaults(func=cmd_status)

    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.project_root).resolve()
    if not (root / ".xdd").exists() and args.command != "init":
        print(f"[gate] .xdd/ no existe en {root}. Corré `xdd-gate.py init` primero.",
              file=sys.stderr)
        return 2
    return args.func(root, args)


if __name__ == "__main__":
    sys.exit(main())
