# Fonts

Self-hosted so Aroha makes no third-party requests and the first load works offline. Latin and Latin Extended subsets (WOFF2), downloaded from Google Fonts.

| Family | Use | Licence |
|---|---|---|
| Crimson Text (400, 400 italic, 600) | Headings, buttons | SIL Open Font License 1.1 |
| Roboto (variable, 400 to 800) | Body text | SIL Open Font License 1.1 |
| Caveat (variable, 500 to 600) | The "Aroha" wordmark | SIL Open Font License 1.1 |

Licence text: https://openfontlicense.org/open-font-license-official-text/

File names carry a short hash of the source URL, so a changed font gets a new name and the `immutable` cache header stays safe. If you swap a file, update the `@font-face` rules at the top of `index.html` and the `SHELL` list in `sw.js`.
