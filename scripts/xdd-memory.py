#!/usr/bin/env python3
"""xdd-memory — Motor nativo de memoria conversacional para X-DD.

Arquitectura identica a ReMe (agentscope-ai/ReMe, Apache-2.0) pero sin dependencia externa.
Implementado sobre stdlib Python + evol-provider.py (MockProvider | AnthropicProvider).

Estructura de archivos (por proyecto):
  MEMORY.md                      long-term memory: hechos, preferencias, decisiones clave
  memory/YYYY-MM-DD.md           journal diario: resumen estructurado de cada sesion
  dialog/YYYY-MM-DD.jsonl        dialogo raw antes de compactacion (gitignored)
  tool_result/<uuid>.txt         cache de outputs largos de herramientas (TTL auto, gitignored)

Comandos:
  load                           carga MEMORY.md + journal del dia anterior (session:start)
  summarize [--messages FILE]    persiste sesion en memory/YYYY-MM-DD.md (stop hook)
  compact [--messages FILE]      compacta historial largo en summary estructurado
  search QUERY [--max N]         busca en MEMORY.md + journals (BM25 simple, sin embeddings)
  gc [--days N]                  purga tool_result/ vencidos (default 3 dias)
  stats                          estadisticas del sistema de memoria

Activacion: XDD_MEMORY=1 (opt-in). Sin XDD_MEMORY=1, todos los comandos son no-op.
Provider LLM: XDD_PROVIDER=mock|anthropic (default mock — sin red).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────

DEFAULT_COMPACT_THRESHOLD = int(os.environ.get("XDD_MEMORY_COMPACT_THRESHOLD", "90000"))
DEFAULT_COMPACT_RESERVE   = int(os.environ.get("XDD_MEMORY_COMPACT_RESERVE", "10000"))
DEFAULT_LANGUAGE          = os.environ.get("XDD_MEMORY_LANGUAGE", "")
DEFAULT_TOOL_TTL_DAYS     = int(os.environ.get("XDD_MEMORY_TOOL_TTL_DAYS", "3"))
MEMORY_ACTIVE             = os.environ.get("XDD_MEMORY", "0") == "1"


def project_dirs(project: Path) -> dict[str, Path]:
    return {
        "memory_long": project / "MEMORY.md",
        "memory_dir":  project / "memory",
        "dialog_dir":  project / "dialog",
        "tool_dir":    project / "tool_result",
    }


def today_str() -> str:
    return date.today().isoformat()


def yesterday_str() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Token counting (aproximado, sin tiktoken) ─────────────────────────────────

def count_tokens_approx(text: str) -> int:
    """Aproximacion: 1 token ~ 4 chars (conservative estimate)."""
    return max(1, len(text) // 4)


# ── Prompt templates (identicos a ReMe) ──────────────────────────────────────

COMPACT_SYSTEM = """\
You are a context compaction assistant. Your role is to create structured summaries of
conversations that can be used to restore context in future sessions. Focus on preserving
critical information while reducing token count."""

COMPACT_USER = """\
# Task
Create a structured summary from the conversation below.

# Rules
- Keep each section concise
- Preserve exact file paths, function names, and error messages

# Output Format

## Goal
[What is the user trying to accomplish? Multiple items if session covers different tasks.]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned by user]

## Progress
### Done
- [x] [Completed tasks/changes]

### In Progress
- [ ] [Current work]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [Ordered list of what should happen next]

## Critical Context
- [Any data, examples, or references needed to continue]

---

Conversation to summarize:
{conversation}"""

SUMMARIZE_USER = """\
Memory Pre-compression Flush Cycle.

Current date: {date}
Working directory: {working_dir}

# Task
Extract and write persistent memory and session reflections to: {journal_path}

# Principles
- Categorize clearly: separate Factual Memory from Reflections & Logic.
- Avoid duplicating already recorded information.
- Enrich existing entries with new details where relevant.
- Maintain chronological order.
- Reflections MUST focus on reusable cognitive frameworks.
- Keep entries concise yet complete.
- If nothing to store, respond with [SILENT].

# Output structure (write to file):
## Factual Memory
[Objective facts, project states, user profile updates, important events]

## Reflections & Logic
[Reusable strategies, mistakes to avoid, actionable insights for future sessions]

---

