/* Aroha service worker. Bump VERSION on every release so old caches are dropped. */
const VERSION = '0.4.0';
const CACHE = 'aroha-' + VERSION;
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/maskable-512.png', './icons/apple-touch-icon.png',
  './fonts/caveat-normal-latin-706a1c.woff2', './fonts/caveat-normal-latin-ext-32f761.woff2', './fonts/crimson-text-italic-latin-1ac6ef.woff2', './fonts/crimson-text-italic-latin-ext-a0f6dd.woff2', './fonts/crimson-text-normal-latin-1f852a.woff2', './fonts/crimson-text-normal-latin-38dc48.woff2', './fonts/crimson-text-normal-latin-ext-c63ee1.woff2', './fonts/crimson-text-normal-latin-ext-e7ca5f.woff2', './fonts/roboto-normal-latin-0f7fcd.woff2', './fonts/roboto-normal-latin-ext-f0106b.woff2'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('aroha-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Pages: network first so releases land, cached shell when offline.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put('./index.html', copy)); return res; })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // Same-origin assets (fonts are self-hosted): stale while revalidate.
  if (url.origin === self.location.origin) {
    e.respondWith(
      caches.match(req).then((hit) => {
        const net = fetch(req).then((res) => {
          if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
          return res;
        }).catch(() => hit);
        return hit || net;
      })
    );
  }
});
