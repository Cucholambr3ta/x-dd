"""Tests para scripts/xdd-provider.py (puerto LLM hexagonal, portado de agentix)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location("xp", SCRIPTS / "xdd-provider.py")
xp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xp)


# --- MockProvider determinismo ---

def test_mock_returns_mapped_response():
    p = xp.MockProvider(responses={"q": "a"})
    assert p.complete("q") == "a"


def test_mock_returns_default_when_unmapped():
    p = xp.MockProvider(default="dflt")
    assert p.complete("anything") == "dflt"


def test_mock_echoes_when_no_default():
    p = xp.MockProvider()
    assert p.complete("hola") == "mock:hola"


def test_mock_is_deterministic():
    p = xp.MockProvider(responses={"x": "y"})
    assert p.complete("x") == p.complete("x") == "y"


def test_mock_records_calls():
    p = xp.MockProvider()
    p.complete("a", system="sys")
    p.complete("b")
    assert p.calls == [("a", "sys"), ("b", None)]


def test_mock_satisfies_provider_port():
    p = xp.MockProvider()
    assert isinstance(p, xp.ProviderPort)  # structural (runtime_checkable)


# --- factory get_provider ---

def test_get_provider_default_is_mock_no_network(monkeypatch):
    monkeypatch.delenv("XDD_PROVIDER_MOCK", raising=False)
    p = xp.get_provider()
    assert isinstance(p, xp.MockProvider)


def test_get_provider_mock_explicit():
    p = xp.get_provider("anthropic", mock=True)
    assert isinstance(p, xp.MockProvider)  # mock gana aunque pidan anthropic


def test_get_provider_env_disables_mock_then_unknown_raises(monkeypatch):
    monkeypatch.setenv("XDD_PROVIDER_MOCK", "0")
    with pytest.raises(ValueError):
        xp.get_provider("nope", mock=False)


def test_get_provider_anthropic_without_key_raises(monkeypatch):
    monkeypatch.setenv("XDD_PROVIDER_MOCK", "0")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError):
        xp.get_provider("anthropic", mock=False)


def test_mock_enabled_respects_env(monkeypatch):
    monkeypatch.setenv("XDD_PROVIDER_MOCK", "1")
    assert xp._mock_enabled() is True
    monkeypatch.setenv("XDD_PROVIDER_MOCK", "false")
    assert xp._mock_enabled() is False


# --- AnthropicProvider lazy (sin red) ---

def test_anthropic_provider_requires_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        xp.AnthropicProvider()


def test_anthropic_provider_construct_with_key_no_call(monkeypatch):
    # construir no dispara red; complete() la dispararía (no se llama aquí)
    prov = xp.AnthropicProvider(api_key="sk-test")
    assert prov.model == "claude-opus-4-8"
    assert prov.api_key == "sk-test"


# --- CLI self-test ---

def test_cli_self_test_passes():
    assert xp.main(["--self-test"]) == 0


def test_cli_complete_uses_mock():
    assert xp.main(["--complete", "ping", "--mock"]) == 0
