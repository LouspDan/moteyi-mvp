#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_rag_seed_catalog.py (v1.1, robuste CI/Windows)
- Tolère les entêtes/colonnes None produites par csv.DictReader quand le CSV est abîmé
- Sortie console "safe" (ASCII) pour éviter les UnicodeEncodeError en CI/Windows
- Modes:
    * strict (local): exige fichiers présents + checksum
    * ci/lenient   : ignore fichiers manquants, mais exige checksum
"""

import csv, os, sys, argparse
from pathlib import Path

CSV = Path("data/rag_seed/rag_seed_catalog.csv")
REQUIRED = [
    "id","titre","source_url","langue","grade_level","matiere","type_doc",
    "file_path","checksum","licence","ingested","validated","notes"
]
BASE = Path("data/rag_seed")  # racine des fichiers RAG

OK = "[OK]"
ERR = "[ERROR]"
INF = "[INFO]"

def resolve_path(p_raw: str) -> Path | None:
    if not p_raw:
        return None
    p_norm = p_raw.strip().replace("\\", os.sep).replace("//", "/")
    candidates = [Path(p_norm), BASE / p_norm]
    candidates = [Path(os.path.normpath(str(c))) for c in candidates]
    for c in candidates:
        if c.exists():
            return c
    return None

def fail(msg: str, code: int = 1) -> None:
    print(ERR, msg)
    sys.exit(code)

def main():
    # Tente d'assurer un encodage tolérant (évite crash emoji en Windows)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mode",
        choices=["strict","ci","lenient"],
        default=None,
        help="strict (local): exige fichiers; ci/lenient: ignore missing_file",
    )
    args = ap.parse_args()

    # Priorité: CLI > ENV > auto (GitHub Actions)
    mode = (
        args.mode
        or os.getenv("RAG_CHECK_MODE")
        or ("ci" if os.getenv("GITHUB_ACTIONS","").lower() == "true" else "strict")
    )
    mode = (mode or "strict").lower()
    print(INF, "RAG_CHECK_MODE =", mode)

    if not CSV.exists():
        fail("CSV non trouvé: data/rag_seed/rag_seed_catalog.csv")

    try:
        with CSV.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # headers: filtre les None et normalise
            raw_headers = [h for h in (reader.fieldnames or []) if h is not None]
            header = [(h or "").strip() for h in raw_headers]
            if not header:
                fail("CSV vide ou entête illisible")

            missing_cols = [c for c in REQUIRED if c not in header]
            if missing_cols:
                fail(f"Colonnes manquantes: {missing_cols}")

            rows = list(reader)
    except Exception as e:
        fail(f"Lecture CSV impossible: {e}")

    if not rows:
        fail("CSV sans lignes de données")

    problems: list[tuple[str,str]] = []
    missing_files = 0

    for row in rows:
        # lignes: filtre les clés None et normalise
        row_norm = { (k or "").strip().lower(): (v or "").strip()
                     for k, v in row.items() if k is not None }

        p_raw = row_norm.get("file_path", "")
        resolved = resolve_path(p_raw)

        if mode in ("ci","lenient"):
            # En CI: on ne bloque pas sur l’absence de fichiers
            if resolved is None:
                missing_files += 1
            if not row_norm.get("checksum", ""):
                problems.append(("no_checksum", p_raw))
            continue

        # Mode strict (local)
        if resolved is None:
            problems.append(("missing_file", p_raw))
            continue
        if not row_norm.get("checksum", ""):
            problems.append(("no_checksum", str(resolved)))

    if mode in ("ci","lenient"):
        if any(k == "no_checksum" for k, _ in problems):
            print(ERR, "Problèmes (checksums manquants):")
            for k,p in problems:
                if k == "no_checksum":
                    print("-", k, p)
            sys.exit(1)
        print(OK, f"Catalog OK (mode CI). Fichiers absents sur runner: {missing_files}")
        sys.exit(0)

    # mode strict
    if problems:
        print(ERR, "Problèmes détectés:")
        for k,p in problems:
            print("-", k, p)
        sys.exit(1)

    print(OK, f"Catalog OK — {len(rows)} lignes, chemins résolus et checksums présents (mode strict).")

if __name__ == "__main__":
    main()
