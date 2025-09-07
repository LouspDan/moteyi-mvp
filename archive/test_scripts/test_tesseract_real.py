# scripts/test_tesseract_real.py
import pytesseract
from PIL import Image

# LIGNE CRUCIALE : Dire à Python où est Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Créer une image de test simple
from PIL import Image, ImageDraw, ImageFont

# Créer une image avec du texte
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)

# Écrire du texte simple
draw.text((10, 30), "25 + 17 = ?", fill='black')
img.save('test_math.png')

# Tester l'OCR
text = pytesseract.image_to_string('test_math.png')
print("Tesseract lit:", text)

if "25" in text and "17" in text:
    print("[SUCCESS] Tesseract fonctionne !")
else:
    print("[ERREUR] Tesseract ne lit pas correctement")