# Plan de Travail — Projet Moteyi / Eteyelo  
**Version : Sprint Phoenix 72h - Septembre 2025**  
**Dernière mise à jour : 06/09/2025**

---

## 🎯 Objectif Sprint 72h
Créer l'effet **"WOW"** : Photo WhatsApp → Explication vocale en langue locale contextualisée RDC en ≤ 5 secondes

---

## 📊 État d'Avancement Global
- **Progression** : 25% (1/4 actions complétées)
- **Temps écoulé** : 4 heures
- **Temps restant** : 68 heures

---

## ✅ Action 1 — Connecteur RAG ↔ Bot [COMPLÉTÉ]
**Statut : ✅ VALIDÉ le 06/09/2025**

### Réalisations :
- [x] Module `rag_connector.py` créé et fonctionnel
- [x] 117 documents du curriculum RDC accessibles
- [x] Fonction `query_rag()` opérationnelle
- [x] Recherche avec scoring de pertinence
- [x] Contexte enrichi avec références MEPST/RDC
- [x] Tests validés sur math, lingala, sciences

### Métriques atteintes :
- Documents chargés : 117/117 ✅
- Documents multilingues : 42 (15 Lingala, 14 Kiswahili, 13 Ciluba) ✅
- Temps de recherche : <100ms ✅
- Taux de succès recherches : 100% ✅

### Livrable :
- `scripts/rag_connector.py` (v1.0 stable)
- Documentation intégrée
- Cache de recherche actif

---

## 🚀 Action 2 — Activation Multilingue [EN COURS]
**Statut : 🔄 PROCHAINE ÉTAPE IMMÉDIATE**

### Objectifs :
- [ ] Détecter la langue préférée de l'utilisateur
- [ ] Menu de sélection langue WhatsApp
- [ ] Adapter les prompts GPT selon la langue
- [ ] Générer réponses en Lingala/Kiswahili
- [ ] Router vers documents de la bonne langue

### Tâches techniques :
```python
# À implémenter dans bot Flask
- [ ] Fonction detect_user_language()
- [ ] Menu interactif WhatsApp (1.Français 2.Lingala 3.Kiswahili...)
- [ ] Prompts multilingues dans config/prompts/
- [ ] Session utilisateur avec préférence langue
```

### Documents disponibles par langue :
- Français : 75 documents ✅
- Lingala : 15 documents ✅
- Kiswahili : 14 documents ✅
- Tshiluba : 13 documents ✅

**Durée estimée** : 4-6 heures
**Priorité** : CRITIQUE

---

## ⏳ Action 3 — Intégration Bot Flask
**Statut : EN ATTENTE**

### Pré-requis :
- Action 1 ✅ (RAG connecté)
- Action 2 ⏳ (Multilingue)

### Modifications à apporter :
- [ ] Importer `rag_connector` dans `moteyi_whatsapp_cloud_bot.py`
- [ ] Appeler RAG avant GPT dans pipeline
- [ ] Utiliser prompt enrichi avec contexte
- [ ] Logger les documents utilisés
- [ ] Gérer les cas sans résultats RAG

### Code d'intégration :
```python
from rag_connector import CongoRAGConnector
rag = CongoRAGConnector(base_path="data")

# Dans process_message():
context = rag.query_rag(extracted_text, user_language)
enhanced_prompt = context['prompt_enhancement']
```

**Durée estimée** : 2 heures
**Dépendance** : Action 2

---

## 📝 Action 4 — Tests Familles Pilotes
**Statut : PLANIFIÉ**

### Préparation :
- [ ] Groupe WhatsApp test (20 familles minimum)
- [ ] Exercices types par niveau
- [ ] Formulaire feedback Google Forms
- [ ] Métriques de suivi (latence, satisfaction)

### Scénarios de test :
1. Math primaire en français
2. Sciences secondaire en français  
3. Question en Lingala → Réponse Lingala
4. Question en Kiswahili → Réponse Kiswahili

**Durée** : 24 heures de test continu
**Objectif** : NPS ≥ 8/10

---

## 📊 Métriques Sprint Phoenix 72h

| Métrique | Objectif | Actuel | Statut |
|----------|----------|---------|---------|
| Documents RAG connectés | 117 | 117 | ✅ |
| Langues supportées | 3+ | 1 (FR) | ⏳ |
| Latence P95 | ≤ 5s | 8-15s | ❌ |
| Familles test | 20 | 0 | ⏳ |
| Contexte RDC dans réponses | 100% | 100% | ✅ |

---

## 🔥 Prochaines 24h - Actions Critiques

### Immédiat (0-4h) :
1. ✅ ~~Connecteur RAG~~ [FAIT]
2. 🔄 Menu sélection langue WhatsApp
3. ⏳ Prompts Lingala/Kiswahili dans GPT

### Court terme (4-12h) :
4. ⏳ Intégration RAG dans bot Flask
5. ⏳ Tests internes multilingues
6. ⏳ Optimisation latence

### Moyen terme (12-24h) :
7. ⏳ Déploiement groupe pilote
8. ⏳ Collecte feedback initial
9. ⏳ Ajustements urgents

---

## 🚨 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|---------|------------|------------|
| TTS langues locales limité | Élevé | Certain | GPT texte + gTTS français |
| Latence > 5s | Moyen | Probable | Cache agressif + async |
| Adoption faible Lingala | Élevé | Possible | Focus sur démo vidéo virale |

---

## 📁 Structure Fichiers Projet

```
moteyi-mvp/
├── scripts/
│   ├── rag_connector.py ✅ [VALIDÉ]
│   ├── moteyi_whatsapp_cloud_bot.py [À MODIFIER]
│   └── archives/ [Tests archivés]
├── data/
│   ├── index/
│   │   └── manifest.json [117 docs]
│   └── rag_seed/
│       └── rag_seed_catalog.csv [117 entrées]
├── config/
│   └── prompts/ [À CRÉER]
│       ├── fr.yaml
│       ├── lingala.yaml
│       └── kiswahili.yaml
└── plan_de_travail.md [CE FICHIER]
```

---

## ✅ Validation des Étapes

**Règle stricte** : Chaque action doit être validée avant de passer à la suivante.

- [x] Action 1 (RAG) → ✅ Validé 06/09 
- [ ] Action 2 (Multilingue) → ⏳ En cours
- [ ] Action 3 (Bot Flask) → Bloqué par Action 2
- [ ] Action 4 (Pilote) → Bloqué par Action 3

---

## 📞 Contacts et Responsabilités

- **Lead Dev** : [À définir]
- **Test Pilote** : [À définir]
- **Support Meta/WhatsApp** : Token actif jusqu'au 07/09

---

## 💬 Notes de Sprint

### 06/09/2025 - 14h00
- RAG connecté avec succès, 117 documents accessibles
- Découverte : 42 documents déjà en langues locales !
- Prochaine priorité : Activation multilingue (Action 2)
- Estimation : Bot multilingue opérationnel dans 6h

### Commande Git pour commit :
```bash
git add scripts/rag_connector.py plan_de_travail.md
git commit -m "feat: RAG connector v1.0 - 117 docs RDC connectés
- Connexion manifest/catalog fonctionnelle
- Recherche avec scoring de pertinence  
- Contexte enrichi MEPST/RDC
- Tests validés math/lingala/sciences
- Sprint Phoenix 72h: 25% complété"
git push origin main
```

---

**🎯 PROCHAIN FOCUS : ACTION 2 - MULTILINGUE**