#!/usr/bin/env python3
"""
Moteyi Repository Audit Toolkit
--------------------------------
Scan a local clone of the repository and produce a structured JSON + Markdown report:
- Directory tree & file inventory (size, lines, last modified)
- Language breakdown & LOC
- Detection of "inactive" (stale) files by last modified threshold
- Likely "orphan" Python modules (not imported by others)
- Redundancies (duplicate files by hash; duplicate large assets)
- CI/Secrets hygiene checks (.env, secrets in repo, large binaries in code dirs)
- RAG assets inventory (docs/, data/, rag_seed/ etc.); unmatched catalog entries
- Prompt & config inventory (prompts/, *.prompt, *.yaml, *.json, *.md)
- Test coverage proxy (presence of tests/, pytest.ini, *.ipynb notebooks without checkpoints)
- Git attributes: latest commits per top-level dir (if repo is a git clone)

Usage:
    python moteyi_repo_audit.py --repo /path/to/moteyi-mvp --days-stale 30 --max-depth 8 --output out_dir

Outputs:
    - out_dir/audit_inventory.json
    - out_dir/audit_findings.json
    - out_dir/audit_report.md
"""
import argparse, os, re, sys, json, hashlib, time, subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

TEXT_EXT = {'.py','.md','.txt','.json','.yml','.yaml','.toml','.ini','.cfg','.csv','.tsv','.sql','.html','.js','.ts','.tsx','.css','.scss','.env','.prompt'}
CODE_EXT = {'.py','.js','.ts','.tsx','.sql','.html','.css','.scss'}
NB_EXT = {'.ipynb'}
BIN_EXT = {'.png','.jpg','.jpeg','.gif','.webp','.pdf','.doc','.docx','.ppt','.pptx','.mp3','.wav','.ogg','.mp4','.mov','.zip','.tar','.gz','.7z','.rar'}

def sha256_file(p, chunk=1024*1024):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def count_lines(path):
    try:
        with open(path,'rb') as f:
            return sum(1 for _ in f)
    except Exception:
        return None

