#!/usr/bin/env python3
"""
Corrige les IDs dans le manifest pour correspondre aux noms de fichiers
"""
import json
from pathlib import Path

def fix_ids():
    print("🔧 CORRECTION DES IDS DANS LE MANIFEST")
    print("="*50)
    
    # Lire le manifest
    manifest_path = Path("data/index/manifest.json")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Corriger les IDs
    for doc in manifest:
        # Extraire le nom du fichier depuis le chemin
        file_path = doc['file']
        # Prendre juste le nom du fichier sans le chemin
        file_name = file_path.split('\\')[-1]
        # Utiliser ce nom comme ID
        doc['id'] = file_name
    
    # Sauvegarder le manifest corrigé
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(manifest)} IDs corrigés")
    print(f"Exemple: {manifest[0]['id']}")
    
    return len(manifest)

if __name__ == "__main__":
    fix_ids()
    print("\n📝 Relancez maintenant : python scripts/rag_eval.py --gold data/eval/gold.jsonl")