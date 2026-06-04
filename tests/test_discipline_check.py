"""Tests para xdd-discipline-check.py — Inc 9 (gate valida contenido por disciplina).

Regla: 2 tests por disciplina — positivo (pasa) + negativo (falla).
[[xdd-content-checks-fragile]]: un validador sin caso negativo no detecta nada.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "xdd_discipline_check",
    Path(__file__).parent.parent / "scripts" / "xdd-discipline-check.py",
)
xdd_dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xdd_dc)


# ── fixtures helpers ──────────────────────────────────────────────────────────

def make_spec(tmp_path, content):
    p = tmp_path / ".xdd" / "briefing" / "SPEC.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


def make_features(tmp_path, content):
    p = tmp_path / ".xdd" / "briefing" / "FEATURES.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


def make_domain(tmp_path, content):
    p = tmp_path / ".xdd" / "spec" / "DOMAIN.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


def make_threats(tmp_path, content):
    p = tmp_path / ".xdd" / "spec" / "THREATS.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


def make_feature_file(tmp_path, content, name="login.feature"):
    p = tmp_path / "tests" / "features" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


def make_qa_report(tmp_path, content):
    p = tmp_path / ".xdd" / "qa" / "QA_REPORT.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return tmp_path


# ── SDD ───────────────────────────────────────────────────────────────────────

def test_sdd_pasa_spec_completa(tmp_path):
    content = """# SPEC

## Objetivo
Resolver el problema de gestion de proyectos.

## Alcance
Incluye modulo de usuarios y tareas.

## Criterios de aceptacion
- El usuario puede crear proyectos
- El usuario puede asignar tareas

## NFR
- Disponibilidad 99.9%
- Latencia < 200ms
"""
    make_spec(tmp_path, content)
    errors = xdd_dc.check_sdd(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_sdd_falla_spec_sin_criterios(tmp_path):
    content = """# SPEC

## Objetivo
Un sistema de gestion de tareas para equipos distribuidos que necesitan coordinar trabajo.

## Alcance
Incluye modulo de usuarios, proyectos y reportes de actividad del equipo.

## Arquitectura
Monolito con separacion de capas.
"""
    make_spec(tmp_path, content)
    errors = xdd_dc.check_sdd(tmp_path)
    # Debe fallar por falta de criterios de aceptacion y NFRs
    assert errors, "Se esperaban errores por falta de criterios/NFRs"
    assert any("aceptacion" in e.lower() or "criterio" in e.lower() or "nfr" in e.lower() for e in errors)


def test_sdd_falla_spec_vacia(tmp_path):
    make_spec(tmp_path, "# SPEC\n\nTodo pendiente.\n")
    errors = xdd_dc.check_sdd(tmp_path)
    assert errors  # cualquier error — contenido insuficiente


# ── FDD ───────────────────────────────────────────────────────────────────────

def test_fdd_pasa_features_con_prioridad(tmp_path):
    content = """# FEATURES

## F-01: Autenticacion de usuarios
**Prioridad:** Must Have (MoSCoW)
**Criterios:** El usuario puede iniciar sesion con email y password.

## F-02: Dashboard principal
**Prioridad:** Should Have
**Criterios:** Vista general del proyecto.
"""
    make_features(tmp_path, content)
    errors = xdd_dc.check_fdd(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_fdd_falla_features_sin_priorizacion(tmp_path):
    content = """# FEATURES

## F-01: Autenticacion
Implementar login.

## F-02: Dashboard
Ver proyectos.
"""
    make_features(tmp_path, content)
    errors = xdd_dc.check_fdd(tmp_path)
    assert any("prioriza" in e.lower() for e in errors)


# ── DDD ───────────────────────────────────────────────────────────────────────

def test_ddd_pasa_domain_completo(tmp_path):
    content = """# DOMAIN

## Ubiquitous Language
- **Proyecto:** Unidad de trabajo agrupada por objetivo.
- **Tarea:** Item atomico de trabajo dentro de un proyecto.

