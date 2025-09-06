# 🔍 AUDIT GLOBAL – Projet Moteyi MVP (Repo `moteyi-mvp`)

**Date :** 06 Septembre 2025  
**Auteur :** Sprint Phoenix – Consolidation Audit

---

## 1. Contexte & Périmètre

- **Repo audité :** [github.com/LouspDan/moteyi-mvp](https://github.com/LouspDan/moteyi-mvp)  
- **Sources analysées :**  
  - Rapport Étape 6 – RAG Monitoring【144】  
  - Rapport Intégration WhatsApp【147】  
  - Rapport Complet v1.0 + Stratégie Localisation【148】  
  - Rapport Formel Point A – Sprint Phoenix【149】  
  - Plan de Travail – Sprint Phoenix 72h【150】  
  - Rapport Diagnostic Eteyelo【146】  
  - Documents de cadrage (Étapes 1 & 7)【139】【145】

**Objectif business immédiat :** Effet WOW = *Photo WhatsApp → Explication vocale en langue locale RDC ≤ 5 secondes*.

---

## 2. Résumé Exécutif

### ✅ Points forts
- Pipeline complet validé (WhatsApp → OCR → GPT → TTS → WhatsApp).  
- OCR Vision (GPT-4o) performant : 95–100% manuscrit/équations【149】.  
- RAG 117 docs indexés avec 100% coverage/hit@1【144】.  
- Multilingue actif (FR, LN, SW, LU, EN) côté texte【149】.  
- Audio fonctionnel (FR/EN)【148】.  
- Architecture “WOW” documentée (visuals + fiches).  

### ❌ Points faibles
- Modules **déconnectés** : RAG non branché au bot Flask【146】.  
- **Latence** encore 10–12s (objectif ≤5s)【149】【150】.  
- **Audio local** manquant pour LN/KK/LU【149】.  
- **Architecture fragmentée** : coexistence Make.com / Flask【146】.  
- **Tokens/Ngrok** temporaires (non viable en prod)【148】.

---

## 3. Inventaire par Composants

### 3.1 Actifs
- **Bot WhatsApp Flask** – Webhook opérationnel【147】.  
- **OCR Vision API** – Stable et précis【149】.  
- **RAG (117 docs)** – Indexation corrigée, manifest/catalog alignés【144】.  
- **Multilingue Texte** – 5 langues actives【149】.  
- **TTS (FR/EN)** – Audio généré et envoyé【148】.

### 3.2 Inactifs / Orphelins
- **RAG non appelé** dans le pipeline Flask【146】.  
- **Prompts multilingues** disponibles mais non intégrés aux réponses【146】.  
- **Scripts stub (rag_index.py, oracle)** remplacés par `rag_index_real.py`【144】.  
- **Orchestration Make.com** encore présente dans doc, mais abandonnée【146】.  
- **TTS Lingala/Kikongo/Tshiluba** absent【149】.

### 3.3 Redondances & Risques
- **Deux architectures concurrentes** (Make.com vs Python)【146】.  
- **OCR Tesseract** encore mentionné/testé alors que Vision API validée【149】.  
- **Documents RAG doublons** (multi-formats : PDF/DOCX)【144】.  
- **Gestion tokens** : Ngrok et clés temporaires à remplacer【148】.

---

## 4. Bilan Stratégique

### Forces
- Démonstration “arme fatale” validée : audio en FR/EN sur WhatsApp【147】.  
- RAG totalement fiable (117 docs, coverage 100%)【144】.  
- OCR Vision corrige les faiblesses critiques de Tesseract【149】.  
- Multilingue déjà prêt côté texte (GPT)【149】.

### Faiblesses
- **Fragmentation** → Effet WOW impossible sans connexion des modules【146】.  
- **Accessibilité limitée** → Audio manquant pour langues locales【149】.  
- **Perf insuffisante** → Latence 2× l’objectif【150】.  
- **Prod instable** → Ngrok + tokens volatiles【148】.

---

## 5. Recommandations Chirurgicales

### P1 – Quick Wins (48h)
1. **Rebrancher RAG → Bot Flask**  
   - Intégrer `rag_connector.py` dans `moteyi_whatsapp_cloud_bot.py`.  
   - Vérifier contexte curriculum dans prompts【146】【149】.  

2. **Audio multilingue local**  
   - Activer Google Cloud TTS (Swahili)【148】.  
   - ElevenLabs (Lingala/Tshiluba).  
   - Menu de sélection langue via WhatsApp【145】.  

3. **Réduction latence (objectif 5s)**【150】  
   - Cache GPT/audio.  
   - Pré-resize images avant OCR.  
   - OCR+RAG parallélisés.  
   - Streaming réponses GPT.  

4. **Déploiement Prod**  
   - Serveur permanent (OVH/Scaleway).  
   - Token WhatsApp permanent.  
   - Monitoring PostHog + Sentry.  

### P2 – Consolidation (1–2 semaines)
- Glossaire scolaire multilingue【149】.  
- Prompts canoniques par matière/niveau.  
- RAG enrichi (examens + exercices corrigés).  
- CI/CD : GitHub Actions + audit automatique.  

---

## 6. Plan d’Action PRs

- **PR1 – perf/latency** → Cache + parallélisation.  
- **PR2 – feat/tts-locales** → TTS LN/KK/LU + dataset test audio.  
- **PR3 – rag/cleanup** → Dédoublonnage docs + manifest canonique.  
- **PR4 – ops/ci-audit** → Workflow audit (lint, secrets, assets).  
- **PR5 – i18n/prompts** → Glossaire + prompts normalisés.

---

## 7. Métriques Cibles (Sprint Phoenix)

- **Latence** : ≤ 5s (actuel : 10–12s).  
- **Langues Audio** : 5/5 (actuel : 2/5).  
- **Docs RAG** : 117 indexés (OK).  
- **Précision OCR** : >95% (OK).  
- **NPS** : ≥ 8/10 (à valider pilote).  

---

## 8. Conclusion

Le repo **moteyi-mvp** dispose de **tous les composants nécessaires** mais souffre de **fragmentation et de latence**.  
La priorité est de **connecter le RAG au bot Flask**, **ajouter audio multilingue**, et **réduire la latence** à 5s.  
Ces quick wins déclencheront l’effet WOW attendu et permettront le déploiement pilote (50 familles) dans les 7 jours.  

---

📌 **Prochaine étape validée :** Lancer **PR1 (perf/latency)** + **PR2 (tts-locales)** dans les 48h.  
