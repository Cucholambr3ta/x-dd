"""tools.py — Implementación de las 6 tools MCP de X-DD."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Reusa scripts/xdd-gate.py como módulo importable.
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util as _ilu  # noqa: E402

_gate_spec = _ilu.spec_from_file_location("xdd_gate", SCRIPTS_DIR / "xdd-gate.py")
xdd_gate = _ilu.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(xdd_gate)  # type: ignore[union-attr]

WORKFLOWS_DIR = ROOT / ".agent" / "workflows"
REGISTRY_PATH = ROOT / "prompts" / "agents" / "registry.json"
XDD_DIR = ROOT / ".xdd"

# Whitelist de paths que xdd_get_phase_artifacts puede devolver (T4.3 mitigación).
ALLOWED_ARTIFACT_PREFIXES = (".xdd/",)


# ---------- Tool: xdd_validate_phase ----------
def xdd_validate_phase(phase: str, project_root: str | None = None) -> dict:
    root = Path(project_root or ROOT).resolve()
    ok, errs = xdd_gate._validate_phase(root, phase)
    return {"phase": phase, "ok": ok, "errors": errs}


# ---------- Tool: xdd_transition_phase ----------
def xdd_transition_phase(from_phase: str, to_phase: str,
                          project_root: str | None = None) -> dict:
    root = Path(project_root or ROOT).resolve()
    phases = xdd_gate.PHASE_IDS
    if from_phase not in phases or to_phase not in phases:
        return {"ok": False, "error": f"Fase desconocida ({from_phase} → {to_phase})"}
    if phases.index(to_phase) != phases.index(from_phase) + 1:
        return {"ok": False, "error": f"Transición no secuencial: {from_phase} → {to_phase}"}
    ok, errs = xdd_gate._validate_phase(root, from_phase)
    return {"from": from_phase, "to": to_phase, "ok": ok, "errors": errs}


# ---------- Tool: xdd_list_workflows ----------
def xdd_list_workflows() -> dict:
    """Lista los workflows .agent/workflows/*.md con su frontmatter `description:`."""
    if not WORKFLOWS_DIR.exists():
        return {"workflows": [], "count": 0}
    workflows = []
    for f in sorted(WORKFLOWS_DIR.glob("*.md")):
        name = f.stem
        if name.lower() in ("readme",):
            continue
        desc = ""
        try:
            text = f.read_text(encoding="utf-8")
            m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            if m:
                desc = m.group(1).strip().strip('"').strip("'")
        except OSError:
            pass
        workflows.append({
            "name": name,
            "description": desc,
            "path": str(f.relative_to(ROOT).as_posix()),
        })
    return {"workflows": workflows, "count": len(workflows)}


# ---------- Tool: xdd_invoke_workflow ----------
def xdd_invoke_workflow(name: str, _args: list[str] | None = None) -> dict:
    """Devuelve el contenido del workflow para que el orquestador lo ejecute.

    NO ejecuta nada por su cuenta — MCP server propio no tiene 'execute_shell'
    (T6.3 mitigación). El orquestador (Claude Code, OpenCode, etc.) es quien
    interpreta el workflow.
    """
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    if safe_name != name:
        return {"ok": False, "error": "Nombre de workflow inválido."}
    wf = WORKFLOWS_DIR / f"{safe_name}.md"
    if not wf.exists() or not wf.resolve().is_relative_to(WORKFLOWS_DIR.resolve()):
        return {"ok": False, "error": f"Workflow {safe_name!r} no encontrado."}
    return {
        "ok": True,
        "name": safe_name,
        "path": str(wf.relative_to(ROOT).as_posix()),
        "content": wf.read_text(encoding="utf-8"),
        "note": "Este server NO ejecuta el workflow — devuelve el .md para que tu "
                "orquestador (Claude Code / OpenCode / etc.) lo interprete.",
    }


# ---------- Tool: xdd_list_agents ----------
def xdd_list_agents(category: str | None = None) -> dict:
    if not REGISTRY_PATH.exists():
        return {"ok": False, "error": "registry.json no existe. Corré scripts/migrate-agents-to-registry.py"}
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    agents = data.get("agents", [])
    if category:
        agents = [a for a in agents if a.get("category") == category]
    return {
        "ok": True,
        "count": len(agents),
        "agents": [{
            "id": a["id"],
            "name": a["name"],
            "category": a["category"],
            "description": a.get("description", ""),
            "prompt_file": a["prompt_file"],
        } for a in agents],
    }


# ---------- Tool: xdd_get_phase_artifacts ----------
def xdd_get_phase_artifacts(phase: str) -> dict:
    """Lista artefactos en .xdd/<fase>/. NO devuelve contenido fuera de .xdd/ (T4.3)."""
    if phase not in xdd_gate.PHASE_IDS:
        return {"ok": False, "error": f"Fase desconocida: {phase}"}
    pdir = XDD_DIR / phase
    if not pdir.exists():
        return {"ok": True, "phase": phase, "exists": False, "artifacts": []}

    artifacts = []
    for f in sorted(pdir.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(ROOT).as_posix())
            if not any(rel.startswith(p) for p in ALLOWED_ARTIFACT_PREFIXES):
                continue  # defensa en profundidad
            artifacts.append({
                "path": rel,
                "size": f.stat().st_size,
            })

    status_file = pdir / ".status"
    status = status_file.read_text().strip() if status_file.exists() else None
    return {
        "ok": True,
        "phase": phase,
        "exists": True,
        "status": status,
        "artifacts": artifacts,
    }


# ---------- Tool registry ----------
TOOLS = {
    "xdd_validate_phase": {
        "fn": xdd_validate_phase,
        "schema": {
            "name": "xdd_validate_phase",
            "description": "Valida una fase del pipeline X-DD: status APROBADO + checksums + firma HMAC.",
            "inputSchema": {
                "type": "object",
                "required": ["phase"],
                "properties": {
                    "phase": {"type": "string", "enum": list(xdd_gate.PHASE_IDS)},
                    "project_root": {"type": "string", "description": "Default: repo raíz."},
                },
            },
        },
    },
    "xdd_transition_phase": {
        "fn": xdd_transition_phase,
        "schema": {
            "name": "xdd_transition_phase",
            "description": "Valida transición de una fase a la siguiente (secuencial, fase origen APROBADA).",
            "inputSchema": {
                "type": "object",
                "required": ["from_phase", "to_phase"],
                "properties": {
                    "from_phase": {"type": "string", "enum": list(xdd_gate.PHASE_IDS)},
                    "to_phase": {"type": "string", "enum": list(xdd_gate.PHASE_IDS)},
                    "project_root": {"type": "string"},
                },
            },
        },
    },
    "xdd_list_workflows": {
        "fn": xdd_list_workflows,
        "schema": {
            "name": "xdd_list_workflows",
            "description": "Lista los workflows X-DD disponibles con su descripción frontmatter.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    },
    "xdd_invoke_workflow": {
        "fn": xdd_invoke_workflow,
        "schema": {
            "name": "xdd_invoke_workflow",
            "description": "Devuelve el contenido del workflow para que el orquestador lo interprete. NO lo ejecuta directamente.",
            "inputSchema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Nombre del workflow (sin .md), alfanumérico+guion."},
                },
            },
        },
    },
    "xdd_list_agents": {
        "fn": xdd_list_agents,
        "schema": {
            "name": "xdd_list_agents",
            "description": "Lista agentes del registry. Filtrable por categoría.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filtra por categoría (ej. engineering, security)."},
                },
            },
        },
    },
    "xdd_get_phase_artifacts": {
        "fn": xdd_get_phase_artifacts,
        "schema": {
            "name": "xdd_get_phase_artifacts",
            "description": "Lista artefactos en .xdd/<fase>/ (paths + sizes). Solo lectura, solo dentro de .xdd/.",
            "inputSchema": {
                "type": "object",
                "required": ["phase"],
                "properties": {
                    "phase": {"type": "string", "enum": list(xdd_gate.PHASE_IDS)},
                },
            },
        },
    },
}
