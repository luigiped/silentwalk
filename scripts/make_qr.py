#!/usr/bin/env python3
"""Genera i QR della landing in qr/:

  qr-silentwalk.svg / .png                 classico nero su bianco (massima leggibilità)
  qr-silentwalk-freespace.svg / .png       personalizzato: colori FreeSpace + logo al centro

Uso: python3 scripts/make_qr.py https://utente.github.io/silentwalk/
Richiede: pip install segno pillow

Il QR contiene SOLO l'URL: si può cambiare tutto il resto del sito senza ristamparlo.
"""
import base64
import io
import sys
from pathlib import Path

import segno
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo-freespace.png"
OUT = ROOT / "qr"

# Colori: fucsia e rosso FreeSpace scuriti quanto basta per un contrasto
# alto sul bianco (> 6:1), così i lettori li vedono come moduli "scuri".
DATA = "#A3105F"     # fucsia scuro (moduli dati)
EYE = "#B20F6C"      # fucsia (cornici dei mirini)
EYE_IN = "#B0101F"   # rosso locandina (centro dei mirini)
LIGHT = "#FFFFFF"
BORDER = 4           # quiet zone in moduli
# Mirini quasi squadrati: con angoli molto tondi alcuni lettori non li riconoscono.
EYE_R = (0.5, 0.35, 0.3)
LOGO_FRAC = 0.24     # diametro del logo rispetto al lato dell'area dati

url = sys.argv[1] if len(sys.argv) > 1 else None
if not url:
    sys.exit("Specifica l'URL, es. python3 scripts/make_qr.py https://utente.github.io/silentwalk/")
OUT.mkdir(exist_ok=True)

qr = segno.make(url, error="h", micro=False, boost_error=False)
matrix = [list(row) for row in qr.matrix]
n = len(matrix)

# ---------- 1) QR classico ----------
scale = -(-2000 // (n + 2 * BORDER))
qr.save(OUT / "qr-silentwalk.svg", scale=10, border=BORDER, dark="#000", light="#fff")
qr.save(OUT / "qr-silentwalk.png", scale=scale, border=BORDER, dark="#000", light="#fff")


# ---------- 2) QR personalizzato FreeSpace ----------
def in_finder(r, c):
    return (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)


finders = [(0, 0), (0, n - 7), (n - 7, 0)]
center = n / 2
logo_d = n * LOGO_FRAC              # diametro logo in moduli
clear_r = logo_d / 2 + 0.9          # area libera attorno al logo (alone bianco)


def covered(r, c):
    dy, dx = r + 0.5 - center, c + 0.5 - center
    return (dx * dx + dy * dy) ** 0.5 < clear_r


def modules():
    for r in range(n):
        for c in range(n):
            if matrix[r][c] and not in_finder(r, c) and not covered(r, c):
                yield r, c


# PNG
M = 56  # pixel per modulo
size = (n + 2 * BORDER) * M
img = Image.new("RGB", (size, size), LIGHT)
d = ImageDraw.Draw(img)
off = BORDER * M
for r, c in modules():
    x, y = off + c * M, off + r * M
    d.rounded_rectangle([x, y, x + M - 1, y + M - 1], radius=M * 0.22, fill=DATA)
for fr, fc in finders:
    x, y = off + fc * M, off + fr * M
    d.rounded_rectangle([x, y, x + 7 * M - 1, y + 7 * M - 1], radius=M * EYE_R[0], fill=EYE)
    d.rounded_rectangle([x + M, y + M, x + 6 * M - 1, y + 6 * M - 1], radius=M * EYE_R[1], fill=LIGHT)
    d.rounded_rectangle([x + 2 * M, y + 2 * M, x + 5 * M - 1, y + 5 * M - 1], radius=M * EYE_R[2], fill=EYE_IN)
logo_px = round(logo_d * M)
logo = Image.open(LOGO).convert("RGBA").resize((logo_px, logo_px), Image.LANCZOS)
cx = cy = off + round(center * M)
img.paste(logo, (cx - logo_px // 2, cy - logo_px // 2), logo)
png_out = img.resize((2000, 2000), Image.LANCZOS) if size > 2000 else img
png_out.save(OUT / "qr-silentwalk-freespace.png", optimize=True)

# SVG (vettoriale per la stampa, logo incorporato come PNG ad alta risoluzione)
S = 10
tot = (n + 2 * BORDER) * S
o = BORDER * S
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tot} {tot}" width="{tot}" height="{tot}">',
         f'<rect width="{tot}" height="{tot}" fill="{LIGHT}"/>', f'<g fill="{DATA}">']
for r, c in modules():
    parts.append(f'<rect x="{o + c * S}" y="{o + r * S}" width="{S}" height="{S}" rx="{S * .22}"/>')
parts.append("</g>")
for fr, fc in finders:
    x, y = o + fc * S, o + fr * S
    parts.append(f'<rect x="{x}" y="{y}" width="{7 * S}" height="{7 * S}" rx="{S * EYE_R[0]}" fill="{EYE}"/>')
    parts.append(f'<rect x="{x + S}" y="{y + S}" width="{5 * S}" height="{5 * S}" rx="{S * EYE_R[1]}" fill="{LIGHT}"/>')
    parts.append(f'<rect x="{x + 2 * S}" y="{y + 2 * S}" width="{3 * S}" height="{3 * S}" rx="{S * EYE_R[2]}" fill="{EYE_IN}"/>')
buf = io.BytesIO()
Image.open(LOGO).convert("RGBA").resize((800, 800), Image.LANCZOS).save(buf, "PNG", optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
ls = logo_d * S
lx = o + center * S - ls / 2
parts.append(f'<image x="{lx}" y="{lx}" width="{ls}" height="{ls}" href="data:image/png;base64,{b64}"/>')
parts.append("</svg>")
(OUT / "qr-silentwalk-freespace.svg").write_text("".join(parts))

print(f"URL: {url}\nVersione {qr.version}, correzione {qr.error}, {n} moduli")
print("File: qr/qr-silentwalk.(svg|png), qr/qr-silentwalk-freespace.(svg|png)")
