# Créez analyse.py dans le dossier scripts
import pandas as pd

df = pd.read_csv('../data/rag_seed/rag_seed_catalog.csv')

print("="*50)
print("RÉSUMÉ DE LA COLLECTE")
print("="*50)
print(f"Total documents : {len(df)}")
print(f"Documents validés : {len(df[df['validated'] == 'true'])}")
print(f"Documents en erreur : {len(df[df['validated'] == 'false'])}")
print("\n📚 PAR MATIÈRE :")
print(df['matiere'].value_counts())
print("\n🌍 PAR LANGUE :")
print(df['langue'].value_counts())
print("\n📖 PAR TYPE :")
print(df['type_doc'].value_counts())
print("\n🎓 PAR NIVEAU :")
print(df['grade_level'].value_counts().head(10))
print("\n📂 PREMIERS DOCUMENTS :")
print(df[['titre', 'matiere', 'validated']].head(10))