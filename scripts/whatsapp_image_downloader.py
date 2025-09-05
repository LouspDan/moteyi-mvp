#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telechargement d'images WhatsApp - MVP Moteyi
Capture les images pour traitement OCR
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import base64
from datetime import datetime
import requests

class WhatsAppImageCapture:
    def __init__(self):
        print("[INIT] Capture d'images WhatsApp")
        self.setup_directories()
        self.driver = self.setup_driver()
        
    def setup_directories(self):
        """Cree les dossiers necessaires"""
        os.makedirs("data/received_images", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        print("[OK] Dossiers crees")
        
    def setup_driver(self):
        """Configure Chrome"""
        options = webdriver.ChromeOptions()
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # Configuration pour telecharger les images
        prefs = {
            "download.default_directory": os.path.join(os.getcwd(), "data", "received_images"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://web.whatsapp.com')
        
        print("[WAIT] Chargement WhatsApp...")
        time.sleep(8)
        return driver
    
    def find_and_click_images(self):
        """Trouve et clique sur les images pour les agrandir"""
        try:
            # Chercher toutes les images
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            
            downloadable_images = []
            for img in images:
                src = img.get_attribute('src')
                if src and ('blob:' in src or 'pps.whatsapp' in src):
                    downloadable_images.append(img)
            
            print(f"[INFO] {len(downloadable_images)} image(s) trouvee(s)")
            
            if downloadable_images:
                # Cliquer sur la premiere image
                print("[CLICK] Ouverture de l'image...")
                downloadable_images[0].click()
                time.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERREUR] Click image: {e}")
            return False
    
    def download_current_image(self):
        """Telecharge l'image actuellement ouverte"""
        try:
            # Methode 1: Chercher le bouton de telechargement
            download_button = None
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            
            for btn in buttons:
                aria_label = btn.get_attribute('aria-label')
                if aria_label and 'download' in aria_label.lower():
                    download_button = btn
                    break
            
            if download_button:
                print("[DOWNLOAD] Via bouton...")
                download_button.click()
                time.sleep(3)
                return True
            
            # Methode 2: Screenshot de l'image agrandie
            print("[SCREENSHOT] Capture d'ecran...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"data/received_images/capture_{timestamp}.png"
            
            # Trouver l'image agrandie
            large_images = self.driver.find_elements(By.CSS_SELECTOR, 'img[style*="height"]')
            if large_images:
                large_images[0].screenshot(screenshot_path)
                print(f"[OK] Image sauvegardee: {screenshot_path}")
                return screenshot_path
            else:
                # Screenshot de toute la zone
                self.driver.save_screenshot(screenshot_path)
                print(f"[OK] Screenshot complet: {screenshot_path}")
                return screenshot_path
                
        except Exception as e:
            print(f"[ERREUR] Download: {e}")
            return None
    
    def extract_image_from_page(self):
        """Extrait directement l'image via JavaScript"""
        try:
            # Executer JavaScript pour obtenir les images
            script = """
            var images = [];
            var imgs = document.querySelectorAll('img[src*="blob"]');
            for(var i = 0; i < Math.min(imgs.length, 3); i++) {
                images.push(imgs[i].src);
            }
            return images;
            """
            
            blob_urls = self.driver.execute_script(script)
            
            if blob_urls:
                print(f"[JS] {len(blob_urls)} blob URL(s) trouvee(s)")
                
                # Pour chaque blob URL, obtenir les donnees
                for i, blob_url in enumerate(blob_urls):
                    try:
                        # Convertir blob en base64 via JS
                        script = f"""
                        var xhr = new XMLHttpRequest();
                        xhr.open('GET', '{blob_url}', false);
                        xhr.responseType = 'blob';
                        xhr.send();
                        
                        var reader = new FileReader();
                        reader.readAsDataURL(xhr.response);
                        while(reader.readyState !== 2) {{}}
                        return reader.result;
                        """
                        
                        base64_data = self.driver.execute_script(script)
                        
                        if base64_data:
                            # Sauvegarder l'image
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"data/received_images/whatsapp_{timestamp}_{i}.png"
                            
                            # Decoder et sauvegarder
                            img_data = base64_data.split(',')[1]
                            with open(filename, 'wb') as f:
                                f.write(base64.b64decode(img_data))
                            
                            print(f"[OK] Image extraite: {filename}")
                            return filename
                    except:
                        continue
            
        except Exception as e:
            print(f"[ERREUR] Extract JS: {e}")
            return None
    
    def monitor_and_capture(self):
        """Surveillance et capture automatique"""
        print("\n[MODE] Surveillance et capture d'images")
        print("=" * 50)
        print("1. Cliquez sur une conversation avec image")
        print("2. Le script va capturer automatiquement")
        print("3. Ctrl+C pour arreter")
        print("-" * 50)
        
        captured_images = []
        
        try:
            while True:
                # Detecter les images
                if self.find_and_click_images():
                    time.sleep(2)
                    
                    # Essayer de telecharger
                    image_path = self.download_current_image()
                    
                    if not image_path:
                        # Essayer extraction JavaScript
                        image_path = self.extract_image_from_page()
                    
                    if image_path:
                        captured_images.append(image_path)
                        print(f"[SUCCES] Total images capturees: {len(captured_images)}")
                        
                        # Fermer l'image agrandie (Echap)
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.ESCAPE).perform()
                        time.sleep(1)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n[STOP] Arret demande")
        
        print(f"\n[RESULTAT] {len(captured_images)} image(s) capturee(s)")
        for img in captured_images:
            print(f"  - {img}")
        
        return captured_images
    
    def cleanup(self):
        """Fermeture"""
        self.driver.quit()

def main():
    capturer = WhatsAppImageCapture()
    
    try:
        images = capturer.monitor_and_capture()
        
        if images:
            print("\n[PRET] Images pretes pour OCR:")
            print(f"  Dossier: data/received_images/")
            print(f"  Prochaine etape: OCR avec Google Vision")
            
    finally:
        capturer.cleanup()

if __name__ == "__main__":
    main()
