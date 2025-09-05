# scripts/tts_real.py
from gtts import gTTS
import os
from pathlib import Path
from datetime import datetime

class RealTTS:
    """
    La voix de Moteyi - Transforme le texte en audio
    Comme un prof qui lit l'explication à haute voix
    """
    
    def __init__(self):
        self.output_dir = Path("data/audio_responses")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print("[TTS] Module vocal initialisé")
    
    def text_to_speech(self, text, language="fr"):
        """
        Convertit du texte en fichier audio MP3
        """
        
        # Mapping des langues
        lang_map = {
            "francais": "fr",
            "lingala": "fr",  # Pas de lingala, on utilise français
            "swahili": "sw",
            "english": "en"
        }
        
        tts_lang = lang_map.get(language, "fr")
        
        try:
            print(f"[TTS] Génération audio en {language}...")
            
            # Créer l'audio
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            
            # Nom unique pour le fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = self.output_dir / f"response_{timestamp}_{language}.mp3"
            
            # Sauvegarder
            tts.save(str(audio_file))
            
            # Vérifier la taille
            file_size = audio_file.stat().st_size / 1024  # En KB
            print(f"[TTS] Audio créé: {audio_file.name} ({file_size:.1f} KB)")
            
            return str(audio_file)
            
        except Exception as e:
            print(f"[ERREUR TTS] {e}")
            return None
    
    def estimate_duration(self, text):
        """
        Estime la durée de l'audio (approximatif)
        """
        # Environ 150 mots par minute en lecture normale
        words = len(text.split())
        duration = (words / 150) * 60  # En secondes
        return duration

# Test du module
def test_tts():
    print("\n" + "="*50)
    print("TEST TTS (Synthèse Vocale)")
    print("="*50)
    
    tts = RealTTS()
    
    # Textes de test
    texts = {
        "francais": "Pour calculer 25 plus 17, décompose: 20 plus 10 égale 30, puis 5 plus 7 égale 12. Donc 30 plus 12 égale 42!",
        "lingala": "Mpo na kosala 25 na 17, tanga boye: 20 na 10 esali 30, pe 5 na 7 esali 12. Donc 30 na 12 esali 42!"
    }
    
    for lang, text in texts.items():
        print(f"\n[TEST] {lang.upper()}")
        print(f"Texte: {text[:50]}...")
        
        # Générer l'audio
        audio_path = tts.text_to_speech(text, lang)
        
        if audio_path and os.path.exists(audio_path):
            print(f"[OK] Audio généré: {audio_path}")
            
            # Estimer la durée
            duration = tts.estimate_duration(text)
            print(f"[DUREE] Environ {duration:.1f} secondes")
        else:
            print("[ERREUR] Échec génération audio")
    
    print("\n[INFO] Les fichiers MP3 sont dans data/audio_responses/")
    print("[INFO] Vous pouvez les écouter avec n'importe quel lecteur")

if __name__ == "__main__":
    # Installer gTTS si nécessaire
    try:
        import gtts
    except ImportError:
        print("[INSTALL] Installation de gTTS...")
        os.system("pip install gtts")
        print("[OK] gTTS installé, relancez le script")
        exit()
    
    test_tts()