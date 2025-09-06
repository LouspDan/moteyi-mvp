#!/usr/bin/env python3
"""
Fix du bug GPT dans moteyi_whatsapp_cloud_bot.py
Point A.1 - Sprint Phoenix
"""

import os
import shutil
from datetime import datetime

def fix_gpt_bug():
    """Corrige le bug de la méthode GPT manquante"""
    
    file_path = "scripts/moteyi_whatsapp_cloud_bot.py"
    backup_path = f"scripts/backups/moteyi_whatsapp_cloud_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    # 1. Créer une sauvegarde
    os.makedirs("scripts/backups", exist_ok=True)
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup créé: {backup_path}")
    
    # 2. Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 3. Corriger la ligne 430 (index 429)
    if "generate_explanation_with_prompt" in lines[429]:
        old_line = lines[429]
        # Remplacer par l'appel correct
        lines[429] = "        written_explanation = self.call_gpt(full_prompt, user_language)\n"
        
        print("✅ Ligne 430 corrigée:")
        print(f"   AVANT: {old_line.strip()}")
        print(f"   APRÈS: {lines[429].strip()}")
        
        # 4. Sauvegarder
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Fichier corrigé avec succès!")
        return True
    else:
        print("⚠️ La ligne 430 ne contient pas l'erreur attendue")
        print(f"   Contenu actuel: {lines[429].strip()}")
        return False

if __name__ == "__main__":
    print("🔧 FIX BUG GPT - Point A.1")
    print("-" * 40)
    
    if fix_gpt_bug():
        print("\n✅ CORRECTION APPLIQUÉE")
        print("👉 Relancez le bot pour tester")
    else:
        print("\n⚠️ Vérification manuelle nécessaire")