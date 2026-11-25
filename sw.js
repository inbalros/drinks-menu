/* Pour Decisions – offline cache.
   After the first visit the page opens instantly and works with no signal.
   Bump VERSION whenever index.html changes so phones pick up the new copy. */
const VERSION = "pour-decisions-v6";
const CORE = ["./", "./index.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(VERSION).then((cache) => cache.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Stale-while-revalidate: answer from cache right away (fast on weak venue Wi-Fi),
// refresh the cached copy in the background when the network is available.
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // The site root and index.html share one cache entry; other pages (e.g. sign.html) keep their own.
  const key = url.pathname.endsWith("/") ? "./index.html" : req;
  event.respondWith(
    caches.open(VERSION).then(async (cache) => {
      const cached = await cache.match(key, { ignoreSearch: true });
      const network = fetch(req)
        .then((res) => {
          if (res && res.ok && res.type === "basic") cache.put(key, res.clone());
          return res;
        })
        .catch(() => null);
      if (cached) {
        event.waitUntil(network);
        return cached;
      }
      const res = await network;
      return res || new Response("אין חיבור לרשת כרגע. נסו שוב בעוד רגע.", {
        status: 503,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    })
  );
});
