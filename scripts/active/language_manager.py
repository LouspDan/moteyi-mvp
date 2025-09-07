#!/usr/bin/env python3
import sys
"""
Gestionnaire de langues pour le bot Moteyi
Support : Français, Lingala, Kiswahili, Tshiluba, Anglais
Sprint Phoenix 72h - Point B
"""
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

class LanguageManager:
    """Gère la sélection et les préférences de langue des utilisateurs"""
    
    def __init__(self, default_language: str = "fr"):
        self.languages = {
            "fr": {
                "name": "Français",
                "code": "fr",
                "emoji": "🇫🇷",
                "welcome": "Bienvenue ! Je suis votre tuteur pédagogique.",
                "menu_prompt": "Choisissez votre langue préférée :",
                "confirmation": "Parfait ! Je vais vous répondre en français.",
                "help_prompt": "Envoyez-moi une photo d'exercice ou posez une question."
            },
            "ln": {
                "name": "Lingala",
                "code": "ln",
                "emoji": "🇨🇩",
                "welcome": "Mbote ! Nazali molakisi na yo.",
                "menu_prompt": "Pona monoko na yo :",
                "confirmation": "Malamu ! Nakoyanola yo na Lingala.",
                "help_prompt": "Tinda ngai foto ya exercice to tuna motuna."
            },
            "sw": {
                "name": "Kiswahili",
                "code": "sw",
                "emoji": "🇹🇿",
                "welcome": "Karibu ! Mimi ni mwalimu wako.",
                "menu_prompt": "Chagua lugha yako :",
                "confirmation": "Sawa ! Nitakujibu kwa Kiswahili.",
                "help_prompt": "Nitumie picha ya zoezi au uliza swali."
            },
            "lu": {
                "name": "Tshiluba",
                "code": "lu",
                "emoji": "🇨🇩",
                "welcome": "Moyo ! Ndi mulongeshi webe.",
                "menu_prompt": "Sangula tshiena-muteketa tshiebe :",
                "confirmation": "Bimpe ! Ndinuandamuna mu Tshiluba.",
                "help_prompt": "Tumisha foto ya exercice to entroga tshiulumuna."
            },
            "en": {
                "name": "English",
                "code": "en",
                "emoji": "🇬🇧",
                "welcome": "Welcome! I am your educational tutor.",
                "menu_prompt": "Choose your preferred language:",
                "confirmation": "Great! I will respond to you in English.",
                "help_prompt": "Send me a photo of an exercise or ask a question."
            }
        }
        
        self.default_language = default_language
        self.user_sessions = {}  # Stockage des préférences par numéro
        self.sessions_file = Path("data/user_language_preferences.json")
        self._load_sessions()
    
    def _load_sessions(self):
        """Charge les préférences sauvegardées"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.user_sessions = json.load(f)
            except:
                self.user_sessions = {}
    
    def _save_sessions(self):
        """Sauvegarde les préférences"""
        try:
            self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_sessions, f, ensure_ascii=False, indent=2)
        except:
            pass  # Échec silencieux si impossible de sauvegarder
    
    def get_language_menu(self) -> str:
        """Génère le menu de sélection de langue pour WhatsApp"""
        menu = "🌍 *Sélection de langue / Language Selection*\n\n"
        menu += "Répondez avec le numéro / Reply with number:\n\n"
        
        for idx, (code, lang) in enumerate(self.languages.items(), 1):
            menu += f"{idx}. {lang['emoji']} {lang['name']}\n"
        
        menu += "\n_Exemple: Tapez 1 pour Français_"
        return menu
    
    def parse_language_choice(self, message: str) -> Optional[str]:
        """
        Analyse le choix de langue de l'utilisateur
        
        Args:
            message: Message de l'utilisateur (numéro ou nom de langue)
            
        Returns:
            Code de langue si trouvé, None sinon
        """
        message = message.strip().lower()
        
        # Vérifier si c'est un numéro
        if message.isdigit():
            choice = int(message)
            if 1 <= choice <= len(self.languages):
                codes = list(self.languages.keys())
                return codes[choice - 1]
        
        # Vérifier si c'est un nom de langue
        for code, lang in self.languages.items():
            if message in lang['name'].lower():
                return code
            if message == code:
                return code
        
        # Mots-clés spécifiques
        keywords = {
            'francais': 'fr', 'français': 'fr', 'french': 'fr',
            'lingala': 'ln',
            'kiswahili': 'sw', 'swahili': 'sw',
            'tshiluba': 'lu', 'ciluba': 'lu',
            'english': 'en', 'anglais': 'en'
        }
        
        for keyword, code in keywords.items():
            if keyword in message:
                return code
        
        return None
    
    def set_user_language(self, phone_number: str, language_code: str) -> str:
        """
        Définit la langue préférée d'un utilisateur
        
        Args:
            phone_number: Numéro WhatsApp
            language_code: Code de langue
            
        Returns:
            Message de confirmation dans la langue choisie
        """
        if language_code not in self.languages:
            language_code = self.default_language
        
        self.user_sessions[phone_number] = {
            'language': language_code,
            'last_update': str(datetime.now().isoformat())
        }
        self._save_sessions()
        
        return self.languages[language_code]['confirmation']
    
    def get_user_language(self, phone_number: str) -> str:
        """
        Récupère la langue préférée d'un utilisateur
        
        Args:
            phone_number: Numéro WhatsApp
            
        Returns:
            Code de langue
        """
        if phone_number in self.user_sessions:
            return self.user_sessions[phone_number].get('language', self.default_language)
        return self.default_language
    
    def get_gpt_prompt_prefix(self, language_code: str) -> str:
        """
        Génère le préfixe de prompt pour GPT selon la langue
        
        Args:
            language_code: Code de langue
            
        Returns:
            Instructions pour GPT
        """
        prompts = {
            "fr": """Tu es un tuteur pédagogique expert du curriculum de la RDC.
