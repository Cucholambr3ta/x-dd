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

# Rutas globales por defecto (instalación central X-DD = ROOT del paquete instalado).
# Sprint 25 + ADR-0035: resolver local-first → fallback global, soporta global install.
GLOBAL_WORKFLOWS_DIR = ROOT / ".agent" / "workflows"
GLOBAL_REGISTRY_PATH = ROOT / "prompts" / "agents" / "registry.json"

# Whitelist de paths que xdd_get_phase_artifacts puede devolver (T4.3 mitigación).
ALLOWED_ARTIFACT_PREFIXES = (".xdd/",)


def _resolve_project_root(project_root: str | None = None) -> Path:
    """Resuelve project_root: arg explícito > cwd actual del proceso (IDE workspace)."""
    return Path(project_root or os.getcwd()).resolve()


def get_workflows_dir(project_root: str | None = None) -> Path:
    """Local `.agent/workflows/` si existe en project, sino global X-DD ROOT."""
    root = _resolve_project_root(project_root)
    local_dir = root / ".agent" / "workflows"
    if local_dir.exists():
        return local_dir
    return GLOBAL_WORKFLOWS_DIR


def get_registry_path(project_root: str | None = None) -> Path:
    """Local `prompts/agents/registry.json` si existe, sino global."""
    root = _resolve_project_root(project_root)
    local_path = root / "prompts" / "agents" / "registry.json"
    if local_path.exists():
        return local_path
    return GLOBAL_REGISTRY_PATH


def get_xdd_dir(project_root: str | None = None) -> Path:
    """Phase artifacts ESTRICTAMENTE en CWD del proyecto. Sin fallback global
    (aislamiento por subproyecto, ADR-0035)."""
    root = _resolve_project_root(project_root)
    return root / ".xdd"


# Backwards compat: alias retiene API previa para tests/imports externos.
WORKFLOWS_DIR = GLOBAL_WORKFLOWS_DIR
REGISTRY_PATH = GLOBAL_REGISTRY_PATH
XDD_DIR = GLOBAL_WORKFLOWS_DIR.parent.parent / ".xdd"


# ---------- Tool: xdd_validate_phase ----------
def xdd_validate_phase(phase: str, project_root: str | None = None) -> dict:
    root = _resolve_project_root(project_root)
    ok, errs = xdd_gate._validate_phase(root, phase)
    return {"phase": phase, "ok": ok, "errors": errs}


# ---------- Tool: xdd_transition_phase ----------
def xdd_transition_phase(from_phase: str, to_phase: str,
                          project_root: str | None = None) -> dict:
    root = _resolve_project_root(project_root)
    phases = xdd_gate.PHASE_IDS
    if from_phase not in phases or to_phase not in phases:
        return {"ok": False, "error": f"Fase desconocida ({from_phase} → {to_phase})"}
    if phases.index(to_phase) != phases.index(from_phase) + 1:
        return {"ok": False, "error": f"Transición no secuencial: {from_phase} → {to_phase}"}
    ok, errs = xdd_gate._validate_phase(root, from_phase)
    return {"from": from_phase, "to": to_phase, "ok": ok, "errors": errs}


# ---------- Tool: xdd_list_workflows ----------
def xdd_list_workflows(project_root: str | None = None) -> dict:
    """Lista los workflows .agent/workflows/*.md con su frontmatter `description:`.
    Sprint 25: local-first (project_root) + global fallback."""
    wf_dir = get_workflows_dir(project_root)
    if not wf_dir.exists():
        return {"workflows": [], "count": 0, "source": str(wf_dir)}
    workflows = []
    for f in sorted(wf_dir.glob("*.md")):
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
            "path": str(f.as_posix()),
        })
    return {"workflows": workflows, "count": len(workflows),
            "source": str(wf_dir), "is_local": wf_dir != GLOBAL_WORKFLOWS_DIR}


