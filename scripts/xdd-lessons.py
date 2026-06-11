#!/usr/bin/env python3
"""xdd-lessons — Motor nativo de gestion de lecciones aprendidas para X-DD.

Administra lecciones.md con la misma filosofia que xdd-memory.py administra
la memoria conversacional: estructura fija, busqueda BM25, deduplicacion,
deteccion de lecciones relevantes, extraccion automatica, ciclo de mejora continua.

Estructura de una leccion (formato canonical extendido):
  ### [CATEGORIA] Titulo breve — YYYY-MM-DD
  **Contexto:** Que estabamos intentando hacer.
  **Problema:** Que fallo o sorprendio.
  **Causa raiz:** Por que paso.
  **Leccion:** Regla aplicable a futuras decisiones.
  **Aplica a:** Ambito (modulo X, todo el proyecto, stack Y...).
  **Fix aplicado:** Que se hizo para resolver el problema (opcional).
  **Mejoras sugeridas:** Propuestas del investigador para evolucion futura (opcional).
  **Estado mejoras:** pendiente | en-progreso | aplicado (opcional).

Categorias: ARQUITECTURA, SEGURIDAD, DOMINIO, TESTING, DEVOPS, PROCESO, HERRAMIENTAS.

Comandos:
  add       Añade leccion nueva. Deduplicacion automatica por similitud titulo+leccion.
  suggest-fix LECCION_TITULO  El agente investigador propone mejoras para esa leccion.
  apply-fix LECCION_TITULO    Marca mejoras como aplicadas + registra que se implemento.
  search    QUERY [--max N] [--categoria CAT]  BM25 sobre lecciones.
  suggest   QUERY [--max N]  Lecciones relevantes formateadas para contexto del agente.
  extract   --messages FILE  Extrae lecciones candidatas desde sesion JSONL.
  list      [--categoria CAT] [--pendientes]  Lista lecciones.
  stats     Estadisticas: total, por categoria, mejoras pendientes.
  gc        Elimina duplicados exactos.

Provider LLM para suggest-fix/extract: XDD_PROVIDER=mock|anthropic (default mock).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

CATEGORIES = {
    "ARQUITECTURA", "SEGURIDAD", "DOMINIO", "TESTING",
    "DEVOPS", "PROCESO", "HERRAMIENTAS",
}

LESSONS_FILE = "lecciones.md"

LESSON_HEADER = re.compile(
    r"^### \[([A-ZÁÉÍÓÚÑ]+)\] (.+?) — (\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)

FIELD_RE = {
    "contexto":           re.compile(r"\*\*Contexto:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "problema":           re.compile(r"\*\*Problema:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "causa":              re.compile(r"\*\*Causa raz[oó]n?:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "leccion":            re.compile(r"\*\*Lecci[oó]n:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "aplica":             re.compile(r"\*\*Aplica a:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "fix_aplicado":       re.compile(r"\*\*Fix aplicado:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "mejoras_sugeridas":  re.compile(r"\*\*Mejoras sugeridas:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
    "estado_mejoras":     re.compile(r"\*\*Estado mejoras:\*\*\s*(.+?)(?=\n\*\*|\Z)", re.S),
}


# ── Utilidades ────────────────────────────────────────────────────────────────

def today_str() -> str:
    return date.today().isoformat()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def lessons_path(project: Path) -> Path:
    return project / LESSONS_FILE


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def _similarity(a: str, b: str) -> float:
    ta, tb = set(_tokenize(a)), set(_tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_lessons(text: str) -> list[dict]:
    lessons = []
    parts = LESSON_HEADER.split(text)
    i = 1
    while i + 3 < len(parts):
        cat, title, dt, body = parts[i], parts[i+1], parts[i+2], parts[i+3]
        lesson: dict[str, Any] = {
            "categoria": cat.strip(),
            "titulo": title.strip(),
            "fecha": dt.strip(),
            "raw": body.strip(),
        }
        for field, rx in FIELD_RE.items():
            m = rx.search(body)
            lesson[field] = m.group(1).strip() if m else ""
        lessons.append(lesson)
        i += 4
    return lessons


def lesson_to_markdown(lesson: dict) -> str:
    lines = [
        f"\n### [{lesson['categoria']}] {lesson['titulo']} — {lesson['fecha']}",
        f"**Contexto:** {lesson['contexto']}",
        f"**Problema:** {lesson['problema']}",
        f"**Causa raiz:** {lesson['causa']}",
        f"**Leccion:** {lesson['leccion']}",
        f"**Aplica a:** {lesson['aplica']}",
    ]
    if lesson.get("fix_aplicado"):
        lines.append(f"**Fix aplicado:** {lesson['fix_aplicado']}")
    if lesson.get("mejoras_sugeridas"):
        lines.append(f"**Mejoras sugeridas:** {lesson['mejoras_sugeridas']}")
    if lesson.get("estado_mejoras"):
        lines.append(f"**Estado mejoras:** {lesson['estado_mejoras']}")
    return "\n".join(lines) + "\n"


def _rewrite_lessons(lpath: Path, lessons: list[dict]) -> None:
    """Reescribe lecciones.md preservando el header del archivo."""
    text = lpath.read_text(encoding="utf-8")
    header_end = text.find("## Lecciones")
    if header_end == -1:
        prefix = text[:200]
    else:
        prefix = text[:header_end + len("## Lecciones\n")]
    lpath.write_text(prefix + "".join(lesson_to_markdown(l) for l in lessons), encoding="utf-8")


# ── BM25 ─────────────────────────────────────────────────────────────────────

def bm25_search_lessons(query: str, lessons: list[dict], max_results: int = 5,
                         categoria: str | None = None,
                         k1: float = 1.5, b: float = 0.75) -> list[tuple[dict, float]]:
    import math
    if categoria:
        lessons = [l for l in lessons if l["categoria"].upper() == categoria.upper()]
    if not lessons:
        return []

    q_terms = _tokenize(query)
    N = len(lessons)

    def doc_text(l: dict) -> str:
        return " ".join([l["titulo"], l["contexto"], l["problema"], l["causa"],
                         l["leccion"], l["aplica"],
                         l.get("fix_aplicado", ""), l.get("mejoras_sugeridas", "")])

    tokenized = [_tokenize(doc_text(l)) for l in lessons]
    df: dict[str, int] = {}
    for toks in tokenized:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1

    avg_dl = sum(len(t) for t in tokenized) / max(N, 1)
    results = []
    for i, lesson in enumerate(lessons):
        toks = tokenized[i]
        dl = len(toks)
        tf_map: dict[str, int] = {}
        for t in toks:
            tf_map[t] = tf_map.get(t, 0) + 1
        score = 0.0
        for term in q_terms:
            if term not in df:
                continue
            idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)
            tf = tf_map.get(term, 0)
            tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            score += idf * tf_norm
        if score > 0:
            results.append((lesson, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:max_results]


# ── LLM ──────────────────────────────────────────────────────────────────────

SUGGEST_FIX_PROMPT = """\
Eres el agente investigador de X-DD. Analiza esta leccion aprendida y propone
mejoras concretas y accionables para evitar que el problema vuelva a ocurrir
y para hacer el sistema mas robusto.

