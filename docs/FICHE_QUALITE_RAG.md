# FICHE QUALITÉ RAG — Moteyi (Étape 6)

## 1) Contexte métier
Moteyi doit expliquer un exercice scanné **en ≤ 5 s**, dans la **bonne langue**, en s’alignant sur le **programme officiel RDC**. Cette fiche définit **comment** nous mesurons et améliorons la qualité.

## 2) Objectifs & SLO
- **Latence E2E p95** ≤ **5 s** (OCR → Retrieval → LLM → TTS)
- **Feedback utile (👍)** ≥ **80 %** (pilote)
- **coverage@5** ≥ **0.60**, **hit@1** ≥ **0.45**, **MRR@5** ≥ **0.55**
- **Taux de langue correcte** ≥ **98 %**
- **Taux d’hallucination** ≤ **5 %**

## 3) Corpus & Périmètre (référence)
- Programmes officiels RDC (primaire/secondaire), manuels homologués INRAP, ENAFEP/EXETAT.
- Versionnage & checksums gérés par CI (voir `ci.yml`).

## 4) Jeu d’évaluation GOLD (JSONL)
Fichier: `data/eval/gold.jsonl` — **1 entrée par ligne**:
```json
{
  "id": "LN_MATH_001",
  "lang": "lingala",
  "grade": "4e_primaire",
  "subject": "mathématiques",
  "query": "Na ndenge nini kobongola fraction ya 3/4 na pourcentage?",
  "expected_doc_ids": ["prog_math_4e_2023.pdf#p.12"],
  "expected_span": "Chapitre 2.1 - Fractions et pourcentages",
  "skill_tag": "fractions:conversion",
  "answer_reference": "3/4 = 0,75 = 75%"
}
