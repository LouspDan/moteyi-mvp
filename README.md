# 🚀 Moteyi MVP – Tutor IA multilingue (RDC / Afrique)

[![CI – Build](https://github.com/LouspDan/moteyi-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/LouspDan/moteyi-mvp/actions/workflows/ci.yml)
[![Quality – RAG](https://github.com/LouspDan/moteyi-mvp/actions/workflows/rag_index_eval.yml/badge.svg)](https://github.com/LouspDan/moteyi-mvp/actions/workflows/rag_index_eval.yml)
[![Licence: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

✨ **Photo du cahier → Explication vocale en 5 secondes**  
📲 Disponible sur **WhatsApp & PWA**  
🗣️ Langues : **Lingala, Swahili, Kikongo, Tshiluba, Français, Anglais**

---

## 🎯 Vision

**Moteyi** est le **tuteur IA d’Eteyelo**, pensé comme un **prof particulier virtuel** accessible aux familles africaines.  
Notre objectif : offrir un soutien scolaire de qualité, multilingue et abordable (≈ 3 €/mois).

- **Quoi ?** 📚 Un assistant pédagogique IA accessible via WhatsApp.  
- **Pourquoi ?** 🌍 Réduire les inégalités d’accès à l’éducation.  
- **Comment ?** 🔎 OCR + RAG (programmes officiels RDC) + GPT + TTS multilingue.  

---

## 🧩 Architecture & Pipeline

- [⚡ Pipeline Effet WOW](docs/diagrams/moteyi-pipeline-visual.html)  
- [🌐 Architecture Globale](docs/diagrams/moteyi-architecture-wow.html)  
- [🎛️ Monitoring & Observabilité](docs/diagrams/moteyi-monitoring-architecture.html)  

---

## 📌 Progression par étapes (9 étapes)

| Étape | Description                                   | Statut |
|-------|-----------------------------------------------|--------|
| 1     | Cadre MVP & vision produit                    | ✅ Validée |
| 2     | Option multilingue (FR + LN/KK/SW/TSH/EN)     | ✅ Validée |
| 3     | Initialisation Git & scaffold repo            | ✅ Validée |
| 4     | Prompts multilingues & config                 | ✅ Validée |
| 5     | Migration RAG (Corpus Officiel RDC)           | ✅ Validée (120 docs + rapport) |
| 6     | Indexation & Évaluation RAG                   | 🚧 En cours |
| 7     | Orchestration WhatsApp/Make + RAG branché     | ⏳ À faire |
| 8     | Monitoring avancé & feedback utilisateurs    | ⏳ À faire |
| 9     | Packaging & lancement pilote (familles/écoles)| ⏳ À faire |

📑 Voir le [CHANGELOG](CHANGELOG.md) pour le détail de chaque jalon.  
📘 Voir [docs/README_CI.md](docs/README_CI.md) pour l’exploitation CI/CD.

---

## ⚙️ Démarrage rapide

```bash
# Cloner le repo
git clone https://github.com/LouspDan/moteyi-mvp.git
cd moteyi-mvp

# Initialiser l'environnement
cp .env.example .env   # renseigner vos clés API
./scripts/init_repo.sh

# Vérifier le catalogue RAG
python data/rag_seed/scripts/check_rag_seed_catalog.py --mode strict
```

📌 Variables à renseigner (`.env`) :
- `META_WHATSAPP_TOKEN`
- `OPENAI_API_KEY`
- `GOOGLE_VISION_KEY`
- `ELEVENLABS_VOICE_ID`
- *(optionnel)* `POSTHOG_API_KEY`, `SENTRY_DSN`

---

## 🛡️ Monitoring Qualité (Étape 6)

- **CI Quality Check** : `check_rag_seed_catalog.py` (structure + checksums)  
- **Rapport RAG** : [`data/rag_seed/report.md`](data/rag_seed/report.md)  
- **Nightly Eval** : export → index pgvector → harness évaluation  

SLOs visés :
- ⏱️ Latence P95 end-to-end ≤ 5s  
- 📊 Feedback positif ≥ 80%  
- 📖 Coverage@5 ≥ 0.60  
- 🟢 Uptime webhook ≥ 99.5%  

---

## 🌍 Impact social

- 🎒 **1000 familles pilotes** ciblées en RDC dès l’Alpha  
- 📈 **+30% d’amélioration des notes** en 2 mois (objectif mesuré)  
- 🤝 Communauté éducative (enseignants, parents, élèves) fédérée autour de l’IA  

---

## 🤝 Contribuer

Les contributions sont les bienvenues 🙌  
- Lire le guide [CONTRIBUTING.md](CONTRIBUTING.md)  
- Respecter la checklist PR :  
  - [ ] Tests manuels effectués  
  - [ ] CHANGELOG mis à jour  
  - [ ] Pas de secrets commités  
  - [ ] Docs mises à jour  

---

## 📜 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE).