## Bounded Contexts
### Gestion de Proyectos
Responsable de crear, modificar y archivar proyectos.

## Context Map
- Gestion de Proyectos ↔ Autenticacion: ACL

## Core Aggregates
### Proyecto (Aggregate Root)
- id, nombre, estado, fechaCreacion
"""
    make_domain(tmp_path, content)
    errors = xdd_dc.check_ddd(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_ddd_falla_domain_sin_ubiquitous_language(tmp_path):
    content = """# DOMAIN

## Arquitectura
Monolito con modulos separados en capas bien definidas para mantener separacion de responsabilidades.

## Entidades principales
- Usuario: persona que usa el sistema
- Proyecto: agrupacion de tareas

## Bounded Contexts
### Gestion de Proyectos
Responsable de crear y gestionar proyectos del equipo.

## Aggregates
- Proyecto (root), Tarea (root)
"""
    make_domain(tmp_path, content)
    errors = xdd_dc.check_ddd(tmp_path)
    # Debe fallar por falta de Ubiquitous Language / glosario
    assert errors, "Se esperaban errores por falta de Ubiquitous Language"
    assert any("ubiquitous" in e.lower() or "glosario" in e.lower() or "vocabulario" in e.lower() for e in errors)


# ── Threat-Driven ─────────────────────────────────────────────────────────────

def test_threat_driven_pasa_threats_completo(tmp_path):
    content = """# THREATS

## Modelo de amenazas STRIDE

### Spoofing — Suplantacion de identidad
**Superficie:** Endpoint /login
**Probabilidad:** Alta
**Control propuesto:** MFA obligatorio + rate limiting

### Tampering — Manipulacion de datos
**Superficie:** API PUT /proyectos/{id}
**Control:** Validacion de ownership en middleware

### Elevation of Privilege
**Superficie:** Endpoint admin
**Control:** RBAC con roles definidos en DOMAIN.md
"""
    make_threats(tmp_path, content)
    errors = xdd_dc.check_threat_driven(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_threat_driven_falla_sin_stride(tmp_path):
    content = """# THREATS

## Riesgos generales

- El sistema puede ser hackeado.
- Posibles problemas de performance.
"""
    make_threats(tmp_path, content)
    errors = xdd_dc.check_threat_driven(tmp_path)
    assert any("stride" in e.lower() for e in errors)


def test_threat_driven_falla_sin_controles(tmp_path):
    content = """# THREATS

## STRIDE

### Spoofing
El atacante suplanta identidad del usuario.
Probabilidad: Alta. Impacto: Critico.

### Tampering
Modificacion de datos en transito.
"""
    make_threats(tmp_path, content)
    errors = xdd_dc.check_threat_driven(tmp_path)
    assert any("control" in e.lower() for e in errors)


# ── BDD ───────────────────────────────────────────────────────────────────────

def test_bdd_pasa_feature_con_escenarios_completos(tmp_path):
    content = """Feature: Login de usuarios
  Como usuario registrado
  Quiero iniciar sesion
  Para acceder al sistema

  Scenario: Happy path — login exitoso
    Given el usuario tiene credenciales validas
    When ingresa email y password correctos
    Then accede al dashboard

  Scenario: Error — credenciales invalidas
    Given el usuario ingresa una password incorrecta
    When intenta iniciar sesion
    Then ve mensaje de error

  Scenario: Borde — cuenta bloqueada tras 5 intentos fallidos
    Given el usuario fallo 5 veces
    When intenta nuevamente
    Then la cuenta queda bloqueada por 15 minutos
"""
    make_feature_file(tmp_path, content)
    errors = xdd_dc.check_bdd(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_bdd_falla_feature_solo_happy_path(tmp_path):
    content = """Feature: Login
  Scenario: Login exitoso
    Given credenciales validas
    When hace login
    Then accede
