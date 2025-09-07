#!/usr/bin/env python3
"""
Code d'intégration multilingue pour moteyi_whatsapp_cloud_bot.py
Sprint Phoenix 72h - Point B
"""

# ===== SECTION 1: IMPORTS À AJOUTER =====
# Ajouter ces imports en haut de moteyi_whatsapp_cloud_bot.py

from language_manager import LanguageManager, handle_language_selection
from rag_connector import CongoRAGConnector

# ===== SECTION 2: INITIALISATION =====
# Ajouter après les autres initialisations globales

# Initialiser le gestionnaire de langues
lang_manager = LanguageManager(default_language="fr")

# Initialiser le connecteur RAG
rag = CongoRAGConnector(base_path="data")

# ===== SECTION 3: FONCTION PROCESS_MESSAGE MODIFIÉE =====
# Remplacer la fonction process_message existante par celle-ci

def process_message(message_body, phone_number):
    """
    Traite les messages WhatsApp avec support multilingue et RAG
    
    Args:
        message_body: Contenu du message
        phone_number: Numéro de l'expéditeur
    
    Returns:
        Réponse à envoyer
    """
    
    # 1. Vérifier si c'est une demande de sélection de langue
    is_language_request, language_response = handle_language_selection(
        message_body, phone_number, lang_manager
    )
    
    if is_language_request:
        # Envoyer le menu ou la confirmation de langue
        send_whatsapp_message(phone_number, language_response)
        return
    
    # 2. Récupérer la langue de l'utilisateur
    user_language = lang_manager.get_user_language(phone_number)
    print(f"🌍 Langue utilisateur: {user_language}")
    
    # 3. Détecter automatiquement la langue si nouveau message
    if phone_number not in lang_manager.user_sessions:
        detected_lang = lang_manager.detect_language_from_text(message_body)
        if detected_lang != "fr":
            # Proposer de changer de langue
            menu = lang_manager.get_language_menu()
            send_whatsapp_message(phone_number, menu)
            return
    
    # 4. Traiter le message selon le type (image ou texte)
    if is_image_message(message_body):
        # Traiter l'image avec OCR
        extracted_text = process_image_with_ocr(message_body)
    else:
        extracted_text = message_body
    
    # 5. Enrichir avec le RAG (avec priorité aux docs de la bonne langue)
    context = rag.query_rag(extracted_text)
    
    # Filtrer les documents par langue si possible
    if context['found'] and user_language != "fr":
        # Chercher spécifiquement des documents dans la langue de l'utilisateur
        lang_keywords = {
            "ln": ["lingala"],
            "sw": ["kiswahili", "swahili"],
            "lu": ["ciluba", "tshiluba"]
        }
        
        if user_language in lang_keywords:
            # Refaire la recherche avec mots-clés de langue
            enhanced_query = f"{extracted_text} {' '.join(lang_keywords[user_language])}"
            context = rag.query_rag(enhanced_query)
    
    # 6. Construire le prompt GPT avec instructions multilingues
    gpt_prefix = lang_manager.get_gpt_prompt_prefix(user_language)
    
    if context['found']:
        # Utiliser le contexte RAG enrichi
        full_prompt = f"{gpt_prefix}\n\n{context['prompt_enhancement']}"
    else:
        # Prompt simple sans contexte RAG
        full_prompt = f"{gpt_prefix}\n\nQuestion: {extracted_text}\n\nRéponds de manière pédagogique."
    
    # Ajouter une instruction explicite pour la langue de réponse
    if user_language != "fr":
        lang_names = {
            "ln": "LINGALA",
            "sw": "KISWAHILI", 
            "lu": "TSHILUBA",
            "en": "ENGLISH"
        }
        full_prompt += f"\n\n⚠️ IMPORTANT: Réponds UNIQUEMENT en {lang_names.get(user_language, 'FRANÇAIS')}!"
    
    # 7. Appeler GPT avec le prompt enrichi
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un tuteur pédagogique expert du curriculum RDC."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        gpt_response = response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Erreur GPT: {e}")
        # Messages d'erreur multilingues
        error_messages = {
            "fr": "Désolé, une erreur s'est produite. Veuillez réessayer.",
            "ln": "Pardon, likambo moko esalemi. Meka lisusu.",
            "sw": "Samahani, kosa limetokea. Tafadhali jaribu tena.",
            "lu": "Tuasakidila, bualu bubi busambile. Enza kayi.",
            "en": "Sorry, an error occurred. Please try again."
        }
        gpt_response = error_messages.get(user_language, error_messages["fr"])
    
    # 8. Formater la réponse selon la langue
    formatted_response = lang_manager.format_response_for_language(gpt_response, user_language)
    
    # 9. Générer l'audio (si TTS disponible pour la langue)
    audio_file = None
    if user_language in ["fr", "en"]:  # gTTS supporte bien FR et EN
        from gtts import gTTS
        try:
            tts = gTTS(text=gpt_response, lang=user_language)
            audio_file = f"audio_response_{phone_number}_{user_language}.mp3"
            tts.save(audio_file)
            print(f"🔊 Audio généré en {user_language}: {audio_file}")
        except Exception as e:
            print(f"⚠️ TTS non disponible pour {user_language}: {e}")
    
    # 10. Envoyer la réponse (texte + audio si disponible)
    send_whatsapp_message(phone_number, formatted_response)
    
    if audio_file and os.path.exists(audio_file):
        send_whatsapp_audio(phone_number, audio_file)
        # Nettoyer le fichier audio après envoi
        try:
            os.remove(audio_file)
        except:
            pass
    
    # 11. Logger les statistiques
    print(f"""
    📊 Traitement terminé:
    - Utilisateur: {phone_number}
    - Langue: {user_language}
    - Documents RAG utilisés: {len(context.get('documents', []))}
    - Longueur réponse: {len(formatted_response)} caractères
    - Audio généré: {'✅' if audio_file else '❌'}
    """)
    
    return formatted_response


