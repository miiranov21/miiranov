// Офлайн-режим: сайт открывается без интернета, свежая версия подтягивается при каждом запуске с сетью.
const CACHE = "moy-den-2026.11.08-11";
const ASSETS = ["./", "index.html", "config.js", "course-en.js", "course-az.js", "foods-ru.js", "fin-lessons.js", "books-ru.js", "program-en.js", "program-en-m1.js", "program-en-m2.js", "program-en-m3.js", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;  // облако и шрифты идут напрямую
  // всегда спрашиваем сервер о свежей версии (без 10-минутного кеша браузера), при отсутствии сети — копия из кеша
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match("index.html"))));
});
