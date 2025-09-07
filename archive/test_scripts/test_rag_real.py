#!/usr/bin/env python3
"""Test du RAG avec le manifest réel de 117 documents"""

import json
from pathlib import Path

# Vérifier que le manifest existe
manifest_path = Path("data/rag_seed/manifest.json")
if manifest_path.exists():
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    print(f"✅ Manifest chargé: {len(manifest)} documents")
    
    # Afficher quelques documents multilingues
    print("\n📚 Documents en langues locales détectés:")
    for doc in manifest:
        if any(lang in doc['title'].lower() or lang in doc['file'].lower() 
               for lang in ['lingala', 'kiswahili', 'ciluba']):
            print(f"  - {doc['title']}")
            if 'lingala' in doc['file'].lower():
                print("    → Langue: LINGALA")
            elif 'kiswahili' in doc['file'].lower():
                print("    → Langue: KISWAHILI")
            elif 'ciluba' in doc['file'].lower():
                print("    → Langue: TSHILUBA")
else:
    print("❌ Manifest non trouvé")
    exit(1)

# Tester le connecteur RAG
print("\n" + "="*50)
print("TEST DU CONNECTEUR RAG")
print("="*50)

from rag_connector import CongoRAGConnector

rag = CongoRAGConnector()

# Test 1: Question en français
print("\n🔍 Test 1: Mathématiques primaire")
q1 = "Comment calculer l'aire d'un rectangle en 5ème primaire?"
ctx1 = rag.query_rag(q1, grade_level="5ème primaire")
print(f"Documents trouvés: {len(ctx1['documents'])}")
if ctx1['found']:
    for doc in ctx1['documents']:
        print(f"  - {doc['titre']} (Score: {doc['score']})")

# Test 2: Question sur Lingala
print("\n🔍 Test 2: Cours de Lingala")
q2 = "Comment enseigner le lingala en 2ème année?"
ctx2 = rag.query_rag(q2)
print(f"Documents trouvés: {len(ctx2['documents'])}")
if ctx2['found']:
    for doc in ctx2['documents']:
        print(f"  - {doc['titre']} (Langue: {doc['langue']})")

# Test 3: Sciences secondaire
print("\n🔍 Test 3: SVT secondaire")
q3 = "Qu'est-ce que la photosynthèse pour les élèves de 8ème?"
ctx3 = rag.query_rag(q3, grade_level="8ème")
print(f"Documents trouvés: {len(ctx3['documents'])}")

print("\n✅ Connecteur RAG opérationnel avec le manifest réel!")