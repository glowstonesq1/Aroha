"""Regenerate _headers (Cloudflare Pages) with a CSP hash for the inline app script.
Run after every change to index.html:  python3 tools/build_headers.py
shortcut: inline script + hash keeps the single-file build; when the app moves to Vite, drop the hash and use script-src 'self'."""
import base64, hashlib, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
html = (root / 'index.html').read_text(encoding='utf-8')
scripts = [m.group(1) for m in re.finditer(r'<script>(.*?)</script>', html, re.S)]
assert len(scripts) == 1, 'expected exactly one inline executable script'
h = base64.b64encode(hashlib.sha256(scripts[0].encode('utf-8')).digest()).decode()

csp = "; ".join([
    "default-src 'self'",
    f"script-src 'self' 'sha256-{h}'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src https://fonts.gstatic.com",
    "img-src 'self' data: blob:",
    "media-src 'self' data: blob:",
    "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com",
    "manifest-src 'self'",
    "worker-src 'self'",
    "frame-ancestors 'none'",
    "base-uri 'none'",
    "form-action 'self'",
    "object-src 'none'",
    "upgrade-insecure-requests",
])
(root / '_headers').write_text(f"""/*
  Content-Security-Policy: {csp}
  Permissions-Policy: camera=(self), microphone=(self), geolocation=(), payment=(), usb=()
  Referrer-Policy: no-referrer
  X-Content-Type-Options: nosniff
  Cross-Origin-Opener-Policy: same-origin
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/
  Cache-Control: no-cache

/index.html
  Cache-Control: no-cache

/sw.js
  Cache-Control: no-cache

/manifest.webmanifest
  Content-Type: application/manifest+json
""", encoding='utf-8')
print('wrote _headers, script hash sha256-' + h)
