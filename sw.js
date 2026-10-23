/* v0.50: cache the application shell, never substitute HTML for missing PBF/DEM. */
const CACHE='fallout-mistral-v050-7';
const CORE=['./','./index.html','./JOUER_FALLOUT_MISTRAL_v0.50.html','./manifest.webmanifest','./icons/mistral-192.png','./icons/mistral-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('fallout-mistral-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;
 if(u.pathname.includes('/data/')||u.pathname.startsWith('/__mistral/')||u.pathname.endsWith('.pbf')){e.respondWith(fetch(e.request).catch(()=>new Response('Ressource locale indisponible',{status:503,headers:{'Content-Type':'text/plain'}})));return;}
 e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).catch(()=>e.request.mode==='navigate'?caches.match('./index.html'):new Response('Ressource indisponible',{status:503}))));
});
