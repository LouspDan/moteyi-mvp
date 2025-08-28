# tools/corpus_audit.py (v2.1)
# -*- coding: utf-8 -*-
"""
Audit du corpus RAG Moteyi (v2.1)
- Compare la réalité disque (PDFs) au manifest et au catalog
- Matching robuste par basename (ex: Guide.pdf)
- Tolère catalog: 'file' OU 'file_path' OU 'path'
- Tolère manifest: list[doc] OU dict{'docs':[...]} OU dict{'documents':[...]}
- Tolère CSV abîmé (entêtes/colonnes None)
- Produit:
    * reports/corpus_audit_report.json
    * reports/files_to_index_priority.csv
"""

from __future__ import annotations
import json
import csv
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

CATALOG = Path("data/rag_seed/rag_seed_catalog.csv")
MANIFEST = Path("data/index/manifest.json")
DATA_DIR = Path("data/rag_seed")
REPORTS_DIR = Path("reports")

FILE_COL_CANDIDATES = ["file", "file_path", "path"]

# ---------- console sûre ----------
def is_utf8_stdout() -> bool:
    enc = getattr(__import__("sys").stdout, "encoding", None)
    return bool(enc and enc.lower().replace("-", "") == "utf8")

EMOJI_OK   = "✅" if is_utf8_stdout() else "[OK]"
EMOJI_ERR  = "❌" if is_utf8_stdout() else "[ERROR]"
EMOJI_WARN = "⚠️" if is_utf8_stdout() else "[WARN]"

# ---------- helpers ----------
def norm_path(p: str) -> str:
    return re.sub(r"[\\/]+", "/", (p or "").strip())

def _load_manifest_docs() -> List[dict]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"{EMOJI_ERR} manifest introuvable: {MANIFEST}")
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"{EMOJI_ERR} manifest illisible: {e}")

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("docs"), list):
            return data["docs"]
        if isinstance(data.get("documents"), list):
            return data["documents"]
    raise ValueError(f"{EMOJI_ERR} format manifest non reconnu (list | dict{{'docs'|'documents':[...]}})")

def load_manifest_basenames() -> Tuple[Set[str], Dict[str, dict]]:
    docs = _load_manifest_docs()
    names: Set[str] = set()
    by_name: Dict[str, dict] = {}
    for d in docs:
        fid = str(d.get("id", "")).strip()
        ffile = norm_path(str(d.get("file", "")).strip())
        base = Path(fid or Path(ffile).name).name
        if not base:
            continue
        names.add(base)
        by_name[base] = d
    return names, by_name

def _detect_catalog_file_col(headers_lower: Set[str]) -> str:
    for c in FILE_COL_CANDIDATES:
        if c in headers_lower:
            return c
    return ""

def load_catalog_basenames() -> Tuple[Set[str], Dict[str, dict]]:
    if not CATALOG.exists():
        raise FileNotFoundError(f"{EMOJI_ERR} catalog introuvable: {CATALOG}")

    basenames: Set[str] = set()
    rows_by_base: Dict[str, dict] = {}

    with CATALOG.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        # entête: filtre les None
        headers = [h for h in (r.fieldnames or []) if h is not None]
        headers_lower = {h.lower() for h in headers}
        file_col = _detect_catalog_file_col(headers_lower)
        id_col = "id" if "id" in headers_lower else ""

        for row in r:
            # lignes: filtre les clés None
            row_items = [(k, v) for k, v in row.items() if k is not None]
            row_lower = { (k or "").lower(): (v or "").strip() for k, v in row_items }

            base = ""
            if id_col and row_lower.get("id"):
                base = Path(row_lower["id"]).name
            elif file_col and row_lower.get(file_col):
                base = Path(norm_path(row_lower[file_col])).name

            if base:
                basenames.add(base)
                rows_by_base[base] = row  # garde la version brute utile pour debug

    return basenames, rows_by_base

def scan_fs_basenames() -> Tuple[Set[str], Dict[str, str]]:
    names: Set[str] = set()
    relmap: Dict[str, str] = {}
    for pdf in DATA_DIR.rglob("*.pdf"):
        rel = norm_path(str(pdf.relative_to(Path("."))))
        base = Path(rel).name
        names.add(base)
        relmap.setdefault(base, rel)
    return names, relmap

def derive_category_from_path(rel_path: str) -> str:
    parts = norm_path(rel_path).split("/")
    try:
        i = parts.index("rag_seed")
        tail = parts[i + 1 : i + 3]
        return "/".join(tail) if tail else "root"
    except ValueError:
        return "root"

