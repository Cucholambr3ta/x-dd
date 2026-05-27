"""Tests para scripts/xdd-state.py (Sprint 9)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util
_spec = importlib.util.spec_from_file_location("xdd_state", SCRIPTS / "xdd-state.py")
xdd_state = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xdd_state)


# ---------- Fixtures ----------

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test-state.db"


def _args(**kw):
    """argparse Namespace ad-hoc."""
    ns = type("A", (), {})()
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


# ---------- init ----------

def test_init_creates_schema(db_path):
    rc = xdd_state.cmd_init(_args(db=db_path))
    assert rc == 0
    assert db_path.exists()
    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    conn.close()
    assert "instincts" in tables
    assert "instinct_sessions" in tables
    assert "evolutions" in tables


# ---------- record-instinct ----------

def test_record_new_instinct(db_path):
    xdd_state.cmd_init(_args(db=db_path))
    rc = xdd_state.cmd_record(_args(
        db=db_path, pattern="test pattern", category="user_action",
        context=None, session_id=None, json=True))
    assert rc == 0
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM instincts").fetchone()[0]
    conn.close()
    assert count == 1


def test_record_existing_increments(db_path):
    xdd_state.cmd_init(_args(db=db_path))
    for _ in range(3):
        xdd_state.cmd_record(_args(db=db_path, pattern="same pattern",
            category="user_action", context=None, session_id=None, json=False))
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT occurrences, confidence FROM instincts").fetchone()
    conn.close()
    assert row[0] == 3
    assert row[1] == pytest.approx(0.3, abs=0.01)  # 0.1 + 0.1 + 0.1


def test_confidence_caps_at_1(db_path):
    xdd_state.cmd_init(_args(db=db_path))
    for _ in range(20):
        xdd_state.cmd_record(_args(db=db_path, pattern="frequent",
            category="user_action", context=None, session_id=None, json=False))
    conn = sqlite3.connect(db_path)
    conf = conn.execute("SELECT confidence FROM instincts").fetchone()[0]
    conn.close()
    assert conf == 1.0


def test_session_tracking(db_path):
    xdd_state.cmd_init(_args(db=db_path))
    xdd_state.cmd_record(_args(db=db_path, pattern="p1",
        category="user_action", context="ctx", session_id="sess_001", json=False))
    conn = sqlite3.connect(db_path)
    sessions = conn.execute("SELECT session_id FROM instinct_sessions").fetchall()
    conn.close()
    assert len(sessions) == 1
    assert sessions[0][0] == "sess_001"


# ---------- list ----------

def test_list_filters_by_category(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    xdd_state.cmd_record(_args(db=db_path, pattern="a", category="user_action",
        context=None, session_id=None, json=False))
    xdd_state.cmd_record(_args(db=db_path, pattern="b", category="tool_use",
        context=None, session_id=None, json=False))
    capsys.readouterr()  # limpiar buffer previo
    rc = xdd_state.cmd_list(_args(db=db_path, category="tool_use",
        min_confidence=None, promoted=None, limit=10, json=True))
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["count"] == 1
    assert out["instincts"][0]["category"] == "tool_use"


def test_list_filters_by_confidence(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    # 1 instinct con alta conf, 1 con baja
    for _ in range(8):  # 0.1 * 8 = 0.8
        xdd_state.cmd_record(_args(db=db_path, pattern="high", category="user_action",
            context=None, session_id=None, json=False))
    xdd_state.cmd_record(_args(db=db_path, pattern="low", category="user_action",
        context=None, session_id=None, json=False))
    capsys.readouterr()
    rc = xdd_state.cmd_list(_args(db=db_path, category=None,
        min_confidence=0.5, promoted=None, limit=10, json=True))
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 1
    assert out["instincts"][0]["pattern"] == "high"


# ---------- evolve ----------

def test_evolve_finds_clusters(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    # 3 instincts de user_action con alta confidence
    for i in range(3):
        for _ in range(6):  # bump confidence to 0.6
            xdd_state.cmd_record(_args(db=db_path, pattern=f"action_{i}",
                category="user_action", context=None, session_id=None, json=False))
    capsys.readouterr()
    rc = xdd_state.cmd_evolve(_args(db=db_path, min_confidence=0.5,
        min_cluster_size=3, generate=False, json=True))
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert len(out["proposals"]) == 1
    p = out["proposals"][0]
    assert p["proposed_type"] == "command"  # user_action → command
    assert p["instinct_count"] == 3


def test_evolve_skips_small_clusters(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    # solo 2 instincts (debajo del min_cluster_size=3)
    for i in range(2):
        for _ in range(6):
            xdd_state.cmd_record(_args(db=db_path, pattern=f"p_{i}",
                category="user_action", context=None, session_id=None, json=False))
    capsys.readouterr()
    rc = xdd_state.cmd_evolve(_args(db=db_path, min_confidence=0.5,
        min_cluster_size=3, generate=False, json=True))
    out = json.loads(capsys.readouterr().out)
    assert len(out["proposals"]) == 0


def test_evolve_generate_saves_to_db(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    for i in range(3):
        for _ in range(6):
            xdd_state.cmd_record(_args(db=db_path, pattern=f"p_{i}",
                category="user_action", context=None, session_id=None, json=False))
    xdd_state.cmd_evolve(_args(db=db_path, min_confidence=0.5,
        min_cluster_size=3, generate=True, json=True))
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM evolutions").fetchone()[0]
    conn.close()
    assert count == 1


# ---------- prune ----------

def test_prune_removes_old_low_confidence(db_path):
    xdd_state.cmd_init(_args(db=db_path))
    xdd_state.cmd_record(_args(db=db_path, pattern="old", category="user_action",
        context=None, session_id=None, json=False))
    # Forzar last_seen viejo
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE instincts SET last_seen = '2020-01-01T00:00:00Z'")
    conn.commit()
    conn.close()
    rc = xdd_state.cmd_prune(_args(db=db_path, older_than_days=30, max_confidence=0.3))
    assert rc == 0
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM instincts").fetchone()[0]
    conn.close()
    assert count == 0


# ---------- stats ----------

def test_stats_reports_correctly(db_path, capsys):
    xdd_state.cmd_init(_args(db=db_path))
    xdd_state.cmd_record(_args(db=db_path, pattern="p1", category="user_action",
        context=None, session_id=None, json=False))
    capsys.readouterr()
    rc = xdd_state.cmd_stats(_args(db=db_path, json=True))
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["total_instincts"] == 1
    assert out["by_category"]["user_action"] == 1
