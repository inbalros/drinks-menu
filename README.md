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
| `tools/embed_fonts.py` | Re-embeds the fonts subset to the page's characters (`pip install fonttools brotli`, then `python tools/embed_fonts.py`). |

## Features

- Fair rolls: `crypto.getRandomValues()` with rejection sampling, so all six drinks are equally likely.
- Optional synthesized sound (rattle, bounces, glass clink), off by default, toggled with the speaker button.
- "זה שלי!" opens an order ticket guests can show at the bar.
- Every few rolls a toast invites guests to raise a glass to the couple.
- Respects reduced-motion settings and keeps its colors in phone dark mode.

## After editing

1. If you changed any text in `index.html`, run `python tools/embed_fonts.py` so new characters are in the fonts.
2. Bump `VERSION` in `sw.js` so guests' phones fetch the new page.

## Hosting

GitHub Pages from the `main` branch, root folder: https://inbalros.github.io/drinks-menu/