"""
    make_feature_file(tmp_path, content)
    errors = xdd_dc.check_bdd(tmp_path)
    assert errors  # solo 1 escenario — falta error y borde


def test_bdd_pasa_sin_feature_files(tmp_path):
    # Sin .feature files no aplica (proyecto sin BDD aun)
    errors = xdd_dc.check_bdd(tmp_path)
    assert errors == []


# ── TDD ───────────────────────────────────────────────────────────────────────

def test_tdd_pasa_con_tests_unitarios(tmp_path):
    test_file = tmp_path / "tests" / "unit" / "test_auth.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_login(): assert True")
    errors = xdd_dc.check_tdd(tmp_path)
    assert errors == []


def test_tdd_falla_sin_tests(tmp_path):
    errors = xdd_dc.check_tdd(tmp_path)
    assert errors  # sin tests/unit/ ni tests/test_*.py


def test_tdd_pasa_con_tests_en_raiz_tests(tmp_path):
    test_file = tmp_path / "tests" / "test_models.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_x(): pass")
    errors = xdd_dc.check_tdd(tmp_path)
    assert errors == []


# ── STDD ──────────────────────────────────────────────────────────────────────

def test_stdd_pasa_con_security_tests(tmp_path):
    make_threats(tmp_path, "# THREATS\n\n## STRIDE\n\n### Spoofing\nControl: rate limiting\n")
    sec_test = tmp_path / "tests" / "security" / "test_auth_security.py"
    sec_test.parent.mkdir(parents=True, exist_ok=True)
    sec_test.write_text("def test_rate_limit(): assert True")
    errors = xdd_dc.check_stdd(tmp_path)
    assert errors == []


def test_stdd_falla_amenazas_sin_tests(tmp_path):
    make_threats(tmp_path, "# THREATS\n\n## STRIDE\n\n### Spoofing\nProblema de suplantacion.\nControl: autenticacion fuerte.\n")
    errors = xdd_dc.check_stdd(tmp_path)
    assert any("stdd" in e.lower() or "security" in e.lower() for e in errors)


def test_stdd_skip_sin_threats(tmp_path):
    # Sin THREATS.md no aplica STDD
    errors = xdd_dc.check_stdd(tmp_path)
    assert errors == []


# ── SecDD ─────────────────────────────────────────────────────────────────────

def test_secdd_pasa_qa_report_completo(tmp_path):
    content = """# QA Report

## SAST — Analisis Estatico
Herramienta: Semgrep. Resultado: 0 criticos.

## DAST — Analisis Dinamico
Herramienta: OWASP ZAP. Resultado: 0 high.

## Secrets Scanning
Herramienta: Gitleaks. Resultado: limpio.
"""
    make_qa_report(tmp_path, content)
    errors = xdd_dc.check_secdd(tmp_path)
    assert errors == [], f"Errores inesperados: {errors}"


def test_secdd_falla_qa_sin_dast(tmp_path):
    content = """# QA Report

## SAST
Bandit: 0 issues.

