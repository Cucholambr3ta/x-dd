"""Tests para scripts/xdd_adapters.py (Branch 3c — SSoT → 7 IDEs, aditivo)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xa", SCRIPTS / "xdd_adapters.py")
xa = importlib.util.module_from_spec(_spec)
sys.modules["xa"] = xa  # dataclass type resolution
_spec.loader.exec_module(xa)


def _wf():
    return xa.Workflow(name="demo", description="prueba", body="cuerpo")


def test_targets_count():
    assert len(xa.TARGETS) == 7


def test_render_claude_uses_name():
    out = xa._render("claude-code", _wf())
    assert "name: demo" in out and "description: prueba" in out


def test_render_cursor_no_name():
    out = xa._render("cursor", _wf())
    assert "description: prueba" in out
    assert "name:" not in out


def test_render_vscode_mode_agent():
    assert "mode: agent" in xa._render("vscode-copilot", _wf())


def test_no_mcp_in_any_render():
    for t in xa.TARGETS:
        assert "mcp" not in xa._render(t, _wf()).lower()


def test_emit_unknown_target_raises(tmp_path):
    with pytest.raises(ValueError):
        xa.emit([_wf()], "bogus-ide", tmp_path)


def test_emit_writes_real_files(tmp_path):
    written = xa.emit([_wf()], "claude-code", tmp_path)
    assert len(written) == 1
    assert written[0].exists()
    assert not written[0].is_symlink()  # copia real
    assert (tmp_path / ".claude" / "commands" / "demo.md").exists()


def test_emit_layouts_per_target(tmp_path):
    res = xa.emit_all([_wf()], tmp_path)
    assert set(res) == set(xa.TARGETS)
    assert (tmp_path / ".cursor" / "rules" / "demo.mdc").exists()
    assert (tmp_path / ".github" / "prompts" / "demo.prompt.md").exists()
    assert (tmp_path / ".codex" / "skills" / "demo" / "SKILL.md").exists()


def test_emit_idempotent(tmp_path):
    xa.emit([_wf()], "opencode", tmp_path)
    xa.emit([_wf()], "opencode", tmp_path)  # no falla al sobrescribir
    assert (tmp_path / ".opencode" / "command" / "demo.md").exists()


def test_parse_workflow_with_frontmatter(tmp_path):
    f = tmp_path / "wf.md"
    f.write_text("---\nname: cool\ndescription: desc\n---\n\nbody here\n")
    wf = xa.parse_workflow(f)
    assert wf.name == "cool"
    assert wf.description == "desc"
    assert "body here" in wf.body


def test_parse_workflow_no_frontmatter_uses_filename(tmp_path):
    f = tmp_path / "plain.md"
    f.write_text("just content")
    wf = xa.parse_workflow(f)
    assert wf.name == "plain"
    assert wf.body == "just content"


def test_load_ssot_from_dir(tmp_path):
    (tmp_path / "a.md").write_text("---\nname: a\ndescription: da\n---\n\nA")
    (tmp_path / "b.md").write_text("---\nname: b\ndescription: db\n---\n\nB")
    ssot = xa.load_ssot_from_dir(tmp_path)
    assert [w.name for w in ssot] == ["a", "b"]


def test_load_ssot_missing_dir_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        xa.load_ssot_from_dir(tmp_path / "nope")


def test_self_test_cli():
    assert xa.main(["--self-test"]) == 0


def test_cli_emit_all(tmp_path):
    (tmp_path / "wf.md").write_text("---\nname: w\ndescription: d\n---\n\nbody")
    dest = tmp_path / "out"
    rc = xa.main(["emit-all", "--from", str(tmp_path), "--dest", str(dest)])
    assert rc == 0
    assert (dest / ".claude" / "commands" / "w.md").exists()
