#!/usr/bin/env python3
"""
Test du connecteur RAG avec les chemins corrects
Vérifie que manifest.json et catalog.csv sont accessibles
"""

import json
import csv
import os
from pathlib import Path

print("="*60)
print("🔍 VÉRIFICATION DES FICHIERS RAG")
print("="*60)

# Chemins absolus et relatifs
base_dir = Path("D:/PROJET/moteyi-mvp") if os.path.exists("D:/PROJET/moteyi-mvp") else Path(".")
manifest_path = base_dir / "data" / "index" / "manifest.json"
catalog_path = base_dir / "data" / "rag_seed" / "rag_seed_catalog.csv"

# Alternative avec chemins relatifs
if not manifest_path.exists():
    manifest_path = Path("data/index/manifest.json")
if not catalog_path.exists():
    catalog_path = Path("data/rag_seed/rag_seed_catalog.csv")

print(f"\n📁 Répertoire de travail: {os.getcwd()}")
print(f"📄 Manifest: {manifest_path}")
print(f"📊 Catalog: {catalog_path}")

# Vérification du manifest
print("\n" + "-"*40)
print("1️⃣ VÉRIFICATION DU MANIFEST")
print("-"*40)

if manifest_path.exists():
    print(f"✅ Manifest trouvé: {manifest_path}")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        if isinstance(manifest, list):
            print(f"✅ {len(manifest)} documents dans le manifest")
            
            # Analyser les langues
            langues = {'Français': 0, 'Lingala': 0, 'Kiswahili': 0, 'Ciluba': 0}
            niveaux = {'Primaire': 0, 'Secondaire': 0, 'Autres': 0}
            
            for doc in manifest:
                doc_file = doc.get('file', '').lower()
                doc_title = doc.get('title', '').lower()
                
                # Détecter la langue
                if 'lingala' in doc_file or 'lingala' in doc_title:
                    langues['Lingala'] += 1
                elif 'kiswahili' in doc_file or 'kiswahili' in doc_title:
                    langues['Kiswahili'] += 1
                elif 'ciluba' in doc_file or 'ciluba' in doc_title:
                    langues['Ciluba'] += 1
                else:
                    langues['Français'] += 1
                
                # Détecter le niveau
                if 'primaire' in doc_file:
                    niveaux['Primaire'] += 1
                elif 'secondaire' in doc_file:
                    niveaux['Secondaire'] += 1
                else:
                    niveaux['Autres'] += 1
            
            print("\n📚 Répartition par langue:")
            for langue, count in langues.items():
                if count > 0:
                    print(f"   - {langue}: {count} documents")
            
            print("\n🎓 Répartition par niveau:")
            for niveau, count in niveaux.items():
                if count > 0:
                    print(f"   - {niveau}: {count} documents")
            
            # Afficher quelques exemples
            print("\n📋 Exemples de documents multilingues:")
            count = 0
            for doc in manifest[:50]:  # Parcourir les 50 premiers
                if any(lang in doc.get('title', '').lower() or lang in doc.get('file', '').lower() 
                       for lang in ['lingala', 'kiswahili', 'ciluba']):
                    print(f"   - {doc.get('title', 'Sans titre')}")
                    count += 1
                    if count >= 5:
                        break
        else:
            print("⚠️ Format du manifest inattendu (n'est pas une liste)")
            
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de lecture du manifest JSON: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
else:
    print(f"❌ Manifest non trouvé à: {manifest_path}")

# Vérification du catalog
print("\n" + "-"*40)
print("2️⃣ VÉRIFICATION DU CATALOG CSV")
print("-"*40)

if catalog_path.exists():
    print(f"✅ Catalog trouvé: {catalog_path}")
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"✅ {len(rows)} entrées dans le catalog")
            
            if rows:
                print(f"\n📊 Colonnes disponibles: {list(rows[0].keys())}")
                print("\n📄 Premiers documents:")
                for row in rows[:3]:
                    print(f"   - ID: {row.get('id', 'N/A')}")
                    if 'file_path' in row:
                        print(f"     Fichier: {row.get('file_path', '')}")
    except Exception as e:
        print(f"❌ Erreur lecture catalog: {e}")
else:
    print(f"❌ Catalog non trouvé à: {catalog_path}")

# Test du connecteur RAG
print("\n" + "="*60)
print("3️⃣ TEST DU CONNECTEUR RAG")
print("="*60)

try:
    # Importer le connecteur avec le bon chemin
    import sys
    scripts_path = base_dir / "scripts" if (base_dir / "scripts").exists() else Path("scripts")
    if scripts_path.exists():
        sys.path.insert(0, str(scripts_path))
    
    from rag_connector import CongoRAGConnector
    
    print("✅ Module rag_connector importé")
    
    # Initialiser le connecteur
    rag = CongoRAGConnector(base_path="data")
    
    # Test de recherche simple
    print("\n🔍 Test de recherche RAG:")
    
    # Test 1: Mathématiques
    question = "Comment calculer l'aire d'un rectangle?"
    print(f"\nQuestion: {question}")
    context = rag.query_rag(question)
    
    if context['found']:
        print(f"✅ {len(context['documents'])} documents trouvés")
        for doc in context['documents'][:3]:
            print(f"   - {doc['titre']} (Score: {doc['score']})")
    else:
        print("⚠️ Aucun document trouvé")
    
    # Test 2: Lingala
    question2 = "Guide lingala 2ème année"
    print(f"\nQuestion: {question2}")
    context2 = rag.query_rag(question2)
    
    if context2['found']:
        print(f"✅ {len(context2['documents'])} documents trouvés")
        for doc in context2['documents'][:3]:
            print(f"   - {doc['titre']}")
            print(f"     Langue: {doc.get('langue', 'N/A')}")
    else:
        print("⚠️ Aucun document trouvé")
    
    # Afficher les statistiques
    stats = rag.get_stats()
    print(f"\n📊 Statistiques RAG:")
    print(f"   - Requêtes: {stats['queries']}")
    print(f"   - Taux de succès: {stats['hit_rate']:.1f}%")
    
except ImportError as e:
    print(f"❌ Impossible d'importer rag_connector: {e}")
    print("   Vérifiez que scripts/rag_connector.py existe")
except Exception as e:
    print(f"❌ Erreur lors du test RAG: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ TEST TERMINÉ")
print("="*60)

# Résumé final
print("\n📋 RÉSUMÉ:")
if manifest_path.exists() and catalog_path.exists():
    print("✅ Tous les fichiers RAG sont présents")
    print("👉 Prochaine étape: Intégrer le RAG dans le bot Flask")
else:
    print("❌ Fichiers manquants - vérifier les chemins")
    if not manifest_path.exists():
        print(f"   - Manifest manquant: {manifest_path}")
    if not catalog_path.exists():
        print(f"   - Catalog manquant: {catalog_path}")