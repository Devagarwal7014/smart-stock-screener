const CACHE_NAME = "smart-stock-screener-cache-v1";
const urlsToCache = [
  "/",
  "/styles.css",
  // add more static assets you want cached
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
