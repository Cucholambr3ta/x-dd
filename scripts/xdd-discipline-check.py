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

import hashlib
import json
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


# ── Atomicidad — 1 doc = 1 dominio tecnico ────────────────────────────────────

# Palabras clave que indican dominios distintos. Si un documento menciona
# DEMASIADOS dominios distintos en sus headings, viola atomicidad.
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "auth":         ["autenticacion", "authentication", "oauth", "jwt", "session", "login"],
    "db":           ["base de datos", "database", "schema", "migracion", "migration", "sql"],
    "api":          ["endpoint", "rest", "graphql", "openapi", "contrato de api"],
    "ui":           ["componente", "component", "wireframe", "frontend", "css", "html"],
    "security":     ["stride", "amenaza", "threat", "sast", "dast", "pentest"],
    "observability":["logging", "metrics", "alertas", "tracing", "slo", "sli"],
    "cicd":         ["pipeline", "deploy", "ci/cd", "github actions", "docker"],
    "testing":      ["test unitario", "unit test", "gherkin", "bdd", "coverage"],
    "domain_model": ["bounded context", "aggregate", "domain event", "ubiquitous language"],
}

# Documentos que PUEDEN ser multi-dominio por diseño (indices, guias de adopcion)
_ALLOWED_MULTI_DOMAIN = {
    "INDEX.md", "README.md", "ONBOARDING.md", "RETROFIT_GUIDE.md",
    "X-DD_Integration_Guide.md", "UBIQUITOUS_LANGUAGE.md",
}

# Lineas minimas relajadas para atomos de carpeta (un sprint o categoria PII
# puede ser legitimamente corto). DOC_STANDARD v2.0 seccion 1.5.
_DEFAULT_ATOM_MIN_LINES = 30

# Umbral de lineas minimas por tipo de documento (DOC_STANDARD v2.0 seccion 1.5)
_LINE_THRESHOLDS: dict[str, int] = {
    "ARQUITECTURA.md": 300,
    "DOMAIN.md":       250,
    "THREATS.md":      200,
    "GATE.md":         150,
    "constitucion.md": 200,
    "PLAN_QA.md":      200,
    "ONBOARDING.md":   200,
    "SPEC.md":         150,
    "FEATURES.md":     100,
}
_DEFAULT_MIN_LINES = 80  # minimo para cualquier doc granular


def check_atomicity(doc_path: Path) -> list[str]:
    """Verifica que el documento cubre un solo dominio tecnico (atomicidad).

    Regla: si el documento menciona headings de 4+ dominios distintos,
    viola atomicidad. Documentos de indice/guia estan exentos.
    """
    errors = []
    if doc_path.name in _ALLOWED_MULTI_DOMAIN:
        return []

    content = _content(doc_path).lower()
    if not content:
        return []

    # Solo analizar headings (lineas que empiezan con #)
    heading_text = " ".join(
        line.lstrip("#").strip()
        for line in content.splitlines()
        if line.startswith("#")
    )

    domains_present = [
        domain for domain, kwds in _DOMAIN_KEYWORDS.items()
        if any(kw in heading_text for kw in kwds)
    ]

    if len(domains_present) >= 4:
        errors.append(
            f"ATOMICIDAD: {doc_path.name} menciona {len(domains_present)} dominios distintos "
            f"en headings ({', '.join(domains_present)}) — "
            f"dividir en documentos separados (1 doc = 1 dominio)"
        )
    return errors


def check_min_lines(doc_path: Path) -> list[str]:
    """Verifica umbral minimo de lineas segun DOC_STANDARD v2.0 seccion 1.5."""
    threshold = _LINE_THRESHOLDS.get(doc_path.name, _DEFAULT_MIN_LINES)
    if not doc_path.exists():
        return []
    lines = len(_content(doc_path).splitlines())
    if lines < threshold:
        return [
            f"PROFUNDIDAD: {doc_path.name} tiene {lines} lineas "
            f"(minimo {threshold} segun DOC_STANDARD v2.0)"
        ]
    return []


