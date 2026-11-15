// Service worker del Monitor de disponibilidad (PWA).
// - Guarda solo la "cáscara": la página, sus scripts y estilos, íconos y la página sin conexión.
//   NUNCA guarda la API (el estado tiene que ser el de ahora).
// - Navegación por red; sin red, la página "Sin conexión".
const VERSION = "monitor-v1";
const CASCARA = ["/offline.html", "/offline.js", "/icono.svg", "/icono-192.png", "/manifest.webmanifest"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(VERSION).then((cache) => cache.addAll(CASCARA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((nombres) => Promise.all(nombres.filter((n) => n !== VERSION).map((n) => caches.delete(n))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // la API vive en otro dominio: nunca pasa por aquí

  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() => caches.match("/offline.html")));
    return;
  }
  // Archivos del build (con huella en el nombre) e íconos: primero la red; la copia, sin conexión.
  if (url.pathname.startsWith("/assets/") || /\.(svg|png|ico|webmanifest)$/.test(url.pathname)) {
    event.respondWith(
      fetch(request)
        .then((respuesta) => {
          if (respuesta.ok) {
            const copia = respuesta.clone();
            caches.open(VERSION).then((cache) => cache.put(request, copia));
          }
          return respuesta;
        })
        .catch(() => caches.match(request)),
    );
  }
});
