#!/usr/bin/env python3
import csv, collections, datetime as dt, os, sys

CSV = "data/rag_seed/rag_seed_catalog.csv"
OUT = "data/rag_seed/report.md"

# Colonnes possibles (on s'adapte à ton CSV actuel)
POSS = {
    "title":  ["title", "titre"],
    "subject":["subject", "matiere"],
    "level":  ["grade_level", "niveau"],
    "lang":   ["language", "langue"],
}

def pick(headers, candidates):
    low = {h.lower(): h for h in headers}
    for c in candidates:
        if c in low: return low[c]
    return None

with open(CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    if not rows:
        print("❌ CSV vide"); sys.exit(1)

    subj_f = pick(reader.fieldnames, POSS["subject"])
    level_f= pick(reader.fieldnames, POSS["level"])
    lang_f = pick(reader.fieldnames, POSS["lang"])

by_subj = collections.Counter((r.get(subj_f,"") or "").strip() for r in rows) if subj_f else {}
by_lvl  = collections.Counter((r.get(level_f,"") or "").strip() for r in rows) if level_f else {}
by_lang = collections.Counter((r.get(lang_f,"") or "").strip() for r in rows) if lang_f else {}

now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# RAG — Rapport de couverture\n\n")
    f.write(f"**Généré :** {now}\n\n")
    f.write(f"**Total documents :** {len(rows)}\n\n")
    if by_subj:
        f.write("## Par matière\n")
        for k,v in by_subj.most_common(): f.write(f"- {k or '(inconnu)'} : {v}\n")
        f.write("\n")
    if by_lvl:
        f.write("## Par niveau\n")
        for k,v in by_lvl.most_common(): f.write(f"- {k or '(inconnu)'} : {v}\n")
        f.write("\n")
    if by_lang:
        f.write("## Par langue\n")
        for k,v in by_lang.most_common(): f.write(f"- {k or '(inconnu)'} : {v}\n")
print(f"✅ Rapport écrit : {OUT}")
