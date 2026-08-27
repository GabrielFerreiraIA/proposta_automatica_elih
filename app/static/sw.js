/* Service worker do Cotador-Elih.
   Só faz o mínimo para o app ser instalável e abrir rápido: guarda a casca da
   interface. Upload, análise e geração NUNCA são cacheados — são POST e
   precisam do servidor. */

/* Trocar a versão invalida o cache antigo no proximo deploy. */
const CACHE = 'cotador-elih-v2';

/* Só o que não muda entre versões. O app.js e o CSS ficam de fora de proposito:
   guardá-los aqui fazia o usuário continuar rodando a versão anterior do app
   depois de um deploy, vendo erros que já tinham sido corrigidos. Eles vêm
   sempre da rede, e o Cache-Control do servidor cuida da revalidação. */
const CASCA = [
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

  // Código do app sempre da rede: cair para uma versão em cache aqui só
  // esconderia um deploy novo atrás de um bug já corrigido.
  const ehCodigo = /\.(js|css)$/.test(url.pathname) || url.pathname === '/';
  if (ehCodigo) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    return;
  }

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
