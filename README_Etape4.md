# Moteyi — Étape 4/9 : CI/CD & Monitoring (No‑Code‑First)

## 1) Contexte métier
Moteyi doit **frapper fort** et rester **fiable**. Cette étape formalise l’**orchestration de qualité** (CI), la **mise en conformité** (contrôles de repo) et la **visibilité produit** (monitoring des flux WhatsApp → Make → OCR → GPT → TTS).

## 2) Objectifs business
- Réduire le risque de régression du MVP.
- Gagner de la crédibilité (pro + documenté).
- Mesurer l’usage (activation, latence, coût/requête) pour piloter la croissance.

## 3) Données utilisées
- `data/rag_seed/rag_seed_catalog.csv` (schéma vérifié).
- Logs agrégés (volumétrie requêtes, temps de réponse, erreurs).

## 4) Stack technique
- **GitHub Actions** : pipeline CI minimaliste.
- **Scripts maison** : `scripts/quality_checks.sh`, `scripts/check_rag_seed_catalog.py`.
- **Monitoring** : PostHog (product analytics), UptimeRobot (disponibilité webhook), Sentry (erreurs).

## 5) Pipeline de traitement (CI)
1. `checkout` → 2. `quality_checks.sh` (fichiers clés, .env.example, prompts) →
3. `check_rag_seed_catalog.py` (schéma + colonnes) → 4. artefacts et statut PR.

## 6) Résultats attendus
- PR bloquée si structure ou CSV non conformes.
- Temps de réponse et incidents suivis (tableau Monitoring).

## 7) Valeur ajoutée
- Fiabilité et propreté perçue → confiance early adopters/partenaires.
- Base mesurable pour itérer (croissance et coûts).

## 8) Comment déployer
1. **Copier** le pack à la racine du repo `moteyi-mvp/` (écrasement OK).
2. **Créer** les secrets GitHub (si besoin) : `POSTHOG_API_KEY`, `SENTRY_DSN` (optionnels).
3. **Push** : le workflow CI s’exécute automatiquement sur PR/commit.

---

**Fichiers inclus dans ce pack :**
- `.github/workflows/ci.yml`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `CODEOWNERS`
- `scripts/quality_checks.sh`
- `scripts/check_rag_seed_catalog.py`
- `docs/MONITORING.md`
- `docs/OPERATIONS_README.md`

*Généré le 2025-08-26.*
