#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteyi Bot Integre - WhatsApp + Pipeline MVP
Version avec Mock OCR pour demo immediate
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import json
from datetime import datetime
from pathlib import Path

# Importer le pipeline mock
from pipeline_mvp import (
    mock_ocr,
    search_rag_context,
    generate_explanation_mock,
    text_to_speech_mock,
    process_whatsapp_image
)

class MoteyiBotIntegrated:
    def __init__(self):
        print("\n" + "="*50)
        print("MOTEYI BOT - DEMARRAGE")
        print("="*50)
        print("[INIT] Initialisation...")
        
        self.setup_directories()
        self.driver = self.setup_driver()
        self.processed_messages = set()
        self.stats = {
            "messages_received": 0,
            "images_processed": 0,
            "total_time": 0
        }
        
    def setup_directories(self):
        """Cree tous les dossiers necessaires"""
        dirs = [
            "data/received_images",
            "data/audio_responses",
            "data/pipeline_results",
            "logs"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def setup_driver(self):
        """Configure Chrome avec WhatsApp Web"""
        options = webdriver.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://web.whatsapp.com')
        
        print("[WAIT] Chargement WhatsApp...")
        time.sleep(8)
        
        print("[OK] WhatsApp connecte")
        return driver
    
    def check_for_new_images(self):
        """Verifie s'il y a de nouvelles images"""
        try:
            current_source = self.driver.page_source
            
            if "blob:" in current_source:
                # Compter les images
                images = self.driver.find_elements(By.TAG_NAME, 'img')
                image_count = sum(1 for img in images 
                                if img.get_attribute('src') and 
                                'blob:' in img.get_attribute('src'))
                
                if image_count > 0:
                    return True
            return False
        except:
            return False
    
    def capture_current_image(self):
        """Capture l'image actuellement visible"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"data/received_images/whatsapp_{timestamp}.png"
            
            # Screenshot de la zone de chat
            chat_area = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="conversation-panel-messages"]')
            if chat_area:
                chat_area.screenshot(image_path)
            else:
                self.driver.save_screenshot(image_path)
            
            print(f"[CAPTURE] Image sauvegardee: {image_path}")
            return image_path
            
        except Exception as e:
            # Fallback: screenshot complet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"data/received_images/screen_{timestamp}.png"
            self.driver.save_screenshot(image_path)
            return image_path
    
    def send_response(self, text_response, audio_path=None):
        """Envoie la reponse sur WhatsApp"""
        try:
            # Trouver la zone de texte
            input_box = self.driver.find_element(
                By.CSS_SELECTOR, 
                'div[contenteditable="true"][data-tab="10"]'
            )
            
            if not input_box:
                # Essayer un autre selecteur
                input_box = self.driver.find_element(
                    By.XPATH,
                    '//div[@contenteditable="true"][@role="textbox"]'
                )
            
            # Envoyer le texte
            input_box.click()
            input_box.clear()
            
            # Message de reponse
            response_msg = f"[MOTEYI BOT]\n{text_response[:200]}..."
            
            # Taper le message
            input_box.send_keys(response_msg)
            input_box.send_keys(Keys.ENTER)
            
            print("[SENT] Reponse envoyee sur WhatsApp")
            
            # Si audio disponible (futur)
            if audio_path and os.path.exists(audio_path):
                input_box.send_keys(f"[Audio disponible: {audio_path}]")
                input_box.send_keys(Keys.ENTER)
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Envoi reponse: {e}")
            return False
    
    def run_demo_mode(self):
        """Mode demo avec interaction manuelle"""
        print("\n" + "="*50)
        print("MODE DEMO INTERACTIF")
        print("="*50)
        print("\nINSTRUCTIONS:")
        print("1. Envoyez une photo d'exercice sur WhatsApp")
        print("2. Cliquez sur la conversation")
        print("3. Le bot va detecter et traiter")
        print("4. La reponse sera envoyee automatiquement")
        print("\n[Ctrl+C pour arreter]")
        print("-"*50)
        
        last_check = ""
        
        try:
            while True:
                # Surveiller les changements
                current_page = self.driver.page_source[:1000]
                
                if current_page != last_check:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Changement detecte...")
                    
                    if self.check_for_new_images():
                        print("[IMAGE] Image detectee!")
                        self.stats["messages_received"] += 1
                        
                        # Capturer l'image
                        image_path = self.capture_current_image()
                        
                        # Traiter avec le pipeline
                        print("\n[PIPELINE] Traitement en cours...")
                        start = time.time()
                        
                        result = process_whatsapp_image(image_path, "lingala")
                        
                        elapsed = time.time() - start
                        self.stats["images_processed"] += 1
                        self.stats["total_time"] += elapsed
                        
                        print(f"\n[RESULTAT] Traite en {elapsed:.2f}s")
                        
                        # Extraire l'explication
                        explanation = result['explanation'][:200] + "..."
                        
                        # Envoyer la reponse
                        self.send_response(explanation, result.get('audio'))
                        
                        print("\n[SUCCESS] Cycle complet termine!")
                        print(f"Stats: {self.stats['images_processed']} images, "
                              f"Temps moyen: {self.stats['total_time']/max(1,self.stats['images_processed']):.2f}s")
                    
                    last_check = current_page
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n[STOP] Arret demande")
    
    def print_stats(self):
        """Affiche les statistiques"""
        print("\n" + "="*50)
        print("STATISTIQUES DE SESSION")
        print("="*50)
        print(f"Messages recus: {self.stats['messages_received']}")
        print(f"Images traitees: {self.stats['images_processed']}")
        if self.stats['images_processed'] > 0:
            avg_time = self.stats['total_time'] / self.stats['images_processed']
            print(f"Temps moyen: {avg_time:.2f}s")
            print(f"Performance: {'OK' if avg_time < 5 else 'A OPTIMISER'}")
    
    def cleanup(self):
        """Fermeture propre"""
        print("\n[CLEANUP] Fermeture...")
        self.driver.quit()

def main():
    print("\n" + "="*50)
    print("MOTEYI BOT MVP - DEMO COMPLETE")
    print("="*50)
    print("\nVersion: Pipeline Mock (sans OCR reel)")
    print("Objectif: Demo fonctionnelle end-to-end")
    print("-"*50)
    
    bot = MoteyiBotIntegrated()
    
    try:
        bot.run_demo_mode()
    except Exception as e:
        print(f"\n[ERREUR FATALE] {e}")
    finally:
        bot.print_stats()
        bot.cleanup()
    
    print("\n[FIN] Bot Moteyi ferme")
    print("\nPour une version complete:")
    print("1. Installer Tesseract pour OCR reel")
    print("2. Ajouter cle OpenAI pour vraies explications")
    print("3. Integrer gTTS pour audio reel")

if __name__ == "__main__":
    main()
