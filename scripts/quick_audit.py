#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Audit Moteyi/Eteyelo – avec métriques calculées automatiquement
- RAG: coverage@5 / hit@1 (parsing stdout)
- Bot: latence P50/P95 (parsing logs)
- Corpus: manifest vs PDFs
- Prompts: langues détectées
- Exporte: artifacts/audit_report_*.md + .json
"""
import os, re, json, sys, subprocess, shlex, time, statistics
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
ART  = ROOT / "artifacts"
LOGS = ROOT / "logs"
DATA = ROOT / "data"
CONF = ROOT / "config"

TS   = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_JSON = ART / f"audit_report_{TS}.json"
OUT_MD   = ART / f"audit_report_{TS}.md"

def run(cmd, timeout=240):
    try:
        p = subprocess.run(shlex.split(cmd), timeout=timeout, cwd=ROOT,
                          capture_output=True, text=True)
        return {"ok": p.returncode == 0, "out": p.stdout, "err": p.stderr, "code": p.returncode}
    except Exception as e:
        return {"ok": False, "out": "", "err": str(e), "code": -1}

def ensure_dirs():
    ART.mkdir(parents=True, exist_ok=True)

# --------- RAG métriques -----------------------------------------------------
def parse_rag_metrics(stdout:str):
    """
    Accepte plusieurs formats possibles:
      coverage@5 = 100%   | coverage@5: 1.00 | coverage@5 0.87
      hit@1 = 80%         | hit@1: 0.80      | hit@1 0.55
    Retourne des floats 0..1 ou None.
    """
    def pick(name):
        m = re.search(fr"{name}\s*[:=]?\s*([0-9\.]+%?)", stdout, re.I)
        if not m: return None
        v = m.group(1)
        return (float(v.replace("%",""))/100.0) if "%" in v else float(v)
    return {
        "coverage@5": pick("coverage@?5"),
        "hit@1":      pick("hit@?1")
    }

# --------- Corpus ------------------------------------------------------------
def count_pdfs():
    return len(list((DATA / "rag_seed").rglob("*.pdf")))

def manifest_len_and_errors():
    man = DATA / "index" / "manifest.json"
    if not man.exists():
        return None, "absent"
    try:
        obj = json.loads(man.read_text(encoding="utf-8"))
        if isinstance(obj, list):
            return len(obj), None
        if isinstance(obj, dict) and "documents" in obj:
            return len(obj["documents"]), None
        return None, "format_inattendu"
    except Exception as e:
        return None, f"parse_error: {e}"

# --------- Langues détectées -------------------------------------------------
def detect_languages_in_prompts():
    langs = set()
    base = CONF / "prompts"
    if not base.exists():
        return []
    tags = ["fr", "francais", "français", "lingala", "swahili", "kikongo", "tshiluba", "en", "anglais"]
    for p in base.rglob("*"):
        n = p.name.lower()
        for t in tags:
            if t in n:
                langs.add(t)
    return sorted(langs)

# --------- Logs & latence ----------------------------------------------------
TS_RGX = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")
LAT_RGX = re.compile(r"LAT(total|_ms|ency)\s*[:=]\s*(?P<val>\d+(\.\d+)?)", re.I)

def parse_ts(s:str):
    try:
        return datetime.fromisoformat(s.replace(" ", "T"))
    except:
        return None

def latency_from_logs():
    """
    Cherche dans logs/bot.log :
    - Paires d’événements horodatés (début/fin) OU lignes "LATtotal = 8.7"
    - Calcule P50/P95/avg (en secondes)
    """
    logf = LOGS / "bot.log"
    if not logf.exists():
        return {"found_file": False, "events": [], "p50": None, "p95": None, "avg": None}

    lines = logf.read_text(errors="ignore").splitlines()
    lines = lines[-5000:]  # fenêtre raisonnable
    durations = []

    # 1) Essayer à partir de lignes de latence explicites
    for ln in lines:
        m = LAT_RGX.search(ln)
        if m:
            try:
                val = float(m.group("val"))
                # suppose secondes si <60, sinon ce sont des ms
                durations.append(val if val < 60 else val/1000.0)
            except: pass

    # 2) Sinon, approx via première/dernière horodatée d’un “cycle”
    # Heuristique: un "cycle" contient OCR / GPT / TTS
    if len(durations) < 5:
        window = []
        for ln in lines:
            U = ln.upper()
            if any(k in U for k in ("REQUEST", "OCR", "GPT", "TTS", "AUDIO_SENT", "REPLY_SENT", "PIPELINE")):
                mt = TS_RGX.search(ln)
                if mt:
                    window.append(parse_ts(mt.group("ts")))
                    if len(window) >= 2 and window[0] and window[-1]:
                        d = (window[-1] - window[0]).total_seconds()
                        if 0.1 <= d <= 120:
                            durations.append(d)
                        window = []  # reset simple

    if not durations:
        return {"found_file": True, "events": lines[-30:], "p50": None, "p95": None, "avg": None}

    durations = sorted(durations)
    p50 = statistics.median(durations)
    # p95 manuel
    idx95 = max(0, int(round(0.95*(len(durations)-1))))
    p95 = durations[idx95]
    avg = sum(durations)/len(durations)
    return {"found_file": True, "count": len(durations), "p50": p50, "p95": p95, "avg": avg}

# --------- Healthcheck (optionnel) ------------------------------------------
def try_health(urls=("http://127.0.0.1:5000/health","http://localhost:5000/health")):
    try:
        import urllib.request
        for u in urls:
            try:
                with urllib.request.urlopen(u, timeout=2) as r:
                    return {"url": u, "code": r.getcode(), "ok": r.getcode()==200}
            except: pass
    except: pass
    return {"url": None, "code": None, "ok": False}

# --------- Main --------------------------------------------------------------
def main():
    ensure_dirs()
    summary = {"generated_at": datetime.now().isoformat(timespec="seconds"), "checks": {}}

    # RAG eval
    gold = DATA / "eval" / "gold.jsonl"
    if (ROOT / "scripts" / "rag_eval.py").exists() and gold.exists():
        r = run(f"{sys.executable} scripts/rag_eval.py --gold {gold}")
        metrics = parse_rag_metrics((r.get("out") or "") + "\n" + (r.get("err") or ""))
        summary["checks"]["rag_eval"] = {**r, **metrics}
    else:
        summary["checks"]["rag_eval"] = {"ok": False, "err": "scripts/rag_eval.py ou data/eval/gold.jsonl manquant"}

    # Corpus
    mlen, mnote = manifest_len_and_errors()
    pdfc = count_pdfs()
    summary["checks"]["manifest"] = {"length": mlen, "note": mnote}
    summary["checks"]["pdfs"] = {"count": pdfc}

    # Prompts/langues
    summary["checks"]["languages"] = detect_languages_in_prompts()

    # Bot latence
    summary["checks"]["latency"] = latency_from_logs()

    # Health
    summary["checks"]["health"] = try_health()

    # Statut synthèse
    s = []
    rag = summary["checks"]["rag_eval"]
    cov, hit = rag.get("coverage@5"), rag.get("hit@1")
    if rag.get("ok"):
        if cov is not None and hit is not None:
            s.append(f"RAG coverage@5={cov:.2f} | hit@1={hit:.2f}")
        else:
            s.append("RAG eval OK (métriques non extraites)")
    else:
        s.append("RAG eval KO")

    if mlen is not None:
        s.append(f"Manifest={mlen} docs")
    else:
        s.append(f"Manifest=KO ({mnote or '—'})")
    s.append(f"PDFs={pdfc}")

    lat = summary["checks"]["latency"]
    if lat.get("p95") is not None:
        s.append(f"Latence P50={lat['p50']:.1f}s | P95={lat['p95']:.1f}s | avg={lat['avg']:.1f}s")
    else:
        s.append("Latence non estimable (logs)")

    langs = summary["checks"]["languages"]
    s.append(f"Langues détectées prompts: {', '.join(langs) if langs else '—'}")

    summary["status"] = s

    # Exports
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    md = []
    md.append(f"# Rapport d’audit — Quick Wins (généré {summary['generated_at']})\n")
    md.append("## Synthèse")
    for line in s: md.append(f"- {line}")
    md.append("\n## Détails")

    md.append("\n### RAG – Évaluation")
    md.append(f"- Statut: {'OK' if rag.get('ok') else 'KO'}")
    md.append(f"- coverage@5: {rag.get('coverage@5')}")
    md.append(f"- hit@1: {rag.get('hit@1')}")
    if rag.get("out"):
        md.append("<details><summary>Sortie</summary>\n\n```\n"+rag["out"].strip()+"\n```\n</details>")
    if rag.get("err"):
        md.append("<details><summary>Erreurs</summary>\n\n```\n"+rag["err"].strip()+"\n```\n</details>")

    md.append("\n### Corpus")
    md.append(f"- PDFs détectés: **{pdfc}**")
    md.append(f"- manifest.json: **{mlen if mlen is not None else '—'}** {'('+mnote+')' if mnote else ''}")

    md.append("\n### Prompts & Langues")
    md.append(f"- {', '.join(langs) if langs else 'Aucun motif détecté'}")

    L = summary["checks"]["latency"]
    md.append("\n### Latence (à partir des logs)")
    if L.get("p95") is not None:
        md.append(f"- N={L.get('count')} échantillons — P50={L['p50']:.1f}s, P95={L['p95']:.1f}s, Moyenne={L['avg']:.1f}s")
    else:
        md.append("- Non estimable (timestamps/indicateurs manquants)")
    if L.get("found_file"):
        md.append("<details><summary>Indices (logs récents)</summary>\n\n```\n" + "\n".join([str(x) for x in (L.get('events') or [])][-15:]) + "\n```\n</details>")
    else:
        md.append("- Fichier logs/bot.log introuvable")

    H = summary["checks"]["health"]
    md.append("\n### Healthcheck")
    md.append(f"- URL: {H.get('url') or '—'} — Statut: {'OK' if H.get('ok') else 'KO'}")

    OUT_MD.write_text("\n".join(md)+"\n", encoding="utf-8")

    print(f"[OK] Rapport Markdown: {OUT_MD}")
    print(f"[OK] Rapport JSON:     {OUT_JSON}")

if __name__ == "__main__":
    main()
