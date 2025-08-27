#!/usr/bin/env python3
import csv, os, sys
from pathlib import Path

CSV = Path("data/rag_seed/rag_seed_catalog.csv")

REQUIRED = [
    "id","titre","source_url","langue","grade_level","matiere","type_doc",
    "file_path","checksum","licence","ingested","validated","notes"
]

BASE = Path("data/rag_seed")  # racine des fichiers RAG

def fail(msg):
    print("❌", msg); sys.exit(1)

def resolve_path(p_raw: str) -> Path | None:
    """Tente plusieurs résolutions pour retrouver le fichier sur disque."""
    if not p_raw:
        return None
    # 1) normaliser les antislashs et espaces
    p_norm = p_raw.strip().replace("\\", os.sep).replace("//", "/")
    # Variantes candidates à tester
    candidates = []
    # as-is (si quelqu’un a déjà mis 'data/rag_seed/...' dans le CSV)
    candidates.append(Path(p_norm))
    # préfixer la base si chemin relatif (autres/..., primaire/...)
    candidates.append(BASE / p_norm)
    # normaliser
    candidates = [Path(os.path.normpath(str(c))) for c in candidates]
    for c in candidates:
        if c.exists():
            return c
    return None

if not CSV.exists():
    fail("CSV non trouvé: data/rag_seed/rag_seed_catalog.csv")

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
if not rows:
    fail("CSV vide")

header = [h.strip() for h in rows[0].keys()]
missing = [c for c in REQUIRED if c not in header]
if missing:
    fail(f"Colonnes manquantes: {missing}")

problems = []
for r in rows:
    p_raw = (r.get("file_path") or "")
    resolved = resolve_path(p_raw)
    if resolved is None:
        problems.append(("missing_file", p_raw))
        continue
    # Option: réécrire le chemin normalisé en mémoire pour d'autres checks
    # checksum obligatoire
    if not (r.get("checksum") or "").strip():
        problems.append(("no_checksum", str(resolved)))

if problems:
    print("❌ Problèmes détectés:")
    for k,p in problems:
        print("-", k, p)
    sys.exit(1)

print(f"✅ Catalog OK — {len(rows)} lignes, chemins résolus et checksums présents.")
