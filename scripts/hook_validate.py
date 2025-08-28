#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hook pre-commit cross-platform pour la validation dual-mode.
- Si des PDFs existent sous data/rag_seed => mode local
- Sinon => mode contrat (CI)
"""

import os
import sys
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "rag_seed"
VALIDATOR = REPO_ROOT / "scripts" / "validate_rag.py"

def has_pdfs() -> bool:
    try:
        next(DATA_DIR.rglob("*.pdf"))
        return True
    except StopIteration:
        return False

def main() -> int:
    # Assure un encodage tolérant (Windows)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if has_pdfs():
        # Mode local (avec PDFs)
        cmd = [sys.executable, str(VALIDATOR)]
        env = os.environ.copy()
    else:
        # Mode contrat (CI)
        cmd = [sys.executable, str(VALIDATOR)]
        env = os.environ.copy()
        env["CI"] = "true"
        env["RAG_CHECK_MODE"] = "ci"

    print("🔒 pre-commit: validation Moteyi RAG…")
    try:
        subprocess.run(cmd, env=env, check=True)
        print("✅ pre-commit: OK")
        return 0
    except subprocess.CalledProcessError as e:
        print("❌ pre-commit: validation échouée.")
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())
