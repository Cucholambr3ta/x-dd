#!/usr/bin/env python3
"""xdd-state.py — State store SQLite para continuous learning (Sprint 9).

Almacena 'instincts': patrones repetidos detectados durante sesiones del agente.
Cada instinct tiene confidence scoring basado en occurrences + last_seen.

Comandos:
  init                     — crea schema en ~/.xdd/state.db
  record-instinct          — añade instinct (de hook stop:pattern-extraction)
  list                     — lista instincts (filtrable por confidence/category)
  evolve                   — clusters instincts similares → propone skills/agents/commands
  prune                    — borra instincts viejos (last_seen > N días) o low-confidence
  stats                    — métricas del state store

Spec instinct:
  {id, category, pattern, context, confidence (0.0-1.0), occurrences,
   first_seen, last_seen, source_sessions[], promoted (bool), promoted_to (path)}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

__version__ = "0.1.0-dev"

DEFAULT_DB = Path(os.environ.get("XDD_STATE_DB",
                                  str(Path.home() / ".xdd" / "state.db")))


SCHEMA = """
CREATE TABLE IF NOT EXISTS instincts (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  pattern TEXT NOT NULL,
  context TEXT,
  confidence REAL DEFAULT 0.1,
  occurrences INTEGER DEFAULT 1,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  promoted INTEGER DEFAULT 0,
  promoted_to TEXT
);

CREATE TABLE IF NOT EXISTS instinct_sessions (
  instinct_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  FOREIGN KEY(instinct_id) REFERENCES instincts(id)
);

