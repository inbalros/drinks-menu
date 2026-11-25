"""Regenerate the QR code inside sign.html.

Usage:
    pip install segno
    python tools/make_qr.py [URL]

The QR SVG is written between the <!-- QR:START --> and <!-- QR:END --> markers,
and the printed URL text between <!-- URL:START --> and <!-- URL:END -->.
"""
import pathlib
import re
import sys

import segno

DEFAULT_URL = "https://inbalros.github.io/drinks-menu/"

url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
sign = pathlib.Path(__file__).resolve().parent.parent / "sign.html"

qr = segno.make(url, error="q", micro=False)
svg = qr.svg_inline(scale=1, border=0, dark="#241c2e", light=None, svgclass="qr", lineclass=None, omitsize=True)

html = sign.read_text(encoding="utf-8")
html = re.sub(r"<!-- QR:START -->.*?<!-- QR:END -->",
              lambda m: "<!-- QR:START -->" + svg + "<!-- QR:END -->", html, flags=re.S)
shown = url.replace("https://", "").rstrip("/")
html = re.sub(r"<!-- URL:START -->.*?<!-- URL:END -->",
              lambda m: "<!-- URL:START -->" + shown + "<!-- URL:END -->", html, flags=re.S)
sign.write_text(html, encoding="utf-8")
print("QR updated for", url)
