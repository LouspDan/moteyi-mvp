# Moteyi MVP — Repo d’Accueil

🚀 **Moteyi** est le **tuteur IA multilingue** de l’écosystème Eteyelo.  
Ce dépôt contient le code, la documentation et les assets nécessaires pour le **MVP no‑code** démonstrateur.

---

## 🎯 Mission de ce repo

- Fournir un **MVP fonctionnel** basé sur la killer feature :
  > *« Photo cahier → Explication vocale Lingala/Swahili/FR en ≤5s »*
- Structurer un dépôt Git propre, versionné et documenté (Étapes 1 à 3 validées).
- Servir de **preuve de concept** virale et crédible pour la relance Eteyelo.

---

## 🔗 Lien avec l’écosystème Eteyelo

**Eteyelo** est la plateforme éducative IA pour l’Afrique, organisée en 3 sous‑marques principales :

1. **Moteyi AI (B2C-first)** — Prof IA personnel (repo actuel `moteyi-mvp`)
2. **Connect AI (B2B)** — Communication école ↔ familles (repo à venir)
3. **Marketplace Éducatif** — Contenus & services éducatifs (repo à venir)

Moteyi est **la porte d’entrée stratégique** de l’écosystème.  
Le succès de ce MVP crée la traction pour les modules suivants (ERP, Marketplace, etc.).

---

## 🧱 Contenu du repo

- `docs/` : résumés Étape 1 et 2, architecture, diagrammes (pipeline WOW).  
- `config/prompts/` : prompts multilingues (LN, KK, SW, TSH, FR, EN).  
- `make_scenarios/` : exports Make (orchestration no‑code).  
- `data/rag_seed/` : catalogue initial de 20 docs validés (programmes RDC).  
- `scripts/` : automatisations (init Git, CI à venir).  
- `.env.example` : variables standardisées (WhatsApp, OpenAI, Google, ElevenLabs).  
- `README.md` : guide d’utilisation technique.  
- `README_accueil.md` *(ce fichier)* : vision produit et rôle stratégique.

---

## 🚀 Roadmap intégrée

### Phase MVP (repo actuel)
- WhatsApp → Make → OCR → GPT → TTS (Alpha multilingue).  
- 50 familles pilotes, 1 vidéo démo virale, 20 docs validés.

### Phase Écosystème
- **Connect AI** (B2B écoles) → intégration avec Moteyi.  
- **Marketplace** → contenus éducatifs, services, paiements Mobile Money.  
- **ERP & LMS 2.0** → alignement programmes officiels, dashboards, certification.

---

## ✅ Conventions de travail

- Branches : `main` (stable), `develop` (intégration), `feat/*`.  
- Commits : Conventional Commits + template `.gitmessage`.  
- CHANGELOG maintenu à chaque étape.  
- Secrets protégés (`.env`, `config/keys/`).

---

## 📌 Prochaines étapes

1. Finaliser `.env` local et configurer Make (WhatsApp Sandbox).  
2. Compléter `data/rag_seed/rag_seed_catalog.csv` (20 docs math + FR validés).  
3. Réaliser 1ère démo vidéo (≤30s).  
4. Lancer test avec 50 familles via WhatsApp.  
5. Préparer le passage à l’Étape 4 (orchestration CI/CD + monitoring).

---

> **Mantra Eteyelo** : « Frapper fort dès le départ » — chaque commit doit contribuer à l’effet WOW et à la crédibilité du projet.
