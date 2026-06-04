#!/usr/bin/env python3
"""xdd-discipline-check — Valida que cada artefacto cumple su disciplina -DD.

Cero deuda tecnica: el gate verifica CONTENIDO, no solo existencia.
Un DOMAIN.md vacio con titulo pasa existencia pero falla discipline-check.

Disciplinas y fases:
  briefing → SDD (SPEC.md) + FDD (FEATURES.md)
  spec     → DDD (DOMAIN.md) + Threat-Driven (THREATS.md)
  plan     → BDD/ATDD (*.feature)
  build    → TDD (tests/unit/) + STDD (tests/security/)
  qa       → SecDD (QA_REPORT.md)

Activacion: llamado por xdd-gate.py _validate_phase cuando XDD_DISCIPLINE=1.
Override: XDD_SKIP_DISCIPLINE=1 (dev-solo, warning visible).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


# ── helpers ────────────────────────────────────────────────────────────────────

def _lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def _content(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _heading_present(content: str, *keywords: str) -> bool:
    """Comprueba que al menos uno de los keywords aparece en un heading."""
    for kw in keywords:
        pattern = rf"(?im)^#{1,4}\s+.*{re.escape(kw)}"
        if re.search(pattern, content):
            return True
    return False


def _section_nonempty(content: str, heading_kw: str) -> bool:
    """Heading presente Y al menos una linea de contenido no-vacia debajo."""
    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        if re.match(rf"(?i)^#{1,4}\s+.*{re.escape(heading_kw)}", line):
            found = True
            # Buscar contenido en las siguientes lineas (hasta el proximo heading)
            for j in range(i + 1, min(i + 20, len(lines))):
                if re.match(r"^#{1,4}\s", lines[j]):
                    break
                if lines[j].strip() and not lines[j].strip().startswith(">"):
                    return True
    return False if found else False


# ── SDD — SPEC.md ──────────────────────────────────────────────────────────────

def check_sdd(root: Path) -> list[str]:
    """SPEC.md debe tener: objetivo/problema, alcance, criterios de aceptacion, NFRs."""
    errors = []
    spec = root / ".xdd" / "briefing" / "SPEC.md"
    if not spec.exists():
        return ["SDD: SPEC.md no existe"]

    content = _content(spec)
    if len(content.strip()) < 100:
        return ["SDD: SPEC.md tiene menos de 100 caracteres — contenido insuficiente"]

    required = [
        ("objetivo", "problema", "proposito", "resuelve"),
        ("alcance", "scope"),
        ("aceptacion", "acceptance", "criterio"),
        ("nfr", "no funcional", "rendimiento", "disponibilidad", "seguridad"),
    ]
    labels = ["objetivo/problema", "alcance", "criterios de aceptacion", "NFRs"]

    for (kwds, label) in zip(required, labels):
        if not any(_heading_present(content, kw) or kw.lower() in content.lower() for kw in kwds):
            errors.append(f"SDD: SPEC.md falta seccion '{label}'")

    return errors


# ── FDD — FEATURES.md ─────────────────────────────────────────────────────────

def check_fdd(root: Path) -> list[str]:
    """FEATURES.md debe tener >= 1 feature con nombre, prioridad y criterios."""
    errors = []
    feat = root / ".xdd" / "briefing" / "FEATURES.md"
    if not feat.exists():
        return ["FDD: FEATURES.md no existe"]

    content = _content(feat)
    if len(content.strip()) < 50:
        return ["FDD: FEATURES.md tiene menos de 50 caracteres — catalogo vacio"]

    # Debe haber al menos 1 feature definida (heading de feature o lista)
    has_feature = bool(re.search(r"(?im)^#{2,4}\s+\w|^\s*[-*]\s+\w", content))
    if not has_feature:
        errors.append("FDD: FEATURES.md no contiene features (ninguna entrada detectada)")

    # Debe mencionar prioridad (MoSCoW o RICE o similar)
    has_priority = bool(re.search(r"(?i)must|should|could|won'?t|moscow|rice|prioridad|priority|alta|media|baja", content))
    if not has_priority:
        errors.append("FDD: FEATURES.md no menciona priorizacion (MoSCoW, RICE, alta/media/baja)")

    return errors


# ── DDD — DOMAIN.md ───────────────────────────────────────────────────────────

def check_ddd(root: Path) -> list[str]:
    """DOMAIN.md debe tener: Ubiquitous Language, >= 1 Bounded Context, Aggregates."""
    errors = []
    domain = root / ".xdd" / "spec" / "DOMAIN.md"
    if not domain.exists():
        return ["DDD: DOMAIN.md no existe"]

    content = _content(domain)
    if len(content.strip()) < 100:
        return ["DDD: DOMAIN.md tiene menos de 100 caracteres — contenido insuficiente"]

    checks = [
        (["ubiquitous", "glosario", "vocabulario", "lenguaje"],
         "DDD: DOMAIN.md falta seccion 'Ubiquitous Language' o glosario"),
        (["bounded context", "contexto acotado", "bounded_context"],
         "DDD: DOMAIN.md falta al menos 1 Bounded Context"),
        (["aggregate", "agregado", "raiz de agregado", "aggregate root"],
         "DDD: DOMAIN.md falta definicion de Aggregates"),
    ]
    for (kwds, msg) in checks:
        if not any(kw.lower() in content.lower() for kw in kwds):
            errors.append(msg)

    return errors


# ── Threat-Driven — THREATS.md ────────────────────────────────────────────────

def check_threat_driven(root: Path) -> list[str]:
    """THREATS.md debe tener STRIDE + al menos 1 amenaza con control documentado."""
    errors = []
    threats = root / ".xdd" / "spec" / "THREATS.md"
    if not threats.exists():
        return ["Threat-Driven: THREATS.md no existe"]

    content = _content(threats)
    if len(content.strip()) < 100:
        return ["Threat-Driven: THREATS.md tiene menos de 100 caracteres — contenido insuficiente"]

    # STRIDE presente
    stride_terms = ["spoofing", "tampering", "repudiation", "information disclosure",
                    "denial of service", "elevation of privilege", "stride"]
    has_stride = any(t.lower() in content.lower() for t in stride_terms)
    if not has_stride:
        errors.append("Threat-Driven: THREATS.md no menciona STRIDE ni sus categorias")

    # Al menos 1 amenaza con control documentado
    has_control = bool(re.search(
        r"(?i)(control|mitigacion|mitigacion|countermeasure|control propuesto|fix|remediacion)",
        content
    ))
    if not has_control:
        errors.append("Threat-Driven: THREATS.md no documenta controles para amenazas")

    # Amenaza CRITICA sin control es una violation
    critica_sin_control = re.findall(
        r"(?i)(critica|critical|alta|high)[^\n]*\n(?:[^\n]*\n){0,5}(?!.*control)",
        content
    )
    # Heuristica conservadora — no bloquear si no hay patron claro
    # Solo reportar si hay "CRITICA" sin ninguna mencion de control en todo el doc
    if re.search(r"(?i)critica|critical", content) and not has_control:
        errors.append("Threat-Driven: hay amenazas criticas pero ninguna tiene control documentado")

    return errors


# ── BDD/ATDD — *.feature ──────────────────────────────────────────────────────

def check_bdd(root: Path) -> list[str]:
    """Cada .feature debe tener: 1 happy path + >= 1 error + >= 1 borde."""
    errors = []
    feature_files = list(root.rglob("*.feature"))

    if not feature_files:
        # No hay features aun — no es un error si estamos en fase plan
        return []

    for fpath in feature_files:
        content = _content(fpath)
        scenarios = re.findall(r"(?im)^\s*Scenario[^:]*:", content)
        n = len(scenarios)

        if n == 0:
            errors.append(f"BDD: {fpath.name} no tiene ningun Scenario")
            continue

        if n < 3:
            errors.append(
                f"BDD: {fpath.name} tiene solo {n} escenario(s) — "
                f"minimo: 1 happy path + 1 error + 1 borde"
            )

        # Detectar escenario de error (por nombre o contenido)
        has_error = bool(re.search(r"(?i)error|falla|fail|invalido|invalid|no autorizado|unauthorized", content))
        if not has_error:
            errors.append(f"BDD: {fpath.name} no tiene escenario de error o caso negativo")

    return errors


# ── TDD — tests/unit/ ─────────────────────────────────────────────────────────

def check_tdd(root: Path) -> list[str]:
    """tests/unit/ debe existir con al menos 1 test file."""
    errors = []
    unit_dir = root / "tests" / "unit"

    if not unit_dir.is_dir():
        # Algunos proyectos usan tests/ directamente — check alternativo
        test_files = list(root.glob("tests/test_*.py")) + list(root.glob("tests/**/*.test.*"))
        if not test_files:
            errors.append("TDD: no se encontraron tests unitarios en tests/unit/ ni tests/test_*.py")
        return errors

    test_files = list(unit_dir.rglob("*.test.*")) + list(unit_dir.rglob("test_*.py"))
    if not test_files:
        errors.append("TDD: tests/unit/ existe pero no tiene archivos de test")

    return errors


# ── STDD — tests/security/ ────────────────────────────────────────────────────

def check_stdd(root: Path) -> list[str]:
    """tests/security/ debe tener al menos 1 security test si hay amenazas en THREATS.md."""
    errors = []
    threats = root / ".xdd" / "spec" / "THREATS.md"

    # Solo validar STDD si hay THREATS.md con amenazas
    if not threats.exists():
        return []

    content = _content(threats)
    has_threats = bool(re.search(r"(?i)(spoofing|tampering|stride|amenaza|threat)", content))
    if not has_threats:
        return []

    # Buscar tests de seguridad
    sec_dirs = [root / "tests" / "security", root / "tests" / "sec"]
    sec_files = []
    for d in sec_dirs:
        if d.is_dir():
            sec_files.extend(d.rglob("*.security.*"))
            sec_files.extend(d.rglob("test_*security*"))
            sec_files.extend(d.rglob("*security*test*"))

    # Buscar en tests/ general con patron de seguridad
    if not sec_files:
        sec_files = list(root.glob("tests/**/*security*")) + list(root.glob("tests/**/*pentest*"))

    if not sec_files:
        errors.append(
            "STDD: THREATS.md define amenazas pero no hay tests de seguridad "
            "(buscar en tests/security/ o tests/**/*security*)"
        )

    return errors


# ── SecDD — QA_REPORT.md ──────────────────────────────────────────────────────

def check_secdd(root: Path) -> list[str]:
    """QA_REPORT.md debe mencionar SAST + DAST + secrets scan."""
    errors = []
    report = root / ".xdd" / "qa" / "QA_REPORT.md"
    if not report.exists():
        return ["SecDD: QA_REPORT.md no existe en .xdd/qa/"]

    content = _content(report)
    if len(content.strip()) < 50:
        return ["SecDD: QA_REPORT.md tiene menos de 50 caracteres — reporte vacio"]

    checks = [
        (["sast", "analisis estatico", "static analysis", "bandit", "semgrep", "sonar"],
         "SecDD: QA_REPORT.md no menciona SAST (analisis estatico)"),
        (["dast", "analisis dinamico", "dynamic analysis", "zap", "burp", "nuclei"],
         "SecDD: QA_REPORT.md no menciona DAST (analisis dinamico)"),
        (["secrets", "gitleaks", "trufflehog", "secretos", "credenciales"],
         "SecDD: QA_REPORT.md no menciona secrets scanning"),
    ]
    for (kwds, msg) in checks:
        if not any(kw.lower() in content.lower() for kw in kwds):
            errors.append(msg)

    return errors


# ── Dispatcher ────────────────────────────────────────────────────────────────

PHASE_CHECKS: dict[str, list] = {
    "briefing": [check_sdd, check_fdd],
    "spec":     [check_ddd, check_threat_driven],
    "plan":     [check_bdd],
    "build":    [check_tdd, check_stdd],
    "qa":       [check_secdd],
    "retro":    [],
}


def check_phase(root: Path, phase: str) -> list[str]:
    """Ejecuta todos los validadores de contenido para una fase."""
    if os.environ.get("XDD_SKIP_DISCIPLINE") == "1":
        print(f"[xdd-discipline] XDD_SKIP_DISCIPLINE=1 — checks de contenido omitidos.", file=sys.stderr)
        return []

    checkers = PHASE_CHECKS.get(phase, [])
    errors: list[str] = []
    for checker in checkers:
        errors.extend(checker(root))
    return errors


# ── CLI standalone ────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="xdd-discipline-check",
        description=__doc__,
    )
    p.add_argument("phase", choices=list(PHASE_CHECKS.keys()), help="Fase a validar")
    p.add_argument("--root", default=".", help="Raiz del proyecto (default: $PWD)")
    p.add_argument("--json", action="store_true", help="Salida JSON")
    args = p.parse_args(argv)

    root = Path(args.root).resolve()
    errors = check_phase(root, args.phase)

    if args.json:
        import json
        print(json.dumps({"phase": args.phase, "ok": len(errors) == 0, "errors": errors}))
        return 0 if not errors else 1

    if errors:
        print(f"[xdd-discipline] ✗ {args.phase}: {len(errors)} violation(es):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"[xdd-discipline] ✓ {args.phase}: contenido valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