Leccion:
  Titulo: {titulo}
  Categoria: {categoria}
  Contexto: {contexto}
  Problema: {problema}
  Causa raiz: {causa}
  Leccion actual: {leccion}
  Fix ya aplicado: {fix_aplicado}

Responde en JSON:
{{
  "mejoras_sugeridas": "lista de mejoras concretas separadas por punto y coma",
  "impacto": "alto|medio|bajo",
  "esfuerzo": "alto|medio|bajo",
  "referencias": "links o patrones de referencia si aplica"
}}"""

EXTRACT_PROMPT = """\
Analiza la siguiente sesion de trabajo y extrae lecciones aprendidas con impacto
real en futuras decisiones. Solo lecciones con REGLA CONCRETA y APLICABLE.

Para cada leccion usa EXACTAMENTE este formato JSON (array):
[
  {{
    "categoria": "ARQUITECTURA|SEGURIDAD|DOMINIO|TESTING|DEVOPS|PROCESO|HERRAMIENTAS",
    "titulo": "Titulo breve y especifico (max 80 chars)",
    "contexto": "Que estabamos intentando hacer.",
    "problema": "Que fallo o sorprendio.",
    "causa": "Por que paso.",
    "leccion": "Regla aplicable a futuras decisiones (concreta, accionable).",
    "aplica": "Ambito donde aplica.",
    "fix_aplicado": "Que se hizo para resolver el problema (si ya se aplico fix).",
    "mejoras_sugeridas": "Propuestas para evolucion futura (opcional)."
  }}
]

Si no hay lecciones claras, responde: []

