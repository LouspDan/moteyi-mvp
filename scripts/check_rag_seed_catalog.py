#!/usr/bin/env python3
import csv, sys, json, os

EXPECTED = [
  "id","titre","source_url","langue","grade_level","matiere","type_doc",
  "file_path","checksum","licence","ingested","validated","notes"
]

path = "data/rag_seed/rag_seed_catalog.csv"
if not os.path.exists(path):
  print("❌ rag_seed_catalog.csv not found")
  sys.exit(1)

with open(path, newline="", encoding="utf-8") as f:
  reader = csv.reader(f)
  rows = list(reader)

if not rows:
  print("❌ CSV is empty")
  sys.exit(1)

header = rows[0]
if header != EXPECTED:
  print("❌ Header mismatch")
  print("Found :", header)
  print("Expect:", EXPECTED)
  sys.exit(1)

print("✅ RAG seed catalog header OK")
# Optional: warn if < 1 data row
if len(rows) < 2:
  print("⚠️ No data rows yet (expect ~20 docs minimum).")
