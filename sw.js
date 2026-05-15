const CACHE_NAME = 'calcfiscal-v3';
const STATIC = [
    '/', 'index.html',
    'isr.html', 'isabi.html', 'iva.html',
    'calcpro.html',
    'manifest.json'
];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(STATIC)));
    self.skipWaiting();
});
self.addEventListener('activate', e => {
    e.waitUntil(caches.keys().then(n => Promise.all(n.filter(x => x !== CACHE_NAME).map(x => caches.delete(x)))));
    self.clients.claim();
});
self.addEventListener('fetch', e => {
    const url = e.request.url;
    // APIs externas: cache fallback
    if (url.includes('/api/') || url.includes('banxico') || url.includes('inegi')) {
        e.respondWith(fetch(e.request).then(r => {
            caches.open(CACHE_NAME).then(c => c.put(e.request, r.clone()));
            return r;
        }).catch(() => caches.match(e.request)));
    } else {
        // HTML/JS: network-first para siempre tener la versión más reciente
        e.respondWith(
            fetch(e.request).then(r => {
                caches.open(CACHE_NAME).then(c => c.put(e.request, r.clone()));
                return r;
            }).catch(() => caches.match(e.request))
        );
    }
});
