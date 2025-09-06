# Plan de Travail — Projet Moteyi / Eteyelo  
**Version : Septembre 2025**  
**Règle :** Avant toute tâche, les développeurs doivent lire ce fichier pour connaître le contexte et la prochaine étape.

---

## 🎯 Objectifs Globaux
- Reconnecter les modules Bot ↔ RAG ↔ Multilingue pour atteindre l’effet **WOW**.  
- Réduire la latence à **≤ 5 s (P95)**.  
- Activer le **multilingue complet** (FR + 4 langues locales + EN).  
- Préparer un **test pilote** (50 familles).  
- Produire une **documentation unifiée** et traçable.

---

## 📌 Tâches Prioritaires (Étape 3 — Plan de Redressement)

### Action 1 — Connecteur RAG ↔ Bot
- [ ] Implémenter fonction `query_rag()` (FastAPI minimal).  
- [ ] Appeler `query_rag()` depuis le pipeline Flask.  
- [ ] Vérifier que chaque réponse GPT intègre les documents RDC.  
**Dépendances :** `manifest.json`, `rag_eval_fixed.py` validés.  
**Livrable :** `bot/core_rag_connector.py` + tests unitaires.  
**Succès :** 100% réponses avec références RDC.

---

### Action 2 — Modification du Bot Flask
- [ ] Réviser pipeline : `OCR → RAG → GPT → TTS → send_message/send_audio`.  
- [ ] Corriger la fonction `send_audio()` (cf. rapport v1.0).  
- [ ] Tester en local avec WhatsApp Sandbox.  
**Dépendances :** Action 1.  
**Livrable :** Release `v1.1` (GitHub tag).  
**Succès :** pipeline complet confirmé sur 10 cas.

---

### Action 3 — Enrichissement des Prompts GPT
- [ ] Ajouter contexte : matière, niveau, doc source.  
- [ ] Insérer exemples culturels congolais.  
- [ ] Stocker dans `config/prompts/`.  
**Dépendances :** Action 1.  
**Livrable :** fichiers YAML/JSON de prompts.  
**Succès :** réponses contextualisées sur 10 cas/langue.

---

### Action 4 — Sélection de Langue
- [ ] Implémenter menu WhatsApp au démarrage (`LANG`).  
- [ ] Routage vers prompt + TTS adaptés.  
- [ ] Tester FR + Swahili + Lingala.  
**Dépendances :** Action 3.  
**Livrable :** module `bot/lang_selector.py`.  
**Succès :** utilisateur reçoit explication dans langue choisie.

---

### Action 5 — Tests avec Familles Pilotes
- [ ] Créer groupe WhatsApp test (50 familles).  
- [ ] Déployer version `v1.1`.  
- [ ] Mesurer latence, feedback, clarté des réponses.  
**Dépendances :** Actions 1–4.  
**Livrable :** Rapport pilote (PDF + dashboard).  
**Succès :** NPS ≥ 8/10 ; ≥ 80% réponses jugées utiles.

---

### Action 6 — Documentation Unifiée
- [ ] Rédiger ce `plan_de_travail.md`.  
- [ ] Mettre à jour `README.md` + `docs/`.  
- [ ] Générer rapport HTML (`eval_report.py`).  
**Dépendances :** Actions 1–5.  
**Livrable :** docs versionnées dans `/docs`.  
**Succès :** documentation validée en revue.

---

## ⏱️ Estimations Durées
- Action 1 (RAG ↔ Bot) : 2 jours.  
- Action 2 (Bot Flask) : 2 jours.  
- Action 3 (Prompts) : 1 jour.  
- Action 4 (Langues) : 2 jours.  
- Action 5 (Pilote) : 5 jours.  
- Action 6 (Docs) : continu.  

**Total sprint Étape 3 : ~2 semaines.**

---

## 📊 Métriques de Suivi
- Latence P95 ≤ 5 s.  
- coverage@5 ≥ 0.60 (actuel = 1.00).  
- hit@1 ≥ 0.35 (actuel = 1.00).  
- Disponibilité API > 99%.  
- NPS familles pilotes ≥ 8/10.  
- ≥ 4 langues locales supportées en texte, ≥ 2 en audio.  

---

## ✅ Prochaine Étape
Dès validation de ce plan, attaquer **Action 1 (Connecteur RAG ↔ Bot)**.  
Aucune autre action ne doit être commencée avant validation explicite.

---
