/* Marseille's authoritative atlas is streamed by query partition. The atlas
   never replaces a missing survey with a fixture or a guessed empty tile. */
const V051_CITY_ID='geo_marseille_commune',V051_CITY_BOUNDS=[43.1696313,5.22875102,43.39105653,5.53254336];
const V051_CITY={index:null,indexPromise:null,terrainIndex:null,terrainPromise:null,epoch:0,navigationSerial:0,loads:new Map(),cache:new MistralStream.BudgetCache(64*1024*1024,24),terrainCache:new MistralStream.BudgetCache(48*1024*1024,8),errors:[],registered:false,requests:0};
/* The identity must exist before a saved exterior is resumed. Terrain bounds
   are installed only after both local indices validate, without touching the
   live bank; the next prepared bank receives the new measured base grid. */
if(!V015_GEO_MACROS[V051_CITY_ID])Object.defineProperty(V015_GEO_MACROS,V051_CITY_ID,{value:{name:'Marseille · commune entière',region:'MACRO-RÉGION · MARSEILLE',center:[43.2965,5.3698],bbox:V051_CITY_BOUNDS.slice(),scale:1,kind:'urban',internal:true,hideOnMap:true,neighbors:['geo_marseille','geo_frioul','geo_calanques','geo_etoile']},enumerable:false,configurable:true,writable:true});
const v051CityRoadClassBase=v017ClassRoad;
v017ClassRoad=function(props){const classification=MistralIntegrity.roadClassification(props);return classification.sourceNature?v051CityRoadClassBase({...props,class:classification.value==='steps'?'footway':classification.value}):v051CityRoadClassBase(props);};
function v051CityError(error){V051_CITY.errors.push(String(error?.message||error));V051_CITY.errors=V051_CITY.errors.slice(-10);}
function v051CityAbort(signal){if(signal?.aborted){const error=new Error('Chargement de Marseille annulé');error.name='AbortError';throw error;}}
function v051CityWait(promise,signal){
 v051CityAbort(signal);if(!signal)return promise;
 return new Promise((resolve,reject)=>{
  let settled=false;
  const cleanup=()=>signal.removeEventListener('abort',abort);
  const abort=()=>{if(settled)return;settled=true;cleanup();const error=new Error('Chargement de Marseille annulé');error.name='AbortError';reject(error);};
  signal.addEventListener('abort',abort,{once:true});
  // A cancellation settles only this waiter; the shared partition request stays alive.
  // Attach both handlers directly: a discarded .finally() chain would reject unobserved.
  promise.then(value=>{if(settled)return;settled=true;cleanup();resolve(value);},error=>{if(settled)return;settled=true;cleanup();reject(error);});
  if(signal.aborted)abort();
 });
}
function v051CityDescriptor(d,terrain=false){
 if(!d||typeof d.path!=='string'||!/^data\/map_pack\/city\/[a-zA-Z0-9_.-]+-[0-9a-f]{16}\.json$/.test(d.path)||!Number.isInteger(d.bytes)||d.bytes<1||d.bytes>64*1024*1024||!/^[0-9a-f]{64}$/.test(d.sha256)||!d.path.endsWith('-'+d.sha256.slice(0,16)+'.json')||!v050SourceBox(d.bbox))throw Error('Descripteur de partition de Marseille invalide');
 if(!terrain&&(typeof d.id!=='string'||!d.id||d.id.length>128||d.region!==V051_CITY_ID||d.bytes>8*1024*1024||!v050SourceBox(d.queryBbox)||!Array.isArray(d.coverages)||d.coverages.length!==2||!d.counts||!['buildings','roads'].every(k=>Number.isInteger(d.counts[k])&&d.counts[k]>=0)||d.counts.buildings+d.counts.roads>3000))throw Error('Comptage de partition de Marseille invalide');
 if(d.renderBbox!==undefined&&(!v050SourceBox(d.renderBbox)||d.renderBbox[0]<d.bbox[0]||d.renderBbox[1]<d.bbox[1]||d.renderBbox[2]>d.bbox[2]||d.renderBbox[3]>d.bbox[3]))throw Error('Emprise rendue de partition invalide');
 return d;
}
async function v051CityIndex(){
 if(typeof location!=='undefined'&&!['http:','https:'].includes(location.protocol))return null;
 const epoch=V051_CITY.epoch;
 if(!V051_CITY.indexPromise)V051_CITY.indexPromise=(async()=>{
  const index=await v050LocalSourceJSON('data/map_pack/city/index.json',null,true);if(!index)return null;
  const municipality=index.municipality;
  if(index.schemaVersion!==1||municipality?.code!=='13055'||!v050SourceBox(municipality.bbox)||municipality.bbox.some((n,i)=>Math.abs(n-V051_CITY_BOUNDS[i])>1e-7)||index.coverage?.complete!==true||!Array.isArray(index.tiles)||!index.tiles.length||index.tiles.length>2048)throw Error('Index communal de Marseille incomplet ou incompatible');
  const ids=new Set(),paths=new Set();for(const d of index.tiles){v051CityDescriptor(d);if(ids.has(d.id)||paths.has(d.path))throw Error('Partition de Marseille dupliquée');ids.add(d.id);paths.add(d.path);}
  if(epoch!==V051_CITY.epoch)throw Error('Index communal de Marseille périmé');V051_CITY.index=index;return index;
 })().catch(error=>{if(epoch===V051_CITY.epoch)V051_CITY.indexPromise=null;throw error;});
 return V051_CITY.indexPromise;
}
async function v051CityTerrainIndex(){
 if(typeof location!=='undefined'&&!['http:','https:'].includes(location.protocol))return null;
 const epoch=V051_CITY.epoch;
 if(!V051_CITY.terrainPromise)V051_CITY.terrainPromise=(async()=>{
  const index=await v050LocalSourceJSON('data/map_pack/city/terrain-index.json',null,true);if(!index)return null;
  if(index.schemaVersion!==1||index.region!==V051_CITY_ID||!v050SourceBox(index.bbox)||index.bbox.some((n,i)=>Math.abs(n-V051_CITY_BOUNDS[i])>1e-7)||!Array.isArray(index.tiles)||index.tiles.length>2048)throw Error('Index du relief communal incompatible');
  v051CityDescriptor(index.base,true);if(index.base.bbox.some((n,i)=>Math.abs(n-index.bbox[i])>1e-7))throw Error('Relief communal de base incomplet');
  const paths=new Set([index.base.path]);for(const d of index.tiles){v051CityDescriptor(d,true);if(paths.has(d.path))throw Error('Dalle de relief communal dupliquée');paths.add(d.path);}
  if(epoch!==V051_CITY.epoch)throw Error('Index du relief communal périmé');V051_CITY.terrainIndex=index;return index;
 })().catch(error=>{if(epoch===V051_CITY.epoch)V051_CITY.terrainPromise=null;throw error;});
 return V051_CITY.terrainPromise;
}
async function v051CityReady(){
 if(V046.lab)return null;const [index,terrain]=await Promise.all([v051CityIndex(),v051CityTerrainIndex()]);
 if(V051_CITY.registered&&(!index||!terrain))throw Error('L’atlas communal précédemment chargé est incomplet ou absent');
 if(index&&terrain&&!V046.lab&&!V051_CITY.registered){V046_BOUNDS[V051_CITY_ID]=index.municipality.bbox.slice();V015_GEO_MACROS[V051_CITY_ID].bbox=index.municipality.bbox.slice();V051_CITY.registered=true;}
 return index;
}
function v051CityDescriptors(box){
 // A partition is relevant if either its source footprint or its explicitly
 // declared rendered footprint intersects the requested tile. Never let a
 // narrow renderBbox hide authoritative geometry crossing a tile boundary.
 return(V051_CITY.index?.tiles||[]).filter(d=>MistralIntegrity.intersects(box,d.bbox)||(d.renderBbox&&MistralIntegrity.intersects(box,d.renderBbox))).sort((a,b)=>a.path.localeCompare(b.path));
}
/* Only the new plan's verified citydem resources may add fine city grids.
   Leaving the commune therefore drops old fine tiles too. Base grids and the
   independently acquired Aubagne sources remain exactly as the caller held
   them. The currently published bank is never edited by this staging copy. */
