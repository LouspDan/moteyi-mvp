#!/usr/bin/env python3
"""Test de validation du fix GPT"""

import sys
sys.path.append('scripts')

from moteyi_whatsapp_cloud_bot import MoteyiCloudBot

def test_methods():
    """Vérifie que les méthodes nécessaires existent"""
    bot = MoteyiCloudBot()
    
    # Test 1: Vérifier que call_gpt existe
    assert hasattr(bot, 'call_gpt'), "❌ Méthode call_gpt manquante"
    print("✅ Méthode call_gpt présente")
    
    # Test 2: Vérifier que generate_explanation existe dans gpt
    assert hasattr(bot.gpt, 'generate_explanation'), "❌ Méthode generate_explanation manquante"
    print("✅ Méthode generate_explanation présente")
    
    # Test 3: Simuler un appel
    try:
        test_prompt = "Test: expliquer 2+2"
        result = bot.call_gpt(test_prompt, "fr")
        print(f"✅ Appel GPT fonctionnel: {len(result)} caractères générés")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 TEST DE VALIDATION - Point A.1")
    print("-" * 40)
    
    if test_methods():
        print("\n✅ TOUS LES TESTS PASSENT")
        print("Le bot devrait maintenant traiter les images correctement")
    else:
        print("\n❌ Des problèmes subsistent")