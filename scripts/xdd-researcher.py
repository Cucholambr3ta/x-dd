#!/usr/bin/env python3
"""xdd-researcher — Investigacion autonoma de mejoras para X-DD y el proyecto activo.

Investiga proactivamente fuentes externas (skills Claude Code en GitHub, changelogs de
dependencias, frameworks/metodologias emergentes) y propone mejoras rankeadas por impacto.
Toda propuesta requiere aprobacion humana antes de aplicarse (Constitucion Art. 2).

Sin red por defecto: usa un proveedor de descubrimiento inyectable. El proveedor por
defecto es determinista y offline (fixtures), apto para CI. Un proveedor online real se
puede conectar via --provider o la env var XDD_RESEARCH_PROVIDER (no incluido por defecto
para preservar el principio "sin red en tests").

Comandos:
  run     [--scope system|project] [--topic TOPIC] [--out RESEARCH.md]
  list    [--status proposed|approved|applied|rejected]
  apply   PROPOSAL_ID [--by NAME]

Persistencia: tabla research_proposals de xdd-state.py (best-effort).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
XDD_ROOT = SCRIPTS_DIR.parent
DEFAULT_DB = Path(os.environ.get("XDD_STATE_DB", str(Path.home() / ".xdd" / "state.db")))
DEFAULT_OUT = XDD_ROOT / "RESEARCH.md"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state():
    """Carga xdd-state.py como modulo para reusar record_research_proposal."""
    path = SCRIPTS_DIR / "xdd-state.py"
    spec = importlib.util.spec_from_file_location("xdd_state", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def proposal_id(title: str, source_url: str) -> str:
    h = hashlib.sha256(f"{title}::{source_url}".encode()).hexdigest()[:12]
    return f"rp_{h}"


# --------------------------------------------------------------------------
# Proveedor de descubrimiento (offline/determinista por defecto)
# --------------------------------------------------------------------------

def discover_offline(scope: str, topic: str | None) -> list[dict]:
    """Proveedor offline determinista. Devuelve candidatos de fixtures.

    Reemplaza/extiende con un proveedor online real conectando GitHub API,
    changelogs y arXiv. La firma (scope, topic) -> list[dict] es el contrato.
    Cada dict: title, source_url, source_type, summary, impact_score, compatibility.
    """
    fixtures_path = XDD_ROOT / "tests" / "fixtures" / "research_candidates.json"
    if fixtures_path.exists():
        candidates = json.loads(fixtures_path.read_text(encoding="utf-8"))
    else:
        candidates = _builtin_candidates()

    out = []
    for c in candidates:
        if c.get("scope", "system") != scope:
            continue
        if topic and topic.lower() not in (c.get("topic") or "").lower():
            continue
        out.append(c)
    out.sort(key=lambda c: c.get("impact_score", 0.0), reverse=True)
    return out


def _builtin_candidates() -> list[dict]:
    """Candidatos minimos embebidos para que el comando funcione sin fixtures."""
    return [
        {
            "scope": "system", "topic": "skills",
            "title": "Claude Code skill: structured-output-validator",
            "source_url": "https://github.com/example/cc-structured-output",
            "source_type": "github-skill",
            "summary": "Skill comunitaria que valida salidas estructuradas contra JSON schema.",
            "impact_score": 0.72, "compatibility": "needs-adaptation",
        },
        {
            "scope": "system", "topic": "observability",
            "title": "OpenTelemetry GenAI semantic conventions update",
            "source_url": "https://github.com/open-telemetry/semantic-conventions",
            "source_type": "changelog",
            "summary": "Nuevas convenciones de spans para llamadas LLM; alinear xdd-otel.py.",
            "impact_score": 0.55, "compatibility": "compatible",
        },
    ]


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------

def cmd_run(args) -> int:
    candidates = discover_offline(args.scope, args.topic)
    state = _load_state()

    proposals = []
    for c in candidates:
        pid = proposal_id(c["title"], c["source_url"])
        record = {
            "id": pid,
            "scope": args.scope,
            "topic": c.get("topic"),
            "title": c["title"],
            "source_url": c.get("source_url"),
            "source_type": c.get("source_type"),
            "summary": c.get("summary"),
            "impact_score": c.get("impact_score", 0.0),
            "compatibility": c.get("compatibility"),
        }
        state.record_research_proposal(record, Path(args.db))
        proposals.append(record)

    _write_research_md(proposals, args.scope, args.topic, Path(args.out))

    if args.json:
        print(json.dumps({"ok": True, "count": len(proposals),
                          "out": str(args.out)}, indent=2))
    else:
        print(f"[researcher] {len(proposals)} propuestas (scope={args.scope}"
              f"{', topic=' + args.topic if args.topic else ''}).")
        print(f"[researcher] Reporte: {args.out}")
        print("[researcher] Revisa y aprueba con: xdd-researcher apply <ID>")
    return 0


def cmd_list(args) -> int:
    import sqlite3
    if not Path(args.db).exists():
        print("[researcher] No hay state DB. Ejecuta 'run' primero.")
        return 0
    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    q = "SELECT id, scope, topic, title, impact_score, compatibility, status FROM research_proposals"
    params = []
    if args.status:
        q += " WHERE status = ?"
        params.append(args.status)
    q += " ORDER BY impact_score DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()

    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2))
        return 0
    if not rows:
        print("[researcher] Sin propuestas.")
        return 0
    print(f"[researcher] {len(rows)} propuestas:")
    for r in rows:
        print(f"  [{r['status']:<8}] {r['impact_score']:.2f} {r['id']}  {r['title']}")
        print(f"             scope={r['scope']} compat={r['compatibility']}")
    return 0


def cmd_apply(args) -> int:
    import sqlite3
    if not Path(args.db).exists():
        print("[researcher] No hay state DB.")
        return 1
    conn = sqlite3.connect(str(args.db))
    cur = conn.execute("SELECT id FROM research_proposals WHERE id = ?", (args.id,))
    if not cur.fetchone():
        conn.close()
        print(f"[researcher] Propuesta {args.id} no encontrada.")
        return 1
    conn.execute(
        "UPDATE research_proposals SET status='approved', reviewed_by=?, reviewed_at=? WHERE id=?",
        (args.by or os.environ.get("USER", "human"), utcnow(), args.id),
    )
    conn.commit()
    conn.close()
    print(f"[researcher] Propuesta {args.id} aprobada. "
          f"Implementacion manual queda a cargo del agente/usuario (Art. 2).")
    return 0


def _write_research_md(proposals: list[dict], scope: str, topic: str | None,
                       out: Path) -> None:
    """Genera RESEARCH.md cumpliendo docs/DOC_STANDARD.md (sin emojis, tablas)."""
    lines = [
        "# RESEARCH.md — Propuestas de Mejora (Investigacion Autonoma)",
        "",
        "> Producido por `xdd-researcher`. Cumple `docs/DOC_STANDARD.md`.",
        "> Toda propuesta requiere aprobacion humana antes de aplicarse (Constitucion Art. 2).",
        "",
        f"- Scope: {scope}",
        f"- Topic: {topic or 'todos'}",
        f"- Generado: {utcnow()}",
        f"- Propuestas: {len(proposals)}",
        "",
        "## 1. Propuestas rankeadas por impacto",
        "",
        "| ID | Impacto | Compatibilidad | Tipo | Titulo |",
        "|----|---------|----------------|------|--------|",
    ]
    for p in proposals:
        lines.append(
            f"| {p['id']} | {p['impact_score']:.2f} | {p['compatibility']} "
            f"| {p['source_type']} | {p['title']} |"
        )
    lines += ["", "## 2. Detalle por propuesta", ""]
    for p in proposals:
        lines += [
            f"### {p['id']} — {p['title']}",
            "",
            f"- Fuente: {p['source_url']}",
            f"- Tipo: {p['source_type']}",
            f"- Impacto estimado: {p['impact_score']:.2f}",
            f"- Compatibilidad: {p['compatibility']}",
            f"- Resumen: {p['summary']}",
            "",
        ]
    lines += [
        "## 3. Siguientes pasos",
        "",
        "1. Revisar cada propuesta.",
        "2. Aprobar las relevantes: `xdd-researcher apply <ID>`.",
        "3. El agente implementa solo las propuestas aprobadas.",
        "",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xdd-researcher", description=__doc__)
    p.add_argument("--db", type=Path, default=DEFAULT_DB,
                   help=f"Path SQLite state (default: {DEFAULT_DB})")
    p.add_argument("--json", action="store_true", help="Salida JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Investiga y genera propuestas")
    pr.add_argument("--scope", choices=["system", "project"], default="system")
    pr.add_argument("--topic", default=None, help="Filtra por area (ej: testing)")
    pr.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"Reporte de salida (default: {DEFAULT_OUT})")
    pr.set_defaults(func=cmd_run)

    pl = sub.add_parser("list", help="Lista propuestas persistidas")
    pl.add_argument("--status", choices=["proposed", "approved", "applied", "rejected"])
    pl.set_defaults(func=cmd_list)

    pa = sub.add_parser("apply", help="Aprueba una propuesta")
    pa.add_argument("id", help="ID de la propuesta")
    pa.add_argument("--by", default=None, help="Aprobador")
    pa.set_defaults(func=cmd_apply)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