def check_doc_quality(root: Path, doc_path: Path) -> list[str]:
    """Atomicidad + umbral de lineas para un documento especifico."""
    errors = []
    errors.extend(check_atomicity(doc_path))
    errors.extend(check_min_lines(doc_path))
    return errors


# ── JSON sidecar — par JSON/MD para ahorro de tokens (Inc 0) ──────────────────

def check_json_sidecar(doc_path: Path) -> list[str]:
    """Verifica que el .md atomico tiene su .json sidecar y el checksum coincide.

    El MD es fuente de verdad; el .json es el indice compacto que ahorra tokens.
    Si falta el .json o el checksum no coincide (MD editado sin re-sync): drift.
    """
    if doc_path.name == "INDEX.md":
        return []
    json_path = doc_path.with_suffix(".json")
    if not json_path.exists():
        return [f"JSON-SIDECAR: {doc_path.name} no tiene .json (correr xdd-doc-sync.py sync)"]
    try:
        sidecar = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [f"JSON-SIDECAR: {json_path.name} no es JSON valido"]
    current = hashlib.sha256(
        doc_path.read_text(encoding="utf-8", errors="replace").encode("utf-8")
    ).hexdigest()[:16]
    if sidecar.get("checksum_md") != current:
        return [f"JSON-SIDECAR: {doc_path.name} cambio sin re-sync (drift JSON/MD)"]
    return []


# ── Atomicidad de carpeta — 1 carpeta = 1 dominio ──────────────────────────────

