#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteyi Bot Simple - Version semi-manuelle mais fonctionnelle
Tapez 'photo' quand vous voulez traiter une image
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
from datetime import datetime

class MoteyiBotSimple:
    def __init__(self):
        print("\n" + "="*50)
        print("MOTEYI BOT - VERSION SIMPLE")
        print("="*50)
        
        self.driver = self.setup_driver()
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://web.whatsapp.com')
        
        print("[WAIT] WhatsApp charge...")
        time.sleep(8)
        return driver
    
    def capture_screen(self):
        """Capture l'ecran actuel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"data/received_images/capture_{timestamp}.png"
        os.makedirs("data/received_images", exist_ok=True)
        
        self.driver.save_screenshot(image_path)
        print(f"[CAPTURE] Image: {image_path}")
        return image_path
    
    def send_text(self, message):
        """Envoie un message dans le chat actif"""
        try:
            # Chercher tous les champs editables
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            
            # Prendre le dernier (generalement la zone de texte)
            if inputs:
                input_box = inputs[-1]
                input_box.click()
                time.sleep(0.5)
                
                # Effacer et taper
                input_box.send_keys(Keys.CONTROL + "a")
                input_box.send_keys(Keys.DELETE)
                input_box.send_keys(message)
                input_box.send_keys(Keys.ENTER)
                
                print("[SENT] Message envoye")
                return True
        except Exception as e:
            print(f"[ERREUR] Envoi: {e}")
        return False
    
    def process_image_mock(self, image_path):
        """Traitement mock de l'image"""
        # Simulation du traitement
        responses = [
            "MOTEYI: Exercice de maths detecte! Pour 25+17, decompose: 20+10=30, puis 5+7=12, donc 25+17=42",
            "MOTEYI: Conjugaison detectee! 'Les enfants JOUENT' - verbe jouer, 3e personne pluriel",
            "MOTEYI: Sciences! Le corps humain a: tete, bras, jambes, tronc. Important pour la sante!",
            "MOTEYI: Probleme detecte! Si Papa a 25 mangues et donne 12, il reste: 25-12=13 mangues"
        ]
        
        import random
        response = random.choice(responses)
        
        # En lingala
        response_ln = "MOTEYI: Na lingala: " + response.replace("detecte", "emoni").replace("Pour", "Mpo na")
        
        return response_ln
    
    def run_interactive(self):
        """Mode interactif avec commandes"""
        print("\n" + "="*50)
        print("MODE INTERACTIF")
        print("="*50)
        print("\nCOMMANDES:")
        print("1. Cliquez sur une conversation WhatsApp")
        print("2. Appuyez ENTREE ici pour capturer et traiter")
        print("3. La reponse sera envoyee automatiquement")
        print("4. Tapez 'quit' pour arreter")
        print("-"*50)
        
        while True:
            command = input("\n[COMMANDE] Appuyez ENTREE pour traiter (ou 'quit'): ").strip().lower()
            
            if command == 'quit':
                break
            
            print("\n[TRAITEMENT]")
            
            # 1. Capturer l'ecran
            image_path = self.capture_screen()
            
            # 2. Traiter (mock)
            print("[ANALYSE] Traitement de l'image...")
            response = self.process_image_mock(image_path)
            
            # 3. Envoyer la reponse
            print("[REPONSE] Envoi sur WhatsApp...")
            self.send_text(response)
            
            print("[OK] Cycle complet!")
            
            # Option pour audio
            audio_msg = "[Audio sera disponible dans version complete]"
            time.sleep(1)
            self.send_text(audio_msg)
    
    def cleanup(self):
        self.driver.quit()

def main():
    print("DEMARRAGE BOT MOTEYI SIMPLE")
    print("Version semi-manuelle mais FONCTIONNELLE")
    
    bot = MoteyiBotSimple()
    
    try:
        bot.run_interactive()
    except KeyboardInterrupt:
        print("\n[STOP] Arret")
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        bot.cleanup()
    
    print("\n[FIN] Bot ferme")

if __name__ == "__main__":
    main()
