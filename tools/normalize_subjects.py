#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalise uniquement le champ 'subject' dans un JSONL (1 objet/ligne).
Remplacements:
- "science"           -> "sciences"
- "mathematics"       -> "mathématiques"
- "history-geography" -> "histoire-géo"
- "histoire"          -> "histoire-géo"
"""
import json, os, sys, shutil

SRC = "data/eval/gold.jsonl"
DST = "data/eval/gold.normalized.jsonl"
BAK = "data/eval/gold.backup.jsonl"

MAP = {
    "science": "sciences",
    "mathematics": "mathématiques",
    "history-geography": "histoire-géo",
    "histoire": "histoire-géo",
}

changed = 0
total = 0

with open(SRC, "r", encoding="utf-8") as fin, open(DST, "w", encoding="utf-8", newline="\n") as fout:
    for line in fin:
        line = line.strip()
        if not line:
            continue
        total += 1
        obj = json.loads(line)
        subj = obj.get("subject", "")
        subj_norm = subj.strip().lower()
        if subj_norm in MAP:
            obj["subject"] = MAP[subj_norm]
            changed += 1
        # ré-écriture propre, sans espaces superflus
        fout.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")

print(f"[normalize] total lignes: {total}, subjects modifiés: {changed}")
# Sauvegarde et remplacement atomique
shutil.copyfile(SRC, BAK)
shutil.move(DST, SRC)
print(f"[normalize] backup -> {BAK}")
print(f"[normalize] écrit -> {SRC}")
