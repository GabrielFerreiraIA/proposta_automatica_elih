/* Service worker do Cotador-Elih.
   Só faz o mínimo para o app ser instalável e abrir rápido: guarda a casca da
   interface. Upload, análise e geração NUNCA são cacheados — são POST e
   precisam do servidor. */

const CACHE = 'cotador-elih-v1';
const CASCA = [
  '/',
  '/static/css/app.css',
  '/static/app.js',
  '/static/img/elih-mark-circle.png',
  '/static/img/icone-192.png',
  '/static/manifest.webmanifest',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CASCA)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((nomes) => Promise.all(nomes.filter((n) => n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.pathname.startsWith('/api/')) return;

  // Rede primeiro: o app é pequeno e o conteúdo precisa estar fresco.
  // O cache existe só para abrir offline e não ficar em branco.
  e.respondWith(
    fetch(e.request)
      .then((resp) => {
        const copia = resp.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copia)).catch(() => {});
        return resp;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match('/')))
  );
});
