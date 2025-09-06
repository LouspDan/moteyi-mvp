# scripts/moteyi_whatsapp_cloud_bot.py
"""
Bot Moteyi avec WhatsApp Cloud API - Version 2.0
Avec support Multilingue (FR, Lingala, Kiswahili, Tshiluba, EN) et RAG intégré
Sprint Phoenix 72h - Points A & B validés
"""

import os
import requests
import json
import base64
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
from datetime import datetime

# Nos modules existants
from ocr_real_english import RealOCR
from gpt_real import RealGPT  
from tts_real import RealTTS

# NOUVEAUX MODULES - Multilingue et RAG
from language_manager import LanguageManager, handle_language_selection
from rag_connector import CongoRAGConnector

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

# INITIALISATION DES MODULES GLOBAUX
lang_manager = LanguageManager(default_language="fr")
rag = CongoRAGConnector(base_path="data")
print(f"🌍 Gestionnaire multilingue initialisé")
print(f"📚 RAG connecté avec {len(rag.documents)} documents")

class MoteyiCloudBot:
    def __init__(self):
        self.ocr = RealOCR()
        self.gpt = RealGPT()
        self.tts = RealTTS()
        print("[BOT] Moteyi Cloud Bot v2.0 initialisé !")
        print("[BOT] Support : FR, Lingala, Kiswahili, Tshiluba, English")
    
    def call_gpt(self, prompt, language="francais"):
        """Helper pour appeler GPT avec la bonne méthode"""
        try:
            # Mapper les codes de langue vers les langues GPT
            lang_map = {
                "fr": "francais",
                "en": "english",
                "ln": "francais",  # Lingala utilise français pour l'instant
                "sw": "francais",  # Swahili utilise français pour l'instant
                "lu": "francais"   # Tshiluba utilise français pour l'instant
            }
            gpt_language = lang_map.get(language, "francais")
            
            # Utiliser la méthode existante de RealGPT
            return self.gpt.generate_explanation(prompt, gpt_language)
        except Exception as e:
            print(f"❌ Erreur GPT: {e}")
            # Messages d'erreur par langue
            error_messages = {
                "fr": "Désolé, une erreur s'est produite. Veuillez réessayer.",
                "ln": "Pardon, likambo moko esalemi. Meka lisusu.",
                "sw": "Samahani, kosa limetokea. Tafadhali jaribu tena.",
                "lu": "Tuasakidila, bualu bubi busambile. Enza kayi.",
                "en": "Sorry, an error occurred. Please try again."
            }
            return error_messages.get(language, error_messages["fr"])
        
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
    
    def create_audio_explanation(self, ocr_text, written_explanation, language_code="fr"):
        """
        Crée une version spécifiquement conçue pour l'audio
        Plus conversationnelle et pédagogique, adaptée à la langue
        """
        # Introductions par langue
        intros = {
            "fr": "Bonjour, je vais t'expliquer cet exercice.",
            "ln": "Mbote, nakoyebisa yo exercice oyo.",
            "sw": "Habari, nitakueleza zoezi hili.",
            "lu": "Moyo, ndinuandamuna exercice eto.",
            "en": "Hello, let me explain this exercise to you."
        }
        
        # Conclusions par langue
        outros = {
            "fr": "J'espère que cette explication t'a aidé. N'hésite pas à m'envoyer d'autres exercices si tu as besoin d'aide. Bonne continuation dans tes études !",
            "ln": "Nalikí explication oyo esalisi yo. Tinda ngai exercices misusu soki ozali na mposa ya lisalisi. Courage na ba études na yo !",
            "sw": "Natumaini maelezo haya yamekusaidia. Tafadhali nitumie mazoezi mengine ukihitaji msaada. Endelea vizuri na masomo yako !",
            "lu": "Ndinusankila ne explication eto ikuafukile. Tumisha exercices mikuabo udi musue musaidiwu. Courage mu masomo ebe !",
            "en": "I hope this explanation helped you. Feel free to send me other exercises if you need help. Good luck with your studies!"
        }
        
        # Extraire la réponse correcte si elle est identifiée
        answer_match = re.search(r'\*([A-E])\.\s*([^*]+)\*', written_explanation)
        
        intro = intros.get(language_code, intros["fr"])
        outro = outros.get(language_code, outros["fr"])
        
        if answer_match:
            correct_letter = answer_match.group(1)
            correct_answer = answer_match.group(2)
            
            # Créer une explication audio personnalisée
            audio_text = f"""
            {intro}
            
            {self.clean_text_for_speech(ocr_text[:200])}.
            
            {self.clean_text_for_speech(written_explanation)}
            
            {outro}
            """
        else:
            # Version de base si pas de structure claire
            audio_text = f"""
            {intro}
            
            {self.clean_text_for_speech(written_explanation)}
            
            {outro}
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
    
    def process_text_message(self, from_number, text):
        """Traite un message texte avec support multilingue et RAG"""
        print(f"\n[TEXT] De {from_number}: {text}")
        
        # 1. Vérifier si c'est une sélection de langue
        is_language_request, language_response = handle_language_selection(
            text, from_number, lang_manager
        )
        
        if is_language_request:
            self.send_message(from_number, language_response)
            return
        
        # 2. Récupérer la langue de l'utilisateur
        user_language = lang_manager.get_user_language(from_number)
        print(f"🌍 Langue utilisateur: {user_language}")
        
        # 3. Si nouveau utilisateur, détecter la langue
        if from_number not in lang_manager.user_sessions:
            detected_lang = lang_manager.detect_language_from_text(text)
            if detected_lang != "fr":
                # Suggérer la langue détectée
                menu = lang_manager.get_language_menu()
                self.send_message(from_number, menu)
                return
        
        # 4. Utiliser le RAG pour enrichir la question
        context = rag.query_rag(text)
        
        # Priorité aux documents de la langue de l'utilisateur
        if user_language != "fr" and user_language in ["ln", "sw", "lu"]:
            lang_keywords = {
                "ln": ["lingala"],
                "sw": ["kiswahili", "swahili"],
                "lu": ["ciluba", "tshiluba"]
            }
            enhanced_query = f"{text} {' '.join(lang_keywords.get(user_language, []))}"
            context = rag.query_rag(enhanced_query)
        
        # 5. Construire le prompt enrichi pour GPT
        gpt_prefix = lang_manager.get_gpt_prompt_prefix(user_language)
        
        if context['found']:
            full_prompt = f"{gpt_prefix}\n\n{context['prompt_enhancement']}"
            print(f"📚 RAG: {len(context['documents'])} documents utilisés")
        else:
            full_prompt = f"{gpt_prefix}\n\nQuestion: {text}\n\nRéponds de manière pédagogique."
        
        # 6. Générer la réponse avec GPT
        written_explanation = self.call_gpt(full_prompt, user_language)
        
        # 7. Formater la réponse
        formatted_response = lang_manager.format_response_for_language(written_explanation, user_language)
        
        # 8. Créer l'audio si langue supportée
        if user_language in ["fr", "en"]:
            audio_text = self.create_audio_explanation(text, written_explanation, user_language)
            audio_path = self.tts.text_to_speech(audio_text, user_language)
            
            if audio_path and os.path.exists(audio_path):
                self.send_audio(from_number, audio_path)
        
        # 9. Envoyer la réponse
        self.send_message(from_number, formatted_response)
    
    def process_image_message(self, from_number, media_id):
        """Pipeline complet de traitement d'image avec multilingue"""
        print(f"\n[NOUVEAU] Image reçue de {from_number}")
        
        # Récupérer la langue de l'utilisateur
        user_language = lang_manager.get_user_language(from_number)
        
        # Messages d'accusé de réception multilingues
        ack_messages = {
            "fr": "📸 Photo reçue ! Je l'analyse...",
            "ln": "📸 Photo eyami ! Nazali kotala yango...",
            "sw": "📸 Picha imepokewa ! Ninaichunguza...",
            "lu": "📸 Photo ituapokelela ! Ndi ngitala...",
            "en": "📸 Photo received! Analyzing..."
        }
        
        # 1. Envoyer accusé de réception
        self.send_message(from_number, ack_messages.get(user_language, ack_messages["fr"]))
        
        # 2. Télécharger l'image
        image_path = self.download_media(media_id)
        if not image_path:
            error_messages = {
                "fr": "❌ Erreur lors du téléchargement de l'image.",
                "ln": "❌ Likambo esalemi na téléchargement.",
                "sw": "❌ Kosa wakati wa kupakua picha.",
                "lu": "❌ Bualu bubi mu téléchargement.",
                "en": "❌ Error downloading the image."
            }
            self.send_message(from_number, error_messages.get(user_language, error_messages["fr"]))
            return
        
        # 3. OCR
        print("[OCR] Lecture en cours...")
        ocr_text = self.ocr.read_image(image_path)
        
        if not ocr_text:
            unclear_messages = {
                "fr": "Je n'ai pas pu lire l'exercice. Essayez avec une photo plus claire.",
                "ln": "Nakoki te kotánga exercice. Meka na photo ya polele.",
                "sw": "Sikuweza kusoma zoezi. Jaribu na picha iliyo wazi zaidi.",
                "lu": "Ntshiakumona kubala exercice. Enza na photo ya bimpe.",
                "en": "I couldn't read the exercise. Try with a clearer photo."
            }
            self.send_message(from_number, unclear_messages.get(user_language, unclear_messages["fr"]))
            return
        
        # 4. RAG - Enrichir avec le contexte
        context = rag.query_rag(ocr_text)
        
        # 5. GPT avec contexte et langue
        print("[GPT] Génération de l'explication...")
        gpt_prefix = lang_manager.get_gpt_prompt_prefix(user_language)
        
        if context['found']:
            full_prompt = f"{gpt_prefix}\n\n{context['prompt_enhancement']}"
            print(f"📚 RAG: {len(context['documents'])} documents utilisés")
        else:
            full_prompt = f"{gpt_prefix}\n\nExercice: {ocr_text}\n\nExplique de manière pédagogique."
        
        written_explanation = self.call_gpt(full_prompt, user_language)
        
        # 6. Créer une version optimisée pour l'audio
        print("[TTS] Préparation du texte pour l'audio...")
        audio_text = self.create_audio_explanation(ocr_text, written_explanation, user_language)
        print(f"[TTS] Texte audio préparé ({len(audio_text)} caractères)")
        
        # 7. TTS si langue supportée
        audio_sent = False
        if user_language in ["fr", "en"]:
            print("[TTS] Création de l'audio...")
            audio_path = self.tts.text_to_speech(audio_text, user_language)
            
            if audio_path and os.path.exists(audio_path):
                print(f"[AUDIO] Envoi du fichier: {audio_path}")
                if self.send_audio(from_number, audio_path):
                    audio_sent = True
                    audio_success_messages = {
                        "fr": "🎵 Explication audio envoyée ! Écoutez pour une meilleure compréhension.",
                        "en": "🎵 Audio explanation sent! Listen for better understanding."
                    }
                    self.send_message(from_number, audio_success_messages.get(user_language, "🎵"))
        
        # 8. Construire et envoyer la réponse texte
        response_headers = {
            "fr": "🤖 MOTEYI - Tuteur IA",
            "ln": "🤖 MOTEYI - Molakisi na IA",
            "sw": "🤖 MOTEYI - Mwalimu wa AI",
            "lu": "🤖 MOTEYI - Mulongeshi wa IA",
            "en": "🤖 MOTEYI - AI Tutor"
        }
        
        # Ajouter info sur les documents utilisés si RAG a trouvé quelque chose
        doc_info = ""
        if context['found'] and context['documents']:
            doc_info = f"\n📚 Documents consultés: {len(context['documents'])}"
            for doc in context['documents'][:2]:
                doc_info += f"\n- {doc['titre']}"
        
        response_message = f"""{response_headers.get(user_language, response_headers["fr"])}

📖 Exercice lu : {ocr_text[:100]}...
{doc_info}

💡 Explication :
{written_explanation}"""
        
        # Formater selon la langue
        formatted_response = lang_manager.format_response_for_language(response_message, user_language)
        
        # 9. Envoyer la réponse
        self.send_message(from_number, formatted_response)
        
        if not audio_sent and user_language not in ["fr", "en"]:
            no_audio_messages = {
                "ln": "ℹ️ Audio ekoki te na lingala, kasi explication ezali awa na likolo.",
                "sw": "ℹ️ Audio haipatikani kwa Kiswahili, lakini maelezo yako hapa juu.",
                "lu": "ℹ️ Audio kayi mu Tshiluba, kasi explication idi apa muulu."
            }
            self.send_message(from_number, no_audio_messages.get(user_language, ""))
        
        print(f"[SUCCÈS] Réponse complète envoyée à {from_number} en {user_language}")

