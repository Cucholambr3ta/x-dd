"""Tests para scripts/xdd-eval.py (Sprint 10)."""
from __future__ import annotations
import json, sys, importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xdd_eval", SCRIPTS / "xdd-eval.py")
xdd_eval = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xdd_eval)


def _args(**kw):
    ns = type("A", (), {})()
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


# ---------- count_tokens ----------

def test_count_tokens_basic():
    assert xdd_eval.count_tokens("hello world") > 0
    assert xdd_eval.count_tokens("") == 0


def test_count_tokens_ignore_code():
    text = "explain this `code` thing"
    plain = xdd_eval.count_tokens(text, ignore_code=False)
    no_code = xdd_eval.count_tokens(text, ignore_code=True)
    assert no_code < plain


def test_count_tokens_ignore_fences():
    text = "explain\n```\nfn() { return 1 }\n```\nthing"
    plain = xdd_eval.count_tokens(text, ignore_code=False)
    no_code = xdd_eval.count_tokens(text, ignore_code=True)
    assert no_code < plain


# ---------- graders ----------

def test_grader_structural_pass():
    ok, _ = xdd_eval.grader_structural({"output": "error: 404"}, {"regex": r"error: \d+"})
    assert ok


def test_grader_structural_fail():
    ok, _ = xdd_eval.grader_structural({"output": "success"}, {"regex": r"error"})
    assert not ok


def test_grader_behavioral_all_keywords():
    ok, _ = xdd_eval.grader_behavioral(
        {"output": "you need useMemo and useCallback"},
        {"required_keywords": ["useMemo", "useCallback"]})
    assert ok


def test_grader_behavioral_missing():
    ok, _ = xdd_eval.grader_behavioral(
        {"output": "only useMemo here"},
        {"required_keywords": ["useMemo", "useCallback"]})
    assert not ok


def test_grader_output_match_exact():
    ok, _ = xdd_eval.grader_output_match({"output": "abc", "expected": "abc"}, {})
    assert ok


def test_grader_output_match_diff():
    ok, _ = xdd_eval.grader_output_match({"output": "abc", "expected": "abd"}, {})
    assert not ok


def test_grader_pass_at_k():
    case = {"runs": [{"passed": True}, {"passed": True}, {"passed": False}]}
    ok, _ = xdd_eval.grader_pass_at_k(case, {"k": 3, "threshold_pct": 60.0})
    assert ok  # 2/3 = 66% >= 60%


def test_grader_pass_at_k_fails():
    case = {"runs": [{"passed": False}, {"passed": True}, {"passed": False}]}
    ok, _ = xdd_eval.grader_pass_at_k(case, {"k": 3, "threshold_pct": 60.0})
    assert not ok  # 1/3 = 33% < 60%


def test_grader_token_reduction_pass():
    case = {
        "baseline": "this is a very long sentence with many extraneous filler words throughout",
        "compact": "long sentence, many fillers",
    }
    ok, msg = xdd_eval.grader_token_reduction(
        case, {"baseline_output_field": "baseline", "test_output_field": "compact",
               "threshold_pct": 50.0, "ignore_code_blocks": True})
    assert ok, msg


def test_grader_token_reduction_fail():
    case = {"baseline": "short text", "compact": "short text here"}
    ok, _ = xdd_eval.grader_token_reduction(
        case, {"baseline_output_field": "baseline", "test_output_field": "compact",
               "threshold_pct": 50.0})
    assert not ok  # compact NO es más corto


# ---------- run_suite ----------

def test_run_suite_xdd_talk_compact():
    suite_dir = ROOT / "evals" / "xdd-talk-compact"
    if not suite_dir.exists():
        pytest.skip("eval suite not present")
    report = xdd_eval.run_suite(suite_dir)
    assert report["suite"] == "xdd-talk-compact"
    assert report["all_passed"] is True
    assert report["total"] >= 5


# ---------- load_grader (S2: JSON reemplaza al parser YAML naive) ----------

def test_load_grader_json_preferido(tmp_path):
    (tmp_path / "grader.json").write_text(
        '{"type": "token_count_reduction", "threshold_pct": 50, "ignore_code_blocks": true}')
    out = xdd_eval.load_grader(tmp_path)
    assert out["type"] == "token_count_reduction"
    assert out["threshold_pct"] == 50
    assert out["ignore_code_blocks"] is True


def test_load_grader_estructura_compleja(tmp_path):
    """Regresión: el parser YAML naive NO soportaba listas/nesting; JSON sí."""
    (tmp_path / "grader.json").write_text(
        '{"type": "inspect_ai_compat", "scorers": ["includes", "match"], '
        '"opts": {"nested": {"k": 1}}, "desc": "multi\\nlinea"}')
    out = xdd_eval.load_grader(tmp_path)
    assert out["scorers"] == ["includes", "match"]       # lista preservada
    assert out["opts"]["nested"]["k"] == 1               # nesting preservado
    assert "\n" in out["desc"]                            # multiline preservado


def test_load_grader_ausente_devuelve_none(tmp_path):
    assert xdd_eval.load_grader(tmp_path) is None


def test_load_grader_json_gana_a_yaml(tmp_path):
    """Si coexisten, grader.json tiene prioridad."""
    (tmp_path / "grader.json").write_text('{"type": "from_json"}')
    (tmp_path / "grader.yaml").write_text("type: from_yaml\n")
    assert xdd_eval.load_grader(tmp_path)["type"] == "from_json"


# ---------- skills registry ----------

def test_skills_registry_valid_json():
    rp = ROOT / "prompts/skills/registry.json"
    data = json.loads(rp.read_text(encoding="utf-8"))
    assert "skills" in data
    assert all("name" in s and "path" in s for s in data["skills"])


def test_skills_registry_paths_exist():
    rp = ROOT / "prompts/skills/registry.json"
    data = json.loads(rp.read_text(encoding="utf-8"))
    for s in data["skills"]:
        assert (ROOT / s["path"]).exists(), f"skill path missing: {s['path']}"
