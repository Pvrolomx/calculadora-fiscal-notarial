const CACHE_NAME = 'calcfiscal-v1';
const STATIC = ['/','index.html','isr.html','isabi.html','istp.html','iva.html','manifest.json'];

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
    if (url.includes('/api/') || url.includes('banxico') || url.includes('inegi')) {
        e.respondWith(fetch(e.request).then(r => {
            caches.open(CACHE_NAME).then(c => c.put(e.request, r.clone()));
            return r;
        }).catch(() => caches.match(e.request)));
    } else {
        e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    }
});
