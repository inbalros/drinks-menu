"""Create the site's QR code images in qr/ and verify that they scan.

Usage:
    pip install segno pillow opencv-python-headless
    python tools/make_qr_images.py

Outputs (in qr/):
    drinks-menu-qr.png              high-resolution QR for printing
    drinks-menu-qr.svg              vector QR (sharp at any size)
    whatToChoose-with-real-qr.png   the poster with its placeholder QR replaced

Every output is decoded with OpenCV (also after shrinking and blurring) and must
return exactly URL, otherwise the script fails.
"""
import pathlib
import sys

import cv2
import numpy as np
import segno
from PIL import Image, ImageFilter

URL = "https://inbalros.github.io/drinks-menu/"

ROOT = pathlib.Path(__file__).resolve().parent.parent
QR_DIR = ROOT / "qr"
POSTER_IN = QR_DIR / "whatToChoose.png"
POSTER_OUT = QR_DIR / "whatToChoose-with-real-qr.png"
QR_PNG = QR_DIR / "drinks-menu-qr.png"
QR_SVG = QR_DIR / "drinks-menu-qr.svg"

# Inner white area of the poster's gold-framed QR box (measured from the image)
BOX_LEFT, BOX_TOP, BOX_RIGHT, BOX_BOTTOM = 408, 900, 713, 1188
CORNER_SAFE_INSET = 6        # keep clear of the box's rounded gold corners
MODULE_PX = 7                # whole pixels per module keeps every module crisp

# Version 4 (33x33 modules) with error correction Q: recovers ~25% damage
qr = segno.make(URL, error="q", micro=False, boost_error=False)
print(f"QR version {qr.version}, error level {qr.error}, {qr.symbol_size(border=0)[0]} modules")

# ---- standalone files ----
qr.save(str(QR_PNG), kind="png", scale=30, border=4, dark="#000000", light="#ffffff")
qr.save(str(QR_SVG), kind="svg", scale=10, border=4, dark="#000000", light="#ffffff")


def qr_image(module_px, border):
    """QR as a PIL image built module by module (no resampling blur)."""
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    size = (n + 2 * border) * module_px
    img = Image.new("RGB", (size, size), "white")
    px = img.load()
    for r, row in enumerate(matrix):
        for c, dark in enumerate(row):
            if dark:
                x0 = (c + border) * module_px
                y0 = (r + border) * module_px
                for y in range(y0, y0 + module_px):
                    for x in range(x0, x0 + module_px):
                        px[x, y] = (0, 0, 0)
    return img


# ---- poster ----
poster = Image.open(POSTER_IN).convert("RGB")
# 1. wipe the placeholder: paint the box interior white, staying inside the rounded border
wipe = Image.new("RGB", (BOX_RIGHT - BOX_LEFT + 1 - 2 * CORNER_SAFE_INSET,
                         BOX_BOTTOM - BOX_TOP + 1 - 2 * CORNER_SAFE_INSET), "white")
poster.paste(wipe, (BOX_LEFT + CORNER_SAFE_INSET, BOX_TOP + CORNER_SAFE_INSET))
# also clear the straight edges between the corners (the border's inner anti-aliasing stays)
edge_h = Image.new("RGB", (BOX_RIGHT - BOX_LEFT + 1 - 2 * 16, BOX_BOTTOM - BOX_TOP + 1), "white")
poster.paste(edge_h, (BOX_LEFT + 16, BOX_TOP))
edge_v = Image.new("RGB", (BOX_RIGHT - BOX_LEFT + 1, BOX_BOTTOM - BOX_TOP + 1 - 2 * 16), "white")
poster.paste(edge_v, (BOX_LEFT, BOX_TOP + 16))

# 2. center the real code (no border: the white box itself is the quiet zone)
code = qr_image(MODULE_PX, border=0)
cx = (BOX_LEFT + BOX_RIGHT + 1) // 2
cy = (BOX_TOP + BOX_BOTTOM + 1) // 2
x0, y0 = cx - code.width // 2, cy - code.height // 2
poster.paste(code, (x0, y0))
quiet_x = min(x0 - BOX_LEFT, BOX_RIGHT - (x0 + code.width - 1)) / MODULE_PX
quiet_y = min(y0 - BOX_TOP, BOX_BOTTOM - (y0 + code.height - 1)) / MODULE_PX
print(f"poster QR {code.width}px at ({x0},{y0}); quiet zone {quiet_x:.1f} x {quiet_y:.1f} modules")
assert min(quiet_x, quiet_y) >= 4, "quiet zone below the 4-module standard"
poster.save(POSTER_OUT, optimize=True)


# ---- verification ----
detector = cv2.QRCodeDetector()


def decode(pil_img):
    arr = cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)
    data, _, _ = detector.detectAndDecode(arr)
    return data


checks = {
    "drinks-menu-qr.png": Image.open(QR_PNG),
    "poster full size": poster,
    "poster at 50%": poster.resize((poster.width // 2, poster.height // 2), Image.LANCZOS),
    "poster blurred": poster.filter(ImageFilter.GaussianBlur(1.5)),
    "poster QR crop": poster.crop((BOX_LEFT - 20, BOX_TOP - 20, BOX_RIGHT + 20, BOX_BOTTOM + 20)),
}
ok = True
for name, img in checks.items():
    got = decode(img)
    good = got == URL
    ok &= good
    print(f"{'OK  ' if good else 'FAIL'} {name}: {got!r}")
if not ok:
    sys.exit("QR verification failed")
print("All QR images decode to", URL)
