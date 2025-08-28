#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertit un catalogue CSV -> data/index/manifest.json
Usage:
  python tools/catalog_to_manifest.py \
    --catalog data/rag_seed/rag_seed_catalog.csv \
    --out data/index/manifest.json
"""
import csv, json, os, argparse
from pathlib import Path
from datetime import datetime

def norm_subject(s):
    s=(s or "").strip().lower()
    if s in {"mathematiques","math","maths"}: return "mathématiques"
    if s in {"francais","français"}: return "français"
    if s in {"svt","sciences","science"}: return "sciences"
    if s in {"histoire"}: return "histoire"
    if s in {"geographie","géographie","geo"}: return "géographie"
    if s in {"spttic","physique"}: return "sciences"
    return s or "autres"

def norm_cycle_from_path(p):
    p=p.lower()
    if "/primaire/" in p or "1ere_annee" in p or "2eme_annee" in p or "3eme_annee" in p or "4eme_annee" in p or "5eme_annee" in p or "6eme_annee" in p:
        return "primaire"
    if "/secondaire/" in p or "hs" in p or "7eme_eb" in p or "8eme_eb" in p:
        return "secondaire"
    return "autre"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, help="Chemin du CSV (ex: data/rag_seed/rag_seed_catalog.csv)")
    ap.add_argument("--out", default="data/index/manifest.json", help="Chemin de sortie JSON")
    args = ap.parse_args()

    catalog = Path(args.catalog)
    out_json = Path(args.out)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    if not catalog.exists():
        raise SystemExit(f"Catalogue absent: {catalog.resolve()}")

    entries=[]
    with catalog.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = (row.get("file_path") or row.get("path") or "").replace("\\","/").strip()
            if not file_path:
                continue  # ignore les lignes sans fichier local
            doc_id = os.path.basename(file_path)
            subject = norm_subject(row.get("matiere") or row.get("subject"))
            cycle = norm_cycle_from_path(file_path)
            title = (row.get("titre") or row.get("title") or os.path.splitext(doc_id)[0]).strip()
            checksum = (row.get("checksum") or row.get("sha256") or "").strip()
            source_url = (row.get("source_url") or row.get("url") or "").strip()
            ingested = (row.get("ingested") or datetime.utcnow().date().isoformat())

            entries.append({
                "doc_id": doc_id,
                "title": title,
                "cycle": cycle,
                "subject": subject,
                "year": None,
                "source_url": source_url,
                "downloaded_at": ingested,
                "checksum_sha256": checksum,
                "pages": None,
                "ocr": False,
                "file_path": file_path
            })

    out_json.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[manifest] {len(entries)} entrées -> {out_json}")

if __name__ == "__main__":
    main()
