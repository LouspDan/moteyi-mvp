# RAG — Corpus Officiel RDC (Étape 5/9)

**But :** garantir un corpus **fiable**, **traçable** et **reproductible** pour Moteyi.

## ✅ Checklist Qualité
- Source **officielle** ou validée (MEN‑RDC/INRAP/UNESCO).
- Fichier **lisible** (PDF texte ou OCR possible).
- Métadonnées **complètes** dans `rag_seed_catalog.csv` (schéma étendu).
- **Checksum** SHA-256 calculé et stocké.
- **Licence/Provenance** renseignée.
- Si OCR : `ocr_text_ratio` ≥ 0.30 recommandé (sinon marquer en `notes`).

## 🧱 Nommage Fichiers
`[annee]_[cycle]_[matiere]_[version].pdf`  
Exemples : `2023_primaire_4_maths_v1.pdf`, `2022_secondaire_francais_grammaire_v2.pdf`

## 🗂️ Emplacements (recommandés)
```
data/rag_seed/
├─ primaire/{{maths,francais,sciences,...}}
├─ secondaire/{{...}}
├─ humanites/{{...}}
├─ examens/{{enafep,exetat}}
└─ rag_seed_catalog.csv
```

## 🧾 Schéma CSV (étendu)
```
id,title,source_url,fetched_at,language,grade_level,subject,doc_type,
file_path,file_size_bytes,pages,ocr_text_ratio,checksum_sha256,
license,validated_by,validated_at,ingested,notes
```

## 🔁 Orchestration & CI
- Workflow planifié **tous les lundis 05:00 UTC** (`.github/workflows/ingest_rag.yml`).
- Ouvre automatiquement une **PR** si des changements sont détectés.

*Généré le 2025-08-27.*
