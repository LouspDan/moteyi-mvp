#!/usr/bin/env python3
"""
Test simple pour vérifier la correspondance des chemins
"""
import json
import csv
from pathlib import Path

# Lire le manifest
with open('data/index/manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

# Lire le catalog
catalog_paths = []
with open('data/rag_seed/rag_seed_catalog.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('file_path'):
            catalog_paths.append(row['file_path'])

print("COMPARAISON DES CHEMINS")
print("="*50)
print(f"Premier chemin du manifest : {manifest[0]['file']}")
print(f"Premier chemin du catalog  : {catalog_paths[0]}")
print("-"*50)
print(f"Chemins identiques ? {manifest[0]['file'] == catalog_paths[0]}")
print("-"*50)

# Compter les correspondances
matches = 0
for doc in manifest:
    if doc['file'] in catalog_paths:
        matches += 1

print(f"\nCorrespondances trouvées : {matches}/{len(manifest)}")