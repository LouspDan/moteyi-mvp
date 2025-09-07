#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validateur dual-mode du corpus RAG (v1.3)
- CI mode (CI=true ou RAG_CHECK_MODE=ci): contrat de structure (sans PDFs)
- Local mode: vérifie la présence des fichiers (avec PDFs)

Nouveautés v1.3:
- Recherche résiliente des PDFs en LOCAL:
  * si la colonne fichier pointe vers un chemin inexistant, on retombe
    sur l'ID (qui = basename.pdf) et on le recherche dans data/rag_seed/**
  * index des basenames construit en 1 passe pour vitesse O(1)
- Tolère CSV abîmé (en-têtes None) + sortie console safe (sans emoji si cp1252)
"""
import os, sys, csv, json, re
from pathlib import Path
from typing import Dict, List, Set, Tuple

CATALOG = Path("data/rag_seed/rag_seed_catalog.csv")
MANIFEST = Path("data/index/manifest.json")
ARTIFACTS_DIR = Path("artifacts")
DATA_BASE = Path("data/rag_seed")

REQUIRED_COLS_BASE = {"id"}
FILE_COL_CANDIDATES = ["file", "file_path", "path"]

def is_utf8_stdout() -> bool:
    enc = getattr(sys.stdout, "encoding", None)
    return bool(enc and enc.lower().replace("-", "") == "utf8")

EMOJI_OK   = "✅" if is_utf8_stdout() else "[OK]"
EMOJI_ERR  = "❌" if is_utf8_stdout() else "[ERROR]"
EMOJI_WARN = "⚠️" if is_utf8_stdout() else "[WARN]"

def norm_path(p: str) -> str:
    return re.sub(r"[\\/]+", "/", (p or "").strip())

def safe_lower(k) -> str:
    return (k or "").lower()

# ---------- Manifest (CI) ----------
def load_manifest_ids() -> Set[str]:
    if not MANIFEST.exists():
        print(f"{EMOJI_ERR} E_MANIFEST: {MANIFEST} introuvable")
        sys.exit(2)
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"{EMOJI_ERR} E_MANIFEST_JSON: manifest illisible ({e})")
        sys.exit(2)

    if isinstance(data, list):
        docs = data
    elif isinstance(data, dict):
        if isinstance(data.get("docs"), list):
            docs = data["docs"]
        elif isinstance(data.get("documents"), list):
            docs = data["documents"]
        else:
            print(f"{EMOJI_ERR} E_MANIFEST_FMT: format non reconnu (liste ou dict{{'docs'|'documents':[...]}})")
            sys.exit(2)
    else:
        print(f"{EMOJI_ERR} E_MANIFEST_FMT: format non reconnu")
        sys.exit(2)

    ids = {str(d.get("id", "")).strip() for d in docs}
    ids.discard("")
    return ids

# ---------- Catalog (lecture générique) ----------
def detect_file_column(lower_headers: Set[str]) -> str:
    for cand in FILE_COL_CANDIDATES:
        if cand in lower_headers:
            return cand
    return ""

def load_catalog_rows() -> List[Dict[str, str]]:
    if not CATALOG.exists():
        print(f"{EMOJI_ERR} E_CATALOG: {CATALOG} introuvable")
        sys.exit(2)
    try:
        with CATALOG.open(encoding="utf-8") as f:
            r = csv.DictReader(f)
            headers_raw = [h for h in (r.fieldnames or []) if h is not None]
            lower_headers = {h.lower() for h in headers_raw}

            missing_base = REQUIRED_COLS_BASE - lower_headers
            if missing_base:
                print(f"{EMOJI_ERR} E_SCHEMA: colonnes manquantes {sorted(missing_base)}")
                print(f"   Colonnes trouvées: {sorted(lower_headers)}")
                sys.exit(2)

            file_col = detect_file_column(lower_headers)
            if not file_col:
                print(f"{EMOJI_ERR} E_SCHEMA_FILECOL: aucune colonne fichier trouvée.")
                print(f"   Attendu l'une de: {FILE_COL_CANDIDATES}")
                print(f"   Colonnes trouvées: {sorted(lower_headers)}")
                sys.exit(2)

            rows: List[Dict[str, str]] = []
            for row in r:
                row_items = [(k, v) for k, v in row.items() if k is not None]
                row_norm = {safe_lower(k): (v or "").strip() for k, v in row_items}
                row_norm["id"] = row_norm.get("id", "").strip()
                # Normalise vers 'file' (peut être vide ou non-exploitable)
                row_norm["file"] = norm_path(row_norm.get(file_col, ""))
                rows.append(row_norm)
            return rows
    except SystemExit:
        raise
    except Exception as e:
        print(f"{EMOJI_ERR} E_CATALOG_READ: lecture catalog impossible ({e})")
        sys.exit(2)

# ---------- CI mode ----------
def validate_ci_mode(rows: List[Dict[str, str]], manifest_ids: Set[str]) -> bool:
    ok = True
    seen, dup = set(), set()
    for r in rows:
        rid = r.get("id", "")
        if rid in seen: dup.add(rid)
        seen.add(rid)
    if dup:
        print(f"{EMOJI_ERR} E_DUP_ID: IDs dupliqués dans catalog: {sorted(list(dup))[:5]}...")
        ok = False

    cat_ids = {r.get("id","") for r in rows if r.get("id","")}
    miss_in_manifest = cat_ids - manifest_ids
    miss_in_catalog = manifest_ids - cat_ids
    if miss_in_manifest:
        ex = list(miss_in_manifest)[:3]
        print(f"{EMOJI_ERR} E_ID_MISS_MANIFEST: {len(miss_in_manifest)} IDs dans catalog mais absents du manifest (ex: {ex})")
        ok = False
    if miss_in_catalog:
        ex = list(miss_in_catalog)[:3]
        print(f"{EMOJI_ERR} E_ID_MISS_CATALOG: {len(miss_in_catalog)} IDs dans manifest mais absents du catalog (ex: {ex})")
        ok = False

    try:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        meta = {
            "mode": "ci",
            "count_catalog": len(cat_ids),
            "count_manifest": len(manifest_ids),
        }
        (ARTIFACTS_DIR / "catalog_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"{EMOJI_WARN} WARN_ARTIFACT: écriture artifacts impossible ({e})")
    return ok

# ---------- LOCAL mode (résilient) ----------
def build_fs_index() -> Dict[str, str]:
    """
    Construit un index {basename_lower: chemin_relatif_depuis_racine}
    pour tous les PDFs sous data/rag_seed.
    """
    index: Dict[str, str] = {}
    for p in DATA_BASE.rglob("*.pdf"):
        rel = norm_path(str(p.relative_to(Path("."))))
        base = Path(rel).name.lower()
        # conserve le 1er si doublon — suffisant pour la validation
        index.setdefault(base, rel)
    return index

def resolve_pdf_path(rel_from_csv: str, id_value: str, fs_index: Dict[str, str]) -> Tuple[bool, str]:
    """
    Résout un chemin PDF fiable en LOCAL.
    1) si rel_from_csv existe sous data/rag_seed, on le garde
    2) sinon on tente par l'ID (basename.pdf) via l'index FS
    """
    # 1) Chemin direct
    if rel_from_csv:
        # gérer les cas où rel inclut déjà 'data/rag_seed/' ou non
        p1 = DATA_BASE / rel_from_csv
        if p1.exists():
            return True, norm_path(str(p1.relative_to(Path("."))))
        if rel_from_csv.startswith("data/rag_seed/"):
            p2 = Path(rel_from_csv)
            if p2.exists():
                return True, norm_path(str(p2.relative_to(Path("."))))

    # 2) Fallback via ID (doit être un basename .pdf)
    base = (id_value or "").strip()
    if base and not base.lower().endswith(".pdf"):
        base += ".pdf"
    rel = fs_index.get(base.lower(), "")
    if rel:
        return True, rel

    return False, rel_from_csv or base or ""

def validate_local_mode(rows: List[Dict[str, str]]) -> bool:
    ok = True
    missing = []

    fs_index = build_fs_index()  # {basename_lower: rel_path}

    for r in rows:
        rid = r.get("id", "")
        rel = r.get("file", "")
        found, resolved = resolve_pdf_path(rel, rid, fs_index)
        if not found:
            missing.append(resolved or rel or rid)
            ok = False

    if missing:
        # Affiche seulement quelques exemples pour guider
        print(f"{EMOJI_ERR} E_FILE_MISSING: {len(missing)} fichier(s) introuvable(s). Exemples: {missing[:3]}")
    else:
        print(f"{EMOJI_OK} Validation locale: tous les fichiers référencés sont présents.")
    return ok

# ---------- Entrée ----------
def main() -> int:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    is_ci = bool(os.environ.get("CI")) or os.environ.get("RAG_CHECK_MODE") == "ci"
    rows = load_catalog_rows()
    if is_ci:
        manifest_ids = load_manifest_ids()
        ok = validate_ci_mode(rows, manifest_ids)
    else:
        ok = validate_local_mode(rows)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
