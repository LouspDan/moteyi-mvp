#!/usr/bin/env bash
set -euo pipefail

# Init git
git init

# Set default branch to main if needed
git symbolic-ref HEAD refs/heads/main || true

git add .
git commit -m "chore: initial scaffold (Étape 3/9)" || true

# Create develop branch
if ! git show-ref --quiet refs/heads/develop; then
  git branch develop
fi

echo "[OK] Dépôt initialisé. Branches: main, develop."
echo "Vous pouvez définir le template de commit: git config commit.template .gitmessage"
