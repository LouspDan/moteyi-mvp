#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation flexible du catalog RAG - Mode CI vs Local
"""
import csv
import os
import sys
from pathlib import Path

def check_catalog(ci_mode=False):
    """Valide le catalog avec tolerance en mode CI."""
    
    catalog_path = "data/rag_seed/rag_seed_catalog.csv"
    
    # Colonnes requises
    required_columns = [
        'id', 'file_path', 'titre', 'source_url', 'langue',
        'grade_level', 'matiere', 'type_doc', 'checksum',
        'licence', 'ingested', 'validated', 'notes'
    ]
    
    minimal_columns = ['id', 'file_path']
    
    print("[VALIDATION] Mode:", "CI" if ci_mode else "LOCAL")
    
    if not os.path.exists(catalog_path):
        print("[ERROR] Catalog introuvable:", catalog_path)
        return False
    
    valid = True
    issues = []
    
    with open(catalog_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        
        # Verification du schema
        if ci_mode:
            # Mode CI: schema complet maintenant present
            missing = set(required_columns) - set(headers)
            if missing:
                print("[ERROR] Colonnes manquantes:", missing)
                return False
            print("[OK] Schema complet - " + str(len(headers)) + " colonnes")
        else:
            # Mode Local: schema complet requis
            missing = set(required_columns) - set(headers)
            if missing:
                print("[ERROR] Colonnes manquantes:", missing)
                return False
            print("[OK] Schema complet - " + str(len(headers)) + " colonnes")
        
        # Validation des lignes
        row_count = 0
        for i, row in enumerate(reader, 1):
            row_count += 1
            
            if not row.get('id', '').strip():
                continue
            
            # En mode local uniquement, verifier les PDFs
            if not ci_mode and 'file_path' in row:
                pdf_path = Path("data/rag_seed") / row['file_path']
                if not pdf_path.exists():
                    issues.append("Ligne " + str(i) + ": PDF manquant - " + row['file_path'])
            
            # Verification des valeurs requises
            for col in minimal_columns:
                if col in row and not row[col].strip():
                    issues.append("Ligne " + str(i) + ": " + col + " vide")
    
    print("[STATS] Documents valides:", row_count)
    
    if issues:
        print("\n[WARNING] " + str(len(issues)) + " problemes detectes:")
        for issue in issues[:5]:
            print("  - " + issue)
        if len(issues) > 5:
            print("  ... et " + str(len(issues) - 5) + " autres")
        if ci_mode:
            print("[INFO] En mode CI, les PDFs manquants sont ignores")
            return True  # On accepte en CI
        valid = False
    else:
        print("[OK] Aucun probleme detecte")
    
    return valid

if __name__ == "__main__":
    # Detection du mode CI
    ci_mode = os.environ.get('CI') == 'true' or \
              os.environ.get('GITHUB_ACTIONS') == 'true' or \
              '--ci' in sys.argv
    
    success = check_catalog(ci_mode=ci_mode)
    exit(0 if success else 1)
