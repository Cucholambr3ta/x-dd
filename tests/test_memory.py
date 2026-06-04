"""Tests para scripts/xdd-memory.py — sistema nativo de memoria conversacional."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xdd_memory", SCRIPTS / "xdd-memory.py")
xm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xm)


def _args(**kw):
    ns = type("A", (), {})()
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


@pytest.fixture
def proj(tmp_path):
    return tmp_path


@pytest.fixture(autouse=True)
def activate_memory(monkeypatch):
    monkeypatch.setenv("XDD_MEMORY", "1")
    monkeypatch.setattr(xm, "MEMORY_ACTIVE", True)


# ── load ──────────────────────────────────────────────────────────────────────

def test_load_no_memory_files(proj, capsys):
    rc = xm.cmd_load(_args(project=proj, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "MEMORY.md no existe" in out


def test_load_with_existing_memory(proj):
    (proj / "AGENT_MEMORY.md").write_text("# long-term\n", encoding="utf-8")
    rc = xm.cmd_load(_args(project=proj, json=False))
    assert rc == 0


def test_load_json(proj, capsys):
    rc = xm.cmd_load(_args(project=proj, json=True))
    assert rc == 0
    out = capsys.readouterr().out.strip()
    # la ultima linea es el JSON (previas son log prints)
    last_line = [l for l in out.splitlines() if l.strip()][-1]
    data = json.loads(last_line)
    assert "ok" in data


# ── summarize ────────────────────────────────────────────────────────────────

def test_summarize_creates_journal(proj):
    rc = xm.cmd_summarize(_args(project=proj, messages=None, json=False))
    assert rc == 0
    today = xm.today_str()
    assert (proj / "memory" / f"{today}.md").exists()


def test_summarize_with_messages(proj, tmp_path):
    msgs_file = tmp_path / "msgs.jsonl"
    msgs = [{"role": "user", "content": "Hola"}, {"role": "assistant", "content": "Mundo"}]
    msgs_file.write_text(json.dumps(msgs), encoding="utf-8")
    rc = xm.cmd_summarize(_args(project=proj, messages=str(msgs_file), json=False))
    assert rc == 0
    today = xm.today_str()
    journal = proj / "memory" / f"{today}.md"
    assert journal.exists()
    assert "Sesion" in journal.read_text(encoding="utf-8")


def test_summarize_appends_on_existing(proj):
    today = xm.today_str()
    (proj / "memory").mkdir()
    (proj / "memory" / f"{today}.md").write_text("# Journal\n\n## Sesion anterior\n\ncontent\n", encoding="utf-8")
    xm.cmd_summarize(_args(project=proj, messages=None, json=False))
    text = (proj / "memory" / f"{today}.md").read_text(encoding="utf-8")
    assert text.count("## Sesion") >= 2


# ── compact ───────────────────────────────────────────────────────────────────

def test_compact_below_threshold(proj, tmp_path, capsys):
    msgs_file = tmp_path / "msgs.jsonl"
    msgs_file.write_text('[{"role":"user","content":"hi"}]', encoding="utf-8")
    rc = xm.cmd_compact(_args(project=proj, messages=str(msgs_file), threshold=999999, output=None, json=False))
    assert rc == 0
    assert "No se compacta" in capsys.readouterr().out


def test_compact_above_threshold_writes_output(proj, tmp_path):
    msgs_file = tmp_path / "msgs.jsonl"
    msgs_file.write_text('[{"role":"user","content":"hi"}]', encoding="utf-8")
    out_file = tmp_path / "summary.md"
    rc = xm.cmd_compact(_args(project=proj, messages=str(msgs_file), threshold=1, output=str(out_file), json=False))
    assert rc == 0
    assert out_file.exists()
    assert "Goal" in out_file.read_text(encoding="utf-8")


def test_compact_missing_messages_returns_error(proj):
    rc = xm.cmd_compact(_args(project=proj, messages="/nonexistent/file.json", threshold=100, output=None, json=False))
    assert rc == 1


# ── search ────────────────────────────────────────────────────────────────────

def test_search_no_docs(proj, capsys):
    rc = xm.cmd_search(_args(project=proj, query=["anything"], max=5, json=False))
    assert rc == 0


def test_search_finds_in_memory_md(proj, capsys):
    (proj / "AGENT_MEMORY.md").write_text("User prefers Python. Loves TDD. Dislikes Java.", encoding="utf-8")
    rc = xm.cmd_search(_args(project=proj, query=["Python", "TDD"], max=5, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "AGENT_MEMORY.md" in out


def test_search_finds_in_journal(proj, capsys):
    (proj / "memory").mkdir()
    (proj / "memory" / f"{xm.today_str()}.md").write_text("Decision: use PostgreSQL for storage.", encoding="utf-8")
    rc = xm.cmd_search(_args(project=proj, query=["PostgreSQL"], max=5, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "PostgreSQL" in out


def test_search_json_output(proj, capsys):
    (proj / "AGENT_MEMORY.md").write_text("Context: testing the search system.", encoding="utf-8")
    rc = xm.cmd_search(_args(project=proj, query=["testing"], max=3, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)


# ── gc ────────────────────────────────────────────────────────────────────────

def test_gc_empty(proj, capsys):
    rc = xm.cmd_gc(_args(project=proj, days=3, json=False))
    assert rc == 0


def test_gc_removes_old_tool_results(proj):
    import time
    tool_dir = proj / "tool_result"
    tool_dir.mkdir()
    old_file = tool_dir / "old.txt"
    old_file.write_text("old content", encoding="utf-8")
    # Modificar mtime para simular archivo viejo (4 dias)
    old_ts = time.time() - (4 * 86400)
    os.utime(old_file, (old_ts, old_ts))
    recent_file = tool_dir / "recent.txt"
    recent_file.write_text("recent content", encoding="utf-8")

    rc = xm.cmd_gc(_args(project=proj, days=3, json=False))
    assert rc == 0
    assert not old_file.exists()
    assert recent_file.exists()


# ── stats ──────────────────────────────────────────────────────────────────────

def test_stats_json(proj, capsys):
    rc = xm.cmd_stats(_args(project=proj, json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "active" in data
    assert data["active"] is True


def test_stats_human(proj, capsys):
    rc = xm.cmd_stats(_args(project=proj, json=False))
    assert rc == 0
    out = capsys.readouterr().out
    assert "SI" in out or "NO" in out


# ── bm25 ──────────────────────────────────────────────────────────────────────

def test_bm25_ranks_relevant_docs():
    docs = [
        ("a.md", "Python is great for data science and machine learning"),
        ("b.md", "Java is a compiled language used in enterprise"),
        ("c.md", "Python testing with pytest is the standard approach"),
    ]
    results = xm.bm25_search("Python testing", docs, max_results=3)
    assert len(results) >= 1
    # El doc con "Python testing" debe ranquear primero
    assert results[0][0] == "c.md"


def test_bm25_empty_docs():
    results = xm.bm25_search("anything", [], max_results=5)
    assert results == []


# ── token counting ────────────────────────────────────────────────────────────

def test_token_count_approx():
    assert xm.count_tokens_approx("") == 1
    assert xm.count_tokens_approx("a" * 400) == 100
    assert xm.count_tokens_approx("hello world") > 0
