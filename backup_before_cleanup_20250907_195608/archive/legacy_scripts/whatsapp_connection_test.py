#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de connexion WhatsApp Web - MVP Moteyi
Objectif: Verifier qu'on peut se connecter et lire les messages
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def test_whatsapp_connection():
    print("TEST DE CONNEXION WHATSAPP WEB")
    print("=" * 50)
    
    # Configuration Chrome
    options = webdriver.ChromeOptions()
    # Garder la session pour ne pas rescanner le QR
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    # Initialiser le driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Ouvrir WhatsApp Web
        driver.get('https://web.whatsapp.com')
        print("\nINSTRUCTIONS:")
        print("1. Scannez le QR code avec WhatsApp sur votre telephone")
        print("2. Attendez que les conversations apparaissent")
        print("3. Appuyez sur Entree ici pour continuer...")
        input()
        
        # Verifier la connexion
        try:
            # Chercher un element qui prouve qu'on est connecte
            search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            print("[OK] Connexion reussie!")
            print("[OK] Session sauvegardee dans ./whatsapp_session")
            return True
        except:
            print("[ERREUR] Connexion echouee - reessayez")
            return False
            
    finally:
        print("\nFermeture dans 5 secondes...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    success = test_whatsapp_connection()
    if success:
        print("\n[SUCCESS] Pret pour l'etape suivante!")
