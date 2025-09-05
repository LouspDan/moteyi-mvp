# scripts/moteyi_whatsapp_cloud_bot.py
"""
Bot Moteyi avec WhatsApp Cloud API
100% automatique !
"""

import os
import requests
import json
import base64
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging

# Nos modules
from ocr_real_english import RealOCR
from gpt_real import RealGPT  
from tts_real import RealTTS

# Charger les variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')
API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v17.0')

# URL de base pour l'API
WHATSAPP_API_BASE = f"https://graph.facebook.com/{API_VERSION}"

class MoteyiCloudBot:
    def __init__(self):
        self.ocr = RealOCR()
        self.gpt = RealGPT()
        self.tts = RealTTS()
        print("[BOT] Moteyi Cloud Bot initialisé !")
        
    def send_message(self, to_number, text):
        """Envoie un message texte via WhatsApp"""
        url = f"{WHATSAPP_API_BASE}/{PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"[SENT] Message envoyé à {to_number}")
            return True
        else:
            print(f"[ERROR] Envoi échoué: {response.text}")
            return False
    
    def download_media(self, media_id):
        """Télécharge une image depuis WhatsApp"""
        # Obtenir l'URL du media
        url = f"{WHATSAPP_API_BASE}/{media_id}"
        headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            media_url = response.json().get('url')
            
            # Télécharger l'image
            media_response = requests.get(media_url, headers=headers)
            
            # Sauvegarder localement
            os.makedirs('data/whatsapp_images', exist_ok=True)
            filename = f"data/whatsapp_images/{media_id}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(media_response.content)
            
            print(f"[DOWNLOAD] Image sauvegardée: {filename}")
            return filename
        
        return None
    
    def process_image_message(self, from_number, media_id):
        """Pipeline complet de traitement d'image"""
        print(f"\n[NOUVEAU] Image reçue de {from_number}")
        
        # 1. Envoyer accusé de réception
        self.send_message(from_number, "📸 Photo reçue ! Je l'analyse...")
        
        # 2. Télécharger l'image
        image_path = self.download_media(media_id)
        if not image_path:
            self.send_message(from_number, "❌ Erreur lors du téléchargement de l'image.")
            return
        
        # 3. OCR
        print("[OCR] Lecture en cours...")
        ocr_text = self.ocr.read_image(image_path)
        
        if not ocr_text:
            self.send_message(from_number, 
                "Je n'ai pas pu lire l'exercice. Essayez avec une photo plus claire.")
            return
        
        # 4. GPT
        print("[GPT] Génération de l'explication...")
        explanation = self.gpt.generate_explanation(ocr_text, "francais")
        
        # 5. TTS
        print("[TTS] Création de l'audio...")
        audio_path = self.tts.text_to_speech(explanation, "francais")
        
        # 6. Envoyer la réponse
        response_message = f"""🤖 MOTEYI - Tuteur IA

📚 Exercice lu : {ocr_text[:100]}...

💡 Explication :
{explanation}

🎧 Audio généré (envoi dans la prochaine version)"""
        
        self.send_message(from_number, response_message)
        
        print(f"[SUCCÈS] Réponse envoyée à {from_number}")

# Instance globale
bot = MoteyiCloudBot()

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """Vérification du webhook par Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('[WEBHOOK] Vérifié avec succès')
        return challenge, 200
    
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook_process():
    """Traite les messages entrants"""
    try:
        data = request.get_json()
        
        # Parser le message
        if data.get('entry'):
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # Vérifier les messages
                    if 'messages' in value:
                        for message in value['messages']:
                            from_number = message['from']
                            msg_type = message['type']
                            
                            if msg_type == 'image':
                                # Traiter l'image
                                media_id = message['image']['id']
                                bot.process_image_message(from_number, media_id)
                                
                            elif msg_type == 'text':
                                # Message texte
                                text = message['text']['body']
                                print(f"[TEXT] De {from_number}: {text}")
                                
                                # Réponse automatique
                                bot.send_message(from_number,
                                    "Envoyez-moi une photo d'exercice et je vous l'expliquerai ! 📚")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MOTEYI BOT - WHATSAPP CLOUD API")
    print("="*50)
    print(f"Phone ID: {PHONE_NUMBER_ID}")
    print(f"Token: ...{ACCESS_TOKEN[-10:]}")
    print("="*50)
    print("\n[NEXT] Lancez ngrok dans un autre terminal:")
    print("ngrok http 5000")
    print("\nPuis configurez le webhook dans Meta")
    print("="*50)
    
    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=5000, debug=True)