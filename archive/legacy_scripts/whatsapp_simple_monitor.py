#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moniteur WhatsApp simplifie - Approche visuelle
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def simple_monitor():
    print("[START] Moniteur WhatsApp simplifie")
    print("=" * 50)
    
    # Setup driver
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')
    
    print("[INFO] WhatsApp charge...")
    time.sleep(8)
    
    print("\n[MODE MANUEL ASSISTE]")
    print("=" * 50)
    print("INSTRUCTIONS:")
    print("1. Gardez Chrome ouvert")
    print("2. Je vais surveiller l'ecran toutes les 5 secondes")
    print("3. Quand vous recevez un message avec photo:")
    print("   - Cliquez manuellement sur la conversation")
    print("   - Le script detectera le changement")
    print("\nPret? Appuyez sur Entree pour commencer...")
    input()
    
    # Capture initiale de la page
    previous_source = driver.page_source
    check_count = 0
    
    print("\n[SURVEILLANCE] Active - Envoyez une photo pour tester")
    print("Appuyez Ctrl+C pour arreter")
    print("-" * 50)
    
    try:
        while True:
            check_count += 1
            time.sleep(5)
            
            # Comparer avec l'etat precedent
            current_source = driver.page_source
            
            # Detecter les changements
            if current_source != previous_source:
                print(f"\n[ALERTE #{check_count}] Changement detecte!")
                
                # Chercher des indices d'images
                if "blob:" in current_source:
                    print("[IMAGE] Probable image detectee (blob URL)")
                
                # Chercher du texte recent
                try:
                    # Methode basique : chercher tous les spans
                    all_spans = driver.find_elements(By.TAG_NAME, 'span')
                    recent_texts = []
                    
                    for span in all_spans[-20:]:  # Les 20 derniers
                        text = span.text.strip()
                        if text and len(text) > 5 and text not in recent_texts:
                            recent_texts.append(text)
                    
                    if recent_texts:
                        print("[TEXTES] Derniers elements:")
                        for txt in recent_texts[-3:]:
                            print(f"  > {txt[:50]}")
                except:
                    pass
                
                # Chercher specifiquement les images
                try:
                    images = driver.find_elements(By.TAG_NAME, 'img')
                    image_count = 0
                    for img in images:
                        src = img.get_attribute('src')
                        if src and ('blob:' in src or 'pps.whatsapp' in src):
                            image_count += 1
                    
                    if image_count > 0:
                        print(f"[IMAGES] {image_count} image(s) dans la conversation")
                        print("[ACTION] Pret pour traitement OCR!")
                except:
                    pass
                
                previous_source = current_source
            else:
                if check_count % 12 == 0:  # Toutes les minutes
                    print(f"[CHECK] Surveillance active... ({check_count} checks)")
                    
    except KeyboardInterrupt:
        print("\n[STOP] Arret demande")
    
    driver.quit()
    print("[FIN] Moniteur ferme")

if __name__ == "__main__":
    simple_monitor()
