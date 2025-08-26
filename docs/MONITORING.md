# Monitoring — Moteyi MVP

## Objectifs
- Surveiller la **disponibilité** du webhook WhatsApp/Make.
- Mesurer la **latence** globale (photo → réponse).
- Suivre le **coût** par requête et le **volume** quotidien.

## Outils
- **UptimeRobot** : ping endpoint public (webhook Make).
- **PostHog** : événements (photo_reçue, ocr_ok, gpt_ok, tts_ok, réponse_envoyée).
- **Sentry** : erreurs (OCR, LLM, TTS, réseau).

## Événements recommandés (PostHog)
- `moteyi_photo_received`
- `moteyi_ocr_done` (props: chars, manuscrit/imprimé)
- `moteyi_llm_done` (props: tokens, langue, niveau)
- `moteyi_tts_done` (props: voix, durée_audio)
- `moteyi_reply_sent` (props: latence_totale_ms)
- `moteyi_error` (props: type, stage)

## Tableaux utiles
- Latence P50/P95 par langue et par type d’exercice
- Taux d’échec OCR/LLM/TTS
- Coût/requête estimé
- Usage quotidien/hebdo (DAU/WAU)
