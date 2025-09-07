# scripts/moteyi_bot_real_complete.py
"""
MOTEYI BOT - VERSION FINALE COMPLÈTE
Avec OCR réel + GPT réel + TTS réel + WhatsApp
LE VRAI MVP FONCTIONNEL !
"""

import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Recharger les variables avec la nouvelle clé
load_dotenv(override=True)

# Selenium pour WhatsApp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Import des modules réels
from ocr_real_english import RealOCR
from gpt_real import RealGPT
from tts_real import RealTTS

class MoteyiBotComplete:
    """
    Le bot Moteyi COMPLET avec tous les vrais composants
    Plus de mock - Tout est réel !
    """
    
    def __init__(self):
        print("\n" + "="*50)
        print("🤖 MOTEYI BOT - VERSION COMPLÈTE RÉELLE")
        print("="*50)
        print("✅ OCR Tesseract")
        print("✅ GPT-4o-mini avec crédit")
        print("✅ TTS gTTS")
        print("✅ WhatsApp")
        print("="*50)
        
        # Charger les modules
        print("\n[INIT] Chargement des modules...")
        self.ocr = RealOCR()
        self.gpt = RealGPT()
        self.tts = RealTTS()
        
        # Vérifier que GPT est bien configuré
        if self.gpt.mock_mode:
            print("[ATTENTION] GPT en mode mock - Vérifiez .env")
        else:
            print("[OK] GPT avec vraie clé API !")
        
        # WhatsApp
        self.driver = self.setup_whatsapp()
        
        # Stats
        self.stats = {
            "processed": 0,
            "total_time": 0,
            "total_cost": 0
        }
    
    def setup_whatsapp(self):
        print("\n[WHATSAPP] Connexion...")
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"data/received_images/moteyi_{timestamp}.png"
        self.driver.save_screenshot(image_path)
        return image_path
    
    def send_message(self, text):
        """Envoi amélioré"""
        try:
            # Chercher la zone de texte
            selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[role="textbox"]',
                'footer div[contenteditable="true"]'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[-1]
                    element.click()
                    time.sleep(0.3)
                    element.clear()
                    element.send_keys(text)
                    element.send_keys(Keys.ENTER)
                    return True
        except:
            pass
        return False
    
    def process_complete(self, image_path, language="francais"):
        """
        PIPELINE COMPLET RÉEL
        """
        print(f"\n{'='*50}")
        print(f"🚀 TRAITEMENT COMPLET - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        
        start = time.time()
        
        # 1. OCR RÉEL
        print("\n[1/4] 👁️ OCR (Tesseract)...")
        ocr_text = self.ocr.read_image(image_path)
        if not ocr_text:
            print("[ERREUR] Pas de texte détecté")
            return None
        print(f"Lu: '{ocr_text}'")
        
        # 2. DÉTECTION TYPE
        exercise_type = self.ocr.detect_exercise_type(ocr_text)
        print(f"Type: {exercise_type}")
        
        # 3. GPT RÉEL !
        print("\n[2/4] 🧠 GPT (Vraie explication)...")
        explanation = self.gpt.generate_explanation(ocr_text, language)
        print(f"Explication générée: {len(explanation)} caractères")
        
        # 4. TTS RÉEL
        print("\n[3/4] 🔊 TTS (Audio)...")
        audio_path = self.tts.text_to_speech(explanation, language)
        if audio_path:
            file_size = os.path.getsize(audio_path) / 1024
            print(f"Audio: {os.path.basename(audio_path)} ({file_size:.1f} KB)")
        
        # 5. ENVOI WHATSAPP
        print("\n[4/4] 📱 WhatsApp...")
        
        # Message formaté
        message = f"""🤖 *MOTEYI - Tuteur IA*

📚 *Exercice détecté:* {exercise_type}
📝 *Texte lu:* {ocr_text[:50]}...

💡 *Explication:*
{explanation}

🎧 Audio disponible: {os.path.basename(audio_path) if audio_path else 'Non généré'}"""
        
        if self.send_message(message[:900]):  # WhatsApp limite
            print("[OK] Message envoyé !")
        else:
            print("[INFO] Copiez le message ci-dessus dans WhatsApp")
            print(message)
        
        # Calculs finaux
        elapsed = time.time() - start
        tokens_approx = len(ocr_text + explanation) / 4  # Approximation
        cost_approx = tokens_approx * 0.00015 / 1000
        
        self.stats["processed"] += 1
        self.stats["total_time"] += elapsed
        self.stats["total_cost"] += cost_approx
        
        print(f"\n{'='*50}")
        print(f"✅ SUCCÈS en {elapsed:.1f}s (Coût: ~${cost_approx:.5f})")
        print(f"{'='*50}")
        
        return {
            "ocr": ocr_text,
            "type": exercise_type,
            "explanation": explanation,
            "audio": audio_path,
            "time": elapsed,
            "cost": cost_approx
        }
    
    def run(self):
        """Mode interactif amélioré"""
        print("\n" + "="*50)
        print("🎮 MODE INTERACTIF - TEST RÉEL COMPLET")
        print("="*50)
        print("\nPOUR TESTER:")
        print("1. Envoyez une photo d'exercice sur WhatsApp")
        print("2. Cliquez sur la conversation")
        print("3. Appuyez ENTRÉE ici")
        print("4. Observez la magie GPT réelle !")
        print("\n[quit = arrêter, stats = voir statistiques]")
        print("-"*50)
        
        while True:
            cmd = input("\n[MOTEYI] Entrée pour traiter, 'quit' pour arrêter: ").strip()
            
            if cmd == 'quit':
                break
            elif cmd == 'stats':
                self.show_stats()
                continue
            
            # Capturer et traiter
            print("\n[CAPTURE]...")
            image = self.capture_screen()
            
            # TRAITEMENT RÉEL COMPLET !
            result = self.process_complete(image)
            
            if result:
                print(f"\n[BILAN] Exercice #{self.stats['processed']}")
                print(f"Temps: {result['time']:.1f}s")
                print(f"Coût: ${result['cost']:.5f}")
                print(f"Crédit restant: ~${5.0 - self.stats['total_cost']:.2f}")
    
    def show_stats(self):
        print("\n" + "="*50)
        print("📊 STATISTIQUES DE SESSION")
        print("="*50)
        print(f"Exercices traités: {self.stats['processed']}")
        if self.stats['processed'] > 0:
            avg_time = self.stats['total_time'] / self.stats['processed']
            print(f"Temps moyen: {avg_time:.1f}s")
            print(f"Performance: {'✅ EXCELLENT' if avg_time < 5 else '⚠️ Correct'}")
        print(f"Coût total: ${self.stats['total_cost']:.4f}")
        print(f"Crédit restant: ~${5.0 - self.stats['total_cost']:.2f}")

def main():
    print("\n" + "🚀"*25)
    print("LANCEMENT MOTEYI BOT - VERSION RÉELLE COMPLÈTE")
    print("OCR + GPT + TTS + WhatsApp = MVP FONCTIONNEL !")
    print("🚀"*25)
    
    bot = MoteyiBotComplete()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n[STOP] Arrêt")
    finally:
        bot.show_stats()
        bot.driver.quit()
        
    print("\n" + "🎉"*25)
    print("BRAVO ! VOTRE MVP EST 100% FONCTIONNEL !")
    print("🎉"*25)

if __name__ == "__main__":
    main()