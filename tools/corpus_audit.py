# tools/corpus_audit.py
import json
import csv
import os
from pathlib import Path
from collections import defaultdict

def audit_corpus():
    """
    Compare manifest.json vs rag_seed_catalog.csv
    pour identifier les documents non indexés
    """
    print("🔍 AUDIT DU CORPUS RAG - MOTEYI MVP")
    print("="*50)
    
    # 1. Charger le manifest depuis le BON chemin
    manifest_path = Path('data/index/manifest.json')
    if not manifest_path.exists():
        print(f"❌ Fichier manifest.json introuvable dans {manifest_path}")
        print("⚠️  Vérifiez que l'indexation a bien été lancée")
        return None
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # 2. Charger le catalog CSV
    catalog_path = Path('data/rag_seed/rag_seed_catalog.csv')
    catalog_docs = {}
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('file_path'):
                # Normaliser le chemin pour comparaison
                file_path = row['file_path'].replace('\\', '/')
                catalog_docs[file_path] = {
                    'id': row.get('id', ''),
                    'title': row.get('title', ''),
                    'grade_level': row.get('grade_level', ''),
                    'subject': row.get('subject', ''),
                    'language': row.get('language', '')
                }
    
    # 3. Analyser le manifest - CORRECTION ICI
    manifest_docs = {}
    
    # Le manifest peut être soit une liste directe, soit un dict avec 'documents'
    if isinstance(manifest, list):
        documents = manifest
    elif isinstance(manifest, dict) and 'documents' in manifest:
        documents = manifest['documents']
    else:
        print("⚠️  Format du manifest non reconnu")
        documents = []
    
    for doc in documents:
        file_path = doc.get('file', '').replace('\\', '/')
        manifest_docs[file_path] = {
            'id': doc.get('id', ''),
            'chunks': doc.get('chunks', 0) if 'chunks' in doc else len(doc.get('content', []))
        }
    
    # 4. Scanner les PDFs réellement présents sur disque
    pdf_files_on_disk = set()
    rag_seed_dir = Path('data/rag_seed')
    for pdf_file in rag_seed_dir.rglob('*.pdf'):
        relative_path = str(pdf_file.relative_to(Path('.'))).replace('\\', '/')
        pdf_files_on_disk.add(relative_path)
    
    print(f"\n📁 PDFs trouvés sur disque : {len(pdf_files_on_disk)}")
    print(f"📋 Documents dans catalog  : {len(catalog_docs)}")
    print(f"📄 Documents dans manifest : {len(manifest_docs)}")
    
    # 5. Analyser les différences
    catalog_files = set(catalog_docs.keys())
    manifest_files = set(manifest_docs.keys())
    
    # Documents dans catalog mais pas dans manifest (NON INDEXÉS)
    missing_in_manifest = catalog_files - manifest_files
    
    # Documents dans manifest mais pas dans catalog
    missing_in_catalog = manifest_files - catalog_files
    
    # PDFs sur disque mais ni dans catalog ni dans manifest (ORPHELINS)
    orphan_pdfs = pdf_files_on_disk - catalog_files - manifest_files
    
    # 6. Analyser par catégorie
    categories_stats = defaultdict(lambda: {'total': 0, 'indexed': 0, 'files': []})
    
    for file_path in pdf_files_on_disk:
        # Extraire la catégorie du chemin
        parts = file_path.split('/')
        if len(parts) > 3:
            category = parts[3]  # Ajusté pour data/rag_seed/[category]/
        else:
            category = 'root'
        
        categories_stats[category]['total'] += 1
        categories_stats[category]['files'].append(file_path)
        
        if file_path in manifest_files:
            categories_stats[category]['indexed'] += 1
    
    # 7. Générer le rapport
    report = {
        'summary': {
            'total_pdfs_on_disk': len(pdf_files_on_disk),
            'total_in_catalog': len(catalog_files),
            'total_in_manifest': len(manifest_files),
            'coverage_rate': (len(manifest_files) / len(pdf_files_on_disk) * 100) if pdf_files_on_disk else 0,
            'missing_count': len(missing_in_manifest) + len(orphan_pdfs)
        },
        'missing_in_manifest': sorted(list(missing_in_manifest)),
        'orphan_pdfs': sorted(list(orphan_pdfs)),
        'missing_in_catalog': sorted(list(missing_in_catalog)),
        'categories': dict(categories_stats),
        'recommendations': []
    }
    
    # 8. Ajouter des recommandations
    if report['missing_in_manifest']:
        report['recommendations'].append(
            f"🔴 URGENT: {len(missing_in_manifest)} documents du catalog ne sont pas indexés"
        )
    
    if report['orphan_pdfs']:
        report['recommendations'].append(
            f"⚠️  {len(orphan_pdfs)} PDFs non référencés trouvés - À ajouter au catalog"
        )
    
    if report['summary']['coverage_rate'] < 50:
        report['recommendations'].append(
            "💡 Taux de couverture < 50% - Relancer l'indexation complète recommandée"
        )
    
    # 9. Sauvegarder le rapport
    os.makedirs('reports', exist_ok=True)
    report_path = Path('reports/corpus_audit_report.json')
    
    # Nettoyer les listes de fichiers pour le JSON
    clean_categories = {}
    for cat, stats in categories_stats.items():
        clean_categories[cat] = {
            'total': stats['total'],
            'indexed': stats['indexed'],
            'coverage': (stats['indexed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        }
    report['categories'] = clean_categories
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 10. Afficher le résumé
    print("\n📊 RÉSUMÉ DE L'AUDIT")
    print("-"*50)
    print(f"📁 PDFs trouvés sur disque    : {report['summary']['total_pdfs_on_disk']}")
    print(f"📋 Documents dans le catalog   : {report['summary']['total_in_catalog']}")
    print(f"✅ Documents indexés (manifest): {report['summary']['total_in_manifest']}")
    print(f"📈 Taux de couverture          : {report['summary']['coverage_rate']:.1f}%")
    print(f"❌ Documents non indexés       : {report['summary']['missing_count']}")
    
    print("\n📂 RÉPARTITION PAR CATÉGORIE")
    print("-"*50)
    for cat, stats in categories_stats.items():
        coverage = (stats['indexed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅" if coverage > 80 else "⚠️" if coverage > 50 else "❌"
        print(f"{status} {cat:20s}: {stats['indexed']}/{stats['total']} ({coverage:.0f}%)")
    
    # Afficher quelques exemples de fichiers non indexés
    if missing_in_manifest:
        print("\n❌ EXEMPLES DE FICHIERS NON INDEXÉS (max 5)")
        print("-"*50)
        for file_path in list(missing_in_manifest)[:5]:
            print(f"  - {file_path}")
    
    if orphan_pdfs:
        print("\n⚠️  EXEMPLES DE PDFs ORPHELINS (max 5)")
        print("-"*50)
        for file_path in list(orphan_pdfs)[:5]:
            print(f"  - {file_path}")
    
    if report['recommendations']:
        print("\n💡 RECOMMANDATIONS")
        print("-"*50)
        for rec in report['recommendations']:
            print(rec)
    
    print(f"\n📄 Rapport détaillé sauvé dans : {report_path}")
    
    # 11. Créer un CSV des fichiers à indexer en priorité
    priority_files_path = Path('reports/files_to_index_priority.csv')
    with open(priority_files_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['file_path', 'status', 'category'])
        
        # D'abord les fichiers du catalog non indexés
        for file_path in sorted(missing_in_manifest)[:50]:  # Top 50
            parts = file_path.split('/')
            category = parts[3] if len(parts) > 3 else 'root'
            writer.writerow([file_path, 'in_catalog_not_indexed', category])
        
        # Puis les PDFs orphelins
        for file_path in sorted(orphan_pdfs)[:20]:  # Top 20
            parts = file_path.split('/')
            category = parts[3] if len(parts) > 3 else 'root'
            writer.writerow([file_path, 'orphan_pdf', category])
    
    print(f"📋 Liste prioritaire créée     : {priority_files_path}")
    
    return report

if __name__ == "__main__":
    report = audit_corpus()
    
    if report and report['summary']['coverage_rate'] < 10:
        print("\n🚨 ALERTE CRITIQUE : Taux de couverture < 10% !")
        print("   Le RAG ne peut pas fonctionner correctement.")
        print("   Action immédiate requise : relancer l'indexation complète")
        
        print("\n🔥 COMMANDE SUGGÉRÉE POUR RÉINDEXER :")
        print("   python scripts/rag_index.py")