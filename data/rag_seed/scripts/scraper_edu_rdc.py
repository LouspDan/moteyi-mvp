#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper pour les programmes scolaires RDC - Version Corrigée
Site source : https://edu-nc.gouv.cd/programmes-scolaires
Organisation optimisée des fichiers par niveau/matière
"""

import os
import sys
import io
import csv
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
import time
import logging
from pathlib import Path
import re

# Fix encodage Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration avec détection automatique des chemins
SCRIPT_DIR = Path(__file__).parent  # scripts/
RAG_SEED_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else Path('.')
OUTPUT_DIR = str(RAG_SEED_DIR)
CATALOG_FILE = str(RAG_SEED_DIR / "rag_seed_catalog.csv")

# URL source
BASE_URL = "https://edu-nc.gouv.cd/programmes-scolaires"
DELAY_BETWEEN_DOWNLOADS = 2  # Secondes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProgrammeScolaireScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (Educational Purpose Bot - Moteyi AI RAG Collector)'
        })
        self.documents = []
        
    def clean_filename(self, url):
        """Nettoie et génère un nom de fichier sûr"""
        filename = os.path.basename(urlparse(url).path)
        
        # Remplacer les caractères problématiques
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.replace(' ', '_')
        
        # Limiter la longueur
        name, ext = os.path.splitext(filename)
        if len(name) > 80:
            name = name[:80]
        
        # S'assurer qu'on a bien l'extension .pdf
        if not ext:
            ext = '.pdf'
        
        return name + ext
        
    def get_page_content(self, url):
        """Récupère le contenu HTML de la page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de {url}: {e}")
            return None
    
    def parse_documents(self, html_content):
        """Parse le HTML pour extraire les liens des documents"""
        soup = BeautifulSoup(html_content, 'html.parser')
        documents = []
        
        # Recherche tous les liens PDF
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                title = link.get_text(strip=True)
                # Nettoyer le titre
                title = title.replace('\n', ' ').replace('\r', '').strip()
                if title:  # Ignorer les liens sans texte
                    doc_info = self.extract_metadata(title, href)
                    documents.append(doc_info)
                
        return documents
    
    def extract_metadata(self, title, url):
        """Extrait les métadonnées du titre et de l'URL"""
        metadata = {
            'titre': title,
            'source_url': url,
            'langue': 'français',  # Par défaut
            'validated': False,
            'grade_level': '',
            'matiere': '',
            'type_doc': 'autre'
        }
        
        title_lower = title.lower()
        
        # === DÉTECTION DE LA LANGUE ===
        if any(word in title_lower for word in ['lingala', 'ln']):
            metadata['langue'] = 'lingala'
        elif any(word in title_lower for word in ['kiswahili', 'swahili', 'sw']):
            metadata['langue'] = 'swahili'
        elif any(word in title_lower for word in ['ciluba', 'tshiluba']):
            metadata['langue'] = 'tshiluba'
        elif any(word in title_lower for word in ['kikongo']):
            metadata['langue'] = 'kikongo'
            
        # === DÉTECTION DU NIVEAU SCOLAIRE ===
        # Primaire (1-6)
        if '1ère' in title or '1ere' in title_lower or '1e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '1ere_annee'
            elif 'hs' in title_lower or 'humanité' in title_lower:
                metadata['grade_level'] = '1ere_HS'
            else:
                metadata['grade_level'] = '1ere_annee'
                
        elif '2ème' in title or '2eme' in title_lower or '2e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '2eme_annee'
            elif 'hs' in title_lower or 'humanité' in title_lower:
                metadata['grade_level'] = '2eme_HS'
            else:
                metadata['grade_level'] = '2eme_annee'
                
        elif '3ème' in title or '3eme' in title_lower or '3e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '3eme_annee'
            elif 'hs' in title_lower or 'humanité' in title_lower:
                metadata['grade_level'] = '3eme_HS'
            elif 'sec' in title_lower:
                metadata['grade_level'] = '1ere_HS'  # 3e Sec = 1ère HS
            else:
                metadata['grade_level'] = '3eme_annee'
                
        elif '4ème' in title or '4eme' in title_lower or '4e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '4eme_annee'
            elif 'hs' in title_lower or 'humanité' in title_lower:
                metadata['grade_level'] = '4eme_HS'
            elif 'sec' in title_lower:
                metadata['grade_level'] = '2eme_HS'  # 4e Sec = 2ème HS
            else:
                metadata['grade_level'] = '4eme_annee'
                
        elif '5ème' in title or '5eme' in title_lower or '5e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '5eme_annee'
            elif 'sec' in title_lower:
                metadata['grade_level'] = '3eme_HS'  # 5e Sec = 3ème HS
            else:
                metadata['grade_level'] = '5eme_annee'
                
        elif '6ème' in title or '6eme' in title_lower or '6e' in title:
            if 'primaire' in title_lower:
                metadata['grade_level'] = '6eme_annee'
            elif 'sec' in title_lower:
                metadata['grade_level'] = '4eme_HS'  # 6e Sec = 4ème HS
            else:
                metadata['grade_level'] = '6eme_annee'
                
        # Cycle terminal EB
        elif '7ème' in title or '7eme' in title_lower or '7e' in title or 'pe7' in title_lower:
            metadata['grade_level'] = '7eme_EB'
        elif '8ème' in title or '8eme' in title_lower or '8e' in title or 'pe8' in title_lower:
            metadata['grade_level'] = '8eme_EB'
            
        # Détection par codes PE (Programme d'Enseignement)
        if 'pe1' in title_lower:
            metadata['grade_level'] = '1ere_annee'
        elif 'pe2' in title_lower:
            metadata['grade_level'] = '2eme_annee'
        elif 'pe3' in title_lower:
            metadata['grade_level'] = '1ere_HS'  # PE3 = 3e Sec = 1ère HS
        elif 'pe4' in title_lower:
            metadata['grade_level'] = '2eme_HS'
        elif 'pe5' in title_lower:
            metadata['grade_level'] = '3eme_HS'
        elif 'pe6' in title_lower:
            metadata['grade_level'] = '4eme_HS'
            
        # === DÉTECTION DE LA MATIÈRE ===
        if 'math' in title_lower:
            metadata['matiere'] = 'mathematiques'
        elif 'svt' in title_lower or 'sciences de la vie' in title_lower:
            metadata['matiere'] = 'SVT'
        elif 'spttic' in title_lower or 'sptic' in title_lower or 'physique' in title_lower:
            metadata['matiere'] = 'SPTTIC'
        elif 'français' in title_lower or 'francais' in title_lower:
            metadata['matiere'] = 'francais'
        elif 'informatique' in title_lower:
            metadata['matiere'] = 'informatique'
        elif 'civique' in title_lower or 'morale' in title_lower:
            metadata['matiere'] = 'education_civique'
        elif 'anglais' in title_lower:
            metadata['matiere'] = 'anglais'
        elif 'histoire' in title_lower:
            metadata['matiere'] = 'histoire'
        elif 'géographie' in title_lower or 'geographie' in title_lower:
            metadata['matiere'] = 'geographie'
            
        # === TYPE DE DOCUMENT ===
        if 'guide' in title_lower:
            metadata['type_doc'] = 'guide'
        elif 'programme' in title_lower or 'pe' in title_lower[:10]:
            metadata['type_doc'] = 'programme'
        elif 'manuel' in title_lower:
            metadata['type_doc'] = 'manuel'
        elif 'cahier' in title_lower:
            metadata['type_doc'] = 'cahier_exercices'
        elif 'livret' in title_lower:
            metadata['type_doc'] = 'livret'
        elif 'curriculum' in title_lower:
            metadata['type_doc'] = 'curriculum'
        elif 'recueil' in title_lower or 'normes' in title_lower:
            metadata['type_doc'] = 'normes'
            
        return metadata
    
    def determine_file_path(self, doc_info):
        """Détermine le chemin de sauvegarde avec organisation optimale"""
        
        grade = doc_info.get('grade_level', '').lower()
        matiere = doc_info.get('matiere', '').lower()
        langue = doc_info.get('langue', '').lower()
        type_doc = doc_info.get('type_doc', '').lower()
        titre = doc_info.get('titre', '').lower()
        
        # Générer un nom de fichier propre
        filename = self.clean_filename(doc_info['source_url'])
        
        # === LANGUES NATIONALES ===
        if langue in ['lingala', 'swahili', 'kikongo', 'tshiluba']:
            if any(x in grade for x in ['1ere', '2eme', '3eme', '4eme', '5eme', '6eme']) and 'hs' not in grade and 'eb' not in grade:
                return os.path.join('langues_nationales', langue, 'primaire', filename)
            elif any(x in grade for x in ['7eme_eb', '8eme_eb', 'hs']):
                return os.path.join('langues_nationales', langue, 'secondaire', filename)
            else:
                return os.path.join('langues_nationales', langue, filename)
        
        # === PRIMAIRE (1-6) ===
        primaire_grades = ['1ere_annee', '2eme_annee', '3eme_annee', '4eme_annee', '5eme_annee', '6eme_annee']
        for niveau in primaire_grades:
            if niveau in grade:
                if matiere == 'mathematiques':
                    return os.path.join('primaire', niveau, 'maths', filename)
                elif matiere == 'francais':
                    return os.path.join('primaire', niveau, 'francais', filename)
                elif matiere in ['svt', 'spttic']:
                    return os.path.join('primaire', niveau, 'sciences', filename)
                elif matiere == 'education_civique':
                    return os.path.join('primaire', niveau, 'education_civique', filename)
                else:
                    return os.path.join('primaire', niveau, 'autres', filename)
        
        # === SECONDAIRE - CYCLE TERMINAL EB (7-8) ===
        if '7eme_eb' in grade:
            if matiere == 'mathematiques':
                return os.path.join('secondaire', '7eme_EB', 'maths', filename)
            elif matiere == 'svt':
                return os.path.join('secondaire', '7eme_EB', 'svt', filename)
            elif matiere == 'spttic':
                return os.path.join('secondaire', '7eme_EB', 'spttic', filename)
            elif matiere == 'francais':
                return os.path.join('secondaire', '7eme_EB', 'francais', filename)
            else:
                return os.path.join('secondaire', '7eme_EB', 'autres', filename)
        
        elif '8eme_eb' in grade:
            if matiere == 'mathematiques':
                return os.path.join('secondaire', '8eme_EB', 'maths', filename)
            elif matiere == 'svt':
                return os.path.join('secondaire', '8eme_EB', 'svt', filename)
            elif matiere == 'spttic':
                return os.path.join('secondaire', '8eme_EB', 'spttic', filename)
            elif matiere == 'francais':
                return os.path.join('secondaire', '8eme_EB', 'francais', filename)
            else:
                return os.path.join('secondaire', '8eme_EB', 'autres', filename)
        
        # === HUMANITÉS SCIENTIFIQUES (1-4 HS) ===
        humanites = ['1ere_hs', '2eme_hs', '3eme_hs', '4eme_hs']
        for niveau_hs in humanites:
            if niveau_hs in grade:
                niveau_folder = niveau_hs.upper().replace('_', '_')  # Format propre
                if matiere == 'mathematiques':
                    return os.path.join('secondaire', niveau_folder, 'maths', filename)
                elif matiere == 'svt':
                    return os.path.join('secondaire', niveau_folder, 'svt', filename)
                elif matiere == 'spttic':
                    return os.path.join('secondaire', niveau_folder, 'spttic', filename)
                elif matiere == 'francais':
                    return os.path.join('secondaire', niveau_folder, 'francais', filename)
                else:
                    return os.path.join('secondaire', niveau_folder, 'autres', filename)
        
        # === GUIDES PÉDAGOGIQUES ===
        if 'guide' in type_doc:
            if 'educateur' in titre or 'enseignant' in titre:
                return os.path.join('guides_pedagogiques', 'enseignants', filename)
            else:
                return os.path.join('guides_pedagogiques', filename)
        
        # === EXAMENS ===
        if 'enafep' in titre:
            return os.path.join('examens', 'ENAFEP', filename)
        elif 'exetat' in titre:
            return os.path.join('examens', 'EXETAT', filename)
        elif 'examen' in titre or 'evaluation' in titre:
            return os.path.join('examens', 'autres', filename)
        
        # === DOCUMENTS ADMINISTRATIFS ===
        if any(x in titre for x in ['normes', 'curriculum', 'arrete', 'politique', 'recueil', 'circulaire']):
            return os.path.join('autres', 'administration', filename)
        
        # === INFORMATIQUE ===
        if matiere == 'informatique':
            if any(x in titre for x in ['primaire', 'eb', '1ere', '2eme', '3eme', '4eme', '5eme', '6eme']):
                return os.path.join('autres', 'informatique', 'primaire', filename)
            elif any(x in titre for x in ['secondaire', 'hs', 'humanité']):
                return os.path.join('autres', 'informatique', 'secondaire', filename)
            else:
                return os.path.join('autres', 'informatique', filename)
        
        # === DÉFAUT ===
        logging.warning(f"Pas de classification trouvée pour: {doc_info.get('titre', 'Unknown')[:50]}")
        return os.path.join('autres', 'divers', filename)
    
    def download_document(self, doc_info, doc_id):
        """Télécharge un document PDF"""
        url = doc_info['source_url']
        
        # S'assurer que l'URL est complète
        if not url.startswith('http'):
            url = urljoin(BASE_URL, url)
        
        # Déterminer le chemin de sauvegarde
        file_path = self.determine_file_path(doc_info)
        full_path = os.path.join(OUTPUT_DIR, file_path)
        
        # Créer les répertoires si nécessaire
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            logging.info(f"[{doc_id:03d}] Téléchargement: {doc_info['titre'][:50]}...")
            logging.info(f"      → Destination: {file_path}")
            
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Sauvegarder le fichier
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Calculer le checksum
            with open(full_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            
            # Mettre à jour les métadonnées
            doc_info.update({
                'id': f"{doc_id:03d}",
                'file_path': file_path.replace('\\', '/'),  # Unix style paths
                'checksum': checksum,
                'licence': 'MEPSP',
                'ingested': datetime.now().strftime('%Y-%m-%d'),
                'validated': 'false',  # String pour CSV
                'notes': 'Document officiel - Collecte automatique'
            })
            
            logging.info(f"      ✓ OK - {os.path.getsize(full_path)/1024:.1f} KB")
            time.sleep(DELAY_BETWEEN_DOWNLOADS)
            return True
            
        except Exception as e:
            logging.error(f"[{doc_id:03d}] ✗ ERREUR: {str(e)[:100]}")
            doc_info['validated'] = 'false'
            doc_info['notes'] = f"Erreur téléchargement: {str(e)[:100]}"
            return False
    
    def save_catalog(self):
        """Sauvegarde le catalogue CSV"""
        fieldnames = ['id', 'titre', 'source_url', 'langue', 'grade_level', 
                     'matiere', 'type_doc', 'file_path', 'checksum', 
                     'licence', 'ingested', 'validated', 'notes']
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(CATALOG_FILE) or '.', exist_ok=True)
        
        with open(CATALOG_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for doc in self.documents:
                # Assurer que tous les champs sont présents
                row = {field: doc.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        logging.info(f"[CATALOG] Sauvegardé: {len(self.documents)} documents → {CATALOG_FILE}")
    
    def print_statistics(self):
        """Affiche des statistiques sur les documents collectés"""
        print("\n" + "="*60)
        print("STATISTIQUES DE COLLECTE")
        print("="*60)
        
        # Compter par niveau
        niveaux = {}
        matieres = {}
        langues = {}
        types = {}
        
        for doc in self.documents:
            niveau = doc.get('grade_level', 'non_classé')
            matiere = doc.get('matiere', 'non_classé')
            langue = doc.get('langue', 'non_classé')
            type_doc = doc.get('type_doc', 'non_classé')
            
            niveaux[niveau] = niveaux.get(niveau, 0) + 1
            matieres[matiere] = matieres.get(matiere, 0) + 1
            langues[langue] = langues.get(langue, 0) + 1
            types[type_doc] = types.get(type_doc, 0) + 1
        
        print("\nPAR NIVEAU:")
        for k, v in sorted(niveaux.items()):
            print(f"  {k:20s} : {v:3d} documents")
        
        print("\nPAR MATIÈRE:")
        for k, v in sorted(matieres.items()):
            print(f"  {k:20s} : {v:3d} documents")
        
        print("\nPAR LANGUE:")
        for k, v in sorted(langues.items()):
            print(f"  {k:20s} : {v:3d} documents")
        
        print("\nPAR TYPE:")
        for k, v in sorted(types.items()):
            print(f"  {k:20s} : {v:3d} documents")
        print("="*60)
    
    def run(self):
        """Lance le processus complet de scraping"""
        logging.info("[START] Démarrage du scraper...")
        logging.info(f"[CONFIG] Output: {OUTPUT_DIR}")
        logging.info(f"[CONFIG] Catalog: {CATALOG_FILE}")
        
        # Récupérer la page principale
        html_content = self.get_page_content(BASE_URL)
        if not html_content:
            logging.error("Impossible de récupérer la page principale")
            return
        
        # Parser les documents
        documents = self.parse_documents(html_content)
        logging.info(f"[DOCS] {len(documents)} documents trouvés")
        
        # Limiter pour les tests (optionnel)
        # documents = documents[:10]  # Décommenter pour tester avec seulement 10 documents
        
        # Télécharger chaque document
        success_count = 0
        for i, doc in enumerate(documents, 1):
            print(f"\n[{i}/{len(documents)}] {'='*40}")
            if self.download_document(doc, i):
                self.documents.append(doc)
                success_count += 1
            else:
                # Ajouter quand même au catalogue avec statut d'erreur
                doc.update({
                    'id': f"{i:03d}",
                    'file_path': '',
                    'checksum': '',
                    'licence': 'MEPSP',
                    'ingested': datetime.now().strftime('%Y-%m-%d'),
                    'validated': 'false',
                    'notes': doc.get('notes', 'Erreur téléchargement')
                })
                self.documents.append(doc)
        
        # Sauvegarder le catalogue
        self.save_catalog()
        
        # Afficher les statistiques
        self.print_statistics()
        
        # Résumé
        print("\n" + "="*60)
        print("COLLECTE TERMINÉE!")
        print(f"Documents trouvés    : {len(documents)}")
        print(f"Documents téléchargés: {success_count}")
        print(f"Erreurs              : {len(documents) - success_count}")
        print(f"Catalogue sauvegardé : {CATALOG_FILE}")
        print("="*60)

if __name__ == "__main__":
    # Vérifier qu'on est dans le bon répertoire
    current_dir = os.getcwd()
    script_name = os.path.basename(__file__)
    
    print(f"[INFO] Exécution depuis: {current_dir}")
    print(f"[INFO] Script: {script_name}")
    
    # Lancer le scraper
    scraper = ProgrammeScolaireScraper()
    scraper.run()