"""Tests para Sprint 23: A2A + AG-UI + bundle + composition_patterns nuevos."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib.util

_modules = {
    "xa": SCRIPTS / "xdd-a2a.py",
    "xg": SCRIPTS / "xdd-agui.py",
    "xb": SCRIPTS / "xdd-bundle.py",
}
mods = {}
for name, p in _modules.items():
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    mods[name] = m


class _Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


# ---------- A2A ----------

def test_a2a_agent_card_structure():
    card = mods["xa"].emit_agent_card()
    assert card["spec_version"] == "a2a/0.1"
    assert card["name"] == "x-dd"
    assert "capabilities" in card
    assert "tools" in card["capabilities"]


def test_a2a_card_includes_composition_patterns():
    card = mods["xa"].emit_agent_card()
    tools = card["capabilities"]["tools"]
    tool_names = {t["name"] for t in tools}
    # Sprint 11 patterns + Sprint 23 new
    assert "security_review" in tool_names
    assert "plan_and_act" in tool_names
    assert "adapt_orch" in tool_names


def test_a2a_cmd_agent_card(capsys):
    rc = mods["xa"].cmd_agent_card(_Args(pretty=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "a2a/0.1" in out


def test_a2a_list_patterns_json(capsys):
    rc = mods["xa"].cmd_list_patterns(_Args(json=True))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    names = {p["name"] for p in out}
    assert "plan_and_act" in names
    assert "adapt_orch" in names


def test_a2a_invoke_unknown_agent_errors(capsys):
    rc = mods["xa"].cmd_invoke(_Args(agent="nonexistent_pattern",
                                        params=None))
    assert rc == 2


# ---------- AG-UI ----------

def test_agui_emit_valid_event():
    event = mods["xg"].emit_event("turn_start", {"turn_id": 1})
    assert event["spec"] == "agui/0.1"
    assert event["event"] == "turn_start"
    assert event["turn_id"] == 1


def test_agui_emit_missing_required_raises():
    with pytest.raises(ValueError, match="missing required"):
        mods["xg"].emit_event("tool_call", {"turn_id": 1})  # missing tool_name + args


def test_agui_unknown_event_raises():
    with pytest.raises(ValueError, match="unknown event"):
        mods["xg"].emit_event("nonexistent_event", {})


def test_agui_schemas_complete():
    schemas = mods["xg"].EVENT_SCHEMAS
    expected = {"turn_start", "tool_call", "tool_result", "hitl_request",
                "content_chunk", "turn_end"}
    assert expected.issubset(set(schemas.keys()))


def test_agui_cmd_emit(capsys):
    rc = mods["xg"].cmd_emit(_Args(
        event="hitl_request", turn_id=5, data='{"prompt":"continue?"}'))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["event"] == "hitl_request"
    assert out["prompt"] == "continue?"


def test_agui_cmd_emit_missing_field_returns_2(capsys):
    rc = mods["xg"].cmd_emit(_Args(event="tool_call", turn_id=1, data='{}'))
    assert rc == 2


# ---------- bundle ----------

def test_bundle_pack_creates_xddbundle(tmp_path):
    src = tmp_path / "src"
    (src / "skills" / "test").mkdir(parents=True)
    (src / "skills" / "test" / "SKILL.md").write_text("test")
    (src / "LICENSE").write_text("MIT License")
    out = tmp_path / "test.xddbundle"
    manifest = mods["xb"].pack(src, out, name="test-bundle", version="1.0",
                                  author="x-dd", license_str="MIT")
    assert out.exists()
    assert "signature" in manifest
    assert manifest["signature"].startswith("sha256:")


def test_bundle_verify_valid(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "LICENSE").write_text("MIT")
    out = tmp_path / "ok.xddbundle"
    mods["xb"].pack(src, out, name="ok", author="x", license_str="MIT")
    result = mods["xb"].verify(out)
    assert result["valid"] is True
    assert result["errors"] == []


def test_bundle_verify_rejects_agpl():
    # AGPL license = block (X-DD MIT pure)
    src = Path("/tmp/agpl-test-src")
    src.mkdir(exist_ok=True)
    (src / "LICENSE").write_text("AGPL")
    out = Path("/tmp/agpl-test.xddbundle")
    mods["xb"].pack(src, out, name="agpl-test", license_str="AGPL-3.0")
    result = mods["xb"].verify(out)
    assert result["valid"] is False
    assert any("license incompatible" in e for e in result["errors"])
    # cleanup
    import shutil
    shutil.rmtree(src, ignore_errors=True)
    out.unlink(missing_ok=True)


def test_bundle_install_extracts(tmp_path):
    src = tmp_path / "src"
    (src / "skills" / "foo").mkdir(parents=True)
    (src / "skills" / "foo" / "SKILL.md").write_text("foo skill")
    (src / "LICENSE").write_text("MIT")
    bundle = tmp_path / "x.xddbundle"
    mods["xb"].pack(src, bundle, name="x", license_str="MIT")
    target = tmp_path / "tgt"
    result = mods["xb"].install(bundle, target)
    assert result["count"] >= 3  # manifest + LICENSE + skill file
    assert (target / "skills" / "foo" / "SKILL.md").exists()


def test_bundle_signature_verification(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "LICENSE").write_text("MIT")
    bundle = tmp_path / "sig.xddbundle"
    mods["xb"].pack(src, bundle, name="sig", license_str="MIT")
    # Tamper: edit manifest
    with zipfile.ZipFile(bundle, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))
    manifest["name"] = "tampered"
    # Repack with tampered manifest (no re-signing)
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("LICENSE", "MIT")
    result = mods["xb"].verify(bundle)
    assert result["valid"] is False
    assert any("signature mismatch" in e for e in result["errors"])


# ---------- composition_patterns ----------

def test_registry_has_new_composition_patterns():
    reg = json.loads((ROOT / "prompts/agents/registry.json").read_text())
    names = {p["name"] for p in reg["composition_patterns"]}
    assert "plan_and_act" in names
    assert "adapt_orch" in names


def test_plan_and_act_pattern_structure():
    reg = json.loads((ROOT / "prompts/agents/registry.json").read_text())
    p = next(x for x in reg["composition_patterns"] if x["name"] == "plan_and_act")
    assert p["orchestration"] == "sequential"
    assert "gate_between" in p


def test_adapt_orch_pattern_structure():
    reg = json.loads((ROOT / "prompts/agents/registry.json").read_text())
    p = next(x for x in reg["composition_patterns"] if x["name"] == "adapt_orch")
    assert p["orchestration"] == "parallel_then_sync"
    assert p["sync_point"] == "topology_decision"


# ---------- security-bundle.xddbundle exists ----------

def test_security_bundle_present():
    p = ROOT / "bundles" / "security-bundle.xddbundle"
    assert p.exists(), "security-bundle should be committed"
    # Verify it
    result = mods["xb"].verify(p)
    assert result["valid"] is True, f"errors: {result['errors']}"
