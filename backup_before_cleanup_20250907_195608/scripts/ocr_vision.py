# scripts/ocr_vision.py
"""OCR avec GPT-4 Vision - Version améliorée pour manuscrit"""

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VisionOCR:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("[OCR] GPT-4 Vision initialisé (v2)")
    
    def read_image(self, image_path):
        """Lit une image - optimisé pour manuscrit et équations"""
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prompt amélioré pour manuscrit
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Transcris TOUT le texte visible dans cette image.

INSTRUCTIONS:
1. Si c'est manuscrit (écrit à la main), lis attentivement chaque mot
2. Si c'est une équation mathématique, inclus tous les symboles (x, ², +, -, =, etc.)
3. Si c'est une question en français ou lingala, transcris-la complètement
4. Retourne EXACTEMENT ce qui est écrit, même si c'est mal écrit
5. N'ajoute AUCUNE explication

Exemples de ce que tu pourrais voir:
- Équation: "2x² + 3x - 5 = 0"
- Question manuscrite: "C'est qui le président du Congo"
- Calcul: "500/3 et ajouter 30"
- Texte lingala: "Comment diviser"

Transcris maintenant:"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.1  # Plus déterministe
            )
            
            text = response.choices[0].message.content.strip()
            print(f"[VISION] Lu: {text}")
            return text
            
        except Exception as e:
            print(f"[VISION ERROR] {e}")
            return ""

RealOCR = VisionOCR