Conversation to process:
{conversation}"""


# ── LLM provider (reutiliza evol-provider / xdd-provider si existe) ──────────

def _call_llm(system: str, user: str, project: Path) -> str:
    """Llama al LLM via xdd-provider.py si disponible, sino retorna stub."""
    provider = os.environ.get("XDD_PROVIDER", os.environ.get("EVOL_PROVIDER", "mock"))
    if provider == "mock":
        # Mock determinista para tests/CI
        return _mock_response(user)

    # Intentar importar xdd-provider o evol-provider
    scripts = Path(__file__).parent
    for name in ("xdd-provider.py", "evol-provider.py"):
        prov_path = scripts / name
        if prov_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("_provider", prov_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            try:
                return mod.AnthropicProvider().complete(system=system, user=user)
            except Exception as e:
                print(f"[xdd-memory] WARN: provider error ({e}), usando mock.", file=sys.stderr)
                return _mock_response(user)
    return _mock_response(user)


def _mock_response(prompt: str) -> str:
    """Respuesta mock estructurada (determinista, sin red)."""
    return """\
## Goal
[Mock: session goals not extracted — enable XDD_PROVIDER=anthropic for real summaries]

## Progress
### Done
- [x] Session completed

## Key Decisions
- **Mock mode**: Real summarization requires XDD_PROVIDER=anthropic + ANTHROPIC_API_KEY

## Next Steps
1. Set XDD_PROVIDER=anthropic to enable real memory summarization

