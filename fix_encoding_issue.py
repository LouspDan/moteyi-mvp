#!/usr/bin/env python3
import os

files_to_fix = [
    "scripts/active/rag_connector.py",
    "scripts/active/moteyi_whatsapp_cloud_bot.py",
    "scripts/active/language_manager.py"
]

for filepath in files_to_fix:
    print(f"Correction de {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filtrer les lignes problématiques
    clean_lines = []
    skip_next = 0
    
    for i, line in enumerate(lines):
        # Supprimer les lignes de reconfiguration d'encodage problématiques
        if 'sys.stdout = io.TextIOWrapper' in line:
            continue
        if 'sys.stderr = io.TextIOWrapper' in line:
            continue
        if 'sys.stdout.reconfigure' in line:
            continue
        if 'sys.stderr.reconfigure' in line:
            continue
        if 'import io' in line and i < 10:  # Supprimer import io ajouté
            continue
        if 'Fix encoding pour Windows' in line:
            continue
        if 'if sys.platform == "win32":' in line and i < 15:
            skip_next = 2  # Skip les 2 prochaines lignes du bloc
            continue
        
        if skip_next > 0:
            skip_next -= 1
            continue
            
        clean_lines.append(line)
    
    # Écrire le fichier nettoyé
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✓ {filepath} nettoyé")

print("\n✅ Corrections appliquées")
