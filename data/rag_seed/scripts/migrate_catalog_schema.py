import pandas as pd
import os

INPUT_CSV = "data/rag_seed/rag_seed_catalog.csv"
OUTPUT_CSV = "data/rag_seed/rag_seed_catalog_migrated.csv"

REQUIRED_COLUMNS = ["id", "cycle", "matiere", "niveau", "langue", "source", "path"]

def migrate_catalog():
    df = pd.read_csv(INPUT_CSV)
    
    # Ajout colonnes manquantes si besoin
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    
    # Normalisation des champs
    df["id"] = df.apply(lambda row: f"{row['cycle']}_{row['matiere']}_{row.name}", axis=1)
    df["langue"] = df["langue"].fillna("fr")
    
    # Export
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Migration terminée. Nouveau fichier : {OUTPUT_CSV}")

if __name__ == "__main__":
    migrate_catalog()