function v051CityStageBank(bounds,active){
 const bank=new MistralIntegrity.TerrainBank(bounds);
 for(const[id,grid]of active.grids)if(id!=='enrichment:'+V051_CITY_ID&&!id.startsWith('enrichment:'+V051_CITY_ID+':'))bank.grids.set(id,grid);
 return bank;
}
async function v051CityChunk(descriptor,signal){
 v051CityAbort(signal);const key=descriptor.path,cached=V051_CITY.cache.get(key);if(cached)return cached;
 const epoch=V051_CITY.epoch;
 if(!V051_CITY.loads.has(key)){
  const load=(async()=>{
   V051_CITY.requests++;const raw=await v050LocalSourceJSON(descriptor.path,descriptor);
   if(raw?.schemaVersion!==1||raw.region!==V051_CITY_ID||!Array.isArray(raw.features)||raw.features.length>3000||!v050SourceBox(raw.queryBbox)||raw.queryBbox.some((n,i)=>Math.abs(n-descriptor.queryBbox[i])>1e-10)||!Array.isArray(raw.coverages)||raw.coverages.length!==2)throw Error('Partition communale incompatible');
   const counts={buildings:0,roads:0},projected=[],spatial=new MistralStream.SpatialGrid(128),seen=new Set(),provenancePool=new Map();
   /* Every object keeps its complete source receipt. Equal receipts share one
      immutable in-memory object rather than thousands of duplicated query
      records; neither the verified file bytes nor any field value changes. */
   for(const feature of raw.features){const proof=feature?.properties?.provenance,key=JSON.stringify(proof);if(proof&&typeof proof==='object'){if(provenancePool.has(key))feature.properties.provenance=provenancePool.get(key);else provenancePool.set(key,proof);}const f=v050SourceFeature(feature,V051_CITY_ID),identity=f.props.kind+':'+f.sourceId;if(seen.has(identity))throw Error('Objet communal dupliqué dans sa partition');seen.add(identity);counts[f.props.kind==='building'?'buildings':'roads']++;projected.push(f);spatial.add(f.v050Bounds,f);}
   if(counts.buildings!==descriptor.counts.buildings||counts.roads!==descriptor.counts.roads)throw Error('Comptage communal différent de son reçu');
   const proofKey=coverage=>JSON.stringify([coverage?.layer,coverage?.bbox,coverage?.crs,coverage?.complete,coverage?.returned]),proofKeys=new Set(raw.coverages.map(proofKey));
   const coverages=raw.coverages.map(coverage=>v050SourceCoverage({kind:coverage.layer==='BDTOPO_V3:troncon_de_route'?'road':'building',provenance:{resource:'ign-bdtopo',coverage}},V051_CITY_ID));
   if(new Set(raw.coverages.map(c=>c.layer)).size!==2||descriptor.coverages.some(c=>!proofKeys.has(proofKey(c)))||raw.coverages.some(c=>c.bbox.some((n,i)=>Math.abs(n-descriptor.queryBbox[i])>1e-10)||c.returned!==counts[c.layer==='BDTOPO_V3:batiment'?'buildings':'roads'])||raw.features.some(f=>!proofKeys.has(proofKey(f.properties.provenance.coverage))))throw Error('Preuves des requêtes communales incohérentes');
   if(epoch!==V051_CITY.epoch)throw Error('Partition communale périmée');const bundle={projected,spatial,coverages,source:raw.source,counts,path:key,wireBytes:descriptor.bytes,provenanceRecords:provenancePool.size};V051_CITY.cache.set(key,bundle);return bundle;
  })();
  V051_CITY.loads.set(key,load);load.then(()=>{if(V051_CITY.loads.get(key)===load)V051_CITY.loads.delete(key);},()=>{if(V051_CITY.loads.get(key)===load)V051_CITY.loads.delete(key);});
 }
 return v051CityWait(V051_CITY.loads.get(key),signal);
}
async function v051CityTerrain(descriptor,signal,base=false){
 v051CityAbort(signal);const key=descriptor.path,cached=V051_CITY.terrainCache.get(key);if(cached)return cached;
 const epoch=V051_CITY.epoch;
 if(!V051_CITY.loads.has(key)){
  const load=(async()=>{V051_CITY.requests++;const raw=await v050LocalSourceJSON(key,descriptor),id=base?V051_CITY_ID:raw.macro;
   if(!base&&(typeof id!=='string'||!/^enrichment:geo_marseille_commune:[0-9a-f]{16}$/.test(id)))throw Error('Identité de dalle communale invalide');
   MistralIntegrity.terrain(raw,id,descriptor.bbox);if(epoch!==V051_CITY.epoch)throw Error('Relief communal périmé');const result={raw,id,source:'IGN — atlas communal local',origin:'IGN — atlas communal local'};V051_CITY.terrainCache.set(key,result);return result;
  })();V051_CITY.loads.set(key,load);load.then(()=>{if(V051_CITY.loads.get(key)===load)V051_CITY.loads.delete(key);},()=>{if(V051_CITY.loads.get(key)===load)V051_CITY.loads.delete(key);});
 }
 return v051CityWait(V051_CITY.loads.get(key),signal);
}
async function v051CityEnrich(resource,signal){
 if(!V051_CITY.registered||!V051_CITY.index||!resource||!['base','cadastre'].includes(resource.source))return resource;
 const tile=v017TileBounds(resource.z,resource.x,resource.y),box=[tile.south,tile.west,tile.north,tile.east],descriptors=v051CityDescriptors(box);if(!descriptors.length)return resource;
 const corners=[[tile.south,tile.west],[tile.north,tile.east]].map(p=>v015GeoProject(V051_CITY_ID,...p)),bounds=v017PolyBounds([corners.map(p=>[p[0],p[2]])]),features=[],coverages=[],seen=new Set();
 /* Sequential inside each tile keeps the existing four-worker map gate as the
    sole concurrency bound. Shared partition promises deduplicate those workers. */
 for(const d of descriptors){const bundle=await v051CityChunk(d,signal);v051CityAbort(signal);const radius=Math.max(bounds.maxX-bounds.minX,bounds.maxZ-bounds.minZ)/2+1;
  for(const feature of bundle.spatial.around(bounds.cx,bounds.cz,radius))if(v050BoxesTouch(bounds,feature.v050Bounds)){const identity=feature.props.kind+':'+feature.sourceId+':'+MistralIntegrity.hash(feature.v050Geometry);if(!seen.has(identity)){seen.add(identity);features.push(feature);}}
  coverages.push(...bundle.coverages);
 }
 return v050ApplySourceOverlays(resource,features,coverages);
}
const v051CityPlanBase=v046Plan;
v046Plan=function(lat,lon){
 const plan=v051CityPlanBase(lat,lon);if(V046.lab){plan.dem=plan.dem.filter(key=>key!=='dem:'+V051_CITY_ID&&!key.startsWith('citydem:'));return plan;}if(!V051_CITY.registered)return plan;
 if(MistralIntegrity.intersects(plan.box,V051_CITY_BOUNDS)&&!plan.dem.includes('dem:'+V051_CITY_ID))plan.dem.push('dem:'+V051_CITY_ID);
 for(const descriptor of V051_CITY.terrainIndex?.tiles||[])if(MistralIntegrity.intersects(plan.box,descriptor.bbox))plan.dem.push('citydem:'+descriptor.sha256);
 const keys=new Set(plan.keys);
 for(const source of ['base','cadastre']){const z=source==='base'?14:16,a=v017LonLatToTile(plan.box[2],plan.box[1],z),b=v017LonLatToTile(plan.box[0],plan.box[3],z);
  for(let x=Math.floor(a.x);x<=Math.floor(b.x);x++)for(let y=Math.floor(a.y);y<=Math.floor(b.y);y++){const tile=v017TileBounds(z,x,y),box=[tile.south,tile.west,tile.north,tile.east];if(v051CityDescriptors(box).length)keys.add(v046TileKey(source,z,x,y));}
 }
 plan.keys=[...keys];return plan;
};
const v051CityResourceBase=v046Resource;
v046Resource=async function(key,signal){
 if(V046.lab)return v051CityResourceBase(key,signal);v051CityAbort(signal);
 if(key==='dem:'+V051_CITY_ID){if(!V051_CITY.terrainIndex)throw Error('Relief communal absent');return v051CityTerrain(V051_CITY.terrainIndex.base,signal,true);}
 if(key.startsWith('citydem:')){const descriptor=V051_CITY.terrainIndex?.tiles.find(d=>d.sha256===key.slice(8));if(!descriptor)throw Error('Dalle communale inconnue');return v051CityTerrain(descriptor,signal);}
 let resource;
 if(!key.startsWith('dem:')){const[source,z0,x0,y0]=key.split(':'),z=+z0,x=+x0,y=+y0;
  if(!v037TileAllowed(source,z,x,y)&&V051_CITY.registered){const tile=v017TileBounds(z,x,y);if(!v051CityDescriptors([tile.south,tile.west,tile.north,tile.east]).length)throw Error('Aucune source vérifiée hors du pack local');resource={source,z,x,y,layers:{},origin:'IGN — partition vérifiée hors du pack de base',empty:false,v051CityOnly:true};}
 }
 resource||=await v051CityResourceBase(key,signal);return v051CityEnrich(resource,signal);
};
const v051CityEnsureBase=v046Ensure;
v046Ensure=async function(lat,lon,w=world,initial=false,opts={}){
 const ticket=V051_CITY.navigationSerial;
 if(!V046.lab)try{await v051CityReady();}catch(error){
  if(ticket!==V051_CITY.navigationSerial)return false;v051CityError(error);V046.last={lat,lon,w,initial,opts};V046.error=[{key:'city-index',message:String(error.message||error)}];
  if(!opts.v047Warm){V046.busy=true;zoneTransitioning=true;mode='LOADING';v046Loading({phase:'failed',done:0,total:1,errors:V046.error});}return false;
 }
 if(ticket!==V051_CITY.navigationSerial)return false;
 return v051CityEnsureBase(lat,lon,w,initial,opts);
};
const v051CityCancelBase=v046Cancel;
v046Cancel=function(){V051_CITY.navigationSerial++;return v051CityCancelBase();};
/* A synthetic laboratory must continue to use only its declared fixture
   bounds. Its bank is constructed after this removal; the retained real bank
   itself is never edited, and its bounds return when the laboratory closes. */
