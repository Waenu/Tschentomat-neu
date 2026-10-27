// Service Worker: zuerst Netz, sonst gespeicherte Fassung (läuft so auch ohne Empfang).
const CACHE = "tschentomat-neu-v1";
const DATEIEN = ["./", "index.html", "einstellungen.json", "versionen.json", "manifest.json", "icon-192.png", "icon-512.png"];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(DATEIEN)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith("tschentomat-neu-") && k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then((r) => {
      const kopie = r.clone();
      caches.open(CACHE).then((c) => c.put(e.request.url.split("?")[0], kopie)).catch(() => {});
      return r;
    }).catch(() => caches.match(e.request.url.split("?")[0]).then((m) => m || caches.match("index.html")))
  );
});
