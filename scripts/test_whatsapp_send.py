# scripts/test_whatsapp_send.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def test_send():
    print("TEST ENVOI WHATSAPP")
    print("="*50)
    
    # Setup
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')
    
    print("[WAIT] Chargement WhatsApp...")
    time.sleep(5)
    
    print("\nINSTRUCTIONS:")
    print("1. Cliquez sur une conversation")
    print("2. Appuyez ENTREE ici")
    input("Pret? ")
    
    # Essayer différents sélecteurs
    selectors_to_try = [
        ('div[contenteditable="true"][data-tab="10"]', "data-tab=10"),
        ('div[contenteditable="true"][data-tab="1"]', "data-tab=1"),
        ('div[role="textbox"]', "role=textbox"),
        ('div[title="Type a message"]', "title"),
        ('footer div[contenteditable="true"]', "footer contenteditable"),
        ('div[class*="copyable-text"][contenteditable="true"]', "copyable-text"),
        ('div[contenteditable="true"][spellcheck="true"]', "spellcheck=true")
    ]
    
    found = False
    for selector, description in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"\n[TROUVE] {description}: {len(elements)} element(s)")
                
                # Essayer d'envoyer un message test
                element = elements[-1]  # Prendre le dernier
                element.click()
                time.sleep(0.5)
                element.clear()
                element.send_keys("TEST MOTEYI: Si vous voyez ce message, l'envoi fonctionne!")
                element.send_keys(Keys.ENTER)
                
                print(f"[SUCCESS] Message envoye avec: {description}")
                found = True
                break
        except Exception as e:
            print(f"[ECHEC] {description}: {e}")
    
    if not found:
        print("\n[PROBLEME] Aucun selecteur ne fonctionne")
        print("[SOLUTION] Utiliser la methode copier-coller")
    
    time.sleep(3)
    driver.quit()

if __name__ == "__main__":
    test_send()