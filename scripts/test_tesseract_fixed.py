# scripts/test_tesseract_fixed.py
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

# IMPORTANT : Chemin vers Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print("=== TEST TESSERACT ===")
print("Creation d'une image de test...")

# Créer une image PLUS GRANDE avec MEILLEUR CONTRASTE
img = Image.new('RGB', (800, 200), color='white')  # Plus grande !
draw = ImageDraw.Draw(img)

# Essayer d'utiliser une police plus grande
try:
    # Windows a Arial
    font = ImageFont.truetype("arial.ttf", 60)  # Grande police
except:
    # Si pas de police, utiliser la défaut mais...
    font = ImageFont.load_default()
    print("[WARN] Police par defaut utilisee (petite)")

# Écrire du texte GROS et NOIR
text_test = "25 + 17 = 42"

# Méthode 1 : avec la police
draw.text((50, 50), text_test, fill='black', font=font)

# Sauvegarder
img.save('test_math_big.png')
print(f"Image creee: test_math_big.png")

# Tester l'OCR
print("\nTest OCR...")
text = pytesseract.image_to_string('test_math_big.png')
print(f"Texte lu par Tesseract: [{text.strip()}]")

if "25" in text and "17" in text:
    print("\n[SUCCESS] Tesseract fonctionne !")
else:
    print("\n[PROBLEME] Tesseract ne lit toujours pas")
    print("Essayons une autre methode...")