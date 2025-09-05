# scripts/moteyi_whatsapp_cloud_bot.py
"""
Bot Moteyi avec WhatsApp Cloud API
Version complète avec audio naturel et pédagogique
100% automatique avec l'arme fatale !
"""

import os
import requests
import json
import base64
import re
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
    
    def send_audio(self, to_number, audio_path):
        """Envoie un fichier audio via WhatsApp"""
        
        # D'abord, uploader le fichier audio
        upload_url = f"{WHATSAPP_API_BASE}/{PHONE_NUMBER_ID}/media"
        
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
        }
        
        # Ouvrir et envoyer le fichier
        with open(audio_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(audio_path), audio_file, 'audio/mpeg'),
                'messaging_product': (None, 'whatsapp'),
                'type': (None, 'audio/mpeg')
            }
            
            # Upload du fichier
            upload_response = requests.post(upload_url, headers=headers, files=files)
            
            if upload_response.status_code == 200:
                media_id = upload_response.json().get('id')
                print(f"[UPLOAD] Audio uploadé avec ID: {media_id}")
                
                # Maintenant envoyer le message avec l'audio
                message_url = f"{WHATSAPP_API_BASE}/{PHONE_NUMBER_ID}/messages"
                
                message_data = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "audio",
                    "audio": {
                        "id": media_id
                    }
                }
                
                message_headers = {
                    'Authorization': f'Bearer {ACCESS_TOKEN}',
                    'Content-Type': 'application/json'
                }
                
                send_response = requests.post(message_url, headers=message_headers, json=message_data)
                
                if send_response.status_code == 200:
                    print(f"[AUDIO] Audio envoyé à {to_number}")
                    return True
                else:
                    print(f"[ERROR] Envoi audio échoué: {send_response.text}")
            else:
                print(f"[ERROR] Upload audio échoué: {upload_response.text}")
        
        return False
    
    def clean_text_for_speech(self, text):
        """
        Transforme le texte formaté en version naturelle pour l'audio
        L'objectif est d'avoir un texte qui sonne naturel quand lu à voix haute
        """
        # Retirer tous les caractères de formatage Markdown
        text = re.sub(r'\*+', '', text)  # Retirer les astérisques
        text = re.sub(r'_+', '', text)   # Retirer les underscores
        text = re.sub(r'#+', '', text)   # Retirer les dièses
        text = re.sub(r'`+', '', text)   # Retirer les backticks
        
        # Retirer les émojis (plus complet)
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Améliorer la ponctuation pour l'oral
        text = text.replace(' : ', ', ')
        text = text.replace(' - ', ', ')
        text = text.replace('...', '.')
        text = text.replace('!', '.')  # Les exclamations sont trop fortes en TTS
        
        # Transformer les listes numérotées
        text = re.sub(r'(\d+)\.\s*', r'Numéro \1, ', text)
        
        # Ajouter des pauses naturelles
        text = text.replace('\n\n', '. ')
        text = text.replace('\n', '. ')
        
        # Retirer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Nettoyer les points multiples
        text = re.sub(r'\.+', '.', text)
        text = re.sub(r'\.\s*\.', '.', text)
        
        # Remplacer certaines abréviations pour une meilleure lecture
        text = text.replace('OB.', 'option B')
        text = text.replace('ex.', 'exemple')
        text = text.replace('etc.', 'et cetera')
        
        # S'assurer que le texte commence et finit proprement
        text = text.strip()
        if not text.endswith('.'):
            text += '.'
            
        return text
    
    def create_audio_explanation(self, ocr_text, written_explanation):
        """
        Crée une version spécifiquement conçue pour l'audio
        Plus conversationnelle et pédagogique
        """
        # Extraire la réponse correcte si elle est identifiée
        answer_match = re.search(r'\*([A-E])\.\s*([^*]+)\*', written_explanation)
        
        if answer_match:
            correct_letter = answer_match.group(1)
            correct_answer = answer_match.group(2)
            
            # Créer une explication audio personnalisée
            audio_text = f"""
            Bonjour, je vais t'expliquer cet exercice.
            
            La question demande : {self.clean_text_for_speech(ocr_text[:200])}.
            
            Pour trouver la bonne réponse, il faut bien comprendre ce qu'on cherche.
            
            La réponse correcte est l'option {correct_letter}, {correct_answer}.
            
            Pourquoi cette réponse ? 
            """
            
            # Extraire l'explication du GPT et la nettoyer
            explanation_part = written_explanation.split('Bravo')[0]
            explanation_part = self.clean_text_for_speech(explanation_part)
            
            audio_text += explanation_part
            
            audio_text += """
            
            J'espère que cette explication t'a aidé. 
            N'hésite pas à m'envoyer d'autres exercices si tu as besoin d'aide.
            Bonne continuation dans tes études !
            """
        else:
            # Version de base si pas de structure claire
            audio_text = f"""
            Bonjour, voici l'explication de ton exercice.
            
            {self.clean_text_for_speech(written_explanation)}
            
            J'espère que cela t'aide. Envoie-moi d'autres exercices si besoin.
            """
        
        # Nettoyer une dernière fois
        audio_text = self.clean_text_for_speech(audio_text)
        
        return audio_text
    
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
        written_explanation = self.gpt.generate_explanation(ocr_text, "francais")
        
        # 5. Créer une version optimisée pour l'audio
        print("[TTS] Préparation du texte pour l'audio...")
        audio_text = self.create_audio_explanation(ocr_text, written_explanation)
        print(f"[TTS] Texte audio préparé ({len(audio_text)} caractères)")
        
        # 6. TTS
        print("[TTS] Création de l'audio...")
        audio_path = self.tts.text_to_speech(audio_text, "francais")
        
        # 7. Envoyer la réponse texte (version écrite)
        response_message = f"""🤖 MOTEYI - Tuteur IA

📚 Exercice lu : {ocr_text[:100]}...

💡 Explication :
{written_explanation}

🎧 Envoi de l'explication audio..."""
        
        self.send_message(from_number, response_message)
        
        # 8. Envoyer l'audio
        if audio_path and os.path.exists(audio_path):
            print(f"[AUDIO] Envoi du fichier: {audio_path}")
            if self.send_audio(from_number, audio_path):
                self.send_message(from_number, 
                    "🎵 Explication audio envoyée ! Écoutez pour une meilleure compréhension.")
            else:
                self.send_message(from_number, 
                    "⚠️ L'audio n'a pas pu être envoyé, mais l'explication écrite est ci-dessus.")
        else:
            print("[ERROR] Fichier audio introuvable")
        
        print(f"[SUCCÈS] Réponse complète envoyée à {from_number}")

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
                                    "Envoyez-moi une photo d'exercice et je vous l'expliquerai ! 📝")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MOTEYI BOT - WHATSAPP CLOUD API")
    print("✨ Version avec Audio Naturel et Pédagogique")
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