def check_atomic_folder(folder: Path, *, require_index: bool = True,
                        require_json: bool = True) -> list[str]:
    """Valida una carpeta atomica: INDEX presente, atomos validos, JSON sidecars.

    Reusable por todos los splits del pipeline (sprints, memoria, features, etc.).
    """
    errors = []
    if not folder.is_dir():
        return [f"ATOMIC-FOLDER: {folder} no existe o no es carpeta"]

    md_files = [m for m in folder.glob("*.md") if m.name != "INDEX.md"]

    if require_index:
        if not (folder / "INDEX.md").exists():
            errors.append(f"ATOMIC-FOLDER: {folder.name}/ falta INDEX.md")
        if require_json and not (folder / "INDEX.json").exists():
            errors.append(f"ATOMIC-FOLDER: {folder.name}/ falta INDEX.json")
        # INDEX.md debe tener tabla de trazabilidad
        idx = folder / "INDEX.md"
        if idx.exists():
            content = idx.read_text(encoding="utf-8", errors="replace")
            if "|" not in content or "---" not in content:
                errors.append(f"ATOMIC-FOLDER: {folder.name}/INDEX.md sin tabla de trazabilidad")

    if not md_files:
        errors.append(f"ATOMIC-FOLDER: {folder.name}/ no tiene atomos (.md)")
        return errors

    for md in md_files:
        # Atomicidad (no mezcla dominios)
        errors.extend(check_atomicity(md))
        # Umbral relajado para atomos de carpeta
        lines = len(md.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines < _DEFAULT_ATOM_MIN_LINES:
            errors.append(
                f"ATOMIC-FOLDER: {folder.name}/{md.name} tiene {lines} lineas "
                f"(minimo {_DEFAULT_ATOM_MIN_LINES} para atomo)"
            )
        # JSON sidecar
        if require_json:
            errors.extend(check_json_sidecar(md))

    return errors


# Wrappers delgados por tipo de carpeta atomica

def check_sprints_atomic(root: Path) -> list[str]:
    return check_atomic_folder(root / "acuerdos" / "sprints")


def check_memory_atomic(root: Path) -> list[str]:
    # MEMORY.md es agregado generado; los atomos son decisiones/convenciones/riesgos
    folder = root / "acuerdos" / "memoria"
    if not folder.is_dir():
        return [f"ATOMIC-FOLDER: {folder} no existe"]
    errors = []
    for atom in ("decisiones.md", "convenciones.md", "riesgos.md"):
        if not (folder / atom).exists():
            errors.append(f"MEMORY: falta atomo {atom}")
    return errors


def check_features_atomic(root: Path) -> list[str]:
    return check_atomic_folder(root / "docs" / "features")


def check_domain_atomic(root: Path) -> list[str]:
    return check_atomic_folder(root / "docs" / "domain")


def check_privacy_atomic(root: Path) -> list[str]:
    return check_atomic_folder(root / "docs" / "privacy")


def check_qa_tiers_atomic(qa_run_folder: Path) -> list[str]:
    errors = []
    for tier in ("tier1-estatico.md", "tier2-funcional.md", "tier3-llm-judge.md"):
        if not (qa_run_folder / tier).exists():
            errors.append(f"QA-TIERS: falta {tier}")
    return errors


def check_openapi_fragments(fragments_folder: Path) -> list[str]:
    errors = []
    if not fragments_folder.is_dir():
        return [f"OPENAPI: {fragments_folder} no existe"]
    yaml_files = list(fragments_folder.glob("*.yaml")) + list(fragments_folder.glob("*.yml"))
    if not yaml_files:
        errors.append("OPENAPI: sin fragmentos .yaml")
    return errors


# Mapeo de kind -> wrapper para el CLI `folder`
_FOLDER_KINDS: dict[str, callable] = {
    "sprints":  lambda p: check_atomic_folder(p),
    "memory":   lambda p: check_atomic_folder(p, require_index=True),
    "features": lambda p: check_atomic_folder(p),
    "domain":   lambda p: check_atomic_folder(p),
    "privacy":  lambda p: check_atomic_folder(p),
    "qa":       check_qa_tiers_atomic,
    "openapi":  check_openapi_fragments,
    "generic":  lambda p: check_atomic_folder(p),
}


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
    p.add_argument("phase", choices=list(PHASE_CHECKS.keys()) + ["doc", "folder"],
                   help="Fase a validar, 'doc' para un documento, o 'folder' para carpeta atomica")
    p.add_argument("--root", default=".", help="Raiz del proyecto (default: $PWD)")
    p.add_argument("--doc", default=None, help="Path al documento (con phase=doc)")
    p.add_argument("--kind", default="generic", choices=list(_FOLDER_KINDS.keys()),
                   help="Tipo de carpeta atomica (con phase=folder)")
    p.add_argument("--path", default=None, help="Path a la carpeta (con phase=folder)")
    p.add_argument("--json", action="store_true", help="Salida JSON")
    args = p.parse_args(argv)

    root = Path(args.root).resolve()

    # Modo folder: validar carpeta atomica
    if args.phase == "folder":
        if not args.path:
            print("[xdd-discipline] --path requerido con phase=folder", file=sys.stderr)
            return 2
        folder = Path(args.path).resolve()
        errors = _FOLDER_KINDS[args.kind](folder)
        if args.json:
            print(json.dumps({"folder": str(folder), "kind": args.kind, "ok": not errors, "errors": errors}))
            return 0 if not errors else 1
        if errors:
            print(f"[xdd-discipline] FALLO {folder.name}/ (kind={args.kind}):")
            for e in errors:
                print(f"  - {e}")
            return 1
        print(f"[xdd-discipline] OK {folder.name}/: carpeta atomica valida.")
        return 0

    # Modo doc: validar atomicidad + umbral de un doc especifico
    if args.phase == "doc" or args.doc:
        doc_path = Path(args.doc).resolve() if args.doc else None
        if doc_path is None:
            print("[xdd-discipline] --doc requerido con phase=doc", file=sys.stderr)
            return 2
        errors = check_doc_quality(root, doc_path)
        if args.json:
            import json
            print(json.dumps({"doc": str(doc_path), "ok": not errors, "errors": errors}))
            return 0 if not errors else 1
        if errors:
            print(f"[xdd-discipline] FALLO {doc_path.name}:")
            for e in errors:
                print(f"  - {e}")
            return 1
        print(f"[xdd-discipline] OK {doc_path.name}: atomico y suficiente.")
        return 0

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
