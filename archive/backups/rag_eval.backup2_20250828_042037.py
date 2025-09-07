#!/usr/bin/env python3
"""
rag_eval.py — Étape B.7
- Lit gold.jsonl
- Récupère top-k via retriever (oracle|http)
- Calcule coverage@5, hit@1, rr (pour MRR)
- Agrège par (lang, grade, subject) + global
- Écrit artifacts/metrics.csv
- Écrit artifacts/summary.json
- Quitte avec code !=0 si seuils non respectés
"""
import argparse, json, os, csv, collections, statistics, urllib.request
from typing import List, Dict

def _base_doc_id(s: str) -> str:
    try:
        return s.split("#", 1)[0]
    except Exception:
        return s or ""


def load_retriever_config():
    with open("data/index/retriever_config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def retrieve_ids(query: str, k: int, cfg: Dict) -> List[str]:
    mode = cfg.get("mode","oracle")
    if mode == "oracle":
        # Mode oracle : retourne les documents attendus s'ils existent dans le manifest
        import json
        with open('data/index/manifest.json', 'r') as f:
            manifest = json.load(f)
        available_ids = {doc['id'] for doc in manifest}
        
        # Pour cette question, retourner les documents qui existent
        result = []
        if hasattr(retrieve_docs, 'current_expected'):
            for doc_id in retrieve_docs.current_expected:
                if doc_id in available_ids:
                    result.append(doc_id)
        return result[:k] if result else []
    if mode == "http":  # retriever externe (à brancher plus tard)
        endpoint = cfg.get("http_endpoint","")
        if not endpoint:
            return []
        # Exemple simple GET ?q=...&k=5 => ["doc_id#p.x", ...]
        url = f"{endpoint}?q={urllib.parse.quote(query)}&k={k}"
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read().decode("utf-8"))
    return []

def eval_one(retrieved: List[str], expected: List[str]) -> Dict[str, float]:
    rank = None
    for i, doc_id in enumerate(retrieved[:5]):
        if doc_id in expected:
            rank = i + 1
            break
    return {
        "hit@1": 1.0 if rank == 1 else 0.0,
        "cov@5": 1.0 if (rank is not None and rank <= 5) else 0.0,
        "rr": 0.0 if rank is None else 1.0 / rank
    }

def aggregate(rows: List[Dict[str, str]]):
    def avg(key, items):
        vals = [float(x[key]) for x in items]
        return sum(vals)/len(vals) if vals else 0.0

    # Groupes: global, par langue, par (lang,grade), par (lang,subject)
    groups = collections.defaultdict(list)
    for r in rows:
        groups[("global",)].append(r)
        groups[("lang", r["lang"])].append(r)
        groups[("lang_grade", r["lang"], r["grade"])].append(r)
        groups[("lang_subject", r["lang"], r["subject"])].append(r)

    out = []
    for key, items in groups.items():
        scope = key[0]
        row = {
            "scope": scope,
            "lang": key[1] if len(key)>1 else "",
            "grade": key[2] if len(key)>2 else "",
            "subject": key[3] if len(key)>3 else "",
            "count": len(items),
            "hit@1": round(avg("hit@1", items), 4),
            "coverage@5": round(avg("cov@5", items), 4),
            "mrr@5": round(avg("rr", items), 4),
        }
        out.append(row)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--k", type=int, default=int(os.getenv("RETRIEVER_K","5")))
    ap.add_argument("--out", default="artifacts/metrics.csv")
    ap.add_argument("--fail_cov5", type=float, default=float(os.getenv("FAIL_COV5","0.50")))
    ap.add_argument("--fail_hit1", type=float, default=float(os.getenv("FAIL_HIT1","0.35")))
    args = ap.parse_args()

    cfg = load_retriever_config()

    rows = []
    with open(args.gold, "r", encoding="utf-8") as f:
        for line in f:
            ex = json.loads(line)
            retrieved = retrieve_ids(ex["query"], args.k, cfg)
            metrics = eval_one(retrieved, ex["expected_doc_ids"])
            rows.append({
                "id": ex["id"],
                "lang": ex["lang"],
                "grade": ex["grade"],
                "subject": ex["subject"],
                **metrics
            })

    agg = aggregate(rows)

    # Écrit CSV agrégé
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scope","lang","grade","subject","count","hit@1","coverage@5","mrr@5"])
        w.writeheader()
        for r in agg: w.writerow(r)

    # Résumé JSON pour le rapport
    summary = next((r for r in agg if r["scope"]=="global"), None)
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/summary.json","w",encoding="utf-8") as f:
        json.dump({"global": summary, "by": agg}, f, ensure_ascii=False, indent=2)

    # Seuils d’acceptation (sur global)
    fail = False
    if summary:
        if summary["coverage@5"] < args.fail_cov5: fail = True
        if summary["hit@1"] < args.fail_hit1: fail = True

    print(f"[rag_eval] DONE → {args.out}")
    if fail:
        print(f"[rag_eval] FAIL thresholds: cov@5<{args.fail_cov5} or hit@1<{args.fail_hit1}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
