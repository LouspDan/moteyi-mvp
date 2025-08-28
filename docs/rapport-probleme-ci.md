# 🚨 Rapport d'Incident CI/CD - Pipeline Bloqué
## Projet Moteyi MVP - Étape 6 RAG System

---

## 📋 Informations Générales

| Élément | Détail |
|---------|--------|
| **Date de l'incident** | 28 Août 2025 |
| **Projet** | Moteyi MVP - Système EdTech RDC |
| **Étape concernée** | Étape 6 - Système RAG |
| **Sévérité** | 🔴 **CRITIQUE** - Bloque la PR et la suite du projet |
| **Statut** | ⚠️ **NON RÉSOLU** - En attente de correction |
| **Impact** | Pipeline CI échoue systématiquement |
| **Branche affectée** | `feat/etape6-rag-resolution` |

---

## 🔍 Description du Problème

### Symptôme Principal
Le pipeline CI GitHub Actions échoue systématiquement à l'étape "Validate RAG seed catalog" avec des erreurs de type `no_checksum` pour tous les fichiers PDF référencés dans le catalogue.

### Message d'Erreur Type
```
❌ Problemes (checksums manquants):
- no_checksum guides_pedagogiques\Guide-de-leducateur-_-Alphabetisation-fonctionnelle.pdf
- no_checksum guides_pedagogiques\Guide-de-leducateur-_-Alphabetisation-initiale.pdf
- no_checksum guides_pedagogiques\Guide-de-leducateur-_-Francais-CRS-N2.pdf
[... 114 autres erreurs similaires ...]
```

### Conséquences
1. **PR bloquée** : Impossible de merger les changements de l'étape 6
2. **Développement arrêté** : Impossible de passer à l'étape 7 (WhatsApp)
3. **CI rouge** : Affecte la crédibilité technique du projet
4. **Tests invalides** : Les validations RAG ne peuvent pas s'exécuter

---

## 🔬 Analyse Technique Détaillée

### 1. Architecture du Problème

```
┌─────────────────────────────────────┐
│         GitHub Repository              │
│  ├── data/                            │
│  │   ├── rag_seed/                    │
│  │   │   ├── rag_seed_catalog.csv ✅  │ ← Présent (référence 117 PDFs)
│  │   │   └── *.pdf ❌                 │ ← ABSENTS (non versionnés, trop lourds)
│  │   └── index/                       │
│  │       └── manifest.json ✅         │ ← Présent
│  └── scripts/                         │
│      └── check_rag_seed_catalog.py ⚠️ │ ← Cherche les PDFs physiques
└────────────────────────────────────────┘
                    ↓
        ┌─────────────────────┐
        │   GitHub Actions CI  │
        │  RAG_CHECK_MODE=ci   │ ← Mode CI activé
        └─────────────────────┘
                    ↓
            ❌ ÉCHEC: PDFs introuvables
```

### 2. Cause Racine

Le script `check_rag_seed_catalog.py` appelé par la CI tente de :
1. Lire le catalogue CSV (✅ fonctionne)
2. Pour chaque entrée, vérifier l'existence du PDF (❌ échoue)
3. Calculer le checksum du PDF (❌ impossible sans fichier)

**Problème fondamental** : Les PDFs (~500MB au total) ne sont pas versionnés dans Git pour des raisons évidentes de taille, mais le script de validation CI essaie quand même de les traiter.

### 3. Analyse du Code Problématique

```python
# Script actuel (simplifié)
def validate_catalog():
    for entry in catalog:
        pdf_path = entry['file_path']
        if not os.path.exists(pdf_path):  # ← ÉCHOUE EN CI
            print(f"❌ no_checksum {pdf_path}")
            errors += 1
```

Le mode `RAG_CHECK_MODE=ci` est défini mais non utilisé correctement dans le script.

---

## 📊 Impact et Risques

