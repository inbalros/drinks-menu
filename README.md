# drinks-menu

**Pour Decisions**: the cocktail die for Inbal & Alon's wedding bar (14.12.2026).

Guests scan a QR code at the bar, roll a 3D die, and get a randomly chosen cocktail with its ingredients.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole site: inline CSS, JS and embedded fonts. No build step, no backend. |
| `sw.js` | Service worker. Caches the page after the first visit so it opens instantly and works offline. |
| `sign.html` | Printable A5 sign for the bar with the QR code. Open in a browser and print (A5, no margins, background graphics on). |
| `tools/make_qr.py` | Regenerates the QR code in `sign.html` (`pip install segno`, then `python tools/make_qr.py [URL]`). |
| `qr/` | QR code for the site (`drinks-menu-qr.png` for print, `drinks-menu-qr.svg` vector) and the poster `whatToChoose-with-real-qr.png`. |
| `tools/make_qr_images.py` | Rebuilds everything in `qr/` and verifies each image decodes to the site URL (`pip install segno pillow opencv-python-headless`). |
| `tools/embed_fonts.py` | Re-embeds the fonts subset to the page's characters (`pip install fonttools brotli`, then `python tools/embed_fonts.py`). |

## Features

- Rolls use `crypto.getRandomValues()` with rejection sampling (unbiased). Odds are set by each drink's `weight` in `index.html`: Non-Alcoholic 1 (about 9%), each cocktail 2 (about 18%).
- Optional synthesized sound (rattle, bounces, glass clink), off by default, toggled with the speaker button.
- "זה שלי!" opens an order ticket guests can show at the bar.
- Every few rolls a toast invites guests to raise a glass to the couple.
- Respects reduced-motion settings and keeps its colors in phone dark mode.

## After editing

1. If you changed any text in `index.html`, run `python tools/embed_fonts.py` so new characters are in the fonts.
2. Bump `VERSION` in `sw.js` so guests' phones fetch the new page.

## Hosting

GitHub Pages from the `main` branch, root folder: https://inbalros.github.io/drinks-menu/
