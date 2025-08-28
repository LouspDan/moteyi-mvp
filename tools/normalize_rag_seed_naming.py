#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalise la nomenclature des PDF dans data/rag_seed/** et met à jour:
- rag_seed_catalog.csv (mêmes colonnes, file_path mis à jour)
- data/index/manifest.json (doc_id = nouveau basename)

Par défaut: DRY-RUN. Ajoutez --apply pour renommer réellement.
"""
import re, csv, json, argparse, shutil
from pathlib import Path
from datetime import datetime

CATALOG_DEFAULT = Path("data/rag_seed/rag_seed_catalog.csv")
MANIFEST_OUT = Path("data/index/manifest.json")

# ---------- helpers ----------
def norm_subj(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("mathematiques","mathématiques").replace("maths","mathématiques")
    s = s.replace("francais","français")
    # grands regroupements
    if "math" in s: return "mathématiques"
    if "franç" in s or "franc" in s: return "français"
    if s in {"svt","sciences","science","biologie","physique","chimie"}: return "sciences"
    if "histoire" in s and "geo" in s: return "histoire-géo"
    if "géographie" in s or "geographie" in s: return "géographie"
    if "informatique" in s: return "informatique"
    return s or "autres"

def detect_cycle_from_path(p: str) -> str:
    x = p.lower()
    if "/primaire/" in x: return "primaire"
    if "/secondaire/" in x: return "secondaire"
    if "7eme_eb" in x or "8eme_eb" in x: return "secondaire"
    if "hs" in x: return "secondaire"
    return "autre"

def detect_level_from_path(p: str) -> str | None:
    x = p.lower()
    for lvl in ["7eme_eb","8eme_eb","1ere_hs","2eme_hs","3eme_hs","4eme_hs"]:
        if lvl in x: return lvl
    return None

def detect_type_from_name(name: str) -> str | None:
    n = name.lower()
    if "guide" in n: return "Guide"
    if "manuel" in n: return "Manuel"
    if "cahier" in n: return "Cahier"
    if re.search(r"\bpe7\b", n): return "PE7"
    if re.search(r"\bpe8\b", n): return "PE8"
    if "programme" in n or "programmes-educatifs" in n: return "Programme"
    return None

def detect_year(text: str) -> str | None:
    m = re.search(r"(20\d{2})", text)
    return m.group(1) if m else None

def compose_doc_id(year, cycle, level, subj, typ):
    parts = []
    if year: parts.append(year)
    if cycle and cycle!="autre": parts.append(cycle)
    if level: parts.append(level)
    if subj and subj!="autres": parts.append(subj.replace(" ", "-"))
    if typ: parts.append(typ)
    base = "_".join(parts) if parts else "document"
    return f"{base}.pdf"

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=str(CATALOG_DEFAULT),
                    help="CSV catalogue d'entrée (data/rag_seed/rag_seed_catalog.csv)")
    ap.add_argument("--apply", action="store_true",
                    help="Appliquer réellement les renommages (sinon DRY-RUN)")
    ap.add_argument("--manifest", default=str(MANIFEST_OUT),
                    help="Chemin de sortie du manifest JSON")
    args = ap.parse_args()

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        raise SystemExit(f"Catalogue absent: {catalog_path.resolve()}")

    rows = list(csv.DictReader(catalog_path.open("r", encoding="utf-8")))
    updates = []
    seen_targets = set()

    for row in rows:
        file_path = (row.get("file_path") or row.get("path") or "").replace("\\","/")
        if not file_path or not file_path.lower().endswith(".pdf"):
            continue
        src = Path(file_path)
        if not src.exists():
            # entrée cassée → on ignore
            continue

        # Détection des champs
        cycle = detect_cycle_from_path(file_path)
        level = detect_level_from_path(file_path)
        subj = norm_subj(row.get("matiere") or row.get("subject") or src.parent.name)
        typ  = detect_type_from_name(src.name)
        year = detect_year(src.name)

        # Compose nouveau doc_id + destination dans le même dossier
        new_name = compose_doc_id(year, cycle, level, subj, typ)

        # Évite collisions: si déjà vu, suffixe incrémental
        base = new_name[:-4]
        k = 2
        while new_name in seen_targets:
            new_name = f"{base}_{k}.pdf"; k += 1
        seen_targets.add(new_name)

        dst = src.with_name(new_name)
        updates.append((src, dst, cycle, level, subj, typ, year))

    # Affichage DRY-RUN
    print(f"[plan] {len(updates)} fichiers candidats au renommage")
    for src, dst, cycle, level, subj, typ, year in updates[:10]:
        print(f"  - {src.name}  ->  {dst.name}  ({cycle},{level},{subj},{typ},{year})")
    if not args.apply:
        print("\n[DRY-RUN] Aucun fichier renommé. Relance avec --apply pour appliquer.")
        return

    # Renommage + mise à jour CSV + manifest
    # Renomme sur disque
    for src, dst, *_ in updates:
        if src.name != dst.name:
            try:
                src.rename(dst)
                print(f"[RENAMED] {src.name} -> {dst.name}")
            except Exception as e:
                print(f"[SKIP] {src} -> {dst}: {e}")

    # Réécriture du CSV (mêmes colonnes)
    out_rows = []
    for row in rows:
        file_path = (row.get("file_path") or row.get("path") or "").replace("\\","/")
        if not file_path.lower().endswith(".pdf"):
            out_rows.append(row); continue
        src = Path(file_path)
        if not src.exists():
            # peut avoir été renommé → chercher le nouveau par dossier
            parent = src.parent
            # heuristique simple: si une cible a ce parent et même stem partiel
            # (sinon on laisse l'ancien chemin)
            candidates = [dst for (s,d, *_)
                          in updates if s.parent == parent]
            # si un seul pdf dans ce dossier, on le prend
            if len(candidates)==1:
                row["file_path"] = str(candidates[0]).replace("\\","/")
            out_rows.append(row)
        else:
            out_rows.append(row)

    # Sauvegarde CSV (backup + overwrite)
    bak = catalog_path.with_suffix(".backup.csv")
    shutil.copyfile(catalog_path, bak)
    with catalog_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_rows[0].keys())
        w.writeheader()
        w.writerows(out_rows)
    print(f"[OK] CSV mis à jour -> {catalog_path} (backup: {bak.name})")

    # Manifest JSON (doc_id = basename)
    manifest = []
    for row in out_rows:
        file_path = (row.get("file_path") or row.get("path") or "").replace("\\","/")
        if not file_path or not file_path.lower().endswith(".pdf"):
            continue
        p = Path(file_path)
        doc_id = p.name
        manifest.append({
            "doc_id": doc_id,
            "title": (row.get("titre") or row.get("title") or p.stem),
            "cycle": detect_cycle_from_path(file_path),
            "subject": norm_subj(row.get("matiere") or row.get("subject") or p.parent.name),
            "year": detect_year(p.name),
            "source_url": (row.get("source_url") or row.get("url") or ""),
            "downloaded_at": (row.get("ingested") or datetime.utcnow().date().isoformat()),
            "checksum_sha256": (row.get("checksum") or row.get("sha256") or ""),
            "pages": None,
            "ocr": False,
            "file_path": file_path
        })
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] manifest -> {MANIFEST_OUT} (entries={len(manifest)})")

if __name__ == "__main__":
    main()
