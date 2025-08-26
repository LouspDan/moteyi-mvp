# Moteyi — MVP No‑Code (Étape 3/9)

**But :** dépôt propre, versionné et prêt pour le MVP *WhatsApp → Make → OCR → GPT → TTS*.

## 🚀 Périmètre
- Canal d’entrée : WhatsApp (Meta Cloud API) via **Make** (scénarios/routers).
- OCR : Google Vision (ou alternative libre).
- LLM : OpenAI (GPT‑4.x), prompts multilingues LN/KK/SW/TSH/FR/EN.
- TTS : ElevenLabs (ou alternative), retour audio/texte à l’utilisateur.

## 📂 Structure
Voir `docs/FOLDERS.md`.

## 🔧 Mise en route rapide
```bash
./scripts/init_repo.sh
git config commit.template .gitmessage
cp .env.example .env
```
Renseigner ensuite les variables : `META_WHATSAPP_TOKEN`, `OPENAI_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `ELEVENLABS_API_KEY`, `ELEVENLABS_*_VOICE_ID`, etc.

## 🧪 Données
- Dossier `data/rag_seed/` : place‑holder et catalogue CSV à compléter (20 docs validés minimum).</n>
## 📜 Conventions
- **Conventional Commits** + **Keep a Changelog**.
- Branches : `main` (stable), `develop` (intégration), feature branches `feat/*`.

## 🔐 Sécurité
- `.env` et `config/keys/` ne sont **jamais** versionnés.
- Voir `SECURITY.md`.

## 📄 Licences
- Code : MIT (voir `LICENSE`). Contenus pédagogiques selon leur licence d’origine (catalogue obligatoire).

## 🧭 Historique
- Étape 1/9 & 2/9 résumées dans `docs/`.

---
*Généré le 2025-08-26.*
