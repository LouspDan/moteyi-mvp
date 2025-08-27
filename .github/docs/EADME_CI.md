# 🧪 CI / CD — Moteyi MVP

Ce dossier documente la **CI rapide du repo** et la **qualité RAG** (export → indexation → évaluation).  
Objectifs : **stabilité**, **traçabilité**, **qualité pédagogique**.

---

## 🏷️ Workflows & Badges

- **Build & Repo Quality** — `.github/workflows/ci.yml`  
  [![CI – Build](https://github.com/LouspDan/moteyi-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/LouspDan/moteyi-mvp/actions/workflows/ci.yml)

- **RAG: Export / Index / Eval (Nightly + Manual)** — `.github/workflows/rag_index_eval.yml`  
  [![Quality – RAG](https://github.com/LouspDan/moteyi-mvp/actions/workflows/rag_index_eval.yml/badge.svg)](https://github.com/LouspDan/moteyi-mvp/actions/workflows/rag_index_eval.yml)

---

## 🔧 Ce que fait chaque workflow

### 1) `ci.yml` (rapide, sur PR & pushes)
- Installe Python & deps légers.
- **Quality checks repo** (optionnel via `scripts/quality_checks.sh`).
- **Validation du catalogue RAG** :  
  `python data/rag_seed/scripts/check_rag_seed_catalog.py --mode ci`  
  > Mode **CI** = tolérant à l’absence des PDFs dans le runner (pas de *missing_file* bloquant).
- **Rapport de couverture** :  
  `python data/rag_seed/scripts/report_rag.py` (si présent).
- **Artefacts** : `moteyi-ci-reports` (report.md, catalog.csv, logs).

### 2) `rag_index_eval.yml` (Nightly 02:00 UTC + déclenchement manuel)
- Installe deps RAG (pypdf, sqlalchemy, psycopg2-binary, rank-bm25, openai, tiktoken, numpy).
- **Export JSONL** → `rag/export_jsonl.py`
- **Indexation pgvector** → `rag/index_pgvector.py --create`
- **Évaluation rapide** → `eval/run_eval.py` → `eval/report.md`
- **Artefacts** : `rag-nightly` (export.jsonl + report.md)

---

## 🔐 Secrets requis

Configurer dans **GitHub → Settings → Secrets and variables → Actions** :

| Secret            | Usage                                  | Exemple                                                                    |
|------------------|----------------------------------------|----------------------------------------------------------------------------|
| `OPENAI_API_KEY` | Embeddings & éventuel LLM judge        | `sk-...`                                                                   |
| `PG_URL`         | Connexion Postgres/pgvector            | `postgresql+psycopg2://user:pass@host:5432/dbname`                        |
| (optionnel) `POSTHOG_API_KEY` | Telemetry produit         | `phc_...`                                                                  |
| (optionnel) `SENTRY_DSN`      | Traces erreurs            | `https://<key>@o<org>.ingest.sentry.io/<project>`                          |

> Les clés WhatsApp/Google/ElevenLabs restent côté runtime produit, **pas** nécessaires à ces jobs CI.

---

## 🧰 Modes de vérification du catalogue

Le checker supporte trois modes (CLI `--mode` ou ENV `RAG_CHECK_MODE`):

- `strict` : exige la présence **réelle** des fichiers (usage **local/pré-prod**).
- `ci` / `lenient` : ignore `missing_file` dans les runners GitHub (usage **CI**).
- Auto-détection GitHub Actions : défaut `ci` si `GITHUB_ACTIONS=true`.

Exemples :
```bash
# Local strict (recommandé avant de pousser)
python data/rag_seed/scripts/check_rag_seed_catalog.py --mode strict

# CI lenient (déjà activé dans ci.yml)
python data/rag_seed/scripts/check_rag_seed_catalog.py --mode ci