CREATE INDEX IF NOT EXISTS idx_category ON instincts(category);
CREATE INDEX IF NOT EXISTS idx_confidence ON instincts(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_last_seen ON instincts(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_promoted ON instincts(promoted);

CREATE TABLE IF NOT EXISTS evolutions (
  cluster_id TEXT PRIMARY KEY,
  proposed_type TEXT NOT NULL,
  proposed_name TEXT NOT NULL,
  instinct_ids TEXT NOT NULL,
  rationale TEXT,
  status TEXT DEFAULT 'proposed',
  created_at TEXT NOT NULL,
  approved_by TEXT,
  approved_at TEXT
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def instinct_id(pattern: str, category: str) -> str:
    h = hashlib.sha256(f"{category}::{pattern}".encode()).hexdigest()[:16]
    return f"inst_{h}"


def db(path: Path = None) -> sqlite3.Connection:
    p = Path(path or DEFAULT_DB)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def cmd_init(args):
    conn = db(args.db)
    conn.commit()
    conn.close()
    print(f"[state] ✓ {args.db} initialized.")
    return 0


def cmd_record(args):
    """Añade instinct. Si ya existe (mismo id), incrementa occurrences y bump confidence."""
    conn = db(args.db)
    iid = instinct_id(args.pattern, args.category)
    now = utcnow()

    cur = conn.execute("SELECT * FROM instincts WHERE id = ?", (iid,))
    existing = cur.fetchone()

    if existing:
        new_occ = existing["occurrences"] + 1
        new_conf = min(1.0, existing["confidence"] + 0.1)
        conn.execute(
            "UPDATE instincts SET occurrences = ?, confidence = ?, last_seen = ? WHERE id = ?",
            (new_occ, new_conf, now, iid),
        )
        action = "incremented"
    else:
        conn.execute(
            "INSERT INTO instincts (id, category, pattern, context, "
            "first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
            (iid, args.category, args.pattern, args.context or "", now, now),
        )
        action = "created"

    if args.session_id:
        conn.execute(
            "INSERT INTO instinct_sessions (instinct_id, session_id, recorded_at) "
            "VALUES (?, ?, ?)",
            (iid, args.session_id, now),
        )

    conn.commit()
    conn.close()

    if args.json:
        print(json.dumps({"ok": True, "id": iid, "action": action}))
    else:
        print(f"[state] ✓ instinct {iid} {action}.")
    return 0


def cmd_list(args):
    conn = db(args.db)
    where, params = [], []
    if args.category:
        where.append("category = ?"); params.append(args.category)
    if args.min_confidence is not None:
        where.append("confidence >= ?"); params.append(args.min_confidence)
    if args.promoted is not None:
        where.append("promoted = ?"); params.append(1 if args.promoted else 0)
    sql = "SELECT * FROM instincts"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY confidence DESC, occurrences DESC LIMIT ?"
    params.append(args.limit or 50)

    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()

    if args.json:
        print(json.dumps({"count": len(rows), "instincts": rows}, indent=2))
    else:
        print(f"[state] {len(rows)} instincts:")
        for r in rows:
            mark = "✓" if r["promoted"] else " "
            print(f"  [{mark}] {r['id']} conf={r['confidence']:.2f} "
                  f"occ={r['occurrences']:>3} cat={r['category']:<14} "
                  f"pattern={r['pattern'][:60]}")
    return 0


def _tokenize(text):
    """Tokenize: lowercase, alphanumeric, drop stopwords + len<3."""
    import re
    stop = {"the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at",
            "for", "by", "with", "is", "are", "was", "be", "as", "from", "que",
            "el", "la", "los", "las", "de", "en", "y", "o", "un", "una"}
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in toks if len(t) >= 3 and t not in stop]


def _tfidf_vectors(docs):
    """Compute TF-IDF vectors (stdlib pure, no sklearn). Returns list of dict[term]=weight."""
    import math
    tokenized = [_tokenize(d) for d in docs]
    df = {}
    for toks in tokenized:
        for term in set(toks):
            df[term] = df.get(term, 0) + 1
    n = len(docs)
    vectors = []
    for toks in tokenized:
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        vec = {}
        for term, count in tf.items():
            tf_norm = count / max(len(toks), 1)
            idf = math.log((n + 1) / (df.get(term, 0) + 1)) + 1
            vec[term] = tf_norm * idf
        vectors.append(vec)
    return vectors


def _cosine(v1, v2):
    """Cosine similarity between sparse vectors (dict[term]=weight)."""
    import math
    common = set(v1) & set(v2)
    num = sum(v1[t] * v2[t] for t in common)
    n1 = math.sqrt(sum(w * w for w in v1.values()))
    n2 = math.sqrt(sum(w * w for w in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return num / (n1 * n2)


def _tfidf_cluster(rows, similarity_threshold=0.3):
    """Cluster instincts by TF-IDF cosine similarity (single-pass greedy clustering)."""
    if not rows:
        return []
    def _ctx(row):
        try:
            v = row["context"]
        except (KeyError, IndexError):
            v = row.get("context") if hasattr(row, "get") else None
        return v or ""
    docs = [f"{r['category']} {r['pattern']} {_ctx(r)}" for r in rows]
    vectors = _tfidf_vectors(docs)
    clusters = []
    cluster_centroids = []
    for i, row in enumerate(rows):
        assigned = False
        for c_idx, centroid in enumerate(cluster_centroids):
            if _cosine(vectors[i], centroid) >= similarity_threshold:
                clusters[c_idx].append(dict(row))
                # Update centroid: simple average of vectors in cluster
                for t, w in vectors[i].items():
                    centroid[t] = (centroid.get(t, 0) + w) / 2
                assigned = True
                break
        if not assigned:
            clusters.append([dict(row)])
            cluster_centroids.append(dict(vectors[i]))
    return clusters


def cmd_evolve(args):
    """Cluster instincts vía TF-IDF cosine similarity (Sprint 16) → propuestas."""
    conn = db(args.db)
    threshold = args.min_confidence or 0.5
    rows = conn.execute(
        "SELECT * FROM instincts WHERE confidence >= ? AND promoted = 0 "
        "ORDER BY confidence DESC", (threshold,)
    ).fetchall()

    use_tfidf = not getattr(args, "category_only", False)
    if use_tfidf:
        sim_threshold = getattr(args, "similarity_threshold", None) or 0.3
        groups = _tfidf_cluster(rows, similarity_threshold=sim_threshold)
        clusters = {f"cluster_{i}": items for i, items in enumerate(groups)}
    else:
        clusters = {}
        for r in rows:
            clusters.setdefault(r["category"], []).append(dict(r))

    proposals = []
    for cluster_label, items in clusters.items():
        if len(items) < (args.min_cluster_size or 3):
            continue
        # Modo dominante en el cluster determina tipo propuesto
        from collections import Counter
        cats = Counter(i["category"] for i in items)
        dominant_cat = cats.most_common(1)[0][0]
        proposed_type = {
            "user_action": "command",
            "auto_trigger": "skill",
            "multi_step": "agent",
        }.get(dominant_cat, "skill")
        seed = f"{cluster_label}-{dominant_cat}"
        cluster_id = f"clu_{hashlib.sha256(seed.encode()).hexdigest()[:12]}"
        proposed_name = f"{dominant_cat}-auto-{cluster_id[-6:]}"
        rationale = (
            f"Cluster {len(items)} instincts (dominant category: '{dominant_cat}') with avg confidence "
            f"{sum(i['confidence'] for i in items) / len(items):.2f}. "
            f"Top pattern: {items[0]['pattern'][:80]}"
        )
        proposals.append({
            "cluster_id": cluster_id,
            "proposed_type": proposed_type,
            "proposed_name": proposed_name,
            "instinct_ids": [i["id"] for i in items],
            "rationale": rationale,
            "instinct_count": len(items),
        })

    if args.generate:
        for p in proposals:
            conn.execute(
                "INSERT OR REPLACE INTO evolutions (cluster_id, proposed_type, "
                "proposed_name, instinct_ids, rationale, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, 'proposed', ?)",
                (p["cluster_id"], p["proposed_type"], p["proposed_name"],
                 json.dumps(p["instinct_ids"]), p["rationale"], utcnow()),
            )
        conn.commit()
    conn.close()

    if args.json:
        print(json.dumps({"proposals": proposals, "generated": args.generate},
                          indent=2))
    else:
        print(f"[state] evolve found {len(proposals)} cluster(s) ≥ "
              f"{args.min_cluster_size or 3} instincts, conf ≥ {threshold}")
        for p in proposals:
            mark = "✓ saved" if args.generate else "  preview"
            print(f"  [{mark}] {p['proposed_type']:<8} {p['proposed_name']} "
                  f"({p['instinct_count']} instincts)")
            print(f"           {p['rationale'][:100]}")
        if not args.generate and proposals:
            print(f"\nRun with --generate to save proposals to evolutions table.")
    return 0


def cmd_prune(args):
    conn = db(args.db)
    cutoff = (datetime.now(timezone.utc) -
              timedelta(days=args.older_than_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        "DELETE FROM instincts WHERE last_seen < ? AND confidence < ? AND promoted = 0",
        (cutoff, args.max_confidence)
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    print(f"[state] ✓ pruned {deleted} instincts (older than {args.older_than_days}d, "
          f"confidence < {args.max_confidence}, not promoted).")
    return 0


def cmd_stats(args):
    conn = db(args.db)
    total = conn.execute("SELECT COUNT(*) FROM instincts").fetchone()[0]
    promoted = conn.execute("SELECT COUNT(*) FROM instincts WHERE promoted = 1").fetchone()[0]
    high_conf = conn.execute("SELECT COUNT(*) FROM instincts WHERE confidence >= 0.5").fetchone()[0]
    cats = conn.execute("SELECT category, COUNT(*) c FROM instincts GROUP BY category").fetchall()
    evolutions = conn.execute("SELECT COUNT(*) FROM evolutions").fetchone()[0]
    conn.close()

    data = {
        "total_instincts": total,
        "promoted": promoted,
        "high_confidence": high_conf,
        "by_category": {r["category"]: r["c"] for r in cats},
        "evolutions": evolutions,
        "db_path": str(args.db),
    }

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"[state] stats — {data['db_path']}")
        print(f"  Total instincts: {total}")
        print(f"  High confidence (≥0.5): {high_conf}")
        print(f"  Promoted to skills/agents: {promoted}")
        print(f"  Evolutions proposed: {evolutions}")
        print(f"  By category:")
        for c, n in data["by_category"].items():
            print(f"    {c:<20} {n}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="xdd-state",
        description="State store SQLite para continuous learning (Sprint 9).")
    p.add_argument("-v", "--version", action="version", version=f"xdd-state v{__version__}")
    p.add_argument("--db", type=Path, default=DEFAULT_DB,
                   help=f"Path SQLite (default: {DEFAULT_DB})")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Crear schema")
    p_init.set_defaults(func=cmd_init)

    p_rec = sub.add_parser("record-instinct", help="Añadir instinct")
    p_rec.add_argument("--pattern", required=True)
    p_rec.add_argument("--category", required=True,
                        choices=["user_action", "auto_trigger", "multi_step",
                                 "tool_use", "error_pattern", "preference"])
    p_rec.add_argument("--context", help="Contexto opcional (file, error, etc.)")
    p_rec.add_argument("--session-id", help="ID de sesión")
    p_rec.add_argument("--json", action="store_true")
    p_rec.set_defaults(func=cmd_record)

    p_list = sub.add_parser("list", help="Listar instincts")
    p_list.add_argument("--category")
    p_list.add_argument("--min-confidence", type=float)
    p_list.add_argument("--promoted", type=lambda x: x.lower() == "true")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_ev = sub.add_parser("evolve", help="Clusters instincts → propuestas")
    p_ev.add_argument("--min-confidence", type=float, default=0.5)
    p_ev.add_argument("--min-cluster-size", type=int, default=3)
    p_ev.add_argument("--similarity-threshold", type=float, default=0.3,
                      help="TF-IDF cosine threshold para agrupar (Sprint 16)")
    p_ev.add_argument("--category-only", action="store_true",
                      help="Modo legacy Sprint 9: cluster sólo por categoría")
    p_ev.add_argument("--generate", action="store_true",
                      help="Guardar propuestas en tabla evolutions")
    p_ev.add_argument("--json", action="store_true")
    p_ev.set_defaults(func=cmd_evolve)

    p_pr = sub.add_parser("prune", help="Borrar instincts viejos low-conf")
    p_pr.add_argument("--older-than-days", type=int, default=30)
    p_pr.add_argument("--max-confidence", type=float, default=0.3)
    p_pr.set_defaults(func=cmd_prune)

    p_st = sub.add_parser("stats", help="Métricas")
    p_st.add_argument("--json", action="store_true")
    p_st.set_defaults(func=cmd_stats)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
