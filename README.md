# drinks-menu

**Pour Decisions**: the cocktail die for Inbal & Alon's wedding bar (14.12.2026).

Guests scan a QR code at the bar, roll a 3D die, and get a randomly chosen cocktail with its ingredients.

- Single self-contained static page: `index.html` (inline CSS and JS, fonts from Google Fonts).
- No build step and no backend. Open `index.html` in a browser, or serve the folder with any static host (for example GitHub Pages from the `main` branch).
- Rolls use `crypto.getRandomValues()` with rejection sampling, so all six drinks are equally likely.
