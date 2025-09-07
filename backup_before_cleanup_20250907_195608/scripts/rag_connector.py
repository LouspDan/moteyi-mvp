#!/usr/bin/env python3
"""
Connecteur RAG corrigé pour Moteyi - Version simplifiée
Fonctionne avec le manifest en liste de 117 documents
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
import re

class CongoRAGConnector:
    """Connecteur RAG pour les 117 documents du curriculum RDC"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.manifest_path = self.base_path / "index" / "manifest.json"
        self.catalog_path = self.base_path / "rag_seed" / "rag_seed_catalog.csv"
        
        # Charger les documents
        self.documents = self._load_all_documents()
        self.cache = {}
        self.stats = {"queries": 0, "hits": 0}
        
        print(f"✅ RAG initialisé avec {len(self.documents)} documents")
    
    def _load_all_documents(self) -> List[Dict]:
        """Charge les documents depuis le manifest (liste) ou le catalog"""
        documents = []
        
        # Essayer le manifest d'abord
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
                if isinstance(manifest_data, list):
                    documents = manifest_data
                    print(f"📚 {len(documents)} documents chargés depuis manifest")
        except:
            print("⚠️ Manifest non chargé, essai du catalog...")
        
        # Si pas de manifest, essayer le catalog
        if not documents:
            try:
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        documents.append({
                            'id': row.get('id', ''),
                            'file': row.get('file_path', ''),
                            'title': row.get('titre', row.get('id', '')),
                        })
                print(f"📋 {len(documents)} documents chargés depuis catalog")
            except:
                print("❌ Ni manifest ni catalog trouvé")
        
        return documents
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'une question"""
        stopwords = {'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'ou', 'est', 'comment', 'que'}
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]+\b', text.lower())
        return [w for w in words if w not in stopwords and len(w) > 2]
    
    def _score_document(self, doc: Dict, keywords: List[str]) -> float:
        """Calcule la pertinence d'un document"""
        score = 0.0
        doc_text = f"{doc.get('title', '')} {doc.get('file', '')} {doc.get('id', '')}".lower()
        
        # Détecter niveau et matière depuis le texte
        if 'primaire' in doc_text:
            doc_text += ' primaire école'
        if 'secondaire' in doc_text or 'HS' in doc_text or 'EB' in doc_text:
            doc_text += ' secondaire lycée'
        if 'math' in doc_text:
            doc_text += ' mathématiques calcul géométrie'
        if 'lingala' in doc_text:
            doc_text += ' lingala langue'
        if 'kiswahili' in doc_text:
            doc_text += ' kiswahili swahili langue'
        if 'ciluba' in doc_text:
            doc_text += ' ciluba tshiluba langue'
        if 'svt' in doc_text:
            doc_text += ' sciences biologie vie terre'
        
        # Calculer le score
        for keyword in keywords:
            if keyword in doc_text:
                score += 1.0
        
        return score / max(len(keywords), 1)
    
    def query_rag(self, question: str, grade_level: Optional[str] = None, max_docs: int = 3) -> Dict:
        """Recherche les documents pertinents pour une question"""
        self.stats["queries"] += 1
        
        # Extraire les mots-clés
        keywords = self._extract_keywords(question)
        if grade_level:
            keywords.extend(self._extract_keywords(grade_level))
        
        # Chercher les documents pertinents
        results = []
        for doc in self.documents:
            score = self._score_document(doc, keywords)
            if score > 0:
                results.append({'document': doc, 'score': score})
        
        # Trier et garder les meilleurs
        results.sort(key=lambda x: x['score'], reverse=True)
        top_results = results[:max_docs]
        
        if top_results:
            self.stats["hits"] += 1
        
        return self._build_context(top_results, question)
    
    def _build_context(self, results: List[Dict], question: str) -> Dict:
        """Construit le contexte pour GPT"""
        if not results:
            return {
                'found': False,
                'documents': [],
                'prompt_enhancement': f"Question: {question}\nRéponds de manière pédagogique adaptée au contexte de la RDC."
            }
        
        # Construire les références
        documents_refs = []
        context_parts = []
        
        for result in results:
            doc = result['document']
            
            # Détecter les métadonnées
            doc_text = f"{doc.get('title', '')} {doc.get('file', '')}".lower()
            
            niveau = "Non spécifié"
            if 'primaire' in doc_text:
                niveau = "Primaire"
                for i in range(1, 7):
                    if f'{i}e' in doc_text:
                        niveau = f"{i}e année primaire"
                        break
            elif any(x in doc_text for x in ['7eme', '8eme', 'HS', 'EB']):
                niveau = "Secondaire"
            
            matiere = "Général"
            if 'math' in doc_text:
                matiere = "Mathématiques"
            elif 'lingala' in doc_text:
                matiere = "Lingala"
            elif 'kiswahili' in doc_text:
                matiere = "Kiswahili"
            elif 'ciluba' in doc_text:
                matiere = "Tshiluba"
            elif 'svt' in doc_text:
                matiere = "Sciences"
            elif 'francais' in doc_text or 'français' in doc_text:
                matiere = "Français"
            
            doc_ref = {
                'titre': doc.get('title', 'Document'),
                'niveau': niveau,
                'matiere': matiere,
                'score': round(result['score'], 2)
            }
            documents_refs.append(doc_ref)
            
            context_parts.append(f"📚 {doc_ref['titre']} ({niveau}, {matiere})")
        
        # Construire le prompt enrichi
        context_text = "\n".join(context_parts)
        
        prompt = f"""Tu es un tuteur pédagogique expert du curriculum de la RDC.

📚 DOCUMENTS CONSULTÉS:
{context_text}

❓ QUESTION: {question}

🎯 INSTRUCTIONS:
- Utilise le contexte du programme national MEPST
- Intègre des exemples locaux (Kinshasa, fleuve Congo, marché central)
- Sois pédagogique et encourageant
- Adapte ton langage au niveau scolaire

Réponds de manière claire et culturellement appropriée pour un élève congolais."""
        
        return {
            'found': True,
            'documents': documents_refs,
            'prompt_enhancement': prompt,
            'context': context_text
        }
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques"""
        return {
            **self.stats,
            'documents_loaded': len(self.documents),
            'hit_rate': (self.stats['hits'] / self.stats['queries'] * 100) if self.stats['queries'] > 0 else 0
        }

# Test rapide si exécuté directement
if __name__ == "__main__":
    print("🚀 Test du Connecteur RAG Corrigé\n")
    
    rag = CongoRAGConnector()
    
    # Test 1
    print("Test 1: Mathématiques")
    ctx = rag.query_rag("Comment calculer l'aire d'un rectangle?")
    print(f"Documents trouvés: {len(ctx['documents'])}")
    if ctx['found']:
        for doc in ctx['documents']:
            print(f"  - {doc['titre']} (Score: {doc['score']})")
    
    # Test 2
    print("\nTest 2: Lingala")
    ctx2 = rag.query_rag("Guide lingala 2ème année")
    print(f"Documents trouvés: {len(ctx2['documents'])}")
    
    # Stats
    print(f"\n📊 Stats: {rag.get_stats()}")
    print("\n✅ Connecteur RAG opérationnel!")