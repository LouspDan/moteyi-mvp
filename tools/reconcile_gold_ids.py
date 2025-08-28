#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Réconcilie data/eval/gold.jsonl avec data/index/manifest.json.

Fonctions clés :
- Normalisation 'subject' + mapping des niveaux (Primaire 1→6, 7e/8e EB, 1→4 HS).
- Déduction de la matière depuis file_path/nom si absente (guides, autres, etc.).
- Détection du niveau depuis 'file_path' des entrées du manifest.
- Index {(subject, level)} pour restreindre la recherche.
- Matching par chevauchement de tokens + fuzzy (difflib).
- Rapports : gold.reconciled.jsonl + artifacts/reconcile_report.csv.
- Option --apply pour écraser gold.jsonl (backup auto).

Usage :
  python tools/reconcile_gold_ids.py
  python tools/reconcile_gold_ids.py --apply
"""

import os
import re
import csv
import json
import argparse
import difflib
import unicodedata
from pathlib import Path

# Emplacements par défaut
MANIFEST = Path("data/index/manifest.json")
GOLD_IN  = Path("data/eval/gold.jsonl")
GOLD_OUT = Path("data/eval/gold.reconciled.jsonl")
REPORT   = Path("artifacts/reconcile_report.csv")

# -------------------- Normalisation -------------------- #

def strip_accents(s: str) -> str:
    if s is None:
        return ""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def norm_token(s: str) -> str:
    """Normalise en token alphanumérique (sans accents, minuscule)."""
    if s is None:
        return ""
    s = strip_accents(s).lower()
    return re.sub(r"[^a-z0-9]+", "", s)

def canon_subject(s: str) -> str:
    """Canonicalise les matières pour croiser gold ↔ manifest."""
    x = (s or "").strip().lower()
    x = strip_accents(x)

    # mathématiques
    if any(k in x for k in ["math", "mathematiques", "mathematique", "maths"]):
        return "mathématiques"

    # français
    if "francais" in x or "français" in x or x == "fr":
        return "français"

    # sciences (SVT, physique, chimie, etc.)
    if any(k in x for k in ["science", "svt", "biologie", "physique", "chimie", "spttic"]):
        return "sciences"

    # histoire-géo (et variantes EN)
    if ("histoire" in x and ("geo" in x or "géographie" in x)) or \
       ("history" in x and "geograph" in x):
        return "histoire-géo"

    # géographie seule
    if "geographie" in x or "géographie" in x:
        return "géographie"

    # fallback
    return (s or "").strip()

def grade_to_level_tokens(grade: str):
    """
    Mappe un grade 'gold' vers des tokens de niveau présents dans file_path du manifest.
    - Primaire : '5e_primaire' → ['5eme_PR', '5e_PR', '5eme', '5e']
    - Secondaire :
        1e_secondaire -> 7eme_EB
        2e_secondaire -> 8eme_EB
        3e_secondaire -> 1ere_HS
        4e_secondaire -> 2eme_HS
        5e_secondaire -> 3eme_HS
        6e_secondaire -> 4eme_HS
    Gère aussi si gold contient déjà '7eme_EB', etc.
    """
    if not grade:
        return []
    g = strip_accents(grade).lower()
    g = g.replace(" ", "_")

    # Primaire (ex: 5e_primaire, 5eme_primaire, 5e_annee_primaire)
    m = re.search(r"(\d)\s*e?m?e?_(?:an|annee|primaire)", g) or re.search(r"(\d)\s*e?_?primaire", g)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 6:
            return [f"{n}eme_PR", f"{n}e_PR", f"{n}eme", f"{n}e"]

    # Secondaire x e_secondaire
    m = re.search(r"(\d)\s*e?_?secondaire", g)
    if m:
        n = int(m.group(1))
        map_sec = {
            1: ["7eme_EB"],
            2: ["8eme_EB"],
            3: ["1ere_HS"],
            4: ["2eme_HS"],
            5: ["3eme_HS"],
            6: ["4eme_HS"],
        }
        return map_sec.get(n, [])

    # Déjà sous forme EB/HS/PR dans gold
    known = ["7eme_EB", "8eme_EB",
             "1ere_HS", "2eme_HS", "3eme_HS", "4eme_HS",
             "1eme_PR", "2eme_PR", "3eme_PR", "4eme_PR", "5eme_PR", "6eme_PR"]
    for lvl in known:
        if lvl.lower() in g:
            return [lvl]
    return []

def detect_level_from_manifest_path(file_path: str):
    """
    Extrait un token de niveau depuis file_path du manifest si présent.
    """
    if not file_path:
        return None
    x = strip_accents(file_path).lower().replace("\\", "/")
    # Tokens standardisés
    for lvl in ["7eme_eb","8eme_eb","1ere_hs","2eme_hs","3eme_hs","4eme_hs",
                "1eme_pr","2eme_pr","3eme_pr","4eme_pr","5eme_pr","6eme_pr"]:
        if f"/{lvl}/" in x:
            return lvl.replace("eb","EB").replace("hs","HS").replace("pr","PR")
    # fallback : patterns 1e..6e primaire
    for n in range(1,7):
        if f"/{n}eme_pr/" in x:
            return f"{n}eme_PR"
    return None

def infer_subject_from_path_or_name(file_path: str, doc_id: str) -> str:
    """Si le subject est vide dans le manifest, on infère depuis le chemin et le nom."""
    base = (file_path or "") + " " + (doc_id or "")
    base_n = strip_accents(base).lower()
    if re.search(r"\b(francais|français|francais-?|francais_?)\b", base_n):
        return "français"
    if re.search(r"\b(math|mathematique|mathematiques|maths)\b", base_n):
        return "mathématiques"
    if re.search(r"\b(svt|science|sciences|biologie|physique|chimie)\b", base_n):
        return "sciences"
    if re.search(r"\b(histoire).*(geo|geographie|géographie)|\b(history).*(geograph)", base_n):
        return "histoire-géo"
    if re.search(r"\b(geographie|géographie)\b", base_n):
        return "géographie"
    if re.search(r"\b(informatique|tic)\b", base_n):
        return "informatique"
    return ""

# -------------------- Index Manifest -------------------- #

def build_index_by_subject_and_level(manifest_entries):
    """
    Construit des index :
      - (subject_canon, level_token) -> [entries]
      - (subject_canon, '*') -> [entries] (fallback sujet)
    """
    by = {}
    for e in manifest_entries:
        fp = (e.get("file_path") or "")
        doc_id = e.get("doc_id") or ""
        subj = canon_subject(e.get("subject")) or infer_subject_from_path_or_name(fp, doc_id) or "autres"
        lvl = detect_level_from_manifest_path(fp) or ""
        key = (subj, lvl)
        by.setdefault(key, []).append(e)
        key_any = (subj, "*")
        by.setdefault(key_any, []).append(e)
    return by

def load_manifest():
    if not MANIFEST.exists():
        raise SystemExit(f"[ERR] Manifest manquant: {MANIFEST}")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_id = {e["doc_id"]: e for e in data}

    by_norm = {}
    for e in data:
        stem = os.path.splitext(e["doc_id"])[0]
        key = norm_token(stem)
        by_norm.setdefault(key, []).append(e)

    by_subj_level = build_index_by_subject_and_level(data)
    return data, by_id, by_norm, by_subj_level

# -------------------- Parsing expected ids -------------------- #

def parse_expected(item: str):
    """
    'file.pdf#p.12' -> ('file.pdf', 12)
    'file.pdf'      -> ('file.pdf', None)
    """
    if "#p." in item:
        name, p = item.split("#p.", 1)
        try:
            page = int(re.findall(r"\d+", p)[0])
        except Exception:
            page = None
        return name, page
    return item, None

# -------------------- Matching -------------------- #

def best_match(cand: str, subject: str, grade: str,
               manifest_entries, by_norm, by_subj_level):
    """
    Recherche le meilleur doc dans le manifest pour 'cand' (basename éventuellement placeholder),
    priorise les candidats filtrés par (subject canonicalisé, level dérivé du grade).
    Combine chevauchement de tokens + fuzzy.
    """
    target_stem = os.path.splitext(cand)[0]
    target_norm = norm_token(target_stem)
    subj_canon = canon_subject(subject)
    level_tokens = grade_to_level_tokens(grade)

    # 1) pools (subject+level → subject-only → global)
    pools = []
    if level_tokens:
        for lt in level_tokens:
            key = (subj_canon, lt)
            if key in by_subj_level:
                pools.append(by_subj_level[key])
    key_any = (subj_canon, "*")
    if key_any in by_subj_level:
        pools.append(by_subj_level[key_any])
    if not pools:
        pools.append(manifest_entries)

    # 2) score overlap tokens + bonus niveau + fuzzy
    def tokenize(s: str):
        s = strip_accents(s).lower()
        return set(re.findall(r"[a-z0-9]+", s))

    target_tokens = tokenize(target_stem)
    best = None
    best_score = -1.0

    for pool in pools:
        for e in pool:
            cand_name = e["doc_id"]
            cand_stem = os.path.splitext(cand_name)[0]
            cand_tokens = tokenize(cand_stem + " " + (e.get("file_path") or ""))

            overlap = len(target_tokens & cand_tokens)
            bonus = 0
            if level_tokens:
                if any(strip_accents(lt).lower() in strip_accents(e.get("file_path") or "").lower()
                       for lt in level_tokens):
                    bonus += 1
            dn = difflib.SequenceMatcher(None, norm_token(cand_stem), target_norm).ratio()
            fuzzy = dn * 2  # pondération

            score = overlap + bonus + fuzzy
            if score > best_score:
                best_score, best = score, e

        # seuil empirique : overlap>=1 + fuzzy correct
        if best and best_score >= 2.2:
            return best

    # fallback global si rien au-dessus du seuil
    return best

# -------------------- Main -------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Écrit gold.jsonl (backup) avec les corrections.")
    args = ap.parse_args()

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest_entries, by_id, by_norm, by_subj_level = load_manifest()

    total = 0
    fixed = 0
    unresolved = 0

    rows_report = []
    out_lines = []

    if not GOLD_IN.exists():
        raise SystemExit(f"[ERR] Fichier gold absent : {GOLD_IN}")

    with GOLD_IN.open("r", encoding="utf-8") as fin:
        for line_no, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                rows_report.append({
                    "id": f"line_{line_no}",
                    "status": "invalid_json",
                    "from": line[:120],
                    "to": "",
                    "subject": "",
                    "cycle_or_level": ""
                })
                continue

            total += 1
            subj = obj.get("subject", "")
            grade = obj.get("grade", "")
            level_hint = ",".join(grade_to_level_tokens(grade)) or ""

            exp = obj.get("expected_doc_ids", []) or []
            new_ids = []
            changed = False

            for raw in exp:
                doc, page = parse_expected(raw)

                # doc_id exact ?
                if doc in by_id:
                    new = f"{doc}#p.{page}" if page else doc
                    new_ids.append(new)
                    rows_report.append({
                        "id": obj.get("id", ""),
                        "status": "kept",
                        "from": raw,
                        "to": new,
                        "subject": canon_subject(subj),
                        "cycle_or_level": level_hint
                    })
                    continue

                # tentative de mapping
                match = best_match(doc, subj, grade, manifest_entries, by_norm, by_subj_level)
                if match:
                    new_doc = match["doc_id"]
                    mapped = f"{new_doc}#p.{page}" if page else new_doc
                    new_ids.append(mapped)
                    fixed += 1
                    changed = True
                    rows_report.append({
                        "id": obj.get("id", ""),
                        "status": "mapped",
                        "from": raw,
                        "to": mapped,
                        "subject": canon_subject(subj),
                        "cycle_or_level": level_hint
                    })
                else:
                    # introuvable → conserver tel quel
                    unresolved += 1
                    new_ids.append(raw)
                    rows_report.append({
                        "id": obj.get("id", ""),
                        "status": "unresolved",
                        "from": raw,
                        "to": raw,
                        "subject": canon_subject(subj),
                        "cycle_or_level": level_hint
                    })

            if changed:
                obj["expected_doc_ids"] = new_ids

            out_lines.append(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))

    # fichiers de sortie
    GOLD_OUT.parent.mkdir(parents=True, exist_ok=True)
    GOLD_OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    with REPORT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","status","from","to","subject","cycle_or_level"])
        w.writeheader()
        w.writerows(rows_report)

    print(f"[reconcile] total cases: {total}, mapped: {fixed}, unresolved: {unresolved}")
    print(f"[reconcile] out -> {GOLD_OUT}")
    print(f"[reconcile] report -> {REPORT}")

    if args.apply:
        # backup puis remplacement
        bak = GOLD_IN.with_suffix(".backup.before_reconcile.jsonl")
        bak.write_text(GOLD_IN.read_text(encoding="utf-8"), encoding="utf-8")
        GOLD_IN.write_text(GOLD_OUT.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[apply] backup -> {bak}")
        print(f"[apply] gold.jsonl updated")

if __name__ == "__main__":
    main()
