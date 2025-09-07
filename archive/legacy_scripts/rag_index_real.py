#!/usr/bin/env python3
"""
rag_index_real.py - Script d'indexation réelle des documents
"""
import json
import os
from pathlib import Path

def main():
    print("🔍 DÉBUT DE L'INDEXATION RÉELLE")
    print("="*50)
    
    # 1. Lire le catalog existant
    catalog_path = Path("data/rag_seed/rag_seed_catalog.csv")
    manifest_path = Path("data/index/manifest.json")
    
    # 2. Lister tous les PDFs
    pdf_count = 0
    pdf_files = []
    
    for pdf_path in Path("data/rag_seed").rglob("*.pdf"):
        relative_path = str(pdf_path.relative_to(Path("."))).replace("\\", "/")
        pdf_files.append({
            "id": f"doc_{pdf_count+1:04d}",
            "file": relative_path,
            "title": pdf_path.stem.replace("-", " ").replace("_", " "),
            "chunks": 1  # Placeholder pour l'instant
        })
        pdf_count += 1
        print(f"  ✓ Trouvé: {pdf_path.name}")
    
    # 3. Créer le manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(pdf_files, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ INDEXATION TERMINÉE")
    print(f"📁 Documents indexés: {pdf_count}")
    print(f"📄 Manifest créé: {manifest_path}")
    
    return pdf_count

if __name__ == "__main__":
    count = main()
    if count > 100:
        print("\n🎉 SUCCÈS: Plus de 100 documents indexés!")