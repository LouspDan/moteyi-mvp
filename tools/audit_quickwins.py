#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_quickwins.py — Audit non intrusif du repo Moteyi/Eteyelo
- Corpus: compte PDFs + longueur manifest
- RAG: lance rag_eval.py si présent, extrait coverage@5 / hit@1
- Prompts: détecte langues (dossiers/nommage)
- Logs: calcule latence P50/P95/Moyenne à partir de logs/bot.log
- Health: GET /health (localhost) si exposé
- Rapport: artifacts/<prefix>_YYYYMMDD_HHMMSS.{json,md}

Usage:
  python tools/audit_quickwins.py --output audit_report
  python tools/audit_quickwins.py --gold data/eval/gold.jsonl --health http://127.0.0.1:5000/health
"""
import argparse, json, os, re, shlex, statistics, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONF = ROOT / "config"
LOGS = ROOT / "logs"
ART  = ROOT / "artifacts"

TS_RGX = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")
LAT_RGX = re.compile(r"LAT(total|_ms|ency)\s*[:=]\s*(?P<val>\d+(\.\d+)?)", re.I)

def run(cmd: str, timeout: int = 240) -> Dict[str, Any]:
    try:
        p = subprocess.run(shlex.split(cmd), timeout=timeout, cwd=ROOT,
                          capture_output=True, text=True)
        return {"ok": p.returncode == 0, "out": p.stdout, "err": p.stderr, "code": p.returncode}
    except Exception as e:
        return {"ok": False, "out": "", "err": str(e), "code": -1}

def ensure_dirs():
    ART.mkdir(parents=True, exist_ok=True)

def count_pdfs(rag_seed_dir: Path) -> int:
    return len(list(rag_seed_dir.rglob("*.pdf")))

def manifest_len_and_note(manifest_path: Path) -> Tuple[Optional[int], Optional[str]]:
    if not manifest_path.exists():
        return None, "absent"
    try:
        obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(obj, list):
            return len(obj), None
        if isinstance(obj, dict) and "documents" in obj:
            return len(obj["documents"]), None
        return None, "format_inattendu"
    except Exception as e:
        return None, f"parse_error: {e}"

def detect_languages_in_prompts(prompts_dir: Path) -> List[str]:
    if not prompts_dir.exists():
        return []
    tags = ["fr", "francais", "français", "lingala", "swahili", "kikongo", "tshiluba", "en", "anglais"]
    langs = set()
    for p in prompts_dir.rglob("*"):
        n = p.name.lower()
        for t in tags:
            if t in n:
                langs.add(t)
    return sorted(langs)

def parse_ts(s: str):
    from datetime import datetime as dt
    try:
        return dt.fromisoformat(s.replace(" ", "T"))
    except:  # noqa: E722
        return None

def latency_from_logs(bot_log: Path) -> Dict[str, Any]:
    if not bot_log.exists():
        return {"found_file": False, "events": [], "p50": None, "p95": None, "avg": None, "count": 0}
    lines = bot_log.read_text(errors="ignore").splitlines()[-5000:]
    durations: List[float] = []

    # Métriques explicites: "LATtotal=9.8" ou "LATency: 875" (ms)
    for ln in lines:
        m = LAT_RGX.search(ln)
        if m:
            try:
                val = float(m.group("val"))
                durations.append(val if val < 60 else val/1000.0)
            except:  # noqa: E722
                pass

    # Heuristique si pas assez d'échantillons: fenêtre OCR→GPT→TTS
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
                        window = []

    if not durations:
        return {"found_file": True, "events": lines[-30:], "p50": None, "p95": None, "avg": None, "count": 0}

    durations.sort()
    p50 = statistics.median(durations)
    idx95 = max(0, int(round(0.95*(len(durations)-1))))
    p95 = durations[idx95]
    avg = sum(durations)/len(durations)
    return {"found_file": True, "p50": p50, "p95": p95, "avg": avg, "count": len(durations)}

def parse_rag_metrics(stdout_err: str) -> Dict[str, Optional[float]]:
    """
    Extrait coverage@5 et hit@1 dans différents formats:
      coverage@5 = 100% | coverage@5: 1.00 | coverage@5 0.87
      hit@1 = 80%       | hit@1: 0.80    | hit@1 0.55
    """
    def pick(pattern: str) -> Optional[float]:
        m = re.search(pattern, stdout_err, re.I)
        if not m: return None
        v = m.group(1)
        try:
            return float(v.replace("%",""))/100.0 if "%" in v else float(v)
        except:  # noqa: E722
            return None
    return {
        "coverage@5": pick(r"coverage@?5\s*[:=]?\s*([0-9\.]+%?)"),
        "hit@1":      pick(r"hit@?1\s*[:=]?\s*([0-9\.]+%?)"),
    }

def http_health(url: str) -> Dict[str, Any]:
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=3) as r:
            return {"url": url, "code": r.getcode(), "ok": r.getcode() == 200}
    except Exception as e:
        return {"url": url, "code": None, "ok": False, "err": str(e)}

def build_markdown(summary: Dict[str, Any]) -> str:
    md = []
    md.append(f"# Rapport d’audit — Quick Wins (généré {summary['generated_at']})\n")
    md.append("## Synthèse")
    for line in summary["status"]:
        md.append(f"- {line}")
    md.append("\n## Détails")

    rag = summary["checks"]["rag_eval"]
    md.append("\n### RAG – Évaluation")
    md.append(f"- Statut: {'OK' if rag.get('ok') else 'KO'}")
    md.append(f"- coverage@5: {rag.get('coverage@5')}")
    md.append(f"- hit@1: {rag.get('hit@1')}")
    if rag.get("out"):
        md.append("<details><summary>Sortie</summary>\n\n```\n"+rag["out"].strip()+"\n```\n</details>")
    if rag.get("err"):
        md.append("<details><summary>Erreurs</summary>\n\n```\n"+rag["err"].strip()+"\n```\n</details>")

    md.append("\n### Corpus")
    md.append(f"- PDFs détectés: **{summary['checks']['pdfs']['count']}**")
    m = summary["checks"]["manifest"]
    md.append(f"- manifest.json: **{m.get('length') if m.get('length') is not None else '—'}** {'('+m['note']+')' if m.get('note') else ''}")

    langs = summary["checks"]["languages"]
    md.append("\n### Prompts & Langues")
    md.append(f"- {', '.join(langs) if langs else 'Aucun motif détecté'}")

    L = summary["checks"]["latency"]
    md.append("\n### Latence (à partir des logs)")
    if L.get("p95") is not None:
        md.append(f"- N={L.get('count')} — P50={L['p50']:.1f}s | P95={L['p95']:.1f}s | Moyenne={L['avg']:.1f}s")
    else:
        md.append("- Non estimable (timestamps/indicateurs manquants)")
    if L.get("found_file") and L.get("events"):
        tail = L["events"][-15:] if isinstance(L["events"], list) else []
        if tail:
            md.append("<details><summary>Logs récents</summary>\n\n```\n" + "\n".join(str(x) for x in tail) + "\n```\n</details>")
    else:
        md.append("- Fichier logs/bot.log introuvable")

    H = summary["checks"]["health"]
    md.append("\n### Healthcheck")
    if H:
        ok = "OK" if H.get("ok") else "KO"
        md.append(f"- URL: {H.get('url') or '—'} — Statut: {ok} " + (f"(code {H.get('code')})" if H.get("code") else ""))
    return "\n".join(md) + "\n"

def main():
    parser = argparse.ArgumentParser(description="Audit non intrusif Moteyi/Eteyelo (Quick Wins)")
    parser.add_argument("--output", default="audit_report", help="Préfixe des fichiers de sortie dans artifacts/")
    parser.add_argument("--gold", default=str(DATA / "eval" / "gold.jsonl"), help="Chemin du jeu gold pour rag_eval.py")
    parser.add_argument("--rag-eval-cmd", default=f"{sys.executable} scripts/rag_eval.py --gold {{gold}}", help="Commande pour lancer l'éval RAG")
    parser.add_argument("--health", default="http://127.0.0.1:5000/health", help="URL healthcheck (optionnel)")
    parser.add_argument("--manifest", default=str(DATA / "index" / "manifest.json"))
    parser.add_argument("--rag-seed", default=str(DATA / "rag_seed"))
    parser.add_argument("--prompts", default=str(CONF / "prompts"))
    parser.add_argument("--bot-log", default=str(LOGS / "bot.log"))
    args = parser.parse_args()

    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = ART / f"{args.output}_{ts}.json"
    out_md   = ART / f"{args.output}_{ts}.md"

    summary: Dict[str, Any] = {"generated_at": datetime.now().isoformat(timespec="seconds"), "checks": {}}

    # RAG eval
    rag_eval_script = ROOT / "scripts" / "rag_eval.py"
    gold_file = Path(args.gold)
    if rag_eval_script.exists() and gold_file.exists():
        cmd = args.rag_eval_cmd.replace("{gold}", str(gold_file))
        r = run(cmd)
        metrics = parse_rag_metrics((r.get("out") or "") + "\n" + (r.get("err") or ""))
        summary["checks"]["rag_eval"] = {**r, **metrics}
    else:
        summary["checks"]["rag_eval"] = {"ok": False, "err": f"rag_eval.py ({rag_eval_script.exists()}) ou gold ({gold_file.exists()}) introuvable"}

    # Corpus
    mlen, mnote = manifest_len_and_note(Path(args.manifest))
    pdf_count = count_pdfs(Path(args.rag_seed))
    summary["checks"]["manifest"] = {"length": mlen, "note": mnote}
    summary["checks"]["pdfs"] = {"count": pdf_count}

    # Langues
    summary["checks"]["languages"] = detect_languages_in_prompts(Path(args.prompts))

    # Latence
    summary["checks"]["latency"] = latency_from_logs(Path(args.bot_log))

    # Health
    summary["checks"]["health"] = http_health(args.health) if args.health else {}

    # Synthèse
    s = []
    rag = summary["checks"]["rag_eval"]
    cov, hit = rag.get("coverage@5"), rag.get("hit@1")
    if rag.get("ok"):
        s.append(f"RAG coverage@5={cov:.2f} | hit@1={hit:.2f}" if cov is not None and hit is not None else "RAG eval OK (métriques non extraites)")
    else:
        s.append("RAG eval KO")

    s.append(f"Corpus: PDFs={pdf_count} | manifest={mlen if mlen is not None else '—'}{(' ('+mnote+')' if mnote else '')}")
    lat = summary["checks"]["latency"]
    s.append(f"Latence: P50={lat['p50']:.1f}s | P95={lat['p95']:.1f}s | Moyenne={lat['avg']:.1f}s" if lat.get("p95") is not None else "Latence: non estimable (logs)")
    langs = summary["checks"]["languages"]
    s.append(f"Prompts/langues: {', '.join(langs) if langs else '—'}")
    H = summary["checks"]["health"]
    if H:
        s.append(f"Health: {'OK' if H.get('ok') else 'KO'}")

    summary["status"] = s

    # Ecritures
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(build_markdown(summary), encoding="utf-8")

    print(f"[OK] Rapport JSON: {out_json}")
    print(f"[OK] Rapport MD:   {out_md}")

if __name__ == "__main__":
    main()
