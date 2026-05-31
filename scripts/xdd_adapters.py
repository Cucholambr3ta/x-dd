#!/usr/bin/env python3
"""xdd_adapters.py — emisión de formatos IDE nativos desde un SSoT (Branch 3c).

Porta el patrón consolidado de agentix: un Single Source of Truth (lista de
Workflow) emite a 7 targets IDE por COPIA REAL (nunca symlink), cada uno con su
layout y cabecera frontmatter.

ADITIVO: NO reemplaza scripts/xdd-adapt.sh (camino probado, 29 tests bats). Este
módulo es la base Python empaquetable para consolidación futura (v0.2.0) y se
expone como tooling vía el paquete pip.

SSoT: se puede construir a mano (lista de Workflow) o cargar desde un directorio
de workflows markdown con frontmatter (load_ssot_from_dir).

Uso:
  xdd_adapters.py emit --from .agent/workflows --target cursor --dest ./out
  xdd_adapters.py emit-all --from .agent/workflows --dest ./out
  xdd_adapters.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

__version__ = "0.1.0"

TARGETS = [
    "claude-code",
    "opencode",
    "cursor",
    "windsurf",
    "vscode-copilot",
    "antigravity",
    "codex",
]


@dataclass
class Workflow:
    """Unidad del SSoT."""

    name: str
    description: str
    body: str


# Mapa target -> (subdir, plantilla de nombre de archivo).
_LAYOUT: dict[str, tuple[str, str]] = {
    "claude-code": (".claude/commands", "{name}.md"),
    "opencode": (".opencode/command", "{name}.md"),
    "cursor": (".cursor/rules", "{name}.mdc"),
    "windsurf": (".windsurf/rules", "{name}.md"),
    "vscode-copilot": (".github/prompts", "{name}.prompt.md"),
    "antigravity": (".agents/skills", "{name}/SKILL.md"),
    "codex": (".codex/skills", "{name}/SKILL.md"),
}

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _render(target: str, wf: Workflow) -> str:
    """Cabecera específica por target + cuerpo. Sin MCP en ninguna."""
    if target in ("cursor", "windsurf"):
        return f"---\ndescription: {wf.description}\n---\n\n{wf.body}\n"
    if target == "vscode-copilot":
        return f"---\nmode: agent\ndescription: {wf.description}\n---\n\n{wf.body}\n"
    # claude-code, opencode, antigravity, codex
    return f"---\nname: {wf.name}\ndescription: {wf.description}\n---\n\n{wf.body}\n"


def emit(ssot: list[Workflow], target: str, dest: str | Path) -> list[Path]:
    """Emite los workflows del SSoT al formato del target. Copia real, idempotente."""
    if target not in TARGETS:
        raise ValueError(f"target desconocido: {target}. Válidos: {TARGETS}")
    subdir, name_tpl = _LAYOUT[target]
    base = Path(dest) / subdir
    written: list[Path] = []
    for wf in ssot:
        rel = name_tpl.format(name=wf.name)
        out = base / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_render(target, wf))  # copia real, NO symlink
        written.append(out)
    return written


def emit_all(ssot: list[Workflow], dest: str | Path) -> dict[str, list[Path]]:
    """Emite a los 7 targets. Sin MCP, sin .mcp.json."""
    return {t: emit(ssot, t, dest) for t in TARGETS}


def parse_workflow(path: Path) -> Workflow:
    """Construye un Workflow desde un .md con frontmatter (name/description + cuerpo).

    Si no hay frontmatter, usa el nombre de archivo y descripción vacía.
    """
    text = path.read_text(encoding="utf-8")
    name = path.stem
    description = ""
    body = text
    m = _FRONTMATTER.match(text)
    if m:
        front, body = m.group(1), m.group(2).strip()
        for line in front.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                k, v = k.strip(), v.strip()
                if k == "name" and v:
                    name = v
                elif k == "description" and v:
                    description = v
    return Workflow(name=name, description=description, body=body)


def load_ssot_from_dir(src: str | Path) -> list[Workflow]:
    """Carga un SSoT desde un directorio de workflows markdown."""
    base = Path(src)
    if not base.is_dir():
        raise FileNotFoundError(f"directorio de workflows no existe: {base}")
    wfs = [parse_workflow(p) for p in sorted(base.glob("*.md"))]
    return wfs


def cmd_emit(args) -> int:
    ssot = load_ssot_from_dir(args.from_dir)
    if not ssot:
        print(f"[adapters] sin workflows en {args.from_dir}", file=sys.stderr)
        return 1
    if args.target:
        written = emit(ssot, args.target, args.dest)
        print(f"[adapters] {args.target}: {len(written)} archivos → {args.dest}")
    else:
        result = emit_all(ssot, args.dest)
        total = sum(len(v) for v in result.values())
        print(f"[adapters] 7 targets: {total} archivos → {args.dest}")
    return 0


def _self_test() -> int:
    """Verifica render por target + emit determinista, sin tocar disco real."""
    import tempfile

    wf = Workflow(name="demo", description="prueba", body="cuerpo")
    assert "mode: agent" in _render("vscode-copilot", wf)
    assert "name: demo" in _render("claude-code", wf)
    assert "description: prueba" in _render("cursor", wf)
    assert "name:" not in _render("cursor", wf)  # cursor no usa name
    with tempfile.TemporaryDirectory() as d:
        res = emit_all([wf], d)
        assert set(res) == set(TARGETS)
        # cursor produce .mdc, vscode .prompt.md
        assert any(p.suffix == ".mdc" for p in res["cursor"])
        assert any(p.name.endswith(".prompt.md") for p in res["vscode-copilot"])
        # antigravity/codex producen SKILL.md anidado
        assert any(p.name == "SKILL.md" for p in res["antigravity"])
    # ningún render contiene MCP
    for t in TARGETS:
        assert "mcp" not in _render(t, wf).lower()
    print("[adapters] self-test OK — 7 layouts, copia real, sin MCP.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="xdd_adapters", description=__doc__)
    ap.add_argument("--version", action="version", version=f"xdd_adapters {__version__}")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    for cmd in ("emit", "emit-all"):
        p = sub.add_parser(cmd)
        p.add_argument("--from", dest="from_dir", required=True, help="dir de workflows .md")
        p.add_argument("--dest", required=True, help="destino")
        if cmd == "emit":
            p.add_argument("--target", required=True, choices=TARGETS)
        else:
            p.set_defaults(target=None)

    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    if args.cmd in ("emit", "emit-all"):
        return cmd_emit(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
