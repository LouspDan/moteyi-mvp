#!/usr/bin/env python3
"""
Fix de la logique mathématique - Point A.2
Sprint Phoenix - Amélioration globale des capacités mathématiques
"""

import os
import re
import shutil
from datetime import datetime

def detect_math_type(text):
    """
    Détecte le type de problème mathématique
    Retourne: (type, niveau_complexité, indices_contextuels)
    """
    text_lower = text.lower()
    
    # Patterns de détection
    patterns = {
        'equation_quadratique': [
            r'\(.*\)\s*[\²2]\s*=',
            r'x[\²2]\s*[+-]',
            r'équation.*second.*degré'
        ],
        'equation_lineaire': [
            r'\d*x\s*[+-]\s*\d+\s*=',
            r'résou.*équation',
            r'trouve.*x'
        ],
        'calcul_arithmetique': [
            r'^\d+\s*[+\-*/×÷]\s*\d+',
            r'calcul',
            r'combien'
        ],
        'fraction': [
            r'\d+/\d+',
            r'fraction',
            r'simplifi'
        ],
        'pourcentage': [
            r'\d+\s*%',
            r'pourcentage',
            r'pourcent'
        ],
        'geometrie': [
            r'aire|périmètre|volume',
            r'triangle|carré|cercle|rectangle',
            r'angle|côté'
        ],
        'probleme_texte': [
            r'si\s+.*alors',
            r'sachant que',
            r'un.*a\s+\d+.*combien'
        ]
    }
    
    # Identifier le type principal
    for math_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, text_lower):
                return math_type
    
    return 'general'

def create_enhanced_math_prompt(ocr_text, context_rag=None, language="fr"):
    """
    Crée un prompt optimisé selon le type de mathématiques détecté
    """
    
    math_type = detect_math_type(ocr_text)
    
    # Base commune pour tous les prompts
    base_prompt = """Tu es MOTEYI, tuteur expert en mathématiques du système éducatif RDC.
    
RÈGLES CRITIQUES :
1. TOUJOURS montrer CHAQUE étape de calcul
2. VÉRIFIER les résultats en substituant
3. Utiliser la notation mathématique RDC
4. Adapter l'explication au niveau détecté
5. NE JAMAIS donner de réponse incorrecte"""
    
    # Prompts spécialisés par type
    specialized_prompts = {
        'equation_quadratique': f"""
{base_prompt}

EXERCICE : {ocr_text}

MÉTHODE pour équations du type (x-a)² = b :
1. Identifier a et b dans l'équation
2. Appliquer : x - a = ±√b
3. Donc : x = a + √b OU x = a - √b
4. Donner les DEUX solutions
5. Vérifier en remplaçant x dans l'équation originale

EXEMPLE CORRECT :
(x-2)² = 49
→ x-2 = ±√49 = ±7
→ x = 2+7 = 9 OU x = 2-7 = -5
Vérification: (9-2)² = 7² = 49 ✓ et (-5-2)² = (-7)² = 49 ✓

Résous maintenant l'exercice en suivant cette méthode.""",
        
        'equation_lineaire': f"""
{base_prompt}

EXERCICE : {ocr_text}

MÉTHODE pour équations linéaires :
1. Regrouper les x d'un côté
2. Regrouper les nombres de l'autre
3. Diviser pour isoler x
4. Vérifier la solution

Montre chaque transformation.""",
        
        'calcul_arithmetique': f"""
{base_prompt}

CALCUL : {ocr_text}

Effectue le calcul étape par étape.
Utilise la méthode appropriée (posée si nombres grands).
Vérifie le résultat.""",
        
        'probleme_texte': f"""
{base_prompt}

PROBLÈME : {ocr_text}

MÉTHODE :
1. Identifier les données
2. Identifier ce qu'on cherche
3. Choisir l'opération appropriée
4. Effectuer le calcul
5. Rédiger la réponse complète avec unités

Résous en expliquant ton raisonnement.""",
        
        'general': f"""
{base_prompt}

QUESTION : {ocr_text}

Analyse le problème et résous-le de manière pédagogique.
Montre toutes les étapes."""
    }
    
    prompt = specialized_prompts.get(math_type, specialized_prompts['general'])
    
    # Ajouter le contexte RAG si disponible
    if context_rag and context_rag.get('found'):
        prompt += f"\n\nCONTEXTE CURRICULUM RDC :\n{context_rag['prompt_enhancement']}"
    
    # Ajouter les consignes de langue
    if language == "ln":
        prompt += "\n\nRéponds en lingala, utilise des termes mathématiques simples."
    elif language == "sw":
        prompt += "\n\nJibu kwa Kiswahili, tumia maneno rahisi ya hisabati."
    
    return prompt

