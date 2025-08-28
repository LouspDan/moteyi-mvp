#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diag rapide des métriques RAG à partir de artifacts/metrics.csv
- Résumé global
- Pires groupes (lang/grade/subject si présents)
- Groupes sous seuils (cov@5<0.50 ou hit@1<0.35)
Usage:
  python tools/eval_diagnose.py --file artifacts/metrics.csv --cov 0.50 --hit 0.35
"""
import csv, argparse
from collections import defaultdict

def f(x):
    try: return float(x)
    except: return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="artifacts/metrics.csv")
    ap.add_argument("--cov", type=float, default=0.50)
    ap.add_argument("--hit", type=float, default=0.35)
    args = ap.parse_args()

    rows=[]
    with open(args.file, encoding="utf-8") as fcsv:
        r=csv.DictReader(fcsv)
        hdr=[h.strip() for h in r.fieldnames]
        for row in r:
            rows.append({k.strip(): v for k,v in row.items()})

    if not rows:
        print("[diag] metrics.csv vide"); return

    # colonnes possibles
    has_lang   = "lang" in rows[0]
    has_grade  = "grade" in rows[0]
    has_subj   = "subject" in rows[0]
    has_cov    = "coverage@5" in rows[0]
    has_hit    = "hit@1" in rows[0]
    has_mrr    = "mrr@5" in rows[0]

    if not (has_cov and has_hit and has_mrr):
        print("[diag] Colonnes attendues manquantes (coverage@5, hit@1, mrr@5)."); return

    # résumé global
    gsum={"n":0,"cov":0.0,"hit":0.0,"mrr":0.0}
    for row in rows:
        gsum["n"]+=1
        gsum["cov"]+=f(row["coverage@5"])
        gsum["hit"]+=f(row["hit@1"])
        gsum["mrr"]+=f(row["mrr@5"])
    print("=== GLOBAL ===")
    print(f"n={gsum['n']}  cov@5={gsum['cov']/max(gsum['n'],1):.3f}  hit@1={gsum['hit']/max(gsum['n'],1):.3f}  mrr@5={gsum['mrr']/max(gsum['n'],1):.3f}")
    print()

    # agrégations
    def group_key(row):
        parts=[]
        if has_lang: parts.append(row["lang"])
        if has_grade: parts.append(row["grade"])
        if has_subj: parts.append(row["subject"])
        return " / ".join(parts) if parts else "GLOBAL"

    agg=defaultdict(lambda: {"n":0,"cov":0.0,"hit":0.0,"mrr":0.0})
    for row in rows:
        k=group_key(row)
        agg[k]["n"]+=1
        agg[k]["cov"]+=f(row["coverage@5"])
        agg[k]["hit"]+=f(row["hit@1"])
        agg[k]["mrr"]+=f(row["mrr@5"])

    # moyenne par groupe
    stats=[]
    for k,v in agg.items():
        n=max(v["n"],1)
        stats.append((k, v["n"], v["cov"]/n, v["hit"]/n, v["mrr"]/n))
    # trier par hit@1 puis cov@5 croissants
    stats.sort(key=lambda x:(x[3], x[2]))

    print("=== PIRES GROUPES (hit@1 puis cov@5) ===")
    for k,n,c,h,m in stats[:10]:
        print(f"- {k:40s}  n={n:3d}  cov@5={c:.3f}  hit@1={h:.3f}  mrr@5={m:.3f}")
    print()

    print(f"=== GROUPES SOUS SEUILS (cov@5<{args.cov} ou hit@1<{args.hit}) ===")
    bad=[(k,n,c,h,m) for (k,n,c,h,m) in stats if (c<args.cov or h<args.hit)]
    if not bad:
        print("OK: aucun groupe sous seuil.")
    else:
        for k,n,c,h,m in bad:
            print(f"* {k:40s}  n={n:3d}  cov@5={c:.3f}  hit@1={h:.3f}  mrr@5={m:.3f}")

if __name__=="__main__":
    main()