# ===== SECTION 4: COMMANDES SPÉCIALES =====
# Ajouter cette fonction pour gérer les commandes

def handle_special_commands(message: str, phone_number: str) -> bool:
    """
    Gère les commandes spéciales du bot
    
    Returns:
        True si une commande a été traitée
    """
    message_lower = message.lower().strip()
    
    # Commande pour afficher le menu de langues
    if message_lower in ["/langue", "/language", "/lang", "menu"]:
        menu = lang_manager.get_language_menu()
        send_whatsapp_message(phone_number, menu)
        return True
    
    # Commande pour les statistiques
    if message_lower == "/stats":
        stats = lang_manager.get_stats()
        rag_stats = rag.get_stats()
        
        stats_message = f"""📊 *Statistiques Moteyi*
        
🌍 *Langues:*
- Utilisateurs totaux: {stats['total_users']}
- Langue principale: {stats['most_used']}

📚 *RAG:*
- Documents: {rag_stats['documents_loaded']}
- Requêtes: {rag_stats['queries']}
- Taux succès: {rag_stats['hit_rate']:.1f}%
        """
        send_whatsapp_message(phone_number, stats_message)
        return True
    
    # Commande d'aide
    if message_lower in ["/aide", "/help", "aide", "help"]:
        user_lang = lang_manager.get_user_language(phone_number)
        help_messages = {
            "fr": """🤖 *Aide Moteyi*
            
Comment m'utiliser:
📸 Envoyez une photo d'exercice
💬 Posez une question directe
🌍 Tapez /langue pour changer de langue

Commandes:
/langue - Menu des langues
/stats - Statistiques
/aide - Cette aide
            """,
            "ln": """🤖 *Lisalisi ya Moteyi*
            
Ndenge ya kosalela ngai:
📸 Tinda foto ya exercice
💬 Tuna motuna
🌍 Koma /langue mpo na kobongola monoko

Bacommande:
/langue - Menu ya minoko
/stats - Bastatistique
/aide - Lisalisi oyo
            """,
            "sw": """🤖 *Msaada wa Moteyi*
            
Jinsi ya kunitumia:
📸 Tuma picha ya zoezi
💬 Uliza swali
🌍 Andika /langue kubadilisha lugha

Amri:
/langue - Menyu ya lugha
/stats - Takwimu
/aide - Msaada huu
            """,
            "en": """🤖 *Moteyi Help*
            
How to use me:
📸 Send a photo of an exercise
💬 Ask a direct question
🌍 Type /langue to change language

Commands:
/langue - Language menu
/stats - Statistics
/aide - This help
            """
        }
        
        help_text = help_messages.get(user_lang, help_messages["fr"])
        send_whatsapp_message(phone_number, help_text)
        return True
    
    return False


# ===== SECTION 5: MODIFICATION DU WEBHOOK =====
# Modifier la fonction webhook pour intégrer les commandes

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook principal pour recevoir les messages WhatsApp"""
    
    data = request.json
    
    # Extraire le message et le numéro
    message = extract_message_from_webhook(data)
    phone_number = extract_phone_number_from_webhook(data)
    
    if message and phone_number:
        # Vérifier d'abord les commandes spéciales
        if handle_special_commands(message, phone_number):
            return jsonify({"status": "command_processed"}), 200
        
        # Sinon, traiter normalement
        process_message(message, phone_number)
    
    return jsonify({"status": "received"}), 200


# ===== SECTION 6: EXEMPLE D'UTILISATION =====
"""
Flux d'utilisation typique:

1. Nouveau utilisateur envoie "Mbote"
   → Détection automatique Lingala
   → Proposition menu langues
   
2. Utilisateur choisit "2" (Lingala)
   → Confirmation en Lingala
   → Préférence sauvegardée
   
3. Utilisateur envoie photo d'exercice
   → OCR extraction
   → RAG cherche docs Lingala prioritairement
   → GPT répond en Lingala
   → Audio généré si possible
   
4. Utilisateur tape /langue
   → Menu pour changer de langue
   
5. Utilisateur change pour Kiswahili
   → Futures réponses en Kiswahili
"""

print("✅ Module d'intégration multilingue prêt!")
print("📝 Instructions: Copier les sections dans moteyi_whatsapp_cloud_bot.py")