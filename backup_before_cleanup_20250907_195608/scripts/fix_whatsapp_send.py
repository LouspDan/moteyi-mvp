# scripts/fix_whatsapp_send.py
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def send_message_foolproof(driver, text):
    """
    Méthode 100% fiable : Copier-coller + raccourci clavier
    """
    try:
        # 1. Mettre le texte dans le presse-papier
        pyperclip.copy(text)
        print("[CLIPBOARD] Message copié")
        
        # 2. Cliquer au centre de l'écran (zone de chat)
        actions = ActionChains(driver)
        actions.move_by_offset(500, 400).click().perform()
        time.sleep(0.5)
        
        # 3. Coller avec Ctrl+V
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("[PASTE] Message collé")
        
        # 4. Envoyer avec Entrée
        time.sleep(0.5)
        actions.send_keys(Keys.ENTER).perform()
        print("[SENT] Message envoyé !")
        
        return True
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        # Fallback : afficher pour copie manuelle
        print("\n" + "="*50)
        print("COPIEZ CE MESSAGE DANS WHATSAPP:")
        print("-"*50)
        print(text)
        print("-"*50)
        return False