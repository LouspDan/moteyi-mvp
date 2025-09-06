#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline MVP Moteyi - Version Mock OCR
WhatsApp -> Mock OCR -> RAG -> GPT -> TTS
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

# Mock OCR en attendant Tesseract
def mock_ocr(image_path):
    """Simule l'OCR avec differents exercices"""
    
    # Exemples d'exercices pour tester
    exercises = [
        """Exercice de Mathematiques
        Calcule les additions suivantes:
        15 + 23 = ?
        47 + 38 = ?
        
        Probleme: Papa achete 25 mangues au marche.
        Il en donne 12 a ses enfants.
        Combien lui reste-t-il de mangues?""",
        
        """Exercice de Francais
        Complete avec le bon verbe:
        Les enfants _____ (jouer) dans la cour.
        Mama _____ (preparer) le diner.
        
        Mets au pluriel:
        Un livre -> Des _____
        Le cahier -> Les _____""",
        
        """Sciences Naturelles
        Questions:
        1. Cite 3 parties du corps humain
        2. Que mange une chevre?
        3. De quelle couleur sont les feuilles?"""
    ]
    
    # Retourner un exercice au hasard
    import random
    text = random.choice(exercises)
    
    print("[MOCK OCR] Texte simule pour test")
    print("-" * 40)
    print(text[:100] + "...")
    print("-" * 40)
    
    return text

# Recherche RAG simplifiee
def search_rag_context(query_text):
    """Cherche le contexte dans les documents RAG"""
    
    # Pour le MVP, contexte fixe base sur le programme RDC
    contexts = {
        "mathematiques": """Programme RDC - 3eme primaire:
        - Addition et soustraction jusqu'a 100
        - Introduction multiplication
        - Resolution de problemes simples avec objets du quotidien
        - Utiliser exemples locaux: mangues, bananes, francs congolais""",
        
        "francais": """Programme RDC - 3eme primaire:
        - Conjugaison present de l'indicatif
        - Accord sujet-verbe
        - Pluriel des noms simples
        - Vocabulaire du quotidien congolais""",
        
        "sciences": """Programme RDC - 3eme primaire:
        - Le corps humain et ses parties
        - Les animaux domestiques
        - Les plantes de notre environnement
        - L'hygiene de base"""
    }
    
    # Detecter le type d'exercice
    query_lower = query_text.lower()
    
    if any(word in query_lower for word in ['addition', 'calcul', 'probleme', '+', '=']):
        context = contexts["mathematiques"]
        subject = "mathematiques"
    elif any(word in query_lower for word in ['verbe', 'pluriel', 'conjugue']):
        context = contexts["francais"]
        subject = "francais"
    else:
        context = contexts["sciences"]
        subject = "sciences"
    
    print(f"[RAG] Contexte trouve: {subject}")
    return context

# Generation GPT simulee (sans API pour test)
def generate_explanation_mock(exercise_text, context, language="lingala"):
    """Genere une explication (mock sans API)"""
    
    explanations = {
        "lingala": f"""Mbote! Nazali Moteyi, prof na yo.

Tala exercice oyo: {exercise_text[:50]}...

NA LINGALA:
- Yeba que 15 + 23 = 38
- Tanga na matoyi na yo: kumi na mitano... plus tuku mibale na misato
- Kanisa na exemple: soki ozali na mbongo 15 francs, pe bazali kopesa yo 23 francs, okozala na 38 francs

Kokoma na cahier na yo pe meka lisusu!
Programme ya kelasi: {context[:100]}...""",

        "francais": f"""Bonjour! Je suis Moteyi, ton tuteur.

Exercice: {exercise_text[:50]}...

EXPLICATION:
- Pour l'addition 15 + 23, compte d'abord les dizaines: 10 + 20 = 30
- Puis ajoute les unites: 5 + 3 = 8
- Donc 15 + 23 = 38

N'oublie pas de bien ecrire dans ton cahier!
Contexte: {context[:100]}..."""
    }
    
    explanation = explanations.get(language, explanations["francais"])
    
    print(f"[GPT MOCK] Explication generee en {language}")
    print(f"[LONGUEUR] {len(explanation)} caracteres")
    
    return explanation