# Ajout de la méthode manquante dans RealGPT si nécessaire
class RealGPTExtended(RealGPT):
    def generate_explanation_with_prompt(self, prompt):
        """Génère une explication avec un prompt personnalisé"""
        try:
            # Utiliser la méthode existante ou appeler directement l'API
            return self.generate_explanation(prompt, "custom")
        except:
            # Fallback si la méthode n'existe pas
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content

# Instance globale
bot = MoteyiCloudBot()

# NOUVELLES FONCTIONS DE COMMANDES
def handle_special_commands(message: str, phone_number: str) -> bool:
    """Gère les commandes spéciales du bot"""
    message_lower = message.lower().strip()
    
    # Commande pour afficher le menu de langues
    if message_lower in ["/langue", "/language", "/lang", "menu", "langue", "language"]:
        menu = lang_manager.get_language_menu()
        bot.send_message(phone_number, menu)
        return True
    
    # Commande pour les statistiques
    if message_lower == "/stats":
        stats = lang_manager.get_stats()
        rag_stats = rag.get_stats()
        
        stats_message = f"""📊 *Statistiques Moteyi v2.0*
        
🌍 *Langues:*
- Utilisateurs: {stats['total_users']}
- Plus utilisée: {stats.get('most_used', 'fr').upper()}

📚 *RAG Curriculum RDC:*
- Documents: {rag_stats['documents_loaded']} 
- Requêtes: {rag_stats['queries']}
- Succès: {rag_stats['hit_rate']:.1f}%

🔥 *Sprint Phoenix 72h*
- Points validés: A ✅ B ✅
- Progression: 50%"""
        
        bot.send_message(phone_number, stats_message)
        return True
    
    # Commande d'aide
    if message_lower in ["/aide", "/help", "aide", "help", "?", "/start"]:
        user_lang = lang_manager.get_user_language(phone_number)
        help_messages = {
            "fr": """🤖 *Moteyi v2.0 - Tuteur IA*
            
Comment m'utiliser:
📸 Envoyez une photo d'exercice
💬 Posez une question directe
🌍 Tapez *langue* pour changer de langue

Je connais le programme scolaire RDC !
            
Commandes:
/langue - Menu des langues (5 disponibles)
/stats - Statistiques
/aide - Cette aide""",
            
            "ln": """🤖 *Moteyi v2.0 - Molakisi IA*
            
Ndenge ya kosalela ngai:
📸 Tinda foto ya exercice
💬 Tuna motuna
🌍 Koma *langue* mpo na kobongola monoko

Nayebi programme ya kelasi ya RDC!

Bacommande:
/langue - Menu ya minoko (5 ezali)
/stats - Bastatistique  
/aide - Lisalisi oyo""",
            
            "sw": """🤖 *Moteyi v2.0 - Mwalimu AI*
            
Jinsi ya kunitumia:
📸 Tuma picha ya zoezi
💬 Uliza swali
🌍 Andika *langue* kubadilisha lugha

Najua mtaala wa DRC!

Amri:
/langue - Menyu ya lugha (5 zinapatikana)
/stats - Takwimu
/aide - Msaada huu""",
            
            "lu": """🤖 *Moteyi v2.0 - Mulongeshi IA*
            
Mudimu wa kunsebenzesa:
📸 Tumisha foto ya exercice
💬 Entroga tshiulumuna
🌍 Funda *langue* bua kubandula tshiena-muteketa

Ngijua programme ya RDC!

Miakulo:
/langue - Menu ya nyema (5 idi)
/stats - Statistiques
/aide - Musaidiwu unu""",
            
            "en": """🤖 *Moteyi v2.0 - AI Tutor*
            
How to use me:
📸 Send a photo of an exercise
💬 Ask a direct question
🌍 Type *langue* to change language

I know the DRC curriculum!

Commands:
/langue - Language menu (5 available)
/stats - Statistics
/aide - This help"""
        }
        
        help_text = help_messages.get(user_lang, help_messages["fr"])
        bot.send_message(phone_number, help_text)
        return True
    
    return False

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
    """Traite les messages entrants avec support multilingue"""
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
                                
                                # Vérifier d'abord les commandes spéciales
                                if not handle_special_commands(text, from_number):
                                    # Sinon traiter normalement
                                    bot.process_text_message(from_number, text)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MOTEYI BOT v2.0 - WHATSAPP CLOUD API")
    print("✨ Multilingue + RAG + Audio Pédagogique")
    print("="*50)
    print(f"📱 Phone ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Token: ...{ACCESS_TOKEN[-10:] if ACCESS_TOKEN else 'NON DÉFINI'}")
    print(f"🌍 Langues: FR, Lingala, Kiswahili, Tshiluba, English")
    print(f"📚 Documents RAG: {len(rag.documents)} chargés")
    print("="*50)
    print("\n[NEXT] Lancez ngrok dans un autre terminal:")
    print("ngrok http 5000")
    print("\nPuis configurez le webhook dans Meta")
    print("="*50)
    
    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=5000, debug=True)