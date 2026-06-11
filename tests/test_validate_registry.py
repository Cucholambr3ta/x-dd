"""Tests para scripts/validate-registry.py — validador del registry (S1, gap de cobertura).

Cubre: registry válido, id duplicado, ref a agente inexistente (composition/routing),
prompt_file faltante. Se monkeypatchean las globals REGISTRY/SCHEMA/ROOT a un tmp.

Run: pytest tests/test_validate_registry.py -v
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("validate_registry", SCRIPTS / "validate-registry.py")
vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vr)


# Schema permisivo (la validación dura de id-refs es la que probamos en --strict).
_SCHEMA = {"type": "object", "required": ["agents"], "properties": {"agents": {"type": "array"}}}


@pytest.fixture
def craft(tmp_path, monkeypatch):
    """Devuelve fn(registry_dict) que escribe registry+schema+prompts y apunta las globals."""
    def _build(registry: dict) -> None:
        reg = tmp_path / "registry.json"
        sch = tmp_path / "registry.schema.json"
        reg.write_text(json.dumps(registry), encoding="utf-8")
        sch.write_text(json.dumps(_SCHEMA), encoding="utf-8")
        # Crear los prompt_file declarados (salvo que el test quiera el caso faltante).
        for a in registry.get("agents", []):
            pf = tmp_path / a["prompt_file"]
            if a.get("_skip_pf"):
                a.pop("_skip_pf", None)
                continue
            pf.parent.mkdir(parents=True, exist_ok=True)
            pf.write_text("# agent\n", encoding="utf-8")
        # Reescribir registry sin el flag interno.
        reg.write_text(json.dumps(registry), encoding="utf-8")
        monkeypatch.setattr(vr, "ROOT", tmp_path)
        monkeypatch.setattr(vr, "REGISTRY", reg)
        monkeypatch.setattr(vr, "SCHEMA", sch)
    return _build


def _agent(aid, cat="engineering", pf=None):
    return {"id": aid, "name": aid, "category": cat,
            "prompt_file": pf or f"prompts/agents/{cat}/{aid}.md"}


def test_registry_valido(craft):
    craft({"agents": [_agent("a1"), _agent("a2")]})
    assert vr.main([]) == 0


def test_id_duplicado_strict(craft):
    craft({"agents": [_agent("dup"), _agent("dup")]})
    assert vr.main(["--strict"]) == 1


def test_id_duplicado_no_strict_pasa(craft):
    """Sin --strict, duplicados no fallan (solo strict los caza)."""
    craft({"agents": [_agent("dup"), _agent("dup")]})
    assert vr.main([]) == 0


def test_composition_ref_inexistente(craft):
    craft({
        "agents": [_agent("lead1")],
        "composition_patterns": [
            {"name": "cp1", "lead": "lead1", "specialists": ["fantasma"]}
        ],
    })
    assert vr.main(["--strict"]) == 1


def test_routing_ref_inexistente(craft):
    craft({
        "agents": [_agent("a1")],
        "routing_rules": [{"agent": "noexiste"}],
    })
    assert vr.main(["--strict"]) == 1


def test_prompt_file_faltante(craft):
    craft({"agents": [{"id": "x", "name": "x", "category": "eng",
                       "prompt_file": "prompts/agents/eng/x.md", "_skip_pf": True}]})
    assert vr.main([]) == 1