# TTS Mock (sans synthese reelle)
def text_to_speech_mock(text, language="lingala"):
    """Simule la generation audio"""
    
    # Pour le vrai MVP, utiliser gTTS ou ElevenLabs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file = f"data/audio_responses/response_{timestamp}_{language}.mp3"
    
    # Creer un fichier vide pour simuler
    os.makedirs("data/audio_responses", exist_ok=True)
    
    # Simuler la creation d'un fichier audio
    with open(audio_file, 'w') as f:
        f.write(f"[AUDIO MOCK] {text[:100]}")
    
    print(f"[TTS MOCK] Audio 'genere': {audio_file}")
    print(f"[DUREE] Environ {len(text.split())/3:.1f} secondes")
    
    return audio_file

# Pipeline complet
def process_whatsapp_image(image_path, language="lingala"):
    """Pipeline complet: Image -> OCR -> RAG -> GPT -> TTS"""
    
    print("\n" + "="*50)
    print("PIPELINE MVP MOTEYI - TRAITEMENT")
    print("="*50)
    
    start_time = time.time()
    
    # 1. OCR (Mock pour l'instant)
    print("\n[1/4] OCR...")
    ocr_text = mock_ocr(image_path)
    
    # 2. RAG Context
    print("\n[2/4] Recherche RAG...")
    context = search_rag_context(ocr_text)
    
    # 3. GPT Explanation
    print("\n[3/4] Generation explication...")
    explanation = generate_explanation_mock(ocr_text, context, language)
    
    # 4. TTS
    print("\n[4/4] Synthese vocale...")
    audio_path = text_to_speech_mock(explanation, language)
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*50)
    print(f"[SUCCESS] Pipeline complete en {elapsed:.2f} secondes!")
    print("="*50)
    
    result = {
        "image": image_path,
        "ocr_text": ocr_text,
        "context": context,
        "explanation": explanation,
        "audio": audio_path,
        "language": language,
        "processing_time": elapsed
    }
    
    # Sauvegarder le resultat
    os.makedirs("data/pipeline_results", exist_ok=True)
    result_file = f"data/pipeline_results/result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] Resultat: {result_file}")
    
    return result

# Test du pipeline
def test_pipeline():
    """Test le pipeline complet avec une image"""
    
    print("\nTEST PIPELINE MVP MOTEYI")
    print("========================\n")
    
    # Utiliser la premiere image capturee
    test_image = "data/received_images/capture_20250902_013644.png"
    
    if not os.path.exists(test_image):
        print("[ERREUR] Image test non trouvee")
        print("Utilisez une image mock...")
        test_image = "mock_image.png"
    
    # Tester en lingala
    print("[TEST 1] Lingala")
    result1 = process_whatsapp_image(test_image, "lingala")
    
    print("\n" + "-"*50 + "\n")
    
    # Tester en francais
    print("[TEST 2] Francais")
    result2 = process_whatsapp_image(test_image, "francais")
    
    print("\n" + "="*50)
    print("TESTS TERMINES")
    print("="*50)
    print("\nMetriques:")
    print(f"- Temps moyen: {(result1['processing_time'] + result2['processing_time'])/2:.2f}s")
    print(f"- Objectif: <5 secondes [{'OK' if result1['processing_time'] < 5 else 'A OPTIMISER'}]")
    print("\nProchaines etapes:")
    print("1. Installer Tesseract pour OCR reel")
    print("2. Connecter OpenAI API pour vraies explications")
    print("3. Ajouter gTTS ou ElevenLabs pour audio reel")
    print("4. Integrer avec WhatsApp listener")

if __name__ == "__main__":
    test_pipeline()
