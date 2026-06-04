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
