#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalise 'grade' et 'lang' pour un JSONL (1 objet/ligne).
- grade canonique : "2e_primaire"..."6e_primaire", "1e_secondaire"..."6e_secondaire"
  Gère variantes : "5e primaire", "5ème primaire", "P5", "5P", "1ère secondaire", "1er secondaire", "S1", etc.
- lang canonique : {français, lingala, swahili, kikongo, tshiluba, anglais}
  Gère variantes : "english/en/eng"→"anglais", "french/fr"→"français", etc.
"""
import json, os, shutil, re, unicodedata

SRC = "data/eval/gold.jsonl"
DST = "data/eval/gold.tmp.jsonl"
BAK = "data/eval/gold.backup.before_grade_lang.jsonl"

# ---------- helpers ----------
def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def canon_lang(lang: str) -> str:
    if not lang: return lang
    x = strip_accents(lang).lower().strip()
    x = x.replace("_", " ").replace("-", " ").replace(".", " ").strip()
    # synonymes
    if x in {"fr","francais","french"}: return "français"
    if x in {"en","eng","english"}:     return "anglais"
    if x in {"ln","lingala"}:           return "lingala"
    if x in {"kk","kikongo","kongo"}:   return "kikongo"
    if x in {"sw","swahili","kiswahili"}: return "swahili"
    if x in {"tsh","tshiluba","chiluba"}: return "tshiluba"
    # si déjà conforme (français, anglais, lingala, kikongo, swahili, tshiluba)
    # on remet l’accent si besoin
    if x == "francais": return "français"
    if x in {"anglais","lingala","kikongo","swahili","tshiluba"}: return x
    return lang  # inconnu → ne pas toucher

# tables rapides pour P/S compacts
PS_SHORT = {
    # primaire
    "p2":"2e_primaire","2p":"2e_primaire","p3":"3e_primaire","3p":"3e_primaire",
    "p4":"4e_primaire","4p":"4e_primaire","p5":"5e_primaire","5p":"5e_primaire",
    "p6":"6e_primaire","6p":"6e_primaire",
    # secondaire
    "s1":"1e_secondaire","1s":"1e_secondaire","s2":"2e_secondaire","2s":"2e_secondaire",
    "s3":"3e_secondaire","3s":"3e_secondaire","s4":"4e_secondaire","4s":"4e_secondaire",
    "s5":"5e_secondaire","5s":"5e_secondaire","s6":"6e_secondaire","6s":"6e_secondaire",
}

def canon_grade(grade: str) -> str:
    if not grade: return grade
    raw = grade
    x = strip_accents(grade).lower().strip()
    x = x.replace("_"," ").replace("-"," ").replace("."," ").strip()
    x = re.sub(r"\s+", " ", x)

    # Formats courts type P5/S3
    if x.replace(" ", "") in PS_SHORT:
        return PS_SHORT[x.replace(" ", "")]

    # capter nombre + libellé cycle
    # ex: "5eme primaire", "5e primaire", "5eme_primaire"
    m = re.search(r"\b(1|2|3|4|5|6)\s*(?:e|er|ere|eme|ème)?\s*(primaire|secondaire)\b", x)
    if m:
        n, cycle = int(m.group(1)), m.group(2)
        if cycle == "primaire" and n in range(2,7):
            return f"{n}e_primaire"
        if cycle == "secondaire" and n in range(1,7):
            return f"{n}e_secondaire"

    # variantes encore plus libres : "classe 5 primaire", "grade 3 secondaire"
    m = re.search(r"\b(1|2|3|4|5|6)\b.*\b(primaire|secondaire)\b", x)
    if m:
        n, cycle = int(m.group(1)), m.group(2)
        if cycle == "primaire" and n in range(2,7):
            return f"{n}e_primaire"
        if cycle == "secondaire" and n in range(1,7):
            return f"{n}e_secondaire"

    # rien de reconnu → ne pas casser, on renvoie original
    return raw

# ---------- process ----------
total = changed_g = changed_l = 0
with open(SRC, "r", encoding="utf-8") as fin, open(DST, "w", encoding="utf-8", newline="\n") as fout:
    for line in fin:
        line = line.strip()
        if not line: continue
        obj = json.loads(line); total += 1

        # lang
        old_l = obj.get("lang")
        new_l = canon_lang(old_l) if old_l is not None else old_l
        if new_l != old_l:
            obj["lang"] = new_l; changed_l += 1

        # grade
        old_g = obj.get("grade")
        new_g = canon_grade(old_g) if old_g is not None else old_g
        if new_g != old_g:
            obj["grade"] = new_g; changed_g += 1

        fout.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")

print(f"[normalize] lignes: {total}, lang modifiés: {changed_l}, grade modifiés: {changed_g}")

# sauvegarde + swap
os.makedirs(os.path.dirname(BAK), exist_ok=True)
shutil.copyfile(SRC, BAK)
shutil.move(DST, SRC)
print(f"[normalize] backup -> {BAK}")
print(f"[normalize] écrit  -> {SRC}")