### Impact Immédiat
| Aspect | Impact | Gravité |
|--------|--------|---------|
| **Développement** | Blocage total de la progression | 🔴 Critique |
| **CI/CD** | Pipeline en échec permanent | 🔴 Critique |
| **Équipe** | Impossibilité de collaborer via PR | 🟠 Élevé |
| **Planning** | Retard sur l'étape 7 (WhatsApp) | 🟠 Élevé |
| **Qualité** | Tests automatisés non exécutés | 🟡 Moyen |

### Risques si Non Résolu
1. **Technique** : Accumulation de dette technique
2. **Projet** : Retard sur le calendrier de livraison
3. **Confiance** : Perte de crédibilité sur la maîtrise technique
4. **Coûts** : Temps perdu en debugging = coûts additionnels

---

## 💡 Solutions Proposées

### Solution 1: Script de Validation Dual-Mode (RECOMMANDÉE)

**Principe** : Créer un script qui détecte automatiquement l'environnement d'exécution

```python
def validate_catalog():
    is_ci = os.environ.get('CI') or os.environ.get('RAG_CHECK_MODE') == 'ci'
    
    if is_ci:
        # Mode CI : Valider structure seulement
        validate_structure_only()
    else:
        # Mode local : Valider structure + fichiers
        validate_with_files()
```

**Avantages** :
- ✅ Un seul script à maintenir
- ✅ Comportement adaptatif
- ✅ Pas de duplication de code

**Inconvénients** :
- ⚠️ Logique plus complexe

### Solution 2: Scripts Séparés CI vs Local

**Principe** : Deux scripts distincts pour deux contextes

```bash
scripts/
├── validate_rag_ci.py      # Pour CI (structure only)
└── validate_rag_local.py   # Pour dev local (avec PDFs)
```

**Avantages** :
- ✅ Séparation claire des responsabilités
- ✅ Scripts simples et focalisés

**Inconvénients** :
- ⚠️ Duplication potentielle de code
- ⚠️ Maintenance de deux scripts

### Solution 3: Catalogue CI Allégé

**Principe** : Maintenir deux catalogues

```bash
data/rag_seed/
├── rag_seed_catalog.csv        # Catalogue complet (local)
└── rag_seed_catalog_ci.csv     # Catalogue sans checksums (CI)
```

**Avantages** :
- ✅ CI toujours verte
- ✅ Pas de modification de scripts

**Inconvénients** :
- ❌ Synchronisation difficile
- ❌ Source de vérité ambiguë

---

## 🔧 Plan d'Action Immédiat

### Étapes de Résolution (Ordre Chronologique)

#### Phase 1: Correction Immédiate (30 minutes)

1. **Créer le script de validation CI**
   ```bash
   # Créer scripts/validate_rag_ci.py
   # Implémenter la logique de validation structure seulement
   ```

2. **Modifier le workflow GitHub Actions**
   ```yaml
   - name: Validate RAG seed catalog (CI mode)
     env:
       CI: true
     run: python scripts/validate_rag_ci.py
   ```

3. **Tester localement**
   ```bash
   CI=true python scripts/validate_rag_ci.py
   # Doit passer sans erreur
   ```

#### Phase 2: Application et Validation (15 minutes)

4. **Commit des corrections**
   ```bash
   git add scripts/validate_rag_ci.py
   git add .github/workflows/ci.yml
   git commit -m "fix(ci): validation RAG adaptée pour CI sans PDFs"
   ```

5. **Push et vérification CI**
   ```bash
   git push origin feat/etape6-rag-resolution
   # Surveiller le pipeline GitHub Actions
   ```

#### Phase 3: Documentation (15 minutes)

6. **Mettre à jour la documentation**
   - README avec instructions pour les PDFs
   - CONTRIBUTING.md avec process de validation
   - Commentaires dans le code

---

## 📈 Métriques de Succès