Sesion:
{conversation}"""


def _call_llm(system: str, user: str, project: Path) -> str:
    provider = os.environ.get("XDD_PROVIDER", os.environ.get("EVOL_PROVIDER", "mock"))
    if provider == "mock":
        return '{"mejoras_sugeridas": "[mock — usar XDD_PROVIDER=anthropic para sugerencias reales]", "impacto": "desconocido", "esfuerzo": "desconocido", "referencias": ""}'

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
                print(f"[xdd-lessons] WARN: LLM error ({e})", file=sys.stderr)
    return "{}"


# ── Comandos ──────────────────────────────────────────────────────────────────

def cmd_add(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        _init_lessons_file(lpath)

    text = lpath.read_text(encoding="utf-8")
    existing = parse_lessons(text)

    key = f"{args.titulo} {args.leccion}"
    for ex in existing:
        sim = _similarity(key, f"{ex['titulo']} {ex['leccion']}")
        if sim > 0.70:
            print(f"[xdd-lessons] SKIP: leccion similar ya existe ({sim:.0%} similitud).")
            print(f"  Existente: [{ex['categoria']}] {ex['titulo']} — {ex['fecha']}")
            if not args.force:
                return 0

    cat = args.categoria.upper()
    lesson: dict[str, Any] = {
        "categoria": cat,
        "titulo": args.titulo,
        "fecha": today_str(),
        "contexto": args.contexto,
        "problema": args.problema,
        "causa": args.causa,
        "leccion": args.leccion,
        "aplica": args.aplica,
        "fix_aplicado": getattr(args, "fix_aplicado", "") or "",
        "mejoras_sugeridas": "",
        "estado_mejoras": "",
    }

    lpath.write_text(text + lesson_to_markdown(lesson), encoding="utf-8")
    print(f"[xdd-lessons] Añadida: [{cat}] {args.titulo} — {today_str()}")
    if args.json:
        print(json.dumps({"ok": True, "categoria": cat, "titulo": args.titulo}))
    return 0


def cmd_suggest_fix(args) -> int:
    """El agente investigador propone mejoras para una leccion especifica."""
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        print("[xdd-lessons] lecciones.md no existe.", file=sys.stderr)
        return 1

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    titulo = " ".join(args.titulo)

    # Buscar la leccion por titulo (BM25 o exact)
    candidates = bm25_search_lessons(titulo, lessons, max_results=1)
    if not candidates:
        print(f"[xdd-lessons] No se encontro leccion para: {titulo}")
        return 1

    lesson = candidates[0][0]
    print(f"[xdd-lessons] Generando mejoras para: [{lesson['categoria']}] {lesson['titulo']}...")

    prompt = SUGGEST_FIX_PROMPT.format(
        titulo=lesson["titulo"],
        categoria=lesson["categoria"],
        contexto=lesson["contexto"],
        problema=lesson["problema"],
        causa=lesson["causa"],
        leccion=lesson["leccion"],
        fix_aplicado=lesson.get("fix_aplicado") or "ninguno",
    )
    raw = _call_llm(
        "Eres el agente investigador de X-DD. Responde solo JSON valido.",
        prompt, project,
    )

    try:
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        data = {}

    mejoras = data.get("mejoras_sugeridas", "[sin sugerencias — revisar manualmente]")
    impacto = data.get("impacto", "?")
    esfuerzo = data.get("esfuerzo", "?")
    refs = data.get("referencias", "")

    print(f"\n  Leccion:   [{lesson['categoria']}] {lesson['titulo']}")
    print(f"  Impacto:   {impacto} | Esfuerzo: {esfuerzo}")
    print(f"  Mejoras:   {mejoras}")
    if refs:
        print(f"  Refs:      {refs}")

    if args.apply:
        # Actualizar la leccion en disco con las mejoras
        for l in lessons:
            if l["titulo"] == lesson["titulo"] and l["fecha"] == lesson["fecha"]:
                l["mejoras_sugeridas"] = mejoras
                l["estado_mejoras"] = "pendiente"
                break
        _rewrite_lessons(lpath, lessons)
        print(f"[xdd-lessons] Mejoras guardadas en lecciones.md (estado: pendiente).")

    if args.json:
        print(json.dumps({"leccion": lesson["titulo"], "mejoras": mejoras,
                          "impacto": impacto, "esfuerzo": esfuerzo}))
    return 0


def cmd_apply_fix(args) -> int:
    """Marca mejoras de una leccion como aplicadas y registra que se implemento."""
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        print("[xdd-lessons] lecciones.md no existe.", file=sys.stderr)
        return 1

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    titulo = " ".join(args.titulo)
    candidates = bm25_search_lessons(titulo, lessons, max_results=1)
    if not candidates:
        print(f"[xdd-lessons] No se encontro leccion para: {titulo}")
        return 1

    lesson = candidates[0][0]
    for l in lessons:
        if l["titulo"] == lesson["titulo"] and l["fecha"] == lesson["fecha"]:
            l["fix_aplicado"] = args.fix or l.get("fix_aplicado", "")
            l["estado_mejoras"] = "aplicado"
            break

    _rewrite_lessons(lpath, lessons)
    print(f"[xdd-lessons] Mejoras marcadas como APLICADAS: [{lesson['categoria']}] {lesson['titulo']}")
    if args.json:
        print(json.dumps({"ok": True, "titulo": lesson["titulo"], "estado": "aplicado"}))
    return 0


def cmd_search(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        print("[xdd-lessons] lecciones.md no existe.")
        return 0

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    query = " ".join(args.query)
    results = bm25_search_lessons(query, lessons, max_results=args.max,
                                   categoria=getattr(args, "categoria", None))
    if not results:
        print(f"[xdd-lessons] Sin resultados para: {query}")
        return 0

    if args.json:
        print(json.dumps([
            {"categoria": l["categoria"], "titulo": l["titulo"], "fecha": l["fecha"],
             "leccion": l["leccion"], "aplica": l["aplica"],
             "fix_aplicado": l.get("fix_aplicado", ""),
             "mejoras_sugeridas": l.get("mejoras_sugeridas", ""),
             "estado_mejoras": l.get("estado_mejoras", ""),
             "score": round(s, 3)}
            for l, s in results
        ], ensure_ascii=False))
        return 0

    print(f"[xdd-lessons] {len(results)} leccion(es) para '{query}':\n")
    for lesson, score in results:
        estado = lesson.get("estado_mejoras", "")
        estado_tag = f" [{estado}]" if estado else ""
        print(f"  [{lesson['categoria']}] {lesson['titulo']} — {lesson['fecha']}{estado_tag}  ({score:.2f})")
        print(f"  Leccion: {lesson['leccion'][:120]}")
        if lesson.get("fix_aplicado"):
            print(f"  Fix:     {lesson['fix_aplicado'][:100]}")
        if lesson.get("mejoras_sugeridas"):
            print(f"  Mejoras: {lesson['mejoras_sugeridas'][:100]}")
        print()
    return 0


def cmd_suggest(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        return 0

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    query = " ".join(args.query)
    results = bm25_search_lessons(query, lessons, max_results=args.max)
    if not results:
        return 0

    print("## Lecciones aprendidas relevantes (consultar antes de proceder)\n")
    for lesson, _ in results:
        print(f"### [{lesson['categoria']}] {lesson['titulo']}")
        print(f"**Leccion:** {lesson['leccion']}")
        if lesson.get("fix_aplicado"):
            print(f"**Fix aplicado:** {lesson['fix_aplicado']}")
        if lesson.get("mejoras_sugeridas") and lesson.get("estado_mejoras") == "pendiente":
            print(f"**Mejoras pendientes:** {lesson['mejoras_sugeridas']}")
        print(f"**Aplica a:** {lesson['aplica']}\n")
    return 0


def cmd_extract(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)

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

    print("[xdd-lessons] Extrayendo lecciones (requiere XDD_PROVIDER=anthropic)...")
    raw_resp = _call_llm(
        "Eres un extractor de lecciones aprendidas. Responde solo JSON valido.",
        EXTRACT_PROMPT.format(conversation=conversation[:15000]),
        project,
    )

    try:
        m = re.search(r"\[.*\]", raw_resp, re.S)
        candidates = json.loads(m.group(0)) if m else []
    except (json.JSONDecodeError, AttributeError):
        candidates = []

    if not candidates:
        print("[xdd-lessons] Sin lecciones extraidas. Con mock provider se requiere revision manual.")
        return 0

    if not args.auto:
        print(f"[xdd-lessons] {len(candidates)} leccion(es) candidata(s):\n")
        for i, c in enumerate(candidates, 1):
            print(f"--- Candidata {i} ---")
            print(f"[{c.get('categoria')}] {c.get('titulo')}")
            print(f"Leccion: {c.get('leccion')}")
            if c.get("fix_aplicado"):
                print(f"Fix: {c.get('fix_aplicado')}")
            if c.get("mejoras_sugeridas"):
                print(f"Mejoras: {c.get('mejoras_sugeridas')}")
            print()
        print("[xdd-lessons] Re-ejecuta con --auto para añadir directamente.")
        return 0

    if not lpath.exists():
        _init_lessons_file(lpath)

    added = 0
    for c in candidates:
        cat = c.get("categoria", "PROCESO").upper()
        if cat not in CATEGORIES:
            cat = "PROCESO"
        lesson: dict[str, Any] = {
            "categoria": cat,
            "titulo": c.get("titulo", "Leccion sin titulo"),
            "fecha": today_str(),
            "contexto": c.get("contexto", ""),
            "problema": c.get("problema", ""),
            "causa": c.get("causa", ""),
            "leccion": c.get("leccion", ""),
            "aplica": c.get("aplica", ""),
            "fix_aplicado": c.get("fix_aplicado", ""),
            "mejoras_sugeridas": c.get("mejoras_sugeridas", ""),
            "estado_mejoras": "pendiente" if c.get("mejoras_sugeridas") else "",
        }
        text = lpath.read_text(encoding="utf-8")
        existing = parse_lessons(text)
        key = f"{lesson['titulo']} {lesson['leccion']}"
        if any(_similarity(key, f"{ex['titulo']} {ex['leccion']}") > 0.70 for ex in existing):
            print(f"[xdd-lessons] SKIP (duplicado): {lesson['titulo']}")
            continue
        lpath.write_text(text + lesson_to_markdown(lesson), encoding="utf-8")
        print(f"[xdd-lessons] Añadida: [{cat}] {lesson['titulo']}")
        added += 1

    print(f"[xdd-lessons] {added}/{len(candidates)} lecciones añadidas.")
    if args.json:
        print(json.dumps({"ok": True, "added": added, "total_candidates": len(candidates)}))
    return 0


def cmd_list(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        print("[xdd-lessons] lecciones.md no existe.")
        return 0

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    if getattr(args, "categoria", None):
        lessons = [l for l in lessons if l["categoria"].upper() == args.categoria.upper()]
    if getattr(args, "pendientes", False):
        lessons = [l for l in lessons if l.get("estado_mejoras") == "pendiente"]
    if getattr(args, "limit", None):
        lessons = lessons[-args.limit:]

    if args.json:
        print(json.dumps([
            {"categoria": l["categoria"], "titulo": l["titulo"], "fecha": l["fecha"],
             "leccion": l["leccion"][:200], "estado_mejoras": l.get("estado_mejoras", "")}
            for l in lessons
        ], ensure_ascii=False))
        return 0

    print(f"[xdd-lessons] {len(lessons)} leccion(es):\n")
    for l in lessons:
        estado = f" [{l['estado_mejoras']}]" if l.get("estado_mejoras") else ""
        print(f"  [{l['categoria']}] {l['titulo']} — {l['fecha']}{estado}")
    return 0


def cmd_stats(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)

    if not lpath.exists():
        data: dict[str, Any] = {"total": 0, "by_category": {}, "latest": None,
                                  "mejoras_pendientes": 0, "mejoras_aplicadas": 0}
    else:
        lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
        by_cat: dict[str, int] = {}
        pendientes = sum(1 for l in lessons if l.get("estado_mejoras") == "pendiente")
        aplicadas = sum(1 for l in lessons if l.get("estado_mejoras") == "aplicado")
        for l in lessons:
            by_cat[l["categoria"]] = by_cat.get(l["categoria"], 0) + 1
        latest = lessons[-1] if lessons else None
        data = {
            "total": len(lessons),
            "by_category": by_cat,
            "latest": f"[{latest['categoria']}] {latest['titulo']} — {latest['fecha']}" if latest else None,
            "mejoras_pendientes": pendientes,
            "mejoras_aplicadas": aplicadas,
        }

    if args.json:
        print(json.dumps(data, ensure_ascii=False))
        return 0

    print("[xdd-lessons] Estadisticas:")
    print(f"  Total lecciones:    {data['total']}")
    print(f"  Mejoras pendientes: {data['mejoras_pendientes']}")
    print(f"  Mejoras aplicadas:  {data['mejoras_aplicadas']}")
    if data["by_category"]:
        print("  Por categoria:")
        for cat, n in sorted(data["by_category"].items()):
            print(f"    {cat:<15} {n}")
    if data["latest"]:
        print(f"  Ultima:            {data['latest']}")
    return 0


def cmd_gc(args) -> int:
    project = Path(args.project)
    lpath = lessons_path(project)
    if not lpath.exists():
        print("[xdd-lessons] gc: lecciones.md no existe.")
        return 0

    lessons = parse_lessons(lpath.read_text(encoding="utf-8"))
    seen: set[str] = set()
    unique = []
    removed = 0
    for l in lessons:
        key = f"{l['titulo']}::{l['fecha']}"
        if key in seen:
            print(f"[xdd-lessons] gc: duplicado eliminado: {l['titulo']}")
            removed += 1
        else:
            seen.add(key)
            unique.append(l)

    if removed == 0:
        print("[xdd-lessons] gc: sin duplicados.")
        return 0

    _rewrite_lessons(lpath, unique)
    print(f"[xdd-lessons] gc: {removed} duplicado(s) eliminados. {len(unique)} restantes.")
    if args.json:
        print(json.dumps({"ok": True, "removed": removed, "remaining": len(unique)}))
    return 0


def _init_lessons_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# lecciones.md — Aprendizajes Acumulados\n\n"
        "> Lecciones aprendidas del proyecto. Consultado por agentes antes de proponer\n"
        "> soluciones (Constitucion Art. 9). Actualizado via `/cierre-fase` o `xdd-lessons add`.\n\n"
        "## Formato\n"
        "```\n"
        "### [CATEGORIA] Titulo — YYYY-MM-DD\n"
        "**Contexto:** ...\n"
        "**Problema:** ...\n"
        "**Causa raiz:** ...\n"
        "**Leccion:** ...\n"
        "**Aplica a:** ...\n"
        "**Fix aplicado:** ... (opcional)\n"
        "**Mejoras sugeridas:** ... (opcional, generado por investigador)\n"
        "**Estado mejoras:** pendiente | en-progreso | aplicado (opcional)\n"
        "```\n\n"
        "Categorias: `ARQUITECTURA`, `SEGURIDAD`, `DOMINIO`, `TESTING`,"
        " `DEVOPS`, `PROCESO`, `HERRAMIENTAS`.\n\n"
        "---\n\n"
        "## Lecciones\n",
        encoding="utf-8",
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xdd-lessons", description=__doc__)
    p.add_argument("--project", default=os.getcwd())
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add")
    pa.add_argument("--titulo", required=True)
    pa.add_argument("--categoria", required=True, choices=sorted(CATEGORIES))
    pa.add_argument("--contexto", required=True)
    pa.add_argument("--problema", required=True)
    pa.add_argument("--causa", required=True)
    pa.add_argument("--leccion", required=True)
    pa.add_argument("--aplica", required=True)
    pa.add_argument("--fix-aplicado", default="", dest="fix_aplicado")
    pa.add_argument("--force", action="store_true")

    psf = sub.add_parser("suggest-fix")
    psf.add_argument("titulo", nargs="+")
    psf.add_argument("--apply", action="store_true", help="Guarda las mejoras en lecciones.md")

    paf = sub.add_parser("apply-fix")
    paf.add_argument("titulo", nargs="+")
    paf.add_argument("--fix", default="", help="Descripcion del fix implementado")

    ps = sub.add_parser("search")
    ps.add_argument("query", nargs="+")
    ps.add_argument("--max", type=int, default=5)
    ps.add_argument("--categoria", default=None)

    pg = sub.add_parser("suggest")
    pg.add_argument("query", nargs="+")
    pg.add_argument("--max", type=int, default=3)

    pe = sub.add_parser("extract")
    pe.add_argument("--messages", required=True)
    pe.add_argument("--auto", action="store_true")

    pl = sub.add_parser("list")
    pl.add_argument("--categoria", default=None)
    pl.add_argument("--limit", type=int, default=None)
    pl.add_argument("--pendientes", action="store_true", help="Solo con mejoras pendientes")

    sub.add_parser("stats")
    sub.add_parser("gc")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    dispatch = {
        "add": cmd_add, "suggest-fix": cmd_suggest_fix, "apply-fix": cmd_apply_fix,
        "search": cmd_search, "suggest": cmd_suggest, "extract": cmd_extract,
        "list": cmd_list, "stats": cmd_stats, "gc": cmd_gc,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
