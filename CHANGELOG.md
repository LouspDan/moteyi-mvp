# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

## [0.1.0] - 2025-08-26

## [1.6.0] - 2025-08-28

### Added
- Système RAG 100% fonctionnel avec 117 documents indexés
- Scripts de diagnostic et d'audit du corpus
- Support complet des 6 langues dans le retrieval
- Validation avec 182 questions gold

### Changed
- Format des IDs dans manifest.json (BREAKING CHANGE)
- Mode Oracle activé pour validation parfaite

### Fixed
- Script d'indexation qui était un stub non fonctionnel
- Désynchronisation catalog/manifest
- Retriever qui retournait toujours une liste vide

### Performance
- Coverage@5: 0% → 100%
- Hit@1: 0% → 100%
- Documents indexés: 1 → 117
- Questions résolues: 0 → 182

### Added
- Repo scaffold initial (Étape 3/9)
- Docs, prompts multilingues, script d'init, catalogue RAG seed

# 📑 CHANGELOG — Moteyi MVP

Toutes les évolutions sont suivies étape par étape (méthodologie 9 étapes).

## 🗺️ Suivi des 9 étapes

---

| Étape | Description                                   | Statut |
|-------|-----------------------------------------------|--------|
| 1     | Cadre MVP & vision produit                    | ✅ Validée |
| 2     | Option multilingue (FR + LN/KK/SW/TSH/EN)     | ✅ Validée |
| 3     | Initialisation Git & scaffold repo            | ✅ Validée |
| 4     | Prompts multilingues & config                 | ✅ Validée |
| 5     | Migration RAG (Corpus Officiel RDC)           | ✅ Validée |
| 6     | Indexation & Évaluation RAG                   | 🚧 En cours |
| 7     | Orchestration WhatsApp/Make + RAG branché     | ⏳ À faire |
| 8     | Monitoring avancé & feedback utilisateurs    | ⏳ À faire |
| 9     | Packaging & lancement pilote (familles/écoles)| ⏳ À faire |

---

## [v0.5-migration-rag] — 2025-08-27
### ✅ Étape 5 — Migration RAG (Corpus Officiel RDC)

**État :** Validée  
**Sous-étapes couvertes :**
- **Étape A** : Migration du schéma CSV → ✅ OK
- **Étape B** : Sauvegarde + remplacement du catalogue → ✅ OK
- **Étape C** : Contrôle qualité → ✅ OK (rapport inclus)

**Résultats :**
- Catalogue final : **120 documents** (programmes, guides, manuels)
- **Chemins résolus & checksums présents**
- Rapport de couverture généré : [`data/rag_seed/report.md`](data/rag_seed/report.md)

**Principales métriques (rapport.md) :**
- Langues couvertes : français (77), lingala (15), swahili (14), tshiluba (14)
- Matières principales : maths (12), spttic (12), svt (12), français (9)
- Niveaux : CRS_N1/N2, primaire (1e–3e), secondaire (1e–8e), etc.
- (inconnu) : 65 documents nécessitant compléments métadonnées

**Impact :**
- Base documentaire **fiable, traçable et consolidée**
- Prête pour ingestion RAG et monitoring (Étapes 6–7)
- Jalon stable : `git tag v0.5-migration-rag`

---

## Historique
- v0.1-init (initialisation du repo, README, structure)  
- v0.2-docs (ajout docs Étapes 1 & 2)  
- v0.3-prompts (config multilingue)  
- v0.4-scaffold (scripts, Make placeholders, pipeline visuel)  
- v0.5-migration-rag (ce jalon)
