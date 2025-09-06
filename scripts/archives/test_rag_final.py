#!/usr/bin/env python3
"""
Test final du connecteur RAG après corrections
Sprint Phoenix 72h - Point A : Validation du RAG
"""

import json
import sys
from pathlib import Path

print("="*60)
print("🚀 TEST FINAL DU CONNECTEUR RAG - MOTEYI/ETEYELO")
print("="*60)

# Ajouter le chemin des scripts
sys.path.insert(0, 'scripts')

# Test 1: Vérification rapide du manifest
print("\n📚 Vérification du Manifest")
print("-"*40)
manifest_path = Path("data/index/manifest.json")
manifest = json.load(open(manifest_path, 'r', encoding='utf-8'))
print(f"✅ {len(manifest)} documents chargés")

# Compter les documents multilingues
langues = {'Lingala': 0, 'Kiswahili': 0, 'Ciluba': 0}
for doc in manifest:
    doc_str = str(doc).lower()
    if 'lingala' in doc_str:
        langues['Lingala'] += 1
    if 'kiswahili' in doc_str:
        langues['Kiswahili'] += 1
    if 'ciluba' in doc_str:
        langues['Ciluba'] += 1

print("\n🌍 Documents en langues locales:")
for langue, count in langues.items():
    print(f"   - {langue}: {count} documents")

# Test 2: Import et initialisation du RAG
print("\n" + "="*60)
print("⚡ TEST DU CONNECTEUR RAG")
print("="*60)

try:
    from rag_connector import CongoRAGConnector
    print("✅ Module rag_connector importé avec succès")
    
    # Initialiser le connecteur
    rag = CongoRAGConnector(base_path="data")
    
    # Vérifier le nombre de documents
    if len(rag.documents) == 117:
        print(f"✅ RAG initialisé avec {len(rag.documents)} documents")
    else:
        print(f"⚠️ RAG initialisé avec {len(rag.documents)} documents (attendu: 117)")
    
    # Test 3: Recherches concrètes
    print("\n🔍 TESTS DE RECHERCHE")
    print("-"*40)
    
    # Test Mathématiques Primaire
    print("\n1️⃣ Test Mathématiques Primaire")
    q1 = "Comment calculer l'aire d'un rectangle en 5ème primaire?"
    ctx1 = rag.query_rag(q1)
    print(f"   Question: {q1}")
    print(f"   ✅ Documents trouvés: {len(ctx1['documents'])}")
    if ctx1['found'] and ctx1['documents']:
        for i, doc in enumerate(ctx1['documents'][:2], 1):
            print(f"   {i}. {doc['titre']}")
            print(f"      Niveau: {doc['niveau']}, Score: {doc['score']}")
    
    # Test Lingala
    print("\n2️⃣ Test Documents Lingala")
    q2 = "Guide enseignant lingala 2ème année"
    ctx2 = rag.query_rag(q2)
    print(f"   Question: {q2}")
    print(f"   ✅ Documents trouvés: {len(ctx2['documents'])}")
    if ctx2['found'] and ctx2['documents']:
        for i, doc in enumerate(ctx2['documents'][:2], 1):
            print(f"   {i}. {doc['titre']}")
            print(f"      Langue: {doc.get('langue', 'N/A')}")
    
    # Test Sciences Secondaire
    print("\n3️⃣ Test Sciences Secondaire")
    q3 = "Photosynthèse SVT 8ème"
    ctx3 = rag.query_rag(q3, grade_level="8ème EB")
    print(f"   Question: {q3}")
    print(f"   ✅ Documents trouvés: {len(ctx3['documents'])}")
    if ctx3['found'] and ctx3['documents']:
        for i, doc in enumerate(ctx3['documents'][:2], 1):
            print(f"   {i}. {doc['titre']}")
            print(f"      Matière: {doc.get('matiere', 'N/A')}")
    
    # Test 4: Vérifier le prompt enrichi
    print("\n4️⃣ Test Enrichissement du Prompt GPT")
    print("-"*40)
    if ctx1['found']:
        prompt = ctx1['prompt_enhancement']
        print("✅ Prompt enrichi généré avec succès")
        print("\n📝 Extrait du prompt enrichi (200 premiers caractères):")
        print(prompt[:200] + "...")
        
        # Vérifier les éléments clés
        elements_cles = ['RDC', 'MEPST', 'fleuve Congo', 'Kinshasa', 'Francs congolais']
        elements_presents = [elem for elem in elements_cles if elem in prompt]
        print(f"\n✅ Éléments contextuels RDC présents: {len(elements_presents)}/{len(elements_cles)}")
        for elem in elements_presents:
            print(f"   - {elem} ✓")
    
    # Test 5: Statistiques
    print("\n📊 STATISTIQUES DU RAG")
    print("-"*40)
    stats = rag.get_stats()
    print(f"   Requêtes effectuées: {stats['queries']}")
    print(f"   Taux de succès: {stats['hit_rate']:.1f}%")
    print(f"   Documents moyens retournés: {stats['avg_docs_returned']:.1f}")
    
    # Validation finale
    print("\n" + "="*60)
    print("✅ VALIDATION DU POINT A - CONNECTEUR RAG")
    print("="*60)
    
    validation_points = {
        "117 documents chargés": len(rag.documents) == 117,
        "Documents multilingues détectés": langues['Lingala'] > 0 and langues['Kiswahili'] > 0,
        "Recherches fonctionnelles": ctx1['found'] or ctx2['found'] or ctx3['found'],
        "Contexte RDC dans les prompts": 'RDC' in str(ctx1.get('prompt_enhancement', '')),
        "Statistiques actives": stats['queries'] > 0
    }
    
    points_valides = sum(validation_points.values())
    total_points = len(validation_points)
    
    print(f"\n📋 Points de validation: {points_valides}/{total_points}")
    for point, valide in validation_points.items():
        status = "✅" if valide else "❌"
        print(f"   {status} {point}")
    
    if points_valides == total_points:
        print("\n🎉 SUCCÈS TOTAL - LE RAG EST 100% OPÉRATIONNEL!")
        print("👉 Prêt pour le Point B: Activation Multilingue")
    elif points_valides >= 3:
        print("\n✅ RAG FONCTIONNEL - Quelques ajustements mineurs possibles")
        print("👉 Peut passer au Point B avec surveillance")
    else:
        print("\n⚠️ RAG PARTIELLEMENT FONCTIONNEL - Corrections nécessaires")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que scripts/rag_connector.py existe et est correct")
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("FIN DU TEST - SPRINT PHOENIX 72H")
print("="*60)