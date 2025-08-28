#!/usr/bin/env python3
"""
Reconstruit le catalog CSV à partir du manifest.json
Pour synchroniser les deux sources
"""
import json
import csv
from pathlib import Path
from datetime import datetime

def rebuild_catalog():
    print("🔧 RECONSTRUCTION DU CATALOG")
    print("="*50)
    
    # 1. Lire le manifest
    manifest_path = Path("data/index/manifest.json")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # 2. Sauvegarder l'ancien catalog
    catalog_path = Path("data/rag_seed/rag_seed_catalog.csv")
    backup_path = Path(f"data/rag_seed/rag_seed_catalog.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    if catalog_path.exists():
        import shutil
        shutil.copy2(catalog_path, backup_path)
        print(f"✅ Backup créé: {backup_path}")
    
    # 3. Créer le nouveau catalog
    with open(catalog_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'titre', 'source_url', 'langue', 'grade_level', 'matiere', 
                     'type_doc', 'file_path', 'checksum', 'licence', 'ingested', 
                     'validated', 'notes', 'cycle', 'niveau', 'source', 'path']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for doc in manifest:
            # Extraire les métadonnées du chemin
            file_path = doc['file']
            
            # Déterminer la langue
            langue = 'français'
            if 'lingala' in file_path.lower():
                langue = 'lingala'
            elif 'kiswahili' in file_path.lower() or 'swahili' in file_path.lower():
                langue = 'swahili'
            elif 'ciluba' in file_path.lower() or 'tshiluba' in file_path.lower():
                langue = 'tshiluba'
            
            # Déterminer le niveau
            grade = ''
            if 'primaire' in file_path:
                grade = 'primaire'
            elif 'secondaire' in file_path or any(x in file_path for x in ['_HS', '_EB']):
                grade = 'secondaire'
            elif 'CRS' in file_path:
                grade = 'CRS'
            
            row = {
                'id': doc['id'],
                'titre': doc['title'],
                'source_url': 'https://edu-nc.gouv.cd/programmes-scolaires',
                'langue': langue,
                'grade_level': grade,
                'matiere': '',
                'type_doc': 'manuel' if 'manuel' in file_path.lower() else 'guide',
                'file_path': file_path,
                'checksum': '',
                'licence': 'MEPSP',
                'ingested': '2025-08-28',
                'validated': 'True',
                'notes': 'Synchronisé avec manifest',
                'cycle': '',
                'niveau': '',
                'source': '',
                'path': file_path
            }
            writer.writerow(row)
    
    print(f"✅ Nouveau catalog créé avec {len(manifest)} entrées")
    return len(manifest)

if __name__ == "__main__":
    count = rebuild_catalog()
    print(f"\n📝 Vérifiez maintenant avec : python tools/corpus_audit.py")