"""Tests para Sprint 22 AHE: trace-summarize + frozen-transfer + evolutions schema."""
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

_specs = {
    "xs": SCRIPTS / "xdd-state.py",
    "xts": SCRIPTS / "xdd-trace-summarize.py",
    "xft": SCRIPTS / "xdd-frozen-transfer.py",
}
mods = {}
for name, p in _specs.items():
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    mods[name] = m


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


# ---------- evolutions schema migration ----------

def test_evolutions_table_includes_ahe_columns(tmp_path):
    db_path = tmp_path / "state.db"
    conn = mods["xs"].db(db_path)
    cols = {row[1] for row in conn.execute(
        "PRAGMA table_info(evolutions)").fetchall()}
    expected = {"rationale_evidence", "predicted_impact",
                "falsification_metric", "falsification_outcome"}
    assert expected.issubset(cols)


def test_migrate_idempotent(tmp_path):
    db_path = tmp_path / "state.db"
    conn = mods["xs"].db(db_path)
    conn.close()
    # Re-open should not error
    conn = mods["xs"].db(db_path)
    cols = {row[1] for row in conn.execute(
        "PRAGMA table_info(evolutions)").fetchall()}
    assert "rationale_evidence" in cols


def test_evolve_populates_ahe_fields(tmp_path, capsys):
    db_path = str(tmp_path / "state.db")
    xs = mods["xs"]
    xs.cmd_init(_Args(db=db_path))
    # Inject 4 instincts confidencia ≥ 0.5
    for i, p in enumerate(["fix auth bug login", "fix auth bug session",
                            "fix auth bug token", "fix auth bug logout"]):
        xs.cmd_record(_Args(db=db_path, pattern=p, category="error_pattern",
                             context=None, session_id=None, json=False))
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE instincts SET confidence = 0.8")
    conn.commit()
    conn.close()
    capsys.readouterr()
    rc = xs.cmd_evolve(_Args(db=db_path, min_confidence=0.5,
                              min_cluster_size=3, similarity_threshold=0.1,
                              category_only=False, generate=True, json=True))
    assert rc == 0
    # Read back from DB to confirm new fields populated
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT cluster_id, rationale_evidence, predicted_impact, "
        "falsification_metric, falsification_outcome FROM evolutions"
    ).fetchall()
    conn.close()
    assert len(rows) >= 1
    cid, evidence, pred, falsif, outcome = rows[0]
    assert evidence is not None
    assert pred is not None
    assert falsif is not None
    assert outcome is None  # filled in next iteration
    # Evidence is valid JSON
    ev = json.loads(evidence)
    assert "instinct_count" in ev


# ---------- trace-summarize ----------

def test_trace_summarize_session(tmp_path):
    sid = "sess-test"
    p = tmp_path / f"{sid}.jsonl"
    events = [
        {"ts": "2026-05-27T10:00:00Z", "event": "turn_start", "role": "user",
         "content": "hello"},
        {"ts": "2026-05-27T10:00:01Z", "event": "tool_call", "role": "assistant",
         "content": "running tool"},
        {"ts": "2026-05-27T10:00:02Z", "event": "turn_end", "role": "assistant",
         "content": "done"},
    ]
    p.write_text("\n".join(json.dumps(e) for e in events))
    loaded = mods["xts"].load_session(sid, tmp_path)
    assert len(loaded) == 3
    report = mods["xts"].summarize(loaded, "detail")
    assert report["events_total"] == 3
    assert "turn_start" in report["event_types"]
    assert "samples" in report


def test_trace_summarize_full_includes_excerpts(tmp_path):
    sid = "s2"
    p = tmp_path / f"{sid}.jsonl"
    p.write_text(json.dumps({"ts": "x", "event": "e", "content": "ab"}))
    loaded = mods["xts"].load_session(sid, tmp_path)
    report = mods["xts"].summarize(loaded, "full")
    assert "all_events_excerpts" in report


def test_trace_summarize_render_markdown(tmp_path):
    report = {"events_total": 5, "first_ts": "a", "last_ts": "b",
              "event_types": {"x": 3, "y": 2}, "roles": {"user": 5}}
    md = mods["xts"].render_markdown(report, "sid1", "summary")
    assert "# Trace Summary" in md
    assert "session=sid1" in md
    assert "`x`: 3" in md


# ---------- frozen-transfer ----------

def test_frozen_transfer_dry_run(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src-proj"
    tgt = tmp_path / "tgt-proj"
    (src / "skills" / "test-skill").mkdir(parents=True)
    (src / "skills" / "test-skill" / "SKILL.md").write_text("test")
    tgt.mkdir()
    monkeypatch.setattr(mods["xft"], "DEFAULT_EXP_DIR", tmp_path / "exps")
    rc = mods["xft"].cmd_run(_Args(source=str(src), target=str(tgt),
                                     suite=None, dry_run=True, json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["transferred"]["skills"]) == 1
    assert out["dry_run"] is True


def test_frozen_transfer_real_copy(tmp_path, monkeypatch):
    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    (src / "skills" / "my-skill").mkdir(parents=True)
    (src / "skills" / "my-skill" / "SKILL.md").write_text("frozen content")
    tgt.mkdir()
    monkeypatch.setattr(mods["xft"], "DEFAULT_EXP_DIR", tmp_path / "exps")
    rc = mods["xft"].cmd_run(_Args(source=str(src), target=str(tgt),
                                     suite=None, dry_run=False, json=True))
    assert rc == 0
    assert (tgt / "skills" / "my-skill" / "SKILL.md").exists()
    content = (tgt / "skills" / "my-skill" / "SKILL.md").read_text()
    assert "frozen content" in content


def test_frozen_transfer_invalid_source():
    rc = mods["xft"].cmd_run(_Args(source="/nonexistent/path/xyz",
                                     target="/tmp", suite=None,
                                     dry_run=True, json=False))
    assert rc == 2


def test_frozen_transfer_list_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mods["xft"], "DEFAULT_EXP_DIR", tmp_path / "exps")
    rc = mods["xft"].cmd_list(_Args(json=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "[]" in out
