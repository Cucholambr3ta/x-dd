"""Tests para scripts/xdd-lessons.py — sistema de lecciones aprendidas."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xdd_lessons", SCRIPTS / "xdd-lessons.py")
xl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xl)


def _args(**kw):
    ns = type("A", (), {})()
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


def _base_lesson(**overrides):
    base = dict(
        titulo="Test de sistema nativo", categoria="PROCESO",
        contexto="Probando el motor", problema="Fallo X", causa="Causa Y",
        leccion="Regla Z siempre aplica", aplica="Todo el proyecto",
        fix_aplicado="", force=False, json=False,
    )
    base.update(overrides)
    return base


@pytest.fixture
def proj(tmp_path):
    return tmp_path


# ── add ──────────────────────────────────────────────────────────────────────

def test_add_creates_lecciones_md(proj):
    rc = xl.cmd_add(_args(project=proj, **_base_lesson()))
    assert rc == 0
    assert (proj / "lecciones.md").exists()


def test_add_leccion_fields_in_file(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    text = (proj / "lecciones.md").read_text(encoding="utf-8")
    assert "Test de sistema nativo" in text
    assert "Regla Z siempre aplica" in text
    assert "PROCESO" in text


def test_add_deduplication_by_similarity(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_add(_args(project=proj, **_base_lesson(
        titulo="Test de sistema nativo duplicado",
        leccion="Regla Z siempre aplica en produccion",  # muy similar
    )))
    assert rc == 0
    out = capsys.readouterr().out
    assert "SKIP" in out


def test_add_force_bypasses_deduplication(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_add(_args(project=proj, **_base_lesson(force=True)))
    assert rc == 0
    lessons = xl.parse_lessons((proj / "lecciones.md").read_text(encoding="utf-8"))
    assert len(lessons) == 2


def test_add_with_fix_aplicado(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson(fix_aplicado="Se aplico el fix X")))
    text = (proj / "lecciones.md").read_text(encoding="utf-8")
    assert "Fix aplicado" in text
    assert "Se aplico el fix X" in text


def test_add_json_output(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson(json=True)))
    out = capsys.readouterr().out
    last_line = [l for l in out.splitlines() if l.strip().startswith("{")][-1]
    data = json.loads(last_line)
    assert data["ok"] is True
    assert data["categoria"] == "PROCESO"


# ── parse_lessons ─────────────────────────────────────────────────────────────

def test_parse_lessons_empty_file(proj):
    (proj / "lecciones.md").write_text("# lecciones\n## Lecciones\n", encoding="utf-8")
    lessons = xl.parse_lessons((proj / "lecciones.md").read_text(encoding="utf-8"))
    assert lessons == []


def test_parse_lessons_extracts_fields(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    text = (proj / "lecciones.md").read_text(encoding="utf-8")
    lessons = xl.parse_lessons(text)
    assert len(lessons) == 1
    assert lessons[0]["categoria"] == "PROCESO"
    assert lessons[0]["leccion"] == "Regla Z siempre aplica"
    assert lessons[0]["titulo"] == "Test de sistema nativo"


def test_parse_lessons_extracts_optional_fields(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson(fix_aplicado="Fix aplicado aqui")))
    text = (proj / "lecciones.md").read_text(encoding="utf-8")
    lessons = xl.parse_lessons(text)
    assert lessons[0]["fix_aplicado"] == "Fix aplicado aqui"


# ── suggest-fix ───────────────────────────────────────────────────────────────

def test_suggest_fix_no_apply(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_suggest_fix(_args(project=proj, titulo=["Test de sistema nativo"],
                                   apply=False, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Leccion" in out or "Mejoras" in out


def test_suggest_fix_apply_saves_to_file(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    xl.cmd_suggest_fix(_args(project=proj, titulo=["Test de sistema nativo"],
                              apply=True, json=False))
    text = (proj / "lecciones.md").read_text(encoding="utf-8")
    assert "Mejoras sugeridas" in text
    assert "Estado mejoras" in text


# ── apply-fix ────────────────────────────────────────────────────────────────

def test_apply_fix_marks_applied(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    xl.cmd_suggest_fix(_args(project=proj, titulo=["Test de sistema nativo"],
                              apply=True, json=False))
    rc = xl.cmd_apply_fix(_args(project=proj, titulo=["Test de sistema nativo"],
                                 fix="Fix implementado en produccion", json=False))
    assert rc == 0
    lessons = xl.parse_lessons((proj / "lecciones.md").read_text(encoding="utf-8"))
    assert lessons[0]["estado_mejoras"] == "aplicado"
    assert "Fix implementado" in lessons[0]["fix_aplicado"]


# ── search ────────────────────────────────────────────────────────────────────

def test_search_finds_relevant(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_search(_args(project=proj, query=["sistema", "nativo"], max=5,
                              categoria=None, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Test de sistema nativo" in out


def test_search_json(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    capsys.readouterr()  # limpiar
    rc = xl.cmd_search(_args(project=proj, query=["Regla"], max=5,
                              categoria=None, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and len(data) >= 1


def test_search_by_categoria(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    xl.cmd_add(_args(project=proj, **_base_lesson(
        titulo="Otra leccion de arquitectura", categoria="ARQUITECTURA",
        leccion="Usar patrones probados", force=True,
    )))
    capsys.readouterr()  # limpiar prints de add
    rc = xl.cmd_search(_args(project=proj, query=["leccion"], max=5,
                              categoria="ARQUITECTURA", json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "ARQUITECTURA" in out
    assert "PROCESO" not in out


def test_search_no_results(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_search(_args(project=proj, query=["supercalifragilistic"], max=5,
                              categoria=None, json=False))
    assert rc == 0


# ── suggest ───────────────────────────────────────────────────────────────────

def test_suggest_outputs_markdown(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_suggest(_args(project=proj, query=["sistema"], max=3))
    assert rc == 0
    out = capsys.readouterr().out
    assert "###" in out or "Leccion" in out


# ── list ─────────────────────────────────────────────────────────────────────

def test_list_all(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_list(_args(project=proj, categoria=None, limit=None,
                            pendientes=False, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Test de sistema nativo" in out


def test_list_pendientes(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    xl.cmd_suggest_fix(_args(project=proj, titulo=["Test de sistema nativo"],
                              apply=True, json=False))
    rc = xl.cmd_list(_args(project=proj, categoria=None, limit=None,
                            pendientes=True, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "pendiente" in out


def test_list_json(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    capsys.readouterr()
    rc = xl.cmd_list(_args(project=proj, categoria=None, limit=None,
                            pendientes=False, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and data[0]["titulo"] == "Test de sistema nativo"


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_json(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    capsys.readouterr()
    rc = xl.cmd_stats(_args(project=proj, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 1
    assert data["by_category"]["PROCESO"] == 1


# ── gc ────────────────────────────────────────────────────────────────────────

def test_gc_removes_exact_duplicates(proj):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    xl.cmd_add(_args(project=proj, **_base_lesson(force=True)))
    lessons_before = xl.parse_lessons((proj / "lecciones.md").read_text(encoding="utf-8"))
    assert len(lessons_before) == 2
    xl.cmd_gc(_args(project=proj, json=False))
    lessons_after = xl.parse_lessons((proj / "lecciones.md").read_text(encoding="utf-8"))
    assert len(lessons_after) == 1


def test_gc_no_duplicates(proj, capsys):
    xl.cmd_add(_args(project=proj, **_base_lesson()))
    rc = xl.cmd_gc(_args(project=proj, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "sin duplicados" in out


# ── bm25 ──────────────────────────────────────────────────────────────────────

def test_bm25_ranks_by_relevance(proj):
    lessons = [
        {"categoria": "PROCESO", "titulo": "Error en manifests", "fecha": "2026-01-01",
         "contexto": "manifests no se actualizaban", "problema": "manifests stale",
         "causa": "no habia checklist", "leccion": "actualizar manifests siempre",
         "aplica": "sprints", "fix_aplicado": "", "mejoras_sugeridas": "", "estado_mejoras": ""},
        {"categoria": "HERRAMIENTAS", "titulo": "Symlinks rechazados", "fecha": "2026-01-02",
         "contexto": "symlinks en IDE", "problema": "IDE no los sigue",
         "causa": "security policy", "leccion": "usar cp real siempre",
         "aplica": "adapters", "fix_aplicado": "", "mejoras_sugeridas": "", "estado_mejoras": ""},
    ]
    results = xl.bm25_search_lessons("manifests checklist", lessons, max_results=2)
    assert results[0][0]["titulo"] == "Error en manifests"


def test_similarity_high_for_duplicates():
    a = "MCP eliminado en adapt.sh Toda eliminacion requiere grep"
    b = "MCP eliminado en adapt.sh Toda eliminacion requiere grep y test"
    assert xl._similarity(a, b) > 0.75


def test_similarity_low_for_different():
    a = "Symlinks rechazados por IDE"
    b = "SQLite tabla research proposals"
    assert xl._similarity(a, b) < 0.3
