#!/usr/bin/env python3
"""
FIX D'URGENCE - Correction de l'erreur ocr_text
"""

import os
import shutil
from datetime import datetime

def emergency_fix():
    """Corrige l'erreur NameError urgente"""
    
    file_path = "scripts/moteyi_whatsapp_cloud_bot.py"
    
    # Backup d'urgence
    backup_path = f"scripts/backups/emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    os.makedirs("scripts/backups", exist_ok=True)
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup d'urgence: {backup_path}")
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Corriger ligne 419 (index 418)
    # AVANT: full_prompt = create_math_enhanced_prompt(ocr_text, context)
    # APRÈS: Il faut revenir à l'original ou corriger avec 'text'
    
    for i, line in enumerate(lines):
        # Trouver et corriger la ligne problématique dans process_text_message
        if "create_math_enhanced_prompt(ocr_text, context)" in line:
            # Dans process_text_message, c'est 'text' pas 'ocr_text'
            lines[i] = line.replace("ocr_text", "text")
            print(f"✅ Ligne {i+1} corrigée: ocr_text → text")
            
        # Aussi chercher dans process_image_message pour s'assurer que c'est correct
        if i > 500 and "create_math_enhanced_prompt" in line and "process_image_message" in "".join(lines[i-50:i]):
            # Ici c'est bien ocr_text
            if "text," in line and "ocr_text" not in line:
                lines[i] = line.replace("text,", "ocr_text,")
                print(f"✅ Ligne {i+1} dans process_image: text → ocr_text")
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Fix d'urgence appliqué!")
    return True

def restore_original():
    """Option pour restaurer la version originale"""
    
    print("\n⚠️  RESTAURATION DE LA VERSION ORIGINALE")
    
    # Chercher la dernière sauvegarde avant les modifications
    backups = sorted([f for f in os.listdir("scripts/backups") if f.endswith(".py")])
    
    if backups:
        print(f"Sauvegardes disponibles:")
        for i, backup in enumerate(backups[-5:]):  # Montrer les 5 dernières
            print(f"  {i+1}. {backup}")
        
        choice = input("\nChoisir le numéro de la sauvegarde à restaurer (ou 'skip'): ")
        
        if choice != 'skip' and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(backups):
                backup_file = f"scripts/backups/{backups[-5:][idx]}"
                shutil.copy2(backup_file, "scripts/moteyi_whatsapp_cloud_bot.py")
                print(f"✅ Restauré depuis: {backup_file}")
                return True
    
    return False

def create_proper_fix():
    """Crée le fix mathématique correct"""
    
    fix_content = '''#!/usr/bin/env python3
"""Fix mathématique CORRIGÉ - Point A.2"""

import os
import re
from datetime import datetime

def apply_math_fix():
    """Applique correctement le fix mathématique"""
    
    file_path = "scripts/moteyi_whatsapp_cloud_bot.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Corriger process_text_message (ligne ~419)
    # Remplacer la ligne problématique
    old_pattern = r'full_prompt = create_math_enhanced_prompt\\(ocr_text, context\\)'
    new_line = 'full_prompt = f"{gpt_prefix}\\\\n\\\\n{context[\\'prompt_enhancement\\']}" if context[\\'found\\'] else f"{gpt_prefix}\\\\n\\\\nQuestion: {text}\\\\n\\\\nRéponds de manière pédagogique."'
    
    content = re.sub(old_pattern, new_line, content)
    
    # 2. Pour process_image_message, ajouter la logique math
    # Chercher "written_explanation = self.call_gpt"
    image_pattern = r'(written_explanation = self\\.call_gpt\\(full_prompt, user_language\\))'
    
    math_logic = """
        # Détection équation quadratique
        if '²' in ocr_text or '^2' in ocr_text or 'second degré' in ocr_text.lower():
            math_prompt = f\"\"\"Tu es un tuteur expert en mathématiques.
Exercice: {ocr_text}

MÉTHODE OBLIGATOIRE pour (x-a)² = b:
1. Identifier a et b
2. Appliquer: x-a = ±√b
3. Solutions: x = a+√b ET x = a-√b
4. Donner les DEUX solutions
5. Vérifier chaque solution

Résous étape par étape.\"\"\"
            written_explanation = self.call_gpt(math_prompt, user_language)
        else:
            written_explanation = self.call_gpt(full_prompt, user_language)"""
    
    content = re.sub(image_pattern, math_logic, content)
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fix mathématique appliqué correctement")

if __name__ == "__main__":
    apply_math_fix()
'''
    
    with open("fix_math_correct.py", 'w', encoding='utf-8') as f:
        f.write(fix_content)
    
    print("✅ Nouveau fix créé: fix_math_correct.py")

if __name__ == "__main__":
    print("="*60)
    print("🚨 FIX D'URGENCE - Correction NameError")
    print("="*60)
    
    print("\nOptions:")
    print("1. Appliquer le fix d'urgence")
    print("2. Restaurer une sauvegarde")
    print("3. Créer un nouveau fix correct")
    
    choice = input("\nChoisir (1/2/3): ")
    
    if choice == "1":
        emergency_fix()
        print("\n✅ Bot devrait fonctionner maintenant")
        print("👉 Relancez le bot pour tester")
        
    elif choice == "2":
        if restore_original():
            print("\n✅ Version originale restaurée")
            print("👉 Relancez le bot")
            
    elif choice == "3":
        create_proper_fix()
        print("\n👉 Exécutez: python fix_math_correct.py")
    
    else:
        print("❌ Choix invalide")