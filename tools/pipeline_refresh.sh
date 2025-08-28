#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Pipeline Moteyi : manifest -> normalize -> reconcile -> index -> eval -> report
# Usage:
#   bash tools/pipeline_refresh.sh
# Options:
#   FAIL_COV5 / FAIL_HIT1 (env) : seuils d'échec eval (défaut 0.50 / 0.35)
# -----------------------------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CATALOG="data/rag_seed/rag_seed_catalog.csv"
MANIFEST="data/index/manifest.json"
GOLD="data/eval/gold.jsonl"

FAIL_COV5="${FAIL_COV5:-0.50}"
FAIL_HIT1="${FAIL_HIT1:-0.35}"

echo "==> 1) Catalog -> Manifest"
python tools/catalog_to_manifest.py --catalog "$CATALOG" --out "$MANIFEST"

echo "==> 2) Normalize naming (apply)"
python tools/normalize_rag_seed_naming.py --catalog "$CATALOG" --apply

echo "==> 3) Reconcile gold.jsonl (apply)"
python tools/reconcile_gold_ids.py --apply

echo "==> 4) Index retriever config"
python scripts/rag_index.py

echo "==> 5) Eval (k=5) avec seuils FAIL_COV5=$FAIL_COV5, FAIL_HIT1=$FAIL_HIT1"
export FAIL_COV5 FAIL_HIT1
mkdir -p artifacts
python scripts/rag_eval.py --gold "$GOLD" --k 5 --out artifacts/metrics.csv || true

echo "==> 6) Rapport HTML"
python scripts/eval_report.py

echo "==> ✅ DONE"
echo " - Manifest : $MANIFEST"
echo " - Metrics  : artifacts/metrics.csv"
echo " - Report   : artifacts/rag_eval_report.html"