const v051CityLabBase=v046StartLab;
v046StartLab=async function(){
 if(!V046.lab&&V046_BOUNDS[V051_CITY_ID]){V051_CITY.labBounds=V046_BOUNDS[V051_CITY_ID];delete V046_BOUNDS[V051_CITY_ID];}
 try{return await v051CityLabBase();}catch(error){if(!V046.lab&&V051_CITY.labBounds){V046_BOUNDS[V051_CITY_ID]=V051_CITY.labBounds;V051_CITY.labBounds=null;}throw error;}
};
const v051CityLeaveLabBase=v047LeaveLab;
v047LeaveLab=function(){const result=v051CityLeaveLabBase();if(!V046.lab&&V051_CITY.labBounds){V046_BOUNDS[V051_CITY_ID]=V051_CITY.labBounds;V051_CITY.labBounds=null;}return result;};
function v051CityRefresh(){
 if(V046.busy||V047.pending)return false;V051_CITY.navigationSerial++;V051_CITY.epoch++;V051_CITY.index=null;V051_CITY.indexPromise=null;V051_CITY.terrainIndex=null;V051_CITY.terrainPromise=null;V051_CITY.loads.clear();V051_CITY.cache.clear();V051_CITY.terrainCache.clear();V051_CITY.errors=[];V046.gate?.cache.clear();V047.records?.clear();V047.meshes?.clear();return true;
}
function v051CityInfo(){
 const index=V051_CITY.index,tiles=index?.tiles||[],resident=[...V051_CITY.cache.values()];
 return{indexPresent:!!index,municipality:index?.municipality?{code:index.municipality.code,name:index.municipality.name,bbox:index.municipality.bbox.slice()}:null,coverage:index?.coverage||null,registered:V051_CITY.registered,tilesAvailable:tiles.length,sourceBuildings:index?.coverage?.uniqueBuildings??tiles.reduce((n,d)=>n+d.counts.buildings,0),sourceRoads:index?.coverage?.uniqueRoads??tiles.reduce((n,d)=>n+d.counts.roads,0),loadedPartitions:resident.length,loadedBuildings:resident.reduce((n,b)=>n+b.counts.buildings,0),loadedRoads:resident.reduce((n,b)=>n+b.counts.roads,0),loadedWireBytes:resident.reduce((n,b)=>n+b.wireBytes,0),sharedProvenanceRecords:resident.reduce((n,b)=>n+b.provenanceRecords,0),cache:V051_CITY.cache.stats(),terrainCache:V051_CITY.terrainCache.stats(),terrainIndexPresent:!!V051_CITY.terrainIndex,terrainTilesAvailable:V051_CITY.terrainIndex?.tiles.length||0,inflight:V051_CITY.loads.size,requests:V051_CITY.requests,errors:V051_CITY.errors.slice()};
}
function v051CityAfterInit(){
 Object.assign(window.__MISTRAL_DEBUG,{v051CityInfo,v051CityRefresh,v051CityReady});
 if(typeof location==='undefined'||['http:','https:'].includes(location.protocol)){const epoch=V051_CITY.epoch;v051CityReady().catch(error=>{if(epoch===V051_CITY.epoch)v051CityError(error);});}
}