## Critical Context
- (none)"""


# ── Tool result cache ─────────────────────────────────────────────────────────

def save_tool_result(project: Path, content: str, tool_name: str = "") -> str:
    """Guarda output largo de herramienta. Retorna UUID referencia."""
    dirs = project_dirs(project)
    dirs["tool_dir"].mkdir(parents=True, exist_ok=True)
    uid = hashlib.sha256(f"{tool_name}:{content}:{utcnow()}".encode()).hexdigest()[:16]
    f = dirs["tool_dir"] / f"{uid}.txt"
    f.write_text(content, encoding="utf-8")
    return uid


def compact_tool_result(content: str, keep_chars: int = 2000) -> tuple[str, str | None]:
    """Si content > keep_chars, guarda en tool_result/ y retorna referencia.

    Returns: (content_or_ref, uid_or_None)
    """
    if len(content) <= keep_chars:
        return content, None
    # No tenemos project aqui — caller debe gestionar
    return content[:keep_chars] + "\n[...truncado — ver tool_result/<uid>.txt]", None


# ── BM25-simple search (sin dependencias) ────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def bm25_search(query: str, docs: list[tuple[str, str]], max_results: int = 5,
                k1: float = 1.5, b: float = 0.75) -> list[tuple[str, str, float]]:
    """BM25 simple sobre lista de (path, text). Retorna [(path, snippet, score)]."""
    if not docs:
        return []
    q_terms = _tokenize(query)
    N = len(docs)
    import math

    # doc freq
    df: dict[str, int] = {}
    tokenized = []
    for _, text in docs:
        toks = _tokenize(text)
        tokenized.append(toks)
        for t in set(toks):
            df[t] = df.get(t, 0) + 1

    avg_dl = sum(len(t) for t in tokenized) / max(N, 1)
    results = []
    for i, (path, text) in enumerate(docs):
        toks = tokenized[i]
        dl = len(toks)
        score = 0.0
        tf_map: dict[str, int] = {}
        for t in toks:
            tf_map[t] = tf_map.get(t, 0) + 1
        for term in q_terms:
            if term not in df:
                continue
            idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)
            tf = tf_map.get(term, 0)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            score += idf * tf_norm
        if score > 0:
            # snippet: primera linea con algún term del query
            snippet = ""
            for line in text.splitlines():
                if any(t in line.lower() for t in q_terms):
                    snippet = line.strip()[:200]
                    break
            results.append((path, snippet or text[:200], score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:max_results]


# ── Comandos ──────────────────────────────────────────────────────────────────

def cmd_load(args) -> int:
    """Session:start — carga MEMORY.md + journal del dia anterior."""
    if not MEMORY_ACTIVE:
        return 0
    project = Path(args.project)
    dirs = project_dirs(project)
    today = today_str()
    yesterday = yesterday_str()

    print(f"[xdd-memory] Cargando memoria conversacional para {project.name}...")

    mem_long = dirs["memory_long"]
    if mem_long.exists():
        lines = mem_long.read_text(encoding="utf-8").splitlines()
        print(f"[xdd-memory] MEMORY.md cargado ({len(lines)} lineas — long-term memory).")
    else:
        print("[xdd-memory] MEMORY.md no existe — se creara al cerrar la primera sesion.")

    journal_dir = dirs["memory_dir"]
    journal_yesterday = journal_dir / f"{yesterday}.md"
    if journal_yesterday.exists():
        print(f"[xdd-memory] Journal de ayer ({yesterday}) disponible en memory/{yesterday}.md")

    journal_today = journal_dir / f"{today}.md"
    if journal_today.exists():
        print(f"[xdd-memory] Journal de hoy ({today}) ya existe — sesion continuada.")

    if args.json:
        out = {
            "ok": True,
            "memory_long_exists": mem_long.exists(),
            "journal_yesterday": journal_yesterday.exists(),
            "journal_today": journal_today.exists(),
        }
        print(json.dumps(out))
    return 0


def cmd_summarize(args) -> int:
    """Stop hook — persiste sesion en memory/YYYY-MM-DD.md."""
    if not MEMORY_ACTIVE:
        return 0
    project = Path(args.project)
    dirs = project_dirs(project)
    today = today_str()

    dirs["memory_dir"].mkdir(parents=True, exist_ok=True)
    journal_path = dirs["memory_dir"] / f"{today}.md"

    # Cargar messages si se proveen
    conversation = ""
    if args.messages and Path(args.messages).exists():
        raw = Path(args.messages).read_text(encoding="utf-8")
        try:
            msgs = json.loads(raw)
            parts = []
            for m in msgs:
                role = m.get("role", "?")
                content = m.get("content", "")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                parts.append(f"{role.upper()}: {content}")
            conversation = "\n\n".join(parts)
        except (json.JSONDecodeError, TypeError):
            conversation = raw
    else:
        conversation = "(no messages provided — stub entry)"

    tokens = count_tokens_approx(conversation)
    print(f"[xdd-memory] Summarizando sesion ({tokens} tokens aprox)...")

    prompt = SUMMARIZE_USER.format(
        date=today,
        working_dir=str(project),
        journal_path=str(journal_path),
        conversation=conversation[:20000],  # cap para no exceder contexto del LLM
    )
    summary = _call_llm("", prompt, project)

    if summary.strip() == "[SILENT]":
        print("[xdd-memory] Sesion sin contenido relevante — journal omitido.")
        return 0

    # Escribir / merge en journal del dia
    if journal_path.exists():
        existing = journal_path.read_text(encoding="utf-8")
        journal_path.write_text(
            existing + f"\n\n---\n\n## Sesion {utcnow()[:19]}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"[xdd-memory] Journal actualizado: memory/{today}.md")
    else:
        journal_path.write_text(
            f"# Journal {today}\n\n## Sesion {utcnow()[:19]}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"[xdd-memory] Journal creado: memory/{today}.md")

    if args.json:
        print(json.dumps({"ok": True, "journal": str(journal_path)}))
    return 0


def cmd_compact(args) -> int:
    """Compacta historial largo en summary estructurado."""
    if not MEMORY_ACTIVE:
        return 0
    project = Path(args.project)

    conversation = ""
    if args.messages and Path(args.messages).exists():
        raw = Path(args.messages).read_text(encoding="utf-8")
        try:
            msgs = json.loads(raw)
            parts = []
            for m in msgs:
                role = m.get("role", "?")
                content = m.get("content", "")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                parts.append(f"{role.upper()}: {content}")
            conversation = "\n\n".join(parts)
        except (json.JSONDecodeError, TypeError):
            conversation = raw
    else:
        print("[xdd-memory] compact: --messages FILE requerido.", file=sys.stderr)
        return 1

    tokens = count_tokens_approx(conversation)
    if tokens < args.threshold:
        print(f"[xdd-memory] Contexto OK ({tokens} tokens < {args.threshold}). No se compacta.")
        if args.json:
            print(json.dumps({"ok": True, "compacted": False, "tokens": tokens}))
        return 0

    print(f"[xdd-memory] Compactando {tokens} tokens (threshold={args.threshold})...")
    prompt = COMPACT_USER.format(conversation=conversation[:20000])
    summary = _call_llm(COMPACT_SYSTEM, prompt, project)

    if args.output:
        Path(args.output).write_text(summary, encoding="utf-8")
        print(f"[xdd-memory] Summary escrito en: {args.output}")
    else:
        print(summary)

    if args.json:
        print(json.dumps({"ok": True, "compacted": True, "tokens_before": tokens, "summary_tokens": count_tokens_approx(summary)}))
    return 0


def cmd_search(args) -> int:
    """Busca en MEMORY.md + journals con BM25 simple."""
    project = Path(args.project)
    dirs = project_dirs(project)
    query = " ".join(args.query)

    docs: list[tuple[str, str]] = []
    if dirs["memory_long"].exists():
        docs.append(("MEMORY.md", dirs["memory_long"].read_text(encoding="utf-8")))

    if dirs["memory_dir"].is_dir():
        for jf in sorted(dirs["memory_dir"].glob("*.md"), reverse=True)[:30]:
            docs.append((f"memory/{jf.name}", jf.read_text(encoding="utf-8")))

    if not docs:
        print("[xdd-memory] Sin documentos de memoria. Ejecuta summarize primero.")
        return 0

    results = bm25_search(query, docs, max_results=args.max)
    if not results:
        print(f"[xdd-memory] Sin resultados para: {query}")
        return 0

    if args.json:
        print(json.dumps([{"path": p, "snippet": s, "score": round(sc, 3)} for p, s, sc in results]))
        return 0

    print(f"[xdd-memory] {len(results)} resultado(s) para '{query}':")
    for path, snippet, score in results:
        print(f"  [{score:.2f}] {path}: {snippet}")
    return 0


def cmd_gc(args) -> int:
    """Purga tool_result/ vencidos."""
    project = Path(args.project)
    dirs = project_dirs(project)
    tool_dir = dirs["tool_dir"]
    if not tool_dir.is_dir():
        print("[xdd-memory] gc: tool_result/ no existe. Nada que limpiar.")
        return 0

    cutoff = datetime.now() - timedelta(days=args.days)
    removed = []
    for f in tool_dir.glob("*.txt"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            f.unlink()
            removed.append(f.name)

    print(f"[xdd-memory] gc: {len(removed)} archivo(s) eliminados (TTL={args.days}d).")
    if args.json:
        print(json.dumps({"ok": True, "removed": removed}))
    return 0


def cmd_stats(args) -> int:
    """Estadisticas del sistema de memoria."""
    project = Path(args.project)
    dirs = project_dirs(project)

    mem_size = dirs["memory_long"].stat().st_size if dirs["memory_long"].exists() else 0
    journals = list(dirs["memory_dir"].glob("*.md")) if dirs["memory_dir"].is_dir() else []
    dialogs = list(dirs["dialog_dir"].glob("*.jsonl")) if dirs["dialog_dir"].is_dir() else []
    tools = list(dirs["tool_dir"].glob("*.txt")) if dirs["tool_dir"].is_dir() else []

    data: dict[str, Any] = {
        "active": MEMORY_ACTIVE,
        "provider": os.environ.get("XDD_PROVIDER", "mock"),
        "memory_long_kb": round(mem_size / 1024, 1),
        "journals": len(journals),
        "dialogs": len(dialogs),
        "tool_results": len(tools),
        "latest_journal": max((j.name for j in journals), default=None),
    }

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    print(f"[xdd-memory] Estado del sistema de memoria:")
    print(f"  Activo:         {'SI' if data['active'] else 'NO (XDD_MEMORY=1 para activar)'}")
    print(f"  Provider LLM:   {data['provider']}")
    print(f"  MEMORY.md:      {data['memory_long_kb']} KB")
    print(f"  Journals:       {data['journals']} archivos en memory/")
    print(f"  Dialogs raw:    {data['dialogs']} archivos en dialog/")
    print(f"  Tool results:   {data['tool_results']} archivos en tool_result/")
    if data['latest_journal']:
        print(f"  Ultimo journal: memory/{data['latest_journal']}")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xdd-memory", description=__doc__)
    p.add_argument("--project", default=os.getcwd(), help="Directorio del proyecto (default: $PWD)")
    p.add_argument("--json", action="store_true", help="Salida JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    # load
    sub.add_parser("load", help="Carga MEMORY.md + journal anterior (session:start)")

    # summarize
    ps = sub.add_parser("summarize", help="Persiste sesion en memory/YYYY-MM-DD.md (stop hook)")
    ps.add_argument("--messages", default=None, help="Archivo JSONL con mensajes de la sesion")

    # compact
    pc = sub.add_parser("compact", help="Compacta historial largo en summary estructurado")
    pc.add_argument("--messages", required=True, help="Archivo JSONL con mensajes")
    pc.add_argument("--threshold", type=int, default=DEFAULT_COMPACT_THRESHOLD)
    pc.add_argument("--output", default=None, help="Archivo de salida del summary")

    # search
    pq = sub.add_parser("search", help="Busca en MEMORY.md + journals (BM25)")
    pq.add_argument("query", nargs="+", help="Terminos de busqueda")
    pq.add_argument("--max", type=int, default=5, help="Maximo de resultados")

    # gc
    pg = sub.add_parser("gc", help="Purga tool_result/ vencidos")
    pg.add_argument("--days", type=int, default=DEFAULT_TOOL_TTL_DAYS, help="TTL en dias")

    # stats
    sub.add_parser("stats", help="Estadisticas del sistema de memoria")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    dispatch = {
        "load": cmd_load,
        "summarize": cmd_summarize,
        "compact": cmd_compact,
        "search": cmd_search,
        "gc": cmd_gc,
        "stats": cmd_stats,
    }
    fn = dispatch.get(args.cmd)
    if fn is None:
        print(f"[xdd-memory] subcomando desconocido: {args.cmd}", file=sys.stderr)
        return 2
    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
