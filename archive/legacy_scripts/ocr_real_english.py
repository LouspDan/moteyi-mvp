# scripts/ocr_real_english.py
import pytesseract
from PIL import Image
import os

# Configuration Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class RealOCR:
    def __init__(self):
        print("[OCR] Initialisation (mode anglais)...")
        self.processed_count = 0
        
    def read_image(self, image_path):
        try:
            if not os.path.exists(image_path):
                print(f"[ERREUR] Image non trouvee: {image_path}")
                return None
            
            print(f"[OCR] Lecture de: {image_path}")
            img = Image.open(image_path)
            
            # CHANGEMENT ICI : pas de lang='fra', utilise l'anglais par défaut
            text = pytesseract.image_to_string(img)  # Sans lang='fra'
            
            text = text.strip()
            
            if text:
                self.processed_count += 1
                print(f"[OCR] Texte extrait ({len(text)} caracteres)")
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"[APERCU] {preview}")
                return text
            else:
                print("[OCR] Aucun texte detecte")
                return None
                
        except Exception as e:
            print(f"[ERREUR OCR] {e}")
            return None
    
    def detect_exercise_type(self, text):
        if not text:
            return "inconnu"
        
        text_lower = text.lower()
        
        # Détection par symboles mathématiques (universels)
        if any(char in text for char in ['+', '-', '×', 'x', '÷', '/', '=']):
            return "mathematiques"
        elif any(word in text_lower for word in ['conjugue', 'verbe', 'phrase']):
            return "francais"
        else:
            return "general"

# Test
def test_ocr_english():
    print("\n" + "="*50)
    print("TEST OCR (Mode Anglais)")
    print("="*50)
    
    ocr = RealOCR()
    
    # Test sur notre image
    print("\n[TEST] Image mathematique")
    text = ocr.read_image("test_math_big.png")
    if text:
        print(f"[TYPE] Exercice: {ocr.detect_exercise_type(text)}")
    
    print(f"\n[STATS] Images traitees: {ocr.processed_count}")
    print("\n[INFO] L'anglais fonctionne pour les chiffres et symboles")
    print("[INFO] Suffisant pour la demo!")

if __name__ == "__main__":
    test_ocr_english()