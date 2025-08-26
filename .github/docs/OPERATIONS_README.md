# Operations — Runbook MVP

## Webhook WhatsApp → Make
- Vérifier status Make (scénario actif).
- Regarder l’historique exécutions (erreurs, latence).
- Si erreur 429/5xx, activer file d’attente côté Make.

## OCR / LLM / TTS
- OCR : vérifier quota Google, latence API.
- LLM : surveiller tokens et coûts (OpenAI dashboard).
- TTS : vérifier quota ElevenLabs.

## Incidents (Sentry)
- Classer par stage (OCR/LLM/TTS).
- Hotfix prompt ou réduire taille message.
- Communiquer statut (WhatsApp message de maintenance si >30min).

## Sauvegarde
- `rag_seed_catalog.csv` sauvegardé dans Git (sans binaires docs).
- Export PostHog mensuel pour KPI.
