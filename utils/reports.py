from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import date
import os
def make_monthly_report(username: str, content: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{username or 'user'}_monthly_report.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    c.setTitle("幸運99｜每月運勢報告")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, h-2.5*cm, "幸運99｜每月運勢報告")
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, h-3.5*cm, f"用戶：{username or '訪客'}")
    c.drawString(2*cm, h-4.2*cm, f"月份：{date.today().strftime('%Y-%m')}")
    text = c.beginText(2*cm, h-5.2*cm)
    text.setFont("Helvetica", 12)
    for line in content.split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
    return path
