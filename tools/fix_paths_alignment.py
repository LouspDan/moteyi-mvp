#!/usr/bin/env python3
"""
Aligne les chemins entre manifest.json et rag_seed_catalog.csv
"""
import json
import csv
from pathlib import Path

def fix_paths():
    print("🔧 ALIGNEMENT DES CHEMINS")
    print("="*50)
    
    # 1. Lire le manifest
    manifest_path = Path("data/index/manifest.json")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # 2. Corriger les chemins dans le manifest
    for doc in manifest:
        # Enlever le préfixe "data/rag_seed/" si présent
        if doc['file'].startswith('data/rag_seed/'):
            doc['file'] = doc['file'].replace('data/rag_seed/', '')
        # Remplacer / par \ pour correspondre au catalog
        doc['file'] = doc['file'].replace('/', '\\')
    
    # 3. Sauvegarder le manifest corrigé
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(manifest)} chemins corrigés dans manifest.json")
    return len(manifest)

if __name__ == "__main__":
    count = fix_paths()
    print(f"\n📝 Relancez maintenant : python tools/corpus_audit.py")