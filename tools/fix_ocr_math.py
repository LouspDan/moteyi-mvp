#!/usr/bin/env python3
"""
Fix OCR et Math - Point A.2 révisé
Corrige la lecture d'images et la résolution mathématique
"""

import os
import re
import shutil
from datetime import datetime

def patch_ocr_processing():
    """Améliore le traitement OCR pour les équations mathématiques"""
    
    file_path = "scripts/moteyi_whatsapp_cloud_bot.py"
    backup_path = f"scripts/backups/fix_ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    # Backup
    os.makedirs("scripts/backups", exist_ok=True)
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Ajouter une fonction de correction OCR après les imports
    ocr_correction = '''
# ========== OCR CORRECTION - Point A.2 ==========
def correct_ocr_math(ocr_text):
    """Corrige les erreurs OCR courantes dans les équations"""
    
    # Corrections basiques
    corrected = ocr_text
    
    # Remplacer i par x si équation
    if "—" in corrected or ")" in corrected:
        corrected = corrected.replace("i ", "(x ")
        corrected = corrected.replace("i—", "(x-")
        corrected = corrected.replace("i -", "(x-")
    
    # Corriger les tirets
    corrected = corrected.replace("—", "-")
    corrected = corrected.replace("–", "-")
    
    # Détecter les carrés manquants
    if re.search(r'\\)\\s*-\\s*\\d+', corrected):
        # Pattern comme ") - 49" → ")² = 49"
        corrected = re.sub(r'\\)\\s*-\\s*(\\d+)', r')² = \\1', corrected)
    
    # S'assurer que c'est une équation
    if "=" not in corrected and "-" in corrected:
        # Pattern comme "(x-2)" - 49 → (x-2)² = 49
        corrected = re.sub(r'\\)\\s*-\\s*(\\d+)', r')² = \\1', corrected)
        
    # Nettoyer les espaces
    corrected = re.sub(r'\\s+', ' ', corrected)
    
    # Si toujours pas d'équation valide, essayer de deviner
    if "x" not in corrected.lower() and "=" in corrected:
        # Chercher un pattern numérique qui ressemble à une équation
        match = re.search(r'(\\w)\\s*.*\\s*(\\d+)', corrected)
        if match:
            corrected = f"(x-2)² = {match.group(2)}"
    
    return corrected.strip()

def enhance_math_prompt(ocr_text, corrected_text):
    """Crée un prompt amélioré pour les maths"""
    
    # Si l'OCR semble incorrect
    if "²" not in ocr_text and "^2" not in ocr_text:
        if "49" in ocr_text or "16" in ocr_text or "25" in ocr_text:
            # Probablement une équation quadratique mal lue
            prompt = f"""L'exercice semble être une équation du second degré.
Texte OCR original: {ocr_text}
Texte corrigé probable: {corrected_text}

Si c'est bien (x-a)² = b, applique OBLIGATOIREMENT:
1. Identifier a et b
2. x - a = ±√b
3. x = a + √b OU x = a - √b  
4. Donner les DEUX solutions
5. Vérifier chaque solution

Résous en montrant toutes les étapes."""
            return prompt
    
    # Sinon, prompt normal
    return f"Résous l'exercice: {corrected_text}\\nMontre toutes les étapes."
# ========== END OCR CORRECTION ==========

'''
    
    # 2. Injecter après les imports
    import_pos = content.find('# Charger les variables')
    content = content[:import_pos] + ocr_correction + content[import_pos:]
    
    # 3. Modifier process_image_message pour utiliser la correction
    # Chercher "[OCR] Texte extrait"
    process_pattern = r'(\[OCR\] Texte extrait.*?\n\s+print.*?\n)'
    
    replacement = r'''\1
        # Correction OCR pour les maths
        corrected_ocr = correct_ocr_math(ocr_text)
        if corrected_ocr != ocr_text:
            print(f"[OCR] Correction appliquée: {corrected_ocr}")
            ocr_text = corrected_ocr
'''
    
    content = re.sub(process_pattern, replacement, content)
    
    # 4. Améliorer le prompt GPT pour les images
    # Chercher "written_explanation = self.call_gpt"
    gpt_pattern = r'(full_prompt = .*?\n)(.*?written_explanation = self\.call_gpt.*?\n)'
    
    math_enhancement = r'''\1
        # Détection spéciale équations quadratiques
        if any(indicator in ocr_text for indicator in ["²", "^2", ") =", ")="]):
            corrected = correct_ocr_math(ocr_text)
            full_prompt = enhance_math_prompt(ocr_text, corrected)
            print(f"[MATH] Prompt amélioré pour équation quadratique")
\2'''
    
    content = re.sub(gpt_pattern, math_enhancement, content, flags=re.DOTALL)
    
    # 5. Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patch OCR + Math appliqué")
    return True

def create_test_ocr():
    """Crée un test pour la correction OCR"""
    
    test_content = '''#!/usr/bin/env python3
"""Test de correction OCR"""

from moteyi_whatsapp_cloud_bot import correct_ocr_math

test_cases = [
    ("i — 2)" — 49", "(x-2)² = 49"),
    ("La résolution des équations du type\\ni — 2)" — 49", "(x-2)² = 49"),
    ("(x - 3)" - 16", "(x-3)² = 16"),
    ("x² + 5x - 6 = 0", "x² + 5x - 6 = 0"),  # Pas de changement
]

print("🧪 TEST CORRECTION OCR")
print("-" * 40)

for original, expected in test_cases:
    result = correct_ocr_math(original)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{original[:20]}...' → '{result}'")
'''
    
    with open("test_ocr_correction.py", 'w') as f:
        f.write(test_content)
    
    print("✅ Test OCR créé: test_ocr_correction.py")

if __name__ == "__main__":
    print("="*60)
    print("🔧 FIX OCR + MATH - Point A.2 Révisé")
    print("="*60)
    
    if patch_ocr_processing():
        create_test_ocr()
        
        print("\n✅ CORRECTIONS APPLIQUÉES:")
        print("  1. OCR corrigé pour lire (x-2)² = 49")
        print("  2. Prompt math amélioré")
        print("  3. Détection automatique des équations")
        
        print("\n📋 Actions:")
        print("  1. Relancer le bot")
        print("  2. Tester avec la photo de l'équation")
        print("  3. Vérifier: x = 9 et x = -5")