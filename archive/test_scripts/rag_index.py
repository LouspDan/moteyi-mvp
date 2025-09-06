#!/usr/bin/env python3
"""
rag_index.py — Étape B.7 (stub)
- Prépare le "retriever provider" en écrivant un petit fichier de config.
- Plus tard: remplacer par vraie indexation (pgvector / pinecone).
"""
import json, os, pathlib

def main():
    pathlib.Path("data/index").mkdir(parents=True, exist_ok=True)
    cfg = {
        "mode": os.getenv("RETRIEVER_MODE", "oracle"),  # oracle | http
        "http_endpoint": os.getenv("RETRIEVER_HTTP", ""),  # si mode http
        "k": int(os.getenv("RETRIEVER_K", "5"))
    }
    with open("data/index/retriever_config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"[rag_index] OK - config écrite: {cfg}")

if __name__ == "__main__":
    main()
