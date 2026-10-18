/* Official vector source priority: local pack -> IndexedDB -> authenticated relay -> direct official URL. */
V017_TILE_SOURCES.base.directUrl=V017_TILE_SOURCES.base.url;
V017_TILE_SOURCES.cadastre.directUrl=V017_TILE_SOURCES.cadastre.url;
V017_TILE_SOURCES.base.relayUrl=`${V036_RELAY}/tile/base/{z}/{x}/{y}.pbf`;
V017_TILE_SOURCES.cadastre.relayUrl=`${V036_RELAY}/tile/cadastre/{z}/{x}/{y}.pbf`;
function v036TileURL(template,z,x,y){return template.replace('{z}',z).replace('{x}',x).replace('{y}',y)}
async function v036FetchBuffer(url,ms=15000,auth=false){
 const ctrl=new AbortController();V018.controllers.add(ctrl);const timer=setTimeout(()=>ctrl.abort(),ms);
 try{
  const headers={Accept:'application/x-protobuf,application/vnd.mapbox-vector-tile,*/*'};
  if(auth){headers.Authorization='Bearer '+V036_PUBLIC_KEY;headers.apikey=V036_PUBLIC_KEY;}
  const r=await fetch(url,{signal:ctrl.signal,mode:'cors',cache:'default',headers});
  if(!r.ok)throw new Error(`HTTP ${r.status}`);const b=await r.arrayBuffer();v017DecodeMVT(b);return b;
 }finally{clearTimeout(timer);V018.controllers.delete(ctrl)}
}
const v036GetTilePrevious=v017GetTileBuffer;
v017GetTileBuffer=async function(source,z,x,y){
 const def=V017_TILE_SOURCES[source],key=v017TileKey(source,z,x,y),errors=[];
 // An installed offline pack is always preferred when served from the local application server.
 if(location.protocol!=='file:')try{return{buffer:await v036FetchBuffer(v017TileURL(def.local,z,x,y),3500,false),source:'pack'}}catch(e){errors.push('pack: '+e.message)}
 if(settings.geoCache!==false){const cached=await v017CacheGet(key);if(cached){try{v017DecodeMVT(cached);state.v036.cacheTilesLoaded++;return{buffer:cached,source:'cache'}}catch{await v018CacheDelete(key)}}}
 if(settings.geoStreaming===false)throw new Error('Aucune donnée locale — streaming désactivé');
 if(state.v036?.preferRelay!==false){try{const b=await v036FetchBuffer(v036TileURL(def.relayUrl,z,x,y),18000,true);state.v036.onlineTilesLoaded++;return{buffer:b,source:'relay'}}catch(e){errors.push('relay: '+e.message)}}
 try{const b=await v036FetchBuffer(v036TileURL(def.directUrl,z,x,y),18000,false);state.v036.onlineTilesLoaded++;return{buffer:b,source:'live'}}catch(e){errors.push('direct: '+e.message)}
 throw new Error(errors.join(' · '));
};
async function v036HealthCheck(){
 V036.health={state:'checking',checkedAt:null,checks:[],error:null};
 try{
  const r=await fetch(`${V036_RELAY}/meta`,{headers:{Authorization:'Bearer '+V036_PUBLIC_KEY,apikey:V036_PUBLIC_KEY},cache:'no-store'});
  if(!r.ok)throw new Error(`HTTP ${r.status}`);const j=await r.json();
  if(j.total!==V036_PLAN.total||j.sources?.base?.count!==V036_PLAN.base||j.sources?.cadastre?.count!==V036_PLAN.cadastre)throw new Error('Manifeste distant incohérent');
  V036.health={state:'ready',checkedAt:new Date().toISOString(),checks:[{name:'manifest',ok:true,total:j.total}],error:null};V036.manifestChecked=true;return true;
 }catch(e){V036.health={state:'unavailable',checkedAt:new Date().toISOString(),checks:[],error:String(e)};return false}
}