# ---------- audit ----------
def audit_corpus() -> dict:
    # essayer d'assurer l'encodage
    try:
        import sys
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("🔎 AUDIT DU CORPUS RAG - MOTEYI MVP")
    print("=" * 50)

    fs_names, fs_relmap = scan_fs_basenames()
    cat_names, cat_rows = load_catalog_basenames()
    man_names, man_docs = load_manifest_basenames()

    print(f"\n📁 PDFs trouvés sur disque : {len(fs_names)}")
    print(f"📋 Documents dans catalog  : {len(cat_names)}")
    print(f"📄 Documents dans manifest : {len(man_names)}")

    indexed = fs_names & man_names
    not_indexed = fs_names - man_names
    missing_on_disk = man_names - fs_names

    in_catalog_not_in_manifest = cat_names - man_names
    in_manifest_not_in_catalog = man_names - cat_names

    coverage_rate = (len(indexed) / len(fs_names) * 100) if fs_names else 0.0
    missing_count = len(in_catalog_not_in_manifest) + len(not_indexed)

    categories = defaultdict(lambda: {"total": 0, "indexed": 0})
    for base in fs_names:
        rel = fs_relmap.get(base, "")
        cat = derive_category_from_path(rel)
        categories[cat]["total"] += 1
        if base in man_names:
            categories[cat]["indexed"] += 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "corpus_audit_report.json"
    priority_path = REPORTS_DIR / "files_to_index_priority.csv"

    clean_categories = {
        cat: {
            "total": stats["total"],
            "indexed": stats["indexed"],
            "coverage": (stats["indexed"] / stats["total"] * 100) if stats["total"] else 0.0,
        }
        for cat, stats in categories.items()
    }

    report = {
        "summary": {
            "total_pdfs_on_disk": len(fs_names),
            "total_in_catalog": len(cat_names),
            "total_in_manifest": len(man_names),
            "indexed_count": len(indexed),
            "coverage_rate": coverage_rate,
            "missing_count": missing_count,
        },
        "missing_in_manifest": sorted(list(in_catalog_not_in_manifest)),
        "orphan_on_disk_not_in_manifest": sorted(list(not_indexed)),
        "missing_on_disk_from_manifest": sorted(list(missing_on_disk)),
        "missing_in_catalog": sorted(list(in_manifest_not_in_catalog)),
        "categories": clean_categories,
        "recommendations": [],
    }

    if in_catalog_not_in_manifest:
        report["recommendations"].append(
            f"{EMOJI_ERR} {len(in_catalog_not_in_manifest)} docs du catalog non indexés (à ajouter au manifest)."
        )
    if not_indexed:
        report["recommendations"].append(
            f"{EMOJI_WARN} {len(not_indexed)} PDFs sur disque mais absents du manifest (orphelins indexation)."
        )
    if in_manifest_not_in_catalog:
        report["recommendations"].append(
            f"{EMOJI_WARN} {len(in_manifest_not_in_catalog)} docs du manifest absents du catalog (compléter le CSV)."
        )

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    with priority_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["basename", "status", "hint"])
        for base in sorted(in_catalog_not_in_manifest)[:100]:
            hint = fs_relmap.get(base, "")
            w.writerow([base, "in_catalog_not_in_manifest", hint])
        for base in sorted(not_indexed)[:100]:
            hint = fs_relmap.get(base, "")
            w.writerow([base, "on_disk_not_in_manifest", hint])

    print("\n📊 RÉSUMÉ DE L'AUDIT")
    print("-" * 50)
    print(f"📁 PDFs trouvés sur disque     : {report['summary']['total_pdfs_on_disk']}")
    print(f"📋 Documents dans le catalog   : {report['summary']['total_in_catalog']}")
    print(f"✅ Documents indexés (manifest): {report['summary']['indexed_count']}")
    print(f"📈 Taux de couverture          : {report['summary']['coverage_rate']:.1f}%")
    print(f"❌ Documents non indexés       : {report['summary']['missing_count']}")

    print("\n📂 RÉPARTITION PAR CATÉGORIE")
    print("-" * 50)
    for cat, stats in sorted(clean_categories.items()):
        cov = stats["coverage"]
        status = "✅" if cov >= 80 else ("⚠️" if cov >= 50 else "❌")
        print(f"{status} {cat:25s}: {stats['indexed']}/{stats['total']} ({cov:.0f}%)")

    if in_catalog_not_in_manifest:
        print("\n❌ EXEMPLES — Catalog non indexés (max 5)")
        print("-" * 50)
        for base in list(sorted(in_catalog_not_in_manifest))[:5]:
            print(f"  - {base}")

    if not_indexed:
        print("\n⚠️ EXEMPLES — Sur disque mais pas manifest (max 5)")
        print("-" * 50)
        for base in list(sorted(not_indexed))[:5]:
            print(f"  - {base}")

    if in_manifest_not_in_catalog:
        print("\n🟠 EXEMPLES — Manifest non présents dans catalog (max 5)")
        print("-" * 50)
        for base in list(sorted(in_manifest_not_in_catalog))[:5]:
            print(f"  - {base}")

    print(f"\n📄 Rapport détaillé : {report_path}")
    print(f"📋 Liste prioritaire: {priority_path}")

    return report

if __name__ == "__main__":
    try:
        audit_corpus()
    except Exception as e:
        print(f"{EMOJI_ERR} ERREUR: {e}")
        raise
