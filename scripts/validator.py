#!/usr/bin/env python3
"""
Validateur pour les documents du RAG seed
Vérifie l'intégrité, la qualité et la conformité des documents
"""

import os
import csv
import hashlib
import PyPDF2
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DocumentValidator:
    def __init__(self, catalog_path, data_dir):
        self.catalog_path = catalog_path
        self.data_dir = data_dir
        self.validation_results = []
        
    def validate_all(self):
        """Valide tous les documents du catalogue"""
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
        
        logging.info(f"🔍 Validation de {len(documents)} documents...")
        
        for doc in documents:
            result = self.validate_document(doc)
            self.validation_results.append(result)
            
        self.generate_report()
    
    def validate_document(self, doc):
        """Valide un document individuel"""
        file_path = os.path.join(self.data_dir, doc['file_path'])
        result = {
            'id': doc['id'],
            'titre': doc['titre'],
            'status': 'OK',
            'issues': []
        }
        
        # 1. Vérifier l'existence du fichier
        if not os.path.exists(file_path):
            result['status'] = 'ERREUR'
            result['issues'].append('Fichier introuvable')
            return result
        
        # 2. Vérifier le checksum
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            if file_hash != doc['checksum']:
                result['issues'].append('Checksum incorrect')
        
        # 3. Vérifier la validité du PDF
        try:
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                num_pages = len(pdf.pages)
                
                # Vérifier le nombre de pages
                if num_pages < 2:
                    result['issues'].append(f'Document trop court ({num_pages} pages)')
                
                # Vérifier l'extractibilité du texte
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                if len(text) < 100:
                    result['issues'].append('Texte non extractible ou insuffisant')
                    
        except Exception as e:
            result['status'] = 'ERREUR'
            result['issues'].append(f'PDF corrompu: {str(e)}')
        
        # 4. Vérifier la taille du fichier
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # En MB
        if file_size > 50:
            result['issues'].append(f'Fichier trop volumineux ({file_size:.1f} MB)')
        elif file_size < 0.1:
            result['issues'].append(f'Fichier trop petit ({file_size:.1f} MB)')
        
        # 5. Vérifier les métadonnées requises
        required_fields = ['titre', 'langue', 'grade_level', 'matiere', 'type_doc']
        for field in required_fields:
            if not doc.get(field):
                result['issues'].append(f'Métadonnée manquante: {field}')
        
        # Déterminer le statut final
        if result['issues']:
            result['status'] = 'ATTENTION' if len(result['issues']) < 3 else 'ERREUR'
            
        return result
    
    def generate_report(self):
        """Génère un rapport de validation"""
        total = len(self.validation_results)
        ok = sum(1 for r in self.validation_results if r['status'] == 'OK')
        attention = sum(1 for r in self.validation_results if r['status'] == 'ATTENTION')
        erreur = sum(1 for r in self.validation_results if r['status'] == 'ERREUR')
        
        print("\n" + "="*60)
        print("📊 RAPPORT DE VALIDATION")
        print("="*60)
        print(f"Total documents: {total}")
        print(f"✅ OK: {ok}")
        print(f"⚠️  Attention: {attention}")
        print(f"❌ Erreur: {erreur}")
        print("="*60)
        
        # Détails des problèmes
        if attention + erreur > 0:
            print("\n🔍 DÉTAILS DES PROBLÈMES:")
            for result in self.validation_results:
                if result['status'] != 'OK':
                    print(f"\n[{result['status']}] {result['titre']}")
                    for issue in result['issues']:
                        print(f"  - {issue}")
        
        # Mise à jour du catalogue avec le statut de validation
        self.update_catalog_validation()
    
    def update_catalog_validation(self):
        """Met à jour le statut de validation dans le catalogue"""
        # Lire le catalogue existant
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
            fieldnames = reader.fieldnames
        
        # Mettre à jour le statut de validation
        for doc in documents:
            for result in self.validation_results:
                if doc['id'] == result['id']:
                    doc['validated'] = 'true' if result['status'] == 'OK' else 'false'
                    if result['issues']:
                        doc['notes'] = f"{doc.get('notes', '')} | Issues: {'; '.join(result['issues'])}"
        
        # Écrire le catalogue mis à jour
        with open(self.catalog_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(documents)
        
        logging.info("✅ Catalogue mis à jour avec les résultats de validation")

if __name__ == "__main__":
    validator = DocumentValidator(
        catalog_path='../data/rag_seed/rag_seed_catalog.csv',
        data_dir='../data/rag_seed'
    )
    validator.validate_all()