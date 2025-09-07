#!/usr/bin/env python3
import os
import sys

# Forcer UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Parcourir et corriger les fichiers
files_to_fix = [
    "scripts/active/rag_connector.py",
    "scripts/active/moteyi_whatsapp_cloud_bot.py",
    "scripts/active/language_manager.py"
]

for filepath in files_to_fix:
    print(f"Correction de {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter l'import en début de fichier si pas présent
    if "sys.stdout.reconfigure" not in content:
        import_block = """import sys
import io
# Fix encoding pour Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
        # Insérer après les imports existants
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                continue
            else:
                if i > 0:  # Après les imports
                    lines.insert(i, import_block)
                    break
        
        content = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {filepath} corrigé")

print("\n✅ Corrections d'encodage appliquées")
