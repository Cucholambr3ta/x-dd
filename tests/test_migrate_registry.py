"""Tests para scripts/migrate-agents-to-registry.py (S1, gap de cobertura).

Cubre slugify, parse_frontmatter (parser YAML mínimo) y parse_agent (round-trip
.md → entrada de registry).

Run: pytest tests/test_migrate_registry.py -v
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("migrate_registry",
                                               SCRIPTS / "migrate-agents-to-registry.py")
mig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mig)


# ---------- slugify ----------

@pytest.mark.parametrize("raw,expected", [
    ("Backend Architect", "backend-architect"),
    ("  Spaces  ", "spaces"),
    ("UPPER_case 123", "upper-case-123"),
    ("már-két!!ing", "m-r-k-t-ing"),  # no-alfanumérico colapsa a guion
    ("--leading-trailing--", "leading-trailing"),
])
def test_slugify(raw, expected):
    assert mig.slugify(raw) == expected


# ---------- parse_frontmatter ----------

def test_frontmatter_basico():
    text = '---\nname: Foo Bar\ndescription: "hace cosas"\n---\n# cuerpo\n'
    fm = mig.parse_frontmatter(text)
    assert fm["name"] == "Foo Bar"
    assert fm["description"] == "hace cosas"  # comillas stripeadas


def test_frontmatter_ausente():
    assert mig.parse_frontmatter("# sin frontmatter\n") == {}


def test_frontmatter_ignora_lineas_indentadas():
    """Líneas que empiezan con espacio (nested) no se toman como keys top-level."""
    text = "---\nname: X\n  nested: ignorado\n---\n"
    fm = mig.parse_frontmatter(text)
    assert fm.get("name") == "X"
    assert "nested" not in fm


# ---------- parse_agent (round-trip) ----------

def test_parse_agent_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(mig, "ROOT", tmp_path)
    cat_dir = tmp_path / "prompts" / "agents" / "engineering"
    cat_dir.mkdir(parents=True)
    md = cat_dir / "backend-architect.md"
    md.write_text('---\nname: Backend Architect\ndescription: Diseña backends.\n---\n# rol\n',
                  encoding="utf-8")

    entry = mig.parse_agent(md, "engineering")
    assert entry is not None
    assert entry["id"] == "backend-architect"
    assert entry["name"] == "Backend Architect"
    assert entry["category"] == "engineering"
    assert entry["description"] == "Diseña backends."
    assert entry["prompt_file"] == "prompts/agents/engineering/backend-architect.md"
    assert "mcp" in entry["ide_compat"]


def test_parse_agent_sin_frontmatter_devuelve_none(tmp_path, monkeypatch):
    monkeypatch.setattr(mig, "ROOT", tmp_path)
    md = tmp_path / "x.md"
    md.write_text("# sin fm\n", encoding="utf-8")
    assert mig.parse_agent(md, "engineering") is None


def test_parse_agent_name_fallback_desde_stem(tmp_path, monkeypatch):
    """Sin campo name, deriva el nombre del filename."""
    monkeypatch.setattr(mig, "ROOT", tmp_path)
    md = tmp_path / "data-ml-engineer.md"
    md.write_text("---\ndescription: ML.\n---\n", encoding="utf-8")
    entry = mig.parse_agent(md, "data")
    assert entry["name"] == "Data Ml Engineer"
