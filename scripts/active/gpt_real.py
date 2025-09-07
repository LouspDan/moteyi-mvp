# scripts/gpt_real.py
import os
import openai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class RealGPT:
    """
    Le cerveau de Moteyi - Génère de vraies explications pédagogiques
    Comme un tuteur patient qui adapte ses explications
    """
    
    def __init__(self):
        # Récupérer la clé depuis .env
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key or self.api_key == 'sk-VOTRE_CLE_ICI':
            print("[ATTENTION] Clé OpenAI non configurée!")
            print("[INFO] Ajoutez votre clé dans le fichier .env")
            print("[INFO] OPENAI_API_KEY=sk-xxxxx")
            self.mock_mode = True
        else:
            openai.api_key = self.api_key
            self.mock_mode = False
            print("[GPT] OpenAI initialisé avec succès")
        
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def generate_explanation(self, exercise_text, language="francais"):
        """
        Génère une explication pédagogique pour un exercice
        """
        
        if self.mock_mode:
            return self._mock_explanation(exercise_text, language)
        
        # Prompts adaptés pour chaque langue
        system_prompts = {
            "francais": """Tu es Moteyi, un tuteur pédagogique africain bienveillant.
            Tu expliques les exercices simplement aux enfants de primaire en RDC.
            Utilise des exemples avec des mangues, bananes, francs congolais.
            Sois encourageant et patient.""",
            
            "lingala": """Tu es Moteyi, tuteur pédagogique africain.
            Explique en lingala simple aux enfants.
            Utilise des exemples de la vie quotidienne congolaise.
            Sois patient et encourageant."""
        }
        
        user_prompts = {
            "francais": f"""Voici un exercice d'école primaire:
            {exercise_text}
            
            Explique étape par étape comment le résoudre.
            Maximum 100 mots, langage simple pour un enfant de 8-10 ans.""",
            
            "lingala": f"""Tala exercice oyo:
            {exercise_text}
            
            Limbolá ndenge ya kosala yango na lingala pé na pasi te.
            Pesá exemple ya mboka."""
        }
        
        try:
            print(f"[GPT] Génération d'explication en {language}...")
            
            # Appel à l'API OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompts.get(language, system_prompts["francais"])},
                    {"role": "user", "content": user_prompts.get(language, user_prompts["francais"])}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content
            print(f"[GPT] Explication générée ({len(explanation)} caractères)")
            
            return explanation
            
        except Exception as e:
            print(f"[ERREUR GPT] {e}")
            return self._mock_explanation(exercise_text, language)
    
    def _mock_explanation(self, exercise_text, language):
        """Fallback si pas de clé API"""
        if "25" in exercise_text and "17" in exercise_text:
            if language == "lingala":
                return "Mpo na 25 + 17: Tanga 20 + 10 = 30, pe 5 + 7 = 12. Donc 30 + 12 = 42!"
            else:
                return "Pour 25 + 17: D'abord 20 + 10 = 30, puis 5 + 7 = 12. Donc 30 + 12 = 42!"
        return f"[Mode démo] Explication pour: {exercise_text[:30]}..."

# Test du module
def test_gpt():
    print("\n" + "="*50)
    print("TEST GPT (Génération d'explications)")
    print("="*50)
    
    gpt = RealGPT()
    
    # Test avec l'exercice de math
    exercise = "25 + 17 = ?"
    
    print(f"\n[EXERCICE] {exercise}")
    
    # Test en français
    print("\n[TEST 1] Explication en français:")
    print("-" * 30)
    explanation_fr = gpt.generate_explanation(exercise, "francais")
    print(explanation_fr)
    
    # Test en lingala
    print("\n[TEST 2] Explication en lingala:")
    print("-" * 30)
    explanation_ln = gpt.generate_explanation(exercise, "lingala")
    print(explanation_ln)
    
    if gpt.mock_mode:
        print("\n[INFO] Mode mock actif - Configurez votre clé OpenAI pour de vraies explications")

if __name__ == "__main__":
    test_gpt()