Réponds en FRANÇAIS avec un vocabulaire adapté au niveau de l'élève.
Utilise des exemples locaux congolais.""",
            
            "ln": """Tu es un tuteur pédagogique expert du curriculum de la RDC.
RÉPONDS UNIQUEMENT EN LINGALA. Utilise un lingala simple et pédagogique.
Exemples : Ebale ya Kongo, zandu ya Kinshasa, mboka ya RDC.
Format de réponse : Explique d'abord, puis donne la réponse.""",
            
            "sw": """Tu es un tuteur pédagogique expert du curriculum de la RDC.
JIBU KWA KISWAHILI TU. Tumia Kiswahili rahisi kwa wanafunzi.
Mifano : Mto Congo, soko la Lubumbashi, nchi ya DRC.
Eleza kwanza, kisha toa jibu.""",
            
            "lu": """Tu es un tuteur pédagogique expert du curriculum de la RDC.
RÉPONDS UNIQUEMENT EN TSHILUBA. Utilise un tshiluba simple.
Tangila malu a ba RDC. Leja bimpe.""",
            
            "en": """You are an expert tutor for the DRC curriculum.
RESPOND IN ENGLISH. Use simple, clear English adapted to the student's level.
Use local Congolese examples when relevant."""
        }
        
        return prompts.get(language_code, prompts["fr"])
    
    def format_response_for_language(self, response: str, language_code: str) -> str:
        """
        Formate la réponse selon la langue (ajoute des éléments culturels)
        
        Args:
            response: Réponse de GPT
            language_code: Code de langue
            
        Returns:
            Réponse formatée
        """
        # Ajouter des salutations appropriées
        greetings = {
            "fr": "",  # Pas de modification
            "ln": "\n\n_Matondo mingi ! (Merci beaucoup !)_",
            "sw": "\n\n_Asante sana ! (Merci beaucoup !)_",
            "lu": "\n\n_Twasakidila ! (Merci !)_",
            "en": "\n\n_Thank you for learning with us!_"
        }
        
        closing = greetings.get(language_code, "")
        return response + closing
    
    def detect_language_from_text(self, text: str) -> str:
        """
        Détecte la langue probable d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Code de langue détecté
        """
        text_lower = text.lower()
        
        # Mots caractéristiques par langue
        indicators = {
            "ln": ["mbote", "malamu", "naza", "nazali", "ndeko", "kobanga", "koloba"],
            "sw": ["habari", "karibu", "asante", "tafadhali", "ndiyo", "hapana", "jambo"],
            "lu": ["moyo", "bimpe", "ndi", "webe", "tshiena", "bualu"],
            "en": ["hello", "thank", "please", "what", "how", "when", "where"],
            "fr": ["bonjour", "merci", "comment", "pourquoi", "quelle", "exercice"]
        }
        
        scores = {lang: 0 for lang in indicators}
        
        for lang, words in indicators.items():
            for word in words:
                if word in text_lower:
                    scores[lang] += 1
        
        # Retourner la langue avec le score le plus élevé
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "fr"  # Défaut au français
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation des langues"""
        stats = {lang: 0 for lang in self.languages}
        
        for session in self.user_sessions.values():
            lang = session.get('language', 'fr')
            if lang in stats:
                stats[lang] += 1
        
        return {
            'total_users': len(self.user_sessions),
            'languages_distribution': stats,
            'most_used': max(stats, key=stats.get) if stats else 'fr'
        }


# Fonctions d'intégration pour le bot WhatsApp
def handle_language_selection(message: str, phone_number: str, lang_manager: LanguageManager) -> Tuple[bool, str]:
    """
    Gère la sélection de langue dans le bot
    
    Args:
        message: Message reçu
        phone_number: Numéro de l'utilisateur
        lang_manager: Instance du gestionnaire de langues
        
    Returns:
        (True si c'était une sélection de langue, Message de réponse)
    """
    # Vérifier si l'utilisateur demande le menu de langues
    if any(keyword in message.lower() for keyword in ['langue', 'language', 'monoko', 'lugha']):
        return True, lang_manager.get_language_menu()
    
    # Vérifier si c'est un choix de langue
    language_code = lang_manager.parse_language_choice(message)
    if language_code:
        confirmation = lang_manager.set_user_language(phone_number, language_code)
        help_text = lang_manager.languages[language_code]['help_prompt']
        return True, f"{confirmation}\n\n{help_text}"
    
    return False, ""


# Tests du module
if __name__ == "__main__":
    print("🌍 Test du Gestionnaire de Langues Moteyi\n")
    
    # Initialiser le gestionnaire
    lang_mgr = LanguageManager()
    
    # Test 1: Menu de langues
    print("📋 Menu de sélection:")
    print(lang_mgr.get_language_menu())
    
    # Test 2: Sélection de langue
    print("\n🔍 Test de sélection:")
    test_choices = ["1", "2", "lingala", "kiswahili", "5"]
    for choice in test_choices:
        result = lang_mgr.parse_language_choice(choice)
        print(f"  '{choice}' → {result} ({lang_mgr.languages.get(result, {}).get('name', 'Invalide')})")
    
    # Test 3: Préfixe GPT
    print("\n📝 Préfixes GPT par langue:")
    for code in ["fr", "ln", "sw"]:
        prefix = lang_mgr.get_gpt_prompt_prefix(code)
        print(f"  {code}: {prefix[:50]}...")
    
    # Test 4: Détection de langue
    print("\n🔎 Détection automatique:")
    test_texts = [
        "Mbote ndeko, nasepeli mingi",
        "Habari yako, karibu sana",
        "Comment calculer l'aire?"
    ]
    for text in test_texts:
        detected = lang_mgr.detect_language_from_text(text)
        print(f"  '{text[:30]}...' → {detected}")
    
    print("\n✅ Module multilingue opérationnel!")