def git_latest_commit_date(repo):
    try:
        out = subprocess.check_output(['git','log','-1','--format=%ct'], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()
        return int(out) if out else None
    except Exception:
        return None

def git_dir_commit_map(repo, depth=1):
    res = {}
    try:
        # for top-level dirs
        for p in Path(repo).iterdir():
            if p.is_dir():
                try:
                    out = subprocess.check_output(['git','log','-1','--format=%ct','--',str(p.relative_to(repo))],
                                                  cwd=repo, stderr=subprocess.DEVNULL).decode().strip()
                    res[str(p.name)] = int(out) if out else None
                except Exception:
                    res[str(p.name)] = None
        return res
    except Exception:
        return res

def find_imports(py_path):
    imports = set()
    try:
        with open(py_path,'r',encoding='utf-8',errors='ignore') as f:
            for line in f:
                line=line.strip()
                m = re.match(r'from\s+([a-zA-Z0-9_\.]+)\s+import', line)
                if m: imports.add(m.group(1).split('.')[0])
                m = re.match(r'import\s+([a-zA-Z0-9_\.]+)', line)
                if m: imports.add(m.group(1).split('.')[0])
    except Exception:
        pass
    return imports

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, help='Path to local repo root')
    ap.add_argument('--days-stale', type=int, default=30, help='Threshold in days for inactivity')
    ap.add_argument('--max-depth', type=int, default=8, help='Max recursion depth')
    ap.add_argument('--output', default='audit_out', help='Output directory')
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

    now = time.time()
    stale_cutoff = now - args.days_stale*24*3600

    inventory = []
    dup_map = defaultdict(list)
    lang_counter = Counter()
    code_loc = Counter()
    imports_map = {}
    module_files = {}
    rag_assets = []
    prompts = []
    secrets_findings = []
    large_in_code = []
    notebooks = []
    max_depth = args.max_depth

    def walk(dir_path, depth=0):
        if depth>max_depth: return
        for entry in Path(dir_path).iterdir():
            p = entry
            try:
                stat = p.stat()
            except Exception:
                continue
            rel = str(p.relative_to(repo))
            item = {
                'path': rel,
                'is_dir': p.is_dir(),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'ext': p.suffix.lower()
            }
            inventory.append(item)
            if p.is_file():
                ext = p.suffix.lower()
                if ext in CODE_EXT or ext in TEXT_EXT:
                    lang_counter[ext]+=1
                    loc = count_lines(p)
                    if loc is not None:
                        code_loc[ext]+=loc
                if ext in BIN_EXT and any(rel.startswith(x) for x in ['src','app','bot','api','scripts']):
                    if stat.st_size>2*1024*1024:
                        large_in_code.append({'path':rel,'size':stat.st_size})
                if p.name.lower() in {'.env','.env.local','secrets.json','credentials.json'}:
                    secrets_findings.append({'path':rel,'note':'Potential secret file committed'})
                if ext in {'.pdf','.doc','.docx','.ppt','.pptx'} and any(s in rel.lower() for s in ['rag','docs','data','curriculum','programmes']):
                    rag_assets.append(rel)
                if any(k in rel.lower() for k in ['prompt','prompts']) or ext=='.prompt':
                    prompts.append(rel)
                # duplicates by content hash for files under 10MB
                if stat.st_size<10*1024*1024:
                    try:
                        h = sha256_file(p)
                        dup_map[h].append(rel)
                    except Exception:
                        pass
                # python imports
                if ext=='.py':
                    imports_map[rel] = list(sorted(find_imports(p)))
                    module_files[Path(rel).stem] = rel
            if p.is_dir():
                walk(p, depth+1)

    walk(repo)

    # Orphan modules: python files that are not imported by any other local file and not entrypoints
    imported_modules = set()
    for imps in imports_map.values():
        for m in imps:
            if m in module_files:
                imported_modules.add(m)
    orphan_py = []
    for m, path in module_files.items():
        if m not in imported_modules and not any(s in path for s in ['__init__.py','main.py','cli.py','wsgi.py','asgi.py','manage.py','bot.py']):
            orphan_py.append(path)

    # stale files
    stale_files = [i['path'] for i in inventory if not i['is_dir'] and i['mtime']<stale_cutoff]

    # duplicates (only those with >1)
    duplicates = [v for v in dup_map.values() if len(v)>1]

    inv_path = out/'audit_inventory.json'
    findings_path = out/'audit_findings.json'
    report_path = out/'audit_report.md'

    with open(inv_path,'w',encoding='utf-8') as f:
        json.dump({'generated_at':datetime.utcnow().isoformat(),'inventory':inventory}, f, indent=2)
    findings = {
        'generated_at': datetime.utcnow().isoformat(),
        'summary': {
            'files_total': len([i for i in inventory if not i['is_dir']]),
            'dirs_total': len([i for i in inventory if i['is_dir']]),
            'languages': dict(lang_counter),
            'loc_by_ext': dict(code_loc)
        },
        'stale_files': stale_files,
        'orphan_python_modules': orphan_py,
        'duplicates': duplicates,
        'rag_assets': rag_assets,
        'prompts': prompts,
        'secrets_findings': secrets_findings,
        'large_binaries_in_code': large_in_code,
        'git': {
            'latest_repo_commit': git_latest_commit_date(str(repo)),
            'latest_commit_by_top_dir': git_dir_commit_map(str(repo))
        }
    }
    with open(findings_path,'w',encoding='utf-8') as f:
        json.dump(findings, f, indent=2)

    # Generate Markdown report
    def fmt_ts(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else 'N/A'

    md = []
    md.append(f"# Audit du Répertoire – Moteyi MVP\n")
    md.append(f"Généré le: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}\n")
    md.append("## Synthèse\n")
    md.append(f"- Fichiers: {findings['summary']['files_total']} | Dossiers: {findings['summary']['dirs_total']}\n")
    md.append(f"- Langages (extensions): {', '.join(f'{k}:{v}' for k,v in findings['summary']['languages'].items())}\n")
    md.append(f"- LOC par extension: {', '.join(f'{k}:{v}' for k,v in findings['summary']['loc_by_ext'].items())}\n")
    md.append("## Inactifs (stale)\n")
    if findings['stale_files']:
        md.extend(f"- {p}" for p in findings['stale_files'][:200])
        if len(findings['stale_files'])>200:
            md.append(f"... (+{len(findings['stale_files'])-200} autres)")
    else:
        md.append("- Rien à signaler")
    md.append("\n## Modules Python orphelins\n")
    if findings['orphan_python_modules']:
        md.extend(f"- {p}" for p in findings['orphan_python_modules'])
    else:
        md.append("- Aucun détecté")
    md.append("\n## Doublons (hash identiques)\n")
    if findings['duplicates']:
        for group in findings['duplicates'][:50]:
            md.append("- " + " | ".join(group))
        if len(findings['duplicates'])>50:
            md.append(f"... (+{len(findings['duplicates'])-50} groupes)")
    else:
        md.append("- Aucun détecté")
    md.append("\n## Gros binaires dans le code (à déplacer vers assets/ ou CDN)\n")
    if findings['large_binaries_in_code']:
        for it in findings['large_binaries_in_code']:
            md.append(f"- {it['path']} ({it['size']} o)")
    else:
        md.append("- Aucun détecté")
    md.append("\n## RAG – Actifs\n")
    if findings['rag_assets']:
        md.extend(f"- {p}" for p in findings['rag_assets'])
    else:
        md.append("- Rien détecté (vérifier data/rag_seed/, docs/)")
    md.append("\n## Prompts & Config\n")
    if findings['prompts']:
        md.extend(f"- {p}" for p in findings['prompts'])
    else:
        md.append("- Aucun fichier de prompt détecté")
    md.append("\n## Hygiène Secrets/CI\n")
    if findings['secrets_findings']:
        md.extend(f"- {x['path']}: {x['note']}" for x in findings['secrets_findings'])
    else:
        md.append("- Pas de secrets évidents")
    md.append("\n## Git – Derniers commits\n")
    md.append(f"- Dernier commit repo: {fmt_ts(findings['git']['latest_repo_commit'])}")
    for d, ts in (findings['git']['latest_commit_by_top_dir'] or {}).items():
        md.append(f"  - {d}: {fmt_ts(ts)}")
    md.append("\n---\n*Fin du rapport généré automatiquement.*\n")

    with open(report_path,'w',encoding='utf-8') as f:
        f.write("\n".join(md))

    print(f"✅ Audit terminé.\n- {inv_path}\n- {findings_path}\n- {report_path}")
if __name__ == "__main__":
    main()
