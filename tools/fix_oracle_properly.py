#!/usr/bin/env python3
"""
Correction appropriée du mode oracle dans rag_eval.py
"""
import shutil
from datetime import datetime

# Backup
shutil.copy('scripts/rag_eval.py', f'scripts/rag_eval.backup2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')

# Lire le fichier
with open('scripts/rag_eval.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver et remplacer la section du mode oracle
new_lines = []
for i, line in enumerate(lines):
    if 'if mode == "oracle":' in line:
        # Remplacer les 5 prochaines lignes par le code corrigé
        new_lines.append(line)
        new_lines.append('        # Mode oracle : utilise les expected_doc_ids du fichier gold\n')
        new_lines.append('        # Ceci simule un retriever parfait pour les tests\n')
        new_lines.append('        return []\n')
        # Skip les lignes originales
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith('if'):
            j += 1
        i = j - 1
    elif i < len(new_lines):
        continue
    else:
        new_lines.append(line)

# Écrire le fichier corrigé
with open('scripts/rag_eval.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)  # Restaurer l'original pour l'instant

print("✅ Restauration de l'original")
print("⚠️  Le mode oracle retourne une liste vide par design")
print("💡 Solution : implémenter un vrai retriever ou modifier retrieve_ids directement")