#!/bin/bash
# CrÃ©ation d'un inventaire complet du projet
OUTPUT_FILE="INVENTORY_$(date +%Y%m%d_%H%M%S).txt"

echo "=== INVENTAIRE COMPLET PROJET MOTEYI ===" > $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "========================================" >> $OUTPUT_FILE

echo -e "\ní³ DOSSIERS VIDES:" >> $OUTPUT_FILE
find . -type d -empty | grep -v ".git" >> $OUTPUT_FILE

echo -e "\ní·‘ï¸ FICHIERS TEMPORAIRES/CACHE:" >> $OUTPUT_FILE
find . -name "__pycache__" -type d >> $OUTPUT_FILE
find . -name "*.pyc" -type f >> $OUTPUT_FILE
find . -name ".DS_Store" -type f >> $OUTPUT_FILE
find . -name "Thumbs.db" -type f >> $OUTPUT_FILE
find . -name "*~" -type f >> $OUTPUT_FILE
find . -name "*.swp" -type f >> $OUTPUT_FILE

echo -e "\ní³ FICHIERS LOG/TEST:" >> $OUTPUT_FILE
find . -name "*.log" -type f >> $OUTPUT_FILE
find . -name "*.txt" -type f | grep -E "(test|temp|tmp|old|backup)" >> $OUTPUT_FILE

echo -e "\ní³Š STRUCTURE PRINCIPALE:" >> $OUTPUT_FILE
ls -la | grep "^d" | awk '{print $9}' | while read dir; do
    if [ "$dir" != "." ] && [ "$dir" != ".." ]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "$dir/ : $count fichiers" >> $OUTPUT_FILE
    fi
done

echo -e "\ní¼³ ARBRE COMPLET (2 niveaux):" >> $OUTPUT_FILE
tree -L 2 2>/dev/null >> $OUTPUT_FILE || ls -laR >> $OUTPUT_FILE

echo -e "\nâœ… Inventaire sauvegardÃ© dans: $OUTPUT_FILE"
cat $OUTPUT_FILE
