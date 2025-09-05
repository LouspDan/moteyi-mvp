# scripts/moteyi_bot_final.py
"""
MOTEYI BOT - VERSION FINALE INTÉGRÉE
Tous les composants réels assemblés
"""

import os
import time
from datetime import datetime
from pathlib import Path

# Selenium pour WhatsApp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Nos modules
from ocr_real_english import RealOCR
from gpt_real import RealGPT
from tts_real import RealTTS

class MoteyiBotFinal:
    """
    Le bot Moteyi complet avec tous les vrais composants
    """
    
    def __init__(self):
        print("\n" + "="*50)
        print("MOTEYI BOT - VERSION FINALE")
        print("="*50)
        print("[INIT] Chargement des modules...")
        
        # Initialiser tous les composants
        self.ocr = RealOCR()
        self.gpt = RealGPT()
        self.tts = RealTTS()
        
        # Setup WhatsApp
        self.driver = self.setup_whatsapp()
        
        # Statistiques
        self.stats = {
            "images_processed": 0,
            "total_time": 0,
            "success_count": 0
        }
        
        print("[OK] Tous les modules chargés!")
        print("-"*50)
    
    def setup_whatsapp(self):
        """Configure WhatsApp Web"""
        print("[WHATSAPP] Connexion...")
        options = webdriver.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-logging')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://web.whatsapp.com')
        
        time.sleep(5)
        print("[OK] WhatsApp connecté")
        return driver
    
    def capture_screen(self):
        """Capture l'écran actuel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"data/received_images/capture_{timestamp}.png"
        self.driver.save_screenshot(image_path)
        return image_path
    
    def send_whatsapp_message(self, message):
        """Envoie un message sur WhatsApp"""
        try:
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            if inputs:
                input_box = inputs[-1]
                input_box.click()
                time.sleep(0.5)
                input_box.send_keys(Keys.CONTROL + "a")
                input_box.send_keys(Keys.DELETE)
                input_box.send_keys(message)
                input_box.send_keys(Keys.ENTER)
                return True
        except:
            return False
    
    def process_exercise(self, image_path, language="francais"):
        """
        PIPELINE COMPLET : Image → OCR → GPT → TTS → WhatsApp
        """
        print(f"\n{'='*50}")
        print(f"TRAITEMENT EXERCICE - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        # 1. OCR - Lecture de l'exercice
        print("\n[1/4] OCR - Lecture de l'image...")
        ocr_text = self.ocr.read_image(image_path)
        
        if not ocr_text:
            print("[ERREUR] Aucun texte détecté")
            return None
        
        print(f"[OCR] Lu: {ocr_text[:50]}...")
        
        # 2. Détection du type d'exercice
        exercise_type = self.ocr.detect_exercise_type(ocr_text)
        print(f"[TYPE] Exercice de: {exercise_type}")
        
        # 3. GPT - Génération de l'explication
        print("\n[2/4] GPT - Génération de l'explication...")
        explanation = self.gpt.generate_explanation(ocr_text, language)
        print(f"[GPT] Explication: {explanation[:100]}...")
        
        # 4. TTS - Synthèse vocale
        print("\n[3/4] TTS - Création de l'audio...")
        audio_path = self.tts.text_to_speech(explanation, language)
        
        if audio_path:
            print(f"[TTS] Audio créé: {audio_path}")
        else:
            print("[TTS] Pas d'audio (erreur)")
        
        # 5. Envoi sur WhatsApp
        print("\n[4/4] WHATSAPP - Envoi de la réponse...")
        
        # Message principal
        message = f"🤖 MOTEYI:\n{explanation[:200]}"
        self.send_whatsapp_message(message)
        
        # Info audio
        if audio_path:
            audio_msg = f"🔊 Audio disponible: {os.path.basename(audio_path)}"
            time.sleep(1)
            self.send_whatsapp_message(audio_msg)
        
        # Temps total
        elapsed = time.time() - start_time
        
        print(f"\n{'='*50}")
        print(f"[SUCCÈS] Traitement en {elapsed:.1f} secondes")
        print(f"{'='*50}")
        
        # Mise à jour stats
        self.stats["images_processed"] += 1
        self.stats["total_time"] += elapsed
        self.stats["success_count"] += 1
        
        return {
            "ocr_text": ocr_text,
            "exercise_type": exercise_type,
            "explanation": explanation,
            "audio_path": audio_path,
            "processing_time": elapsed
        }
    
    def run_interactive(self):
        """
        Mode interactif - L'utilisateur contrôle quand traiter
        """
        print("\n" + "="*50)
        print("MODE INTERACTIF")
        print("="*50)
        print("\nINSTRUCTIONS:")
        print("1. Cliquez sur une conversation WhatsApp avec photo")
        print("2. Appuyez ENTRÉE ici pour traiter")
        print("3. La réponse complète sera envoyée")
        print("4. Tapez 'quit' pour arrêter")
        print("-"*50)
        
        while True:
            command = input("\n[COMMANDE] ENTRÉE pour traiter, 'quit' pour arrêter: ").strip()
            
            if command.lower() == 'quit':
                break
            
            # Capturer l'écran
            image_path = self.capture_screen()
            print(f"[CAPTURE] Image: {image_path}")
            
            # Traiter l'exercice
            result = self.process_exercise(image_path)
            
            if result:
                print(f"\n[STATS] {self.stats['images_processed']} exercices traités")
                print(f"[TEMPS MOYEN] {self.stats['total_time']/self.stats['images_processed']:.1f}s")
    
    def print_summary(self):
        """Affiche le résumé de la session"""
        print("\n" + "="*50)
        print("RÉSUMÉ DE SESSION")
        print("="*50)
        print(f"Exercices traités: {self.stats['images_processed']}")
        print(f"Succès: {self.stats['success_count']}")
        if self.stats['images_processed'] > 0:
            avg = self.stats['total_time'] / self.stats['images_processed']
            print(f"Temps moyen: {avg:.1f} secondes")
            print(f"Performance: {'✅ EXCELLENT' if avg < 5 else '⚠️ À optimiser'}")

# Programme principal
def main():
    print("🚀 DÉMARRAGE MOTEYI BOT - VERSION FINALE")
    print("Avec OCR réel + Explications + Audio")
    
    bot = MoteyiBotFinal()
    
    try:
        bot.run_interactive()
    except KeyboardInterrupt:
        print("\n[STOP] Arrêt demandé")
    except Exception as e:
        print(f"\n[ERREUR] {e}")
    finally:
        bot.print_summary()
        bot.driver.quit()
    
    print("\n[FIN] Bot Moteyi fermé")
    print("\n🎉 FÉLICITATIONS ! Vous avez un MVP COMPLET et FONCTIONNEL !")

if __name__ == "__main__":
    main()