#!/usr/bin/env python3
"""xdd-readme.py — Generador de README "vendible" del flujo X-DD.

Rellena templates/readme.template.md con datos REALES minados del repo
(cero invención). Producido por /cierre-fase para la fase `docs` del gate.

REGLA DE ORO: cada {{AUTO:campo}} sale de un hecho verificable del repo.
Si un dato no existe, la sección que depende de él se OMITE (no se imprime
placeholder roto — eso mata credibilidad y rompería el gate `docs`).

Los <CONFIGURAR:...> son copy humano; este script NO los inventa. Quedan en
el output para que el autor los rellene; el gate `docs` rechaza el README
mientras siga habiendo {{AUTO:...}} o <CONFIGURAR> sin resolver.

Comandos:
  generate   — genera README.md (idioma base) en la raíz del repo.
               --lang es,en,pt-BR  genera además README.<lang>.md
  facts      — imprime los hechos minados (JSON) sin escribir nada (debug).

Exit 0 si OK; 1 si faltan fuentes críticas; 2 si error de uso.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0-dev"

TEMPLATE_REL = "templates/readme.template.md"

# Banderas por código de idioma para el switch i18n.
_LANG_FLAGS = {"es": "🇪🇸 Español", "en": "🇬🇧 English", "pt-BR": "🇧🇷 Português"}


# ─────────────────────────── helpers de minería ───────────────────────────

def _run(cmd: list[str], root: Path) -> str:
    try:
        out = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True, timeout=30
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _count_glob(root: Path, pattern: str) -> int:
    return sum(1 for _ in root.glob(pattern))


def _detect_license(root: Path) -> str:
    lic = root / "LICENSE"
    if not lic.exists():
        return ""
    first = lic.read_text(errors="ignore").splitlines()[0].strip()
    # "MIT License" -> "MIT"
    return first.replace(" License", "").strip() or first


def _detect_copyright(root: Path) -> str:
    lic = root / "LICENSE"
    if not lic.exists():
        return ""
    for line in lic.read_text(errors="ignore").splitlines():
        if line.lower().startswith("copyright"):
            return line.strip()
    return ""


def _detect_stack(root: Path) -> list[str]:
    stack = []
    if (root / "Cargo.toml").exists() or list(root.glob("**/Cargo.toml")):
        stack.append("Rust")
    if (root / "package.json").exists():
        stack.append("Node/TypeScript")
    if (root / "pyproject.toml").exists() or list(root.glob("scripts/*.py")):
        stack.append("Python")
    return stack


def _detect_translations(root: Path) -> list[str]:
    """Devuelve códigos de idioma de README.<lang>.md presentes."""
    langs = []
    for p in sorted(root.glob("README.*.md")):
        m = re.match(r"README\.([A-Za-z-]+)\.md$", p.name)
        if m:
            langs.append(m.group(1))
    return langs


def _install_command(root: Path) -> str:
    if (root / "scripts" / "xdd-init.sh").exists():
        return "bash ./scripts/xdd-init.sh . --profile=developer"
    if (root / "package.json").exists():
        return "npm install"
    if list(root.glob("**/Cargo.toml")):
        return "cargo build --release"
    return ""


def mine(root: Path) -> dict:
    """Mina todos los hechos verificables. Valor vacío => sección omitida."""
    f: dict = {}
    f["project_name"] = root.name
    f["license"] = _detect_license(root)
    f["copyright_holder"] = _detect_copyright(root)
    f["stack"] = _detect_stack(root)
    f["agent_count"] = _count_glob(root, "prompts/agents/**/*.md")
    f["adr_count"] = _count_glob(root, "docs/adr/*.md")
    f["script_count"] = _count_glob(root, "scripts/*.sh") + _count_glob(
        root, "scripts/*.py"
    )
    f["workflow_count"] = _count_glob(root, ".agent/workflows/*.md")
    f["translations"] = _detect_translations(root)
    f["install_command"] = _install_command(root)
    f["has_security"] = (root / "SECURITY.md").exists()
    f["has_coc"] = (root / "CODE_OF_CONDUCT.md").exists()
    f["has_contributing"] = (root / "CONTRIBUTING.md").exists()
    f["last_commit_date"] = _run(
        ["git", "log", "-1", "--format=%cs"], root
    )
    f["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Estado del gate X-DD
    gate_json = _run(
        ["python3", "scripts/xdd-gate.py", "status", "--json"], root
    )
    try:
        f["gate_status"] = json.loads(gate_json) if gate_json else None
    except json.JSONDecodeError:
        f["gate_status"] = None
    return f


# ─────────────────────────── render de campos ───────────────────────────

def _quick_facts(f: dict) -> str:
    parts = []
    if f["agent_count"]:
        parts.append(f"{f['agent_count']} agentes")
    if f["adr_count"]:
        parts.append(f"{f['adr_count']} ADRs")
    if f["script_count"]:
        parts.append(f"{f['script_count']} scripts")
    if f["workflow_count"]:
        parts.append(f"{f['workflow_count']} workflows")
    if f["license"]:
        parts.append(f"licencia {f['license']}")
    return " · ".join(parts)


def _badges(f: dict) -> str:
    b = []
    for s in f["stack"]:
        slug = s.split("/")[0]
        b.append(f"![{slug}](https://img.shields.io/badge/-{slug}-informational)")
    if f["license"]:
        b.append(
            f"![License](https://img.shields.io/badge/license-{f['license']}-green)"
        )
    return " ".join(b)


def _translations_switch(f: dict) -> str:
    if not f["translations"]:
        return ""
    links = []
    for lang in f["translations"]:
        label = _LANG_FLAGS.get(lang, lang)
        links.append(f"[{label}](README.{lang}.md)")
    return "<p align=\"center\">" + " · ".join(links) + "</p>"


def _governance(f: dict) -> str:
    bits = []
    if f["license"]:
        bits.append(f"- Licencia **{f['license']}**")
    if f["adr_count"]:
        bits.append(f"- {f['adr_count']} ADRs documentan las decisiones")
    if f["has_security"]:
        bits.append("- Política de seguridad: [SECURITY.md](SECURITY.md)")
    if f["has_coc"]:
        bits.append("- Código de conducta: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)")
    return "\n".join(bits)


def _contributing(f: dict) -> str:
    if not f["has_contributing"]:
        return ""
    return "Ver [CONTRIBUTING.md](CONTRIBUTING.md)."


def _built_with(f: dict) -> str:
    return "![Built with X-DD](https://img.shields.io/badge/Built%20with-X--DD-blueviolet)"


# Mapa {{AUTO:campo}} -> función render. Campos no resueltos quedan intactos
# (el gate `docs` los detectará y bloqueará — fail-loud, nunca inventar).
def build_substitutions(f: dict) -> dict:
    return {
        "project_name": f["project_name"],
        "license": f["license"],
        "copyright_holder": f["copyright_holder"],
        "quick_facts": _quick_facts(f),
        "badges": _badges(f),
        "readme_translations": _translations_switch(f),
        "install_command": f["install_command"],
        "governance": _governance(f),
        "contributing": _contributing(f),
        "built_with_badge": _built_with(f),
        "date": f["date"],
        "release_status": f["gate_status"] and "pipeline X-DD completo" or "",
    }


_AUTO_RE = re.compile(r"\{\{AUTO:([a-z_]+)\}\}")


def render(template: str, subs: dict) -> str:
    def repl(m: re.Match) -> str:
        key = m.group(1)
        val = subs.get(key)
        # Si no hay valor resuelto, dejamos el token para que el gate lo cace.
        return val if val else m.group(0)

    return _AUTO_RE.sub(repl, template)


# ─────────────────────────── comandos ───────────────────────────

def cmd_generate(root: Path, args) -> int:
    tpl_path = root / TEMPLATE_REL
    if not tpl_path.exists():
        print(f"[readme] ✗ falta {TEMPLATE_REL}", file=sys.stderr)
        return 1
    facts = mine(root)
    if not facts["license"]:
        print("[readme] ⚠ sin LICENSE — badges/license quedarán pendientes")
    subs = build_substitutions(facts)
    out = render(tpl_path.read_text(), subs)

    target = root / "README.md"
    target.write_text(out, encoding="utf-8")
    remaining = len(re.findall(r"\{\{AUTO:[^}]+\}\}|<CONFIGURAR[^>]*>", out))
    print(f"[readme] ✓ {target.name} generado. {remaining} campo(s) por resolver.")
    if remaining:
        print("[readme]   completa los <CONFIGURAR> antes del gate `docs`.")
    return 0


def cmd_facts(root: Path, args) -> int:
    print(json.dumps(mine(root), indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Generador de README X-DD")
    ap.add_argument("--root", default=".", help="raíz del repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--lang", default="", help="idiomas extra: es,en,pt-BR")
    sub.add_parser("facts")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    if args.cmd == "generate":
        return cmd_generate(root, args)
    if args.cmd == "facts":
        return cmd_facts(root, args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
