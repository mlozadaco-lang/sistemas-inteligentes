# -*- coding: utf-8 -*-
# Export a JSON/HTML (+PDF si reportlab está disponible)

import json
import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
    from reportlab.lib.units import cm
    REPORTLAB = True
except Exception:
    REPORTLAB = False

def export_all(result: dict) -> list[str]:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = []

    jname = f"resultado_vocacional_{ts}.json"
    with open(jname, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    out.append(jname)

    hname = f"perfil_vocacional_{ts}.html"
    with open(hname, "w", encoding="utf-8") as f:
        f.write(build_html(result))
    out.append(hname)

    if REPORTLAB:
        pname = f"perfil_vocacional_{ts}.pdf"
        build_pdf(pname, result)
        out.append(pname)

    return out

def build_html(lr: dict) -> str:
    def li(items): return "".join([f"<li>{x}</li>" for x in items])
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Perfil Vocacional</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;margin:40px;color:#111}}
h1{{margin-bottom:4px}}.sub{{color:#666}}.card{{border:1px solid #e5e7eb;padding:16px;border-radius:12px;margin:12px 0}}
</style></head><body>
<h1>Perfil de Orientación Vocacional</h1>
<div class="sub">Fecha: {lr['timestamp']}</div>
<div class="card"><b>Área principal:</b> {lr['area']}<br><b>Profesión sugerida:</b> {lr.get('profession','')}</div>
<div class="card"><b>Top 3 áreas:</b><ol>{li(lr.get('top3',[]))}</ol></div>
<div class="card"><b>Puntajes normalizados:</b><ul>{li([f"{k}: {v:.2f}" for k,v in lr.get('normalized',{}).items()])}</ul></div>
<p class="sub">Siguiente paso: 1–2 cursos intro / club escolar / mini-proyecto.</p>
</body></html>"""

def build_pdf(pdf_name: str, lr: dict):
    doc = SimpleDocTemplate(pdf_name, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elems = [
        Paragraph("Perfil de Orientación Vocacional", styles['Title']),
        Paragraph(f"Fecha: {lr['timestamp']}", styles['Normal']),
        Paragraph(f"Área principal: <b>{lr['area']}</b>", styles['Heading2']),
    ]
    if lr.get("profession"):
        elems.append(Paragraph(f"Profesión sugerida: <b>{lr['profession']}</b>", styles['Normal']))
    elems.append(Paragraph("Top 3 áreas", styles['Heading2']))
    for a in lr.get("top3", []):
        elems.append(Paragraph(f"• {a}", styles['Normal']))
    elems.append(Paragraph("Puntajes normalizados", styles['Heading2']))
    items = [ListItem(Paragraph(f"{k}: {v:.2f}", styles['Normal']), leftIndent=12)
             for k, v in lr.get("normalized", {}).items()]
    elems.append(ListFlowable(items, bulletType='bullet'))
    doc.build(elems)
