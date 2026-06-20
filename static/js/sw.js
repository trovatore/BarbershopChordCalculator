/* Service Worker for Offline Mode Serial: #001 */
const CACHE_NAME = 'barbershop-calculator-v1';
const ASSETS = [
  '/',
  '/help',
  '/static/js/main.js',
  '/static/js/state.js',
  '/static/js/theory.js',
  '/static/js/audio.js',
  '/static/js/notation.js',
  '/static/js/spelling.js',
  '/static/js/ui-controls.js',
  'https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});