# ---------- Tool: xdd_invoke_workflow ----------
def xdd_invoke_workflow(name: str, _args: list[str] | None = None,
                         project_root: str | None = None) -> dict:
    """Devuelve el contenido del workflow para que el orquestador lo ejecute.

    NO ejecuta nada por su cuenta — MCP server propio no tiene 'execute_shell'
    (T6.3 mitigación). Sprint 25: local-first + global fallback.
    """
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    if safe_name != name:
        return {"ok": False, "error": "Nombre de workflow inválido."}
    wf_dir = get_workflows_dir(project_root)
    wf = wf_dir / f"{safe_name}.md"
    if not wf.exists() or not wf.resolve().is_relative_to(wf_dir.resolve()):
        return {"ok": False, "error": f"Workflow {safe_name!r} no encontrado.",
                "searched": str(wf_dir)}
    return {
        "ok": True,
        "name": safe_name,
        "path": str(wf.as_posix()),
        "source": str(wf_dir),
        "is_local": wf_dir != GLOBAL_WORKFLOWS_DIR,
        "content": wf.read_text(encoding="utf-8"),
        "note": "Este server NO ejecuta el workflow — devuelve el .md para que tu "
                "orquestador (Claude Code / OpenCode / etc.) lo interprete.",
    }


# ---------- Tool: xdd_list_agents ----------
def xdd_list_agents(category: str | None = None,
                     project_root: str | None = None) -> dict:
    """Sprint 25: local-first registry + global fallback."""
    reg_path = get_registry_path(project_root)
    if not reg_path.exists():
        return {"ok": False, "error": "registry.json no existe. Corré scripts/migrate-agents-to-registry.py"}
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    agents = data.get("agents", [])
    if category:
        agents = [a for a in agents if a.get("category") == category]
    return {
        "ok": True,
        "count": len(agents),
        "source": str(reg_path),
        "is_local": reg_path != GLOBAL_REGISTRY_PATH,
        "agents": [{
            "id": a["id"],
            "name": a["name"],
            "category": a["category"],
            "description": a.get("description", ""),
            "prompt_file": a["prompt_file"],
        } for a in agents],
    }


# ---------- Tool: xdd_get_phase_artifacts ----------
def xdd_get_phase_artifacts(phase: str, project_root: str | None = None) -> dict:
    """Lista artefactos en .xdd/<fase>/ del project_root (CWD). NO fallback global
    — phase artifacts STRICTAMENTE per-project (ADR-0035 + T4.3)."""
    if phase not in xdd_gate.PHASE_IDS:
        return {"ok": False, "error": f"Fase desconocida: {phase}"}
    root = _resolve_project_root(project_root)
    xdd_dir = get_xdd_dir(project_root)
    pdir = xdd_dir / phase
    if not pdir.exists():
        return {"ok": True, "phase": phase, "exists": False, "artifacts": [],
                "project_root": str(root)}

    artifacts = []
    for f in sorted(pdir.rglob("*")):
        if f.is_file():
            try:
                rel = str(f.relative_to(root).as_posix())
            except ValueError:
                continue
            if not any(rel.startswith(p) for p in ALLOWED_ARTIFACT_PREFIXES):
                continue
            artifacts.append({"path": rel, "size": f.stat().st_size})

    status_file = pdir / ".status"
    status = status_file.read_text().strip() if status_file.exists() else None
    return {
        "ok": True,
        "phase": phase,
        "exists": True,
        "status": status,
        "artifacts": artifacts,
        "project_root": str(root),
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
            "description": "Lista workflows X-DD. Local-first (project_root) + global fallback.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_root": {"type": "string", "description": "Default: cwd del proceso (workspace IDE)."},
                },
            },
        },
    },
    "xdd_invoke_workflow": {
        "fn": xdd_invoke_workflow,
        "schema": {
            "name": "xdd_invoke_workflow",
            "description": "Devuelve contenido workflow para que orquestador lo interprete. Local-first + global fallback.",
            "inputSchema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "description": "Nombre workflow (sin .md), alfanumérico+guion."},
                    "project_root": {"type": "string", "description": "Default: cwd del proceso."},
                },
            },
        },
    },
    "xdd_list_agents": {
        "fn": xdd_list_agents,
        "schema": {
            "name": "xdd_list_agents",
            "description": "Lista agentes del registry. Filtrable por categoría. Local-first + global fallback.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filtra por categoría (ej. engineering, security)."},
                    "project_root": {"type": "string"},
                },
            },
        },
    },
    "xdd_get_phase_artifacts": {
        "fn": xdd_get_phase_artifacts,
        "schema": {
            "name": "xdd_get_phase_artifacts",
            "description": "Lista artefactos .xdd/<fase>/ del project_root. ESTRICTAMENTE per-project (sin fallback global).",
            "inputSchema": {
                "type": "object",
                "required": ["phase"],
                "properties": {
                    "phase": {"type": "string", "enum": list(xdd_gate.PHASE_IDS)},
                    "project_root": {"type": "string", "description": "Default: cwd del proceso."},
                },
            },
        },
    },
}
