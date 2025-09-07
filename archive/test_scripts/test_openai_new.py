# scripts/test_openai_new.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Recharger les variables d'environnement
load_dotenv(override=True)  # override=True pour forcer le rechargement

def test_new_api_key():
    print("\n" + "="*50)
    print("TEST NOUVELLE CLÉ OPENAI")
    print("="*50)
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'sk-VOTRE_NOUVELLE_CLE_ICI':
        print("[ERREUR] Mettez votre nouvelle clé dans .env")
        return False
    
    print(f"[INFO] Clé détectée: sk-...{api_key[-4:]}")
    
    try:
        # Initialiser le client
        client = OpenAI(api_key=api_key)
        
        # Test simple
        print("\n[TEST] Envoi d'une requête test...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un tuteur pédagogique."},
                {"role": "user", "content": "Explique simplement: 25 + 17 = ?"}
            ],
            max_tokens=100
        )
        
        explanation = response.choices[0].message.content
        
        print("\n[RÉPONSE GPT RÉELLE]:")
        print("-" * 40)
        print(explanation)
        print("-" * 40)
        
        # Info sur l'usage
        if hasattr(response, 'usage'):
            tokens = response.usage.total_tokens
            cost = tokens * 0.00015 / 1000  # Prix approximatif
            print(f"\n[TOKENS] {tokens} tokens utilisés")
            print(f"[COÛT] ~${cost:.5f}")
            print(f"[CRÉDIT] Il vous reste ~{5.0 - cost:.2f}$ de crédit")
        
        print("\n✅ NOUVELLE CLÉ FONCTIONNELLE !")
        return True
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        return False

if __name__ == "__main__":
    success = test_new_api_key()
    
    if success:
        print("\n[NEXT] La clé fonctionne ! Prêt pour le test réel complet")
    else:
        print("\n[ACTION] Vérifiez votre clé dans .env")