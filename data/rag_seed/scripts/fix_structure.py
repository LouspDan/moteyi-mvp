#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction de la structure des dossiers
Corrige la double imbrication et réorganise les PDFs
"""

import os
import shutil
import csv
from pathlib import Path
import hashlib
from datetime import datetime
import re

class StructureFixer:
    def __init__(self):
        # Déterminer les chemins de base
        self.script_dir = Path(__file__).parent
        
        # Le script est dans data/rag_seed/scripts/
        if self.script_dir.name == 'scripts':
            self.rag_seed_dir = self.script_dir.parent
        else:
            # Si lancé depuis ailleurs
            self.rag_seed_dir = Path('.')
            
        self.catalog_file = self.rag_seed_dir / "rag_seed_catalog.csv"
        self.documents_moved = []
        self.stats = {
            'total_files': 0,
            'moved_files': 0,
            'errors': 0,
            'by_category': {}
        }
        
    def find_pdf_files(self):
        """Trouve tous les fichiers PDF peu importe où ils sont"""
        pdf_files = []
        
        # Chercher dans toute l'arborescence
        for root, dirs, files in os.walk(self.rag_seed_dir):
            # Ignorer le dossier scripts
            if 'scripts' in root:
                continue
                
            for file in files:
                if file.endswith('.pdf'):
                    full_path = Path(root) / file
                    pdf_files.append(full_path)
                    print(f"📄 Trouvé: {full_path.relative_to(self.rag_seed_dir)}")
        
        self.stats['total_files'] = len(pdf_files)
        print(f"\n📊 Total: {len(pdf_files)} fichiers PDF trouvés")
        return pdf_files
    
    def extract_metadata_from_filename(self, filename):
        """Extrait les métadonnées du nom de fichier"""
        metadata = {
            'titre': filename,
            'langue': 'français',
            'grade_level': '',
            'matiere': '',
            'type_doc': 'autre'
        }
        
        filename_lower = filename.lower()
        
        # === LANGUE ===
        if any(word in filename_lower for word in ['lingala', 'ln']):
            metadata['langue'] = 'lingala'
        elif any(word in filename_lower for word in ['kiswahili', 'swahili']):
            metadata['langue'] = 'swahili'
        elif any(word in filename_lower for word in ['ciluba', 'tshiluba']):
            metadata['langue'] = 'tshiluba'
        elif any(word in filename_lower for word in ['kikongo']):
            metadata['langue'] = 'kikongo'
            
        # === NIVEAU - Détection par patterns ===
        # Années primaires
        if '1e-annee' in filename_lower or '1e_annee' in filename_lower:
            metadata['grade_level'] = '1ere_annee'
        elif '2e-annee' in filename_lower or '2e_annee' in filename_lower:
            metadata['grade_level'] = '2eme_annee'
        elif '3e-annee' in filename_lower or '3e_annee' in filename_lower:
            metadata['grade_level'] = '3eme_annee'
        elif '4e-annee' in filename_lower:
            metadata['grade_level'] = '4eme_annee'
        elif '5e-annee' in filename_lower:
            metadata['grade_level'] = '5eme_annee'
        elif '6e-annee' in filename_lower:
            metadata['grade_level'] = '6eme_annee'
            
        # CRS (Cours de Récupération Scolaire)
        elif 'crs-n1' in filename_lower or 'crs_n1' in filename_lower:
            metadata['grade_level'] = 'CRS_N1'
        elif 'crs-n2' in filename_lower or 'crs_n2' in filename_lower:
            metadata['grade_level'] = 'CRS_N2'
            
        # Cycle terminal PE7/PE8
        elif 'pe7' in filename_lower or 'guide-pe7' in filename_lower:
            metadata['grade_level'] = '7eme_EB'
        elif 'pe8' in filename_lower or 'guide-pe8' in filename_lower:
            metadata['grade_level'] = '8eme_EB'
            
        # Humanités (PE3-PE6 ou détection directe)
        elif 'pe3' in filename_lower or '3e-sec' in filename_lower or '1-hs' in filename_lower:
            metadata['grade_level'] = '1ere_HS'
        elif 'pe4' in filename_lower or '4e-sec' in filename_lower or '2-hs' in filename_lower:
            metadata['grade_level'] = '2eme_HS'
        elif 'pe5' in filename_lower or '5e-sec' in filename_lower or '3-hs' in filename_lower:
            metadata['grade_level'] = '3eme_HS'
        elif 'pe6' in filename_lower or '6e-sec' in filename_lower or '4-hs' in filename_lower:
            metadata['grade_level'] = '4eme_HS'
            
        # === MATIÈRE ===
        if 'math' in filename_lower:
            metadata['matiere'] = 'maths'
        elif 'svt' in filename_lower:
            metadata['matiere'] = 'svt'
        elif 'spttic' in filename_lower or 'sptic' in filename_lower:
            metadata['matiere'] = 'spttic'
        elif 'francais' in filename_lower or 'français' in filename_lower:
            metadata['matiere'] = 'francais'
        elif 'informatique' in filename_lower:
            metadata['matiere'] = 'informatique'
        elif 'civique' in filename_lower or 'morale' in filename_lower:
            metadata['matiere'] = 'education_civique'
        elif 'histoire' in filename_lower:
            metadata['matiere'] = 'histoire'
        elif 'geographie' in filename_lower or 'géographie' in filename_lower:
            metadata['matiere'] = 'geographie'
        elif 'electricite' in filename_lower or 'électricité' in filename_lower:
            metadata['matiere'] = 'electricite'
        elif 'electronique' in filename_lower or 'électronique' in filename_lower:
            metadata['matiere'] = 'electronique'
        elif 'petrochimie' in filename_lower or 'pétrochimie' in filename_lower:
            metadata['matiere'] = 'petrochimie'
        elif 'psychopedagogie' in filename_lower or 'psychopédagogie' in filename_lower:
            metadata['matiere'] = 'psychopedagogie'
            
        # === TYPE DE DOCUMENT ===
        if 'guide' in filename_lower:
            metadata['type_doc'] = 'guide'
        elif 'cahier' in filename_lower:
            metadata['type_doc'] = 'cahier'
        elif 'manuel' in filename_lower:
            metadata['type_doc'] = 'manuel'
        elif 'livret' in filename_lower:
            metadata['type_doc'] = 'livret'
        elif 'programme' in filename_lower:
            metadata['type_doc'] = 'programme'
        elif 'curriculum' in filename_lower:
            metadata['type_doc'] = 'curriculum'
        elif 'politique' in filename_lower or 'normes' in filename_lower or 'arrete' in filename_lower:
            metadata['type_doc'] = 'administratif'
        elif 'ifadem' in filename_lower:
            metadata['type_doc'] = 'formation'
        elif 'alphabetisation' in filename_lower:
            metadata['type_doc'] = 'alphabetisation'
            
        return metadata
    
    def determine_target_path(self, pdf_file):
        """Détermine le chemin cible basé sur le nom du fichier"""
        filename = pdf_file.name
        metadata = self.extract_metadata_from_filename(filename)
        
        langue = metadata['langue']
        grade = metadata['grade_level']
        matiere = metadata['matiere']
        type_doc = metadata['type_doc']
        
        # === LANGUES NATIONALES ===
        if langue in ['lingala', 'swahili', 'tshiluba', 'kikongo']:
            if grade in ['1ere_annee', '2eme_annee', '3eme_annee']:
                return f'primaire/langues_nationales/{langue}/{filename}'
            elif grade in ['CRS_N1', 'CRS_N2']:
                return f'autres/CRS/{langue}/{filename}'
            elif type_doc == 'alphabetisation':
                return f'autres/alphabetisation/{langue}/{filename}'
            else:
                return f'secondaire/langues_nationales/{langue}/{filename}'
        
        # === PRIMAIRE (1-6) ===
        primaire_grades = ['1ere_annee', '2eme_annee', '3eme_annee', 
                          '4eme_annee', '5eme_annee', '6eme_annee']
        if grade in primaire_grades:
            if matiere == 'maths':
                return f'primaire/{matiere}/{filename}'
            elif matiere == 'francais':
                return f'primaire/{matiere}/{filename}'
            elif matiere in ['svt', 'spttic']:
                return f'primaire/sciences/{filename}'
            elif matiere == 'education_civique':
                return f'primaire/education_civique/{filename}'
            else:
                return f'primaire/autres/{filename}'
        
        # === SECONDAIRE - CYCLE TERMINAL (7-8 EB) ===
        if grade == '7eme_EB':
            if matiere == 'maths':
                return f'secondaire/7eme_EB/maths/{filename}'
            elif matiere == 'svt':
                return f'secondaire/7eme_EB/svt/{filename}'
            elif matiere == 'spttic':
                return f'secondaire/7eme_EB/spttic/{filename}'
            else:
                return f'secondaire/7eme_EB/autres/{filename}'
                
        elif grade == '8eme_EB':
            if matiere == 'maths':
                return f'secondaire/8eme_EB/maths/{filename}'
            elif matiere == 'svt':
                return f'secondaire/8eme_EB/svt/{filename}'
            elif matiere == 'spttic':
                return f'secondaire/8eme_EB/spttic/{filename}'
            else:
                return f'secondaire/8eme_EB/autres/{filename}'
        
        # === HUMANITÉS (1-4 HS) ===
        humanites = ['1ere_HS', '2eme_HS', '3eme_HS', '4eme_HS']
        if grade in humanites:
            if matiere == 'maths':
                return f'secondaire/{grade}/maths/{filename}'
            elif matiere == 'svt':
                return f'secondaire/{grade}/svt/{filename}'
            elif matiere == 'spttic':
                return f'secondaire/{grade}/spttic/{filename}'
            else:
                return f'secondaire/{grade}/autres/{filename}'
        
        # === GUIDES ET FORMATION ===
        if type_doc == 'guide':
            return f'guides_pedagogiques/{filename}'
        elif type_doc == 'formation' or 'ifadem' in filename.lower():
            return f'guides_pedagogiques/formation/{filename}'
        
        # === DOCUMENTS ADMINISTRATIFS ===
        if type_doc == 'administratif':
            return f'autres/administration/{filename}'
        
        # === INFORMATIQUE ===
        if matiere == 'informatique':
            if 'primaire' in filename.lower():
                return f'autres/informatique/primaire/{filename}'
            elif 'secondaire' in filename.lower():
                return f'autres/informatique/secondaire/{filename}'
            else:
                return f'autres/informatique/{filename}'
        
        # === ÉDUCATION CIVIQUE ===
        if matiere == 'education_civique':
            if 'primaire' in filename.lower():
                return f'autres/education_civique/primaire/{filename}'
            elif 'secondaire' in filename.lower():
                return f'autres/education_civique/secondaire/{filename}'
            else:
                return f'autres/education_civique/{filename}'
        
        # === MATIÈRES TECHNIQUES ===
        if matiere in ['electricite', 'electronique', 'petrochimie']:
            return f'autres/techniques/{matiere}/{filename}'
        
        # === PSYCHOPÉDAGOGIE ===
        if matiere == 'psychopedagogie':
            return f'guides_pedagogiques/psychopedagogie/{filename}'
        
        # === AUTRES MATIÈRES ===
        if matiere in ['histoire', 'geographie']:
            return f'autres/{matiere}/{filename}'
        
        # === CRS (Cours de Récupération) ===
        if 'CRS' in grade:
            return f'autres/CRS/{filename}'
        
        # === DÉFAUT ===
        return f'autres/divers/{filename}'
    
    def move_file(self, source_path, target_path):
        """Déplace un fichier vers sa destination correcte"""
        try:
            # Créer le dossier cible si nécessaire
            target_dir = target_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Déplacer le fichier
            shutil.move(str(source_path), str(target_path))
            
            # Calculer le checksum
            with open(target_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            
            # Enregistrer le déplacement
            self.documents_moved.append({
                'source': str(source_path.relative_to(self.rag_seed_dir)),
                'target': str(target_path.relative_to(self.rag_seed_dir)),
                'checksum': checksum,
                'filename': target_path.name
            })
            
            self.stats['moved_files'] += 1
            
            # Statistiques par catégorie
            category = str(target_path.relative_to(self.rag_seed_dir)).split('/')[0]
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
            
            print(f"✅ Déplacé: {source_path.name}")
            print(f"   → {target_path.relative_to(self.rag_seed_dir)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du déplacement: {e}")
            self.stats['errors'] += 1
            return False
    
    def fix_double_nesting(self):
        """Corrige spécifiquement la double imbrication data/rag_seed/data/rag_seed"""
        print("\n🔍 Recherche de double imbrication...")
        
        # Chercher le dossier imbriqué problématique
        nested_path = self.rag_seed_dir / "data" / "rag_seed"
        
        if nested_path.exists():
            print(f"⚠️  Double imbrication détectée: {nested_path}")
            print("🔄 Correction en cours...")
            
            # Déplacer tout le contenu vers la racine rag_seed
            for item in nested_path.iterdir():
                source = item
                target = self.rag_seed_dir / item.name
                
                try:
                    if target.exists():
                        if item.is_dir():
                            # Fusionner les dossiers
                            print(f"   📁 Fusion: {item.name}/")
                            self.merge_directories(source, target)
                        else:
                            # Renommer le fichier existant
                            print(f"   📄 Conflit: {item.name}")
                            new_name = f"merged_{item.name}"
                            shutil.move(str(source), str(self.rag_seed_dir / new_name))
                    else:
                        # Déplacer directement
                        print(f"   ➡️  Déplacement: {item.name}")
                        shutil.move(str(source), str(target))
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
            
            # Supprimer la structure imbriquée vide
            try:
                shutil.rmtree(self.rag_seed_dir / "data")
                print("✅ Structure imbriquée supprimée")
            except Exception as e:
                print(f"⚠️  Impossible de supprimer data/: {e}")
        else:
            print("✅ Pas de double imbrication détectée")
    
    def merge_directories(self, source_dir, target_dir):
        """Fusionne deux dossiers récursivement"""
        for item in source_dir.iterdir():
            source = item
            target = target_dir / item.name
            
            if source.is_dir():
                if not target.exists():
                    target.mkdir(parents=True)
                self.merge_directories(source, target)
            else:
                if target.exists():
                    # Garder les deux avec un nouveau nom pour la source
                    new_target = target_dir / f"merged_{item.name}"
                    shutil.move(str(source), str(new_target))
                else:
                    shutil.move(str(source), str(target))
    
    def fix_structure(self):
        """Corrige la structure complète"""
        print("\n" + "="*60)
        print("CORRECTION DE LA STRUCTURE DES DOSSIERS")
        print("="*60)
        
        # 0. IMPORTANT: Corriger d'abord la double imbrication
        self.fix_double_nesting()
        
        # 1. Trouver tous les PDFs
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            print("❌ Aucun fichier PDF trouvé")
            return
        
        print(f"\n🔄 Réorganisation de {len(pdf_files)} fichiers...")
        print("-"*60)
        
        # 2. Traiter chaque fichier
        for pdf_path in pdf_files:
            # Déterminer le chemin cible
            target_relative = self.determine_target_path(pdf_path)
            target_path = self.rag_seed_dir / target_relative
            
            # Ne déplacer que si nécessaire
            if pdf_path != target_path:
                self.move_file(pdf_path, target_path)
            else:
                print(f"✓ Déjà au bon endroit: {pdf_path.name}")
        
        # 3. Nettoyer les dossiers vides
        self.cleanup_empty_dirs()
        
        # 4. Mettre à jour le catalogue CSV
        self.update_catalog()
        
        # 5. Afficher les statistiques
        self.print_statistics()
    
    def cleanup_empty_dirs(self):
        """Supprime agressivement TOUS les dossiers vides"""
        print("\n🧹 Nettoyage complet des dossiers vides...")
        
        # Liste pour stocker les dossiers à supprimer
        dirs_to_delete = []
        
        # D'abord, identifier tous les dossiers vides
        for root, dirs, files in os.walk(self.rag_seed_dir, topdown=False):
            # Ignorer le dossier scripts
            if 'scripts' in str(root):
                continue
            
            # Chemin relatif pour l'affichage
            rel_path = Path(root).relative_to(self.rag_seed_dir)
            
            # Si c'est un dossier vide ou ne contient que des dossiers vides
            if not files:
                # Vérifier si tous les sous-dossiers sont dans la liste de suppression
                subdirs_empty = all(
                    Path(root) / d in dirs_to_delete 
                    for d in dirs
                )
                
                if not dirs or subdirs_empty:
                    dirs_to_delete.append(Path(root))
        
        # Supprimer les dossiers vides (du plus profond au moins profond)
        dirs_to_delete.sort(key=lambda x: len(x.parts), reverse=True)
        
        for dir_path in dirs_to_delete:
            try:
                # Ne pas supprimer la racine rag_seed
                if dir_path == self.rag_seed_dir:
                    continue
                    
                dir_path.rmdir()
                rel_path = dir_path.relative_to(self.rag_seed_dir)
                print(f"   🗑️  Supprimé: {rel_path}")
            except OSError:
                # Le dossier n'est peut-être plus vide ou n'existe plus
                pass
        
        # Nettoyage spécial pour le dossier data/ s'il existe encore
        data_dir = self.rag_seed_dir / "data"
        if data_dir.exists():
            try:
                # Vérifier s'il est vraiment vide
                if not any(data_dir.iterdir()):
                    data_dir.rmdir()
                    print(f"   🗑️  Supprimé: data/")
                else:
                    # Forcer la suppression si ne contient que des dossiers vides
                    remaining_items = list(data_dir.iterdir())
                    if all(item.is_dir() and not any(item.iterdir()) for item in remaining_items):
                        shutil.rmtree(data_dir)
                        print(f"   🗑️  Supprimé (forcé): data/")
            except Exception as e:
                print(f"   ⚠️  Impossible de supprimer data/: {e}")
    
    def update_catalog(self):
        """Met à jour le catalogue CSV avec les nouveaux chemins"""
        print("\n📝 Mise à jour du catalogue CSV...")
        
        fieldnames = ['id', 'titre', 'source_url', 'langue', 'grade_level', 
                     'matiere', 'type_doc', 'file_path', 'checksum', 
                     'licence', 'ingested', 'validated', 'notes']
        
        rows = []
        
        # Créer les entrées du catalogue
        for i, doc in enumerate(self.documents_moved, 1):
            metadata = self.extract_metadata_from_filename(doc['filename'])
            
            row = {
                'id': f"{i:03d}",
                'titre': doc['filename'].replace('.pdf', '').replace('_', ' ').replace('-', ' '),
                'source_url': 'https://edu-nc.gouv.cd/programmes-scolaires',
                'langue': metadata['langue'],
                'grade_level': metadata['grade_level'],
                'matiere': metadata['matiere'],
                'type_doc': metadata['type_doc'],
                'file_path': doc['target'],
                'checksum': doc['checksum'],
                'licence': 'MEPSP',
                'ingested': datetime.now().strftime('%Y-%m-%d'),
                'validated': 'true',
                'notes': 'Réorganisé par fix_structure.py'
            }
            rows.append(row)
        
        # Écrire le nouveau catalogue
        if rows:
            with open(self.catalog_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"✅ Catalogue mis à jour: {len(rows)} entrées")
        else:
            print("⚠️ Aucun document à cataloguer")
    
    def print_statistics(self):
        """Affiche les statistiques finales"""
        print("\n" + "="*60)
        print("STATISTIQUES DE RÉORGANISATION")
        print("="*60)
        print(f"📊 Total fichiers trouvés : {self.stats['total_files']}")
        print(f"✅ Fichiers déplacés      : {self.stats['moved_files']}")
        print(f"❌ Erreurs               : {self.stats['errors']}")
        
        if self.stats['by_category']:
            print("\n📂 Répartition par catégorie:")
            for category, count in sorted(self.stats['by_category'].items()):
                print(f"   {category:20s} : {count:3d} fichiers")
        
        print("\n📁 Structure finale:")
        self.print_tree()
        print("="*60)
    
    def print_tree(self):
        """Affiche l'arborescence finale"""
        print("data/rag_seed/")
        
        # Liste des dossiers principaux à afficher
        main_dirs = ['primaire', 'secondaire', 'guides_pedagogiques', 'autres']
        
        for main_dir in main_dirs:
            dir_path = self.rag_seed_dir / main_dir
            if dir_path.exists():
                print(f"├── {main_dir}/")
                
                # Afficher les sous-dossiers (niveau 1 seulement)
                subdirs = sorted([d for d in dir_path.iterdir() if d.is_dir()])
                for i, subdir in enumerate(subdirs[:5]):  # Limiter l'affichage
                    is_last = i == len(subdirs) - 1
                    prefix = "└──" if is_last else "├──"
                    print(f"│   {prefix} {subdir.name}/")
                
                if len(subdirs) > 5:
                    print(f"│   └── ... ({len(subdirs)-5} autres dossiers)")

def main():
    """Point d'entrée principal"""
    print("\n🔧 SCRIPT DE CORRECTION DE STRUCTURE")
    print("Version 2.0 - Détection automatique")
    
    fixer = StructureFixer()
    fixer.fix_structure()
    
    print("\n✨ Terminé! Structure corrigée avec succès.")

if __name__ == "__main__":
    main()