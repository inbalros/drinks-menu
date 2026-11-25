"""Embed the site's Google Fonts into index.html, subset to the characters the page uses.

Usage (after changing any text in index.html):
    pip install fonttools brotli
    python tools/embed_fonts.py

Fonts: Frank Ruhl Libre, Heebo, Playfair Display (SIL Open Font License).
"""
import base64, io, re, sys, urllib.request, pathlib
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
html_path = ROOT / "index.html"
CSS_URL = ("https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500..900"
           "&family=Heebo:wght@400..800&family=Playfair+Display:ital,wght@0,700..800;1,600..800&display=swap")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
css = urllib.request.urlopen(urllib.request.Request(CSS_URL, headers={"User-Agent": UA})).read().decode("utf-8")
html = html_path.read_text(encoding="utf-8")

# Characters the page can ever show: everything in the file + ASCII + typographic extras
chars = set(html)
chars |= set(chr(c) for c in range(0x20, 0x7F))
chars |= set(chr(c) for c in range(0x05D0, 0x05EB))  # whole Hebrew alphabet, so text edits never miss a letter
chars |= set("׳״־…–— ‑­·’‘“”₪")
text = "".join(sorted(c for c in chars if c >= " "))

blocks = re.findall(r"/\* (\w[\w-]*) \*/\s*@font-face \{(.*?)\}", css, flags=re.S)
want = {"hebrew", "latin"}
out = []
total = 0
for subset_name, body in blocks:
    if subset_name not in want:
        continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    style = re.search(r"font-style: (\w+)", body).group(1)
    weight = re.search(r"font-weight: ([\d ]+);", body).group(1)
    url = re.search(r"url\((https://[^)]+)\)", body).group(1)
    rng = re.search(r"unicode-range: ([^;]+);", body).group(1)
    data = urllib.request.urlopen(url).read()
    font = TTFont(io.BytesIO(data))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "rlig"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b = buf.getvalue()
    total += len(b)
    print(f"{fam:18} {style:6} {subset_name:7} {len(data)//1024:4}KB -> {len(b)//1024:3}KB")
    out.append(
        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
        "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s;}"
        % (fam, style, weight, base64.b64encode(b).decode(), rng)
    )
print("total", total // 1024, "KB binary")

style = '<style id="embedded-fonts">\n/* Google Fonts (OFL), subset to the characters this page uses and embedded so the page needs no font server. */\n' + "\n".join(out) + "\n</style>"

old = re.search(r'<link rel="preconnect" href="https://fonts.googleapis.com">\s*<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\s*<link rel="stylesheet" href="https://fonts.googleapis.com/css2[^"]*">', html)
if old:
    html = html[:old.start()] + style + html[old.end():]
else:
    html, n = re.subn(r'<style id="embedded-fonts">.*?</style>', lambda m: style, html, flags=re.S)
    assert n == 1, "no font block found"
html_path.write_text(html, encoding="utf-8")
print("written")
