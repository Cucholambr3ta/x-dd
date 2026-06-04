"""Tests para xdd-memory.py sprint-close — Inc 5 memoria/lecciones por sprint."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "xdd_memory",
    Path(__file__).parent.parent / "scripts" / "xdd-memory.py",
)
xdd_memory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xdd_memory)


# ── helpers ───────────────────────────────────────────────────────────────────

def run_sprint_close(tmp_path, sprint, **kwargs):
    """Invoca cmd_sprint_close con args mínimos."""
    class Args:
        pass
    a = Args()
    a.project = str(tmp_path)
    a.sprint = sprint
    a.memoria = kwargs.get("memoria", None)
    a.lecciones = kwargs.get("lecciones", None)
    a.force = kwargs.get("force", False)
    a.json = kwargs.get("json", False)
    return xdd_memory.cmd_sprint_close(a)


# ── tests ────────────────────────────────────────────────────────────────────

def test_sprint_close_crea_memoria_file(tmp_path):
    rc = run_sprint_close(tmp_path, sprint=1)
    assert rc == 0
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").exists()


def test_sprint_close_crea_lecciones_file(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    assert (tmp_path / "acuerdos" / "lecciones" / "sprint-01.md").exists()


def test_sprint_close_crea_index(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    idx = tmp_path / "acuerdos" / "lecciones" / "INDEX.md"
    assert idx.exists()
    content = idx.read_text()
    assert "sprint-01" in content


def test_sprint_close_crea_memory_md(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    mem = tmp_path / "acuerdos" / "memoria" / "MEMORY.md"
    assert mem.exists()
    assert "Hechos persistentes" in mem.read_text()


def test_sprint_close_numero_normalizado(tmp_path):
    """Sprint '3' → sprint-03.md, sprint 12 → sprint-12.md."""
    run_sprint_close(tmp_path, sprint="3")
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-03.md").exists()

    run_sprint_close(tmp_path, sprint=12)
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-12.md").exists()


def test_sprint_close_no_sobreescribe_sin_force(tmp_path):
    run_sprint_close(tmp_path, sprint=1, memoria="# Original\n")
    run_sprint_close(tmp_path, sprint=1, memoria="# Nuevo\n")
    content = (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").read_text()
    assert "Original" in content
    assert "Nuevo" not in content


def test_sprint_close_force_sobreescribe(tmp_path):
    run_sprint_close(tmp_path, sprint=1, memoria="# Original\n")
    run_sprint_close(tmp_path, sprint=1, memoria="# Nuevo\n", force=True)
    content = (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").read_text()
    assert "Nuevo" in content


def test_sprint_close_contenido_personalizado(tmp_path):
    mem = "# Sprint 5\n\n## Hitos\n- Implementado auth\n"
    les = "### [ARQUITECTURA] Patron X — 2026-06-04\n**Contexto:** ...\n"
    run_sprint_close(tmp_path, sprint=5, memoria=mem, lecciones=les)
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-05.md").read_text() == mem
    assert (tmp_path / "acuerdos" / "lecciones" / "sprint-05.md").read_text() == les


def test_sprint_close_index_acumula_multiples_sprints(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    run_sprint_close(tmp_path, sprint=2)
    run_sprint_close(tmp_path, sprint=3)
    idx = (tmp_path / "acuerdos" / "lecciones" / "INDEX.md").read_text()
    assert "sprint-01" in idx
    assert "sprint-02" in idx
    assert "sprint-03" in idx


def test_sprint_close_index_no_duplica_entrada(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    run_sprint_close(tmp_path, sprint=1, force=True)
    idx = (tmp_path / "acuerdos" / "lecciones" / "INDEX.md").read_text()
    # Contar lineas de tabla que corresponden al sprint (empieza con "| sprint-01 |")
    table_rows = [l for l in idx.splitlines() if l.startswith("| sprint-01 |")]
    assert len(table_rows) == 1


def test_sprint_close_json_output(tmp_path, capsys):
    class Args:
        project = str(tmp_path)
        sprint = 2
        memoria = None
        lecciones = None
        force = False
        json = True
    xdd_memory.cmd_sprint_close(Args())
    captured = capsys.readouterr()
    # ultima linea es JSON
    lines = [l for l in captured.out.strip().splitlines() if l.startswith("{")]
    assert lines, "No JSON output found"
    data = json.loads(lines[-1])
    assert data["ok"] is True
    assert data["sprint"] == "02"
