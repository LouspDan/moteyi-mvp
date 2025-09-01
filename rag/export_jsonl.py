#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

def main():
    print("Export JSONL - Pipeline RAG")
    output_dir = Path("data/export")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rag_export.jsonl"
    data = {"id": "doc_001", "status": "ok"}
    with open(output_file, "w") as f:
        f.write(json.dumps(data))
    print("Export OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