| Métrique | Avant (Actuel) | Après (Cible) |
|----------|---------------|---------------|
| **Status CI** | ❌ Rouge | ✅ Vert |
| **Tests passants** | 0% | 100% |
| **PR mergeable** | Non | Oui |
| **Temps validation** | ∞ (échec) | <30 secondes |
| **Couverture catalogue** | 0% (CI) | 100% (structure) |

---

## 🚦 Critères de Validation

La solution sera considérée comme réussie si :

- [ ] Le pipeline CI passe au vert
- [ ] Le script valide la structure du catalogue
- [ ] Aucune recherche de PDFs physiques en mode CI
- [ ] Les tests locaux continuent de fonctionner avec PDFs
- [ ] La documentation est claire sur la gestion des PDFs

---

## 📚 Recommandations Architecture

### Court Terme (Immédiat)
1. Implémenter la **Solution 1** (Script Dual-Mode)
2. Documenter clairement le processus
3. Ajouter des tests unitaires pour le script

### Moyen Terme (Post-Étape 7)
1. Mettre en place un CDN/S3 pour héberger les PDFs
2. Implémenter un système de cache local
3. Créer un script de synchronisation PDFs

### Long Terme (Production)
1. Base de données vectorielle pour les embeddings
2. Pipeline de traitement asynchrone
3. Versioning des documents avec Git LFS ou alternative

---

## ⚠️ Points d'Attention Critiques

### 1. **NE PAS** versionner les PDFs
- Taille totale : ~500MB
- Ralentirait considérablement le clone du repo
- Limites GitHub (100MB/fichier, 1GB/repo recommandé)

### 2. **TOUJOURS** maintenir le catalogue
- Source de vérité pour les documents disponibles
- Nécessaire pour le tracking et l'audit
- Base pour l'indexation future

### 3. **DOCUMENTER** le processus
- Instructions claires pour obtenir les PDFs
- Process de mise à jour du catalogue
- Validation locale vs CI

---

## 📎 Ressources et Références

### Documentation Technique
- [GitHub Actions - Environment Variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables)
- [Python os.environ](https://docs.python.org/3/library/os.html#os.environ)
- [Git LFS pour fichiers volumineux](https://git-lfs.github.com/)

### Fichiers Concernés
```
.github/workflows/ci.yml
scripts/check_rag_seed_catalog.py
data/rag_seed/rag_seed_catalog.csv
data/index/manifest.json
```

### Commandes Utiles
```bash
# Tester en mode CI local
CI=true python scripts/validate_rag_ci.py

# Vérifier la taille des PDFs
du -sh data/rag_seed/*.pdf

# Compter les entrées du catalogue
wc -l data/rag_seed/rag_seed_catalog.csv
```

---

## 📝 Conclusion et Prochaines Étapes

### État Actuel
🔴 **BLOQUÉ** - Le pipeline CI empêche toute progression du projet. Ce problème DOIT être résolu avant de continuer vers l'étape 7.

### Action Requise
1. **Immédiat** : Appliquer la solution proposée (30-60 minutes)
2. **Validation** : Vérifier que la CI passe au vert
3. **Merge** : Fusionner la PR de l'étape 6
4. **Progression** : Démarrer l'étape 7 (WhatsApp)

### Message Clé
> ⚠️ **Ce problème est un BLOQUEUR CRITIQUE**. Aucune progression n'est possible tant que le pipeline CI n'est pas réparé. La solution est claire et peut être implémentée en moins d'une heure.

---

## 👥 Contacts et Escalade

| Rôle | Responsabilité | Action |
|------|---------------|---------|
| **Dev Lead** | Implémenter la correction | Priorité MAX |
| **DevOps** | Valider le workflow CI | Support si nécessaire |
| **PM** | Comprendre l'impact planning | Informé du blocage |

---

*Document généré le 28 Août 2025*  
*Projet: Moteyi MVP - Système EdTech pour la RDC*  
*Criticité: 🔴 BLOQUEUR - Résolution requise immédiatement*