## Secrets
Gitleaks: limpio.
"""
    make_qa_report(tmp_path, content)
    errors = xdd_dc.check_secdd(tmp_path)
    assert any("dast" in e.lower() for e in errors)


# ── XDD_SKIP_DISCIPLINE override ──────────────────────────────────────────────

def test_skip_discipline_omite_todos_los_checks(tmp_path, monkeypatch):
    monkeypatch.setenv("XDD_SKIP_DISCIPLINE", "1")
    # Spec vacia — normalmente fallaria
    make_spec(tmp_path, "# vacio")
    errors = xdd_dc.check_phase(tmp_path, "briefing")
    assert errors == []


def test_discipline_activo_detecta_violations(tmp_path, monkeypatch):
    monkeypatch.delenv("XDD_SKIP_DISCIPLINE", raising=False)
    make_spec(tmp_path, "# vacio")
    errors = xdd_dc.check_phase(tmp_path, "briefing")
    assert errors  # debe detectar spec incompleta


# ── check_phase dispatcher ────────────────────────────────────────────────────

def test_check_phase_briefing_corre_sdd_y_fdd(tmp_path):
    # Ni SPEC ni FEATURES — ambos checkers deben reportar
    errors = xdd_dc.check_phase(tmp_path, "briefing")
    has_sdd = any("SDD" in e or "SPEC" in e for e in errors)
    has_fdd = any("FDD" in e or "FEATURES" in e for e in errors)
    assert has_sdd and has_fdd


def test_check_phase_retro_sin_checks(tmp_path):
    # retro no tiene validadores de disciplina
    errors = xdd_dc.check_phase(tmp_path, "retro")
    assert errors == []


# ── Atomicidad ────────────────────────────────────────────────────────────────

def test_atomicidad_doc_con_un_dominio_pasa(tmp_path):
    """Doc que cubre solo autenticacion: atomico."""
    doc = tmp_path / "AUTH.md"
    doc.write_text(
        "# Autenticacion\n\n## OAuth\n\nFlujo OAuth 2.0.\n\n"
        "## JWT\n\nTokens de sesion.\n\n## Login\n\nEndpoint de autenticacion.\n"
    )
    errors = xdd_dc.check_atomicity(doc)
    assert errors == []


def test_atomicidad_doc_multi_dominio_falla(tmp_path):
    """Doc que mezcla 4+ dominios en headings: viola atomicidad."""
    doc = tmp_path / "GUIDE.md"
    doc.write_text(
        "# Guia\n\n## Autenticacion y OAuth\n\n## Base de datos y migracion\n\n"
        "## Pipeline CI/CD y deploy\n\n## STRIDE y threat modeling\n\n"
        "## Logging y metrics\n\n## Componentes frontend\n"
    )
    errors = xdd_dc.check_atomicity(doc)
    assert errors
    assert "ATOMICIDAD" in errors[0]


def test_atomicidad_index_exento(tmp_path):
    """INDEX.md puede ser multi-dominio por diseno."""
    doc = tmp_path / "INDEX.md"
    doc.write_text(
        "# INDEX\n\n## Autenticacion\n\n## Base de datos\n\n"
        "## CI/CD\n\n## Threats\n\n## Logging\n\n## Frontend\n"
    )
    errors = xdd_dc.check_atomicity(doc)
    assert errors == []


# ── Umbral de lineas ──────────────────────────────────────────────────────────

def test_min_lines_sobre_umbral_pasa(tmp_path):
    """Documento con suficientes lineas pasa."""
    doc = tmp_path / "SPEC.md"
    doc.write_text("\n".join(f"linea {i}" for i in range(200)))
    errors = xdd_dc.check_min_lines(doc)
    assert errors == []


def test_min_lines_bajo_umbral_falla(tmp_path):
    """SPEC.md con menos de 150 lineas falla (umbral definido)."""
    doc = tmp_path / "SPEC.md"
    doc.write_text("\n".join(f"linea {i}" for i in range(50)))
    errors = xdd_dc.check_min_lines(doc)
    assert errors
    assert "PROFUNDIDAD" in errors[0]


def test_min_lines_doc_generico_umbral_80(tmp_path):
    """Doc sin umbral especifico usa default 80 lineas."""
    doc = tmp_path / "MI-DOMINIO.md"
    doc.write_text("\n".join(f"linea {i}" for i in range(30)))
    errors = xdd_dc.check_min_lines(doc)
    assert errors
    assert "80" in errors[0]


def test_doc_quality_atomico_y_suficiente(tmp_path):
    """check_doc_quality: doc atomico y sobre umbral = sin errores."""
    doc = tmp_path / "AUTH.md"
    doc.write_text(
        "# Autenticacion\n\n## Login\n\n"
        + "\n".join(f"Contenido linea {i}" for i in range(100))
    )
    errors = xdd_dc.check_doc_quality(tmp_path, doc)
    assert errors == []


# ── JSON sidecar + atomic folder (Inc 0/1) ────────────────────────────────────

import json as _json
import hashlib as _hashlib
import importlib.util as _ilu

_ds_spec = _ilu.spec_from_file_location(
    "xdd_doc_sync", Path(__file__).parent.parent / "scripts" / "xdd-doc-sync.py"
)
_doc_sync = _ilu.module_from_spec(_ds_spec)
_ds_spec.loader.exec_module(_doc_sync)


def _atom(folder, name, lines=40, dominio_kw="autenticacion"):
    folder.mkdir(parents=True, exist_ok=True)
    doc = folder / f"{name}.md"
    body = "\n".join(f"Linea {i} sobre {dominio_kw}." for i in range(lines))
    doc.write_text(f"# {name}\n\n> Cubre {name}.\n\n## Detalle\n\n{body}\n")
    return doc


def _make_index(folder):
    (folder / "INDEX.md").write_text(
        "# INDEX\n\n| Doc | Resumen |\n|-----|--------|\n| a.md | x |\n"
    )


def test_json_sidecar_falta_json(tmp_path):
    doc = _atom(tmp_path, "esquemas")
    errors = xdd_dc.check_json_sidecar(doc)
    assert errors
    assert "JSON-SIDECAR" in errors[0]


def test_json_sidecar_ok(tmp_path):
    doc = _atom(tmp_path, "esquemas")
    _doc_sync.sync_doc(doc)
    assert xdd_dc.check_json_sidecar(doc) == []


def test_json_sidecar_detecta_drift(tmp_path):
    doc = _atom(tmp_path, "esquemas")
    _doc_sync.sync_doc(doc)
    doc.write_text(doc.read_text() + "\n## Extra\n\nNuevo.\n")  # cambio sin re-sync
    errors = xdd_dc.check_json_sidecar(doc)
    assert errors
    assert "drift" in errors[0].lower()


def test_atomic_folder_ok(tmp_path):
    folder = tmp_path / "sprints"
    folder.mkdir(parents=True)
    a = _atom(folder, "sprint-01")
    _doc_sync.sync_doc(a)
    _make_index(folder)
    _doc_sync.sync_folder(folder)  # genera INDEX.json
    errors = xdd_dc.check_atomic_folder(folder)
    assert errors == [], f"Errores inesperados: {errors}"


def test_atomic_folder_falla_sin_index(tmp_path):
    folder = tmp_path / "sprints"
    a = _atom(folder, "sprint-01")
    _doc_sync.sync_doc(a)
    errors = xdd_dc.check_atomic_folder(folder)
    assert any("INDEX" in e for e in errors)


def test_atomic_folder_falla_sin_json(tmp_path):
    folder = tmp_path / "sprints"
    folder.mkdir(parents=True)
    _atom(folder, "sprint-01")  # sin sync → sin .json
    _make_index(folder)
    errors = xdd_dc.check_atomic_folder(folder)
    assert any("JSON-SIDECAR" in e for e in errors)


def test_atomic_folder_falla_atomo_corto(tmp_path):
    folder = tmp_path / "sprints"
    folder.mkdir(parents=True)
    a = _atom(folder, "sprint-01", lines=5)  # < 30 lineas
    _doc_sync.sync_doc(a)
    _make_index(folder)
    _doc_sync.sync_folder(folder)
    errors = xdd_dc.check_atomic_folder(folder)
    assert any("minimo" in e.lower() for e in errors)


def test_folder_kinds_dispatch(tmp_path):
    folder = tmp_path / "docs" / "features"
    folder.mkdir(parents=True)
    a = _atom(folder, "login")
    _doc_sync.sync_doc(a)
    _make_index(folder)
    _doc_sync.sync_folder(folder)
    errors = xdd_dc.check_features_atomic(tmp_path)
    assert errors == []
