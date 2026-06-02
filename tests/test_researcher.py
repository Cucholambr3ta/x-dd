"""Tests para scripts/xdd-researcher.py (investigacion autonoma)."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xdd_researcher", SCRIPTS / "xdd-researcher.py")
xr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xr)


def _args(**kw):
    ns = type("A", (), {})()
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "state.db"


@pytest.fixture
def out_path(tmp_path):
    return tmp_path / "RESEARCH.md"


# ---------- discover (offline, sin red) ----------

def test_discover_offline_is_deterministic():
    a = xr.discover_offline("system", None)
    b = xr.discover_offline("system", None)
    assert a == b
    assert all("title" in c for c in a)


def test_discover_offline_filters_by_scope():
    sys_only = xr.discover_offline("system", None)
    assert all(c.get("scope", "system") == "system" for c in sys_only)


def test_discover_offline_ranks_by_impact():
    items = xr.discover_offline("system", None)
    scores = [c["impact_score"] for c in items]
    assert scores == sorted(scores, reverse=True)


# ---------- run ----------

def test_run_generates_report_and_persists(db_path, out_path):
    rc = xr.cmd_run(_args(scope="system", topic=None, out=out_path,
                          db=db_path, json=False))
    assert rc == 0
    assert out_path.exists()
    # persistido en SQLite
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT id, status FROM research_proposals").fetchall()
    conn.close()
    assert len(rows) >= 1
    assert all(r[1] == "proposed" for r in rows)


def test_report_has_no_emojis(db_path, out_path):
    xr.cmd_run(_args(scope="system", topic=None, out=out_path, db=db_path, json=False))
    text = out_path.read_text(encoding="utf-8")
    emoji_ranges = [(0x1F000, 0x1FAFF), (0x2600, 0x27BF)]
    for ch in text:
        cp = ord(ch)
        assert not any(lo <= cp <= hi for lo, hi in emoji_ranges), f"emoji {ch!r}"


def test_report_has_table_header(db_path, out_path):
    xr.cmd_run(_args(scope="system", topic=None, out=out_path, db=db_path, json=False))
    text = out_path.read_text(encoding="utf-8")
    assert "| ID | Impacto | Compatibilidad | Tipo | Titulo |" in text


def test_run_topic_filter(db_path, out_path):
    xr.cmd_run(_args(scope="system", topic="observability", out=out_path,
                     db=db_path, json=False))
    conn = sqlite3.connect(str(db_path))
    topics = [r[0] for r in conn.execute("SELECT topic FROM research_proposals").fetchall()]
    conn.close()
    assert all("observability" in (t or "") for t in topics)


# ---------- apply ----------

def test_apply_marks_approved(db_path, out_path):
    xr.cmd_run(_args(scope="system", topic=None, out=out_path, db=db_path, json=False))
    conn = sqlite3.connect(str(db_path))
    pid = conn.execute("SELECT id FROM research_proposals LIMIT 1").fetchone()[0]
    conn.close()

    rc = xr.cmd_apply(_args(id=pid, by="tester", db=db_path))
    assert rc == 0

    conn = sqlite3.connect(str(db_path))
    status, by = conn.execute(
        "SELECT status, reviewed_by FROM research_proposals WHERE id=?", (pid,)
    ).fetchone()
    conn.close()
    assert status == "approved"
    assert by == "tester"


def test_apply_unknown_id_fails(db_path, out_path):
    xr.cmd_run(_args(scope="system", topic=None, out=out_path, db=db_path, json=False))
    rc = xr.cmd_apply(_args(id="rp_doesnotexist", by=None, db=db_path))
    assert rc == 1


# ---------- list ----------

def test_list_json(db_path, out_path, capsys):
    xr.cmd_run(_args(scope="system", topic=None, out=out_path, db=db_path, json=False))
    capsys.readouterr()  # descarta salida del run previo
    rc = xr.cmd_list(_args(db=db_path, status=None, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and len(data) >= 1


# ---------- proposal_id ----------

def test_proposal_id_stable():
    a = xr.proposal_id("Title", "https://x")
    b = xr.proposal_id("Title", "https://x")
    assert a == b and a.startswith("rp_")
