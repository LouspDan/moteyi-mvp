#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecteur de messages WhatsApp - MVP Moteyi
Detecte les nouveaux messages avec images
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

class WhatsAppReader:
    def __init__(self):
        print("[INIT] Demarrage du lecteur WhatsApp...")
        self.driver = self.setup_driver()
        self.processed_messages = set()
        
    def setup_driver(self):
        """Configure Chrome avec session existante"""
        options = webdriver.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        # Mode silencieux
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://web.whatsapp.com')
        
        # Attendre que WhatsApp charge
        print("[WAIT] Chargement de WhatsApp...")
        time.sleep(5)
        
        try:
            # Verifier qu'on est connecte
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            print("[OK] WhatsApp charge et connecte")
        except:
            print("[ERREUR] WhatsApp non connecte - relancez whatsapp_connection_test.py")
            driver.quit()
            exit(1)
            
        return driver
    
    def get_unread_chats(self):
        """Trouve les conversations non lues"""
        try:
            # Chercher les badges de messages non lus
            unread_elements = self.driver.find_elements(
                By.XPATH, 
                '//span[@aria-label and contains(@aria-label, "unread")]'
            )
            
            if unread_elements:
                print(f"[INFO] {len(unread_elements)} conversation(s) non lue(s)")
                return unread_elements
            return []
        except:
            return []
    
    def click_on_chat(self, chat_element):
        """Clique sur une conversation"""
        try:
            # Remonter au parent clickable
            chat_item = chat_element.find_element(By.XPATH, './../../../../..')
            chat_item.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"[ERREUR] Click chat: {e}")
            return False
    
    def check_for_images(self):
        """Verifie s'il y a des images dans la conversation"""
        try:
            # Chercher les images
            images = self.driver.find_elements(
                By.XPATH,
                '//img[contains(@src, "blob:")]'
            )
            
            if images:
                print(f"[IMAGE] {len(images)} image(s) trouvee(s)")
                return True
            return False
        except:
            return False
    
    def get_last_messages(self, count=5):
        """Recupere les derniers messages texte"""
        try:
            messages = self.driver.find_elements(
                By.CLASS_NAME,
                'selectable-text'
            )
            
            last_messages = []
            for msg in messages[-count:]:
                text = msg.text.strip()
                if text and text not in last_messages:
                    last_messages.append(text)
            
            return last_messages
        except:
            return []
    
    def monitor_messages(self, duration=60):
        """Surveille les messages pendant X secondes"""
        print(f"\n[START] Surveillance des messages pendant {duration} secondes")
        print("[INFO] Envoyez une photo sur WhatsApp pour tester")
        print("-" * 50)
        
        start_time = time.time()
        check_count = 0
        
        while (time.time() - start_time) < duration:
            check_count += 1
            
            # Chercher les conversations non lues
            unread = self.get_unread_chats()
            
            if unread:
                print(f"\n[CHECK #{check_count}] Messages non lus detectes!")
                
                # Cliquer sur la premiere conversation non lue
                if self.click_on_chat(unread[0]):
                    time.sleep(1)
                    
                    # Verifier s'il y a des images
                    if self.check_for_images():
                        print("[ALERTE] IMAGE DETECTEE - Pret pour traitement OCR")
                        
                        # Recuperer le contexte (derniers messages)
                        messages = self.get_last_messages(3)
                        if messages:
                            print("[CONTEXTE] Derniers messages:")
                            for msg in messages:
                                print(f"  > {msg[:50]}...")
                    else:
                        # Juste du texte
                        messages = self.get_last_messages(1)
                        if messages:
                            print(f"[TEXTE] {messages[0][:100]}...")
            else:
                if check_count % 10 == 0:
                    print(f"[CHECK #{check_count}] Pas de nouveaux messages...")
            
            # Attendre avant le prochain check
            time.sleep(3)
        
        print("\n[FIN] Surveillance terminee")
    
    def cleanup(self):
        """Ferme le navigateur"""
        print("[CLEANUP] Fermeture...")
        self.driver.quit()

def main():
    reader = WhatsAppReader()
    
    try:
        # Surveiller pendant 2 minutes
        reader.monitor_messages(duration=120)
    except KeyboardInterrupt:
        print("\n[STOP] Arret demande par l'utilisateur")
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        reader.cleanup()

if __name__ == "__main__":
    main()
