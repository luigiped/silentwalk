#!/usr/bin/env python3
"""Genera il QR della landing: SVG (stampa) + PNG ad alta risoluzione in qr/.

Uso: python3 scripts/make_qr.py https://utente.github.io/silentwalk/
Richiede: pip install segno
"""
import sys
from pathlib import Path

import segno

url = sys.argv[1] if len(sys.argv) > 1 else None
if not url:
    sys.exit("Specifica l'URL, es. python3 scripts/make_qr.py https://utente.github.io/silentwalk/")

out = Path(__file__).resolve().parent.parent / "qr"
out.mkdir(exist_ok=True)

qr = segno.make(url, error="h", micro=False, boost_error=False)
modules = qr.symbol_size(border=0)[0]
border = 4  # quiet zone minima
scale = -(-2000 // (modules + 2 * border))  # >= 2000 px

qr.save(out / "qr-silentwalk.svg", scale=10, border=border, dark="#000", light="#fff")
qr.save(out / "qr-silentwalk.png", scale=scale, border=border, dark="#000", light="#fff")
px = (modules + 2 * border) * scale
print(f"URL: {url}\nVersione {qr.version}, correzione {qr.error}, {modules} moduli, PNG {px}x{px}px")
