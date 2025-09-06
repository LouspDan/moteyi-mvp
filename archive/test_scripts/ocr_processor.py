#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Processor - Extraction de texte des images
MVP Moteyi - Version Tesseract (gratuite)
"""

import pytesseract
from PIL import Image
import os
from pathlib import Path
import json
from datetime import datetime

class OCRProcessor:
    def __init__(self):
        print("[INIT] OCR Processor")
        
        # Configurer Tesseract (Windows)
        # Si Tesseract n'est pas dans PATH, specifier le chemin
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.images_dir = Path("data/received_images")
        self.output_dir = Path("data/ocr_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def process_image(self, image_path):
        """Extrait le texte d'une image"""
        try:
            print(f"\n[OCR] Traitement: {image_path}")
            
            # Ouvrir l'image
            img = Image.open(image_path)
            
            # Configuration OCR pour francais
            custom_config = r'--oem 3 --psm 6'
            
            # Extraction du texte
            text = pytesseract.image_to_string(
                img, 
                lang='fra',  # Francais
                config=custom_config
            )
            
            # Nettoyer le texte
            text = text.strip()
            
            if text:
                print(f"[OK] Texte extrait ({len(text)} caracteres)")
                print("[EXTRAIT] Debut du texte:")
                print("-" * 40)
                print(text[:200])
                print("-" * 40)
            else:
                print("[WARN] Aucun texte detecte")
            
            return text
            
        except Exception as e:
            print(f"[ERREUR] OCR: {e}")
            return None
    
    def process_all_images(self):
        """Traite toutes les images du dossier"""
        print("\n[START] Traitement OCR de toutes les images")
        print("=" * 50)
        
        # Lister les images
        image_files = list(self.images_dir.glob("*.png")) + \
                     list(self.images_dir.glob("*.jpg")) + \
                     list(self.images_dir.glob("*.jpeg"))
        
        if not image_files:
            print("[WARN] Aucune image trouvee dans data/received_images/")
            return []
        
        print(f"[INFO] {len(image_files)} image(s) a traiter")
        
        results = []
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Image: {image_path.name}")
            
            # OCR
            text = self.process_image(image_path)
            
            if text:
                # Sauvegarder le resultat
                result = {
                    'image': str(image_path),
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'char_count': len(text),
                    'word_count': len(text.split())
                }
                results.append(result)
                
                # Sauvegarder dans un fichier texte
                output_file = self.output_dir / f"{image_path.stem}_ocr.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"[SAVE] Texte sauve: {output_file}")
        
        # Sauvegarder tous les resultats en JSON
        summary_file = self.output_dir / "ocr_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[RESULTATS] {len(results)} texte(s) extrait(s)")
        print(f"[SAVE] Resume: {summary_file}")
        
        return results
    
    def analyze_content(self, results):
        """Analyse le contenu extrait pour identifier le type d'exercice"""
        print("\n[ANALYSE] Identification du contenu")
        print("=" * 50)
        
        for result in results:
            text = result['text'].lower()
            
            # Detecter le type de contenu
            content_type = "inconnu"
            
            if any(word in text for word in ['addition', 'soustraction', 'multiplication', 'division', '+', '-', 'x', '÷', '=']):
                content_type = "mathematiques"
            elif any(word in text for word in ['conjugue', 'verbe', 'phrase', 'mot', 'texte', 'dictee']):
                content_type = "francais"
            elif any(word in text for word in ['science', 'nature', 'animal', 'plante', 'corps']):
                content_type = "sciences"
            elif any(word in text for word in ['histoire', 'geographie', 'carte', 'pays']):
                content_type = "histoire-geo"
            
            result['content_type'] = content_type
            
            print(f"\n[IMAGE] {Path(result['image']).name}")
            print(f"  Type detecte: {content_type}")
            print(f"  Mots: {result['word_count']}")
            print(f"  Apercu: {text[:100]}...")
        
        return results

def main():
    # Test OCR sur les images capturees
    processor = OCRProcessor()
    
    # Traiter toutes les images
    results = processor.process_all_images()
    
    if results:
        # Analyser le contenu
        results = processor.analyze_content(results)
        
        print("\n" + "=" * 50)
        print("[SUCCESS] OCR termine avec succes!")
        print(f"[NEXT] Pret pour l'etape RAG + GPT")
        print(f"[DATA] Resultats dans: data/ocr_results/")
    else:
        print("\n[WARN] Aucun texte extrait")
        print("[TIP] Verifiez que les images sont claires")
        print("[TIP] Ou essayez Google Vision API pour plus de precision")

if __name__ == "__main__":
    main()
