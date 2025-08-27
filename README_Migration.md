# Patch Étape 5 — Migration RAG (Qualité + Cron + Report)

**Généré le : 2025-08-27**

## 1) Ce que contient le patch
- `.github/workflows/ingest_rag.yml` — CI/CD planifié (cron hebdo) + PR auto.
- `data/rag_seed/README_RAG.md` — checklist qualité + schéma CSV étendu + règles nommage.
- `data/rag_seed/scripts/migrate_catalog_schema.py` — mise à niveau de votre `rag_seed_catalog.csv`.
- `data/rag_seed/scripts/check_rag_quality.py` — quality gate (fichiers présents, colonnes, checksum).
- `data/rag_seed/scripts/report_rag.py` — génère `data/rag_seed/report.md` (stats couverture).
- `ingest/sources.yaml` — manifeste de sources (exemple MEN‑RDC).
- `ingest/ingest.py` — orchestrateur simple (scraper + QA + report).
- `requirements-rag.txt` — dépendances minimales côté CI/local.

## 2) Installation (copier/coller)
```bash
# À la racine de votre repo local moteyi-mvp
unzip moteyi-mvp-rag-patch-etape5_full.zip -d moteyi-mvp
cd moteyi-mvp

# (Optionnel) Installer deps localement pour test
pip install -r requirements-rag.txt

# 1) Migrer le CSV vers le schéma étendu
python data/rag_seed/scripts/migrate_catalog_schema.py
# Vérifier le fichier généré, puis remplacer l'ancien :
mv data/rag_seed/rag_seed_catalog.migrated.csv data/rag_seed/rag_seed_catalog.csv

# 2) Lancer QA & Report en local
python data/rag_seed/scripts/check_rag_quality.py
python data/rag_seed/scripts/report_rag.py

# 3) Commit & push
git add .
git commit -m "chore(rag): patch Étape 5 (migration CSV, QA, cron, report)"
git push origin develop
```

## 3) CI/CD (cron hebdo)
Le workflow `ingest_rag.yml` s’exécute chaque **lundi 05:00 UTC** et peut être lancé à la main
depuis l’onglet *Actions* (événement `workflow_dispatch`). Il :
1. Exécute votre scraper `data/rag_seed/scripts/scraper_edu_rdc.py` si présent.
2. Applique le **quality gate**.
3. Génère `data/rag_seed/report.md`.
4. Ouvre une **Pull Request automatique** si des fichiers/CSV ont changé.

## 4) Schéma CSV (étendu)
```
id,title,source_url,fetched_at,language,grade_level,subject,doc_type,
file_path,file_size_bytes,pages,ocr_text_ratio,checksum_sha256,
license,validated_by,validated_at,ingested,notes
```

## 5) Points de contrôle qualité
- Chaque ligne pointe vers un **fichier existant** (`file_path`).
- `checksum_sha256` présent.
- `file_size_bytes` > 0, `pages` ≥ 1.
- Ratio OCR renseigné si OCR appliqué (sinon 0).

## 6) Personnalisation
- Modifiez le **cron** dans `.github/workflows/ingest_rag.yml`.
- Ajoutez des règles supplémentaires dans `check_rag_quality.py` (ex. `ocr_text_ratio ≥ 0.30`).
- Étendez `report_rag.py` pour inclure des graphes si besoin.
