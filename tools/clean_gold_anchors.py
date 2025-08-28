#!/usr/bin/env python3
"""
Retire les ancres #p.XX des expected_doc_ids dans gold.jsonl
"""
import json
from pathlib import Path
from datetime import datetime

def clean_anchors():
    print("🔧 NETTOYAGE DES ANCRES DANS GOLD.JSONL")
    print("="*50)
    
    gold_path = Path("data/eval/gold.jsonl")
    
    # Backup
    backup_path = Path(f"data/eval/gold.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
    import shutil
    shutil.copy2(gold_path, backup_path)
    print(f"✅ Backup créé: {backup_path}")
    
    # Lire et nettoyer
    questions = []
    with open(gold_path, 'r', encoding='utf-8') as f:
        for line in f:
            question = json.loads(line)
            # Nettoyer les expected_doc_ids
            if 'expected_doc_ids' in question:
                cleaned_ids = []
                for doc_id in question['expected_doc_ids']:
                    # Retirer l'ancre #p.XX
                    if '#' in doc_id:
                        doc_id = doc_id.split('#')[0]
                    cleaned_ids.append(doc_id)
                question['expected_doc_ids'] = cleaned_ids
            questions.append(question)
    
    # Sauvegarder
    with open(gold_path, 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    print(f"✅ {len(questions)} questions nettoyées")
    return len(questions)

if __name__ == "__main__":
    clean_anchors()
    print("\n📝 Relancez maintenant : python scripts/rag_eval.py --gold data/eval/gold.jsonl")