# scripts/ocr_real.py
import pytesseract
from PIL import Image
import os
from pathlib import Path

# Configuration Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class RealOCR:
    """
    Le vrai lecteur d'images de Moteyi
    Comme un professeur qui lit attentivement chaque exercice
    """
    
    def __init__(self):
        print("[OCR] Initialisation du lecteur d'images...")
        self.processed_count = 0
        
    def read_image(self, image_path):
        """
        Lit le texte dans une image
        Retourne le texte extrait ou None si erreur
        """
        try:
            # Vérifier que l'image existe
            if not os.path.exists(image_path):
                print(f"[ERREUR] Image non trouvee: {image_path}")
                return None
            
            # Ouvrir l'image
            print(f"[OCR] Lecture de: {image_path}")
            img = Image.open(image_path)
            
            # Extraction du texte
            # lang='fra' pour français (meilleur pour nos exercices)
            text = pytesseract.image_to_string(img, lang='fra')
            
            # Nettoyer le texte
            text = text.strip()
            
            if text:
                self.processed_count += 1
                print(f"[OCR] Texte extrait ({len(text)} caracteres)")
                
                # Afficher un aperçu
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"[APERCU] {preview}")
                
                return text
            else:
                print("[OCR] Aucun texte detecte dans l'image")
                return None
                
        except Exception as e:
            print(f"[ERREUR OCR] {e}")
            return None
    
    def detect_exercise_type(self, text):
        """
        Devine le type d'exercice d'après le texte
        Comme un prof qui reconnaît la matière
        """
        if not text:
            return "inconnu"
        
        text_lower = text.lower()
        
        # Détection par mots-clés
        if any(word in text_lower for word in ['+', '-', '×', '÷', '=', 'calcul', 'addition']):
            return "mathematiques"
        elif any(word in text_lower for word in ['conjugue', 'verbe', 'phrase', 'pluriel']):
            return "francais"
        elif any(word in text_lower for word in ['science', 'corps', 'animal', 'plante']):
            return "sciences"
        else:
            return "general"
    
    def extract_math_problem(self, text):
        """
        Extrait spécifiquement les problèmes de maths
        """
        import re
        
        # Chercher des patterns comme "25 + 17"
        patterns = [
            r'(\d+)\s*\+\s*(\d+)',  # Addition
            r'(\d+)\s*\-\s*(\d+)',  # Soustraction  
            r'(\d+)\s*[×x]\s*(\d+)', # Multiplication
            r'(\d+)\s*[÷/]\s*(\d+)'  # Division
        ]
        
        problems = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                problems.append(match)
        
        return problems

# Fonction de test
def test_real_ocr():
    """Test le vrai OCR sur différentes images"""
    
    print("\n" + "="*50)
    print("TEST OCR REEL")
    print("="*50)
    
    ocr = RealOCR()
    
    # Test 1: Notre image de test
    print("\n[TEST 1] Image de test generee")
    text = ocr.read_image("test_math_big.png")
    if text:
        exercise_type = ocr.detect_exercise_type(text)
        print(f"[TYPE] Exercice de: {exercise_type}")
        
        if exercise_type == "mathematiques":
            problems = ocr.extract_math_problem(text)
            print(f"[PROBLEMES] Trouves: {problems}")
    
    # Test 2: Une vraie capture WhatsApp (si elle existe)
    capture_path = "data/received_images/capture_20250902_013644.png"
    if os.path.exists(capture_path):
        print("\n[TEST 2] Vraie capture WhatsApp")
        text = ocr.read_image(capture_path)
        if text:
            print(f"[TYPE] Detecte: {ocr.detect_exercise_type(text)}")
    
    print(f"\n[STATS] Images traitees: {ocr.processed_count}")

if __name__ == "__main__":
    test_real_ocr()