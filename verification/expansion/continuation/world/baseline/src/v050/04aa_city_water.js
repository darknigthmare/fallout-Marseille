/* The sea is classified from official polygons and high-water shoreline, never
   from zero elevation or an inverted administrative boundary. */
const MistralCityWater=(()=>{
 const finite=n=>typeof n==='number'&&Number.isFinite(n);
 function box(b){return Array.isArray(b)&&b.length===4&&b.every(finite)&&b[0]>=-90&&b[2]<=90&&b[1]>=-180&&b[3]<=180&&b[0]<b[2]&&b[1]<b[3];}
 function descriptor(d){
  if(!d||!/^data\/map_pack\/city\/water-[0-9a-f]{16}\.json$/.test(d.path)||!/^[0-9a-f]{64}$/.test(d.sha256)||!d.path.endsWith(d.sha256.slice(0,16)+'.json')||!Number.isInteger(d.bytes)||d.bytes<1||d.bytes>8*1024*1024||!box(d.bbox)||d.tile?.z!==14||!Number.isInteger(d.tile.x)||!Number.isInteger(d.tile.y)||d.tile.x<0||d.tile.y<0||d.tile.x>=16384||d.tile.y>=16384||!Number.isInteger(d.features)||d.features<1||d.features>512||!Number.isInteger(d.vertices)||d.vertices<4||d.vertices>250000)throw Error('Descripteur maritime incompatible');
  return d;
 }
 function index(raw){
  const expected=[43.1696313,5.22875102,43.39105653,5.53254336],g=raw?.grid,s=raw?.source;
  if(raw?.schemaVersion!==1||raw.crs!=='EPSG:4326'||!box(raw.bbox)||!box(raw.municipalityBbox)||raw.municipalityBbox.some((n,i)=>Math.abs(n-expected[i])>1e-10)||raw.bbox.some((n,i)=>Math.abs(n-expected[i])>.04)||!s||s.resource!=='ign-city-water'||!['source','license','attribution','acquiredAt'].every(k=>typeof s[k]==='string'&&s[k].trim())||raw.derivation?.noSimplification!==true||!Array.isArray(raw.tiles)||!raw.tiles.length||raw.tiles.length>1024||g?.zoom!==14||!['minX','maxX','minY','maxY'].every(k=>Number.isInteger(g[k]))||g.minX>g.maxX||g.minY>g.maxY||(g.maxX-g.minX+1)*(g.maxY-g.minY+1)>1024)throw Error('Atlas maritime incompatible');
  const seen=new Set();for(const d of raw.tiles){descriptor(d);const key=d.tile.x+':'+d.tile.y;if(seen.has(key)||d.tile.x<g.minX||d.tile.x>g.maxX||d.tile.y<g.minY||d.tile.y>g.maxY)throw Error('Tuile maritime dupliquée ou hors emprise');seen.add(key);}
  return raw;
 }
 function project(raw,d,projector){
  descriptor(d);if(raw?.schemaVersion!==1||raw.role!=='water-tile'||JSON.stringify(raw.tile)!==JSON.stringify(d.tile)||JSON.stringify(raw.bbox)!==JSON.stringify(d.bbox)||raw.source?.resource!=='ign-city-water'||!Array.isArray(raw.features)||raw.features.length!==d.features)throw Error('Tuile maritime incompatible');
  let vertices=0;const features=[];
  function ring(r){if(!Array.isArray(r)||r.length<4||r.length>2048)throw Error('Anneau maritime hors budget');const first=r[0],last=r.at(-1);if(!Array.isArray(first)||!Array.isArray(last)||first[0]!==last[0]||first[1]!==last[1])throw Error('Anneau maritime ouvert');return r.map(p=>{if(!Array.isArray(p)||p.length!==2||!p.every(finite)||p[0]<d.bbox[1]-1e-10||p[0]>d.bbox[3]+1e-10||p[1]<d.bbox[0]-1e-10||p[1]>d.bbox[2]+1e-10||++vertices>250000)throw Error('Coordonnée maritime incompatible');const q=projector(p[1],p[0]);return[q[0],q[2]];});}
  for(const f of raw.features){
   if(f?.type!=='Feature'||typeof f.id!=='string'||f.properties?.kind!=='water'||f.properties.v051Water!==true||JSON.stringify(f.properties.provenance)!==JSON.stringify(raw.source)||!['Polygon','MultiPolygon'].includes(f.geometry?.type))throw Error('Polygone maritime sans provenance');
   const groups=(f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates).map(p=>{if(!Array.isArray(p)||!p.length||p.length>512)throw Error('Polygone maritime vide');return p.map(ring);});
   features.push({id:f.id,type:3,props:{...f.properties},v050Source:true,v050Geometry:f.geometry,v050Groups:groups,v050Paths:groups.flat()});
  }
  if(vertices!==d.vertices)throw Error('Comptage maritime différent de sa preuve');return features;
 }
 function containsTile(index,x,y){const g=index?.grid;return!!g&&x>=g.minX&&x<=g.maxX&&y>=g.minY&&y<=g.maxY;}
 function ocean(feature){return /^(?:ocean|sea)$/i.test(String(feature?.props?.class||feature?.props?.subclass||''));}
 return{box,descriptor,index,project,containsTile,ocean};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCityWater;
let v051WaterAfterInit=()=>{};

if(typeof window!=='undefined'&&typeof v046Resource==='function'){
 const maritime={index:null,promise:null,epoch:0,loads:new Map(),cache:new MistralStream.BudgetCache(8*1024*1024,16),errors:[],requests:0};
 async function ready(){
  if(V046.lab||typeof location!=='undefined'&&!['http:','https:'].includes(location.protocol))return null;
  if(!maritime.promise){const epoch=maritime.epoch;maritime.promise=(async()=>{const raw=await v050LocalSourceJSON('data/map_pack/city/water-index.json',null,true);if(!raw)return null;const value=MistralCityWater.index(raw);if(epoch!==maritime.epoch)throw Error('Atlas maritime périmé');maritime.index=value;return value;})().catch(e=>{maritime.promise=null;throw e;});}
  return maritime.promise;
 }
 async function chunk(descriptor,signal){
  v051CityAbort(signal);const cached=maritime.cache.get(descriptor.path);if(cached)return cached;
  if(!maritime.loads.has(descriptor.path)){const epoch=maritime.epoch,load=(async()=>{maritime.requests++;const raw=await v050LocalSourceJSON(descriptor.path,descriptor),features=MistralCityWater.project(raw,descriptor,(lat,lon)=>v015GeoProject('geo_huveaune',lat,lon));if(epoch!==maritime.epoch)throw Error('Tuile maritime périmée');maritime.cache.set(descriptor.path,features);return features;})();maritime.loads.set(descriptor.path,load);const release=()=>{if(maritime.loads.get(descriptor.path)===load)maritime.loads.delete(descriptor.path);};load.then(release,release);}
  return v051CityWait(maritime.loads.get(descriptor.path),signal);
 }
 const previousReady=v051CityReady;v051CityReady=async function(){const city=await previousReady();if(city)await ready();return city;};
 const previousPlan=v046Plan;v046Plan=function(lat,lon){const plan=previousPlan(lat,lon);if(V046.lab||!maritime.index)return plan;const g=maritime.index.grid,a=v017LonLatToTile(plan.box[2],plan.box[1],14),b=v017LonLatToTile(plan.box[0],plan.box[3],14),keys=new Set(plan.keys);for(let x=Math.max(g.minX,Math.floor(a.x));x<=Math.min(g.maxX,Math.floor(b.x));x++)for(let y=Math.max(g.minY,Math.floor(a.y));y<=Math.min(g.maxY,Math.floor(b.y));y++)keys.add(v046TileKey('base',14,x,y));plan.keys=[...keys];return plan;};
 const previousResource=v046Resource;v046Resource=async function(key,signal){
  if(V046.lab||!maritime.index||!key.startsWith('base:14:'))return previousResource(key,signal);
  const[,z0,x0,y0]=key.split(':'),z=+z0,x=+x0,y=+y0;if(!MistralCityWater.containsTile(maritime.index,x,y))return previousResource(key,signal);
  let resource;
  if(!v037TileAllowed('base',z,x,y)){const tile=v017TileBounds(z,x,y);if(!v051CityDescriptors([tile.south,tile.west,tile.north,tile.east]).length)resource={source:'base',z,x,y,layers:{},empty:false,origin:'IGN — mer vérifiée ; autres couches non disponibles dans cette ressource',v051WaterOnly:true};}
  resource||=await previousResource(key,signal);v051CityAbort(signal);
  const descriptor=maritime.index.tiles.find(d=>d.tile.x===x&&d.tile.y===y),extra=descriptor?await chunk(descriptor,signal):[];
  const old=resource.layers.water,retained=(old?.features||[]).filter(f=>!MistralCityWater.ocean(f));
  return{...resource,layers:{...resource.layers,water:{...(old||{name:'water',extent:4096}),features:[...retained,...extra]}},v051WaterAtlas:true};
 };
 const previousRefresh=v051CityRefresh;v051CityRefresh=function(){const result=previousRefresh();if(result){maritime.epoch++;maritime.index=null;maritime.promise=null;maritime.loads.clear();maritime.cache.clear();maritime.errors=[];}return result;};
 v051WaterAfterInit=()=>Object.assign(window.__MISTRAL_DEBUG,{v051WaterInfo:()=>({present:!!maritime.index,source:maritime.index?.source||null,derivation:maritime.index?.derivation||null,tiles:maritime.index?.tiles.length||0,cache:maritime.cache.stats(),requests:maritime.requests,errors:maritime.errors.slice()})});
}
