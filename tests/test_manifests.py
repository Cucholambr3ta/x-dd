"""Tests para los manifests + schemas de install (Sprint 7.5)."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = ROOT / "manifests"
SCHEMAS = ROOT / "schemas"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- Schemas son JSON Schema válidos ----------

@pytest.mark.parametrize("schema_file", [
    "install-modules.schema.json",
    "install-profiles.schema.json",
    "install-components.schema.json",
    "hooks.schema.json",
    "xdd.config.schema.json",
    # registry.schema.json no está en schemas/, vive en prompts/agents/
])
def test_schema_is_valid_jsonschema(schema_file):
    schema = load(SCHEMAS / schema_file)
    # Si el Draft202012Validator no rechaza el meta-schema, está OK.
    jsonschema.Draft202012Validator.check_schema(schema)


# ---------- Manifests validan contra su schema ----------

def test_install_modules_valida():
    schema = load(SCHEMAS / "install-modules.schema.json")
    doc = load(MANIFESTS / "install-modules.json")
    jsonschema.validate(doc, schema)


def test_install_profiles_valida():
    schema = load(SCHEMAS / "install-profiles.schema.json")
    doc = load(MANIFESTS / "install-profiles.json")
    jsonschema.validate(doc, schema)


def test_install_components_valida():
    schema = load(SCHEMAS / "install-components.schema.json")
    doc = load(MANIFESTS / "install-components.json")
    jsonschema.validate(doc, schema)


def test_hooks_valida():
    schema = load(SCHEMAS / "hooks.schema.json")
    doc = load(ROOT / ".agent/hooks/hooks.json")
    jsonschema.validate(doc, schema)


# ---------- Integridad referencial ----------

def test_perfiles_referencian_modulos_existentes():
    profs = load(MANIFESTS / "install-profiles.json")["profiles"]
    mods = load(MANIFESTS / "install-modules.json")["modules"]
    for pname, prof in profs.items():
        for m in prof["modules"]:
            assert m in mods, f"perfil {pname!r}: módulo {m!r} no existe en install-modules.json"


def test_componentes_referencian_modulos_existentes():
    comps = load(MANIFESTS / "install-components.json")["components"]
    mods = load(MANIFESTS / "install-modules.json")["modules"]
    for cname, comp in comps.items():
        assert comp["module"] in mods, f"component {cname!r}: módulo {comp['module']!r} no existe"


def test_modulos_requires_referencian_modulos_existentes():
    mods = load(MANIFESTS / "install-modules.json")["modules"]
    for mname, mod in mods.items():
        for req in mod.get("requires", []):
            assert req in mods, f"módulo {mname!r}: requires {req!r} no existe"


# ---------- Archivos declarados existen (donde aplica) ----------

def test_modulos_core_archivos_existen():
    """Para módulos sin available_from (ya disponibles), todos los files deben existir."""
    mods = load(MANIFESTS / "install-modules.json")["modules"]
    for mname, mod in mods.items():
        if "available_from" in mod:
            continue  # módulos futuros (Sprint 9-12)
        for f in mod["files"]:
            target = ROOT / f
            assert target.exists(), f"módulo {mname!r}: archivo {f!r} no existe"


# ---------- Hooks ----------

def test_hook_scripts_existen():
    hooks_doc = load(ROOT / ".agent/hooks/hooks.json")
    for event, hook_list in hooks_doc["hooks"].items():
        for h in hook_list:
            script_path = ROOT / h["script"]
            assert script_path.exists(), \
                f"hook {h['id']!r} script no existe: {h['script']}"


def test_hooks_ids_unicos():
    hooks_doc = load(ROOT / ".agent/hooks/hooks.json")
    ids = []
    for event, hook_list in hooks_doc["hooks"].items():
        for h in hook_list:
            ids.append(h["id"])
    assert len(ids) == len(set(ids)), f"IDs duplicados: {ids}"


def test_hooks_count():
    """Sprint 7.2 declaró 8 hooks (3 PreToolUse + 2 PostToolUse + 1 SessionStart + 2 Stop)."""
    hooks_doc = load(ROOT / ".agent/hooks/hooks.json")
    total = sum(len(h) for h in hooks_doc["hooks"].values())
    assert total == 8, f"se esperaban 8 hooks, hay {total}"
