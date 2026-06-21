/* Service Worker for Offline Mode Serial: #001 */
const CACHE_NAME = 'barbershop-calculator-v1';
const ASSETS = [
  '/',
  '/help',
  '/analysis',
  '/static/js/main.js',
  '/static/js/state.js',
  '/static/js/theory.js',
  '/static/js/audio.js',
  '/static/js/notation.js',
  '/static/js/spelling.js',
  '/static/js/ui-controls.js',
  'https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests for caching
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) return cachedResponse;
      return fetch(event.request).then((response) => {
        // Optional: Cache new successful requests on the fly
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      });
    }).catch(() => {
      // Fallback if both cache and network fail
      return new Response("Offline content not available");
    })
  );
});