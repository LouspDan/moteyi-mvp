#!/usr/bin/env python3
"""
eval_report.py — B.7 SAFE
- Lit artifacts/summary.json et artifacts/metrics.csv (si dispo)
- Produit artifacts/rag_eval_report.html robuste (même si fichiers manquants/vides)
- Utilise string.Template pour éviter les conflits avec les {} du CSS
"""
import csv, json, os
from string import Template

HTML = Template("""<!doctype html>
<html lang="fr"><meta charset="utf-8">
<title>Moteyi — RAG Eval Report</title>
<style>
body{font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;margin:24px;color:#111}
h1{font-size:22px;margin-bottom:8px}
h2{font-size:18px;margin-top:24px}
table{border-collapse:collapse;width:100%;margin-top:8px}
th,td{border:1px solid #ddd;padding:8px;font-size:14px}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;background:#eef}
.kpi{display:flex;gap:12px;margin:12px 0;flex-wrap:wrap}
.kpi div{background:#f7f7f7;border-radius:8px;padding:8px 12px;min-width:180px}
.bar{height:10px;background:#e5e5e5;border-radius:5px;overflow:hidden}
.fill{height:10px;background:#6366f1}
.small{color:#666;font-size:12px}
.warn{background:#fff7ed;border:1px solid #fdba74;padding:8px 12px;border-radius:8px;margin:12px 0}
.ok{background:#ecfdf5;border:1px solid #34d399;padding:8px 12px;border-radius:8px;margin:12px 0}
</style>
<h1>Moteyi — Rapport d'évaluation RAG</h1>
<div class="small">Généré automatiquement</div>

$notices

<h2>KPIs globaux</h2>
<div class="kpi">
  <div>coverage@5: <b>${cov5}</b><div class="bar"><div class="fill" style="width:${cov5p}%;"></div></div></div>
  <div>hit@1: <b>${hit1}</b><div class="bar"><div class="fill" style="width:${hit1p}%;"></div></div></div>
  <div>mrr@5: <b>${mrr5}</b><div class="bar"><div class="fill" style="width:${mrr5p}%;"></div></div></div>
</div>

<h2>Détails agrégés</h2>
<table><thead><tr>
<th>Scope</th><th>Lang</th><th>Grade</th><th>Subject</th><th>Count</th><th>hit@1</th><th>coverage@5</th><th>mrr@5</th>
</tr></thead><tbody>
${rows}
</tbody></table>
</html>
""")

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def main():
    # 1) Résumé global
    summary_path = os.path.join("artifacts", "summary.json")
    cov5 = hit1 = mrr5 = 0.0
    notices = []

    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                g = (json.load(f) or {}).get("global") or {}
                cov5 = safe_float(g.get("coverage@5", 0))
                hit1 = safe_float(g.get("hit@1", 0))
                mrr5 = safe_float(g.get("mrr@5", 0))
        except Exception as e:
            notices.append(f"<div class='warn'>summary.json illisible ({e}). Valeurs globales par défaut à 0.</div>")
    else:
        notices.append("<div class='warn'>summary.json introuvable. Valeurs globales par défaut à 0.</div>")

    # 2) Détails agrégés (CSV)
    rows_html = []
    metrics_path = os.path.join("artifacts", "metrics.csv")
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                empty = True
                for r in reader:
                    empty = False
                    scope   = r.get("scope","")
                    lang    = r.get("lang","")
                    grade   = r.get("grade","")
                    subject = r.get("subject","")
                    count   = r.get("count","0")
                    v_hit1  = r.get("hit@1","0")
                    v_cov5  = r.get("coverage@5","0")
                    v_mrr5  = r.get("mrr@5","0")
                    rows_html.append(
                        f"<tr><td>{scope}</td><td>{lang}</td><td>{grade}</td>"
                        f"<td>{subject}</td><td>{count}</td>"
                        f"<td>{v_hit1}</td><td>{v_cov5}</td><td>{v_mrr5}</td></tr>"
                    )
                if empty:
                    notices.append("<div class='warn'>metrics.csv est vide. Aucun détail à afficher.</div>")
        except Exception as e:
            notices.append(f"<div class='warn'>metrics.csv illisible ({e}). Aucun détail à afficher.</div>")
    else:
        notices.append("<div class='warn'>metrics.csv introuvable. Lance d'abord rag_eval.py.</div>")

    if not rows_html:
        rows_html.append("<tr><td colspan='8'>Aucune métrique disponible pour le moment.</td></tr>")

    html = HTML.substitute(
        notices="\n".join(notices) if notices else "<div class='ok'>Artefacts chargés avec succès.</div>",
        cov5=f"{cov5:.3f}", hit1=f"{hit1:.3f}", mrr5=f"{mrr5:.3f}",
        cov5p=f"{cov5*100:.2f}", hit1p=f"{hit1*100:.2f}", mrr5p=f"{mrr5*100:.2f}",
        rows="\n".join(rows_html),
    )

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "rag_eval_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[eval_report] OK → {out_path}")

if __name__ == "__main__":
    main()
