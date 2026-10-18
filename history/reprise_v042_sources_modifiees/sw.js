const CACHE='fallout-mistral-v042-1';
const CORE=['./','./index.html','./JOUER_FALLOUT_MISTRAL_v0.42.html','./manifest.webmanifest','./icons/mistral-192.png','./icons/mistral-512.png','./data/corridors/aubagne_marseille.json','./data/corridors/aubagne_laciotat.json','./data/map_pack/local_pack_v041_manifest.json','./data/fallout_layer_v042.json'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r}).catch(()=>caches.match('./index.html'))))});
