# STRUCTURE DU PROJET MOTEYI/ETEYELO

## Organisation Actuelle (Post-Nettoyage)

### Dossiers Principaux
- scripts/active/ : Bot WhatsApp et modules actifs
- data/ (569M) : Données RAG et index FAISS
- docs/ (1.1M) : Documentation
- tools/ (168K) : Outils de développement
- archive/ (479K) : Code archivé

### Nettoyage Effectué
- 373 MB libérés (venv/test_env supprimés)
- Espace total : 727 MB (avant 1.1 GB)
- Projet prêt pour Sprint Phoenix

### Lancement du Bot
cd /d/PROJET/moteyi-mvp
python -X utf8 scripts/active/moteyi_whatsapp_cloud_bot.py
