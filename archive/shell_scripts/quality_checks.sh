#!/usr/bin/env bash
set -euo pipefail

mkdir -p ci_reports

# 1) Required files exist
required=(
  "README.md"
  ".gitignore"
  ".gitmessage"
  "CHANGELOG.md"
  "docs/ETAPE_1_RESUME.md"
  "docs/ETAPE_2_RESUME.md"
  "config/prompts/system_multilingue.txt"
  "config/prompts/user_template.txt"
  "data/rag_seed/rag_seed_catalog.csv"
  "scripts/init_repo.sh"
)
missing=()
for f in "${required[@]}"; do
  [[ -f "$f" ]] || missing+=("$f")
done

if (( ${#missing[@]} > 0 )); then
  printf "❌ Missing required files:\n" | tee -a ci_reports/quality.txt
  printf '%s
' "${missing[@]}" | tee -a ci_reports/quality.txt
  exit 1
else
  echo "✅ Required files present" | tee -a ci_reports/quality.txt
fi

# 2) .env.example sanity
if [[ ! -f ".env.example" ]]; then
  echo "❌ .env.example missing" | tee -a ci_reports/quality.txt
  exit 1
fi

needed_vars=(
  "META_WHATSAPP_TOKEN"
  "OPENAI_API_KEY"
  "GOOGLE_APPLICATION_CREDENTIALS"
  "ELEVENLABS_API_KEY"
)
for v in "${needed_vars[@]}"; do
  if ! grep -q "^${v}=" .env.example; then
    echo "❌ Missing var in .env.example: ${v}" | tee -a ci_reports/quality.txt
    exit 1
  fi
done
echo "✅ .env.example keys OK" | tee -a ci_reports/quality.txt

# 3) Prompt files not empty
for p in config/prompts/*.txt; do
  if [[ ! -s "$p" ]]; then
    echo "❌ Empty prompt file: $p" | tee -a ci_reports/quality.txt
    exit 1
  fi
done
echo "✅ Prompts look non-empty" | tee -a ci_reports/quality.txt

echo "🎉 CI quality checks passed." | tee -a ci_reports/quality.txt
