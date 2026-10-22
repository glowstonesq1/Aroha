# Aroha v0.3.0

A self-care web app and installable PWA for young adults living with generalised anxiety. Single-file front end, no build step, no server, no third-party requests. All data lives in the user's browser.

## Run locally
```
python3 -m http.server 8080        # from this folder
open http://localhost:8080
```
Service worker and install only work on `https://` or `localhost`.

## Test
```
pip install playwright && playwright install chromium
python3 tests/smoke.py              # with the local server running
CHROMIUM_PATH=/path/to/chrome python3 tests/smoke.py   # reuse an installed Chromium
```
`Aroha.selfTest()` in the browser console runs the built-in checks (input validation, heart-rate maths). The smoke test calls it too.

## Deploy (Cloudflare Pages)
1. Run `python3 tools/build_headers.py` after every change to `index.html`. It writes `_headers` with a CSP hash for the inline script. If you skip it, the CSP blocks the app.
2. Push this folder to a repo and connect it to Cloudflare Pages. No build command; output directory is the root.
3. Once you have a domain, make `og:image` in `index.html` an absolute URL and add `<link rel="canonical">`.
4. Bump `APP_VERSION` in `index.html` and `VERSION` in `sw.js` together on every release.

## Files
| File | What it is |
|---|---|
| `index.html` | The whole app: CSS, views, router, data layer |
| `fonts/` | Self-hosted Crimson Text, Roboto and Caveat (OFL), see `fonts/README.md` |
| `manifest.webmanifest`, `sw.js`, `icons/` | PWA install, offline shell, home-screen shortcuts (SOS, Log, To-dos) |
| `_headers` | Security headers and CSP for Cloudflare Pages (generated) |
| `robots.txt`, `llms.txt`, `og-image.png` | Search, AI crawler and share-card basics |
| `docs/supabase-schema.sql` | Proposed tables with owner-only RLS for the backend phase |
| `tests/smoke.py` | End-to-end check of onboarding, logging, back button, SOS, app lock, deep links |

## Architecture
- **Data layer.** `db.read/db.write` (localStorage) plus `normalise()`, which validates everything loaded or imported before it can reach the DOM. To add a backend, replace `db` with API calls and keep `normalise()` as the client-side guard.
- **Router.** Hash routes with real history (`#home`, `#log`, `#todos`, `#sos`), so Android back and swipe-back work. `guard()` handles login, consent and onboarding.
- **Rendering.** String templates into `#app`. Every user string passes through `esc()`. Event delegation via `data-go`, `data-act`, `data-submit`, `data-input`.

## What changed in 0.3.0
- **Logout means something.** Sign-up stores a salted PBKDF2 hash of the password on the device; log-in checks it. Before, any email and password reopened the previous person's logs on a shared phone. Sign-up can't overwrite an existing device account, and no longer pre-fills the last user's name and email. "Forgot password?" offers a full wipe, since there is no server to reset against.
- **No silent data loss when storage fills.** A photo or voice note that doesn't fit is dropped with a message instead of making every later save fail. Voice notes are capped at 3 minutes at 32 kbps.
- **Intro.** The circles now start in the palette colours and merge into the cosmos logo, and land on the logo's real spacing. The full intro plays once per device; returning users get a ~2 s version.
- **SOS shortcut skips the intro** and opens straight away, also while the app lock is on (the lock screen already offered SOS).
- **Crisis language** in a log note or chat opens the helplines sheet. Nobody reads chats in this prototype.
- Self-hosted fonts (CSP tightened to `'self'`), centred tablet layout, legible feed tags, an empty state for memories.

## Privacy and safety decisions
- Consent screen before any data is collected, with an 18+ confirmation. India's DPDP Rules require verifiable parental consent for under-18s; the app does not support minors yet.
- Download, restore and delete-all in Account.
- Local password: the hash sits next to the data it protects, so this stops casual access only, not someone with the device and dev tools.
- Optional 4-digit app lock. This only stops casual access on a shared phone: the hash is in local storage and a 4-digit space is trivially brute-forced offline. SOS stays reachable while locked.
- Crisis lines are region-aware (India, US, Canada, UK, Ireland, Australia, New Zealand), with findahelpline.com for everyone else. Re-verify the numbers before each release.
- Weekly trends instead of streaks.

## Next steps for the Claude Code phase
1. Split into Vite modules (`views/`, `data/`, `ui/`), then drop the CSP hash for `script-src 'self'`.
2. Supabase auth (email OTP) and the schema in `docs/`, then sync with `db` behind the same interface. Keep offline-first: write locally, sync in the background.
3. Encrypt sensitive fields at rest and run a DPDP-aligned privacy notice and retention policy past someone qualified.
4. Push notifications for an opt-in gentle daily check-in.
5. Hindi and Marathi copy. The notice must be available in the user's language under DPDP.
6. Community needs moderation, reporting and a safeguarding escalation path before it goes live. It is sample content today.
7. Lighthouse and axe accessibility passes on real devices.
8. Move photos and voice notes to IndexedDB; localStorage caps the safe box at about 5 MB.
9. Articles and community posts carry named bylines (Dr. Nilambari Tendulkar, Tia Parekh, Monica). Confirm each person reviewed and agreed to the content before launch, or mark them as sample.
10. Gender step offers only male, female or skip. Consider a "another identity" option; it changes the design, so it needs a design decision.
