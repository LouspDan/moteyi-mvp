#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Align IDs to filename (with extension .pdf) for both:
- data/rag_seed/rag_seed_catalog.csv
- data/index/manifest.json

Contract: id == basename(file)  (e.g., "CURRICULUM-... .pdf")
Creates backups alongside originals before writing.
"""

import csv, json, shutil
from pathlib import Path

CATALOG = Path("data/rag_seed/rag_seed_catalog.csv")
MANIFEST = Path("data/index/manifest.json")

def backup(p: Path):
    bak = p.with_suffix(p.suffix + ".bak")
    shutil.copy2(p, bak)
    print(f"🗂️  Backup créé: {bak}")

def basename_from_row(row, file_col_candidates=("file","file_path","path")):
    for col in file_col_candidates:
        if col in row and row[col]:
            return Path(row[col]).name.strip()
    return ""

def align_catalog():
    print("→ Mise à jour catalog ...")
    backup(CATALOG)
    with CATALOG.open(encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        headers = [h for h in rdr.fieldnames] if rdr.fieldnames else []
        # s'assurer que 'id' est présent
        if "id" not in [h.lower() for h in headers]:
            raise SystemExit("❌ 'id' manquant dans catalog")

        rows = []
        for row in rdr:
            # normalise clés en lower pour manip, mais on réécrira avec headers d'origine
            lower = {k.lower(): v for k,v in row.items()}
            fn = basename_from_row(lower)
            if not fn:
                print(f"⚠️  Ligne sans chemin fichier exploitable: {row}")
                rows.append(row)
                continue
            # remplace l'id par le nom de fichier .pdf
            # trouve la clé 'id' réelle (respecte casse d'origine)
            id_key = next((h for h in headers if h.lower()=="id"), "id")
            row[id_key] = fn
            rows.append(row)

    with CATALOG.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows: w.writerow(r)
    print("✅ catalog aligné (id = filename.pdf)")

def align_manifest():
    print("→ Mise à jour manifest ...")
    backup(MANIFEST)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # manifest peut être list[dict] ou dict{docs:[...]}
    if isinstance(data, list):
        docs = data
    elif isinstance(data, dict) and isinstance(data.get("docs"), list):
        docs = data["docs"]
    else:
        raise SystemExit("❌ Format manifest non reconnu (liste ou dict{'docs':[...]}) attendu")

    for d in docs:
        file_val = str(d.get("file","")).strip()
        if file_val:
            d["id"] = Path(file_val).name.strip()

    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ manifest aligné (id = filename.pdf)")

if __name__ == "__main__":
    align_catalog()
    align_manifest()
    print("✨ Terminé.")
