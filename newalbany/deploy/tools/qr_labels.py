"""QR label sheet generator for any MDI app.

Usage:
  python qr_labels.py --url "https://apps.powerapps.com/play/e/<env>/a/<appId>?tenantId=<tid>" \
      --title "TROUBLESHOOT" --lines 205,209 --equip Labeler,Capper,Filler --out ts_qr_labels.pdf
  # or a CSV with columns: line,equip,asset,label  (asset/label optional)
  python qr_labels.py --url ... --csv stations.csv --out labels.pdf

Each label = QR (url + &line=..&equip=..&asset=..) + big line/equipment text, Voyant colours.
Prints 2 x 4 labels per US Letter page (3.75" x 2.4"), cut lines included.
"""
import argparse, csv, io, urllib.parse
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

DARK = (7/255, 39/255, 45/255); TEAL = (0, 178/255, 169/255); GREY = (117/255, 120/255, 123/255)

def link(base, **params):
    p = {k: v for k, v in params.items() if v}
    sep = "&" if "?" in base else "?"
    return base + (sep + urllib.parse.urlencode(p) if p else "")

def qr_img(data):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=1)
    q.add_data(data); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color="black", back_color="white").save(buf, "PNG"); buf.seek(0)
    return ImageReader(buf)

def build(rows, base, title, out):
    c = canvas.Canvas(out, pagesize=letter)
    W, H = letter; lw, lh = 3.75 * inch, 2.4 * inch; mx = (W - 2 * lw) / 2; my = (H - 4 * lh) / 2
    for i, r in enumerate(rows):
        if i and i % 8 == 0: c.showPage()
        col, row = i % 2, (i % 8) // 2
        x, y = mx + col * lw, H - my - (row + 1) * lh
        c.setStrokeColorRGB(*GREY); c.setDash(2, 3); c.rect(x, y, lw, lh); c.setDash()
        url = link(base, line=r.get("line"), equip=r.get("equip"), asset=r.get("asset"))
        q = 1.9 * inch
        c.drawImage(qr_img(url), x + 0.2 * inch, y + (lh - q) / 2, q, q)
        tx = x + 0.2 * inch + q + 0.15 * inch
        c.setFillColorRGB(*DARK); c.rect(tx - 0.05 * inch, y + lh - 0.55 * inch, lw - (tx - x) - 0.1 * inch, 0.4 * inch, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1); c.setFont("Helvetica-Bold", 11); c.drawString(tx, y + lh - 0.42 * inch, title)
        c.setFillColorRGB(*DARK); c.setFont("Helvetica-Bold", 30); c.drawString(tx, y + lh - 1.05 * inch, str(r.get("line", "")))
        c.setFont("Helvetica-Bold", 14); c.drawString(tx, y + lh - 1.35 * inch, r.get("label") or r.get("equip", ""))
        if r.get("asset"):
            c.setFont("Helvetica", 9); c.setFillColorRGB(*GREY); c.drawString(tx, y + lh - 1.55 * inch, r["asset"])
        c.setFont("Helvetica", 7); c.setFillColorRGB(*TEAL); c.drawString(tx, y + 0.2 * inch, "Scan with phone camera")
    c.save()

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--url", required=True); a.add_argument("--title", default="TROUBLESHOOT")
    a.add_argument("--lines"); a.add_argument("--equip"); a.add_argument("--csv"); a.add_argument("--out", default="qr_labels.pdf")
    o = a.parse_args()
    if o.csv:
        rows = list(csv.DictReader(open(o.csv, newline="")))
    else:
        rows = [{"line": l.strip(), "equip": e.strip()} for l in o.lines.split(",") for e in o.equip.split(",")]
    build(rows, o.url, o.title, o.out); print(f"{len(rows)} labels -> {o.out}")
