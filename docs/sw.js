// Офлайн-режим: сайт открывается без интернета, свежая версия подтягивается при каждом запуске с сетью.
const CACHE = "moy-den-2026.11.11-1";
const ASSETS = ["./", "index.html", "config.js", "course-en.js", "course-az.js", "foods-ru.js", "fin-lessons.js", "books-ru.js", "i18n.js", "program-en.js", "program-en-m1.js", "program-en-m2.js", "program-en-m3.js", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
// Страница на случай, когда нет ни сети, ни сохранённой копии: вместо ошибки Safari — понятный экран с кнопкой.
const OFFLINE = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Мой день</title>
<style>body{font-family:-apple-system,system-ui,sans-serif;background:#0f141d;color:#e8edf5;display:flex;min-height:100vh;margin:0;align-items:center;justify-content:center;text-align:center;padding:24px}
button{margin-top:18px;font-size:17px;font-weight:700;padding:12px 22px;border-radius:12px;border:0;background:#7d93ff;color:#fff}p{color:#9aa6b8;line-height:1.5}</style></head>
<body><div><h2>Нет связи с сайтом</h2><p>Не получилось загрузить приложение. Проверь интернет (иногда помогает Wi‑Fi или VPN) и попробуй ещё раз.<br>Твои записи на телефоне не пропали.</p>
<p>No connection. Check your internet and try again. Your data is safe.</p><button onclick="location.reload()">Попробовать ещё раз · Retry</button></div></body></html>`;
async function fromCache(req){
  try {
    const hit = await caches.match(req, { ignoreSearch: true });
    if (hit) return hit;
    if (req.mode === "navigate") return (await caches.match("index.html")) || (await caches.match("./")) || null;
  } catch (e) {}
  return null;
}
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;  // облако и шрифты идут напрямую
  // всегда спрашиваем сервер о свежей версии (без 10-минутного кеша браузера), при отсутствии сети — копия из кеша
  e.respondWith((async () => {
    try {
      const r = await fetch(e.request, { cache: "no-cache" });
      if (r && r.ok){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {}); }
      // сервер ответил ошибкой (сбой или обновление сайта): страницу лучше взять из сохранённой копии
      if (r && r.status >= 500 && e.request.mode === "navigate"){ const c = await fromCache(e.request); if (c) return c; }
      return r;
    } catch (err) {
      const c = await fromCache(e.request);
      if (c) return c;
      if (e.request.mode === "navigate") return new Response(OFFLINE, { status: 503, headers: { "Content-Type": "text/html; charset=utf-8" } });
      return new Response("", { status: 504, statusText: "offline" });
    }
  })());
});
