#!/usr/bin/env python3
"""
Module de connexion RAG pour le bot Moteyi/Eteyelo
Connecte les 117 documents du curriculum RDC au pipeline WhatsApp
Version: 1.0 - Sprint Phoenix 72h
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

class CongoRAGConnector:
    """
    Connecteur entre le système RAG et le bot WhatsApp
    Interroge les 117 documents RDC pour enrichir les réponses GPT
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Initialise le connecteur RAG
        
        Args:
            base_path: Chemin vers le dossier data du projet
        """
        self.base_path = Path(base_path)
        # Chemins réels des fichiers
        self.manifest_path = self.base_path / "index" / "manifest.json"
        self.catalog_path = self.base_path / "rag_seed" / "rag_seed_catalog.csv"
        
        # Charger les documents
        self.manifest = self._load_manifest()
        self.catalog = self._load_catalog()
        
        # Cache pour optimiser les recherches
        self.cache = {}
        
        # Statistiques d'usage
        self.stats = {
            "queries": 0,
            "hits": 0,
            "cache_hits": 0,
            "avg_docs_returned": 0
        }
        
        print(f"✅ RAG Connector initialisé avec {len(self.manifest)} documents")
    
    def _load_manifest(self) -> Dict:
        """Charge le manifest.json avec les documents indexés"""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📚 Manifest chargé: {len(data.get('documents', []))} documents")
                return data
        except Exception as e:
            print(f"❌ Erreur chargement manifest: {e}")
            return {"documents": []}
    
    def _load_catalog(self) -> List[Dict]:
        """Charge le catalog CSV avec les métadonnées enrichies"""
        catalog = []
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    catalog.append(row)
            print(f"📋 Catalog chargé: {len(catalog)} entrées")
            return catalog
        except Exception as e:
            print(f"❌ Erreur chargement catalog: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrait les mots-clés pertinents d'une question
        
        Args:
            text: Question de l'utilisateur
            
        Returns:
            Liste de mots-clés normalisés
        """
        # Mots vides à ignorer (français + langues locales)
        stopwords = {
            'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'ou', 
            'est', 'sont', 'être', 'avoir', 'que', 'qui', 'quoi', 'comment',
            'pourquoi', 'où', 'quand', 'dans', 'sur', 'avec', 'pour', 'par',
            'na', 'ya', 'po', 'te', 'pe', 'mpe'  # Lingala common words
        }
        
        # Nettoyer et découper le texte
        text_lower = text.lower()
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]+\b', text_lower)
        
        # Filtrer les mots vides et garder les mots significatifs
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Ajouter des variantes pour les termes éducatifs communs
        education_terms = {
            'math': ['mathématique', 'mathématiques', 'calcul', 'géométrie'],
            'français': ['francais', 'grammaire', 'conjugaison', 'orthographe'],
            'science': ['sciences', 'physique', 'chimie', 'biologie'],
            'histoire': ['histoires', 'géographie', 'civisme'],
            'primaire': ['1ère', '2ème', '3ème', '4ème', '5ème', '6ème'],
            'secondaire': ['1er', '2e', '3e', '4e', '5e', '6e']
        }
        
        expanded_keywords = []
        for kw in keywords:
            expanded_keywords.append(kw)
            for term, variants in education_terms.items():
                if kw in variants or term in kw:
                    expanded_keywords.extend(variants)
        
        return list(set(expanded_keywords))
    
    def _calculate_relevance_score(self, doc: Dict, keywords: List[str]) -> float:
        """
        Calcule un score de pertinence pour un document
        
        Args:
            doc: Document du manifest/catalog
            keywords: Mots-clés de la recherche
            
        Returns:
            Score de pertinence (0-1)
        """
        score = 0.0
        
        # Récupérer les métadonnées du document
        doc_id = doc.get('id', '')
        doc_title = doc.get('titre', doc.get('file', '')).lower()
        doc_type = doc.get('type_doc', '').lower()
        doc_grade = doc.get('grade_level', '').lower()
        doc_subject = doc.get('matiere', '').lower()
        
        # Pondération par champ
        weights = {
            'title': 0.4,
            'subject': 0.3,
            'grade': 0.2,
            'type': 0.1
        }
        
        # Calculer les correspondances
        for keyword in keywords:
            if keyword in doc_title:
                score += weights['title']
            if keyword in doc_subject:
                score += weights['subject']
            if keyword in doc_grade:
                score += weights['grade']
            if keyword in doc_type:
                score += weights['type']
        
        # Normaliser le score
        return min(score / len(keywords) if keywords else 0, 1.0)
    
    def query_rag(self, 
                  question: str, 
                  grade_level: Optional[str] = None,
                  subject: Optional[str] = None,
                  max_docs: int = 3) -> Dict:
        """
        Interroge le système RAG pour obtenir le contexte pertinent
        
        Args:
            question: Question de l'utilisateur
            grade_level: Niveau scolaire (optionnel)
            subject: Matière (optionnel)
            max_docs: Nombre maximum de documents à retourner
            
        Returns:
            Dictionnaire avec contexte et métadonnées
        """
        self.stats["queries"] += 1
        
        # Vérifier le cache
        cache_key = f"{question}_{grade_level}_{subject}"
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return self.cache[cache_key]
        
        # Extraire les mots-clés
        keywords = self._extract_keywords(question)
        if grade_level:
            keywords.append(grade_level.lower())
        if subject:
            keywords.append(subject.lower())
        
        print(f"🔍 Recherche RAG: {len(keywords)} mots-clés extraits")
        
        # Chercher dans les documents disponibles
        results = []
        for doc in self.documents:
            score = self._calculate_relevance_score(doc, keywords)
            if score > 0.1:  # Seuil de pertinence minimum
                results.append({
                    'document': doc,
                    'score': score
                })
        
        # Trier par pertinence et garder les top N
        results.sort(key=lambda x: x['score'], reverse=True)
        top_results = results[:max_docs]
        
        if top_results:
            self.stats["hits"] += 1
            self.stats["avg_docs_returned"] = (
                (self.stats["avg_docs_returned"] * (self.stats["queries"] - 1) + len(top_results)) 
                / self.stats["queries"]
            )
        
        # Construire le contexte
        context = self._build_context(top_results, question)
        
        # Mettre en cache
        self.cache[cache_key] = context
        
        return context
    
    def _build_context(self, results: List[Dict], question: str) -> Dict:
        """
        Construit le contexte enrichi pour GPT
        
        Args:
            results: Documents pertinents avec scores
            question: Question originale
            
        Returns:
            Contexte structuré pour enrichir le prompt GPT
        """
        if not results:
            return {
                'found': False,
                'context': '',
                'documents': [],
                'prompt_enhancement': f"Question: {question}\n\nRéponds de manière pédagogique."
            }
        
        # Construire le contexte textuel
        context_parts = []
        documents_refs = []
        
        for idx, result in enumerate(results):
            doc = result['document']
            score = result['score']
            
            # Extraire les métadonnées depuis le chemin et titre
            doc_file = doc.get('file', '')
            doc_title = doc.get('title', 'Document')
            
            # Détection intelligente du niveau et de la matière
            niveau = 'Non spécifié'
            matiere = 'Non spécifiée'
            langue = 'Français'
            
            # Niveau
            if 'primaire' in doc_file:
                for i in range(1, 7):
                    if f'{i}e' in doc_title.lower():
                        niveau = f'{i}e année primaire'
                        break
            elif '7eme_EB' in doc_file or '7ème EB' in doc_title:
                niveau = '7ème EB (1ère secondaire)'
            elif '8eme_EB' in doc_file or '8ème EB' in doc_title:
                niveau = '8ème EB (2ème secondaire)'
            elif '1ere_HS' in doc_file or '1ère HS' in doc_title:
                niveau = '3ème secondaire (1ère HS)'
            elif '2eme_HS' in doc_file or '2ème HS' in doc_title:
                niveau = '4ème secondaire (2ème HS)'
            elif '3eme_HS' in doc_file or '3ème HS' in doc_title:
                niveau = '5ème secondaire (3ème HS)'
            elif '4eme_HS' in doc_file or '4ème HS' in doc_title:
                niveau = '6ème secondaire (4ème HS)'
            
            # Matière et langue
            if 'math' in doc_file.lower() or 'math' in doc_title.lower():
                matiere = 'Mathématiques'
            elif 'francais' in doc_title.lower():
                matiere = 'Français'
            elif 'lingala' in doc_file.lower() or 'lingala' in doc_title.lower():
                matiere = 'Lingala'
                langue = 'Lingala'
            elif 'kiswahili' in doc_file.lower() or 'kiswahili' in doc_title.lower():
                matiere = 'Kiswahili'
                langue = 'Kiswahili'
            elif 'ciluba' in doc_file.lower() or 'ciluba' in doc_title.lower():
                matiere = 'Tshiluba'
                langue = 'Tshiluba'
            elif 'svt' in doc_file.lower():
                matiere = 'Sciences de la Vie et de la Terre'
            elif 'spttic' in doc_file.lower() or 'sptic' in doc_file.lower():
                matiere = 'Sciences Physiques et TIC'
            elif 'histoire' in doc_file.lower():
                matiere = 'Histoire'
            elif 'geographie' in doc_file.lower():
                matiere = 'Géographie'
            elif 'informatique' in doc_file.lower():
                matiere = 'Informatique'
            
            # Type de document
            doc_type = 'Document pédagogique'
            if 'guide' in doc_title.lower():
                doc_type = "Guide de l'enseignant"
            elif 'manuel' in doc_title.lower():
                doc_type = "Manuel de l'élève"
            elif 'cahier' in doc_title.lower():
                doc_type = "Cahier d'exercices"
            elif 'programme' in doc_title.lower() or 'PE' in doc.get('id', ''):
                doc_type = 'Programme éducatif officiel'
            
            # Référence du document
            doc_ref = {
                'titre': doc_title,
                'type': doc_type,
                'niveau': niveau,
                'matiere': matiere,
                'langue': langue,
                'score': round(score, 2)
            }
            documents_refs.append(doc_ref)
            
            # Contexte textuel
            context_parts.append(
                f"📚 Document {idx+1}: {doc_title}\n"
                f"   Type: {doc_type}\n"
                f"   Niveau: {niveau}\n"
                f"   Matière: {matiere}\n"
                f"   Langue: {langue}\n"
            )
        
        # Construire le prompt enrichi pour GPT
        context_text = "\n".join(context_parts)
        
        # Déterminer la langue dominante des documents trouvés
        langues_trouvees = [doc['langue'] for doc in documents_refs]
        langue_principale = max(set(langues_trouvees), key=langues_trouvees.count)
        
        prompt_enhancement = f"""Tu es un tuteur pédagogique expert du curriculum de la République Démocratique du Congo (RDC).

📚 DOCUMENTS DU PROGRAMME NATIONAL CONSULTÉS:
{context_text}

❓ QUESTION DE L'ÉLÈVE:
{question}

🎯 INSTRUCTIONS IMPORTANTES:
1. Base ta réponse sur les documents officiels du MEPST (Ministère de l'Enseignement Primaire, Secondaire et Technique)
2. Utilise des exemples locaux et culturellement pertinents pour la RDC:
   - Références géographiques: fleuve Congo, Kinshasa, Lubumbashi, Goma, etc.
   - Contexte local: marché central, école du quartier, saison sèche/pluies
   - Monnaie: Francs congolais (FC)
   - Noms congolais dans les exemples

3. Si les documents sont en {langue_principale}, tu peux répondre dans cette langue si approprié
4. Cite le document source si tu fais référence à une leçon spécifique
5. Explique de manière claire, progressive et encourageante
6. Adapte ton niveau de langage au niveau scolaire identifié

🌍 CONTEXTE CULTUREL RDC:
- Salutations respectueuses (Mbote, Jambo selon la région)
- Valorise l'effort et la persévérance
- Encourage la solidarité et l'entraide entre élèves

Réponds de manière pédagogique, bienveillante et culturellement appropriée."""
        
        return {
            'found': True,
            'context': context_text,
            'documents': documents_refs,
            'prompt_enhancement': prompt_enhancement,
            'keywords': results[0]['document'].get('keywords', []) if results else [],
            'langue_suggeree': langue_principale
        }
    
    def enhance_prompt(self, question: str, context: Dict) -> str:
        """
        Enrichit le prompt pour GPT avec le contexte RAG
        
        Args:
            question: Question originale
            context: Contexte retourné par query_rag
            
        Returns:
            Prompt enrichi pour GPT
        """
        return context.get('prompt_enhancement', question)
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation du RAG"""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'hit_rate': (self.stats['hits'] / self.stats['queries'] * 100) if self.stats['queries'] > 0 else 0,
            'cache_hit_rate': (self.stats['cache_hits'] / self.stats['queries'] * 100) if self.stats['queries'] > 0 else 0
        }
    
    def clear_cache(self):
        """Vide le cache de recherche"""
        self.cache.clear()
        print("🗑️ Cache RAG vidé")


# Fonction d'intégration pour le bot Flask existant
def integrate_with_flask_bot(extracted_text: str, user_session: Optional[Dict] = None) -> str:
    """
    Fonction d'intégration pour le bot Flask existant
    
    Args:
        extracted_text: Texte extrait par OCR
        user_session: Session utilisateur avec grade_level, subject, etc.
        
    Returns:
        Prompt enrichi pour GPT
    """
    # Initialiser le connecteur (singleton pattern recommandé en production)
    rag = CongoRAGConnector()
    
    # Extraire les métadonnées de session si disponibles
    grade_level = user_session.get('grade_level') if user_session else None
    subject = user_session.get('subject') if user_session else None
    
    # Interroger le RAG
    context = rag.query_rag(
        question=extracted_text,
        grade_level=grade_level,
        subject=subject,
        max_docs=3
    )
    
    # Retourner le prompt enrichi
    return rag.enhance_prompt(extracted_text, context)


# Tests unitaires
if __name__ == "__main__":
    print("🚀 Test du Connecteur RAG Moteyi/Eteyelo\n")
    
    # Initialiser le connecteur
    rag = CongoRAGConnector()
    
    # Test 1: Question simple
    print("Test 1: Question de mathématiques primaire")
    print("-" * 50)
    question1 = "Comment calculer l'aire d'un rectangle en 5ème primaire?"
    context1 = rag.query_rag(question1, grade_level="5ème primaire", subject="mathématiques")
    print(f"Documents trouvés: {len(context1['documents'])}")
    if context1['found']:
        for doc in context1['documents']:
            print(f"  - {doc['titre']} (score: {doc['score']})")
    print()
    
    # Test 2: Question en contexte
    print("Test 2: Question d'histoire avec contexte local")
    print("-" * 50)
    question2 = "Quelle est l'histoire de l'indépendance du Congo?"
    context2 = rag.query_rag(question2, subject="histoire")
    print(f"Contexte enrichi généré: {context2['found']}")
    print()
    
    # Test 3: Intégration Flask
    print("Test 3: Intégration avec le bot Flask")
    print("-" * 50)
    ocr_text = "L'opération par laquelle l'enseignant maintient le manuel scolaire dans un bon état"
    enhanced_prompt = integrate_with_flask_bot(ocr_text, {'grade_level': '3ème secondaire'})
    print(f"Prompt enrichi (premiers 200 chars):\n{enhanced_prompt[:200]}...")
    print()
    
    # Afficher les statistiques
    print("📊 Statistiques RAG")
    print("-" * 50)
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")