# Makefile — Utilitaires Moteyi RAG & CI/CD
# ---------------------------------------------------------
# Usage rapide :
#   make help
#   make validate-ci        # Contrat (CI) : manifest <-> catalog, sans PDFs
#   make validate-local     # Local : vérifie présence des PDFs
#   make test-rag           # Audit + évaluation gold + print des métriques
#   make audit              # Audit de couverture du corpus
#   make eval               # Évaluation RAG sur gold.jsonl
#   make check-ci           # Enchaîne validate-ci + affichage meta
#   make show-tree          # Aperçu des fichiers data/
#   make clean-artifacts    # Nettoyage des artifacts
#   make lint               # Lint si ruff/flake8 dispo
#   make format             # Format si black dispo
# ---------------------------------------------------------

.ONESHELL:

# ===== Config =====
PY ?= python
VALIDATOR := scripts/validate_rag.py
GOLD := data/eval/gold.jsonl
ARTIFACTS := artifacts
DATA_DIR := data
INDEX_DIR := $(DATA_DIR)/index
CATALOG := $(DATA_DIR)/rag_seed/rag_seed_catalog.csv
MANIFEST := $(INDEX_DIR)/manifest.json

# ===== Aide =====
.PHONY: help
help:
	@echo "Cibles disponibles :"
	@echo "  make validate-ci       -> Valide le CONTRAT (CI mode, sans PDFs)"
	@echo "  make validate-local    -> Valide avec PDFs (dev local)"
	@echo "  make test-rag          -> Audit + Eval gold + affiche métriques"
	@echo "  make audit             -> Audit de couverture du corpus"
	@echo "  make eval              -> Évaluation RAG avec gold.jsonl"
	@echo "  make check-ci          -> validate-ci + export meta"
	@echo "  make show-tree         -> Affiche un extrait des fichiers data/"
	@echo "  make clean-artifacts   -> Supprime artifacts/"
	@echo "  make lint              -> Lance ruff/flake8 si dispo"
	@echo "  make format            -> Lance black si dispo"

# ===== Validation (dual-mode) =====
.PHONY: validate-ci
validate-ci:
	@echo "🔎 Validation CONTRAT (CI mode) ..."
	@CI=true RAG_CHECK_MODE=ci $(PY) $(VALIDATOR)

.PHONY: validate-local
validate-local:
	@echo "🔎 Validation LOCALE (avec PDFs) ..."
	@$(PY) $(VALIDATOR)

# ===== Audit & Évaluation =====
.PHONY: audit
audit:
	@echo "📊 Audit de couverture du corpus ..."
	@$(PY) tools/corpus_audit.py

.PHONY: eval
eval:
	@echo "🧪 Évaluation RAG (gold set) ..."
	@$(PY) scripts/rag_eval.py --gold $(GOLD)

.PHONY: test-rag
test-rag: audit eval
	@echo "📄 Métriques (si générées) :"
	@if [ -f "$(ARTIFACTS)/metrics.csv" ]; then \
		cat $(ARTIFACTS)/metrics.csv; \
	else \
		echo "⚠️  $(ARTIFACTS)/metrics.csv introuvable (pas encore produit par l'éval)."; \
	fi

# ===== CI helper =====
.PHONY: check-ci
check-ci: validate-ci
	@echo "📦 Meta CI :"
	@if [ -f "$(ARTIFACTS)/catalog_meta.json" ]; then \
		cat $(ARTIFACTS)/catalog_meta.json; \
	else \
		echo "⚠️  $(ARTIFACTS)/catalog_meta.json introuvable (l’étape CI ne l’a pas généré)."; \
	fi

# ===== Utilitaires =====
.PHONY: show-tree
show-tree:
	@echo "📂 Aperçu data/ :"
	@find $(DATA_DIR) -maxdepth 3 -type f | head -n 50 || true

.PHONY: clean-artifacts
clean-artifacts:
	@rm -rf $(ARTIFACTS)
	@echo "🧹 $(ARTIFACTS)/ nettoyé."

# ===== Qualité (optionnel si outils non installés) =====
.PHONY: lint
lint:
	@echo "🔍 Lint du code ..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check . ; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 . ; \
	else \
		echo "⚠️  Aucun linter trouvé (installe ruff ou flake8)."; \
	fi

.PHONY: format
format:
	@echo "🧽 Formatage du code ..."
	@if command -v black >/dev/null 2>&1; then \
		black . ; \
	else \
		echo "⚠️  black non installé (pip install black)."; \
	fi
