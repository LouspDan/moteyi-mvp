#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug WhatsApp - Trouve les bons selecteurs
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def debug_whatsapp():
    print("[DEBUG] Analyse de WhatsApp Web")
    print("=" * 50)
    
    # Setup driver
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')
    
    print("[WAIT] Chargement...")
    time.sleep(5)
    
    print("\n[TEST 1] Recherche des conversations")
    print("-" * 30)
    
    # Essayer differents selecteurs pour les chats
    selectors_to_try = [
        ('div[role="listitem"]', 'role=listitem'),
        ('div[class*="conversation"]', 'class conversation'),
        ('div[class*="chat-list"]', 'chat-list'),
        ('div[aria-label*="Chat"]', 'aria-label Chat'),
        ('div[class*="_2gzeB"]', 'class _2gzeB'),
        ('div[class*="copyable-area"]', 'copyable-area')
    ]
    
    for selector, description in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"[TROUVE] {description}: {len(elements)} element(s)")
        except:
            pass
    
    print("\n[TEST 2] Recherche des badges non lus")
    print("-" * 30)
    
    # Essayer de trouver les indicateurs de messages non lus
    unread_selectors = [
        ('span[aria-label*="unread"]', 'aria-label unread'),
        ('span[class*="unread"]', 'class unread'),
        ('div[class*="unread"]', 'div unread'),
        ('span[data-testid*="unread"]', 'data-testid unread'),
        ('div[class*="_38M1B"]', 'class _38M1B'),
        ('span[class*="_1pJ9J"]', 'class _1pJ9J')
    ]
    
    for selector, description in unread_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"[TROUVE] {description}: {len(elements)} element(s)")
                # Afficher le texte du premier
                if elements[0].text:
                    print(f"  Texte: {elements[0].text}")
        except:
            pass
    
    print("\n[TEST 3] Detection manuelle")
    print("-" * 30)
    print("INSTRUCTIONS:")
    print("1. Gardez cette fenetre ouverte")
    print("2. Envoyez-vous un message depuis un autre telephone")
    print("3. Voyez-vous un badge rouge avec un chiffre?")
    print("4. Appuyez sur Entree pour continuer...")
    input()
    
    # Capturer tous les elements avec du texte
    all_spans = driver.find_elements(By.TAG_NAME, 'span')
    badges = []
    for span in all_spans:
        text = span.text.strip()
        # Chercher les badges numeriques (1, 2, 3, etc.)
        if text and text.isdigit() and int(text) < 100:
            badges.append((text, span.get_attribute('class')))
    
    if badges:
        print(f"\n[BADGES] Trouves: {badges}")
        print("Classes a utiliser pour detection:")
        for text, classes in badges:
            print(f"  Badge '{text}': class='{classes}'")
    
    print("\n[TEST 4] Cliquer sur une conversation")
    print("-" * 30)
    print("Cliquez manuellement sur une conversation avec un message non lu")
    print("Appuyez sur Entree apres...")
    input()
    
    # Chercher les messages
    message_selectors = [
        ('div[class*="message"]', 'message'),
        ('span[class*="selectable-text"]', 'selectable-text'),
        ('div[class*="copyable-text"]', 'copyable-text'),
        ('div[data-pre-plain-text]', 'data-pre-plain-text')
    ]
    
    for selector, description in message_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"[TROUVE] {description}: {len(elements)} element(s)")
                # Afficher un exemple
                if elements[-1].text:
                    print(f"  Dernier texte: {elements[-1].text[:50]}...")
        except:
            pass
    
    print("\n[RESULTATS] Selecteurs recommandes:")
    print("=" * 50)
    print("Copiez ces selecteurs pour le script principal")
    
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    debug_whatsapp()