def patch_bot_file():
    """
    Modifie moteyi_whatsapp_cloud_bot.py pour intégrer la logique mathématique améliorée
    """
    
    file_path = "scripts/moteyi_whatsapp_cloud_bot.py"
    backup_path = f"scripts/backups/moteyi_whatsapp_cloud_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    # 1. Créer une sauvegarde
    os.makedirs("scripts/backups", exist_ok=True)
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup créé: {backup_path}")
    
    # 2. Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Ajouter les nouvelles fonctions après les imports
    new_functions = '''
# ========== MATH LOGIC ENHANCEMENT - Point A.2 ==========
def detect_math_type(text):
    """Détecte le type de problème mathématique"""
    text_lower = text.lower()
    
    if any(p in text_lower for p in ['(', ')', '²', 'second degré']):
        if '²' in text or '^2' in text:
            return 'equation_quadratique'
    elif '=' in text and any(c in text for c in 'xyz'):
        return 'equation_lineaire'
    elif any(op in text for op in ['+', '-', '*', '/', '×', '÷']):
        return 'calcul_arithmetique'
    else:
        return 'general'

def create_math_enhanced_prompt(ocr_text, context_rag=None):
    """Crée un prompt mathématique optimisé"""
    math_type = detect_math_type(ocr_text)
    
    if math_type == 'equation_quadratique':
        return f"""Tu es un tuteur expert. 
Exercice: {ocr_text}

Pour (x-a)² = b:
1. x-a = ±√b
2. x = a±√b (DEUX solutions)
3. Vérifie chaque solution

Résous étape par étape."""
    
    return f"Résous: {ocr_text}\\nMontre toutes les étapes."
# ========== END MATH ENHANCEMENT ==========

'''
    
    # 4. Injecter après les imports
    import_end = content.find('# Charger les variables')
    if import_end > 0:
        content = content[:import_end] + new_functions + content[import_end:]
    
    # 5. Modifier process_image_message pour utiliser la nouvelle logique
    # Chercher la ligne avec "full_prompt = "
    pattern = r'full_prompt = f".*?"'
    replacement = 'full_prompt = create_math_enhanced_prompt(ocr_text, context)'
    content = re.sub(pattern, replacement, content, count=1)
    
    # 6. Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Bot patché avec logique mathématique améliorée")
    return True

def create_test_file():
    """Crée un fichier de test pour valider les corrections"""
    
    test_content = '''#!/usr/bin/env python3
"""Test de validation - Logique mathématique Point A.2"""

test_cases = [
    {
        "input": "(x-2)² = 49",
        "expected": ["x = 9", "x = -5"],
        "type": "equation_quadratique"
    },
    {
        "input": "(x-3)² = 16",
        "expected": ["x = 7", "x = -1"],
        "type": "equation_quadratique"
    },
    {
        "input": "3x + 5 = 20",
        "expected": ["x = 5"],
        "type": "equation_lineaire"
    },
    {
        "input": "659 + 341",
        "expected": ["1000"],
        "type": "calcul_arithmetique"
    }
]

def test_math_detection():
    from fix_math_logic import detect_math_type
    
    print("🧪 Test de détection des types...")
    for case in test_cases:
        detected = detect_math_type(case["input"])
        status = "✅" if detected == case["type"] else "❌"
        print(f"{status} {case['input'][:20]}... → {detected}")

if __name__ == "__main__":
    print("="*50)
    print("TEST LOGIQUE MATHÉMATIQUE - Point A.2")
    print("="*50)
    test_math_detection()
'''
    
    with open("test_math_fix.py", "w", encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ Fichier de test créé: test_math_fix.py")

def main():
    """Fonction principale d'application du fix"""
    
    print("="*60)
    print("🔧 FIX LOGIQUE MATHÉMATIQUE - Point A.2")
    print("="*60)
    
    try:
        # 1. Patcher le bot
        print("\n1️⃣ Application du patch...")
        if not patch_bot_file():
            print("❌ Échec du patch")
            return False
        
        # 2. Créer les tests
        print("\n2️⃣ Création des tests...")
        create_test_file()
        
        # 3. Instructions finales
        print("\n" + "="*60)
        print("✅ FIX APPLIQUÉ AVEC SUCCÈS!")
        print("="*60)
        print("\n📋 Prochaines étapes:")
        print("1. Relancer le bot: python scripts/moteyi_whatsapp_cloud_bot.py")
        print("2. Tester avec l'équation: (x-2)² = 49")
        print("3. Vérifier que les solutions sont: x=9 et x=-5")
        print("\n⚠️  Si problème, restaurer depuis scripts/backups/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()